"""End-to-end pipeline: data → distortion → training → evaluation.

Orchestrates the full NightmareNet sleep-cycle workflow as a single
unit of work, with status tracking and optional callbacks for live
metric streaming.
"""

from __future__ import annotations

import copy
import enum
import logging
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

from nightmarenet.data.generator import create_generators_from_config
from nightmarenet.data.ingest import DataIngestor
from nightmarenet.evaluation.evaluator import Evaluator
from nightmarenet.training.trainer import Trainer, _tokenize_dataset
from nightmarenet.utils.config import load_config

logger = logging.getLogger(__name__)


class PipelineStatus(str, enum.Enum):
    """Lifecycle status of a Pipeline run."""

    IDLE = "idle"
    INGESTING = "ingesting"
    PREPARING = "preparing"
    TRAINING = "training"
    EVALUATING = "evaluating"
    COMPLETE = "complete"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PipelineMetrics:
    """Snapshot of live training metrics."""

    status: PipelineStatus = PipelineStatus.IDLE
    current_cycle: int = 0
    total_cycles: int = 0
    current_phase: str = ""
    phase_loss: float = 0.0
    progress_pct: float = 0.0
    eta_seconds: float = 0.0
    history: list[dict] = field(default_factory=list)
    error: Optional[str] = None
    baseline_results: Optional[dict] = None
    trained_results: Optional[dict] = None
    comparison: Optional[dict] = None
    report_md: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "current_cycle": self.current_cycle,
            "total_cycles": self.total_cycles,
            "current_phase": self.current_phase,
            "phase_loss": self.phase_loss,
            "progress_pct": round(self.progress_pct, 2),
            "eta_seconds": round(self.eta_seconds, 1),
            "history": self.history,
            "error": self.error,
            "has_report": self.report_md is not None,
        }


