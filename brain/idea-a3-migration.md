# Idea A.3 — ChromaDB → Cortex Migration (LIVE EXEC)

**Session:** 2026-04-24 (continuation)
**Status:** in flight
**Decision doc:** `brain/decisions/2026-04-24-chroma-cortex-unification.md`

## What this doc covers

The **execution** of the A.3 decision. Verification of each step + final state.

## Execution log

### 2026-04-24 10:20 — migration + hook cleanup shipped

**Step 1 — sessions handler in scan-all:** added a new block in `atrium-embed-source` before the claude_memory loop. Reads every `.md` from `<vault>/Sessions/`, parses frontmatter, truncates to 2000 chars, and embeds with a `[session:…] [project:…] [date:…] [state:…]` prefix for search context. `stable_id` keyed on `sessions:{filename}`.

**Step 2 — backfill:**
- Before: `solutions=557, claude_memory=208, events_curated=91, brain_walkthrough=9, brain_handoff=7, brain_decision=2` → **874 total**.
- After: plus `sessions=4282, brain_decision=3` (the third being today's A.3 decision doc itself) → **5,157 total**.
- Runtime: **6:25** (in-process MiniLM, not via daemon — 90ms per embed × 4282). Acceptable one-shot.
- Cortex DB: 16 MB → 23 MB (7 MB delta).

**Step 3 — ChromaDB block retired from `memory-surface.sh`:**
- Entire live-query block deleted (~120 lines of inline Python).
- Replaced with a 5-line note explaining the migration + 30-day rollback window.
- Moved `CWD_PROJECT` and `KEY_TERMS` computations out to top-level since skills block still needs `KEY_TERMS`.
- Hook went from 241 → 152 lines.
- Verified: substantive prompt now surfaces pure Cortex hits (including `sessions:*` rows). No `Intent-Matched Memory` section anymore — Cortex Corpus Hits covers it.

**Daemon behavior post-migration:**
- `query_all "…" --client --limit 8` took 244ms end-to-end. Sessions picked up fresh via SQLite WAL (no daemon restart needed).
- A.4 feedback multipliers apply to `sessions:*` rows the same way they apply to `claude_memory:*`. The chroma_* source_tables in `recall-feedback.db` are orphaned (no new writes) — can be deleted at some point, or left as historical.

**What stays (transition state):**
- `~/.claude/memory-search/chroma/` dir: **kept for 30 days** as rollback safety net. Delete on or after 2026-05-24.
- `~/.claude/scripts/index-sessions.py`: **left running** on SessionStart — harmless. It continues to mirror into ChromaDB but nothing reads from ChromaDB anymore. Cheap; revisit when the dir deletion lands.

**What's different about the ambient recall now:**
- Single semantic source (Cortex) → single A.4 feedback surface.
- `sessions:*` rows rank among the unified top-N via the same multiplier logic as everything else.
- Cortex corpus grew 6x; no latency regression observed (warm daemon path is constant-time w.r.t. corpus size for `find_by_vector`).

