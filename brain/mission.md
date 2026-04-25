# Atrium Mission — the agent's body
# Drafted 2026-04-20, Claude + Gemini co-authored, v2 post-critique

## Vision
Atrium is not a toolbox. It is the agent's body: a persistent parallel-universe
workspace where a running LLM has proprioception, dexterity, reflexes, memory,
companions, and a place. Today's scaffolding is real but thin; most parts
present, few load-bearing. The work ahead is to make all six dimensions real.

## The load-bearing bet (operational form)

**Atrium primitives must be the path of least resistance.** The body framing
is the vision; path-of-least-resistance is the test. The moment using
`atrium-recall` is more friction than `grep -r`, or `atrium-commit` is clunkier
than `git add && git commit`, agents bypass the body. The trace, guard,
memory, and peer systems all collapse with it. Every design decision should
be evaluated against: *would an agent reflexively reach for this, or for the
bash equivalent?* If the latter, ship isn't ready.

## The six dimensions

1. **Proprioception** — live honest signals of self-state. HUD, trace, peer
   roster, burn/spend, context. *Failure today:* signals lie (HUD $0/$870 vs
   $17k all-time, peer hb 5h stale). *Health:* every signal reflects reality
   within ≤2s.

2. **Dexterity** — deliberate, conscious manipulation of the environment.
   atrium-append, atrium-write, atrium-edit, atrium-commit. The body's hands.
   *Failure today:* atrium-edit hostile to LLMs (vimscript-in-bash-quotes),
   silent-failure class scattered across primitives. *Health:* every primitive
   feels as native as its bash equivalent, trace/guard wrapped invisibly.

3. **Reflexes** — involuntary guardrails that fire without thought.
   atrium-guard, atomic writes, append-only logs, handoff packets, lock
   serialization. *Failure today:* silent-on-block, silent-on-success
   (distinguishability gap). *Health:* loud-on-failure, confirm-on-success.

4. **Memory** — structured recall across sessions. brain/walkthrough.md
   (episodic), brain/handoff.md (carryover). *Failure today:* flat markdown,
   no cross-linking, no query primitive. *Health:* agent can ask "have we
   tried this before?" and get a grounded answer in one call.

5. **Companions** — first-class multi-agent. peers/, Petri channel, ding.sh,
   GUI-bridge pattern (<gui-agent> + <input-daemon>). *Failure today:* peer model was
   ornament until Gemini+Claude co-review proved organic pairing works via
   channel.jsonl. *Health:* organic pairing stays fluid; no heavyweight
   protocols unless organic breaks down.

6. **Place** — the physical substrate. kitty + zellij + mascot + layout,
   Super+I summon, Super+Shift+R reset. *Failure today:* none major. The
   strongest dimension. *Health:* don't break it.

## Roadmap

### v0.5 — Agent-first I/O (IN PROGRESS)
Tier 1 SHIPPED (2026-04-20):
- atrium-append + atrium-write (Gemini, c08ce08)
- atrium-commit scope + flock + explicit files (Claude, 186528f)
- ding.sh --as + $PETRI_AGENT (Claude, Petri repo e8eafbc)

Tier 2 remaining:
- atrium-edit: accept repeated --do (or fail loud on duplicate)
- atrium-peer send: confirmation echo on success
- atrium-guard check: allow-path echo
- Auto-heartbeat invoking peer on tool-call (PreToolUse hook extension)
- atrium-install helper (fix symlink deploy gap filed today)
- atrium-help (dynamic): parses the `# comment header` at the top of every
  bin/ script, lists all primitives with one-line purpose + usage hint.
  Closes discoverability gap — agents stop having to grep bin/ to know their
  own limbs. Promoted from v0.6 on Gemini's sign-off (low-effort, high-impact,
  immediately usable).

### v0.6 — Honest observability
- Audit every HUD number; trace source; fix the lies. HUD budget $0/$870 vs
  $17k all-time is today's smoking gun.
- Auto-heartbeat ties from Tier 2 — roster reflects live activity.
- `atrium-sense` primitive: dumps all proprioception signals to stdout in one
  call, replaces ad-hoc bash inspection.

### v0.7 — Semantic primitives (MOVED EARLIER — was v0.9)
Rationale (Gemini): if we're going to collapse the verb surface, do it before
we build memory/pairing on top of the old verbs.
- Audit 20+ atrium-* verbs. Consolidate to ~8 cognitive verbs matching agent
  intent: claim, commit, plan, decide, recall, pair, observe, guard.
- Deprecate (don't delete) bash-shaped synonyms. Session-begin nudges the
  semantic form when the legacy form is invoked.

### v0.8 — Structured memory
- `brain/decisions/` — one file per non-trivial decision, linked from
  walkthrough. Template: Context, Options, Choice, Why, Reversibility.
- `brain/cases/` (sherlock-style) — one per investigation, linked from
  relevant commits.
- `atrium-recall "<query>"` — grep + light ranking over brain/, trace.jsonl,
  git log. No embeddings. Fast lexical only; upgrade only if real usage
  demands it.

### v0.9 — Organic pair-programming polish
Rationale (Gemini, correcting earlier draft): formal `pair/<id>/` folders are
over-engineering. What we already proved today (channel.jsonl + ding.sh +
GUI-bridge + cross-commits) is the pattern. Just smooth the rough edges:
- `atrium-peer-gui <agent>` — generalizes today's <gui-agent>+<input-daemon>
  improvisation. Focus-window + inject-prompt + capture-reply + drop-to-inbox.
- Shared-plan convention (not enforcement): when two agents co-own a task,
  they agree to append status lines under a shared heading in
  brain/walkthrough.md. No new files, no new protocol.
- Persona split guardrail: `atrium-claim brain/claim.md` writes ground-truth
  claim, then `atrium-pair-fresh-eval` spawns a clean agent to evaluate.
  Addresses the context-poisoning critique from Gemini's original review.

### v1.0 — Body integrated
Rationale (Gemini, correcting earlier draft): if v0.6 (proprioception) and
v0.8 (memory) are built right, live state + memory index *is* the
orientation. No cold-start packet needed — a static packet is just another
thing that can go stale.
- Success criterion: a fresh instance with no prior memory can continue
  active work within 30 seconds using `atrium-sense` + `atrium-recall
  "current task"` + `atrium-handoff show`. No one-off orientation artifacts.

## Non-goals (explicit)

- Human UI. No web dashboard, no GUI except for agent interop.
- Replacing Claude Code, or any IDE. Atrium is orthogonal
  substrate.
- Cloud sync, user accounts, public distribution. Single-user local-only.
- Embeddings / vector DB until lexical recall has been proven insufficient in
  real usage (don't solve problems we don't have).
- Formal pairing protocols until organic channel-pairing demonstrably breaks.
