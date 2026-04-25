# Decision: ChromaDB / Cortex store unification — migrate to Cortex

**Date:** 2026-04-24
**Context:** Idea A.3 from the Meridian roadmap. With the A.0 embed daemon shipped earlier today, the original "warm-query advantage" argument for keeping ChromaDB as a separate store is gone. A decision was locked in as `→ Next:` and this doc records the call.

## Audit (what's in each store right now)

### Cortex embeddings (`~/.local/share/cortex/cortex.db`, 16 MB)
- `solutions` — **557** rows (after today's bash-noise filter pass)
- `claude_memory` — **208** rows (typed memory files across all projects)
- `events_curated` — **91** rows (breadcrumbs + DMN events)
- `brain_walkthrough` — **9** rows
- `brain_handoff` — **7** rows
- `brain_decision` — **2** rows
- **Total: 874 embeddings.** Polymorphic by `source_table`; 384-dim MiniLM-L6-v2.

### ChromaDB (`~/.claude/memory-search/chroma/`, 67 MB)
- `solutions` — **376** rows. IDs like `cortex_1`, metadata includes `success_count` / `fail_count` / `tags`. **This is a stale mirror of Cortex's solutions table** — fed by `~/.claude/scripts/index-sessions.py` from Cortex on SessionStart.
- `sessions` — **3573** rows. Unique content: full session notes from the Obsidian vault at `<vault>/Sessions/`. Metadata: `date`, `project`, `filename`, `state`. Full document embedded (avg ~2KB each).

**Feeder cadence:** `session-init.sh` (SessionStart) runs `index-sessions.py --cache $PROJECT_NAME`. That's it. No cron; it's session-triggered. Explains why ChromaDB is current-to-today (14 of today's vault notes already indexed).

## The real question

ChromaDB's `solutions` collection is redundant (lossy mirror of a source Cortex owns). The only genuine-unique content is the 3,573 session-note embeddings.

**So: should we migrate session notes into Cortex as a `sessions` source_table, and retire ChromaDB?**

## Verdict: **YES. Migrate sessions to Cortex, retire ChromaDB.**

## Why

1. **Daemon removes the performance argument.** Pre-A.0, ChromaDB won on latency (warm client holding the collection open). Post-A.0, Cortex queries through the embed daemon land in ~11ms — already faster than ChromaDB's cold-client path in practice. No reason to keep two warm systems.

2. **Two stores means two A.4 feedback loops.** The recall feedback module already handles both (via `chroma_sessions` / `chroma_solutions` source_tables) but every cross-cutting concern (scoring, migration, rolling window pruning) gets doubled. Single store = single mental model.

3. **ChromaDB's schema is lossy for Atrium's purposes.** Its metadata carries Obsidian concepts (filename, date, project, state) that matter when the vault is the interface, but they're reconstructable from the filename in a Cortex `sessions` source_table. No real data loss on migration.

4. **Migration cost is trivial.** 3,573 sessions × ~10ms/embed through the warm daemon = ~35 seconds of wall time. Disk delta: ~20 MB (384 floats × 4 bytes × 3573 + previews). We already have the infrastructure (`atrium-embed-source store` + preview sidecar).

5. **"Home, not toolbox" (Atrium principle #9).** One store is the workspace; two stores is a toolbox. The principle says to prefer the workspace.

## What stays / what goes

**Stays:**
- `~/.claude/scripts/index-sessions.py` — repurpose to write to Cortex via `atrium-embed-source` instead of ChromaDB. Keep the frontmatter parser, drop the ChromaDB client. Continue to run on SessionStart.
- ChromaDB directory at `~/.claude/memory-search/chroma/` — **keep as archive for 30 days** in case the migration misses something, then delete.

**Goes:**
- ChromaDB query block in `memory-surface.sh` — remove after migration lands (Cortex query block already covers it).
- `chroma_sessions` / `chroma_solutions` source_tables in `recall-feedback.db` — orphaned after migration, can be cleaned up or left as a historical record.
- Per-session ChromaDB feeder calls from `session-init.sh` — replace with the new Cortex feeder.

## Open questions (for follow-up, not blockers)

- **Preview sidecar size.** 3,573 previews × ~240 chars = ~900 KB. Fine, negligible.
- **Session-note re-embedding policy.** If a session note is edited (rare — they're append-only by convention), do we re-embed? Default: no, since filename+timestamp makes it effectively immutable.
- **Backfill or go-forward?** Recommend: backfill everything now (it's 35 seconds), then flip the feeder.

## Migration plan (when we execute — not today)

1. Add `sessions` source_table handler in `atrium-embed-source scan-all` — reads from `Sessions/*.md`, embeds full document, stores filename in preview sidecar.
2. Backfill run: `atrium-embed-source scan-all` picks up 3,573 new rows under `sessions`.
3. Rewrite `memory-surface.sh`'s ChromaDB block to query `sessions` source_table via embed daemon (or drop it entirely — the existing Cortex block now covers it).
4. Rewrite `index-sessions.py` to feed Cortex (dual-write during transition, then drop ChromaDB write).
5. After 30 days of stable behavior, delete `~/.claude/memory-search/chroma/`.

Not shipping the migration tonight — this is the decision doc, not the change. Sequence it when the next session has bandwidth. Closes A.3 as a **decided**, not **built**, item.

## Rollback

Decision is reversible by not starting the migration. If we start and it goes sideways, the ChromaDB directory stays on disk untouched for 30 days — restore by pointing `index-sessions.py` back at it and rewiring the memory-surface hook.

## Connected artifacts

- [ROADMAP Idea A](https://github.com/Upua/captain-meridian-stack-public/blob/main/ROADMAP.md) — A.3 line now reads "shipped (decision)".
- [A.0 embed daemon decision](./../idea-a0-embed-daemon.md) — the prerequisite that made this tractable.
- [A.4 feedback loop](./../idea-a4-recall-feedback.md) — will need a small source_table rename after migration.
