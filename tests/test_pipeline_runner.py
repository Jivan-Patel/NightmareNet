"""Tests for pipeline runner registry behavior."""

from unittest.mock import MagicMock

import pytest

from nightmarenet.pipeline_runner import PipelineRunner, register_runner


class _FakePipeline:
    def cancel(self) -> None:
        pass


def test_register_evicts_completed_runners_first(monkeypatch) -> None:
    import nightmarenet.pipeline_runner as pr

    monkeypatch.setattr(pr, "_MAX_RUNNERS", 2)
    pr._runners.clear()
    r1 = PipelineRunner(_FakePipeline())
    r2 = PipelineRunner(_FakePipeline())
    register_runner(r1)
    register_runner(r2)
    r3 = PipelineRunner(_FakePipeline())
    register_runner(r3)
    assert r1.id not in pr._runners
    assert r2.id in pr._runners
    assert r3.id in pr._runners


def test_register_raises_when_registry_at_cap_and_all_running(monkeypatch) -> None:
    import nightmarenet.pipeline_runner as pr

    monkeypatch.setattr(pr, "_MAX_RUNNERS", 1)
    pr._runners.clear()
    r1 = PipelineRunner(_FakePipeline())
    t = MagicMock()
    t.is_alive.return_value = True
    r1._thread = t
    register_runner(r1)
    r2 = PipelineRunner(_FakePipeline())
    with pytest.raises(RuntimeError, match="capacity"):
        register_runner(r2)
