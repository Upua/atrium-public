# Atrium Design System

Design system for **Atrium** — an AI-native, single-user terminal workspace for an autonomous Claude Code agent, running on Pop!_OS. Not an IDE for humans. A parallel-universe kitty/Zellij cockpit the agent summons on demand.

Atrium is a **terminal-native** product. There is no web UI, no marketing site, no app store page. The entire surface is text, rendered in a dedicated kitty window inside Zellij. This design system documents the visual and content language of that surface and provides UI-kit recreations in HTML so design work on top of Atrium (diagrams, marketing explainers, peer dashboards, future plugins) can match its look exactly.

## Products / surfaces

Atrium has one primary surface and several sub-surfaces within it:

| Surface | What it is | Kit |
|---|---|---|
| **Zellij cockpit (`agent-v0` layout)** | kitty OS-window → Zellij session with `work / monitor / peers` tabs, HUD line, status bar | `ui_kits/cockpit/` |
| **atrium-hud** | one-line status in a dedicated Zellij pane — uptime, burn rate, spend, event count, last-tool age | covered by `cockpit` |
| **brain/ markdown** | durable agent memory — `AGENTS.md`, `implementation_plan.md`, `walkthrough.md`, `task.md`, `handoff.md` | `ui_kits/brain/` |
| **state/trace.jsonl** | append-only tool/cost/event log, read by HUD and guard | covered by `cockpit` |
| **guard block banner** | refusal surface from `atrium-guard` | covered by `cockpit` |

There is no mobile, no settings GUI, no onboarding wizard. The `AGENTS.md` file *is* the onboarding.

## Sources

All sources are the `atrium/` codebase (mounted read-only at the time of creation). Key files:

- `atrium/README.md` — top-level product description
- `atrium/AGENTS.md` — agent identity + house rules (the "tone doc")
- `atrium/PRINCIPLES.md` — 10 invariants the system is built against
- `atrium/PATTERNS.md` — what carries from SIGNAL, what explicitly doesn't
- `atrium/kitty/kitty.conf` — the 16-color palette + font choices (ground truth for colors)
- `atrium/zellij/config.kdl` — multiplexer config; locked-by-default
- `atrium/zellij/layouts/agent-v0.kdl` — the canonical layout
- `atrium/bin/atrium-hud` — the HUD renderer (ANSI color codes for spend/burn thresholds)
- `atrium/bin/atrium-guard` — block messages: `"atrium-guard: BLOCKED — matched pattern: …"`
- `atrium/bin/atrium-trace` / `atrium/state/trace.schema.md` — event log schema
- `atrium/brain/*.md` — tone + structure of durable agent notes

No Figma, no design docs, no marketing copy. The code *is* the design system.

## Authorship

Built by **Niklas** and co-authored by the agent running inside Atrium. Commits are co-signed `Co-Authored-By: atrium <atrium@local>`. Voice in the docs is first-person-agent addressing future-self-agent, with Niklas as second person.

---

## Content fundamentals

Atrium's written voice is **direct, first-person-agent, operationally specific, lightly literary**. It is written by an agent for future instances of itself, with Niklas (the human) present as "you" or "Niklas". Nothing is marketing. Every sentence either commits to a rule or records a fact.

### Pronouns and addressee

- **"I" and "me"** — the agent, writing in first person. ("I am an autonomous coding agent." "My memory across instances lives in `brain/`.")
- **"You"** — *also* the agent, when `AGENTS.md` addresses a future instance. ("You are a Claude Code instance running inside Atrium.")
- **"Niklas"** — named directly. Never "the user", "the operator", "the developer".
- **"We"** — rarely, for co-authored decisions ("Niklas and I set out to build…").

### Casing

