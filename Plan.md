NightmareNet: End-to-End Strategic Plan

1. Innovation Thesis (Validated)

NightmareNet is the first platform that actively improves model robustness through biologically-grounded training cycles, rather than merely detecting or measuring vulnerabilities.

Core insight: adversarial training causes "robustness forgetting" (2025 AAAI/ICCV). NightmareNet's 4-phase sleep cycle addresses this through cyclic consolidation — the mechanism biological sleep uses to protect memories.

Defensible novelty: No published work combines all of:





Biologically-grounded 4-phase cycle for adversarial robustness (not representation learning)



Dream = generative augmentation for diversity (not replay)



Nightmare = curriculum adversarial hardening (REM threat simulation)



Compress = distillation after hardening (synaptic homeostasis)



Self-referential loop: compressed model restarts the cycle

Closest prior art: PAD (Deperrois 2022) targets unsupervised representation learning, no compression. NightmareNet targets supervised adversarial robustness with integrated compression.



2. Product Requirements Document (PRD)

Problem Statement

ML models deployed in production silently degrade under distribution shift and adversarial inputs. Existing tools (ART, TextAttack) detect or measure robustness but don't improve it. No platform provides autonomous, cyclic hardening that prevents robustness forgetting.

Target Users (Priority)





ML Engineer — needs reliable production models without manual stress-testing



Startup ML Team — needs 5-minute CI robustness check before deploy



AI Safety/Red Team — needs scalable adversarial evaluation with regression tracking



Researcher — needs reproducible robustness benchmarks in one command



Compliance — needs EU AI Act Article 15 evidence generation

Core User Stories





As an ML Engineer, I can run nightmarenet train --config robustness.yaml and get a model hardened against adversarial inputs with measurable improvement metrics



As a startup dev, I can add a GitHub Action that blocks deploys when model robustness drops below threshold



As a red team lead, I can configure custom nightmare distortions and track regression across model versions



As a researcher, I can reproduce NightmareNet benchmarks with nightmarenet benchmark --suite standard



As a compliance officer, I can export a robustness audit trail showing continuous testing per EU AI Act Article 15

Success Metrics





10-30% robustness improvement on standard NLP/CV benchmarks vs baseline fine-tuning



Sub-5-minute CI check for small models (DistilBERT class)



1K GitHub stars within 6 months of public release



10+ beta customers within 12 months of hosted platform launch

Scope Boundaries (What NOT to Build)





Runtime guardrails (Lakera owns this)



Model inventory/discovery (different problem)



General MLOps (W&B, Neptune)



Prompt injection defense (RAMPART)



Data labeling



3. Technical Requirements Document (TRD)

System Architecture Overview

graph TB
    subgraph oss_core [Open-Source Core - Apache 2.0]
        CLI[CLI Interface]
        DistortionEngine[Distortion Engines]
        TrainingLoop[4-Phase Training Loop]
        EvalFramework[Evaluation Framework]
        PipelineRunner[Pipeline Runner]
    end

    subgraph hosted [Hosted Platform - Paid]
        APIGateway[API Gateway + Auth]
        Orchestrator[Distributed Orchestrator]
        ExperimentDB[Experiment Store]
        ComplianceEngine[Compliance Engine]
        WebUI[Web Dashboard]
    end

    subgraph infra [Infrastructure]
        Queue[Task Queue - Redis]
        DB[PostgreSQL]
        ObjectStore[S3/Blob Storage]
        GPU[GPU Compute Pool]
    end

    CLI --> TrainingLoop
    TrainingLoop --> DistortionEngine
    TrainingLoop --> EvalFramework
    WebUI --> APIGateway
    APIGateway --> Orchestrator
    Orchestrator --> PipelineRunner
    Orchestrator --> Queue
    Queue --> GPU
    Orchestrator --> ExperimentDB
    ExperimentDB --> DB
    PipelineRunner --> ObjectStore
    ComplianceEngine --> ExperimentDB
end

Architecture Principles





Layer separation — OSS core has zero dependencies on hosted infra (no DB, no Redis, no auth)



Plugin architecture — Distortion engines are pluggable (register custom distortions)



Event-driven pipeline — Training loop emits events; hosted platform subscribes for real-time UI



