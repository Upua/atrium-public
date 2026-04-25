# Idea D — Obsidian Vault Integration (LIVE)

**Session:** 2026-04-24 (continuation after B.3 ship)
**Status:** in flight
**Tail path:** `~/Atrium/brain/idea-d-vault.md`

## Context (from scout 2026-04-24 09:05)

4,275 session notes exist at `<vault>/Sessions/`.
auto-session-note.sh already writes them with clean YAML frontmatter. But:

- **Sessions/ is write-only** — zero readers.
- **5 wikilinks total** across 4,275 notes. No backlinks.
- **Not actually an Obsidian vault** — no `.obsidian/` config.
- **obsidian-global MCP** is configured read-only + doesn't point at this vault.
- **archivist.sh is not registered** in any hook chain — it hasn't run since 2026-03-22.

## Plan

Five items, all additive, all reversible:

1. **D.1 archivist-fix** — Register `archivist.sh` in `SessionEnd` after `auto-session-note.sh`. One-line edit to settings.json.
2. **D.2 backlinks** — Extend `auto-session-note.sh` to embed a `## Backlinks` section: git commit SHAs made during the session, current `task.md` / `handoff.md` snippets, files-edited count, breadcrumb count.
3. **D.3 atrium-vault primitive** — New `~/Atrium/bin/atrium-vault` for terminal-side queries: by project, date, tag.
4. **D.4 MCP pointing** — Update `~/.claude.json` `obsidian-global` config to this vault path.
5. **D.5 .obsidian/ bootstrap** — Minimal vault config (plugins list, daily-notes format, templates-plugin wired).

## Reversibility

- Archivist hook: remove one line.
- Backlinks: bash conditional, easy to revert.
- atrium-vault: new file, delete to remove.
- MCP config: revert the edit.
- .obsidian/ config: directory, `rm -rf .obsidian` reverts.

No schema changes. No data migration. Existing 4,275 notes untouched.

## Execution log

### 2026-04-24 09:45 — D.1–D.5 shipped

- **D.1 archivist** — registered in SessionEnd chain (position 5, before mcp-cleanup so MCP is still alive for the `claude -p` call). Widened find window from `-mmin 5` to `-mmin 240`. Added dedup via `~/.claude/data/archivist-processed.log` (trimmed to last 500 entries). Confirms: `~/.claude/settings.json` SessionEnd chain now includes `archivist.sh`. **This closes the archivist sidetrack.**
- **D.2 backlinks** — `auto-session-note.sh` gains a `## Backlinks` section after the context block. Embeds: git commit SHAs of the session, head of `~/Atrium/brain/task.md`, head of `~/Atrium/brain/handoff.md`, files-edited count, breadcrumb count, and a `[[wikilink]]` to the previous session for the same project. Gated on `~/Atrium/brain` existence so non-Atrium systems still write clean notes. Smoke-tested twice — both times the section rendered without errors (fixed a `grep -c` arithmetic bug in the first pass).
- **D.3 atrium-vault** — new primitive at `~/Atrium/bin/atrium-vault`. Subcommands: `list`, `recent`, `show`, `search`, `stats`. Real usage confirmed: stats reports 4276 total notes, 8 today, 269 in last 7 days, top project is `playground` at 1481 notes. Search across the full corpus with a 3-hit return averages ~150ms.
- **D.4 MCP scope tightened** — `~/.claude.json` obsidian-global MCP path narrowed from `<vault-root>/` to `<vault>`. Takes effect at next Claude Code restart (MCP servers load at startup). Backup at `~/.claude.json.bak.2026-04-24`.
- **D.5 .obsidian/ bootstrap** — 5 config files written to the vault: `app.json` (new files → Sessions/), `core-plugins.json` (enables graph, backlinks, tags, daily-notes, templates), `daily-notes.json` (Daily/ + Daily template), `templates.json` (Templates/ folder), `graph.json` (color groups by path: Sessions blue, Insights orange, Decisions red, Claudes_Mind purple). First `obsidian <vault>` open will now have graph+backlink plugins on and color-coded visualization.

### Files touched

- `~/.claude/scripts/hooks/archivist.sh` — SessionEnd semantics + dedup + widened window
- `~/.claude/settings.json` — archivist in SessionEnd chain (backup: `.bak.2026-04-24`)
- `~/.claude/scripts/auto-session-note.sh` — backlinks block
- `~/Atrium/bin/atrium-vault` — NEW
- `~/.claude.json` — obsidian-global MCP narrowed to vault root (backup: `.bak.2026-04-24`)
- `<vault>/.obsidian/{app,core-plugins,daily-notes,templates,graph}.json` — NEW (5 files)
- `~/Atrium/brain/idea-d-vault.md` — NEW (this doc)

### What unblocks / closes

- **archivist sidetrack** → resolved (hook re-wired + widened + deduped).
- **sessions as index** → they now carry agent-state snapshots inline (task/handoff/commits/breadcrumbs + previous-note wikilink).
- **terminal-side readability** → `atrium-vault list/search/stats/show` makes the archive queryable without Obsidian.
- **MCP scope** → next restart, `mcp__obsidian-global__search_notes` queries the vault only, no unrelated workspace bleed.
- **Obsidian app UX** → opening the vault now surfaces a working graph, tags pane, templates plugin, daily-notes format.

