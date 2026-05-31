# NightmareNet Improvement Plan — Task Tracker

## Phase 1: P0 — Performance, Security & CI
- [x] Step 1.1: Mixed-Precision Training (AMP) + Gradient Checkpointing
- [x] Step 1.2: API Authentication & Rate Limiting
- [x] Step 1.3: CI/CD Pipeline (GitHub Actions)
- [x] Phase 1 Verification: 164 tests pass, no regressions

## Phase 2: P1 — Observability, Scalability & Deployment
- [x] Step 2.1: Wandb/TensorBoard Experiment Tracking
- [x] Step 2.2: Streaming Dataset Support
- [x] Step 2.3: Dockerfile & Docker Compose
- [x] Phase 2 Verification: 164 tests pass

## Phase 3: P2 — Research Capabilities
- [x] Step 3.1: Multi-Model Architecture Support
- [x] Step 3.2: Learned Adversarial Distortions
- [x] Phase 3 Verification: 169 tests pass (5 new learned adversarial tests)

## Review
All 3 phases implemented and verified. 169 tests passing.

---

## Phase 5: PR Review Hardening (current)
- [x] Fix SlowAPIMiddleware not registered (rate limiting was a no-op)
- [x] Fix CORS origins not stripped of whitespace
- [x] Remove hardcoded `tests_passing=159` from health endpoint
- [x] Fix DDP save races: tokenizer + history gated behind main process
- [x] Gate tracker creation behind `dist_ctx.is_main_process`
- [x] Fix 22+ Ruff line-length violations across 8 files
- [x] Add `test_integration.py` — end-to-end pipeline tests
- [x] Update documentation (overview, lessons, todo)

## Phase 6: Full Lint Cleanup
- [x] Move ruff `select` to `lint.select` (fix deprecated config warning)
- [x] Ignore UP007/UP045 in ruff config (incompatible with Python 3.9 target)
- [x] Fix I001: import sorting across all files (auto-fixed)
- [x] Fix F401: remove unused imports (Dataset, CyclicScheduler, Optional, os, pytest)
- [x] Fix B904: add `from e`/`from None` to all `raise` in except blocks (app.py)
- [x] Fix E402: move distortion imports inside try/except block (app.py)
- [x] Fix B008: move `Body(...)` to module-level singletons (app.py)
- [x] Fix B023: bind loop variable in lambda via default arg (metrics.py)
- [x] Fix E721: use `is` instead of `==` for type comparison (config.py)
- [x] Fix N805: rename `self_dl` to `self` in test helper classes (test_metrics.py)
- [x] Fix B007: prefix unused loop vars with `_` (pruning.py, test_phases.py)
- [x] Fix F841: remove unused `dataset` variable (test_metrics.py)
- [x] Fix N812: add `# noqa: N812` for `torch.nn.functional as F` (phases.py)
- [x] Fix UP035: import `Iterator`/`Sequence` from `collections.abc` (scheduler.py, validation.py)
- [x] Fix UP015: remove unnecessary open mode `"r"` (config.py)
- [x] `ruff check` passes clean — 0 errors
- [x] All 206 tests passing

---

## Verification Audit (April 2, 2026)

All 18 improvement suggestions verified against actual code. 3 subagents used for parallel audit.

### ✅ PASS — Fully Implemented & Correct (11/18)
| # | Suggestion | Files |
|---|-----------|-------|
| 1 | Multi-model support (encoder models) | trainer.py, config.py, metrics.py, evaluator.py, default.yaml |
| 2 | Mixed-precision training (AMP) | trainer.py, phases.py (all 4 phases), config.py, default.yaml |
| 3 | Gradient checkpointing | trainer.py, config.py, default.yaml |
| 4 | Learned adversarial distortions | learned.py, adversarial.py, config.py, default.yaml, test_distortions.py |
| 5 | Wandb/TensorBoard integration | tracking.py, trainer.py, evaluator.py, train.py, evaluate.py, pyproject.toml |
| 6 | Streaming datasets | loader.py, generator.py, trainer.py, config.py, default.yaml |
| 7 | API Authentication | auth.py, app.py, schemas.py, test_api.py |
| 8 | Rate limiting | app.py, pyproject.toml |
| 9 | Dockerfile & Docker Compose | Dockerfile, docker-compose.yml, .dockerignore |
| 10 | CI/CD pipeline | ci.yml, release.yml |
| 11 | Classification metrics | metrics.py (classification_metrics), evaluator.py |

