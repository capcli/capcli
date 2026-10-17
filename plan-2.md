# plan-2.md — Wireframe IDL Ripple Resolutions

**Scope:** the 13 ripples of the plan.md / diff-patches.md conversion, verified against the tree at `58e5cbc`. Each ripple gets a ruling: doc fix, new work, or sequencing constraint. **Status:** design.

**Doc status:**
- plan.md — verified against the tree and fixed (scenario-home ruling, codegen module location, stale trailer replaced). Done.
- diff-patches.md — verified against the tree and fixed (fixture count 320, exemplar `$example` literals, node-text anchors, bare-`template` gate, §11 node labels, §13 header level). Done, with one open question: manifest `version` 3→1 direction.
- plan-2.md — this document (13 ripple rulings + runbook). Design.

**Conversion status:** not started. The tree holds 320 `wireframe/v2` screens, 0 `v1`, 0 `$slot` objects (verified 2026-10-17 ~19:15 WIB). The conversion is pending work; §R14 sequences it and breaks it into items. Nothing in screens/ has been touched.

---

## R1. Conversion scale

Measured on the tree: 2,664 component string leaves, 320 `command`s, 311 `target`s, 74 `audit_op`s, 320 `elapsed_ms` values, 423 array string leaves — **~3,000 slot insertions** across 320 files. diff-patches §2 keeps its three transformations; the runbook (§R14) is sized to this number, not to the "mechanical" framing.

## R2. Volatility law

Volatile fields are always `$slot`, never literal. The structural-match runner asserts byte-exact literals and type-only slots; a volatile literal fails every run.

Volatile on the tree: root `elapsed_ms` (all 320 screens, integer, varies per run); time-like component strings — durations, `next_fire`, `measured`, reset/window times (97 hits). The converter slots every match. Manifest `output_contract.slot` gains `"volatility": "elapsed_ms and time-like strings (durations, timestamps, windows) are always $slot"`.

## R3. Slot / semantic boundary

Closed semantic list (never slotted): `$schema`, `id`, `archetype`, `rule`, `domain`, `layer`, `remedy` (deterministic per §R4), `context.env`, `context.tier`, `context.trust`, `trailer.prompt`, `attention.*.class`, `isolated`, `isolated_reason`.

Everything else slots, including `audit_op`, `attention.*.summary`, `attention.*.affordance.*`, `affordances[].command` (as `$interpolate`), `elapsed_ms` (§R2). Manifest `semantic_positions` and diff-patches §1/§2 carry this list verbatim.

## R4. Remedy determinism

`remedy` stays literal. Law: a remedy is a fixed string per (screen, scenario); the scenario tokens inside it (verb names, versions, URLs — 87 of 142 remedies on the tree) are frozen scenario data. The runner asserts remedies byte-exact. Stated in plan.md §4 "What stays literal".

## R5. Missing target

9 screens carry no `target` (env.doctor ×2, env.list.populated, routine.pending ×2, routine.sweep ×2, rule.plan.planned, sys.help.stub). The converter skips absent `target`. One line in diff-patches §2.

## R6. `$kind: "semantic"` deleted

The design contradicts itself: the binder rejects `"semantic"`, yet it "exists as an author marker." Rejected values cannot appear in files. The concept is removed; non-slotted positions are simply bare, and the `semantic_positions` list (§R3) is the marker. plan.md §4 loses the two sentences; `kind_enum` stays `["instance"]`.

## R7. Binding path grammar

`^(context|scenario|world|live)(\.[a-z_][a-z0-9_]*|\[\d+\])+$` — covers `live.trace.nodes[0].children[0].label`. Declared in manifest `output_contract.slot` as `binding_path_grammar`; enforced by check-trinity.py (diff-patches §11.6) and the v1 validator (§R10).

## R8. Scenario duplication

Per-screen `scenario` blocks repeat journey data across screens. Accepted trade-off, stated plainly: the screen is the standalone unit the runner dispatches, and each block holds only the keys its own slots reference, bounding the duplication. Added as a guardrail Q&A row in plan.md §12.

## R9. `isolated` markers

`isolated` / `isolated_reason` (3 shim fixtures, from the parallel orphan-wiring work) are author markers: in `semantic_positions`, never slotted, carried through the conversion untouched.

## R10. v1 validator

`validate_wireframe_v2.py` is superseded by a v1 validator. String-type assertions become slot-aware: a checked position accepts a string literal or a `$slot` / `$interpolate` object satisfying the slot grammar. Affordance attestation compares affordance `command` against the `$example` of each screen's command slot. Preserved verbatim: the affordance law (rel/risk enums, `requires_intent` ⇔ `risk == "mutating"`, success-only), the trailer law, the archetype structural checks. Newly enforced: the volatility rule (§R2) and the binding path grammar (§R7).

## R11. check-trinity.py

No action beyond diff-patches §11.6. Flagged out of scope: its `doc://prompts/` trailer-scheme check disagrees with the v2 validator's `prompt://` regex — pre-existing, not a v1 ripple.

## R12. §5 lockstep

wireframe-structure.md §5 embeds 14 full fixtures (5.1–5.14). §5 gets the §4 treatment: indexes, never originates; the fixture wins any conflict. The 14 embeds convert in lockstep with screens/ (§R14); diff-patches §4 gains the bullet.

## R13. `domain_fields` derivation

Specified: `domain_fields[domain]` = sorted union of component keys holding a `$slot` / `$interpolate` object, across v1 screens carrying that `domain`, minus the diagnostic core `{domain, rule, layer, culprit, remedy}`. `_states.json` `domain_fields` regenerates once at conversion — the derived set supersedes the hand-maintained list — and regenerates with no diff thereafter. This replaces the unspecified derivation behind plan.md §11 acceptance #7.

## R14. Conversion runbook

1. Land the section6 orphan-wiring first (13 transitions, `isolated` markers) — the converter consumes its output.
2. Ship the v1 validator (§R10).
3. Convert screens/ script-assisted, in items:
   - a. `$schema` → `wireframe/v1` (320 files).
   - b. Add a root `scenario` block per screen holding only the keys its own slots reference (§R8); skip `target` on the 9 target-less screens (§R5).
   - c. Slot instance literals per the rules: volatility (§R2), slot/semantic boundary (§R3), remedy determinism (§R4), no `$kind: "semantic"` (§R6), binding path grammar (§R7), `isolated` markers untouched (§R9).
   - d. Convert the §5 14 embeds in lockstep (§R12).
4. Apply the thirteen-file edit set from diff-patches.md.
5. Regenerate `_states.json` `domain_fields` (§R13); re-run until no diff.
6. Gates, all green: `cans check`, v1 validator, `wireframe-codegen --check`, `cargo test --workspace` (structural match).

---

## Acceptance additions (plan.md §11)

9. v1 validator green on all 320 v1 screens; zero volatile literals; zero `$kind: "semantic"`.
10. `_states.json` `domain_fields` regenerates from v1 screens with no diff (against the §R13 baseline).
11. §5 embeds byte-match their screens post-instantiation (`$example` substitution).
12. Every binding path matches the §R7 grammar.
