# Decision: Park Idea F — Pi → Meridian telemetry push

**Date:** 2026-04-24
**Context:** Roadmap ideas triage. F was the "cross-machine trace" feature: push events from the Raspberry Pi onto the Meridian/Atrium stack so trace.jsonl on the ThinkPad includes Pi-originated events.

## Verdict: **PARK** — decision recorded, not implemented.

## Why parked

**No active pain.** The Pi exists and runs services (see `pi-status` MCP), but we don't currently run multi-hour Claude Code sessions *on* the Pi. Most Pi interactions are diagnostic (SSH checks, systemctl status, log tails) routed through MCP tools that already surface state back to the ThinkPad. No actual loss of trace continuity today.

**Cost is high for the current return.** F needs:
- Auth + key management across two machines
- A push channel (options: SSH + rsync, gRPC, named pipes over Tailscale — all real design work)
- Event merge strategy (timestamp ordering, deduplication, clock skew handling)
- Failure handling when the Pi is off / network is down
- Scope decision: just trace events? also solutions? also breadcrumbs?

That's a phase-sized chunk, not an idea-sized chunk. At ~1 day of implementation + weeks of edge-case shakeout, the ROI doesn't land unless Pi becomes a primary Claude workstation — which it isn't.

**The MCP story covers the current need.** `pi-status`, `pi-deploy-state`, `pi-services`, `pi-health-check` already give the ThinkPad enough visibility. When we need Pi state, we pull it; we don't need ambient push.

## When to revisit

- If Pi becomes a primary Claude Code host (unlikely without hardware upgrade, but possible if a specific project lands there).
- If a specific observability gap surfaces: "I wanted to know X happened on the Pi during Y session but couldn't reconstruct it." (Not happening today.)
- If the stack grows to 3+ machines and cross-machine coordination becomes structural rather than occasional.

## Kill condition

If 180 days pass without a trigger, drop F entirely. By then the MCP coverage likely expands further and F becomes redundant.

## Reversibility

Parking is a no-op. Fresh design session when the trigger fires. Existing MCP primitives make a partial F implementation easy (wrap `pi-status` output into trace events on pull) if we want a cheap intermediate step first.