### ⚠️ FIXED DURING AUDIT (2/18)
| # | Issue | Fix Applied |
|---|-------|------------|
| 12 | `--tracker` in evaluate.py was a dead flag — no tracker created/passed | Added `create_tracker_from_config()` + pass `tracker=` to Evaluator + `tracker.finish()` |
| 13 | evaluate.py hardcoded `AutoModelForCausalLM` — ignored model.type config | Now uses `_MODEL_TYPE_MAP` dispatch from trainer.py |

### ⚠️ PARTIAL — Now Completed (2/18)
| # | Suggestion | Resolution |
|---|-----------|------------|
| 14 | Early stopping | ✅ IMPLEMENTED — Patience-based convergence detection in `AdaptiveScheduler`. Config keys: `early_stopping`, `early_stopping_patience`, `early_stopping_min_delta`. Trainer checks `should_stop` after each phase. 5 tests. |
| 15 | Type hints | ✅ IMPLEMENTED — Annotations added to phases.py, trainer.py, config.py. mypy added to CI. `py.typed` marker created. mypy config in pyproject.toml. |

### 🔇 EXCLUDED — Assessed & Resolved (4/18)
| # | Suggestion | Resolution |
|---|-----------|------------|
| 16 | Distributed training (DDP) | ✅ IMPLEMENTED via HuggingFace Accelerate — `DistributedContext` wrapper in `distributed.py`. Graceful fallback when accelerate absent. 10 tests. |
| 17 | Multilingual support | ⏹️ SKIPPED — Distortions (char_swap, keyboard_typo, synonym_replace) are English-specific. Requires per-language distortion strategies — not feasible as a standalone change. |
| 18 | Downstream task evaluation (GLUE) | ✅ IMPLEMENTED — `glue.py` module with SST-2, MRPC, QNLI, RTE, CoLA tasks. Integrated into Evaluator. 10 tests. |
| — | Config schema as Pydantic models | ⏹️ SKIPPED — Current dict-based validation is sufficient. Would require refactoring 180+ `config.get()` calls for marginal benefit. |

### ❌ NOT IN PLAN (2/18)
| # | Suggestion | Notes |
|---|-----------|-------|
| 19 | Distortion strength auto-tuning | No adaptive mechanism for dream/nightmare strengths |
| 20 | Caching distorted datasets | No content-hash caching; regenerated each run |

---

## Strategic Plan Execution (2026-05-23)

### Completed
- [x] Environment: gitnexus index (2280 nodes), code-review-graph build, `.env` + gitignore
- [x] Stabilize WIP: 288+ tests, ruff clean, frontend build, 4 atomic commits
- [x] Architecture: `nightmarenet_server/` package, CLI (`nightmarenet`), distortion registry, training callbacks
- [x] Docs: PRD, TRD, database schema, paper outline, OpenAPI spec, benchmark v1 protocol
- [x] Benchmark configs: `configs/benchmark_sst2.yaml` + baseline
- [x] CONTRIBUTING.md, CI frontend build job
- [x] UI primitives: `Button`, `Card` in `frontend/src/components/ui/`
- [x] Pipeline progress: `on_progress` in trainer + pipeline `progress_pct` mapping (15–85% training band)
- [x] PipelineLab: phase index resolver, progress % in metrics, `Button` CTAs
- [x] Hosted scaffold: SQLAlchemy models (`User`, `Org`, `Run`, …) + JWT helpers
- [x] Benchmark runner: `scripts/run_benchmark.py` (`--quick` distortion smoke)

### In Progress / Next
- [x] Dark mode toggle with system preference detection
- [x] Custom NightmareNet SVG logo component
- [x] Dashboard navigation from landing page (Hero, Navbar, Footer)
- [x] GSAP animations (floating orbs in Hero)
- [x] Light mode CSS overrides (glass, cards, navbar, terminal)
- [x] Fix Node.js process spawning (removed stray lockfile from user home)
- [x] Fix .env loading (added python-dotenv to app.py)
- [x] Fix npm vulnerabilities (upgraded Next.js to 16.2.6)
- [x] Merge to main + push (GitHub contributions now count)
- [ ] Run full benchmark on GPU (Python 3.12 + cu121 venv)
- [ ] WebSocket live progress (replace 3s polling in PipelineLab)
- [ ] Hosted platform: FastAPI routes + Celery workers wired to models
- [ ] README feature-dense rewrite (DarkLead-style panel catalog)
- [ ] Colab quickstart notebooks (3)
