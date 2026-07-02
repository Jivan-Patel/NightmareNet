"""Tests for the `nightmarenet --version` CLI flag."""

import pytest

from nightmarenet import __version__
from nightmarenet.cli import build_parser


def test_version_flag_exits_zero(capsys):
    parser = build_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--version"])

    assert exc_info.value.code == 0


def test_version_flag_prints_installed_version(capsys):
    parser = build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["--version"])

    captured = capsys.readouterr()
    assert __version__ in captured.out
    assert "nightmarenet" in captured.out
