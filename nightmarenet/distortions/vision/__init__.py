"""Computer Vision (image-based) distortions."""

from nightmarenet.distortions.vision.base import ImageDistortion
from nightmarenet.distortions.vision.dream import (
    ColorJitter,
    GaussianBlur,
    GeometricTransform,
    JPEGCompression,
)

__all__ = [
    "ImageDistortion",
    "ColorJitter",
    "GeometricTransform",
    "GaussianBlur",
    "JPEGCompression",
]

