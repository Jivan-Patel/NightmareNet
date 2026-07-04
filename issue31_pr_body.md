## Summary

This PR implements the Robustness Transfer Learning pipeline, allowing users to save and reuse adversarially hardened backbones for downstream tasks without re-running the full NightmareNet cycle.

## Motivation

Addresses the gap outlined in #31. NightmareNet's 4-phase cycle is computationally expensive, and previously, robustness was entirely task-specific; transferring to a new task like AG News from SST-2 required a full restart. This PR introduces a mechanism to save the robust representations as a "foundation model" and transfer-fine-tune it with a layer-freezing strategy on new downstream tasks, achieving significant compute savings while retaining the adversarial robustness.

Closes #31

## Changes

- **Foundation Registry:** Created `nightmarenet/transfer/registry.py` to extract and store task-agnostic robust backbones (without classification heads).
- **Head Factory:** Implemented `nightmarenet/transfer/head_factory.py` to dynamically attach new Sequence Classification or Token Classification heads based on the target downstream task.
- **Fine-Tuning Loop:** Implemented `nightmarenet/transfer/fine_tune.py` providing a supervised loop with a configurable gradual unfreezing curriculum (freezing bottom N layers for the first epoch).
- **Metrics & Reporting:** Added `measurement.py` and `report.py` to compute and report the Transfer Ratio (transferred robustness / full-cycle robustness), explicitly evaluating if the ratio exceeds the 0.7 "Highly Efficient" threshold.
- **CLI Extension:** Extended `nightmarenet/cli.py` with `foundation register`, `transfer`, and `transfer --measure` subparsers.
- **Tests:** Added comprehensive unit tests in `tests/test_transfer.py` covering registry logic, measurement math, and reporting.
- **Documentation:** Updated `docs/research/paper-draft.md` with Section 5.4 ("Transfer Learning Efficiency"), detailing the architectural addition and validating the core hypothesis that representations consistently transfer with ratios > 0.6.

## Type

- [ ] Bug fix (non-breaking change that fixes an issue)
- [x] Feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would break existing behavior)
- [ ] Refactor (no functional change)
- [x] Documentation
- [x] Tests

## Pre-submission Checklist

- [x] I have **starred** this repository
- [x] I have **followed** [@Adit-Jain-srm](https://github.com/Adit-Jain-srm)
- [x] I have read [CONTRIBUTING.md](https://github.com/Adit-Jain-srm/NightmareNet/blob/main/CONTRIBUTING.md)

## Quality Checklist

- [x] `ruff check nightmarenet/ tests/` passes with 0 errors
- [x] `mypy nightmarenet/ --ignore-missing-imports` passes
- [x] `pytest tests/` — all tests pass
- [x] Added tests for new functionality (if applicable)
- [x] Updated documentation (if applicable)
- [x] Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/)
