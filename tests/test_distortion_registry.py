"""Tests for distortion plugin registry."""

import pytest

from nightmarenet.distortions.registry import DistortionRegistry, get_registry


def test_builtin_engines_registered() -> None:
    registry = DistortionRegistry()
    assert "dream" in registry
    assert "nightmare" in registry
    assert len(registry) >= 2


def test_apply_dream_deterministic_with_seed() -> None:
    registry = DistortionRegistry()
    text = "The quick brown fox jumps over the lazy dog."
    a = registry.apply("dream", text, strength=0.3, seed=42)
    b = registry.apply("dream", text, strength=0.3, seed=42)
    assert a == b
    assert isinstance(a, str)
    assert len(a) > 0


def test_unknown_engine_raises() -> None:
    registry = DistortionRegistry()
    with pytest.raises(KeyError, match="Unknown distortion"):
        registry.apply("nonexistent", "hello", strength=0.5)


def test_custom_engine_registration() -> None:
    registry = DistortionRegistry()

    def upper_distort(text: str, strength: float, seed: int = None) -> str:
        return text.upper()

    registry.register("upper", upper_distort)
    assert registry.apply("upper", "hello", strength=1.0) == "HELLO"


def test_get_registry_singleton() -> None:
    a = get_registry()
    b = get_registry()
    assert a is b