Stateless API — All state lives in DB/object store; API servers are horizontally scalable



GPU-agnostic — Runs on CPU (dev), single GPU (OSS), multi-GPU/multi-node (hosted)

Technology Stack

Backend (Python 3.9+):





PyTorch (training core)



Transformers (model loading)



FastAPI (API layer)



Celery + Redis (task queue, hosted only)



SQLAlchemy + PostgreSQL (hosted only)



Pydantic v2 (validation)

Frontend (TypeScript):





Next.js 14 (App Router)



Tailwind CSS v4



Framer Motion (animations)



Recharts (training visualization)



Socket.io (real-time updates, hosted)

Infrastructure:





Docker (containerization)



GitHub Actions (CI/CD)



Vercel (frontend hosting)



Railway/AWS (backend hosting)



S3-compatible storage (model artifacts)

Non-Functional Requirements





Latency: API responses < 200ms (non-training); training status polls < 50ms



Throughput: Support 100 concurrent pipeline runs (hosted)



Availability: 99.9% uptime for hosted API



Security: OAuth 2.0 + JWT, RBAC, encrypted at rest, TLS in transit



Compliance: Audit log every state mutation; exportable training lineage



4. Market Context





SAM: $2.4-$3.1B in 2026, growing 27-29% CAGR



Regulatory tailwind: EU AI Act Article 15 fully applicable August 2, 2026



Acquisitions: Cisco/Robust Intelligence, Palo Alto/Protect AI, F5/CalypsoAI (2024-2025)



Year-1 SOM: $500K-$5M ARR



Moat: 4-way intersection no competitor occupies (adversarial generation + forgetting prevention + compression + orchestration)



5. Target Architecture (Folder Structure)

NightmareNet/
├── nightmarenet/                  # OSS Core Package
│   ├── __init__.py
│   ├── cli.py                     # Click/Typer CLI entry point
│   ├── pipeline.py                # 4-phase orchestrator
│   ├── pipeline_runner.py         # Background thread runner
│   ├── config.py                  # YAML config loader + validation
│   ├── distortions/               # Plugin-based distortion engines
│   │   ├── __init__.py
│   │   ├── registry.py            # Distortion plugin registry
│   │   ├── dream.py               # Dream-phase distortions
│   │   ├── nightmare.py           # Nightmare-phase distortions
│   │   └── custom.py              # User-defined distortion base
│   ├── training/                  # Training loop + phases
│   │   ├── __init__.py
│   │   ├── trainer.py             # Core Trainer class
│   │   ├── phases.py              # Wake/Dream/Nightmare/Compress
│   │   ├── scheduler.py           # Adaptive scheduling
│   │   ├── distributed.py         # DDP/FSDP support
│   │   └── callbacks.py           # Event system for UI streaming
│   ├── compression/               # Knowledge distillation
│   │   ├── __init__.py
│   │   ├── distiller.py           # Teacher-student distillation
│   │   └── pruning.py             # Structured pruning
│   ├── evaluation/                # Robustness metrics
│   │   ├── __init__.py
│   │   ├── evaluator.py           # Multi-strength evaluator
│   │   ├── metrics.py             # Robustness score computation
│   │   └── benchmarks.py          # Standard benchmark suite
│   ├── data/                      # Data ingestion
│   │   ├── __init__.py
│   │   ├── ingest.py              # Multi-source ingestion
│   │   └── scraper.py             # Web scraping
│   └── utils/                     # Shared utilities
│       ├── __init__.py
│       ├── validation.py
│       └── logging_config.py
├── nightmarenet_server/            # Hosted Platform (separate package)
│   ├── __init__.py
│   ├── app.py                     # FastAPI app (hosted features)
│   ├── auth/                      # OAuth2 + JWT + RBAC
│   ├── models/                    # SQLAlchemy ORM models
│   ├── services/                  # Business logic layer
│   ├── tasks/                     # Celery task definitions
│   └── compliance/                # Audit log + EU AI Act reports
├── frontend/                      # Next.js 14 Dashboard
│   ├── src/
│   │   ├── app/                   # App Router pages
│   │   ├── components/            # UI components
│   │   │   ├── pipeline/          # Pipeline wizard + visualization
│   │   │   ├── dashboard/         # Experiment dashboard
│   │   │   ├── ui/                # Design system primitives
│   │   │   └── charts/            # Training visualization charts
│   │   ├── lib/                   # API client, hooks, utils
│   │   └── styles/                # Tailwind theme
│   └── public/
├── tests/                         # Comprehensive test suite
├── configs/                       # YAML training configs
├── scripts/                       # CLI entry points
├── docs/                          # Documentation
│   ├── api/                       # OpenAPI spec
│   ├── architecture/              # ADRs (Architecture Decision Records)
│   └── research/                  # Paper drafts, benchmarks
├── .github/
│   ├── workflows/                 # CI/CD pipelines
│   └── actions/                   # Custom GitHub Action (robustness check)
├── docker/
│   ├── Dockerfile.api             # API server container
│   ├── Dockerfile.worker          # Training worker container
│   └── docker-compose.yml         # Local dev stack
└── infra/                         # Infrastructure as Code
    └── terraform/                 # Cloud provisioning



