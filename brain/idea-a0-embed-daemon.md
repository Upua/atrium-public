# Idea A.0 — Persistent embed daemon (LIVE)

**Session:** 2026-04-24  
**Status:** in flight  
**Tail path:** `~/Atrium/brain/idea-a0-embed-daemon.md`

## Goal
A Python process holding MiniLM-L6-v2 warm, exposing a UNIX socket so hooks and CLI
callers can embed + query Cortex in <100ms instead of eating the 7s cold-load every
invocation. Unblocks wiring the Phase 1 Cortex corpus into `memory-surface.sh`.

## Design (decided upfront)

**Socket:** `~/Atrium/state/embed-daemon.sock`  
**Wire:** line-delimited JSON (`\n`-terminated). One request → one response per line.  
**Ops:**
- `{"op":"ping"}` → `{"ok":true,"uptime_s":N}`  — cheap health probe
- `{"op":"embed","text":"..."}` → `{"ok":true,"vector_b64":"..."}`  — raw 384-dim f32 vector, base64
- `{"op":"query_all","text":"...","limit":8}` → `{"ok":true,"hits":[{score, source_table, source_id, preview}]}`

**Supervision:** `atrium-daemon start embed-daemon -- ~/Atrium/bin/atrium-embed-daemon`.  
**Client:** `atrium-embed-source query-all --client "query"` — uses socket if present, falls
back to in-process embedder otherwise.

**Hook use:** `memory-surface.sh` gets a new block that calls the client with `timeout 0.5s`
— if socket is up, results land; if not, silent skip. No regression when daemon isn't running.

## Reversibility

- Daemon is additive: new file, new socket, new subcommand. No schema change.
- `atrium-daemon stop embed-daemon` cleanly shuts down and removes socket.
- `memory-surface.sh` edit is one block; diffable revert if anything misbehaves.
- Golden snapshot from yesterday (`~/Atrium/snapshots/golden-20260423-212255/`) still covers the reversible envelope; no new snapshot needed for this additive change.

## Execution log

### 2026-04-24 08:28 — daemon shipped & smoke-tested

- Wrote `~/Atrium/bin/atrium-embed-daemon` (247 lines Python). Socket server, line-delimited JSON, ops `ping` / `embed` / `query_all`. SIGTERM-clean shutdown.
- Added `--client` / `--no-client` flags + `_daemon_query_all()` helper to `atrium-embed-source`. Auto-detects socket; falls back to in-process MiniLM if absent.
- Started under supervision: `atrium-daemon start embed-daemon -- ~/Atrium/bin/atrium-embed-daemon`.
- Cold-load: **8.18s** (one-time at daemon start).
- Warm timings from raw socket:
  - `ping` → **0.2ms**
  - `embed` → **8.5ms** (for a ~35-char query)
  - `query_all limit=5` → **11.4ms** across 6 source_tables with preview hydration
- End-to-end via CLI wrapper (`atrium-embed-source query-all --client`) → **63ms** total (includes python3.11 startup).
- Sub-100ms target hit with margin. Hook budget of 2s is now trivially satisfied.

### 2026-04-24 09:00 — hook wired + autostart + docs

- `memory-surface.sh` Cortex block **re-enabled** — 0.8s timeout, gated on socket presence. Simulated UserPromptSubmit: 5 Cortex hits blended with ChromaDB session hits, both stores surface.
- `atrium-session-begin` step 3c added: ensures `embed-daemon` is running at session start. Idempotent.
- ROADMAP: A.0 / A.1 / A.2 all ticked [x]. `→ Next:` pointer moved to **A.3 — re-evaluate store unification** (the warm-query argument for ChromaDB is gone now).
- CHANGELOG: new top entry "2026-04-24 — Idea A.0–A.2 shipped" with timings + hook integration details.

### Status: done, awaiting commit approval

Files touched:
- `~/Atrium/bin/atrium-embed-daemon` (NEW, 247 lines)
- `~/Atrium/bin/atrium-embed-source` (client mode added, ~40 lines)
- `~/Atrium/bin/atrium-session-begin` (step 3c added, ~8 lines)
- `~/Atrium/brain/idea-a0-embed-daemon.md` (NEW, this file)
- `~/.claude/scripts/hooks/memory-surface.sh` (Cortex block un-reverted, ~20 lines replaced comment)
- `<captain-meridian-stack>/ROADMAP.md` (A.0–A.2 ticked + Next moved)
- `<captain-meridian-stack>/CHANGELOG.md` (2026-04-24 entry added)

Not touched (pre-existing diff from prior session, leaving for Niklas to review):
- `captain-meridian-stack/claude-config/hooks/archivist.sh` (Haiku→Opus escalation edit)

