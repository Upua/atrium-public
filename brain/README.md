# brain/ — Durable Agent Memory

This is the agent's writable home. Files here survive across sessions and instances. Structure is convention, not enforced.

## Standard files

| File | Purpose | Written by |
|---|---|---|
| `task.md` | The current top-level task. Who asked, what's the goal, what's "done" look like. | Agent at start of a task |
| `implementation_plan.md` | The step-by-step plan. Checked boxes as steps complete. Updated as scope changes. | Agent before execution; updated throughout |
| `decisions.md` | Log of non-obvious choices made, with rationale. Append-only. | Agent when a decision is made |
| `walkthrough.md` | Narrated record of what was built and why — future-you reads this to re-orient. | Agent after a meaningful milestone |
| `handoff.md` | Compact state packet written when context is nearly full or session ends. Next instance reads this first. | Agent at session end or at ~70% context |
| `open_questions.md` | Things unresolved and needing user or peer input. | Agent when blocked |

## Conventions

- **Markdown only.** Scannable by agents and humans.
- **Append where possible.** Don't rewrite history casually — decisions/walkthroughs accrete.
- **Date-prefix important entries** (`## 2026-04-19 — <topic>`).
- **Link between files** when a plan references a decision, etc.
- **No secrets.** Credentials, tokens, or API keys never live here. They're git-tracked.

## Format templates

See `*.template.md` files in this directory.
