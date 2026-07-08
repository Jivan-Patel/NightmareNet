"""Tests for distortion DSL (chain execution, parsing, presets)."""

import pytest
from pathlib import Path
import tempfile
import yaml

from nightmarenet.distortions.dsl import ChainExecutor, parse_chain_config, list_presets, load_preset
from nightmarenet.distortions.dsl.schema import ChainConfig, ChainStep, Defaults
from nightmarenet.distortions.dsl.parser import validate_chain_config


def test_chain_config_schema_validation():
    """Test Pydantic schema validation for chain config."""
    # Valid config
    config_data = {
        "name": "test_chain",
        "description": "Test chain",
        "version": 1,
        "chain": [
            {"engine": "dream", "strength": 0.3, "condition": "always"}
        ],
        "defaults": {"seed": 42, "preserve_length": False, "max_retries": 3}
    }
    config = ChainConfig(**config_data)
    assert config.name == "test_chain"
    assert len(config.chain) == 1
    assert config.chain[0].engine == "dream"
    assert config.chain[0].strength == 0.3


def test_chain_config_invalid_strength():
    """Test that invalid strength values are rejected."""
    with pytest.raises(ValueError, match="strength"):
        ChainStep(engine="dream", strength=1.5)


def test_chain_config_invalid_condition():
    """Test that invalid conditions are rejected."""
    with pytest.raises(ValueError, match="Condition must reference"):
        ChainStep(engine="dream", strength=0.3, condition="foo > 0.5")


def test_chain_config_empty_chain():
    """Test that empty chains are rejected."""
    with pytest.raises(ValueError, match="at least one step"):
        ChainConfig(name="test", chain=[])


