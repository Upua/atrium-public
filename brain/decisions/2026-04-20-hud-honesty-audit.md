# Decision: HUD Honesty Audit (v0.6 Phase 1)

**Date:** 2026-04-20
**Context:** Atrium v0.6 "honest observability" phase. Both Claude and Gemini
independently flagged HUD lies as today's #1 trust-erosion problem. Smoking
gun: HUD showed `spend $0 of $870` while handoff reported all-time $17657.

## Investigation

Traced every HUD number to its source:

| Number | Source | Status pre-audit | Cause |
|---|---|---|---|
| `$870` daily budget | state/budget.json `daily_usd` | correct (user-tuned) | — |
| `$0` today spent | sum(cost_usd) over today's trace events | FALSE ZERO | cost-ingest-watcher daemon stopped for ~1 day |
| burn rate | derived from cost events | $0 | downstream of above |
| sparkline | last 10 cost events | stale | downstream |
| context window % | latest tool event's tokens_in + cache | honest | — |
| uptime | first-today event ts | honest | — |
| `last tool·Xh` | ts of last tool event | honest | — |

252 tool events accumulated today before the audit — zero had `cost_usd`
populated. After manually running `atrium-cost-ingest scan`: 460/713 events
gained cost_usd, today's total went from $0 to $163.86.

## Root cause

The cost-ingest-watcher is a background daemon that tails session JSONLs and
stamps cost_usd onto trace events as they arrive. It had been stopped (when?
unclear — possibly since yesterday's reboot cycle). session-begin ran a
one-shot `atrium-cost-ingest scan` but didn't verify the watcher was still
running, so freshly-arriving tool events never got stamped.

## Fix

1. Started the watcher: `atrium-daemon start cost-ingest-watcher -- atrium-cost-ingest watch`
2. Patched session-begin to auto-restart the watcher if not running. Session 1
   will pay the one-shot scan cost, then the watcher keeps HUD live.
3. No changes needed to atrium-hud itself — once cost_usd is present on new
   events, the HUD computes correctly. The HUD wasn't lying; it was reporting
   the truth of an upstream blind spot.

## Reversibility

Fully reversible — remove the watcher-start block from session-begin to go
back to one-shot-scan-only. The daemon itself can be stopped via
`atrium-daemon stop cost-ingest-watcher`.

## Why

Proprioception is load-bearing. A body that can't feel its own budget spend
will either over-consume (no pain signal) or become paranoid (over-checking).
The HUD's job is to be a dumb honest mirror; the fix was upstream.

## Follow-ups

- Session-begin should check ALL daemons it depends on, not just
  cost-ingest-watcher. Filed as a candidate for v0.6 Phase 2.
- `atrium-sense` (Gemini's v0.6 assignment) should include a daemon
  health-check section so stopped workers surface early.
