"""Sequential chain executor for distortion chains."""

import logging
import random
from typing import List, Optional

from nightmarenet.distortions.dsl.schema import ChainConfig, ChainStep
from nightmarenet.distortions.registry import get_registry

logger = logging.getLogger(__name__)


class ChainExecutor:
    """Executes distortion chains sequentially with condition evaluation."""
    
    def __init__(self, registry=None):
        """Initialize the executor.
        
        Args:
            registry: Optional DistortionRegistry instance. If None, uses global registry.
        """
        self.registry = registry or get_registry()
    
    def _evaluate_condition(self, condition: str, strength: float) -> bool:
        """Evaluate a condition string against the current strength.
        
        Args:
            condition: Condition string (e.g., "strength > 0.5", "always")
            strength: Current strength value to evaluate against
            
        Returns:
            True if condition passes, False otherwise
        """
        if condition == "always":
            return True
        
        # Safe evaluation: only allow strength comparisons
        try:
            # Create a safe namespace with only the strength variable
            namespace = {"strength": strength}
            # Evaluate the condition
            result = eval(condition, {"__builtins__": {}}, namespace)
            return bool(result)
        except Exception as e:
            logger.warning(f"Failed to evaluate condition '{condition}': {e}")
            return False
    
    def execute(
        self,
        text: str,
        chain_config: ChainConfig,
        overall_strength: float,
        seed: Optional[int] = None,
    ) -> str:
        """Execute a distortion chain sequentially.
        
        Each step evaluates its condition, applies if passed,
        and feeds output to the next step. Failed steps are logged but don't abort the chain.
        
        Args:
            text: Input text to distort
            chain_config: Chain configuration to execute
            overall_strength: Overall strength for the chain (used for condition evaluation)
            seed: Random seed for reproducibility (overrides chain defaults if provided)
            
        Returns:
            Final distorted text after applying all applicable steps
        """
        # Set seed for reproducibility
        effective_seed = seed if seed is not None else chain_config.defaults.seed
        if effective_seed is not None:
            random.seed(effective_seed)
        
        current_text = text
        steps_applied = 0
        steps_skipped = 0
        steps_failed = 0
        
        logger.info(f"Executing chain '{chain_config.name}' with strength {overall_strength}")
        
        for i, step in enumerate(chain_config.chain):
            step_num = i + 1
            
            # Check condition
            if not self._evaluate_condition(step.condition, overall_strength):
                logger.debug(
                    f"Step {step_num} ({step.engine}) skipped: condition '{step.condition}' not met"
                )
                steps_skipped += 1
                continue
            
            # Apply the distortion
            try:
                logger.debug(
                    f"Step {step_num} ({step.engine}): applying with strength {step.strength}"
                )
                
                # Use step-specific strength, not overall strength
                step_seed = effective_seed + i if effective_seed is not None else None
                distorted = self.registry.apply(
                    step.engine,
                    current_text,
                    strength=step.strength,
                    seed=step_seed,
                )
                
                current_text = distorted
                steps_applied += 1
                logger.debug(f"Step {step_num} completed successfully")
                
            except Exception as e:
                logger.warning(
                    f"Step {step_num} ({step.engine}) failed: {e}. Skipping and continuing."
                )
                steps_failed += 1
                # Don't abort the chain - continue with next step
                continue
        
        logger.info(
            f"Chain execution complete: {steps_applied} applied, "
            f"{steps_skipped} skipped, {steps_failed} failed"
        )
        
        return current_text
    
    def execute_with_trace(
        self,
        text: str,
        chain_config: ChainConfig,
        overall_strength: float,
        seed: Optional[int] = None,
    ) -> dict:
        """Execute a chain and return detailed trace information.
        
        Useful for debugging and UI visualization of step-by-step transformations.
        
        Args:
            text: Input text to distort
            chain_config: Chain configuration to execute
            overall_strength: Overall strength for the chain
            seed: Random seed for reproducibility
            
        Returns:
            Dictionary with trace information including:
            - original: Original text
            - final: Final distorted text
            - steps: List of step results with input/output and status
        """
        effective_seed = seed if seed is not None else chain_config.defaults.seed
        if effective_seed is not None:
            random.seed(effective_seed)
        
        current_text = text
        steps_trace = []
        
        for i, step in enumerate(chain_config.chain):
            step_num = i + 1
            step_trace = {
                "step": step_num,
                "engine": step.engine,
                "strength": step.strength,
                "condition": step.condition,
                "input": current_text,
                "status": "skipped",
                "output": current_text,
                "error": None,
            }
            
            # Check condition
            if not self._evaluate_condition(step.condition, overall_strength):
                steps_trace.append(step_trace)
                continue
            
            # Apply the distortion
            try:
                step_seed = effective_seed + i if effective_seed is not None else None
                distorted = self.registry.apply(
                    step.engine,
                    current_text,
                    strength=step.strength,
                    seed=step_seed,
                )
                
                step_trace["status"] = "applied"
                step_trace["output"] = distorted
                current_text = distorted
                
            except Exception as e:
                step_trace["status"] = "failed"
                step_trace["error"] = str(e)
            
            steps_trace.append(step_trace)
        
        return {
            "original": text,
            "final": current_text,
            "steps": steps_trace,
            "seed": effective_seed,
        }
