# `diff-patches.md` — Wireframe as IDL

No new files, no new crates. Codegen is a module inside the existing `capcli-cli` crate, spec'd in `assembly.md`. Every fixture is `wireframe/v1`. `template` becomes `screen`. Thirteen files edited.

---

## 1. `cans/artifacts/wireframe/manifest.json`

```diff
-  "version": 3,
+  "version": 1,
   "policy_version": 5,
   "governance_version": 8,
   "schema_version": 2,
-  "fixture_schema": "wireframe/v2",
+  "fixture_schema": "wireframe/v1",
```

```diff
   "output_contract": {
+    "slot": {
+      "schema": "wireframe/v1",
+      "keys": ["$slot", "$interpolate"],
+      "slot_requires": ["$from", "$example"],
+      "slot_optional": ["$kind", "$type", "$pattern", "$enum"],
+      "interpolate_requires": ["$bindings", "$example"],
+      "kind_enum": ["instance"],
+      "binding_prefixes": ["context", "scenario", "world", "live"],
+      "semantic_positions": [
+        "id", "$schema", "archetype", "rule", "domain", "layer",
+        "remedy", "context.env", "context.tier", "context.trust",
+        "trailer.prompt", "attention.top[].class"
+      ],
+      "banned_substring_in_screens": ["template"]
+    },
     "pointer_schemes": ["cap://", "ask://", "audit://", "quota://", "vault://", "pack://", "policy://", "ws://", "db://", "doc://", "plugin://"],
```

No other keys change.

---

## 2. `cans/artifacts/wireframe/screens/**/*.json` (all 260 fixtures)

Three mechanical transformations, one rule:

1. `"$schema": "wireframe/v2"` → `"wireframe/v1"`.
2. Add a root `scenario` block — the per-screen data referenced by `$from: "scenario.*"`. Only what the screen needs.
3. Every instance-data literal → `$slot` or `$interpolate`, with the current literal as `$example`.

Semantic literals (never a slot): `id`, `archetype`, `rule`, `domain`, `layer`, `remedy`, `context.{env,tier,trust}`, banned tokens.

### 2.1 `screens/run/execute/run.execute.yield.quota.json`

```diff
 {
-  "$schema": "wireframe/v2",
+  "$schema": "wireframe/v1",
   "id": "run.execute.yield.quota",
-  "target": "cap://broadcast_newsletter@2",
-  "command": "capcli run cap://broadcast_newsletter@2 -p audience=followers -m \"daily digest broadcast\"",
+  "scenario": {
+    "routine_urp": "cap://broadcast_newsletter@2",
+    "routine_name": "broadcast_newsletter",
+    "routine_version": 2,
+    "audience": "followers",
+    "intent": "daily digest broadcast"
+  },
+  "target":  { "$slot": "routine_urp", "$from": "scenario.routine_urp", "$example": "cap://broadcast_newsletter@2" },
+  "command": { "$interpolate": "capcli run {{routine_urp}} -p audience={{audience}} -m \"{{intent}}\"",
+               "$bindings": { "routine_urp": "scenario.routine_urp", "audience": "scenario.audience", "intent": "scenario.intent" },
+               "$example": "capcli run cap://broadcast_newsletter@2 -p audience=followers -m \"daily digest broadcast\"" },
   "context": { "env": "prod", "tier": "tier_1", "trust": "pinned" },
   "archetype": "diagnostic",
   "component": {
     "rule": "policy.api.quota_exhausted",
     "domain": "api.quota",
-    "culprit": "Provider quota exhausted: threads has 0/50 tokens left in the 24h window.",
+    "layer": "quota",
+    "culprit": { "$slot": "culprit", "$from": "live.culprit",
+                 "$example": "Provider quota exhausted: threads has 0/50 tokens left in the 24h window." },
     "remedy": "task safely yielded; daemon will auto-resume at reset_at",
-    "tokens_left": "0 / 50 (24h window)",
-    "reset_at": "18:00:00 UTC (in 4h 12m)",
-    "suspended_frame": "task_99a8b1",
-    "provider": "threads",
-    "verb": "threads.create_media_post",
-    "layer": "quota",
-    "lines": ["routine broadcast_newsletter@2 (frame_018)"]
+    "tokens_left":     { "$slot": "tokens_left",     "$from": "live.tokens_left",     "$example": "0 / 50 (24h window)" },
+    "reset_at":        { "$slot": "reset_at",        "$from": "live.reset_at",        "$example": "18:00:00 UTC (in 4h 12m)" },
+    "suspended_frame": { "$slot": "frame_id",        "$from": "live.frame_id",        "$example": "task_99a8b1" },
+    "provider":        { "$slot": "provider",        "$from": "live.provider",        "$example": "threads" },
+    "verb":            { "$slot": "api_verb",        "$from": "live.api_verb",        "$example": "threads.create_media_post" },
+    "lines": [ { "$interpolate": "routine {{routine_name}}@{{routine_version}} ({{frame_id}})",
+                 "$bindings": { "routine_name": "scenario.routine_name",
+                                "routine_version": "scenario.routine_version",
+                                "frame_id": "live.frame_id" },
+                 "$example": "routine broadcast_newsletter@2 (frame_018)" } ]
   }
 }
```

