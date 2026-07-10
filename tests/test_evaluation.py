"""Tests for evaluation metrics and comparison."""

import numpy as np
import pytest
from scipy import stats


def _bootstrap_ci(
    baseline: list[float],
    trained: list[float],
    n_bootstrap: int = 10000,
    alpha: float = 0.05,
) -> dict:
    """Compute bootstrap confidence interval for paired differences.

    Args:
        baseline: List of baseline metric values (e.g., per-strength scores).
        trained: List of trained metric values (same length as baseline).
        n_bootstrap: Number of bootstrap samples.
        alpha: Significance level for CI (default 0.05 for 95% CI).

    Returns:
        Dict with delta_mean, ci_lower, ci_upper, p_value, and significant flag.
    """
    if len(baseline) != len(trained) or len(baseline) < 2:
        return {
            "delta_mean": 0.0,
            "ci_lower": 0.0,
            "ci_upper": 0.0,
            "p_value": 1.0,
            "significant": False,
            "method": "insufficient_data",
        }

    baseline_arr = np.array(baseline)
    trained_arr = np.array(trained)
    deltas = trained_arr - baseline_arr
    delta_mean = float(np.mean(deltas))

    # Bootstrap resampling
    n = len(deltas)
    bootstrap_deltas = []
    for _ in range(n_bootstrap):
        indices = np.random.choice(n, size=n, replace=True)
        bootstrap_deltas.append(np.mean(deltas[indices]))

    bootstrap_deltas = np.array(bootstrap_deltas)
    ci_lower = float(np.percentile(bootstrap_deltas, 100 * alpha / 2))
    ci_upper = float(np.percentile(bootstrap_deltas, 100 * (1 - alpha / 2)))

    # Paired t-test p-value
    try:
        _, p_value = stats.ttest_rel(trained_arr, baseline_arr)
        p_value = float(p_value)
        # Handle NaN from identical data (zero variance)
        if np.isnan(p_value) or np.isinf(p_value):
            p_value = 1.0
    except Exception:
        p_value = 1.0

    # Significant if CI doesn't include 0 and p < alpha
    significant = (ci_lower > 0 or ci_upper < 0) and p_value < alpha

    return {
        "delta_mean": delta_mean,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "p_value": p_value,
        "significant": significant,
        "method": "bootstrap_ci",
        "alpha": alpha,
    }


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
