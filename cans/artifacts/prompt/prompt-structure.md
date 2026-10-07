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
   a `docs:` pointer to the user-facing page that explains the full topic.
   Slices never summarise `cans/` and never copy reference tables.
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
| L1 | trigger screen trailer / `next_prompt` (JSON) | ≤30 tokens (≤60 via `search`, per `cans/action.md`) | pointer `doc://prompt/{bank}/{slug}@{version}` + one-line reason |
| L2 | `capcli inspect doc://prompt/{bank}/{slug}@{version}` | ≤150 tokens | envelope only: vars, section index, caps, blocked status; no body |
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
  legal screen ID is marked blocked (§6).
- Every command in a campaign body is legal `cans/interface.md` surface.
- Every file starts with YAML frontmatter: `id` (`doc://prompt/...`),
  `stem`, `bank`, `slug`, `version`, `trust`, `trigger.screens`,
  `trigger.predicate`, `vars` (kernel sources only), `sections`
  (per-section token caps, each ≤500; a cap covers its rendered size),
  `slice_max_tokens: 500`, and `docs:` (the `docs/` page for completeness).
- Variables resolve only from kernel state. Unresolvable variable →
  refusal (exit 3). The kernel never guesses state facts.
- `manifest.json` and `_triggers.json` in this directory are the compiled
  indexes of the banks, generated from bank frontmatter — never
  hand-edited to disagree with it.

## 5. Triggers

Defined in `_triggers.json` (12 entries). Precedence: most specific
predicate wins — screen, then predicate keys, then bank order as declared
in `manifest.json`. Two campaigns may share a screen only if their
predicates are disjoint (genesis/authoring/promotion share
`routine.prove.success.passed`, disjoint on `overview_exists` / `trust`).

## 6. Bank inventory (9 banks, 11 campaigns)

| Bank / stem | Trigger | Docs (completeness) | Status |
|---|---|---|---|
| genesis `genesis.blank_world.empty` | `db.schema.success.empty`, `run.search.success.empty` | `docs/start/`, `docs/understand/world.md` | served |
| onboarding `onboarding.harness.empty` | `sys.doctor.success.nominal` (harness) | `docs/agents/` | served |
| onboarding `onboarding.human.stub` | `sys.help.success.stub` (human) | `docs/start/` | served |
| authoring `authoring.overview.absent` | `routine.prove.success.passed`, no overview | `docs/agents/codification.md` | served |
| authoring `authoring.routine.gaps` | `run.search.success.gaps` | `docs/automate/repetition.md` | served |
| crucible `crucible.execution.starved` | `run.execute.denial.budget_cascade` | `docs/reference/limits.md` | served |
| evolution `evolution.schema.drift` | `rule.diff.success.populated` | `docs/guides/migration.md` | served |
| promotion `promotion.routine.passed` | `routine.prove.success.passed`, draft | `docs/automate/promotion.md` | served |
| wire `wire.catalog.empty` | `api.catalog.success.empty` | `docs/use/` (API catalog page: open) | served |
| forensics `forensics.audit.tampered` | `sys.doctor.success.tamper` | `docs/understand/` (audit page: open) | served |
| hitl `hitl.ping_ask.suspended` | `run.execute.yield.ask` | `docs/use/` (ask page: open) | served |

All 11 campaigns serve. A blocked campaign would carry
`"serve": "blocked"` in `_triggers.json` and emit no L1 trailer; none
currently does.

## 7. Open items

1. Leaf addressing via `doc outline` node ids needs a `cans/interface.md`
   ruling (§3).
2. `docs/` completeness is partial: several `docs:` targets above are open
   pages. A missing page is docs debt, never licence to inline the content
   into a bank.
3. Two remedy seams await `cans/` owner rulings (the `api sync` verb; the
   exit-5 scope for secret leaks) — tracked in `cans/_collab/conflicts.md`.
4. One tokenizer counts tokens for prompt-bank caps and wireframe trailer
   caps alike; unifying the two counts is an open ADR item.

## 8. Where each kind of content lives

| Content | Home |
|---|---|
| Remedy catalogue | `docs/reference/errors.md` |
| Prompt-serving engine | `cans/assembly.md` ownership; no code in this file |
| Thresholds (promotion, budgets, shapes) | `cans/trust.md`, `cans/budget.md`, `cans/artifacts/governance.yaml` — cited, never restated |
| Full schema / routine teaching | `docs/` via `docs:` pointers; banks keep one action-sized fragment per stage |

Decision records: `cans/_adr/002-prompt-three-layer.md`,
`cans/_adr/003-wireframe-state-taxonomy.md`.
