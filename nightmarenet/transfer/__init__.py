"""Robustness Transfer Learning module.

This module provides functionality to register hardened foundation models
and transfer their robustness to downstream tasks efficiently via fine-tuning.
"""

from nightmarenet.transfer.fine_tune import TransferFineTuner
from nightmarenet.transfer.head_factory import create_transfer_model
from nightmarenet.transfer.measurement import calculate_transfer_ratio, evaluate_transfer_efficiency
from nightmarenet.transfer.registry import FoundationRegistry, get_registry
from nightmarenet.transfer.report import generate_transfer_report

__all__ = [
    "FoundationRegistry",
    "get_registry",
    "create_transfer_model",
    "TransferFineTuner",
    "calculate_transfer_ratio",
    "evaluate_transfer_efficiency",
    "generate_transfer_report",
]
