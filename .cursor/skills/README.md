# Cursor Project Skills

Elite engineering philosophy installed as Cursor skills. Each skill is auto-discoverable — Cursor agent loads them when the description matches the current task.

## Skill Map

| Skill | When it activates |
|-------|-------------------|
| [`elite-execution-philosophy`](./elite-execution-philosophy/SKILL.md) | All tasks — sets the staff-engineer quality bar |
| [`workflow-orchestration`](./workflow-orchestration/SKILL.md) | Non-trivial tasks (3+ steps, architecture) — plan-mode-first |
| [`task-management-loop`](./task-management-loop/SKILL.md) | Maintaining `tasks/todo.md` and `tasks/lessons.md` |
| [`verification-and-elegance`](./verification-and-elegance/SKILL.md) | Before claiming any work complete |
| [`subagent-strategy`](./subagent-strategy/SKILL.md) | Parallel research, isolated exploration, specialized execution |
| [`autonomous-bug-fixing`](./autonomous-bug-fixing/SKILL.md) | Bugs, failing tests, CI failures, broken UX |
| [`research-first-execution`](./research-first-execution/SKILL.md) | Before non-trivial feature work — competitive analysis, prior art |
| [`spec-kit-driven-development`](./spec-kit-driven-development/SKILL.md) | New features/subsystems — PRD/TRD/ADR before code |
| [`ai-native-product-thinking`](./ai-native-product-thinking/SKILL.md) | Product/feature design — AI copilots, semantic search, automation |
| [`ui-ux-pro-max`](./ui-ux-pro-max/SKILL.md) | Any UI work — design systems, palettes, typography, a11y |
| [`performance-security-devops`](./performance-security-devops/SKILL.md) | Production hardening, infra, deployment readiness |
| [`gitnexus`](./gitnexus/SKILL.md) | Impact analysis, safe refactoring, codebase exploration |

## How They Interact

```
Start of task
  ├─ workflow-orchestration → plan mode
  │   └─ task-management-loop → tasks/todo.md
  ├─ research-first-execution → competitive + technical research
  │   └─ subagent-strategy → parallel research subagents
  ├─ spec-kit-driven-development → PRD/TRD/ADR (if significant)
  └─ gitnexus → impact analysis before editing any symbol

During implementation
  ├─ elite-execution-philosophy → quality bar always on
  ├─ ai-native-product-thinking → product design lens
  ├─ ui-ux-pro-max → frontend work
  ├─ performance-security-devops → infra/prod concerns
  └─ autonomous-bug-fixing → when anything fails

Before completion
  ├─ verification-and-elegance → proof + redesign pass
  ├─ gitnexus → detect_changes before commit
  └─ task-management-loop → review summary, lessons.md if corrected
```

## Authoring New Skills

Create `.cursor/skills/<name>/SKILL.md` with YAML frontmatter:

```yaml
---
name: skill-name
description: WHAT it does and WHEN to use it (third person, ≤1024 chars, include trigger keywords)
---
```

Body ≤ 500 lines. Progressive disclosure for detail — link to reference files one level deep.

## Companion Files

- `tasks/todo.md` — active workstream tracker
- `tasks/lessons.md` — permanent corrections memory
- `AGENTS.md` — repo-level agent configuration
- `CLAUDE.md` — project conventions (auto-applied)
