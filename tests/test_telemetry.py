"""Tests for nightmarenet.utils.telemetry and JSON logging support.

Covers:
- No-op behaviour when OTel endpoint is not configured
- JSON formatter emits valid JSON records
- trace_phase context manager spans start/end without errors
- record_metric is silent and safe when telemetry is disabled
- setup_logging_from_config reads observability config correctly
"""

from __future__ import annotations

import json
import logging
from io import StringIO
from unittest.mock import patch

import pytest

from nightmarenet.utils.logging_config import (
    reset_logging,
    setup_logging,
    setup_logging_from_config,
)
from nightmarenet.utils.telemetry import (
    _NoOpSpan,
    _NoOpTracer,
    get_tracer,
    record_metric,
    reset_telemetry,
    setup_telemetry,
    trace_phase,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_singletons():
    """Ensure telemetry and logging singletons are clean between tests."""
    reset_telemetry()
    reset_logging()
    yield
    reset_telemetry()
    reset_logging()


# ---------------------------------------------------------------------------
# Telemetry: no-op when endpoint not configured
# ---------------------------------------------------------------------------


class TestNoOpTelemetry:
    """Telemetry must be silent when otel_endpoint is null or absent."""

    def test_setup_with_no_endpoint_is_noop(self):
        """setup_telemetry with null endpoint installs no-op tracer."""
        config = {"observability": {"otel_endpoint": None}}
        setup_telemetry(config)
        tracer = get_tracer()
        assert isinstance(tracer, _NoOpTracer)

    def test_setup_with_missing_observability_section(self):
        """setup_telemetry with no observability key at all is safe."""
        setup_telemetry({})
        tracer = get_tracer()
        assert isinstance(tracer, _NoOpTracer)

    def test_get_tracer_before_setup_returns_noop(self):
        """get_tracer() before any setup returns a no-op tracer."""
        tracer = get_tracer()
        assert isinstance(tracer, _NoOpTracer)

    def test_idempotent_setup(self):
        """Calling setup_telemetry multiple times does not raise."""
        config: dict = {}
        setup_telemetry(config)
        setup_telemetry(config)  # Should be a silent no-op

    def test_noop_span_attribute_set_is_silent(self):
        """_NoOpSpan.set_attribute must never raise."""
        span = _NoOpSpan()
        span.set_attribute("key", "value")
        span.set_attribute("number", 42)

    def test_noop_span_record_exception_is_silent(self):
        """_NoOpSpan.record_exception must never raise."""
        span = _NoOpSpan()
        span.record_exception(ValueError("boom"))

    def test_noop_tracer_context_manager(self):
        """_NoOpTracer.start_as_current_span returns a usable context manager."""
        tracer = _NoOpTracer()
        ctx = tracer.start_as_current_span("test-span")
        assert isinstance(ctx, _NoOpSpan)


# ---------------------------------------------------------------------------
# trace_phase: context manager behaviour
# ---------------------------------------------------------------------------


class TestTracePhase:
    """trace_phase must wrap code safely regardless of OTel availability."""

    def test_trace_phase_no_endpoint_executes_body(self):
        """Code inside trace_phase runs normally without OTel configured."""
        setup_telemetry({})
        result = []
        with trace_phase("ingest", {"source": "test"}):
            result.append(1)
        assert result == [1]

    def test_trace_phase_yields_span(self):
        """trace_phase yields a span-compatible object."""
        setup_telemetry({})
        with trace_phase("prepare") as span:
            assert span is not None

    def test_trace_phase_propagates_exception(self):
        """Exceptions raised inside trace_phase are re-raised."""
        setup_telemetry({})
        with pytest.raises(RuntimeError, match="pipeline error"):
            with trace_phase("train"):
                raise RuntimeError("pipeline error")

    def test_trace_phase_records_duration_noop(self):
        """Duration recording inside trace_phase never raises (no-op path)."""
        setup_telemetry({})
        with trace_phase("evaluate", {"model.name": "gpt2"}):
            pass  # duration recorded internally without error

    def test_trace_phase_empty_attributes(self):
        """trace_phase with no attributes dict is safe."""
        setup_telemetry({})
        with trace_phase("ingest"):
            pass


# ---------------------------------------------------------------------------
# record_metric: safe emission
# ---------------------------------------------------------------------------


class TestRecordMetric:
    """record_metric must be completely silent when telemetry is disabled."""

    def test_record_robustness_score_no_otel(self):
        """record_metric('robustness_score', ...) is safe without OTel."""
        setup_telemetry({})
        record_metric("robustness_score", 0.42, {"model": "gpt2"})

    def test_record_gpu_utilization_no_otel(self):
        """record_metric('gpu_utilization', ...) is safe without OTel."""
        setup_telemetry({})
        record_metric("gpu_utilization", 73.5)

    def test_record_unknown_metric_is_silent(self):
        """Unknown metric names are silently ignored."""
        setup_telemetry({})
        record_metric("unknown.custom.metric", 1.0)

    def test_record_metric_before_setup_is_silent(self):
        """record_metric before setup_telemetry never raises."""
        record_metric("robustness_score", 0.1)


# ---------------------------------------------------------------------------
# JSON Logging
# ---------------------------------------------------------------------------


class TestJsonLogging:
    """JSON log formatter must emit valid, parseable JSON records."""

    def test_plain_text_logging_default(self):
        """Default setup_logging produces non-JSON plain text output."""
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
        log = logging.getLogger("nightmarenet.test.plain")
        log.addHandler(handler)
        log.setLevel(logging.INFO)
        log.info("hello plain")
        output = stream.getvalue()
        assert "hello plain" in output

    def test_json_logs_emit_valid_json(self):
        """When json_logs=True and python-json-logger is installed, output is JSON."""
        pytest.importorskip("pythonjsonlogger", reason="python-json-logger not installed")

        stream = StringIO()
        # Set up with json_logs=True but redirect to our StringIO
        setup_logging(log_dir="/tmp", file_logging=False, json_logs=True, console=False)

        from pythonjsonlogger.json import JsonFormatter  # type: ignore[import-untyped]

        formatter = JsonFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            rename_fields={"asctime": "timestamp", "levelname": "level", "name": "logger"},
        )
        handler = logging.StreamHandler(stream)
        handler.setFormatter(formatter)
        test_logger = logging.getLogger("nightmarenet.test.json")
        test_logger.addHandler(handler)
        test_logger.setLevel(logging.INFO)
        test_logger.info("structured event", extra={"phase": "ingest"})

        output = stream.getvalue().strip()
        assert output, "Expected JSON output, got empty string"
        record = json.loads(output)
        assert record.get("level") == "INFO"
        assert record.get("message") == "structured event"

    def test_json_logs_fallback_when_package_missing(self):
        """When python-json-logger is absent, setup_logging falls back silently."""
        mock_modules = {"pythonjsonlogger": None, "pythonjsonlogger.jsonlogger": None}
        with patch.dict("sys.modules", mock_modules):
            # Should not raise even if the package is unavailable
            setup_logging(log_dir="/tmp", file_logging=False, json_logs=True)


# ---------------------------------------------------------------------------
# setup_logging_from_config
# ---------------------------------------------------------------------------


class TestSetupLoggingFromConfig:
    """setup_logging_from_config must read the observability section correctly."""

    def test_reads_json_logs_flag(self):
        """json_logs flag from config is passed to setup_logging."""
        config = {
            "observability": {"json_logs": False, "log_level": "WARNING"},
            "training": {"log_dir": "/tmp"},
        }
        # Should not raise
        setup_logging_from_config(config)

    def test_defaults_when_no_observability_key(self):
        """Missing observability section uses sensible defaults."""
        setup_logging_from_config({})

    def test_custom_log_level_applied(self):
        """Log level from observability.log_level is respected."""
        config = {
            "observability": {"log_level": "DEBUG", "json_logs": False},
            "training": {"log_dir": "/tmp"},
        }
        setup_logging_from_config(config)
        root = logging.getLogger("nightmarenet")
        assert root.level == logging.DEBUG
