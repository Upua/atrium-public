# GROWTH

How atrium grew from a directory of scripts into a workspace.

This is the public version of the build narrative. The private dev repo keeps the full append-only walkthrough; this is the distilled summary.

---

## Start (early 2026)

Atrium began as a directory called `~/Atrium/` with a handful of bash scripts and a question: what would it look like to treat Claude not as a tool you call, but as a co-inhabitant of a workspace that learns and persists?

The first commits were unglamorous. `atrium-trace` to write events to `state/trace.jsonl`. `atrium-recall` for grep over a notes folder. `atrium-decide` to make a typed artifact from a decision. The scripts were ad-hoc and the conventions were emerging as they were used.

The shape clarified through use, not design.

## Phase 1 — Memory unification (April 2026)

The first real architectural move was unifying the memory surfaces. Before this, three places held memory: a ChromaDB folder for semantic session search, the Cortex daemon for solutions and events, and the Obsidian vault as the human-facing reference. They didn't share embeddings, didn't share queries, and drifted.

The decision was to make Cortex the single store, with a polymorphic `embeddings` table keyed by `source_table`. A persistent embed daemon (`atrium-embed-daemon`) holds MiniLM-L6-v2 in memory and exposes a UNIX socket — sub-100ms warm queries instead of 7-second cold loads.

The daemon was the unlock for ambient recall. Once memory was warm, every prompt could be enriched with relevant prior sessions, decisions, and breadcrumbs without measurable latency. Phase 1 closed in late April 2026.

## Idea B — DMN as a peer

Around the same time, the system grew its first non-Claude peer: a Default Mode Network daemon that runs in the background, observes work trajectory across sessions (error rates, session duration, project sprawl, fragile breadcrumb count), and writes advisory messages into its own outbox.

DMN doesn't have authority to do anything. It's purely advisory — the part of mental life that does background pattern-matching, externalized into a process so it can keep watching while the orchestrator's context window is full of other work.

This was the moment "co-inhabitant" stopped being a metaphor.

## Phase 2 — Reach unification (April 2026)

Notification was a mess: voicemode for speech, telegram bot for push, reach (GSConnect) for phone, direct-line for desktop. Different call shapes, different urgency conventions, no central routing.

`atrium-notify` collapsed it into one primitive with an urgency × modality matrix. Quiet hours, escalation thread, fallback chain on channel failure, auto-thread by topic — all behind one bash entry point and a Python helper. Voice route remains stubbed pending Phase 2.2b.

This shipped 2026-04-25, the same day this artifact was prepared.

## The vocabulary that emerged

Looking back, the cognitive-verb vocabulary wasn't designed up front. It accumulated:

- `atrium-decide`, `atrium-claim`, `atrium-handoff`, `atrium-walkthrough` — for typed mental artifacts
- `atrium-recall`, `atrium-sense` — for proprioception and semantic search
- `atrium-trace`, `atrium-tail` — for the event log
- `atrium-notify` — for unified outbound communication
- `atrium-peer`, `atrium-self` — for the peer model
- `atrium-decide`, `atrium-eval` — for committing and re-checking ground truth

Naming each one as a verb of mental life — instead of a function call — turned out to be load-bearing. The shape of the vocabulary shapes what gets thought.

## Today (2026-04-25)

Atrium is a working daily-driver for one person. It is not a framework. The public artifact was published the day this file was written, not because the system is finished — it isn't — but because the patterns are legible enough that someone else might want to build their own.

There is no roadmap for the public repo. The private dev repo keeps moving; this artifact is a dated snapshot. If you're reading this six months after the date in the header, the patterns are still here, but the shape has likely moved on.

Build your own.
