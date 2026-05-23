# NightmareNet 🧠💤

**Autonomous AI Self-Improvement Platform**

[![Tests](https://img.shields.io/badge/tests-288%2B%20passing-brightgreen)](#running-tests)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](#installation)
[![License](https://img.shields.io/badge/license-MIT-blue)](#license)
[![Phases](https://img.shields.io/badge/training-Wake%20%E2%86%92%20Dream%20%E2%86%92%20Nightmare%20%E2%86%92%20Compress-blueviolet)](#training-phases)

> *Models that don't just learn—they **harden** through sleep-inspired cycles: mild dream augmentation, adversarial nightmares, and synaptic compression.*

---

## Feature Surface

| Area | Capabilities |
|------|----------------|
| **Distortion API** | Dream + nightmare text generation, multi-strength robustness scoring |
| **Training pipeline** | 4-phase cycle, YAML configs, AMP, DDP, early stopping |
| **Pipeline orchestration** | Ingest (URL/file/HF/text), scrape, background runner, cancel/report |
| **CLI** | `nightmarenet train`, `distort`, `evaluate`, `benchmark` |
| **Dashboard** | PipelineLab wizard, Playground, Resilience Lab, live health matrix |
| **Plugins** | Custom distortion engines via registry |
| **Compliance (roadmap)** | EU AI Act Article 15 export, audit trail |

---

## Overview

NightmareNet is a biologically inspired training framework that introduces **dream** and **nightmare** phases to improve model generalization and robustness. Instead of relying solely on scaling data and parameters, NightmareNet incorporates:

- **Synthetic distortion** (Dream Phase)
- **Controlled forgetting** (Compression Phase)
- **Adversarial stress testing** (Nightmare Phase)

This forces models to learn **invariant structures** rather than memorize patterns.

### Platform Vision

NightmareNet is evolving from a single-model training tool into a **multi-tenant SaaS platform** where organizations deploy AI systems that continuously learn, stress-test themselves, and improve via Dream + Nightmare cycles:

```
Users (Org A, B, C...)
        │
        ▼
┌──────────────────────────────┐
│     API Gateway (Auth)       │
└────────────┬─────────────────┘
             ▼
┌──────────────────────────────┐
│ Multi-Tenant Control Plane   │
│ - User & project management  │
│ - Pipeline orchestration     │
└────────────┬─────────────────┘
             ▼
┌────────────────────────────────────────────┐
│              Data Plane                    │
│  ┌──────────────┐  ┌──────────────┐        │
│  │ Dream Engine │  │ Nightmare    │        │
│  │              │  │ Engine       │        │
│  └──────┬───────┘  └──────┬───────┘        │
│         ▼                  ▼               │
│  ┌─────────────────────────────────────┐   │
│  │ Self-Improvement Orchestrator       │   │
│  │ (Evaluation + Feedback + Metrics)   │   │
│  └─────────────────────────────────────┘   │
└────────────────────────────────────────────┘
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│                Training Pipeline                 │
│                                                  │
│   ┌─────────┐   ┌─────────┐   ┌───────────┐    │
│   │  Wake   │──▶│  Dream  │──▶│ Nightmare │    │
│   │ Phase   │   │  Phase  │   │   Phase   │    │
│   └─────────┘   └─────────┘   └───────────┘    │
│       │                             │           │
│       │         ┌───────────┐       │           │
│       └────────▶│ Compress  │◀──────┘          │
│                 │   Phase   │                   │
│                 └───────────┘                   │
│                      │                          │
│                 ┌────▼─────┐                    │
│                 │ Evaluate │                    │
│                 └──────────┘                    │
└─────────────────────────────────────────────────┘
```

### Training Phases

| Phase | Description | Data |
|-------|-------------|------|
| **Wake** | Standard supervised fine-tuning | Real-world data |
| **Dream** | Training on mildly distorted data | Synthetic dream data (strength 0.2–0.3) |
| **Nightmare** | Stress-testing on extreme perturbations | Adversarial nightmare data (strength 0.7–0.9) |
| **Compression** | Pruning & bottleneck to force abstraction | N/A (model surgery) |

### Distortion Types

- **Text-level**: character swaps, typos, word shuffling, token masking
- **Semantic-level**: synonym replacement, negation injection, topic splicing
- **Adversarial**: contradictory premises, ambiguous queries, cross-domain prompts

## Installation

```bash
# Clone the repository
git clone https://github.com/Adit-Jain-srm/NightmareNet.git
cd NightmareNet

# Install core dependencies
pip install -e .

# Install with dev tools (pytest, ruff)
pip install -e ".[dev]"

# Install with API server support
pip install -e ".[api]"
```

## Quick Start

### 1. Generate Dream & Nightmare Data

```bash
python scripts/generate_data.py --config configs/default.yaml --output data/generated/
```

### 2. Run Full Training Pipeline

```bash
python scripts/train.py --config configs/default.yaml
```

### 3. Evaluate a Checkpoint

```bash
python scripts/evaluate.py --checkpoint checkpoints/best_model --config configs/default.yaml
```

### 4. Start the API Server

```bash
pip install -e ".[api]"
uvicorn nightmarenet.api.app:app --host 0.0.0.0 --port 8000
```

API endpoints:
- `POST /api/v1/generate/dream` — Generate dream-distorted text
- `POST /api/v1/generate/nightmare` — Generate nightmare-distorted text
- `POST /api/v1/evaluate/robustness` — Evaluate text robustness score
- `GET /api/v1/health` — Health check

## Configuration

All hyperparameters are controlled via `configs/default.yaml`:

```yaml
model:
  name: gpt2
  max_length: 128

training:
  wake_epochs: 3
  dream_epochs: 2
  nightmare_epochs: 1
  num_cycles: 3
  learning_rate: 5.0e-5

distortion:
  dream_strength: 0.25
  nightmare_strength: 0.8

compression:
  pruning_ratio: 0.2
```

Config loading uses schema validation with defaults merging—see `nightmarenet/utils/config.py`.

## Expected Outcomes

| Metric | Baseline Model | DreamPhase Model |
|--------|---------------|-----------------|
| Recall | High | Moderate |
| Generalization | Medium | High |
| Robustness | Low | High |
| Hallucination | High | Reduced |

## Project Structure

```
NightmareNet/
├── nightmarenet/          # Core library
│   ├── api/               # FastAPI platform service
│   ├── data/              # Dataset loading & generation
│   ├── distortions/       # Text, semantic, adversarial distortions
│   ├── training/          # Phase-based training pipeline
│   ├── compression/       # Pruning & bottleneck utilities
│   ├── evaluation/        # Metrics & evaluation engine
│   └── utils/             # Validation, config, logging
├── configs/               # YAML configuration files
├── scripts/               # CLI entry points
├── tests/                 # Unit & edge-case tests
├── notebooks/             # Demo notebooks
└── data/                  # Raw & generated datasets
```

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=nightmarenet --cov-report=term-missing
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'nightmarenet'` | Run `pip install -e .` from the repo root |
| `FileNotFoundError: Configuration file not found` | Verify the `--config` path exists; default is `configs/default.yaml` |
| `ValueError: Configuration validation errors` | Check your YAML against the schema in `nightmarenet/utils/config.py` |
| `CUDA out of memory` | Reduce `batch_size` or `max_length` in config, or set `device: cpu` |
| `KeyError` on dataset columns | Ensure your dataset has the column specified in `dataset.text_column` |
| Tests fail with import errors | Run `pip install -e ".[dev]"` to install test dependencies |

## Production Hardening

All modules include:
- **Input validation** — strength, ratio, type, and range checks via `nightmarenet/utils/validation.py`
- **Error isolation** — try/except with fallback behavior in distortion pipelines
- **NaN/Inf guards** — loss checks during training phases
- **Graceful shutdown** — SIGINT handling with checkpoint saves
- **Structured logging** — configurable via `nightmarenet/utils/logging_config.py`
- **Config schema validation** — type and range checks on all YAML fields

## License

MIT