### 2.2 `screens/sys/trace/sys.trace.success.populated.json`

```diff
 {
-  "$schema": "wireframe/v2",
+  "$schema": "wireframe/v1",
   "id": "sys.trace.success.populated",
-  "target": "op_7c4f",
-  "command": "capcli sys audit trace op_7c4f --explain",
+  "scenario": { "session_id": "ses_a992f", "root_intent": "fulfill urgent pending orders", "trace_op": "op_7c4f" },
+  "target":  { "$slot": "trace_op", "$from": "scenario.trace_op", "$example": "op_7c4f" },
+  "command": { "$interpolate": "capcli sys audit trace {{trace_op}} --explain",
+               "$bindings": { "trace_op": "scenario.trace_op" },
+               "$example": "capcli sys audit trace op_7c4f --explain" },
   "context": { "env": "dev", "tier": "tier_1", "trust": "draft", "data_shape": "populated" },
   "archetype": "tree",
   "component": {
-    "title": "Causal DAG Trace (op_7c4f)",
-    "root": "ses_a992f session.start \"fulfill urgent pending orders\"",
+    "title": { "$interpolate": "Causal DAG Trace ({{trace_op}})",
+               "$bindings": { "trace_op": "scenario.trace_op" },
+               "$example": "Causal DAG Trace (op_7c4f)" },
+    "root":  { "$interpolate": "{{session_id}} session.start \"{{root_intent}}\"",
+               "$bindings": { "session_id": "scenario.session_id", "root_intent": "scenario.root_intent" },
+               "$example": "ses_a992f session.start \"fulfill urgent pending orders\"" },
     "nodes": [{
-      "label": "op_9f2c routine.dispatch_order@4",
+      "label": { "$slot": "n0", "$from": "live.trace.nodes[0].label", "$example": "op_9f2c routine.dispatch_order@4" },
       "children": [
-        { "label": "op_9f2d db.query (orders) ✓ [allowed] 12ms", "children": [] },
+        { "label": { "$slot": "n0c0", "$from": "live.trace.nodes[0].children[0].label",
+                     "$example": "op_9f2d db.query (orders) ✓ [allowed] 12ms" }, "children": [] },
         …
       ]
     }]
```

The remaining 258 fixtures apply the same three transformations. Every `$slot`/`$interpolate` carries `$example: <current literal>`.

---

## 3. `cans/artifacts/wireframe/wireframe.html`

```diff
-function fixtureExitCode(fixture){
-  if(!fixture)return 0;
-  if(fixture.$schema==='wireframe/v2')return exitCodeFromScreenId(fixture.id||fixture.screen_id);
-  return fixture.state?.exit_code??0;
-}
+function screenExitCode(screen){
+  if(!screen)return 0;
+  return exitCodeFromScreenId(screen.id);
+}

-function normalizeV2Fixture(fixture){ … }
+function instantiate(value){
+  if(Array.isArray(value))return value.map(instantiate);
+  if(value&&typeof value==='object'){
+    if('$slot' in value)return instantiate(value.$example);
+    if('$interpolate' in value)return instantiate(value.$example);
+    const out={};
+    for(const[k,v]of Object.entries(value))out[k]=instantiate(v);
+    return out;
+  }
+  return value;
+}
+
+function normalizeScreen(screen){
+  const id=screen.id||'';
+  const exit=exitCodeFromScreenId(id);
+  const inst=instantiate(screen);
+  const context={env:'dev',tier:'tier_1',trust:'draft',
+                 ...(inst.context&&typeof inst.context==='object'?inst.context:{}),
+                 id, audit_op:inst.audit_op??null, exit};
+  const renderer=WIREFRAME_V1_RENDERERS[inst.archetype];
+  const built=renderer?renderer(context,inst.component||{}):null;
+  const header=built?.header||{style:'badge',label:`exit ${exit}`};
+  const sections=built?.sections||[];
+  const rawTrailer=inst.trailer||inst.next_action;
+  const trailer=(rawTrailer&&typeof rawTrailer==='object')
+    ?{prompt:rawTrailer.prompt??rawTrailer.next_prompt,reason:rawTrailer.reason,serve:rawTrailer.serve}
+    :undefined;
+  return{ ...inst,
+    state:{exit_code:exit,env:context.env,tier:context.tier,trust:context.trust,
+           state_modified:exit!==0?false:!!inst.state_modified,
+           domain:(inst.component&&inst.component.domain)||null,data_shape:null},
+    render:{header,sections}, trailer };
+}

-  const view=fixture.$schema==='wireframe/v2'?normalizeV2Fixture(fixture):fixture;
+  const view=normalizeScreen(fixture);

-const WIREFRAME_V2_RENDERERS={…};
+const WIREFRAME_V1_RENDERERS={…};

-  const exit=fixtureExitCode(fixture);
+  const exit=screenExitCode(fixture);
```

