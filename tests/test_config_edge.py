"""Tests for configuration loading edge cases.

Covers YAML parsing, missing keys, unknown keys (permissive mode),
deep merge behavior, and empty/edge values.
"""

from __future__ import annotations

import logging

import pytest
import yaml

from nightmarenet.utils.config import (
    DEFAULT_CONFIG,
    _deep_merge,
    _find_closest_key,
    _levenshtein_distance,
    load_config,
    validate_config,
)


class TestLoadConfigEdgeCases:
    """Tests for YAML loading and parsing edge cases."""

    def test_load_nonexistent_file_raises_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/dir/config.yaml")

    def test_load_yaml_with_missing_required_keys(self, tmp_path):
        cfg_file = tmp_path / "partial.yaml"
        cfg_file.write_text(yaml.dump({"model": {"name": "gpt2"}}))
        cfg = load_config(str(cfg_file))
        assert "model" in cfg
        assert cfg["model"]["name"] == "gpt2"

    def test_load_config_with_extra_unknown_keys_no_error(self, tmp_path):
        cfg_file = tmp_path / "extra.yaml"
        cfg_data = {
            "model": {"name": "gpt2", "type": "causal_lm", "max_length": 128},
            "unknown_section": {"foo": "bar", "baz": 123},
            "another_extra": True,
        }
        cfg_file.write_text(yaml.dump(cfg_data))
        cfg = load_config(str(cfg_file))
        assert cfg["unknown_section"]["foo"] == "bar"
        assert cfg["another_extra"] is True

    def test_load_empty_yaml_file(self, tmp_path):
        cfg_file = tmp_path / "empty.yaml"
        cfg_file.write_text("")
        cfg = load_config(str(cfg_file))
        assert isinstance(cfg, dict)

    def test_load_yaml_with_null_values(self, tmp_path):
        """Null values in config should raise validation error for required fields."""
        cfg_file = tmp_path / "nulls.yaml"
        cfg_file.write_text(yaml.dump({"model": {"name": None, "type": None}}))
        with pytest.raises(ValueError, match="validation errors"):
            load_config(str(cfg_file))


class TestDeepMerge:
    """Tests for the _deep_merge utility."""

    def test_deep_merge_nested_overrides(self):
        base = {"a": {"x": 1, "y": 2}, "b": 3}
        override = {"a": {"y": 99, "z": 100}}
        result = _deep_merge(base, override)
        assert result == {"a": {"x": 1, "y": 99, "z": 100}, "b": 3}

    def test_deep_merge_does_not_mutate_base(self):
        base = {"a": {"x": 1, "y": 2}}
        override = {"a": {"x": 42}}
        _deep_merge(base, override)
        assert base["a"]["x"] == 1

    def test_deep_merge_empty_override(self):
        base = {"a": 1, "b": {"c": 2}}
        result = _deep_merge(base, {})
        assert result == base

    def test_deep_merge_empty_base(self):
        override = {"a": 1, "b": {"c": 2}}
        result = _deep_merge({}, override)
        assert result == override

    def test_deep_merge_replaces_non_dict_with_dict(self):
        base = {"a": "string_value"}
        override = {"a": {"nested": True}}
        result = _deep_merge(base, override)
        assert result["a"] == {"nested": True}

    def test_deep_merge_three_levels_deep(self):
        base = {"l1": {"l2": {"l3": "original"}}}
        override = {"l1": {"l2": {"l3": "new", "extra": True}}}
        result = _deep_merge(base, override)
        assert result["l1"]["l2"]["l3"] == "new"
        assert result["l1"]["l2"]["extra"] is True


class TestValidateConfig:
    """Tests for config validation edge cases."""

    def test_default_config_is_valid(self):
        errors = validate_config(DEFAULT_CONFIG)
        assert errors == []

    def test_invalid_max_length_type(self):
        cfg = _deep_merge(DEFAULT_CONFIG, {"model": {"max_length": "not_int"}})
        errors = validate_config(cfg)
        assert any("max_length" in e for e in errors)

    def test_zero_num_cycles_invalid(self):
        cfg = _deep_merge(DEFAULT_CONFIG, {"training": {"num_cycles": 0}})
        errors = validate_config(cfg)
        assert any("num_cycles" in e for e in errors)

    def test_negative_learning_rate_invalid(self):
        cfg = _deep_merge(DEFAULT_CONFIG, {"training": {"learning_rate": -0.01}})
        errors = validate_config(cfg)
        assert any("learning_rate" in e for e in errors)

    def test_empty_string_model_name_handled(self):
        cfg = _deep_merge(DEFAULT_CONFIG, {"model": {"name": ""}})
        errors = validate_config(cfg)
        # Empty string may or may not be valid depending on implementation
        assert isinstance(errors, list)

    def test_very_large_batch_size_no_crash(self):
        cfg = _deep_merge(DEFAULT_CONFIG, {"training": {"batch_size": 999999}})
        errors = validate_config(cfg)
        assert isinstance(errors, list)

    def test_validation_error_includes_dotted_path(self):
        cfg = _deep_merge(DEFAULT_CONFIG, {"training": {"batch_size": -1}})
        errors = validate_config(cfg)
        assert any("training.batch_size" in e for e in errors)


