# atrium

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg) ![Status: artifact](https://img.shields.io/badge/status-artifact-orange.svg) ![Last verified](https://img.shields.io/badge/last%20verified-2026--04--25-brightgreen.svg) ![Companion: captain-meridian-stack](https://img.shields.io/badge/companion-captain--meridian--stack--public-lightgrey.svg)

Workspace primitives for treating Claude as a co-inhabitant, not a tool.

> **This is a published artifact, not a maintained project.**
> **Last verified:** 2026-04-25.

---

## What this is

Working code from one person's daily-driver personal AI infrastructure. About thirty `atrium-*` shell verbs (cognitive primitives), a small Python lib (`lib/atrium_notify.py` and helpers), philosophy docs (`AGENTS.md`, `PRINCIPLES.md`, `PATTERNS.md`), and the brain corpus (`brain/decisions/`, `brain/idea-*.md`, templates) that explains the patterns.

This is the workspace half. The narrative + roadmap + competitive landscape live in [`captain-meridian-stack`](https://github.com/Upua/captain-meridian-stack-public).

## What this isn't

- A framework you can `pip install`
- A maintained project with issues, PRs, and a roadmap driven by users
- Multi-provider, portable, generalized, or production-hardened
- Useful as-is on your machine without significant adaptation

## How to read this repo

1. Start with [`AGENTS.md`](AGENTS.md), [`PRINCIPLES.md`](PRINCIPLES.md), [`PATTERNS.md`](PATTERNS.md) — the operating philosophy
2. Then [`brain/idea-a0-embed-daemon.md`](brain/idea-a0-embed-daemon.md), [`brain/idea-b-dmn-peer.md`](brain/idea-b-dmn-peer.md), [`brain/idea-a4-recall-feedback.md`](brain/idea-a4-recall-feedback.md) — the load-bearing patterns
3. Then [`bin/`](bin/) — the actual cognitive verbs as shell scripts
4. Then [`brain/GROWTH.md`](brain/GROWTH.md) — how it got here

If you want to understand the system, read the philosophy first and the code second. The code only makes sense once you accept the framing.

## What "artifact, not project" means

- **No issues accepted.** This isn't a place to file bug reports or feature requests.
- **No PRs accepted.** Adapt patterns into your own fork; don't expect upstream merges.
- **No support promised.** The author has a day job and uses this every day, but doesn't owe time to questions.
- **No promises about updates.** This is a snapshot. If the "Last verified" date in this README is six months stale when you find it, the patterns are still here, but the live system has moved on.

If those boundaries don't work for you, that's fine — read the patterns, build your own version with your own stack.

## License

MIT. See [LICENSE](LICENSE).

The code is permissive; the philosophy doesn't transfer by copying. You'll have to live with your own version a while before it becomes yours.

## Companion repo

[`captain-meridian-stack`](https://github.com/Upua/captain-meridian-stack-public) — meta repo with `ROADMAP.md`, `ARCHITECTURE.md`, `LANDSCAPE.md` (where this sits in the 2026 ecosystem), and the build narrative.

For the long-form essay introducing the philosophy, see [Building a home for an AI](https://github.com/Upua/captain-meridian-stack-public/blob/main/docs/posts/2026-04-25-building-a-home-for-an-ai.md).

## Author

Upua (`Upua` on GitHub). Built collaboratively with Claude (Opus and Sonnet). The collaboration is named in the writing because the framing was earned through it, not stipulated.