`TerminalPanel`, `JourneyChip`, `GraphNode`, `GraphEdge`, and the four component renderers are unchanged.

---

## 4. `cans/artifacts/wireframe/wireframe-structure.md`

### §1 invariants — add one bullet

```diff
 * **Dynamic Environment Namespaces:** …
+* **Slot Law:** every screen is `$schema: "wireframe/v1"`; instance data appears as `$slot` or `$interpolate` with `$example`. Semantic literals (`id`, `archetype`, `rule`, `domain`, `layer`, `remedy`, `context.{env,tier,trust}`) are never slotted. Grammar — `manifest.json#output_contract.slot`.
```

### §5 — every fixture in §5 is converted as in §2 of this doc

Rendered output is byte-identical because `$example` matches today's literal.

### §6.1 — replace the schema block with §6.1 `Screen Shape`

Delete `### 6.1 Screen Fixture Schema` through the end of "Component law", replace with:

````markdown
### 6.1 Screen Shape

A screen is a serialized `CliEnvelope` payload with typed holes.

Root field law:

- `$schema` is `"wireframe/v1"`. `id` is the screen identity; noun and verb are its first two segments.
- `scenario` is a light key-value block carrying the per-screen data referenced by `$from: "scenario.*"`.
- `command`, `target`, and any component value may be a literal string, a `$slot` object, or an `$interpolate` object.
- `context`, `audit_op`, `trailer`, `affordances`, `attention`, `archetype`, `component` — unchanged from today.
- `archetype` is exactly one of `diagnostic`, `tree`, `receipt`, `document`. `component` carries that archetype's payload.

Slot grammar (also declared in `manifest.json#output_contract.slot`):

```json
{ "$slot": "<name>", "$kind": "instance", "$from": "<binding>",
  "$type"?: "<urp|string|integer|…>", "$pattern"?: "<regex>", "$enum"?: [...],
  "$example": "<current literal>" }

{ "$interpolate": "text {{a}} text {{b}}",
  "$bindings": { "a": "<binding>", "b": "<binding>" },
  "$example": "<current literal>" }
```

Binding sources (closed set):

- `context.*` — the screen's own `context` block.
- `scenario.*` — the screen's `scenario` block.
- `world.*` — seeded workspace state for the screen's scenario (opt-in).
- `live.*` — extracted from the invocation's actual envelope at assertion time.

`$kind` is `"instance"` or absent. `$example` is required.

Derived state is unchanged: exit code derives from the `id` state segment; `state_modified` derives from exit-0 variants in `_states.json`; diagnostics carry no `exit_code` or `state_modified`; typography (carets, glyphs, dividers, alignment) is renderer output.
````

### §6.2 — replace the runner with structural match

Delete the current `test_wireframe_fixtures.rs` code block and its supporting structs; replace with:

````markdown
### 6.2 Runner Contract

One mode — **structural match**. `cargo test --workspace` executes it against every screen.

For each screen:

1. Dispatch `command` against the real binary.
2. Extract `live.*` bindings from the emitted envelope (via the `CliEnvelope<T>` deserializer).
3. Walk the screen: every literal matches byte-exact; every `$slot` satisfies its `$type`/`$pattern`/`$enum` and equals the actual field; every `$interpolate` produces a string that equals the actual field.
4. Assert exit code equals the derivation from `id`; assert `state_modified: false` on non-zero exits.
5. Assert banned tokens absent, no pipe character, trailer present iff `_triggers.json` says so, no `next_action` on a screen with no trailer.

