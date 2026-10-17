# `plan.md` — Wireframe as Codebase IDL

**Scope:** `cans/artifacts/wireframe/` · **Gates:** `cans check`, `wireframe-codegen --check`, `cargo test --workspace` · **Status:** shipped-state design

---

## 1. Summary

`cans/artifacts/wireframe/screens/` is the typed IDL for capcli's CLI surface. Every screen is a `wireframe/v1` fixture — a `CliEnvelope` shape with typed `$slot` / `$interpolate` holes bound to scenario data. A single generator (`wireframe-codegen`) compiles screens into the clap trees, envelope structs, renderers, and diagnostic enums consumed by both the kernel and every installed plugin. Hand-written code owns behavior; generated code owns surface. The wireframe is not a mirror of the binary — it is the binary's shape.

---

## 2. Invariants (what the wireframe does **not** own)

The wireframe declares *shape*. Everything below stays exactly where it is today:

| Law | Home | Preserved because |
|---|---|---|
| Exit code `0,2,3,4,5,6` | `kernel.md#Exit-code-law` | Derived from the screen id's state segment; never stored |
| `state_modified: false` on non-zero exits | same | Computed at assertion time, never authored |
| Archetype set `diagnostic, tree, receipt, document` | `kernel.md#Diagnostic-output-law` | Closed; plugins extend only via sandboxed `custom` |
| Domain taxonomy `policy.*, api.*, db.*, …` | `effect.md#Denials`, mirrored by `_states.json` | Plugins reuse domains; new domains only via kernel PR |
| Banned-token list, divider `─`, tree glyphs, caret `^` | `manifest.json#output_contract` | Renderer output, never screen data |
| Trailer mapping | `artifacts/prompt/_triggers.json` | Unchanged |
| Attribution, `audit_op`, `attention` | `kernel.md#Diagnostic-output-law` | Envelope law, not fixture law |

---

## 3. Vocabulary — **screen**, not template

`template` is already overloaded three ways: `artifacts/templates/*.yaml` (config-file archetype), `pack scaffold` (blueprint hydration), and would-be "output shape." Adding a fourth sense violates `_rules.yaml#vocabulary`.

| Rejected | Chosen | Why |
|---|---|---|
| template | **screen** | Already the directory name and the rendered unit. Zero collision. |
| `$template` (interpolation key) | **`$interpolate`** | Removes the last `template` token from the DSL |
| plugin `returns:` | plugin **`screens:`** | Same axis: one screen per state |
| `_scenarios/`, `_bindings.schema.json` | folded into existing files | No new files where an existing file owns the concept |

**Guardrail** (`_rules.yaml`): `vocabulary.required_qualifiers` gains `template: [manifest template, pack template, code template]`. `cans check` fails on bare `template` in `cans/**` prose, and on any key or value under `wireframe/screens/**` containing `template`.

The DSL is exactly two keys: `$slot` and `$interpolate`. Nothing else.

---

## 4. `wireframe/v1` — the screen shape

A screen keeps the existing `CliEnvelope` root (§6.1 of `wireframe-structure.md`) and uses two slot forms wherever instance data appears:

**Whole-value slot** — for any JSON scalar position:

```json
{ "$slot": "frame_id", "$kind": "instance",
  "$type": "string", "$pattern": "^frame_[0-9a-f]+$",
  "$from": "live.frame_id", "$example": "frame_018" }
```

**String interpolation** — for placeholder data embedded in prose:

```json
{ "$interpolate": "routine {{routine_name}}@{{routine_version}} ({{frame_id}})",
  "$bindings": { "routine_name": "scenario.routine_name",
                 "routine_version": "scenario.routine_version",
                 "frame_id": "live.frame_id" },
  "$example": "routine broadcast_newsletter@2 (frame_018)" }
```

Rules:
- `$kind` is `"instance"` or absent. `"semantic"` is rejected by the binder; it exists as an author marker so reviewers can see an intentional non-slot.
- `$example` is required — it is the byte-golden used by strict-instantiation mode (§6).
- `$bindings` values are binding paths (see §5), never literals. Literals need no wrapper.
- `$schema: "wireframe/v1"` everywhere. No other version is valid.

**What stays literal (never a slot):** `archetype`, `rule`, `domain`, `layer`, id state segment, banned tokens, divider/glyph/caret runs, `remedy`, `culprit`, `$schema`, trailer `prompt`, attention `class` enum. The binder refuses `$slot` for these positions.

---

## 5. Binding sources

Four prefixes, declared once, no new file:

| Prefix | Source | Where declared |
|---|---|---|
| `context.*` | the screen's own `context` block (`env`, `tier`, `trust`, `data_shape`) | per-screen (already exists) |
| `scenario.*` | the journey's data — one journey is one scenario | `_flows.json#journeys[*].scenario` |
| `world.*` | the seeded workspace state for that journey | `_flows.json#journeys[*].world` |
| `live.*` | extracted from the actual envelope at assertion time | `wireframe-structure.md#Binding-Sources` |

