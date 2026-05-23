# Benchmark v1 — NightmareNet vs Baseline (SST-2)

## Objective

Demonstrate measurable robustness improvement from the 4-phase cycle vs wake-only fine-tuning on a CPU-friendly task.

## Setup

| Item | Value |
|------|-------|
| Dataset | GLUE SST-2 (subset 2000 samples) |
| Model | `distilbert-base-uncased` |
| Device | CPU (dev) / CUDA when available |
| Seeds | 42 (training), 42 (evaluation) |

## Configs

- **NightmareNet:** `configs/benchmark_sst2.yaml` (Wake→Dream→Nightmare→Compress)
- **Baseline:** `configs/benchmark_sst2_baseline.yaml` (Wake only, matched total epochs)

## Commands

```bash
pip install -e ".[dev]"

# Baseline
python scripts/train.py --config configs/benchmark_sst2_baseline.yaml

# Full cycle
python scripts/train.py --config configs/benchmark_sst2.yaml

# Robustness sweep (API or CLI)
nightmarenet distort --type nightmare --strength 0.7 --text "Sample sentence for eval."
```

## Metrics

1. **Clean accuracy** — validation set, no distortion
2. **Robustness score** — multi-strength evaluation (`/api/v1/evaluate/robustness`)
3. **Adversarial retention** — accuracy under dream/nightmare-augmented validation batches

## Success Criteria

- NightmareNet robustness score ≥ **10% higher** than baseline at strength ≥ 0.5
- Clean accuracy drop ≤ **2%** vs baseline (acceptable tradeoff)

## Reproducibility

Record: git commit, config hashes, `pytest` count, torch version, device in `results/benchmark-v1.json` (create on first run).
