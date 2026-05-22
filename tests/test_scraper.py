"""Tests for the WebScraper module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from nightmarenet.data.scraper import WebScraper

# ── Fixtures ──


@pytest.fixture
def scraper():
    """Create a scraper with robots.txt and rate-limiting disabled for speed."""
    return WebScraper(delay=0, respect_robots=False, min_text_length=10)


SAMPLE_HTML = """
<html>
<head><title>Test</title></head>
<body>
  <nav><a href="/">Home</a></nav>
  <article>
    <h1>Machine Learning Overview</h1>
    <p>Machine learning is a subset of artificial intelligence that focuses on
    building systems that can learn from data. These systems improve their
    performance on specific tasks over time without being explicitly programmed.</p>
    <p>Common approaches include supervised learning, unsupervised learning,
    and reinforcement learning. Each paradigm has its own strengths and is
    suited to different types of problems.</p>
  </article>
  <footer>Copyright 2026</footer>
</body>
</html>
"""

MINIMAL_HTML = "<html><body><p>Too short</p></body></html>"


# ── Tests ──


class TestWebScraper:
    """Tests for WebScraper."""

    def test_extract_text_strips_nav_and_footer(self, scraper):
        """Text extraction should remove nav and footer elements."""
        text = WebScraper._extract_text(SAMPLE_HTML)
        assert "Home" not in text
        assert "Copyright" not in text
        assert "Machine Learning" in text

    def test_extract_text_preserves_paragraphs(self, scraper):
        """Paragraphs should be preserved as separate blocks."""
        text = WebScraper._extract_text(SAMPLE_HTML)
        assert "artificial intelligence" in text
        assert "supervised learning" in text

    @patch("nightmarenet.data.scraper.requests.get")
    def test_scrape_returns_dataset(self, mock_get, scraper):
        """scrape() should return a Dataset with a text column."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = SAMPLE_HTML
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        ds = scraper.scrape(["https://example.com/article"])
        assert "text" in ds.column_names
        assert len(ds) > 0

    @patch("nightmarenet.data.scraper.requests.get")
    def test_scrape_skips_short_pages(self, mock_get, scraper):
        """Pages with too little text should be skipped."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = MINIMAL_HTML
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        with pytest.raises(RuntimeError, match="No text could be extracted"):
            scraper.scrape(["https://example.com/tiny"])

    @patch("nightmarenet.data.scraper.requests.get")
    def test_scrape_multiple_urls(self, mock_get, scraper):
        """Scraping multiple URLs should produce chunks from all pages."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = SAMPLE_HTML
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        ds = scraper.scrape(["https://a.com/1", "https://b.com/2"])
        assert len(ds) >= 2  # At least one chunk per url

    def test_scrape_empty_urls_raises(self, scraper):
        """An empty URL list should raise ValueError."""
        with pytest.raises(ValueError, match="urls list must not be empty"):
            scraper.scrape([])

    def test_negative_delay_raises(self):
        """Negative delay should raise ValueError."""
        with pytest.raises(ValueError, match="delay must be >= 0"):
            WebScraper(delay=-1)

    @patch("nightmarenet.data.scraper.requests.get")
    def test_retry_on_failure(self, mock_get, scraper):
        """Transient failures should be retried."""
        import requests as req

        mock_get.side_effect = req.ConnectionError("timeout")

        # Should fail gracefully after retries
        text = scraper._fetch_url("https://example.com/flaky")
        assert text is None
        assert mock_get.call_count == scraper.max_retries

    @patch("nightmarenet.data.scraper.requests.get")
    def test_robots_txt_respected(self, mock_get):
        """When robots.txt disallows, scraper should skip URL."""
        scraper_with_robots = WebScraper(delay=0, respect_robots=True)

        with patch.object(scraper_with_robots, "_can_fetch", return_value=False):
            result = scraper_with_robots._fetch_url("https://example.com/blocked")
            assert result is None
            mock_get.assert_not_called()