`_flows.json` gains two optional blocks per journey (`scenario`, `world`). Journeys already declare `entry`/`terminal` and carry command strings in transitions; adding scenario data here is the minimal non-redundant extension. No `_scenarios/` directory.

---

## 6. Renderer contract (two consumers, one law)

### 6.1 `wireframe.html`

Renders `wireframe/v1` screens by substituting `$example` in authoring mode. When a slot is present, the canvas shows the slot name and type on hover; the terminal panel previews `$example`. Zoom/pan/node-click/search behaviour is unchanged.

### 6.2 `test_wireframe_fixtures.rs`

One mode — **structural match**:

1. Dispatch the fixture's `command` against the real binary.
2. Extract `live.*` bindings from the actual envelope.
3. Assert every literal matches byte-exact; every `$slot`/`$interpolate` satisfies its `$type`/`$pattern`/`$enum`; the substituted string equals the actual field.
4. Assert exit code derives correctly from the id state segment; `state_modified: false` on non-zero exits.
5. Assert banned tokens absent, no pipe character, trailer present iff `_triggers.json` says so, no `next_action` on fixtures with no trailer.

Strict instantiation (substitute `$example`, byte-compare against the historical golden) is a `cargo xtask wireframe-strict` developer tool, not the CI mode. CI is structural match only.

---

## 7. Codegen — screens → Rust

`wireframe-codegen` is a single binary at `crates/capcli-cli/src/bin/wireframe-codegen.rs`. Deterministic (sorted iteration, no timestamps). It reads every `wireframe/v1` screen — kernel and plugin — and emits:

```
crates/capcli-types/src/generated/
  envelope.rs        CliEnvelope<T> per archetype (union of components)
  bindings.rs        <Screen>Bindings per screen family, fields typed from $slot
  diagnostics.rs     DiagnosticRule enum from the union of `rule` literals
  domains.rs         Domain enum, cross-checked against _states.json

crates/capcli-cli/src/generated/
  nouns/<noun>.rs    clap subcommand tree per noun/verb/target/flag
  renderers/<…>.rs   fn render(&<Screen>Bindings) -> Component
  tests/             generated structural-match #[test_case] entries
```

Hand-written modules own behavior (authorizer, quota bookkeeping, DAG append, claims). Generated modules own surface (clap, envelope construction, rendering, diagnostic enum). The seam is `<Screen>Bindings` — hand-written handlers populate it; generated renderers format it.

`wireframe codegen --check` diffs generated output against the checked-in modules and fails the PR on drift. `cargo build` fails if the binary's surface drifts from a `v1` screen.

---

## 8. Plugin contract

**What the plugin creator writes** — one `screens:` map per verb:

```ts
defineVerb({
  name: "charge",
  screens: {
    success: Receipt<{ charge_id: string, amount_cents: integer, status: "captured" | "pending" }>,
    denial:  Diagnostic<{ domain: "api.quota", rule: "api.quota.exhausted" }>,
    yield:   Diagnostic<{ domain: "api.quota", suspended_frame: string }>,
  },
  async run(params) { /* … */ },
});
```

**What `capcli plugin build` emits** (author never touches):

- `screens/<noun>.<verb>.<state>.<condition>.v1.json` in the plugin package
- `capcli-plugin.yaml#cli.surface[].screens[]` entries pointing at those files
- The plugin's contribution to `wireframe codegen` output

**What `capcli plugin install` does:** runs `wireframe codegen --plugin <id>` against the plugin's screens, mounts the resulting clap subcommands into the noun tree, registers renderers keyed by `(noun, verb, state)`, atomic-flips the generation pointer. Kernel install stays fast — codegen for a plugin runs at *plugin build* time, not kernel install.

**Reciprocal obligation:** every key in `defineVerb.screens` must yield a resolvable screen at build time and install time. `plugin verify` and `plugin install` refuse otherwise.

**Escape hatch:** `screens: { success: Custom({ renderer: "./renderers/logs.ts" }) }` → the plugin's renderer runs in a Tri-Jail sandbox at invocation; the kernel validates its output against `CliEnvelope<T>` before wrapping. Opt-in, sandboxed, `cans check`-ed.

**Pack vs screen boundary:**

| | pack | screen |
|---|---|---|
| Kind | shipping unit (`.cap`) | rendering unit (one CLI output) |
| URP | `pack://*` | none (`<noun>.<verb>.<state>.<condition>`) |
| Lifecycle | `new → bundle → import → scaffold` | authored → bound → rendered |
| Contains the other? | yes — a pack may ship `screens/` | no — a screen is never a pack |

---

## 9. Canonical homes

`_rules.yaml#canonical_homes` — additions and narrowings:

