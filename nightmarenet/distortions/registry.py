"""Distortion plugin registry.

Allows registration of custom distortion engines for extensibility.
Built-in engines: dream, nightmare.

Usage:
    from nightmarenet.distortions.registry import DistortionRegistry

    registry = DistortionRegistry()
    registry.register("custom_dream", my_distortion_fn)
    result = registry.apply("custom_dream", text, strength=0.5)
"""

from typing import Any, Callable, Dict, List, Optional

DistortionFn = Callable[[str, float, Optional[int]], str]


class DistortionRegistry:
    """Plugin registry for distortion engines.

    Supports registration of custom distortion functions that follow
    the signature: (text: str, strength: float, seed: Optional[int]) -> str
    """

    def __init__(self) -> None:
        self._engines: Dict[str, DistortionFn] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._register_builtins()

    def _register_builtins(self) -> None:
        from nightmarenet.distortions import dream as dream_mod
        from nightmarenet.distortions import nightmare as nightmare_mod

        self.register(
            "dream",
            dream_mod.distort,
            metadata={"phase": "dream", "description": "Mild stochastic augmentation"},
        )
        self.register(
            "nightmare",
            nightmare_mod.distort,
            metadata={"phase": "nightmare", "description": "Adversarial perturbation"},
        )

    def register(
        self,
        name: str,
        fn: DistortionFn,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a distortion engine."""
        if not callable(fn):
            raise TypeError(f"Distortion function must be callable, got {type(fn)}")
        self._engines[name] = fn
        self._metadata[name] = metadata or {}

    def unregister(self, name: str) -> None:
        """Remove a registered distortion engine."""
        self._engines.pop(name, None)
        self._metadata.pop(name, None)

    def apply(
        self,
        name: str,
        text: str,
        strength: float = 0.3,
        seed: Optional[int] = None,
    ) -> str:
        """Apply a named distortion to text."""
        if name not in self._engines:
            available = ", ".join(sorted(self._engines.keys()))
            raise KeyError(f"Unknown distortion '{name}'. Available: {available}")
        return self._engines[name](text, strength, seed)

    def list_engines(self) -> List[Dict[str, Any]]:
        """List all registered distortion engines with metadata."""
        return [
            {"name": name, **self._metadata.get(name, {})}
            for name in sorted(self._engines.keys())
        ]

    @property
    def engine_names(self) -> List[str]:
        return sorted(self._engines.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._engines

    def __len__(self) -> int:
        return len(self._engines)


_default_registry: Optional[DistortionRegistry] = None


def get_registry() -> DistortionRegistry:
    """Get the global distortion registry (lazy singleton)."""
    global _default_registry
    if _default_registry is None:
        _default_registry = DistortionRegistry()
    return _default_registry
