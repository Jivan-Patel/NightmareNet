"""Tests for Adaption Labs dataset optimization wrapper."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from nightmarenet.data.adaption import AdaptionOptimizer


class TestAdaptionOptimizerUnavailable:
    def test_optimize_returns_none_without_sdk(self, monkeypatch):
        monkeypatch.delenv("ADAPTION_API_KEY", raising=False)
        with patch("nightmarenet.data.adaption.Adaption", None):
            optimizer = AdaptionOptimizer()
            assert optimizer.optimize_dataset([], {"prompt": "text"}) is None

    def test_estimate_returns_none_without_key(self, monkeypatch):
        monkeypatch.delenv("ADAPTION_API_KEY", raising=False)
        optimizer = AdaptionOptimizer(api_key=None)
        assert optimizer.estimate_cost([], {"prompt": "text"}) is None


class TestAdaptionOptimizerWithMockClient:
    @pytest.fixture
    def mock_dataset(self):
        ds = MagicMock()
        ds.__len__.return_value = 2
        ds.column_names = ["text", "label"]
        ds.select.return_value = ds
        ds.__iter__.return_value = iter(
            [{"text": "hello", "label": "1"}, {"text": "world", "label": "0"}]
        )
        return ds

    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        upload = MagicMock(dataset_id="ds-123")
        client.datasets.upload_file.return_value = upload
        client.datasets.wait_for_completion.return_value = MagicMock(status="completed")
        client.datasets.download.return_value = "https://example.com/out.csv"
        client.datasets.get_status.return_value = MagicMock(row_count=2, status="completed")
        return client

    def test_optimize_dataset_success(self, mock_dataset, mock_client, monkeypatch, tmp_path):
        monkeypatch.setenv("ADAPTION_API_KEY", "test-key")
        out_csv = tmp_path / "optimized.csv"
        out_csv.write_text("text,label\nhello,1\nworld,0\n", encoding="utf-8")

        def _fake_urlretrieve(_url, path):
            import shutil

            shutil.copy(out_csv, path)

        with patch("nightmarenet.data.adaption.Adaption", MagicMock(return_value=mock_client)):
            with patch("urllib.request.urlretrieve", side_effect=_fake_urlretrieve):
                with patch("datasets.Dataset") as mock_hf:
                    mock_hf.from_csv.return_value = MagicMock(__len__=lambda _s: 2)
                    optimizer = AdaptionOptimizer()
                    result = optimizer.optimize_dataset(
                        mock_dataset, {"prompt": "text", "completion": "label"}, max_rows=2
                    )

        assert result is not None
        optimized, quality = result
        assert optimized is not None
        assert quality["row_count"] == 2

    def test_estimate_cost(self, mock_dataset, mock_client, monkeypatch):
        monkeypatch.setenv("ADAPTION_API_KEY", "test-key")
        mock_client.datasets.run.return_value = MagicMock(
            estimated_credits_consumed=1.5,
            estimated_minutes=2.0,
        )

        with patch("nightmarenet.data.adaption.Adaption", MagicMock(return_value=mock_client)):
            optimizer = AdaptionOptimizer()
            estimate = optimizer.estimate_cost(mock_dataset, {"prompt": "text"})

        assert estimate == {"credits": 1.5, "estimated_minutes": 2.0, "dataset_id": "ds-123"}