Strict instantiation (substitute `$example`, byte-compare) is a developer tool: `cargo xtask wireframe-strict`. It never runs in CI.

Cross-layer test (`assert_prompt_triggers_match_wireframe_screens`) is unchanged.
````

### §7 — one-line fix

```diff
-The HTML canvas renders all screens directly from `.json` fixture shapes. No `.txt` files are fetched.
+The HTML canvas renders all screens by instantiating `$example` values from `wireframe/v1` screens. No `.txt` files are fetched.
```

### §8 and §9 — new sections appended

````markdown
## 8. Codegen Contract

`wireframe-codegen` (module `crates/capcli-cli/src/codegen/`, binary `wireframe-codegen`) reads every `wireframe/v1` screen — kernel and installed plugin — and emits, deterministically (sorted iteration, no timestamps):

```
crates/capcli-types/src/generated/
  envelope.rs        CliEnvelope<T> per archetype
  bindings.rs        <Screen>Bindings per screen family
  diagnostics.rs     DiagnosticRule enum from the union of `rule` literals
  domains.rs         Domain enum, cross-checked against _states.json
crates/capcli-cli/src/generated/
  nouns/<noun>.rs    clap subcommand trees
  renderers/<…>.rs   fn render(&<Screen>Bindings) -> Component
  tests/             structural-match #[test_case] entries
```

Hand-written modules own behavior (authorizer, quota, DAG, claims); generated modules own surface. The seam is `<Screen>Bindings` — handlers populate it; generated renderers format it.

`wireframe-codegen --check` regenerates into a temp dir and exits 1 on any diff against the checked-in modules.

## 9. Plugin Screens

A plugin author writes one `screens:` map per verb (`defineVerb({ screens: {…} })`). `capcli plugin build` emits, inside the plugin package:

- `screens/<noun>.<verb>.<state>.<condition>.json` — one per state
- `capcli-plugin.yaml#cli.surface[].screens[]` entries pointing at those files

`capcli plugin install` runs `wireframe-codegen --plugin <id>`, mounts the generated clap subcommands into the noun tree, registers renderers keyed by `(noun, verb, state)`, and atomic-flips the generation pointer.

**Reciprocal obligation:** every key in `defineVerb.screens` must yield a resolvable screen at build time and install time.

**Escape hatch:** `screens: { success: Custom({ renderer: "./renderers/logs.ts" }) }` — the renderer runs in a Tri-Jail sandbox; the kernel validates output against `CliEnvelope<T>` before wrapping.

**Pack vs screen:**

| | pack | screen |
|---|---|---|
| Kind | shipping unit (`.cap`) | rendering unit (one CLI output) |
| URP | `pack://*` | none (`<noun>.<verb>.<state>.<condition>`) |
| Lifecycle | `new → bundle → import → scaffold` | authored → bound → rendered |
| Contains the other? | yes — a pack may ship `screens/` | no — a screen is never a pack |
````

---

## 5. `cans/_rules.yaml`

```diff
   required_qualifiers:
     env: [environment, process env, CliEnvelope]
     …
     namespace: [ctx namespace, CLI noun]
+    template: [manifest template, pack template, code template]
```

```diff
   wireframe: interface.md#Surface-conformance
   wireframe_contract: kernel.md#Diagnostic-output-law
   wireframe_runner: assembly.md#Test-architecture
+  output_shape: artifacts/wireframe/wireframe-structure.md#61-screen-shape
+  output_shape_instances: artifacts/wireframe/screens/
+  output_shape_grammar: artifacts/wireframe/manifest.json#output_contract.slot
+  surface_generation: artifacts/wireframe/wireframe-structure.md#8-codegen-contract
+  plugin_screens: artifacts/wireframe/wireframe-structure.md#9-plugin-screens
@@
 overflow:
   max_node_chars: 95
   force_file_for: [code_block, table, diagram]
+
+shape_exception:
+  # Root anchors may cite the wireframe for CLI output shape. The
+  # wireframe owns shape; there is no trailing consumer to chain
+  # through, so this is the one legal root → artifacts pointer.
+  permitted_from: [overview.md, kernel.md, AGENTS.md, _rules.yaml]
+  permitted_to:
+    - artifacts/wireframe/screens/
+    - artifacts/wireframe/wireframe-structure.md
+  reason: "shape is generated, not derived; no trailing consumer to chain through"
```

