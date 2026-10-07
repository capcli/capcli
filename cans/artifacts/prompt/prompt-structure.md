# Prompt Banks — Agent-Facing Progressive Disclosure

`cans/artifacts/prompt/prompt-structure.md`

This file defines only the agent-facing prompt layer: what a prompt is,
when it is served, how it is sliced, and where completeness lives.
It is not a spec of capcli, and it is not user documentation.

---

## 1. Three layers, three audiences

| Layer | Home | Audience | Job | Never does |
|---|---|---|---|---|
| Truth (SSOT) | `cans/*.md` (13 canonical files, `cans/AGENTS.md`) | kernel / spec builders | legality: nouns, verbs, flags, exits, gates, thresholds | get injected wholesale into an agent context |
| Completeness | `docs/` | humans | explain everything, end to end, in reading order | redefine a command, state, or threshold |
| Action | `cans/artifacts/prompt/banks/` | agents, mid-task | one triggered slice: state → next action → bound → exit condition | restate the spec, teach the whole system, duplicate reference tables |

Rules that follow from the table:

1. **Legality is checked against `cans/` at author/compile time, never at
   serve time.** A prompt file cannot legalise a noun, verb, flag, screen,
   exit code, or threshold. If serving a prompt would need one that `cans/`
   does not define, the prompt is blocked and the change goes through the
   canonical home plus an ADR (`cans/_adr/`) first.
2. **Completeness is deferred to `docs/`.** Every campaign slice ends with
   a `doc://` pointer (bank `docs:` frontmatter) to the user-facing page
   that explains the full topic. `prompt://` addresses agent campaign
   banks; `doc://` addresses human docs; the two schemes never substitute
   for each other. Slices never summarise `cans/` and never copy
   reference tables.
3. **A prompt is served only when the next action is agent-authored work**
   (synthesis, authoring, judged migration/promotion). A single denial
   whose kernel `remedy:` line fully specifies the next command gets no
   prompt.

## 2. Remedy vs campaign

- **Remedy** — closes one failed command. Kernel-emitted, in-band,
  ephemeral. The remedy catalogue is user-facing reference:
  `docs/reference/errors.md`. This file and the banks contain no remedy
  matrix.
- **Campaign (prompt)** — opens multi-stage agent work. Durable, versioned,
  served in slices under the ladder in §3. Campaign bodies live only in
  `banks/`, one campaign per file; this file carries structure, not bodies.

## 3. Progressive disclosure ladder

| Level | Surface (frozen in `cans/interface.md`) | Cap | Content |
|---|---|---|---|
| L0 | boot | 0 prompt tokens | nothing; no bank, catalog, or manifest is mounted |
| L1 | trigger screen trailer / `next_action` (JSON) | ≤30 tokens (≤60 via `search`, per `cans/action.md`) | pointer `prompt://{bank}/{slug}@{version}` + one-line reason, inside the wireframe's generic trailer slot (`wireframe-structure.md` §6.1.1) |
| L2 | `capcli inspect prompt://{bank}/{slug}@{version}` | ≤150 tokens | envelope only: vars, section index, caps, blocked status; no body |
| L3 | `capcli doc outline` → `capcli doc read <ptr> --max-tokens <n>` | 1 leaf/turn, leaf ≤500 tokens | exactly one rendered section, kernel-substituted vars |

Caps, stated once:

- Ordinary `doc read` defaults to `--max-tokens 100`
  (`cans/interface.md`); the global result ceiling is 500 tokens
  (`cans/action.md`). Prompt leaves request up to 500 explicitly.
- Leaf selection rides `doc outline` node ids; there is no `--section`
  flag. Open ruling: whether the kernel can address a leaf by outline
  node without a new flag — a `cans/interface.md` amendment + ADR if not
  (§7).
- No L1→L3 shortcut. Levels are not skipped; the ladder is the contract.
- Serving never mutates state (`state_modified: false`), per exit-code law
  in `cans/physics.md`.

## 4. File and frontmatter law

- One campaign = one `.md` file under `banks/{bank}/`. No `.json`/`.txt`
  companions in `banks/`. Depth is exactly 2 below `banks/`.
- Filename: `{bank}.{slug}.{state}.{condition}.md`, where `state` is a
  legal wireframe state token. A campaign whose trigger screen is not a
  legal screen ID carries `"serve": "blocked"` in `_triggers.json` (§5).
- Every command in a campaign body is legal `cans/interface.md` surface.
- Every file starts with YAML frontmatter: `id`
  (`prompt://{bank}/{slug}@{version}`), `stem`, `bank`, `slug`, `version`,
  `trust`, `vars` (kernel sources only), `sections` (per-section token
  caps, each ≤500; a cap covers its rendered size),
  `slice_max_tokens: 500`, `docs:` (`doc://` pointers to the human-facing
  pages for completeness; bare repo paths are illegal here), and `status`.
  Frontmatter carries no trigger facts.
- Variables resolve only from kernel state. Unresolvable variable →
  refusal (exit 3). The kernel never guesses state facts.
- `manifest.json` in this directory is the compiled campaign inventory
  (bank, stem, file, status), generated from bank frontmatter.
  `_triggers.json` is the sole trigger registry (§5).

## 5. Triggers

`_triggers.json` is the only trigger registry: screen, predicate,
pointer, serve level, reason. Bank frontmatter, `manifest.json`, and
every wireframe file carry no trigger facts. Precedence: most specific
predicate wins — screen, then predicate keys, then bank order as
declared in `manifest.json`. Two campaigns share a screen only when
their predicates are disjoint. A trigger with `"serve": "blocked"`
emits no L1 trailer.

## 6. Bank inventory

The inventory lives in `manifest.json` (bank, stem, file, status),
compiled from bank frontmatter. Triggers live in `_triggers.json`.
Completeness pointers live in each bank's `docs:` frontmatter. No
inventory table exists in this file: a hand-maintained copy of the
registry is a second inventory, and the two desync. Counts come from
`manifest.json` at read time.

## 7. Open items

1. Leaf addressing via `doc outline` node ids needs a `cans/interface.md`
   ruling (§3).
2. `docs/` completeness is partial: several `doc://` targets in bank
   `docs:` frontmatter are open pages. A missing page is docs debt,
   never licence to inline the content into a bank.
3. Two remedy seams await `cans/` owner rulings (the `api sync` verb; the
   exit-5 scope for secret leaks) — tracked in `cans/_collab/conflicts.md`.

## 8. Where each kind of content lives

| Content | Home |
|---|---|
| Remedy catalogue | `docs/reference/errors.md` |
| Prompt-serving engine | `cans/assembly.md` ownership; no code in this file |
| Thresholds (promotion, budgets, shapes) | `cans/trust.md`, `cans/budget.md`, `cans/artifacts/governance.yaml` — cited, never restated |
| Full schema / routine teaching | `docs/` via `doc://` pointers in bank `docs:` frontmatter; banks keep one action-sized fragment per stage |
| Trigger registry | `cans/artifacts/prompt/_triggers.json` — the only home |
| Campaign inventory | `cans/artifacts/prompt/manifest.json` |
| Wireframe trailer slot | `cans/artifacts/wireframe/wireframe-structure.md` §6.1.1 — generic `trailer` / `next_action`, content opaque to the wireframe |

Decision records: `cans/_adr/002-prompt-three-layer.md` (pointer
split and trigger SSOT in its 2026-10-07 amendment),
`cans/_adr/003-wireframe-state-taxonomy.md`.
