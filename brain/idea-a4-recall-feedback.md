# Idea A.4 — Recall Feedback Loop (LIVE)

**Session:** 2026-04-24 (continuation after D.5 ship)
**Status:** in flight
**Tail:** `~/Atrium/brain/idea-a4-recall-feedback.md`

## Goal

Close the recall loop. Right now memory-surface.sh surfaces ChromaDB + Cortex hits on every substantive prompt, but we never learn which ones were actually useful. A.4 adds observability (log surfaces), detection (fuzzy-match cited content in response), scoring (Bayesian-smoothed useful/ignored ratio), and application (rerank future surfaces by learned usefulness).

## Design

**Storage** — SQLite at `~/.claude/cache/recall-feedback.db`:

```
surfaces(id PK, ts, session_id, prompt_hash, source_table, source_id,
         preview TEXT, raw_score REAL)
scores(source_table, source_id, useful_count, ignored_count,
       last_seen_ts, PRIMARY KEY(source_table, source_id))
```

**Scoring formula** — Laplace-smoothed posterior:

```
posterior = (useful + 1) / (useful + ignored + 2)    # ∈ [0, 1], seed 0.5
multiplier = 0.7 + 0.6 * posterior                   # ∈ [0.7, 1.3]
final_score = raw_similarity * multiplier
```

Brand-new items land at multiplier 1.0, consistently useful items boost by 30%, consistently ignored items sink by 30%. Doesn't amplify noise for low-sample memories.

**Detection heuristic** — fuzzy match preview against response text: normalize both to lowercase, strip punctuation, split into trigrams. If ≥3 trigrams from preview appear in response → useful++. Else → ignored++. Tight enough to avoid false positives from common words, loose enough to credit partial paraphrase.

## Reversibility

- Every read path gates on `[ -f ~/.claude/cache/recall-feedback.db ]`.
- Delete the DB → today's behavior restored exactly.
- No modification to Cortex or ChromaDB schemas.
- New detector hook registered in Stop chain but gated behind DB existence.

## Execution log

### 2026-04-24 10:05 — A.4.1 through A.4.5 all shipped

- **A.4.1 schema** — `~/.claude/scripts/recall_feedback.py` (~200 lines). Two tables: `surfaces` (append-only log of what was shown), `scores` (per-memory useful/ignored counts). Source_id is TEXT to cover Cortex integer ids + ChromaDB string ids. WAL journal. Auto-creates on first write.
- **A.4.2 logging** — `memory-surface.sh`'s ChromaDB and Cortex blocks both log every emitted hit via `rf.log_surface(session_id, prompt_hash, source_table, source_id, preview, raw_score)`. Zero-delta if the recall_feedback module is missing.
- **A.4.3 detector** — new `~/.claude/scripts/hooks/recall-detector.sh` registered in Stop chain (position 4, after auto-session-note, cortex-bridge, skill-capture). Reads `last_assistant_message` (or falls back to transcript_path), calls `rf.credit_session_surfaces(session_id, response, lookback_seconds=3600)`. Trigram detection with threshold=2 (calibrated on paraphrase tests; ≥3 missed clear citations, =1 was noise).
- **A.4.4 multiplier** — both surfacing paths multiply raw similarity by `rf.get_multiplier(src, sid)`. Formula: `0.7 + 0.6 * laplace_posterior` → ∈ [0.7, 1.3]. Seed at 1.0 for new items (posterior=0.5); consistently useful boosts 30%, consistently ignored sinks 30%. Cortex path overfetches 15 → multiplier-reranks → emits top 5.
- **A.4.5 inspector** — `atrium-recall feedback [summary|useful|ignored|recent]` subcommand. Smoke-tested all modes; output is clean, greppable, shows per-memory multiplier + credit counts.

### Verification

- End-to-end: prompt surfaced 5 Cortex hits, test response cited 3 → 3 useful credits + 2 ignored. Multipliers for cited memories moved from 1.0 → 1.1 on next surface.
- Gate: with the DB deleted, `rf.get_multiplier()` returns 1.0 for everything → identical ranking to pre-A.4.
- All test data cleared; production starts at 0/0/0.

### Files

- `~/.claude/scripts/recall_feedback.py` — NEW (shared module)
- `~/.claude/scripts/hooks/recall-detector.sh` — NEW (Stop hook)
- `~/.claude/scripts/hooks/memory-surface.sh` — MODIFIED (logging + multiplier apply in both source paths)
- `~/.claude/settings.json` — MODIFIED (detector registered in Stop)
- `~/Atrium/bin/atrium-recall` — MODIFIED (feedback subcommand)
- All mirrored into `captain-meridian-stack/claude-config/`.

### What closes

- Ambient recall is no longer a one-way broadcast. Every surface now has an observable outcome; the system's ranking improves as we use it.
- Next pass that should fire once data accumulates: re-evaluate whether the trigram threshold=2 produces believable scores. Currently calibrated on one test case; look at production data after a week.