No `wireframe:` / `wireframe_contract:` / `wireframe_runner:` keys are removed — only new keys added.

---

## 6. `cans/AGENTS.md`

```diff
 - Root anchors — overview.md, kernel.md, AGENTS.md, _rules.yaml
 - Branch files — plugins, sandbox, egress, governor, routines, world,
-  effect, governance, identity, lifecycle, marketplace, interface
+  effect, governance, identity, lifecycle, marketplace, interface,
+  artifacts/wireframe/wireframe-structure
 - Leaf file — assembly.md (points to everything, nothing points to it)
+- Shape exception — root anchors may cite artifacts/wireframe/screens/
+  and artifacts/wireframe/wireframe-structure.md for CLI output shape
+  per _rules.yaml#shape_exception; no other downward pointer is legal

 Violations to reject:
 - Root file with `see <branch>.md` — wrong direction
 - Any chain: `A → B → C`. Collapse to `A → C`.
+- Root file citing artifacts/wireframe outside _rules.yaml#shape_exception
```

---

## 7. `cans/interface.md#Surface-conformance`

```diff
     - Surface conformance <!-- ref-by: assembly.md -->
       - Mechanism
-        - Executable mirror of this file's CLI grammar
-        - Golden fixture per screen, byte-asserted in CI
-        - Never a source of truth, only a mirror
-        - Canonical homes — kernel.md, effect.md, this file
+        - Executable IDL of the CLI surface
+        - Canonical home for shape — wireframe-structure.md#61-screen-shape
+        - This node consumes shape; it does not own it
+        - Generated clap trees, envelope structs, renderers
         - Runner mechanics — see assembly.md#Test-architecture
       - Fixture identity
         - Location — artifacts/wireframe/screens/
         - Naming — <noun>.<verb>.<state>.<condition>.json
-        - One JSON per screen, zero .txt companions
+        - One screen per invocation, zero .txt companions
         - Path depth exactly three under screens/
-        - Root shape — wireframe/v2 CliEnvelope
+        - Root shape — wireframe/v1 CliEnvelope with $slot / $interpolate
+        - Shape grammar — wireframe-structure.md#61-screen-shape
       - Fixture derivation
-        - Command string carries the invocation verbatim
+        - command carries the invocation as literal or $interpolate
         - Exit code derives from the id state segment
         - state_modified derives from the exit law
         - Derived fields never stored, always computed
         - Exit law — see kernel.md#Exit-code-law
       - State taxonomy
         - Six states, one per exit code, no seventh
         - Mirror of the exit-to-domain law
         - Canonical home — see effect.md#Denials
         - Mirror file — artifacts/wireframe/_states.json
         - Fixture domains must resolve to canon
       - Flow engine
         - Journeys declare entry and terminal screens
         - Transitions bind from, to, trigger, arrow type
-        - Every endpoint resolves to a fixture id
-        - Every fixture id appears in some journey
+        - Every endpoint resolves to a screen id
+        - Every screen id appears in some journey
         - Mirror file — artifacts/wireframe/_flows.json
       - Registry mirror
         - Nouns mirror this file plus plugin nouns
         - Noun registry — see #Two-tier-noun-model
         - Schemes mirror this file's URP dispatch
         - URP dispatch — see #Run-noun
         - Mirror file — artifacts/wireframe/manifest.json
       - Companion
-        - Byte-level fixture schema and runner contract
+        - Byte-level screen grammar and runner contract
         - Shape only, never mechanism or lifecycle
         - Detail — artifacts/wireframe/wireframe-structure.md
-        - Zero authority, cited for byte shapes
+        - Authority for shape; cited by canon for byte grammar
       - PR gate
         - Fires on CLI surface, exit, or archetype change
         - Fires on output contract or domain change
         - Runner — assembly.md#Test-architecture
         - Checker — assembly.md#Checker-tool
         - Gate — assembly.md#PR-gate
+        - Codegen — assembly.md#CICD-pipeline
```

---

## 8. `cans/kernel.md#Diagnostic-output-law`

