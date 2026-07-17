import pytest
import torch
from PIL import Image

from nightmarenet.distortions.registry import get_vision_registry
from nightmarenet.distortions.vision.dream import (
    ColorJitter,
    GaussianBlur,
    GeometricTransform,
    JPEGCompression,
)
from nightmarenet.distortions.vision.gaussian_noise import GaussianNoise
from nightmarenet.distortions.vision.utils import to_pil, to_tensor


def test_vision_registry_singleton():
    """Test that get_vision_registry returns a singleton."""
    r1 = get_vision_registry()
    r2 = get_vision_registry()
    assert r1 is r2


def test_vision_registry_builtin_loaded():
    """Test that builtin gaussian noise is loaded."""
    registry = get_vision_registry()
    assert "vision_gaussian_noise" in registry


def test_gaussian_noise_no_op():
    """Test that strength 0.0 is a no-op."""
    noise = GaussianNoise()
    img = torch.zeros(3, 32, 32)
    distorted = noise.distort(img, strength=0.0)
    assert torch.all(img == distorted)


def test_gaussian_noise_determinism():
    """Test that the same seed produces the same output."""
    noise = GaussianNoise()
    img = torch.zeros(3, 32, 32)

    distorted1 = noise.distort(img, strength=0.5, seed=42)
    distorted2 = noise.distort(img, strength=0.5, seed=42)

    assert torch.all(distorted1 == distorted2)


def test_gaussian_noise_different_seeds():
    """Test that different seeds produce different outputs."""
    noise = GaussianNoise()
    img = torch.zeros(3, 32, 32)

    distorted1 = noise.distort(img, strength=0.5, seed=42)
    distorted2 = noise.distort(img, strength=0.5, seed=43)

    assert not torch.all(distorted1 == distorted2)


def test_gaussian_noise_bounds():
    """Test that gaussian noise output is bounded between 0 and 1."""
    noise = GaussianNoise()
    # image full of 0.5
    img = torch.ones(3, 32, 32) * 0.5
    distorted = noise.distort(img, strength=1.0)

    assert torch.all(distorted >= 0.0)
    assert torch.all(distorted <= 1.0)


def test_utils_conversions():
    """Test PIL to Tensor and Tensor to PIL conversions."""
    # Create a random RGB image
    img = Image.new("RGB", (32, 32), color="red")

    tensor = to_tensor(img)
    assert tensor.shape == (3, 32, 32)
    assert isinstance(tensor, torch.Tensor)

    img_back = to_pil(tensor)
    assert isinstance(img_back, Image.Image)
    assert img_back.size == (32, 32)


def test_vision_registry_apply():
    """Test applying a vision distortion via the registry."""
    registry = get_vision_registry()
    img = torch.ones(3, 32, 32) * 0.5

    distorted = registry.apply("vision_gaussian_noise", img, strength=0.5, seed=123)
    assert distorted.shape == (3, 32, 32)
    assert torch.all(distorted >= 0.0) and torch.all(distorted <= 1.0)


def test_gaussian_noise_empty_tensor():
    """Test empty tensor handling (e.g. shape with 0 dimension)."""
    noise = GaussianNoise()
    img = torch.zeros(3, 0, 0)
    distorted = noise.distort(img, strength=0.5, seed=42)
    assert distorted.shape == (3, 0, 0)


@pytest.mark.parametrize(
    "distortion_cls,name",
    [
        (ColorJitter, "vision_color_jitter"),
        (GeometricTransform, "vision_geometric_transform"),
        (GaussianBlur, "vision_gaussian_blur"),
        (JPEGCompression, "vision_jpeg_compression"),
    ],
)
def test_dream_distortions_properties(distortion_cls, name):
    """Test standard distortion properties: registered, no-op, bounds, and determinism."""
    # 1. Test Registry integration
    registry = get_vision_registry()
    assert name in registry

    distortion = distortion_cls()
    img = torch.ones(3, 32, 32) * 0.5

    # 2. Test strength 0.0 is no-op
    distorted_noop = distortion.distort(img, strength=0.0)
    assert torch.all(img == distorted_noop)

    # 3. Test bounds [0, 1] at max strength 1.0
    distorted_max = distortion.distort(img, strength=1.0)
    assert distorted_max.shape == (3, 32, 32)
    assert torch.all(distorted_max >= 0.0)
    assert torch.all(distorted_max <= 1.0)

    # 4. Test determinism with seed
    distorted_seed1 = distortion.distort(img, strength=0.8, seed=42)
    distorted_seed2 = distortion.distort(img, strength=0.8, seed=42)
    assert torch.all(distorted_seed1 == distorted_seed2)


def test_dream_distortions_single_channel():
    """Test that all dream distortions handle single channel grayscale images correctly."""
    img = torch.ones(1, 32, 32) * 0.5

    for distortion_cls in [ColorJitter, GeometricTransform, GaussianBlur, JPEGCompression]:
        distortion = distortion_cls()
        distorted = distortion.distort(img, strength=0.5, seed=42)
        assert distorted.shape == (1, 32, 32)
        assert torch.all(distorted >= 0.0) and torch.all(distorted <= 1.0)
