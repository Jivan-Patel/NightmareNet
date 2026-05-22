"""Tests for the DataIngestor module."""

from __future__ import annotations

import json
import os
import tempfile

import pytest

from nightmarenet.data.ingest import DataIngestor


@pytest.fixture
def ingestor():
    return DataIngestor(text_column="text", max_samples=None, seed=42)


# ── TXT ingestion ──


class TestTxtIngestion:
    def test_load_txt_paragraphs(self, ingestor):
        """Paragraphs separated by blank lines become samples."""
        content = "\n\n".join([
            f"This is paragraph number {i} with enough text to pass the filter threshold."
            for i in range(20)
        ])
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8",
        ) as f:
            f.write(content)
            path = f.name

        try:
            ds = ingestor.from_file(path)
            assert "text" in ds.column_names
            assert len(ds) >= 10
        finally:
            os.unlink(path)

    def test_load_txt_fallback_to_lines(self, ingestor):
        """When no blank-line paragraphs, fall back to single-line splitting."""
        content = "\n".join([
            f"Line {i}: This contains enough text to be a valid training sample."
            for i in range(20)
        ])
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8",
        ) as f:
            f.write(content)
            path = f.name

        try:
            ds = ingestor.from_file(path)
            assert len(ds) >= 10
        finally:
            os.unlink(path)


# ── CSV ingestion ──


class TestCsvIngestion:
    def test_load_csv(self, ingestor):
        """CSV with a text column should be loaded."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8",
        ) as f:
            f.write("text,label\n")
            for i in range(20):
                f.write(f"\"This is sample {i} with meaningful content for training.\",{i}\n")
            path = f.name

        try:
            ds = ingestor.from_file(path)
            assert "text" in ds.column_names
            assert len(ds) >= 10
        finally:
            os.unlink(path)

    def test_csv_missing_column_raises(self, ingestor):
        """CSV without the expected text column should raise."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8",
        ) as f:
            f.write("content,label\n")
            f.write("hello,1\n")
            path = f.name

        try:
            with pytest.raises(ValueError, match="text"):
                ingestor.from_file(path)
        finally:
            os.unlink(path)


# ── JSONL ingestion ──


class TestJsonlIngestion:
    def test_load_jsonl(self, ingestor):
        """JSONL with a text key should be loaded."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False, encoding="utf-8",
        ) as f:
            for i in range(20):
                f.write(json.dumps({"text": f"Sample {i}: enough text for training."}) + "\n")
            path = f.name

        try:
            ds = ingestor.from_file(path)
            assert len(ds) >= 10
        finally:
            os.unlink(path)

    def test_jsonl_skips_malformed(self, ingestor):
        """Malformed JSONL lines should be skipped without crashing."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False, encoding="utf-8",
        ) as f:
            for i in range(15):
                f.write(json.dumps({"text": f"Valid sample {i} with real content."}) + "\n")
            f.write("this is not json\n")
            f.write('{"text": "Another valid sample at the end."}\n')
            path = f.name

        try:
            ds = ingestor.from_file(path)
            assert len(ds) >= 10
        finally:
            os.unlink(path)


# ── Text content ingestion ──


class TestTextContent:
    def test_from_text_content(self, ingestor):
        """Raw text should be split into paragraphs."""
        content = "\n\n".join([
            f"Paragraph {i}: This is a valid paragraph with substantial training text."
            for i in range(15)
        ])
        ds = ingestor.from_text_content(content)
        assert len(ds) >= 10

    def test_empty_content_raises(self, ingestor):
        """Empty text content should raise."""
        with pytest.raises(ValueError):
            ingestor.from_text_content("")


# ── Edge cases ──


class TestEdgeCases:
    def test_unsupported_extension_raises(self, ingestor):
        """Unsupported file types should raise ValueError."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".xml", delete=False,
        ) as f:
            f.write("<root>hello</root>")
            path = f.name

        try:
            with pytest.raises(ValueError, match="Unsupported file extension"):
                ingestor.from_file(path)
        finally:
            os.unlink(path)

    def test_file_not_found_raises(self, ingestor):
        """Non-existent file paths should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            ingestor.from_file("/nonexistent/path/data.txt")

    def test_max_samples_caps_output(self):
        """max_samples should limit the output dataset size."""
        ingestor = DataIngestor(max_samples=15)
        content = "\n\n".join([
            f"Paragraph {i}: This paragraph has plenty of content for model training purposes."
            for i in range(50)
        ])
        ds = ingestor.from_text_content(content)
        assert len(ds) <= 15