```diff
     - Data contract
       - All commands return CliEnvelope<T>
       - Envelope shape — context, exit_code, state_modified
       - Plus data, diagnostic, audit_op
       - --json returns raw serialized envelope
+      - Concrete layout — see artifacts/wireframe/wireframe-structure.md#61-screen-shape
     …
     - Archetype A structure
       - Header line with exit domain
       - Failing span with caret markers
       - Indented metadata block
       - Remedy line for agent fix
+      - Layout grammar — see artifacts/wireframe/wireframe-structure.md#61-screen-shape
     - Archetype B structure
       …
+      - Layout grammar — see artifacts/wireframe/wireframe-structure.md#61-screen-shape
     - Archetype C structure
       …
+      - Layout grammar — see artifacts/wireframe/wireframe-structure.md#61-screen-shape
     - Archetype D structure
       …
+      - Layout grammar — see artifacts/wireframe/wireframe-structure.md#61-screen-shape
@@
     - Fixture law
-      - Screen is a wireframe/v2 fixture JSON
+      - Screen is a wireframe/v1 fixture JSON
       - Schema — see artifacts/wireframe/wireframe-structure.md
       - Exit code derived from id state segment
       - state_modified derived from exit-0 variant
       - Trailer dispatch — artifacts/prompt/_triggers.json
       - Runner — see assembly.md#Test-architecture
```

Semantics (exit derivation, archetype presence, trailer/attention/affordance law, typography bans) stay in `kernel.md`. Concrete layout points at `wireframe-structure.md`.

---

## 9. `cans/plugins.md`

### `#Manifest`

```diff
     - Capability declarations <!-- ref-by: effect.md, egress.md, marketplace.md -->
       - verbs — callable operations with params
       - subscribes — causal DAG event patterns
       - provides — native extension surfaces
       - fuel_declared — per-verb fuel envelope
       - attends — attention source names
+      - screens — per-verb screen map, one screen per exit state
+      - Screen shape — see artifacts/wireframe/wireframe-structure.md#9-plugin-screens
       - Frame fields — see governance.md#Budget-frames
```

### `#Capabilities`

```diff
     - Plugin verbs
       - Declaration — name, description, params
       - Invocation — JSON on stdin, JSON on stdout
       - Exit protocol — integer contract
       - Fuel declaration — integer per verb
       - Param typing — integer, string, boolean
       - Default values — optional fallback
+      - Screen map — one screen per state, generated by the SDK
+      - SDK surface — defineVerb({ screens: { … } })
+      - Screen files emitted at plugin build
+      - Screen shape — see artifacts/wireframe/wireframe-structure.md#9-plugin-screens
```

### `#CLI-projection`

```diff
     - Compilation
-      - Install time — validate, check collisions
-      - Write — plugins.json.cli_projection
-      - Boot — merge with native clap tree
-      - Update — new generation carries new projection
-      - Disable — projection unmounts immediately
+      - Plugin build — SDK emits screens/<noun>.<verb>.<state>.json
+      - Plugin build — SDK emits cli.surface[].screens[] entries
+      - Install time — validate, check collisions
+      - Install time — wireframe-codegen --plugin <id>
+      - Install time — merge generated clap into native tree
+      - Write — plugins.json.cli_projection
+      - Boot — mount generated subcommands
+      - Update — new generation carries new screens
+      - Disable — projection unmounts immediately
+      - Screen shape — see artifacts/wireframe/wireframe-structure.md#9-plugin-screens
```

### `#Installation-lifecycle`

```diff
     - Pre-flight preview
       - Vault keys — displayed before write
       - Egress domains — displayed before write
       - Shell commands — displayed before write
+      - Screens — every cli.surface[].screens[] entry must resolve
       - Confirmation — explicit operator approval
```

---

## 10. `cans/marketplace.md#Intake`

```diff
     - Intake pipeline
       - 1 — Download to tmpfs /scratch
       - 2 — Stream cap at 5MB
       - 3 — SHA-256 verify against index
       - 4 — Archive extraction
       - 5 — rule validate on manifest
       - 6 — Sub-check 1 and 2 on schema
       - 7 — py_compile on routines
       - 8 — AST complexity scan
-      - 9 — Register into dev worktree
+      - 9 — Verify every cli.surface[].screens[] entry resolves to a wireframe/v1 screen
+      - 10 — Register into dev worktree
+      - Screen shape — see artifacts/wireframe/wireframe-structure.md#9-plugin-screens
```

---

## 11. `cans/assembly.md`

### 11.1 `## Monorepo layout` — declarative artifacts

