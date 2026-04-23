# NightmareNet Agent Configuration

## Instructions

Read and follow `CLAUDE.md` in this repository for project-specific conventions.

## Skills

The following skills are available and SHOULD be used when relevant:

### Superpowers (via ~/.agents/skills/superpowers/)

- **test-driven-development** — Use when writing any new feature or fixing bugs
- **systematic-debugging** — Use when investigating test failures or runtime errors
- **verification-before-completion** — Use before claiming ANY task is done
- **writing-plans** — Use when the task requires 3+ steps of implementation
- **executing-plans** — Use when executing a previously written plan

### Project Skills (via .claude/skills/)

- **ui-ux-pro-max** (`.claude/skills/ui-ux-pro-max/`) — Use for any frontend/UI work on the Next.js frontend

## Commands

Available slash commands in `.claude/commands/`:

- `/check` — Run full quality pipeline (lint + tests + frontend build)
- `/tdd <feature>` — Implement a feature with strict TDD
- `/commit` — Create a conventional commit with pre-flight checks
- `/debug <problem>` — Systematic debugging workflow
- `/prime` — Load project context for a new session

## Hooks

Configured in `.claude/settings.json`:

- **PostToolUse**: Python syntax check on `.py` file edits
- **Stop**: Ruff lint check before session ends

## Learned User Preferences

## Learned Workspace Facts

- Next.js client uses same-origin `/api`; `frontend/next.config.ts` rewrites to `NEXT_API_REWRITE_URL` (backend base, no trailing slash). If `NEXT_PUBLIC_API_URL` is set, the browser calls that origin directly and rewrites are not used (configure API CORS for split-host).
- Health (`/api/v1/health`): `NIGHTMARENET_HEALTH_TEST_COUNT` optionally runs a subprocess `pytest --collect-only` check; leave unset/off in production.
- Pipeline runner registry: `NIGHTMARENET_MAX_PIPELINE_RUNNERS` caps in-memory runners (default 64); when over cap, completed runs are evicted first.
- `docs/solutions/nightmarenet-research-synthesis.md` is the research synthesis artifact; full deep-research workflows expect **parallel-cli** (or equivalent) available.