## Summary

This PR addresses issue #40 by adding missing unit test coverage for `DataIngestor` methods in `tests/test_ingest.py`.

## Changes
- **URL Ingestion**: Added a mock test for `DataIngestor.from_urls` verifying that `WebScraper` is properly instantiated and called.
- **HuggingFace Hub Ingestion**: Added a mock test for `DataIngestor.from_huggingface` verifying that `DatasetWrapper` is properly utilized.
- **Minimum Threshold Validation**: Added a test explicitly verifying the `ValueError` raised in `_finalise` when the ingested sample count is below `_MIN_SAMPLES` (10).

Closes #40

## Type
- [x] Bug fix (non-breaking change that fixes an issue)
- [ ] Feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would break existing behavior)
- [ ] Refactor (no functional change)
- [ ] Documentation
- [x] Tests

## Quality Checklist
- [x] `ruff check nightmarenet/ tests/` passes with 0 errors
- [x] `mypy nightmarenet/ --ignore-missing-imports` passes
- [x] `pytest tests/` — all tests pass
- [x] Added tests for new functionality (if applicable)
- [x] Updated documentation (if applicable)
- [x] Commit messages follow Conventional Commits