class Pipeline:
    """Orchestrates the full NightmareNet pipeline.

    Usage::

        pipe = Pipeline(config)
        pipe.ingest(urls=["https://en.wikipedia.org/wiki/Machine_learning"])
        pipe.prepare()
        pipe.train()
        pipe.evaluate()
        pipe.export("results/my_model")

    Args:
        config: Full NightmareNet YAML configuration (dict).
        on_event: Optional callback ``fn(metrics_dict)`` called after
                  every phase and status change for live dashboards.
    """

    def __init__(
        self,
        config: dict,
        on_event: Optional[Callable[[dict], None]] = None,
    ) -> None:
        self.config = config
        self.on_event = on_event
        self.metrics = PipelineMetrics()
        self._cancelled = False

        # Populated by each stage
        self._dataset = None
        self._train_dl = None
        self._dream_dl = None
        self._nightmare_dl = None
        self._val_dl = None
        self._trainer: Optional[Trainer] = None
        self._baseline_model = None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _emit(self) -> None:
        if self.on_event is not None:
            try:
                self.on_event(self.metrics.to_dict())
            except Exception:
                logger.debug("on_event callback failed", exc_info=True)

    def _set_status(self, status: PipelineStatus) -> None:
        self.metrics.status = status
        self._emit()

    def _fail(self, error: str) -> None:
        self.metrics.status = PipelineStatus.FAILED
        self.metrics.error = error
        self._emit()

    def cancel(self) -> None:
        """Request graceful cancellation of a running pipeline."""
        self._cancelled = True
        self.metrics.status = PipelineStatus.CANCELLED
        self._emit()

    # ------------------------------------------------------------------
    # Stage 1: Ingest
    # ------------------------------------------------------------------

    def ingest(
        self,
        *,
        urls: Optional[list[str]] = None,
        file_path: Optional[str] = None,
        text_content: Optional[str] = None,
        hf_dataset: Optional[str] = None,
        hf_subset: Optional[str] = None,
    ) -> None:
        """Load data from one of the supported sources.

        Exactly one of *urls*, *file_path*, *text_content*, or
        *hf_dataset* must be provided.
        """
        self._set_status(PipelineStatus.INGESTING)

        dataset_cfg = self.config.get("dataset", {})
        text_column = dataset_cfg.get("text_column", "text")
        max_samples = dataset_cfg.get("max_samples")
        seed = self.config.get("seed", 42)

        ingestor = DataIngestor(
            text_column=text_column,
            max_samples=max_samples,
            seed=seed,
        )

        try:
            if urls:
                self._dataset = ingestor.from_urls(urls)
            elif file_path:
                self._dataset = ingestor.from_file(file_path)
            elif text_content:
                self._dataset = ingestor.from_text_content(text_content)
            elif hf_dataset:
                self._dataset = ingestor.from_huggingface(hf_dataset, subset=hf_subset)
            else:
                raise ValueError(
                    "Provide one of: urls, file_path, text_content, or hf_dataset."
                )
            if self._dataset is not None:
                logger.info("Ingestion complete: %d samples.", len(self._dataset))
        except Exception as exc:
            self._fail(f"Ingestion failed: {exc}")
            raise

    # ------------------------------------------------------------------
    # Stage 2: Prepare
    # ------------------------------------------------------------------

    def prepare(self) -> None:
        """Generate dream/nightmare splits and tokenise all data."""
        if self._dataset is None:
            raise RuntimeError("Call .ingest() before .prepare()")
        self._set_status(PipelineStatus.PREPARING)

        try:
            dream_gen, nightmare_gen = create_generators_from_config(self.config)
            dream_data = dream_gen.generate(self._dataset)
            nightmare_data = nightmare_gen.generate(self._dataset)

            # Create trainer (loads model + tokenizer)
            self._trainer = Trainer(config=self.config)

            # Snapshot baseline model weights for later evaluation
            self._baseline_model = copy.deepcopy(self._trainer.model)
            self._baseline_model.eval()

            # Tokenise
            text_column = self.config.get("dataset", {}).get("text_column", "text")
            max_length = self.config.get("model", {}).get("max_length", 128)
            batch_size = self.config.get("training", {}).get("batch_size", 8)

            self._train_dl = _tokenize_dataset(
                self._dataset, self._trainer.tokenizer,
                text_column, max_length, batch_size,
            )
            self._dream_dl = _tokenize_dataset(
                dream_data, self._trainer.tokenizer,
                text_column, max_length, batch_size,
            )
            self._nightmare_dl = _tokenize_dataset(
                nightmare_data, self._trainer.tokenizer,
                text_column, max_length, batch_size,
            )
            logger.info("Preparation complete: dataloaders ready.")
        except Exception as exc:
            self._fail(f"Preparation failed: {exc}")
            raise

    # ------------------------------------------------------------------
    # Stage 3: Train
    # ------------------------------------------------------------------

    def train(self) -> list[dict]:
        """Run the full sleep-cycle training pipeline.

        Returns:
            Training history (list of phase result dicts).
        """
        if self._trainer is None:
            raise RuntimeError("Call .prepare() before .train()")
        if self._cancelled:
            return []

        self._set_status(PipelineStatus.TRAINING)
        self.metrics.total_cycles = self.config.get("training", {}).get("num_cycles", 3)

        start = time.time()
        try:
            history = self._trainer.train(
                train_dataloader=self._train_dl,
                dream_dataloader=self._dream_dl,
                nightmare_dataloader=self._nightmare_dl,
                val_dataloader=self._val_dl,
            )

            # Update metrics from history
            self.metrics.history = history
            for entry in history:
                self.metrics.current_cycle = entry.get("cycle", 0)
                self.metrics.current_phase = entry.get("phase", "")
                self.metrics.phase_loss = entry.get("avg_loss", 0.0)

            elapsed = time.time() - start
            self.metrics.progress_pct = 100.0
            self.metrics.eta_seconds = 0.0
            self._emit()
            logger.info("Training complete in %.1fs.", elapsed)
            return history
        except Exception as exc:
            self._fail(f"Training failed: {exc}")
            raise

    # ------------------------------------------------------------------
    # Stage 4: Evaluate
    # ------------------------------------------------------------------

    def evaluate(self) -> dict:
        """Run baseline vs trained model evaluation and generate report.

        Returns:
            Comparison dict with all metric deltas.
        """
        if self._trainer is None:
            raise RuntimeError("Call .train() before .evaluate()")

        self._set_status(PipelineStatus.EVALUATING)

        try:
            evaluator = Evaluator(
                model=self._trainer.model,
                tokenizer=self._trainer.tokenizer,
                config=self.config,
                device=str(self._trainer.device),
            )

            # Evaluate trained model
            trained_results = evaluator.evaluate(
                clean_dataloader=self._train_dl,
                label="nightmarenet-trained",
            )
            self.metrics.trained_results = trained_results

            # Evaluate baseline model (pre-training snapshot)
            baseline_evaluator = Evaluator(
                model=self._baseline_model,
                tokenizer=self._trainer.tokenizer,
                config=self.config,
                device=str(self._trainer.device),
            )
            baseline_results = baseline_evaluator.evaluate(
                clean_dataloader=self._train_dl,
                label="baseline",
            )
            self.metrics.baseline_results = baseline_results

            # Generate comparison
            comparison = evaluator.compare(baseline_results, trained_results)
            self.metrics.comparison = comparison

            # Generate markdown report
            report = evaluator.generate_report(comparison)
            self.metrics.report_md = report

            # Save results
            results_dict = {
                "baseline": baseline_results,
                "trained": trained_results,
                "comparison": comparison,
            }
            evaluator.save_results(results_dict)

            self._set_status(PipelineStatus.COMPLETE)
            logger.info("Evaluation complete.")
            return comparison
        except Exception as exc:
            self._fail(f"Evaluation failed: {exc}")
            raise

    # ------------------------------------------------------------------
    # Stage 5: Export
    # ------------------------------------------------------------------

    def export(self, output_dir: str) -> str:
        """Save the trained model, tokenizer, and report to disk.

        Args:
            output_dir: Directory to save artifacts.

        Returns:
            Path to the saved model directory.
        """
        import os

        if self._trainer is None:
            raise RuntimeError("No trained model to export.")

        os.makedirs(output_dir, exist_ok=True)

        self._trainer.model.save_pretrained(output_dir)
        self._trainer.tokenizer.save_pretrained(output_dir)

        if self.metrics.report_md:
            report_path = os.path.join(output_dir, "evaluation_report.md")
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(self.metrics.report_md)

        logger.info("Model exported to %s", output_dir)
        return output_dir

    # ------------------------------------------------------------------
    # Convenience: run all stages
    # ------------------------------------------------------------------

    def run(
        self,
        *,
        urls: Optional[list[str]] = None,
        file_path: Optional[str] = None,
        text_content: Optional[str] = None,
        hf_dataset: Optional[str] = None,
        hf_subset: Optional[str] = None,
        export_dir: Optional[str] = None,
    ) -> dict:
        """Execute the full pipeline end-to-end.

        Returns:
            The evaluation comparison dict.
        """
        self.ingest(
            urls=urls,
            file_path=file_path,
            text_content=text_content,
            hf_dataset=hf_dataset,
            hf_subset=hf_subset,
        )
        self.prepare()
        self.train()
        comparison = self.evaluate()

        if export_dir:
            self.export(export_dir)

        return comparison


def create_pipeline_from_config(
    config_path: str = "configs/default.yaml",
    on_event: Optional[Callable[[dict], None]] = None,
) -> Pipeline:
    """Create a Pipeline from a YAML config file.

    Args:
        config_path: Path to the YAML configuration.
        on_event: Optional event callback for live dashboards.

    Returns:
        Configured Pipeline instance.
    """
    config = load_config(config_path)
    return Pipeline(config=config, on_event=on_event)