6. API Contract (OpenAPI Summary)

OSS API (FastAPI — runs locally or self-hosted)

POST /api/v1/pipeline/create        # Start a training pipeline
GET  /api/v1/pipeline/{id}/status   # Poll pipeline status + metrics
POST /api/v1/pipeline/{id}/cancel   # Cancel a running pipeline
GET  /api/v1/pipeline/{id}/report   # Get evaluation report
POST /api/v1/generate/dream         # Generate dream-distorted text
POST /api/v1/generate/nightmare     # Generate nightmare-distorted text
POST /api/v1/evaluate/robustness    # Multi-strength robustness eval
GET  /api/v1/health                 # Health check

Hosted Platform API (extends OSS)

POST /api/v1/auth/login             # OAuth2 token exchange
POST /api/v1/auth/refresh           # Token refresh
GET  /api/v1/orgs/{id}/projects     # List org projects
POST /api/v1/projects               # Create project
GET  /api/v1/experiments            # List experiments (paginated)
GET  /api/v1/experiments/{id}       # Experiment detail + history
POST /api/v1/experiments/compare    # Compare N experiments
GET  /api/v1/compliance/audit-log   # Audit trail (paginated)
POST /api/v1/compliance/export      # Export EU AI Act report
POST /api/v1/webhooks               # Configure CI/CD webhooks



7. Database Schema (Hosted Platform)

users (id, email, name, avatar_url, created_at)
orgs (id, name, plan_tier, created_at)
org_members (org_id, user_id, role [admin|member|viewer])
projects (id, org_id, name, description, created_at)
experiments (id, project_id, name, config_json, status, created_at)
runs (id, experiment_id, status, phase, progress_pct,
      metrics_json, started_at, completed_at, gpu_seconds)
run_events (id, run_id, event_type, payload_json, timestamp)
model_artifacts (id, run_id, path, size_bytes, checksum, created_at)
audit_logs (id, org_id, user_id, action, resource_type,
            resource_id, metadata_json, timestamp)
api_keys (id, org_id, user_id, key_hash, name, scopes[], last_used_at)



8. UX Architecture and Flows

Design System (Cyberpunk-Neural Theme)