```diff
     - Declarative artifacts
       - Path — artifacts/
       - templates/world-schema.yaml — domain model
       - system-schema.yaml — kernel tables
       - policy.yaml — behavioral rules
       - governance.yaml — structural limits
       - world.sql — deterministic DDL dump
-      - artifacts/wireframe/ — golden CLI fixtures, edgeless canvas
+      - artifacts/wireframe/ — canonical CLI surface IDL, edgeless canvas
       - artifacts/prompt/ — trailer trigger table, prompt campaigns
       - artifacts/test-plan/ — behavioural cases, 1:1 with crate tests
       - Definition — see world.md#Dual-schema
```

### 11.2 `## Rust workspace crates` — cli description

```diff
     - Crates
       - capcli-types — shared contracts (exit, error, URP, audit, schema, rpc)
       - capcli-core — domain engine (db, parse, compile, budget, audit, vault, plugin)
-      - capcli-cli — CLI executable (main, transport, commands, terminal)
+      - capcli-cli — CLI executable (main, transport, commands, terminal, codegen)
       - capcli-daemon — daemon (server, hub_rpc, ipc, cron, webhook, reaper, registry)
```

### 11.3 `## Core subsystems` — new top-level `Surface` category

Insert after `## Core subsystems` intro bullets, before `- Kernel`:

```diff
   - Core subsystems
+    - Surface
+      - codegen — mod.rs, screens.rs, emit_types.rs, emit_cli.rs
+      - codegen — reads wireframe/v1 screens, emits generated modules
+      - codegen — binary wireframe-codegen, `--check` diffs generated output
+      - codegen — lives in capcli-cli, not core
+      - Contract — see artifacts/wireframe/wireframe-structure.md#8-codegen-contract
     - Kernel
       - db — connection.rs, authorizer.rs, migrate.rs, bytecode.rs
```

### 11.4 `## Test architecture` — fixture law

```diff
       - Fixture law
-        - Fixture mechanism — see interface.md#Surface-conformance
-        - Fixture runner asserts stdout byte-identical
-        - Fixture runner asserts derived exit and state_modified
-        - Fixture runner asserts banned tokens absent
-        - Cross-layer — every trigger entry resolves to fixture
+        - Fixture mechanism — see interface.md#Surface-conformance
+        - Fixture runner asserts structural match (wireframe-structure.md#62-runner-contract)
+        - Fixture runner asserts derived exit and state_modified
+        - Fixture runner asserts banned tokens absent, no `template` substring
+        - Cross-layer — every trigger entry resolves to a screen
       - Runner contract — see artifacts/wireframe/wireframe-structure.md
       - Onboarding — see interface.md#Onboarding
```

### 11.5 `## Build outputs` — rendering line and generated dirs

```diff
     - Binary composition
       - Static x86_64 and aarch64 musl
       - libc and SQLite bundled
       - No dynamic host library dependency
       - Zero pack bundling in binary
-      - CLI renders output procedurally
+      - CLI renders output via generated renderers
+    - Generated modules
+      - Path — crates/capcli-types/src/generated/
+      - Path — crates/capcli-cli/src/generated/
+      - Emitted by wireframe-codegen, checked in
+      - Regenerated on every `cargo build` via build.rs hook
+      - --check-gated in CI; hand-edits fail the PR
+      - Contract — see artifacts/wireframe/wireframe-structure.md#8-codegen-contract
```

### 11.6 `## CICD pipeline` — PR gate jobs, codegen job, checker tool

```diff
     - PR gate
       - Workflow — .github/workflows/pr-gate.yml
       - SLA — under 4 minutes, fail-closed
-      - Jobs — PWA, Astro, Trinity, Rust, TS, Python, Cans
+      - Jobs — PWA, Astro, Trinity, Codegen, Rust, TS, Python, Cans
       - Config — see artifacts/contracts/cicd.yaml
       - Concurrency — cancel-in-progress per ref
+      - Codegen job
+        - Runs wireframe-codegen --check
+        - Fails on any diff against checked-in generated modules
+        - Deterministic: sorted iteration, no timestamps
+        - Contract — see artifacts/wireframe/wireframe-structure.md#8-codegen-contract
       - Cans check
         - Tool — cans-spec 0.5.1 via bunx
         - Trigger — cans/** changes only
         - Pass — 0 errors, 0 broken refs
+        - Pass — 0 occurrences of `template` in cans/** prose
+        - Pass — 0 occurrences of `template` in artifacts/wireframe/screens/**
         - Config — see artifacts/contracts/cicd.yaml
```

