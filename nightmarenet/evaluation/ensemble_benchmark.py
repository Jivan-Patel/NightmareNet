"""Orchestrator for multi-model ensemble robustness benchmarking."""

from __future__ import annotations

import logging
import time
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from typing import Any, Optional

import torch
import yaml
from pydantic import BaseModel, Field
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from nightmarenet.distortions.registry import get_registry
from nightmarenet.evaluation.metrics import robustness_score

logger = logging.getLogger(__name__)


class DatasetConfig(BaseModel):
    name: str = "sst2"
    split: str = "validation"
    max_samples: Optional[int] = 100
    text_column: str = "sentence"


class DistortionConfig(BaseModel):
    type: str = "dream"
    strengths: list[float] = Field(default_factory=lambda: [0.1, 0.3, 0.5, 0.7, 0.9])


class EnsembleConfig(BaseModel):
    models: list[str]
    dataset: DatasetConfig = Field(default_factory=DatasetConfig)
    distortions: list[DistortionConfig] = Field(default_factory=list)



def _evaluate_model_worker(
    model_name: str,
    dataset_name: str,
    dataset_split: str,
    max_samples: int,
    text_column: str,
    distortion_type: str,
    strengths: list[float],
) -> dict[str, Any]:
    """Worker function to evaluate a single model.

    Runs in a separate process to ensure memory is freed after execution.
    """
    from datasets import load_dataset

    device = "cuda" if torch.cuda.is_available() else "cpu"

    logger.info("Loading model %s on %s", model_name, device)
    # Using sequence classification as baseline for benchmarking.
    # Can be extended to generic AutoModel later.
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.to(device)
    model.eval()

    params = sum(p.numel() for p in model.parameters())

    logger.info("Loading dataset %s", dataset_name)
    ds = load_dataset(dataset_name, split=dataset_split)
    if max_samples and max_samples < len(ds):
        ds = ds.select(range(max_samples))

    registry = get_registry()

    def distortion_fn(text, strength):
        return registry.apply(distortion_type, text, strength=strength, seed=42)

    start_time = time.time()

    try:
        # We reuse robustness_score from metrics
        # Note: robustness_score currently evaluates perplexity, which means
        # it expects CausalLM. If we use SequenceClassification, we might need
        # to adapt it, but for now we follow the existing evaluate API that expects
        # the model to accept input_ids and labels (which SequenceClassification does).
        # Actually SequenceClassification returns loss, which compute_perplexity can use.
        result = robustness_score(
            model=model,
            base_dataset=ds,
            tokenizer=tokenizer,
            distortion_fn=distortion_fn,
            strengths=strengths,
            text_column=text_column,
            max_length=128,
            batch_size=8,
            device=device,
        )
    except Exception as e:
        logger.error("Evaluation failed for %s: %s", model_name, e)
        raise e

    latency = time.time() - start_time

    return {
        "model": model_name,
        "robustness": result.get("auc_robustness", 0.0),
        "latency": latency,
        "params": params,
        "strengths": result.get("strengths", []),
        "perplexities": result.get("perplexities", []),
    }


class EnsembleOrchestrator:
    """Orchestrates the evaluation of multiple models from a config."""

    def __init__(self, config_path: str):
        self.config_path = config_path
        with open(config_path, encoding="utf-8") as f:
            raw_config = yaml.safe_load(f)

        # Validate with Pydantic
        self.config = EnsembleConfig(**raw_config)

    def run(self, timeout_seconds: int = 300) -> dict[str, Any]:
        """Run the ensemble benchmark suite.

        Args:
            timeout_seconds: Maximum time (in seconds) to allow per model.
        """
        models = self.config.models
        dataset_cfg = self.config.dataset
        ds_name = dataset_cfg.name
        ds_split = dataset_cfg.split
        max_samples = dataset_cfg.max_samples
        text_column = dataset_cfg.text_column

        distortions = self.config.distortions

        if not distortions:
            distortion_type = "dream"
            strengths = [0.1, 0.3, 0.5, 0.7, 0.9]
        else:
            distortion_type = distortions[0].type
            strengths = distortions[0].strengths

        results = {}
        models_summary = []

        for model_name in models:
            logger.info("Starting evaluation for %s", model_name)

            with ProcessPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    _evaluate_model_worker,
                    model_name,
                    ds_name,
                    ds_split,
                    max_samples,
                    text_column,
                    distortion_type,
                    strengths,
                )
                try:
                    res = future.result(timeout=timeout_seconds)
                    models_summary.append({
                        "model": res["model"],
                        "robustness": res["robustness"],
                        "latency": res["latency"],
                        "params": res["params"],
                    })
                    results[model_name] = {
                        "strengths": res["strengths"],
                        "perplexities": res["perplexities"],
                    }
                except TimeoutError:
                    logger.error("Timeout exceeded for model %s", model_name)
                except Exception as e:
                    logger.error("Error evaluating model %s: %s", model_name, e)

        return {
            "models_summary": models_summary,
            "raw_results": results,
        }
