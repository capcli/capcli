# Wireframe Prompt-Awareness — Patch Spec (draft)

`cans/artifacts/wireframe/prompt-awareness-spec.md`
Status: draft patch spec. Not implemented. This file specifies the smallest
change that makes the wireframe **declaratively aware** of the prompt layer
without importing any of it. Decision records: `cans/_adr/002-prompt-three-layer.md`,
`cans/_adr/003-wireframe-state-taxonomy.md`.

---

## 0. Non-goals (read first)

- No bank content enters the wireframe. No campaign titles, sections, caps,
  or bank inventory are copied here or into fixtures.
- The screen → prompt mapping stays single-sourced in
  `cans/artifacts/prompt/_triggers.json`. The wireframe never grows a
  second mapping table.
- No new screen IDs, states, domains, CLI nouns, verbs, or flags.
- No change to the progressive-disclosure ladder
  (`cans/artifacts/prompt/prompt-structure.md` §3). This spec covers only
  the L1 surface: what a screen looks like when a prompt is offered.

## 1. The one contract slot

`manifest.json` → `output_contract` gains exactly one block:

```json
"prompt_trailer": {
  "human_field": "prompt: doc://prompt/{bank}/{slug}@{version}",
  "machine_field": "next_prompt",
  "reason": "one line, plain language",
  "caps_tokens": { "default": 30, "via_search": 60 },
  "position": "final line of human output; additive envelope key in --json",
  "serving": "read-only: no audit_op, no state write, exit code and state_modified of the host screen unchanged"
}
```

Rules:

1. The trailer is a **pointer plus a reason**, nothing else. Pointer form is
   frozen: `doc://prompt/{bank}/{slug}@{version}`.
2. Emitted only when the trigger predicate holds for the screen actually
   rendered (screen ID + kernel state, e.g. `domain_tables: 0`,
   `trust: draft`, `caller: harness`). Never emitted from screen ID alone.
3. Banned where the kernel `remedy:` line already fully specifies the next
   command — a remedy-complete denial gets no trailer. A trailer exists only
   when the next action is agent-authored work (synthesis, authoring, judged
   promotion/migration), per the prompt-layer serving rule.
4. Banned at boot (L0 is zero prompt tokens) and banned on any screen the
   trigger table marks blocked. (Currently 12/12 triggers serve; the ban
   stays in the contract for future blocked entries.)
5. Serving never mutates state: no audit row, no claim, no cursor advance.
   The host screen's `[env:tier]` prefix, exit code, and `state_modified`
   are byte-identical with and without the trailer; the trailer is the only
   added line (human) or the only added key (JSON).

## 2. Fixture support

One optional top-level block on a screen fixture pair. Absent = the screen
is not prompt-aware, and that is the default for all 223 screens.

```json
"prompt": {
  "pointer": "doc://prompt/genesis/blank_world@1",
  "reason": "blank world: 0 domain tables",
  "predicate": { "domain_tables": 0 }
}
```

- The JSON fixture carries the block; the `.txt` pair renders the trailer as
  its final line, verbatim: `prompt: <pointer> — <reason>` (or the field
  format frozen in §1), and `test_assertions.stdout_contains` includes that
  exact line.
- `predicate` keys are kernel-state facts already declared by the fixture's
  own `state` block or by the screen's §4 preconditions. A predicate key the
  kernel cannot observe is a spec bug, not a fixture feature.
- Only pointer + reason + predicate may appear. Restating a bank title,
  section list, cap, or body text inside a fixture is a failure (see §3e).

## 3. Runner checks (extends §6.2 of `wireframe-structure.md`)

a. **Closure.** Every fixture `prompt.pointer` resolves to a bank file whose
   frontmatter `trigger.screens` contains this fixture's `screen_id`, and a
   `_triggers.json` entry exists for (screen, predicate) with
   `serve: "L1"`. A trigger marked blocked asserts the opposite: fixture
   must carry no `prompt:` block and output must contain no trailer.
b. **Caps.** Trailer token count ≤30 (≤60 when the screen is the `search`
   surface), counted with the same tokenizer the golden assertions use.
c. **No body leak.** The trailer contains the pointer, the reason, and
   nothing else. The reason must not duplicate any rendered bank section
   text (checked by substring scan against the bank file).
d. **State neutrality.** For every prompt-aware fixture, a twin assertion
   runs the same command with the predicate unsatisfied: exit code and
   `state_modified` identical, output identical except the trailer line/key
   is absent.
e. **No duplication.** Fixture `prompt:` blocks may not contain bank titles,
   section names, or caps; flows must not gain prompt edges (flows stay a
   screen graph). Screen → prompt mapping changes land only in
   `_triggers.json` and bank frontmatter, which are compiled from each
   other — never in the wireframe.
f. **Negative space.** Every fixture without a `prompt:` block asserts
   `stdout_not_contains: ["next_prompt", "doc://prompt/"]`, so awareness can
   never leak into screens that were never declared eligible.

## 4. What changes where (patch order)

1. `manifest.json`: add the §1 block; bump `version` 3 → 4. `output_contract`
   is the only manifest home for output shape — no per-screen flags.
2. `wireframe-structure.md` §6.1: document the optional `prompt:` block;
   §6.2: add checks (a)–(f). §4 rows do not change; eligibility is a fixture
   fact, not an inventory fact.
3. Fixtures: add `prompt:` blocks only to screens named in
   `_triggers.json` (12 triggers at time of writing; the list is read from
   the trigger file at patch time, never copied into this spec).
4. Runner: implement checks (a)–(f) in the fixture test contract; golden
   `.txt` files gain exactly one trailer line where eligible.

## 5. Dependencies and open rulings

- Leaf addressing (L3) is out of scope here, but the trailer points at the
  same `doc://` surface: the `cans/interface.md` ruling on outline-node leaf
  addressing (prompt-structure §7.1) must land before L1 trailers are
  user-visible, or trailers would advertise a ladder whose top rung is
  unaddressable. This spec does not legalise `--section`.
- Token counting must use one tokenizer across wireframe golden tests and
  prompt-bank caps; if they diverge today, that is a separate ADR.
- `doc.inspect` remains an open legality question against
  `cans/interface.md`; nothing in this spec depends on or legitimises it.

---

Cross-references (pointers, not copies): ladder and serving rules —
`cans/artifacts/prompt/prompt-structure.md`; triggers —
`cans/artifacts/prompt/_triggers.json`; exit/state law — `cans/physics.md`,
`cans/artifacts/wireframe/_states.json`.
