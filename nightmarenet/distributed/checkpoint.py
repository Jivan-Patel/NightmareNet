"""Atomic checkpointing for distributed execution."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import tempfile
from typing import Optional

import torch

logger = logging.getLogger(__name__)


def compute_config_hash(config: dict) -> str:
    """Compute a deterministic hash of the training configuration."""
    config_str = json.dumps(config, sort_keys=True)
    return hashlib.sha256(config_str.encode()).hexdigest()


class AtomicCheckpointer:
    """Handles atomic saves of model, optimizer, and phase state."""

    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def save(
        self,
        run_id: str,
        cycle: int,
        phase: str,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        config: dict,
        metrics: Optional[dict] = None,
        devices_used: Optional[list[int]] = None
    ) -> str:
        """Save state atomically and drop a .complete sentinel."""
        run_dir = os.path.join(self.base_dir, run_id)
        os.makedirs(run_dir, exist_ok=True)

        target_dir = os.path.join(run_dir, f"cycle-{cycle}-{phase}")
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)

        # Write to a temporary directory first
        temp_dir = tempfile.mkdtemp(dir=run_dir, prefix=f".tmp_cycle-{cycle}-{phase}_")
        try:
            # 1. Model weights
            model_path = os.path.join(temp_dir, "model.pt")

            # Handle DDP / DataParallel unwrapping
            model_to_save = model.module if hasattr(model, "module") else model
            if hasattr(model_to_save, "save_pretrained"):
                model_to_save.save_pretrained(temp_dir)
            else:
                torch.save(model_to_save.state_dict(), model_path)

            # 2. Optimizer state
            opt_path = os.path.join(temp_dir, "optimizer.pt")
            torch.save(optimizer.state_dict(), opt_path)

            # 3. RNG States
            rng_path = os.path.join(temp_dir, "rng_state.pt")
            torch.save({
                "cpu": torch.get_rng_state(),
                "cuda": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else []
            }, rng_path)

            # 4. Metadata and Config hash
            meta_path = os.path.join(temp_dir, "metadata.json")
            with open(meta_path, "w") as f:
                json.dump({
                    "cycle": cycle,
                    "phase": phase,
                    "config_hash": compute_config_hash(config),
                    "metrics": metrics or {},
                    "devices_used": devices_used or []
                }, f, indent=2)

            # Atomically rename
            os.rename(temp_dir, target_dir)

            # Drop sentinel
            sentinel_path = os.path.join(target_dir, ".complete")
            with open(sentinel_path, "w") as f:
                f.write("complete")

            logger.info(f"Atomically saved checkpoint to {target_dir}")
            return target_dir

        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            logger.error(f"Failed to save checkpoint: {e}")
            raise