Primary: Void Black (#020617) — backgrounds



Dream Accent: Indigo (#818CF8) — dream phase, calm states



Nightmare Accent: Red (#EF4444) — nightmare phase, alerts



Neural Accent: Cyan (#06B6D4) — data, connections, active states



Compress Accent: Amber (#F59E0B) — compression, optimization



Typography: Inter (UI) + JetBrains Mono (code/metrics)



Motion: Spring-based (Framer Motion), 60fps, purposeful

Key UX Flows

Flow 1: First-Time "Try It" (< 2 minutes to value)

Landing → "Try Robustness Check" CTA → Paste text or select preset
→ Live distortion visualization (dream vs nightmare side-by-side)
→ Robustness score with breakdown → "Run Full Pipeline" upsell

Flow 2: Pipeline Wizard (ML Engineer)

Dashboard → New Experiment → Source (URL/HF/Upload/Paste)
→ Model Selection (with size/speed tradeoffs shown)
→ Config (cycles, strengths, epochs — smart defaults)
→ Launch → Real-time Phase Visualization (Wake→Dream→Nightmare→Compress)
→ Live metrics (loss curve, robustness score per phase)
→ Completion → Report (before/after comparison, exportable)

Flow 3: CI/CD Integration (Startup Team)

Settings → API Keys → Copy key
→ GitHub Action YAML shown (one-click copy)
→ Configure threshold (robustness score >= X to pass)
→ Push code → Action runs → Badge in PR (pass/fail + score)

Flow 4: Compliance Export (Enterprise)

Dashboard → Compliance tab → Select experiments
→ Generate EU AI Act Report → PDF/JSON with:
  - Training lineage (data → model → phases → result)
  - Robustness scores at each distortion level
  - Timestamp-signed audit trail
  - Configuration reproducibility hash

Component Inventory (Frontend)

Layout:





AppShell — sidebar + topbar + content area



Sidebar — navigation, org switcher, project selector



CommandPalette — Raycast-style cmd+k for power users

Pipeline:





PipelineWizard — multi-step creation flow



PhaseVisualizer — animated Wake→Dream→Nightmare→Compress



LiveMetrics — real-time loss/robustness charts (Recharts + WebSocket)



DistortionPreview — side-by-side text distortion visualization

Dashboard:





ExperimentList — sortable/filterable experiment table



ExperimentDetail — full run history + comparison



RobustnessRadar — radar chart of multi-dimension robustness



ModelComparison — before/after metrics overlay

Shared UI Primitives:





Button, Input, Select, Modal, Toast, Tooltip



Card, Badge, Progress, Skeleton



DataTable — sortable, filterable, paginated



Chart — line, bar, radar, heatmap variants



9. Deployment Architecture

Local Development

docker-compose up  →  FastAPI (8000) + Next.js (3000) + Redis + PostgreSQL

Production (Hosted Platform)

graph LR
    subgraph edge [Edge Layer]
        CDN[Vercel CDN]
        FrontendProd[Next.js on Vercel]
    end

    subgraph api_layer [API Layer - Railway/AWS]
        LB[Load Balancer]
        API1[FastAPI Instance 1]
        API2[FastAPI Instance 2]
    end

    subgraph compute [Compute Layer]
        RedisQ[Redis Queue]
        Worker1[GPU Worker 1]
        Worker2[GPU Worker 2]
    end

    subgraph data [Data Layer]
        PG[PostgreSQL]
        S3[S3 Model Storage]
    end

    CDN --> FrontendProd
    FrontendProd --> LB
    LB --> API1
    LB --> API2
    API1 --> RedisQ
    API2 --> RedisQ
    RedisQ --> Worker1
    RedisQ --> Worker2
    API1 --> PG
    Worker1 --> S3
    Worker2 --> S3
end

CI/CD Pipeline (GitHub Actions)

# .github/workflows/ci.yml
triggers: [push to main, PR]
jobs:
  lint:     ruff check . && mypy nightmarenet/
  test:     pytest tests/ -v --tb=short (206+ tests)
  build:    docker build + frontend build
  security: safety check + bandit scan
  deploy:   (main only) Railway deploy + Vercel deploy

Environment Strategy





development — local docker-compose, hot reload



staging — Railway preview environment per PR



production — Railway (API) + Vercel (frontend) + managed PostgreSQL



10. Security Architecture





Authentication: OAuth 2.0 (GitHub, Google) + API key for programmatic access



Authorization: RBAC (admin, member, viewer per org)



Secrets: Environment variables via Railway/Vercel; never in code



API Security: Rate limiting (slowapi), CORS whitelist, request validation



Data: Encrypted at rest (AES-256), TLS 1.3 in transit



Audit: Every state mutation logged with user, timestamp, diff



Model artifacts: Signed with SHA-256, integrity verified on download



11. Environment and Tooling Setup

GPU Configuration





Primary: NVIDIA GeForce RTX 3050 Ti Laptop GPU (4 GB VRAM)



Integrated: Intel Iris Xe Graphics (128 MB) — offload non-training rendering



Reference setup: Already configured at C:\Users\aditj\New Projects\Skin-Cancer-Disease-Prediction-System



Optimization targets: Mixed precision (FP16), gradient checkpointing, small batch accumulation for 4GB VRAM constraint



Model constraints: DistilBERT/DistilGPT-2 fit in 4GB; GPT-2 medium requires gradient checkpointing

Browser Automation (Browser Use)





API available for browser-based testing, UX research, and competitive analysis



Reference: https://docs.browser-use.com/cloud/llms.txt (overview), https://docs.browser-use.com/cloud/llms-full.txt (full)



Use cases: automated UI validation, screenshot-based design comparison, live demo recording

Repository Intelligence Tools

gitnexus — Knowledge graph for architecture visualization and vibe-coding acceleration:

npx gitnexus analyze

graphify — Repository comprehension, dependency intelligence, developer onboarding:

graphify setup && graphify optimize

code-review-graph — Maintainability analysis, PR intelligence, architecture auditing:

pip install code-review-graph
code-review-graph install
code-review-graph build

Spec-Driven Development

Integrate spec-kit for:





Structured specifications with architecture alignment



Implementation tracking and validation pipelines



Technical decision records (ADRs)



Requirement consistency verification

Design Inspiration Source

Reference C:\Users\aditj\New Projects\TR-104-DarkLead-main (Zero — AI-Powered Code Intelligence Platform) for:





Feature density: 20+ functional panels, each solving one specific problem



README as demo: Live scan results shown upfront, every panel screenshot-documented



Pipeline visualization: 13-step pipeline explained as numbered sequence



Information architecture: Command Center dashboard with drill-down into specialized views



Panel design pattern: Each view = one concern (Compliance, Dependency Intel, Trend Analysis, etc.)

Panels to mirror for NightmareNet (adapted from DarkLead's 28-panel approach):





Command Center (dashboard overview with live metrics)



Pipeline Wizard (create + configure experiments)



Phase Visualizer (animated Wake→Dream→Nightmare→Compress)



Live Training Monitor (real-time loss/robustness curves)



Experiment History (all past runs, sortable/filterable)



Robustness Radar (multi-dimension robustness chart)



Model Comparison (before/after, A/B side-by-side)



Distortion Preview (dream vs nightmare text visualization)



Benchmark Suite (standard robustness benchmarks)



Compliance Dashboard (EU AI Act progress, NIST mapping)



Audit Trail (every state mutation, exportable)



API Playground (try distortions interactively)



CI/CD Integration (GitHub Action setup + status)



Model Registry (all trained artifacts with checksums)



Export Center (PDF reports, JSON, CSV)



Trend Analysis (robustness improvement over cycles)



Self-Health Monitor (API, GPU, workers, queue depth)



AI Assistant (context-aware chat about current experiment)



Settings (API keys, model config, distortion tuning)



Team Management (RBAC, org switcher)



12. Sprint Plan (Execution Sequence)

Sprint 0: Stabilize + Environment Setup (Days 1-3)





Configure CUDA for RTX 3050 Ti (verify torch.cuda.is_available(), set memory limits)



Run npx gitnexus analyze — generate knowledge graph



Install + configure graphify for repository intelligence



Install code-review-graph and build codebase index



Integrate spec-kit for structured development tracking



Run full test suite, fix failures



Fix known gaps (real-time progress, phase name alignment)



Remove orphaned components (AutoPipeline.tsx)



Clean commit history with conventional commits



Verification: pytest green, ruff check . clean, npm run build passes, CUDA verified

Sprint 1: Architecture Refactor (Days 4-10)





Separate nightmarenet/ (OSS core) from nightmarenet_server/ (hosted)



Implement CLI via Click/Typer (nightmarenet train, nightmarenet evaluate, nightmarenet benchmark)



Add event/callback system to Pipeline for real-time streaming



Plugin registry for custom distortion engines



Verification: CLI runs end-to-end on GPT-2 with measurable output

Sprint 2: Technical Validation (Days 11-17)





Design benchmark experiment: GPT-2 on AG News or SST-2



Run baseline (standard fine-tuning) vs NightmareNet (4-phase cycle)



Measure: accuracy, adversarial accuracy (TextFooler, BertAttack), robustness score



Target: demonstrate 10-30% adversarial robustness improvement



Document results in docs/research/benchmark-v1.md



Verification: reproducible results with fixed seeds

Sprint 3: Frontend Elevation (Days 18-28)





Design system: primitives (Button, Card, Input, Toast, Modal)



AppShell with sidebar navigation, cmd+k palette



PipelineWizard redesign: premium multi-step with animations



PhaseVisualizer: animated 4-phase cycle with real-time metrics



LiveMetrics: WebSocket-connected loss curves + robustness charts



ExperimentDashboard: list, compare, export



Verification: Lighthouse 95+, responsive, keyboard accessible

Sprint 4: CI/CD + DevOps (Days 29-35)





GitHub Actions: lint + test + build + security scan



Docker: API + worker Dockerfiles, docker-compose for local dev



Custom GitHub Action: nightmarenet-robustness-check for CI gates



Staging environment on Railway (auto-deploy from PRs)



Verification: PR triggers full CI, staging deploys automatically

Sprint 5: Hosted Platform Foundation (Days 36-50)





PostgreSQL schema (users, orgs, experiments, runs, audit)



Auth layer (OAuth2 via GitHub/Google + API keys)



Celery workers for background training on GPU



Real-time updates via WebSocket (run status → frontend)



Verification: End-to-end flow from login → create experiment → view results

Sprint 6: Community Launch Prep (Days 51-60)





README rewrite (investor-demo quality)



Colab notebooks (3: quickstart, benchmark reproduction, custom distortions)



CONTRIBUTING.md + developer guide



Paper draft (workshop submission quality)



Discord server + public research channel



Verification: Fresh clone → install → run demo in < 5 minutes



13. Pricing Model





Community: $0 — Full OSS core, single-GPU, CLI, self-hosted, unlimited



Pro: $49/seat/mo + compute — Cloud orchestration, multi-GPU, experiment tracking, teams, 1000 cycles/mo included



Enterprise: $50K-$100K/year — SSO, audit logs, compliance reports, on-prem, SLA, custom distortion engines, dedicated support



14. GTM Sequence





Months 0-6: Ship OSS core on PyPI, publish paper, benchmark results, Discord, Colab notebooks. Target 1K stars.



Months 6-12: HF Hub integration, GitHub Action CI check, blog posts, second paper. Target 5K stars, 10K installs/mo.



Months 12-18: Launch hosted platform beta, SOC 2 Type I, team features. Target 10 customers, $15K MRR.



Months 18-30: Enterprise motion, SOC 2 Type II, EU AI Act compliance export, first AE hire. Target $2M ARR.



15. Risk Analysis and Mitigations





Academic novelty challenged (PAD is close) [Medium] — Differentiate on objective (robustness vs representation) + compression + practical architectures



Big player builds this into existing MLOps [High] — Speed to market + community + paper citations create switching cost



Can't monetize open-source (vLLM problem) [Medium] — Clear boundary: science free, orchestration/compliance paid



EU AI Act demand spike before platform ready [Low] — Position OSS as compliance-adjacent from day 1



Research results don't show improvement [High] — Validate benchmarks BEFORE community launch; pivot framing if needed



GPU compute costs for hosted platform [Medium] — Usage-based pricing passes cost to user; start with Railway/spot instances



16. Verification Strategy (Definition of Done)

Every sprint ends with:





pytest tests/ -v — all tests pass (206+ and growing)



ruff check . — zero lint errors



cd frontend && npm run build — production build succeeds



Manual flow verification — key user journey works end-to-end



Performance check — no regression in API latency or bundle size



Security scan — no new vulnerabilities introduced

Before marking complete:



"Would a staff engineer at a top-tier startup approve this implementation?"



17. Immediate Execution (This Session)

Priority order:





Environment setup — CUDA verification, gitnexus analyze, graphify, code-review-graph, spec-kit



Stabilize WIP — get tests green, lint clean, commit the work



Architecture separation — split OSS core from hosted platform concerns



Technical validation — prove the thesis works on RTX 3050 Ti (benchmark)



Frontend elevation — 20-panel feature-dense dashboard (DarkLead-inspired)



CI/CD — automated quality gates



Community prep — README with screenshots of every panel, notebooks, launch materials

Key constraint: RTX 3050 Ti (4GB VRAM) means:





DistilBERT/DistilGPT-2 for fast iteration



GPT-2 (124M) requires gradient checkpointing + FP16



Batch size 4-8 max depending on sequence length



Use CPU for distortion generation, GPU only for training forward/backward

