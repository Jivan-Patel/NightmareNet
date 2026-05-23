"""Dream-phase distortion pipeline (mild text + semantic augmentation)."""

import random
from typing import Any, Dict, Optional

from nightmarenet.distortions.semantic import apply_semantic_distortions
from nightmarenet.distortions.text import apply_text_distortions


def distort(
    text: str,
    strength: float,
    seed: Optional[int] = None,
    config: Optional[Dict[str, Any]] = None,
) -> str:
    """Apply mild dream distortions to text."""
    if seed is not None:
        random.seed(seed)
    text_config = config.get("text") if config else None
    semantic_config = config.get("semantic") if config else None
    result = apply_text_distortions(text, strength=strength, config=text_config)
    return apply_semantic_distortions(result, strength=strength, config=semantic_config)