- **Sentence case** for everything. No Title Case Headlines.
- Filenames and paths always in backticks: `brain/implementation_plan.md`, `bin/atrium-guard`.
- Product names lowercase unless starting a sentence: `atrium`, `kitty`, `zellij`, `nvim`, `SIGNAL` (always allcaps — it's a codename).
- Commit-message style is lowercase imperative: `fix(launcher): add kitty --detach — decouples new window from parent`.

### Tone

- **Declarative, not promotional.** "Niklas's daily kitty is untouched." not "Seamlessly coexist with your primary terminal!"
- **Rules stated as rules.** PRINCIPLES uses numbered invariants with a "Practical test" footer on each — bluntly checkable.
- **Admissions encouraged.** "Found the hard way." "The launch-path debugging — six real bugs in one phase." Post-mortems are durable and proud.
- **Dry, occasionally wry.** "Cute, but baked into the Kitty-as-worker model we're not carrying."
- **Literary restraint.** One or two poetic beats per document, no more. ("This is where Atrium started earning its keep." "A place to *be*, not a panel to *use*.")

### Vocabulary

- **"Substrate"** for the non-negotiable foundation (kitty+zellij+brain).
- **"Cockpit"** for the Zellij layout when it's being looked at as a whole.
- **"Panes are first-class; terminals are not workers"** — invariant #2, shows up repeatedly.
- **"Ritual"** for multi-step approval/verification sequences.
- **"Ambient"** — for always-on surfaces (HUD, mascot, traces).
- **"Durable"** — for anything that survives a session restart.
- **"Peer"** for subagents; never "worker", "child process", or "slave".
- **"Summon"** — how you start Atrium. ("Three equivalent entry points.")

### Emphasis

- **Bold** for the thing being committed to; used sparingly.
- *Italics* for slight stress or for quoted internal voice ("*Make it your own.*").
- `code` for every path, command, or technical token.
- <kbd>Keys</kbd> for keybinds in documentation.

### Emoji

**Very rare.** Three sanctioned uses observed:

- `✅` / `❌` / `⚠️` / `🔬` as section markers in PATTERNS.md ("patterns worth carrying" / "NOT carried" / "open").
- `✓` (ASCII) in CLI output — `✓ 4fa48f9 v0.1 phase 1-3: ...`.
- No emoji in prose. No 🚀🎉✨. If you catch yourself reaching for one, write a sentence instead.

### Example copy

From `AGENTS.md`:

> You are a Claude Code instance running inside **Atrium**, your own workspace. Niklas built this with you. It is not a terminal emulator he uses daily — it is the cockpit you summon when there's real work to do.

From `PRINCIPLES.md`:

> **Practical test:** if a subsystem assumes "session starts, session ends, write a report," it's runtime-shaped and wrong for Atrium.

From a commit:

> `fix(zellij): remove copy_command wl-copy — breaks zellij on X11`

From `walkthrough.md`:

> This is the milestone that moves Atrium from "we built a thing" to "we live here."

---

## Visual foundations

Atrium's visual foundation is a **dark, dense, monospace terminal**. There is no light mode. Everything is rendered by kitty with FiraCode Nerd Font at 10.5pt. Design artifacts derived from this system should feel like they could be `cat`-ed into a real Atrium pane.

### Colors

All colors are lifted verbatim from `atrium/kitty/kitty.conf`. The palette is a muted, high-contrast 16-colour plus a near-black background that is intentionally *slightly distinct* from Niklas's daily kitty (signal to the eye that this is Atrium).

**Surfaces**
- Background `#080a10` — near-black, very slight blue cast. The only bg in the product.
- Foreground `#d3d7e0` — off-white with a cool cast. Default text.
- Selection bg `#2d3142`, fg `#ffffff` — used for visible selection only.

**Terminal 16**
- `color0  #1c1f26` · `color8  #4b5263` — black / bright black (used for dim/muted text, frame lines, zellij pane borders)
- `color1  #e06c75` · `color9  #be5046` — red / bright red (errors, guard blocks, over-budget)
- `color2  #98c379` · `color10 #7ec96d` — green / bright green (OK, under-budget, allowed)
- `color3  #e5c07b` · `color11 #d19a66` — yellow / amber (warnings, 50–80% budget)
- `color4  #61afef` · `color12 #528bff` — blue / bright blue (info, URLs, diff-added accent)
- `color5  #c678dd` · `color13 #a663c4` — magenta (keywords, rare accent)
- `color6  #56b6c2` · `color14 #3ab9c6` — cyan (emphasis, agent identity)
- `color7  #abb2bf` · `color15 #ffffff` — white / bright white (default/strong text)

**Semantic mapping (from `atrium-hud`)**
- Spend < 50% → green (`color2`)
- Spend 50–80% → amber (`color3`)
- Spend ≥ 80% → red (`color1`)
- Burn rate would blow budget in 8h → amber; in 1h → red
- Dim muted metadata (`up 42m`, `last tool 3s`) → ANSI `2` (faint) — render as 40–50% alpha of fg

### Typography

- **Primary and only** — `FiraCode Nerd Font` (monospace, ligatures disabled in Atrium), with `cell_height` 90% for density.
- **Base size** — 10.5pt in the terminal; design artifacts use 13–14px body to stay readable outside the 1600×1000 kitty window.
- **No proportional fonts anywhere.** Not even headings. Visual hierarchy is size + color + space, never face.
- **Nerd Font fallback** — for glyphs unavailable in plain FiraCode (powerline arrows, devicons). See ICONOGRAPHY.

### Spacing

Everything lives on a character cell. The native unit is 1 cell (`ch` in CSS, roughly 7.8px at 13px/mono). Macro spacing rules:

- Kitty window padding — `4 6` (4px vertical, 6px horizontal).
- Zellij pane frames are on; pane border = 1 cell line, `color8` dim.
- HUD pane — exactly 1 line high (`size=1 borderless=true`).
- Status bar — 2 lines.
- Tab bar — 1 line.
- Everything else fills available space.

### Backgrounds, imagery, gradients

- **Flat `#080a10` everywhere.** No gradients, no images, no textures, no blur, no transparency.
- `background_opacity` is `1.0` in kitty config — deliberately opaque.
- No hero images, no illustrations, no photography. Any design artifact should reach for a terminal rendering before reaching for an image.

### Borders, corners, shadows

- **No rounded corners.** Everything is grid-aligned rectangles.
- **No drop shadows.** The only "elevation" is Zellij's pane frame — a 1-cell dim line around active regions.
- Focused pane is indicated by a slightly brighter border (`color7` → `color15`), never by a glow or color accent.

### Hover, press, focus states

- There is no mouse hover in the terminal (though `mouse_mode true` is set in zellij, it's rare).
- Focus is communicated by Zellij pane-border brightness and by the cursor position.
- Kitty cursor: `beam` shape, `2.0` thick, blinking at `0.5s` — "signals active cognition".
- In HTML derivatives: use cursor color (`#61afef` URL blue) for caret; use brighter fg for focused pane; never scale / shadow / glow.

### Animation

- **None by default.** Real terminal output is "print-and-settle". `watch -n 2` refresh on the HUD is the only repeated motion, and it's a clean swap.
- Cursor blink is 0.5s on/off — the only constant motion.
- In design artifacts (e.g. a typing-out-a-log scene), use step-wise character reveal at ~30–80 chars/sec, not smooth slides.
- Never use bounce, ease-out, or spring curves. Linear or stepped only.

### Transparency / blur

- **Forbidden.** The config explicitly sets `background_opacity 1.0`. Atrium is flat and opaque; anything translucent breaks the "this is a real pane" illusion.

### Layout rules

- Fixed header (tab bar, 1 cell) · flexible middle · HUD (1 cell) · status bar (2 cells).
- No overlays, no modals, no toasts. Notifications go to the HUD line or to `state/trace.jsonl`.
- When something is better seen than typed about (diffs, traces), it renders in a pane, not a popup.

### What Atrium deliberately isn't

Avoid, in any design artifact claiming to represent Atrium:

- bluish-purple gradients
- rounded 12/16px cards with colored left-border accents
- hero images of abstract networks / glowing nodes
- emoji anywhere in prose
- proportional fonts (Inter, system-ui, even for body)
- light mode
- drop shadows, blur, glassmorphism

---

## Iconography

See `ICONOGRAPHY.md` for details. Short version: **Atrium's icons are text.** The Nerd Font glyphs bundled into FiraCode Nerd Font provide powerline separators, branch glyphs, and a few file-type icons. Everything else is ASCII or Unicode box-drawing. No SVG icon set. No PNG assets. Logos are text.

---

## Index

Root files:

- `README.md` — this file
- `ICONOGRAPHY.md` — icon approach
- `colors_and_type.css` — CSS variables for both raw and semantic tokens
- `SKILL.md` — agent-skill front-matter for downloading this as a Claude Code skill
- `fonts/` — FiraCode Nerd Font Mono webfont (substitute — see `fonts/README.md`)
- `assets/` — logos, reference captures
- `preview/` — individual design-system preview cards (register each in the Design System tab)
- `ui_kits/` — HTML recreations of Atrium surfaces
  - `cockpit/` — kitty+Zellij agent-v0 layout, HUD, guard block, trace log
  - `brain/` — brain/*.md rendered as a durable-memory doc view

## Caveats

Noted in `README.md` at the end of the creation session; repeat here for reference.
