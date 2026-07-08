"""Pydantic schema for distortion chain configuration validation."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class Defaults(BaseModel):
    """Default configuration values for the chain."""
    
    seed: int = 42
    preserve_length: bool = False
    max_retries: int = 3


class ChainStep(BaseModel):
    """A single step in a distortion chain."""
    
    engine: str = Field(..., description="Name of the distortion engine to apply")
    strength: float = Field(..., ge=0.0, le=1.0, description="Strength of distortion (0-1)")
    description: Optional[str] = Field(None, description="Human-readable description of this step")
    condition: Optional[str] = Field(
        "always",
        description="Condition for applying this step (e.g., 'strength > 0.5', 'always')"
    )
    config: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional engine-specific configuration"
    )
    
    @field_validator("condition")
    @classmethod
    def validate_condition(cls, v: Optional[str]) -> str:
        """Validate condition syntax."""
        if v is None or v == "":
            return "always"
        v = v.strip()
        if v == "always":
            return v
        # Simple validation: must be a comparison with strength
        if "strength" not in v:
            raise ValueError("Condition must reference 'strength' variable")
        allowed_ops = [">", "<", ">=", "<=", "==", "!="]
        if not any(op in v for op in allowed_ops):
            raise ValueError(f"Condition must use one of: {', '.join(allowed_ops)}")
        return v


class ChainConfig(BaseModel):
    """Complete distortion chain configuration."""
    
    name: str = Field(..., description="Name of the distortion chain")
    description: Optional[str] = Field(None, description="Human-readable description")
    version: int = Field(1, ge=1, description="Configuration version")
    chain: List[ChainStep] = Field(..., min_length=1, description="Ordered list of distortion steps")
    defaults: Defaults = Field(default_factory=Defaults, description="Default configuration values")
    
    @field_validator("chain")
    @classmethod
    def validate_chain_not_empty(cls, v: List[ChainStep]) -> List[ChainStep]:
        """Ensure chain has at least one step."""
        if not v:
            raise ValueError("Chain must have at least one step")
        return v