def test_parse_chain_config_from_yaml():
    """Test parsing a valid YAML chain config."""
    yaml_content = """
name: test_chain
description: Test description
version: 1
chain:
  - engine: dream
    strength: 0.3
    condition: always
defaults:
  seed: 42
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        f.flush()
        config = parse_chain_config(f.name, validate_engines=False)
        assert config.name == "test_chain"
        assert len(config.chain) == 1
        Path(f.name).unlink()


def test_parse_chain_config_invalid_yaml():
    """Test that invalid YAML is rejected."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("invalid: yaml: content: [")
        f.flush()
        with pytest.raises(ValueError):
            parse_chain_config(f.name)
        Path(f.name).unlink()


def test_parse_chain_config_unknown_engine():
    """Test that unknown engines are rejected when validate_engines=True."""
    yaml_content = """
name: test_chain
chain:
  - engine: nonexistent_engine
    strength: 0.3
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        f.flush()
        with pytest.raises(ValueError, match="Unknown engine"):
            parse_chain_config(f.name, validate_engines=True)
        Path(f.name).unlink()


def test_validate_chain_config():
    """Test the validate_chain_config function."""
    yaml_content = """
name: test_chain
chain:
  - engine: dream
    strength: 0.3
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        f.flush()
        is_valid, message = validate_chain_config(f.name)
        assert is_valid is True
        assert "valid" in message.lower()
        Path(f.name).unlink()


def test_validate_chain_config_invalid():
    """Test validation with invalid config."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("invalid: [")
        f.flush()
        is_valid, message = validate_chain_config(f.name)
        assert is_valid is False
        Path(f.name).unlink()


def test_chain_executor_condition_always():
    """Test that 'always' condition always passes."""
    executor = ChainExecutor()
    assert executor._evaluate_condition("always", 0.0) is True
    assert executor._evaluate_condition("always", 1.0) is True


def test_chain_executor_condition_strength_gt():
    """Test strength > condition."""
    executor = ChainExecutor()
    assert executor._evaluate_condition("strength > 0.5", 0.7) is True
    assert executor._evaluate_condition("strength > 0.5", 0.3) is False


def test_chain_executor_condition_strength_lt():
    """Test strength < condition."""
    executor = ChainExecutor()
    assert executor._evaluate_condition("strength < 0.5", 0.3) is True
    assert executor._evaluate_condition("strength < 0.5", 0.7) is False


def test_chain_executor_condition_strength_gte():
    """Test strength >= condition."""
    executor = ChainExecutor()
    assert executor._evaluate_condition("strength >= 0.5", 0.5) is True
    assert executor._evaluate_condition("strength >= 0.5", 0.7) is True
    assert executor._evaluate_condition("strength >= 0.5", 0.3) is False


def test_chain_executor_condition_strength_lte():
    """Test strength <= condition."""
    executor = ChainExecutor()
    assert executor._evaluate_condition("strength <= 0.5", 0.5) is True
    assert executor._evaluate_condition("strength <= 0.5", 0.3) is True
    assert executor._evaluate_condition("strength <= 0.5", 0.7) is False


def test_chain_executor_condition_invalid():
    """Test that invalid conditions return False (safe default)."""
    executor = ChainExecutor()
    assert executor._evaluate_condition("invalid syntax", 0.5) is False


def test_chain_executor_single_step():
    """Test executing a single-step chain."""
    config = ChainConfig(
        name="test",
        chain=[ChainStep(engine="dream", strength=0.3, condition="always")]
    )
    executor = ChainExecutor()
    text = "The quick brown fox"
    result = executor.execute(text, config, overall_strength=0.5, seed=42)
    assert isinstance(result, str)
    assert len(result) > 0


def test_chain_executor_multiple_steps():
    """Test executing a multi-step chain."""
    config = ChainConfig(
        name="test",
        chain=[
            ChainStep(engine="dream", strength=0.2, condition="always"),
            ChainStep(engine="dream", strength=0.3, condition="always"),
        ]
    )
    executor = ChainExecutor()
    text = "The quick brown fox"
    result = executor.execute(text, config, overall_strength=0.5, seed=42)
    assert isinstance(result, str)


def test_chain_executor_condition_skipping():
    """Test that steps are skipped when condition fails."""
    config = ChainConfig(
        name="test",
        chain=[
            ChainStep(engine="dream", strength=0.2, condition="always"),
            ChainStep(engine="dream", strength=0.3, condition="strength > 0.8"),
        ]
    )
    executor = ChainExecutor()
    text = "The quick brown fox"
    # With overall_strength=0.5, second step should be skipped
    result = executor.execute(text, config, overall_strength=0.5, seed=42)
    assert isinstance(result, str)


def test_chain_executor_determinism():
    """Test that execution is deterministic with same seed."""
    config = ChainConfig(
        name="test",
        chain=[
            ChainStep(engine="dream", strength=0.3, condition="always"),
        ]
    )
    executor = ChainExecutor()
    text = "The quick brown fox"
    
    result1 = executor.execute(text, config, overall_strength=0.5, seed=42)
    result2 = executor.execute(text, config, overall_strength=0.5, seed=42)
    
    assert result1 == result2


def test_chain_executor_with_trace():
    """Test execute_with_trace returns detailed information."""
    config = ChainConfig(
        name="test",
        chain=[
            ChainStep(engine="dream", strength=0.3, condition="always"),
        ]
    )
    executor = ChainExecutor()
    text = "The quick brown fox"
    
    trace = executor.execute_with_trace(text, config, overall_strength=0.5, seed=42)
    
    assert "original" in trace
    assert "final" in trace
    assert "steps" in trace
    assert trace["original"] == text
    assert len(trace["steps"]) == 1
    assert trace["steps"][0]["status"] in ["applied", "skipped", "failed"]


def test_load_preset():
    """Test loading a preset by name."""
    # This test uses the actual preset files created in the package
    try:
        config = load_preset("minimal_dream")
        assert config.name == "minimal_dream"
        assert len(config.chain) >= 1
    except FileNotFoundError:
        pytest.skip("Preset files not found in expected location")


def test_list_presets():
    """Test listing available presets."""
    presets = list_presets()
    assert isinstance(presets, list)
    # If presets exist, check their structure
    for preset in presets:
        assert "name" in preset
        assert "path" in preset
        assert "version" in preset


def test_chain_executor_failed_step_continues():
    """Test that failed steps don't abort the chain."""
    # Create a custom registry with a failing engine
    from nightmarenet.distortions.registry import DistortionRegistry
    
    def failing_distort(text: str, strength: float, seed=None) -> str:
        raise RuntimeError("Intentional failure")
    
    registry = DistortionRegistry()
    registry.register("failing", failing_distort)
    
    config = ChainConfig(
        name="test",
        chain=[
            ChainStep(engine="dream", strength=0.2, condition="always"),
            ChainStep(engine="failing", strength=0.3, condition="always"),
            ChainStep(engine="dream", strength=0.2, condition="always"),
        ]
    )
    
    executor = ChainExecutor(registry=registry)
    text = "The quick brown fox"
    
    # Should not raise, should skip the failing step
    result = executor.execute(text, config, overall_strength=0.5, seed=42)
    assert isinstance(result, str)