| Key | Home | Notes |
|---|---|---|
| `output_shape` | `wireframe-structure.md#Screen-Shape` | The `wireframe/v1` grammar; unchanged file, new section |
| `output_shape_instances` | `wireframe/screens/` | The data |
| `scenario_binding` | `wireframe/_flows.json#journeys` | Scenario + world data per journey |
| `surface_generation` | `assembly.md#CICD-pipeline` | The codegen mechanism |
| `surface_conformance` | `interface.md#Surface-conformance` | Re-framed: consumes shape; no longer owns it |
| `wireframe_contract` | `kernel.md#Diagnostic-output-law` | Narrowed: laws only, not layout |

Pointer topology (`AGENTS.md`): wireframe moves leaf → **branch**. `_rules.yaml` gains a `shape_exception:` entry so root anchors may cite the wireframe for shape without review flagging it.

---

## 10. File inventory — the shipped state

**Modified, no new files:**

- `wireframe/manifest.json` — `$schema` is `wireframe/v1`; `output_contract.slot` block describes the DSL
- `wireframe/_states.json` — structurally unchanged; a `cans check` assertion derives `domain_fields` from `live.*` slots in v1 screens
- `wireframe/_flows.json` — journeys gain `scenario` and `world` blocks
- `wireframe/screens/**/*.json` — every fixture is `wireframe/v1`
- `wireframe/wireframe.html` — renders `v1`; slot hover + `$example` preview
- `wireframe/wireframe-structure.md` — new sections `## Screen Shape (v1)`, `## Binding Sources`, `## Plugin Screens`
- `_rules.yaml` — `canonical_homes` (§9), `vocabulary.required_qualifiers.template`, `shape_exception`
- `interface.md#Surface-conformance` — re-framed as consumer
- `kernel.md#Diagnostic-output-law` — narrowed to law only
- `plugins.md#Manifest`, `#Capabilities` — `screens:` replaces `returns:`
- `plugins.md#CLI-projection` — install-time codegen pipeline
- `marketplace.md#Intake` — screen-resolution check
- `assembly.md#CICD-pipeline` — `wireframe-codegen --check` PR job
- `crates/capcli-cli/tests/e2e/test_wireframe_fixtures.rs` — structural match only
- `packages/ts/src/define-verb.ts`, `packages/py/capcli/__init__.py` — `screens:` param

**New, single-purpose:**

- `crates/capcli-cli/src/bin/wireframe-codegen.rs` — the generator
- `crates/capcli-types/src/generated/**` — generated (checked in, `--check`-gated)
- `crates/capcli-cli/src/generated/**` — generated (checked in, `--check`-gated)

No `_scenarios/`, no `_bindings.schema.json`, no `*.v2.json` twins, no `phases/`, no migration directory.

---

## 11. Acceptance criteria (shipped-state assertions)

1. `cans check` is green; no bare `template` in `cans/**` prose; no `template` substring under `wireframe/screens/**`.
2. Every fixture is `$schema: "wireframe/v1"`.
3. `cargo test --workspace` runs the structural-match runner and passes; a PR that drifts the binary's surface from any v1 screen fails at `cargo test`.
4. `wireframe-codegen --check` is green; a hand-edit to any generated module fails the PR.
5. `cargo build` fails if the binary's surface drifts from a v1 screen.
6. `capcli plugin build` on `capcli.plugin.stripe@1.4.0` emits ≥1 v1 screen per `screens[*]` key, and `capcli plugin install` mounts `stripe charge` end-to-end with the generated renderer.
7. `_states.json` `domain_fields` regenerates from v1 screens with no diff.
8. `wireframe.html` renders every v1 screen with `$example` substitution and slot hover.

---

## 12. Guardrails

| Reviewer question | Answer |
|---|---|
| Isn't this over-parameterizing? | `$kind: "instance"` only. Banned-token strings are semantic literals by assertion. `$kind: "semantic"` is a review marker, not a slot. |
| Do we lose byte-goldens? | `$example` + `cargo xtask wireframe-strict` is the byte-golden path; it stays a developer tool, not a CI mode. |
| Does codegen bloat kernel install? | No — a plugin's screens are codegenned at *plugin build* time. Kernel install loads compiled artifacts from the `.cap` bundle. |
| Does the wireframe own behavior? | No. `kernel.md` owns exit codes; `effect.md` owns domains; wireframe owns shape. |
| Can a plugin invent a domain or archetype? | No. `defineVerb`'s `domain` type is restricted to the union from `effect.md#Denials`. New archetypes go through kernel PR. `custom` is the only extension, and it's sandboxed. |
| What breaks on `pack`? | Nothing. `pack scaffold`, `pack bundle`, `pack import` are untouched. A pack may contain screens; a screen is never a pack. |
| Do we need `_scenarios/` or `_bindings.schema.json`? | No. Scenario + world data live inside `_flows.json` journeys. Binding sources are declared once in `wireframe-structure.md`. |

---

**Ready to produce `diff-patches.md`.**
