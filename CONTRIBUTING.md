# Contributing to NightmareNet

Thank you for helping improve NightmareNet. This project uses a **research-first, verification-driven** workflow.

## Quick Start

```bash
git clone https://github.com/Adit-Jain-srm/NightmareNet.git
cd NightmareNet
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -e ".[dev,api]"
pytest tests/ -v --tb=short
ruff check .
```

## Development Standards

- **Python 3.9+** — use `Union[X, Y]` not `X | Y` in public APIs
- **No `from __future__ import annotations`** in `nightmarenet/api/` (Pydantic v2)
- **Line length:** 100 (ruff)
- **Tests:** mirror package structure under `tests/`
- **Commits:** conventional commits (`feat:`, `fix:`, `docs:`, `test:`)

## Before Opening a PR

1. `pytest tests/ -v --tb=short` — all tests must pass
2. `ruff check .` — zero errors
3. `cd frontend && npm run build` — if you changed frontend
4. Update `tasks/todo.md` if completing a planned milestone

## Architecture Boundaries

| Package | Purpose |
|---------|---------|
| `nightmarenet/` | OSS core — training, distortions, evaluation, CLI |
| `nightmarenet_server/` | Hosted platform — auth, DB, Celery (optional) |
| `frontend/` | Next.js dashboard |

OSS core must **not** depend on PostgreSQL, Redis, or hosted-only packages.

## Documentation

- PRD: `docs/architecture/PRD.md`
- TRD: `docs/architecture/TRD.md`
- API: `docs/api/openapi.yaml`
- Research: `docs/research/paper-outline.md`

## GPU Development

Dev machine: RTX 3050 Ti (4GB). Prefer DistilBERT/DistilGPT-2. For CUDA, use Python 3.12 venv with `torch` cu121 wheels.

## Questions

Open a GitHub issue or discussion with the `question` label.
