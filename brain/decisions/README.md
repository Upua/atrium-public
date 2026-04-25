# decisions/

This directory holds typed decision artifacts produced by `atrium-decide`. Each file is a dated post-mortem of a non-trivial choice — the kind where the reasoning matters as much as the outcome.

Filename pattern: `YYYY-MM-DD-<slug>.md`

These records exist so a future session (or a reader) gets the WHY behind shipped and parked items, not just the WHAT. They are append-only. A decision that gets reversed gets a new file, not an edit.

## Current decisions

- **2026-04-20-hud-honesty-audit.md** — fix HUD lies discovered during v0.6 phase; dashboard was showing stale/fabricated state
- **2026-04-20-seed-v07-cognitive-verb-consolidation.md** — collapse 25 atrium primitives into ~8 cognitive verbs; reduce surface area before publishing
- **2026-04-24-chroma-cortex-unification.md** — retire ChromaDB, migrate sessions corpus to Cortex; one embedding store, not two
- **2026-04-24-park-idea-e-teaching-mode.md** — park narration/teaching mode; no use trigger has surfaced in real sessions
- **2026-04-24-park-idea-f-pi-telemetry.md** — park Pi → Atrium telemetry push; Pi is stable enough that the overhead isn't justified yet
- **2026-04-24-park-idea-g-multi-instance.md** — park multi-instance coordination layer; needs a usage audit before adding the complexity

Parked items are not abandoned — they re-enter when a concrete trigger appears.
