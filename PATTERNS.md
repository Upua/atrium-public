# Atrium — Patterns Carried from SIGNAL

SIGNAL is a mature agent harness. Atrium is not its fork. But SIGNAL has hard-won lessons that are cheap for Atrium to inherit — if we port the *patterns*, not the code.

Each pattern below: what SIGNAL learned, what we carry, and where it lives in Atrium (planned or built).

---

## ✅ Patterns worth carrying

### 1. Hard budget cap + blocked command filter
**SIGNAL:** `safety.py` caps sessions at $38, refuses `sudo`, `rm -rf /`, `mkfs*`, etc.
**Atrium:** re-implement in `bin/atrium-guard` (planned). Model-agnostic: the filter sits between tool calls and the kernel, regardless of which model made them. Budget is per-workspace, not per-session — Atrium is continuous.

### 2. Atomic state writes (temp-then-rename)
**SIGNAL:** `core/state.py` writes to `*.tmp` then `Path.replace(target)`. Prevents half-written files under concurrent access.
**Atrium:** every writer to `brain/`, `state/`, `peers/` does the same. Wrapper function in `bin/atrium-writefile`.

### 3. Cost forecasting from historical JSONL with IQR-robust median
**SIGNAL:** `core/estimate.py` — tails `cost.jsonl`, computes median-excluding-outliers, predicts session total.
**Atrium:** `state/trace.jsonl` is the append-only source. HUD plugin reads tail, computes same IQR-median, renders burn-rate + predicted tokens-to-wall. Simpler impl (no multi-phase prediction, just one rolling rate).

### 4. Ground-truth file-state checks before claiming progress
**SIGNAL:** swarm workers got caught claiming `is_done=true` with empty `files_modified`. Added hallucination guard that diffs real file state against claim.
**Atrium:** approval ritual requires a verification command logged in `state/trace.jsonl` with exit 0 before any `brain/implementation_plan.md` checkbox flips to `[x]`.

### 5. Append-only learnings with supersede-links
**SIGNAL:** `learnings/patterns.jsonl` — every entry is append-only. A better pattern supersedes an old one via `supersedes: <id>`.
**Atrium:** `brain/patterns.jsonl` follows the same shape. Wrapper enforces append-only via OS permissions (future) or a write-guard in the agent harness.

### 6. Git checkpoint as the unit of progress
**SIGNAL:** every successful session ends with a git commit. "Progress" is `git log --oneline | wc -l` delta.
**Atrium:** same, but ambient not end-of-session. Commits happen per meaningful milestone. `brain/walkthrough.md` links to commit SHAs.

### 7. Phase 1 / Phase 2+ / Evaluator as roles, not separate sessions
**SIGNAL:** uses three distinct prompt files (`initializer.md`, `orient.md`, `evaluate.md`) for three sessions with fresh context.
**Atrium:** treats these as **personas the agent adopts mid-stream**, not separate processes. An "evaluator pass" is a ritual inside the same Atrium session — pause, switch role, verify, switch back. Different shape; same logic.

### 8. Fresh context + handoff packet at boundary
**SIGNAL:** writes `handoff.md` when session runs low on context; next session reads it first.
**Atrium:** `brain/handoff.md` template already scaffolded. Auto-written at ~70% context usage with a Telegram ping (via reach). Next instance reads this + `AGENTS.md` first.

### 9. Graceful-degrade notify
**SIGNAL:** `notify.py` tries desktop, then GSConnect phone, each wrapped in try/except; agent never blocks on a missing channel.
**Atrium:** already have `reach` MCP for phone + desktop notify; keep the fail-silent pattern.

---

## ❌ Patterns deliberately NOT carried

### 1. Kitty-as-worker model
**SIGNAL:** spawns new Kitty windows as worker processes, talks to them via `kitten ls / kitten set-colors`.
**Why skip:** Atrium's unit is the Zellij pane, not the Kitty window. Workers live in panes, coordinated via `zellij action`, `zellij pipe`, and sockets in `peers/`. Peer Kitty windows are for *graphics*, not *processes*.

### 2. FastAPI + Jinja2 dashboard
**SIGNAL:** web UI for cost, task DAG, session timeline, swarm stats.
**Why skip:** wrong medium. Atrium's surfaces are Zellij panes and peer Kitty windows. If we ever need HTTP, it's a thin shim, not the primary UI.

### 3. Claude Agent SDK tightly coupled hooks
**SIGNAL:** `core/harness.py` binds to `AsyncToolHook`, `ResultMessage` from the SDK.
**Why skip:** Atrium should accept Claude *and* Gemini *and* local models. SDK-specific code lives in adapters, not in the core.

### 4. 5-worker Petri swarm
**SIGNAL:** `core/swarm.py` runs 5 Haiku workers coordinated via Petri bus — and the last 15+ commits on it are hallucination-guards, deadlock-closures, ownership fixes.
**Why skip:** the complexity signals the base pattern is brittle. Perplexity research corroborates: "group-chat style multi-agent systems are brittle without semantic firewalls." Atrium supports 2-3 scoped peers with explicit handoffs — if we ever need swarms, we revisit then.

### 5. Full Petri bus protocol for a workspace with 2 peers
**SIGNAL:** SQLite-backed, energy-gated, role-aware message bus.
**Why skip:** over-engineered for Atrium's scope. A flat JSONL queue (`peers/<name>/inbox.jsonl`, `peers/<name>/outbox.jsonl`) with file-lock for concurrent writes is enough for 2-3 peers. If we grow, we adopt Petri then.

### 6. Tasks.json as single source of truth
**SIGNAL:** run-to-completion model — one tasks.json defines the whole run.
**Why skip:** Atrium is continuous. `brain/task.md` is human-prose, markdown, append-oriented. Multiple tasks coexist in `brain/tasks/<slug>/task.md` if needed. No single-source-of-truth JSON.

### 7. Terminal color signals for worker status
**SIGNAL:** uses `kitten set-colors` to flash worker terminals red/green as status.
**Why skip:** cute, but baked into the Kitty-as-worker model we're not carrying. Status lives in the Zellij status bar + HUD plugin.

---

## 🔬 Open: patterns worth studying before deciding

### 1. Session ritual: `initializer.md → orient.md → evaluate.md`
Worth reading SIGNAL's prompt files in full before writing Atrium's version. The structure (Phase 1 expands tasks + verification, Phase 2+ is incremental, Evaluator is quality gate) is sound. Our version should be persona-based inside one session, not three separate sessions.

### 2. Learnings promotion pipeline
SIGNAL's `core/learnings_pipeline.py` takes evaluator failures and promotes patterns. Interesting, but we should understand it before porting — the promotion rules might embed SIGNAL's run-to-completion assumptions.

### 3. Cost.jsonl schema
SIGNAL's JSONL fields should inform Atrium's `state/trace.jsonl` schema. Same shape where it makes sense — lets us reuse `estimate.py`'s math mentally, if not its code.

---

This file evolves as we build. Every time a SIGNAL lesson is imported into Atrium, update the relevant entry with "how we did it in Atrium" and link to the commit.