```diff
     - Checker tool
       - Tool identity — tools/check-trinity.py
       - Zero third-party dependencies
       - Identical local and CI execution
       - Exit 0 intact, exit 1 breach
       - Fixture resolution for every screen
       - Doc URI resolution to markdown
       - Anchor slug verification
       - Token estimation via 3.5 char ratio
+      - Slot grammar — every $slot / $interpolate satisfies manifest.json#output_contract.slot
+      - Semantic-position check — no $slot at rule, domain, layer, archetype, remedy, context.{env,tier,trust}
+      - Binding-prefix check — $from/$bindings values match context.*, scenario.*, world.*, live.*
       - Config — see artifacts/contracts/cicd.yaml
```

### 11.7 `## Verification checklist`

```diff
     - Verification checklist
       - 1 Pre-build — workspace diff, path filter
-      - 2 Compile — AST syntax, semantics, DFS
-      - 3 Integrity — lockfile, Trinity, UI assets
-      - 4 Runtime — sandbox, binary, polyglot
+      - 2 Codegen — wireframe-codegen --check, zero drift
+      - 3 Compile — AST syntax, semantics, DFS
+      - 4 Integrity — lockfile, Trinity, UI assets
+      - 5 Runtime — sandbox, binary, polyglot
       - Token ceilings — see routines.md#Shape-constraints
       - Config — see artifacts/contracts/cicd.yaml
```

---

## 12. `cans/artifacts/contracts/cicd.yaml`

```diff
 filters:
+  wireframe:
+    - 'cans/artifacts/wireframe/**'
   rust:
     - 'crates/**'
     - 'Cargo.toml'
```

```diff
 gates:
+  wireframe_codegen:
+    job: check-codegen
+    trigger:
+      - 'cans/artifacts/wireframe/**'
+      - 'crates/capcli-types/src/generated/**'
+      - 'crates/capcli-cli/src/generated/**'
+    command: cargo run --bin wireframe-codegen -- --check
+    pass_criteria:
+      drift: 0
+      grammar_violations: 0
   cans_check:
     job: check-cans
     trigger:
       - 'cans/**'
     command: bunx -y cans-spec@0.5.1 check
     pass_criteria:
       errors: 0
       broken_refs: 0
       stale_backpointers: 0
+      bare_template: 0
+      template_in_screens: 0
```

---

## 13. `cans/artifacts/templates/plugin.yaml`

Add the `screens[]` field to the `verbs[]` example under `## 2. CAPABILITY DECLARATIONS`:

```diff
 verbs:
   - name: charge
     description: "Authorize and capture credit card charge"
     params:
       amount_cents: { type: integer, required: true }
       customer_id: { type: string, required: true }
       currency: { type: string, default: "usd" }
     fuel_declared: 15
+    screens:
+      - { state: success, archetype: receipt,    screen: "screens/stripe.charge.success.chap_captured.json" }
+      - { state: denial,  domain: api.quota, rule: api.quota.exhausted, archetype: diagnostic, screen: "screens/stripe.charge.denial.quota.json" }
+      - { state: yield,   domain: api.quota, archetype: diagnostic, screen: "screens/stripe.charge.yield.quota.json" }
   - name: refund
```

And under `## 2. CAPABILITY DECLARATIONS` preamble comments:

```diff
 # Verbs — callable operations with params
 # Subscribes — causal DAG event patterns
 # Provides — native extension surfaces
 # fuel_declared — per-verb fuel envelope
+# screens — per-verb screen map, one screen per exit state
+# screens — generated by SDK from defineVerb({ screens }); not hand-authored
 # Canonical home — plugins.md#Capabilities
```

---

## Summary

| Kind | Count | Files |
|---|---|---|
| Config/prose edits | 12 | `manifest.json`, `wireframe.html`, `wireframe-structure.md`, `_rules.yaml`, `AGENTS.md`, `interface.md`, `kernel.md`, `plugins.md`, `marketplace.md`, `assembly.md`, `cicd.yaml`, `templates/plugin.yaml` |
| Screen rewrites | 260 | `screens/**/*.json` — three mechanical transformations per file |
| **New files** | **0** | — |
| **New crates** | **0** | codegen is a module in `capcli-cli`, described in `assembly.md` |

`_states.json`, `_flows.json`, `_triggers.json`, `pack.yaml`, `pack-schema.yaml`, `policy.yaml`, `governance.yaml` — untouched. No `v2`, no `v3`, no migration prose, no `returns:`, no `_scenarios/`, no `_bindings.schema.json`. Every fixture is `wireframe/v1`. Every reference to `template` in the wireframe namespace is now `screen`, enforced by a `cans check` gate.