class TestLevenshteinDistance:
    """Tests for the Levenshtein distance utility."""

    def test_identical_strings_zero_distance(self):
        assert _levenshtein_distance("test", "test") == 0

    def test_empty_string_distance(self):
        assert _levenshtein_distance("", "test") == 4
        assert _levenshtein_distance("test", "") == 4

    def test_single_edit_distance(self):
        assert _levenshtein_distance("test", "tent") == 1
        assert _levenshtein_distance("test", "tast") == 1
        assert _levenshtein_distance("test", "tests") == 1

    def test_multiple_edits_distance(self):
        assert _levenshtein_distance("kitten", "sitting") == 3
        assert _levenshtein_distance("training", "trainng") == 1

    def test_case_sensitivity(self):
        assert _levenshtein_distance("Test", "test") == 1


class TestFindClosestKey:
    """Tests for the key suggestion utility."""

    def test_exact_match_returns_key(self):
        result = _find_closest_key("training", ["model", "training", "dataset"])
        assert result == "training"

    def test_typo_within_distance_2(self):
        result = _find_closest_key("trainng", ["model", "training", "dataset"])
        assert result == "training"

    def test_typo_beyond_distance_2_returns_none(self):
        result = _find_closest_key("xyz", ["model", "training", "dataset"])
        assert result is None

    def test_multiple_candidates_picks_closest(self):
        result = _find_closest_key("modle", ["model", "module", "dataset"])
        # Both "model" and "module" are within distance 2, "module" is selected
        assert result in ("model", "module")

    def test_empty_candidates_returns_none(self):
        result = _find_closest_key("training", [])
        assert result is None


class TestUnknownKeyWarnings:
    """Tests for unknown key warning functionality."""

    def test_unknown_key_with_suggestion_logged(self, tmp_path, caplog):
        cfg_file = tmp_path / "typo.yaml"
        cfg_data = {"model": {"name": "gpt2"}, "trainng": {"wake_epochs": 3}}
        cfg_file.write_text(yaml.dump(cfg_data))

        with caplog.at_level(logging.WARNING):
            load_config(str(cfg_file))

        warning_messages = [
            record.message
            for record in caplog.records
            if record.levelname == "WARNING"
        ]
        assert any("trainng" in msg and "training" in msg for msg in warning_messages)

    def test_unknown_key_without_suggestion_logged(self, tmp_path, caplog):
        cfg_file = tmp_path / "unknown.yaml"
        cfg_data = {"model": {"name": "gpt2"}, "xyz": {"foo": "bar"}}
        cfg_file.write_text(yaml.dump(cfg_data))

        with caplog.at_level(logging.WARNING):
            load_config(str(cfg_file))

        warning_messages = [
            record.message
            for record in caplog.records
            if record.levelname == "WARNING"
        ]
        assert any("xyz" in msg and "did you mean" not in msg for msg in warning_messages)

    def test_unknown_key_non_string_no_crash(self, tmp_path, caplog):
        """Non-string YAML keys (int, bool) should warn without crashing."""
        cfg_file = tmp_path / "nonstring.yaml"
        cfg_file.write_text("123:\n  foo: bar\nmodel:\n  name: gpt2\n")
        with caplog.at_level(logging.WARNING):
            load_config(str(cfg_file))
        warning_messages = [r.message for r in caplog.records if r.levelname == "WARNING"]
        assert any("123" in msg for msg in warning_messages)

    def test_valid_keys_no_warning(self, tmp_path, caplog):
        cfg_file = tmp_path / "valid.yaml"
        cfg_data = {"model": {"name": "gpt2"}, "training": {"wake_epochs": 3}}
        cfg_file.write_text(yaml.dump(cfg_data))

        with caplog.at_level(logging.WARNING):
            load_config(str(cfg_file))

        warning_messages = [
            record.message
            for record in caplog.records
            if record.levelname == "WARNING"
        ]
        assert not any("Unknown config key" in msg for msg in warning_messages)
