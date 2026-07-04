"""Configuration loader for robustness transfer learning."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class TransferConfig:
    """Configuration for robustness transfer fine-tuning."""

    task_type: str = "seq_classification"
    dataset: str = "sst2"
    num_labels: int = 2
    batch_size: int = 8
    num_epochs: int = 3
    freeze_bottom_n: int = 0
    unfreeze_after_epoch: int = 1
    learning_rate: float = 3e-5
    output_dir: str = "./output/transfer"
    device: str = "cuda"
    strict_layer_freezing: bool = False


def load_config(path: str | Path) -> TransferConfig:
    """Load a transfer configuration from a YAML file."""
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data:
        data = {}

    return TransferConfig(**data)
