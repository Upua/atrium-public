# Decision: Park Idea G — Multi-instance coordination

**Date:** 2026-04-24
**Context:** Roadmap ideas triage. G was "some kind of locking / event bus / coordination layer so multiple concurrent Claude Code instances don't collide when writing to shared state (cortex.db, ~/Atrium, session notes)."

## Verdict: **PARK — and tagged as "audit-first, build-second" if ever.**

## Why parked

**G.0 is literally "is this a real problem?"** — the ROADMAP text acknowledges this. The idea as filed is not a build plan; it's an audit request. Until the audit confirms real collisions, there's no design to write.

**Current evidence on collision frequency:** none.

- Cortex uses SQLite WAL mode — allows multiple readers + one writer without corruption.
- Atrium state files (trace.jsonl, peer inboxes, heartbeats) use append-only or atomic-write-via-rename. Collision-safe by construction.
- Session notes are one-file-per-session with minute-granularity filenames; the existing collision guard (adds session_id suffix) has never fired to my knowledge.

If there IS a real concurrency problem, it's probably in specific narrow places (e.g., `atrium-commit` touching the same walkthrough.md) — but those are per-file, not stack-wide.

**"Solutions looking for problems" risk.** Building a coordination layer for phantom collisions is a classic over-engineering trap. Even a lightweight file-lock scheme introduces failure modes (stale locks, daemon crashes holding locks, deadlock on cascading locks).

## What IS in scope (and already done)

- Atomic writes via temp-then-rename for every mutation (Atrium principle #5).
- Append-only logs where possible (trace.jsonl, session-breadcrumbs.md, peer inboxes).
- Cortex's WAL mode.

These are "collision avoidance through discipline" rather than "collision resolution through coordination." Different model, lower cost, works until it doesn't.

## When to revisit

- If we hit a real collision → capture evidence (trace of both processes, the specific file, the broken state) and file a bug, not an idea. Then design for THAT specific case, not the general one.
- If we start regularly running 2+ concurrent Claude Code sessions on the same project → G's G.0 audit becomes worth doing for real.
- If a shared write path is identified where atomic-rename isn't possible (e.g., DB transaction spanning two files) → design a narrow lock for that specific path.

## Kill condition

If in 180 days no collision evidence surfaces, drop G entirely. "General coordination layer" is the wrong framing even if specific cases emerge — each case gets its own narrow solution.

## Reversibility

Parking is free. Future audit is always possible. Nothing is blocked.
