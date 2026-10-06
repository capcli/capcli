# Prompt Banks — Agent-Facing Progressive Disclosure

`cans/artifacts/prompt/prompt-structure.md`
Status: v2, three-layer rewrite. Supersedes the v1 all-in-one draft on `post-mortem`.

This file defines **only the agent-facing prompt layer**: what a prompt is,
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
2. **Completeness is deferred to `docs/`.** Every campaign slice ends with a
   `docs:` pointer to the user-facing page that explains the full topic.
   Slices never summarise `cans/` and never copy reference tables.
3. **A prompt is served only when the next action is agent-authored work**
   (synthesis, authoring, judged migration/promotion). A single denial whose
   kernel `remedy:` line fully specifies the next command gets no prompt.

## 2. Remedy vs campaign (the boundary v1 blurred)

- **Remedy** — closes one failed command. Kernel-emitted, in-band, ephemeral.
  The full remedy catalogue is user-facing reference and belongs in
  `docs/reference/errors.md` (candidate extraction lives there now; it must
  be verified against its `cans/` owners before it is treated as published).
  This file and the banks contain **no remedy matrix**.
- **Campaign (prompt)** — opens multi-stage agent work. Durable, versioned,
  served in slices under the ladder in §3. Campaign bodies live only in
  `banks/`, one campaign per file; this file carries structure, not bodies.

## 3. Progressive disclosure ladder (reconciled to SSOT)

| Level | Surface (frozen in `cans/interface.md`) | Cap | Content |
|---|---|---|---|
| L0 | boot | 0 prompt tokens | nothing; no bank, catalog, or manifest is mounted |
| L1 | trigger screen trailer / `next_prompt` (JSON) | ≤30 tokens (≤60 via `search`, per `cans/action.md`) | pointer `doc://prompt/{bank}/{slug}@{version}` + one-line reason |
| L2 | `capcli inspect doc://prompt/{bank}/{slug}@{version}` | ≤150 tokens | envelope only: vars, section index, caps, blocked status; no body |
| L3 | `capcli doc outline` → `capcli doc read <ptr> --max-tokens <n>` | 1 leaf/turn, leaf ≤500 tokens | exactly one rendered section, kernel-substituted vars |

Reconciliation notes (v1 contradictions, resolved — not hidden):

- `cans/interface.md` gives `doc read` a `--max-tokens 100` default for
  ordinary docs. The global result ceiling is 500 tokens (`cans/action.md`,
  routine output envelope; wireframe pagination). Prompt leaves may
  therefore request up to 500 explicitly; 100 remains the ordinary default.
- **No `--section` flag exists in v1.** v1 invented one. Leaf selection rides
  the existing `doc outline` node ids (inspect on `doc://` returns outline
  nodes; `doc read` fetches a targeted leaf, per `cans/action.md`). If the
  kernel cannot address a leaf by outline node without a new flag, that is a
  `cans/interface.md` amendment + ADR — open, listed in §7, not faked here.
- No L1→L3 shortcut. Levels are not skipped; the ladder is the contract.
- Serving never mutates state (`state_modified: false`), per exit-code law
  in `cans/physics.md`.

## 4. File and frontmatter law

- One campaign = one `.md` file under `banks/{bank}/`. No `.json`/`.txt`
  companions in `banks/`. Depth is exactly 2 below `banks/`.
- Filename: `{bank}.{slug}.{state}.{condition}.md`. `state` must be a legal
  wireframe state token; campaigns whose trigger screen is itself illegal
  are marked blocked (§6) rather than renamed in secret.
- Every file starts with YAML frontmatter: `id` (`doc://prompt/...`), `stem`,
  `bank`, `slug`, `version`, `trust`, `trigger.screens`,
  `trigger.predicate`, `vars` (kernel sources only), `sections`
  (per-section token caps, each ≤500, honest — cap ≥ rendered size),
  `slice_max_tokens: 500`, and `docs:` (the `docs/` page for completeness).
- Variables resolve only from kernel state. Unresolvable variable → refusal
  (exit 3). The kernel never guesses state facts.
- `manifest.json` and `_triggers.json` in this directory are the compiled
  indexes of the banks. They are generated from bank frontmatter, never
  hand-edited to disagree with it.

## 5. Triggers

Defined in `_triggers.json` (12 entries). Precedence: most specific
predicate wins — screen, then predicate keys, then bank order as declared
in `manifest.json`. Two campaigns may share a screen only if their
predicates are disjoint (see genesis/authoring/promotion on
`routine.prove.success.passed`: disjoint on `overview_exists` / `trust`).

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
| wire `wire.catalog.empty` | `api.catalog.success.empty` | `docs/use/` (API catalog page: docs debt) | served |
| forensics `forensics.audit.tampered` | `sys.doctor.success.tamper` | `docs/understand/` (audit page: docs debt) | served — unblocked by ADR-003 rename (`warning` demoted to condition slot) |
| hitl `hitl.ping_ask.suspended` | `run.execute.yield.ask` | `docs/use/` (ask page: docs debt) | served — unblocked by ADR-003 rename (ask suspension is exit-6 `yield` per `cans/action.md`) |

Blocked means: files exist for review, `_triggers.json` carries
`"serve": "blocked"`, and no L1 trailer is emitted until the trigger screen
is a legal screen ID in the wireframe. (No bank is currently blocked.)

Campaign bodies were corrected to SSOT while extracting them from v1:
no `sys verify` (trust receipt is `sys doctor --report`), no
`sys vault_import` (`sys vault import-env`), no `routine new --runtime`,
no `--section`, no harness-history scraping in genesis stage 1 (mission
intent comes from governed discovery: `sys doctor`, `db schema`, `search`),
promotion gates restated from `cans/trust.md` (≥0.95 success, invariant
suite, zero denials/drift, 1-hour canary), evolution lists all four phases
(Expand, Backfill, Contract, Pin).

## 7. Open blockers (TBD — owned, not papered over)

1. Leaf addressing without `--section`: needs `cans/interface.md` ruling.
2. `docs/` completeness is partial in this repo (e.g. `docs/reference/`
   has only authorizer/limits/errors). Every `docs:` pointer above is a
   target; missing pages are docs debt, not licence to inline the content
   here.
3. Remedy catalogue extraction in `docs/reference/errors.md` is unverified
   against `cans/` owners; its screen IDs were renamed with the wireframe
   (ADR-003) but rows are not yet verified per-row.

Resolved since v3: illegal screen states `warning` / `suspended` / `alarm` /
`rollback` — renamed, not legalised; state vocabulary stays the six exit
labels. Record: `cans/_adr/003-wireframe-state-taxonomy.md`. Forensics and
hitl now serve.

## 8. What moved out of v1, and where it went

| v1 content | Layer it actually belongs to | New home |
|---|---|---|
| 48-condition remedy matrix | completeness (user reference) | `docs/reference/errors.md` (candidate) |
| Rust prompt-engine code | truth (build) | `cans/assembly.md` ownership; no code in this file |
| Thresholds (promotion, budgets, shapes) | truth | cited from `cans/trust.md`, `cans/budget.md`, `cans/artifacts/governance.yaml` — never restated |
| Full schema / routine examples | completeness | `docs/` pages via `docs:` pointers; banks keep only the action-sized fragment per stage |

Decision records: `cans/_adr/002-prompt-three-layer.md` (three-layer split),
`cans/_adr/003-wireframe-state-taxonomy.md` (screen renames that unblocked
forensics + hitl).
