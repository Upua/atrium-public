# Decision: Park Idea E — Teaching mode

**Date:** 2026-04-24
**Context:** Roadmap ideas triage at end of day's shipping sprint. E was the "narrated agent output mode — toggle that adds narration directives to the system prompt so Claude explains its thinking step-by-step, for didactic use."

## Verdict: **PARK** — decision recorded, not implemented. No work item remains open.

## Why parked (not killed, not built)

**Low-leverage in the current shape.** The value proposition of E is "ask Claude to narrate more." But that's already possible inline: any prompt can include *"walk me through your reasoning"* or *"explain each step before you take it"* and Claude adapts. A keybind/toggle that flips a prompt augmentation doesn't add much beyond saving ~8 keystrokes — and adds a mode to remember, a UI affordance to maintain, a prompt template to keep in sync with model updates.

**The real trigger for E would be a recurring user experience of**: *"I keep having to ask Claude to slow down and narrate — a toggle would save me the repetition."* That hasn't happened. The ask emerged during brainstorm, not during frustration.

**Adjacent feature that IS valuable:** session-level instruction hooks (already exist via CLAUDE.md and UserPromptSubmit prepends). Those cover the "always-on narrator" case without a dedicated mode.

## When to revisit

- If in 30 days we see 3+ sessions where the user explicitly asks for narration multiple times → trigger fired, build E.
- If a teaching/demo use case emerges (e.g., Niklas showing the system to a collaborator repeatedly) → build E with that specific UX in mind.
- If a model-level narration primitive lands in Claude Code (similar to reasoning output) → rethink E entirely.

## Kill condition (not park, actually drop from roadmap)

If in 90 days no trigger has surfaced AND we've added other observability primitives (atrium-hud narration? auto-caption?), delete E entirely with a CHANGELOG note.

## Reversibility

Trivial — parking is a no-op. Anyone can pull E back by writing the prompt augmentation + keybind. Scope is small (~1 hour of work) if the trigger surfaces.
