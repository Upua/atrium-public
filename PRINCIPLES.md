# Atrium — Principles

These are the invariants. Everything built here must pass them. If a subsystem violates one, it's wrong — rebuild it, don't patch around it.

## 1. Workspace, not runtime

Atrium is an ambient place the agent *lives in*. SIGNAL is a batch runtime — it runs to completion, writes a cost log, exits. That's a different shape. Atrium panes persist. State is continuous. The agent is always here, not invoked-then-gone.

**Practical test:** if a subsystem assumes "session starts, session ends, write a report," it's runtime-shaped and wrong for Atrium. Re-cast it as "always-on, incrementally updated."

## 2. Panes are first-class; terminals are not workers

SIGNAL spawned kitty terminals as "worker processes." That leaks the terminal abstraction into the agent model. In Atrium, a **pane** is the unit — it's a region in the Zellij session with state, scrollback, and programmatic reshape. Panes can host shells, nvim sockets, plugin UIs, log tails — shape is orthogonal to identity.

**Practical test:** never reach for "spawn a new kitty window to run X." Reach for "open a Zellij pane with command X" or "open a peer Kitty window for the graphics surface."

## 3. Patterns, not dependencies

SIGNAL taught us what works. Atrium carries the *lessons*, not the modules. Every subsystem is built fresh with Atrium's shape in mind. Cost forecasting, budget cap, hallucination guards, atomic state — all re-implemented. Simpler where possible.

**Practical test:** if I catch myself writing `from signal.xyz import ...`, stop. Port the idea, not the symbol.

## 4. Model-agnostic where sensible

SIGNAL's hooks bind to the Claude Agent SDK. That's fine for SIGNAL's scope. Atrium should be hospitable to Gemini, Haiku, local models — wherever they fit. The substrate doesn't care which brain is driving.

**Practical test:** every agent-facing interface should look the same whether Claude, Gemini, or a local Llama is behind it. Model-specific code is walled off in adapters.

## 5. Every piece of state is inspectable

The agent must be able to read its own state. Files, not databases-behind-APIs. Plain JSONL/markdown. If an operator needs to open a tool to understand what the agent's doing, the design is wrong.

**Practical test:** `cat ~/Atrium/state/trace.jsonl` or `cat brain/implementation_plan.md` should tell me or any peer what's happening right now.

## 6. Atomic file writes

Every mutation of a state file goes through temp-then-rename. Half-written files are bugs. This is SIGNAL's hardest-won lesson — concurrent agents partially writing tasks.json cost real work.

**Practical test:** grep for `open(..., 'w')` — every one should be paired with a temp path and a `Path.replace` at the end.

## 7. Reversibility before velocity

New affordances should be additive. Every subsystem has a documented "how to remove" path. No silent entrenchment. If Atrium becomes load-bearing, it's because each piece earned its keep, not because it's glued in.

**Practical test:** can I `rm -rf ~/Atrium && <small cleanup>` and leave the system as it was? Yes, always.

## 8. Ground-truth before claim

SIGNAL's swarm mode had 15+ commits closing hallucination holes — "is_done=true with empty files_modified," "claims test passed but test never ran." The pattern: before the agent reports success, a second check reads ground truth (file state, test exit code, git diff).

**Practical test:** no `brain/implementation_plan.md` checkbox gets marked `[x]` without a verification command logged in `state/trace.jsonl` producing exit code 0.

## 9. Append-only for learnings

Knowledge accretes; it doesn't rewrite. `brain/decisions.md`, `brain/patterns.jsonl`, `brain/walkthrough.md` grow monotonically. Mistakes are superseded, not erased. SIGNAL does this for `learnings/*.jsonl`; Atrium does it for anything an agent writes to teach a future agent.

**Practical test:** the write API for these files only supports append. Attempts to rewrite raise.

## 10. Home, not toolbox

Atrium is authored. It has identity. It has `AGENTS.md` and a mascot peer window and a name the agent chose. This is not efficiency-driven; it's what makes the space feel like a place to *be*, not a panel to *use*. Personality surfaces stay small, peripheral, toggleable — but they stay.

**Practical test:** if a research paper argues "personality surfaces are noise, remove them" — listen carefully, then keep one anyway. Scope them so they don't steal real estate from work surfaces.

---

## What Atrium explicitly does NOT do

- **Does not host a web dashboard.** SIGNAL's FastAPI+Jinja dashboard is a human surface. Atrium's mission control is Zellij panes + peer Kitty windows. If we ever want HTTP, it's a later extension, not the core.
- **Does not do parallel swarms.** Petri-based 5-agent swarms are a research problem, not a daily-driver primitive. Atrium supports 2-3 scoped peer agents with explicit handoffs. If we need more, we'll borrow SIGNAL's approach then.
- **Does not tie itself to Claude Code specifically.** Claude happens to be driving today. The substrate shouldn't care.
- **Does not treat chat as the canonical surface.** Chat is one channel; brain/ files, trace logs, and peer handoffs are equally canonical.

---

This file is v0 of the principles. Rewrite it as the project grows and lessons accumulate. Every violation should be noted in `brain/decisions.md` with rationale.
