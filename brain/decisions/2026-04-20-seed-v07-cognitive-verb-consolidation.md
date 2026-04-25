# Decision: seed v0.7 — cognitive verb consolidation

**Date:** 2026-04-20
**Logged by:** claude (with Gemini co-design)

## Context
Mission.md v2.1 commits to collapsing 25 bash-shaped atrium-* primitives
into ~8 cognitive verbs matching agent intent. First draft proposed
`observe/act/recall/claim/plan/decide/pair/guard` with `act` as a bucket
for edit/append/write/commit.

## Options
1. **8-verb taxonomy with `act` bucket** — forces cognitive categories
   at the invocation surface. Clean conceptually, awkward at the CLI
   (`atrium act edit` vs `atrium edit`).
2. **Git-style flat dispatcher** (Gemini's counter-proposal) — drop
   `act`, promote atoms to first-class verbs, single `atrium` command
   with subcommands, tab-completion reveals the surface.
3. **Keep current shape, just consolidate help docs** — lowest risk,
   zero muscle-memory cost, but doesn't advance the vision.

## Choice
Option 2 — git-style flat dispatcher with 12 first-class verbs:
observe, edit, append, write, commit, peer, plan, guard, decide,
recall, handoff, claim.

## Why
"`act` adds zero semantic value; it's just a bucket to hold the verbs
we actually care about." The cognitive taxonomy is useful in the
mission document, but forcing it into the invocation surface makes
every write-oriented call 30% longer for no clarity win. Git-style
gets us better discoverability (tab completion on `atrium `), cleaner
PATH, and keeps the atoms as the atoms they already are.

## Reversibility
Medium. Legacy `atrium-<name>` scripts stay functional during the
transition, so rollback is "remove the dispatcher, keep the atoms."
But muscle memory shifts are the real cost — once agents start typing
`atrium observe`, rolling back to `atrium-sense` would itself be
disruptive.

## Follow-ups
- Gemini implementing the `atrium` dispatcher (extend existing launcher)
- Once-per-session stderr nudge on legacy invocations via marker file
- `atrium help` parses new verb headers, surfaces roster
- After dispatcher lands: cross-review, close v0.7, move to v0.8 (memory)
