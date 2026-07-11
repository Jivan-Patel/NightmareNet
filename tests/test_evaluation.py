"""Tests for evaluation metrics and comparison."""

import pytest

from nightmarenet.evaluation.evaluator import _bootstrap_ci


def test_bootstrap_ci_identical():
    """Test that identical data produces p > 0.05 (not significant)."""
    baseline = [0.5, 0.6, 0.7, 0.8, 0.9]
    trained = [0.5, 0.6, 0.7, 0.8, 0.9]

    result = _bootstrap_ci(baseline, trained, alpha=0.05)

    assert result["delta_mean"] == pytest.approx(0.0, abs=1e-6)
    assert result["p_value"] > 0.05
    assert result["significant"] is False
    assert result["method"] == "bootstrap_ci"


def test_bootstrap_ci_different():
    """Test that clearly different data produces p < 0.05 (significant)."""
    baseline = [0.1, 0.2, 0.3, 0.4, 0.5]
    trained = [0.6, 0.7, 0.8, 0.9, 1.0]

    result = _bootstrap_ci(baseline, trained, alpha=0.05)

    assert result["delta_mean"] > 0
    assert result["p_value"] < 0.05
    assert result["significant"] is True
    assert result["ci_lower"] > 0  # CI should be entirely positive


def test_bootstrap_ci_insufficient_data():
    """Test that insufficient data returns not significant result."""
    baseline = [0.5]
    trained = [0.6]

    result = _bootstrap_ci(baseline, trained, alpha=0.05)

    assert result["significant"] is False
    assert result["method"] == "insufficient_data"
    assert result["p_value"] == 1.0


def test_bootstrap_ci_custom_alpha():
    """Test that custom alpha threshold is respected."""
    baseline = [0.1, 0.2, 0.3, 0.4, 0.5]
    trained = [0.6, 0.7, 0.8, 0.9, 1.0]

    result = _bootstrap_ci(baseline, trained, alpha=0.01)

    assert result["alpha"] == 0.01
    assert result["significant"] is True
