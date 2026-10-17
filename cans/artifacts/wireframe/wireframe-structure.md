# Wireframe Fixture Schema & Runner Contract

Fixture schema and runner contract only. Mechanism spec lives at
cans/interface.md#Surface-conformance. This document owns byte-level
shape; that node owns what, why, when.

Anchor nodes — cross-file pointers land on these four:

- Screen Shape
- Runner Contract
- Codegen Contract
- Plugin Screens

---

## 1. Directory Tree & Architecture

The wireframe layer serves a dual purpose: an **interactive edgeless canvas** for humans and harnesses, and a **deterministic golden-file test fixture suite** for the Rust kernel.

Flow graphs, journey definitions, and multi-branch transition metadata are codified into `_flows.json`. Individual screen fixtures are atomic, stateless JSON shapes congruent with runtime compiler and authorizer output. No `.txt` companions are committed; the renderer (HTML or Rust) is the sole consumer of the JSON shape.

```
cans/artifacts/wireframe/
  manifest.json
  _flows.json
  _states.json
  wireframe.html
  screens/
    run/
      execute/
      sql/
      overview/
      search/
      inspect/
      abort/
    db/
      lock/
      unlock/
      schema/
      snapshot/
      restore/
      dump/
    routine/
      prove/
      ship/
      pending/
      sweep/
      stats/
      rollback/
      retire/
    api/
      sync/
      diff/
      catalog/
      prove/
      ship/
      stats/
      retire/
      rollback/
      record/
    bind/
      cron/
      webhook/
      endpoint/
      list/
      inspect/
      pause/
      resume/
      remove/
      keys/
      federation/
    ping/
      notify/
      ask/
      list/
      resolve/
      expire/
    rule/
      show/
      diff/
      apply/
      validate/
      plan/
      prove/
    env/
      new/
      use/
      list/
      inspect/
      doctor/
      merge/
      remove/
    sys/
      help/
      inbox/
      init/
      tail/
      trace/
      query/
      replay/
      audit_sample/
      register/
      agents/
      revoke/
      vault_set/
      vault_import/
      vault_list/
      doctor/
      backup/
      recover/
      update/
      exec/
      serve/
      swarm/
      shim/
    doc/
      read/
      outline/
      inspect/
    pack/
      import/
      new/
      pack/
      scaffold/
      sync/
    serve/
      export/
      start/
      stop/
      restart/
      status/
    storage/
      put/
      get/
      url/
      list/
      remove/
    plugin/
      install/
      link/
      unlink/
      list/
      inspect/
      update/
      enable/
      disable/
      uninstall/
      search/
      logs/
      doctor/
    ws/
      peers/
      dial/
      status/
      cassettes/
```

### 1.1 Structural Invariants
* **Active Nouns:** The 9 kernel-reserved nouns (`run`, `sys`, `plugin`, `db`, `routine`, `env`, `rule`, `doc`, `pack`) are always active (interface.md#The-9-kernel-nouns). Plugin-provided nouns (`api`, `bind`, `ping`, `serve`, `storage`, `ws`) arrive with pack installs and leave at uninstall (interface.md#Plugin-provided-nouns).
* **Single-Source Law:** Every screen has exactly one `.json` fixture. No `.txt` files are committed. The JSON shape IS the screen; renderers (HTML canvas, Rust test harness) consume it directly.
* **Depth Ceiling:** File paths relative to `screens/` must remain exactly 3 path components: `{noun}/{verb}/{filename}.json`.
* **Sibling Invariants:** Min 3, max 18 verb directories per noun branch node.
* **Naming Law:** Strict 4-segment token syntax:
  ```
  {noun}.{verb}.{state}.{condition}.json
  ```
* **Root Aliases:** Exactly four ergonomic root shortcuts are legal invocation grammar (cans/interface.md#CLI-surface): `capcli sql` ≡ `capcli run sql`, `capcli search` ≡ `capcli run search`, `capcli inspect` ≡ `capcli run inspect`, and `capcli apply` ≡ `capcli rule apply schema`. These four root aliases may appear in fixture `command` strings; no other root shortcuts exist — everything else is `capcli <noun> <verb>`.
* **Run Execute Form:** `capcli run <cap://...>` is the execute invocation (cans/interface.md#CLI-surface: `execute — run <capability>`); `execute` names the screen family and the fixture directory and does not appear in the typed command, and no `capcli run execute ...` form exists.
* **Compound-Verb Mapping:** Screen IDs use `{noun}.{verb}.{state}.{condition}` where the verb joins multi-token verbs with underscore (`sys.vault_set`, `sys.vault_import`) and carries single-token verbs bare (`sys.register`, `sys.revoke`, `sys.agents`). The invocation grammar follows cans/interface.md#CLI-surface and may differ in surface form (`capcli sys vault set`, `capcli sys agent register`). The ID names the fixture; the spaced form is what the user types.
* **Dynamic Environment Namespaces:** Environments are user-provisionable namespaces (`env new <slug>`, cans/interface.md#CLI-surface). `state_axes.env` in `manifest.json` lists only the kernel-reserved roots (`dev`, `sim`, `prod`); values like `staging` or `lab` are legal fixtures of dynamically provisioned namespaces (see `env_policy` in `manifest.json`).
* **Slot Law:** every screen is `$schema: "wireframe/v1"`; instance data appears as `$slot` or `$interpolate` with `$example`. Semantic literals (`id`, `archetype`, `rule`, `domain`, `layer`, `remedy`, `context.{env,tier,trust}`) are never slotted. Grammar — `manifest.json#output_contract.slot`.

---

## 2. Core Manifests & States

### 2.1 `manifest.json`

Canonical file: `manifest.json` (same directory). It owns the noun list, the state axes, and the output contract; this document points at it and does not reproduce it.

The domain registry lives only in `_states.json`. This manifest carries no copy of it; consumers read `_states.json` directly.

Naming convention, both artifact directories (`wireframe/`, `prompt/`): a leading underscore marks internal engine configuration and graph state — `_states.json`, `_flows.json`, `_triggers.json`. A clean name marks an externally consumable compiler artifact — `manifest.json`.

### 2.2 `_states.json`

Canonical file: `_states.json` (same directory). It is a generated mirror of the state taxonomy owned by effect.md#Denials: exit code → label, exit → legal domains, exit → required diagnostic fields. The mirror derives from canon and owns nothing. Not reproduced here by design.

The law in one paragraph: six states, one per exit — `success` 0, `denial` 2, `refusal` 3, `crash` 4, `panic` 5, `yield` 6 (kernel.md#Exit-code-law). The screen-ID state slot takes exactly these labels; severity and lifecycle words (`warning`, `tamper`, `suspended`, `rolled_back`) live in the condition slot. A domain determines its exit; the domain→exit mapping lives in effect.md#Denials and this document restates none of it. `api.quota` is dual-registered (exit 2 Critical, exit 6 Background). `policy.pack` registers exit 3 only — pack intake validation refusal. Exit 6 covers both quota yields and `ping.ask` frame suspensions (governor.md#Suspension-registry).

---

## 3. Decoupled Flow & Journey Engine (`_flows.json`)

Canonical file: `_flows.json` (same directory). It owns journeys and screen-to-screen routing; this document points at it and does not reproduce it.

Every screen ID referenced by a flow must exist as a `.json` fixture under `screens/` and as a row in §4 — the validator enforces closure. Flow prose in §5 quotes individual screens for walkthroughs; the routing itself lives only in `_flows.json`.

---

## 4. Complete Screen Inventory & State Matrix

This table is a context index: one scannable surface a reader loads
before drilling into fixture shapes. It indexes; it does not originate.
Fixture `.json` files under `screens/` are the source, `_states.json` owns
state and domain legality, and `_flows.json` owns routing. Every row
resolves to one fixture shape and every fixture shape has one row —
the validator enforces closure, and in any conflict the fixture wins.


### 4.1 `run/` (6 verbs → 58 screens)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `run.execute.success.populated` | success | 0 | — | populated | Deterministic execution and commit |
| `run.execute.success.redirected` | success | 0 | — | redirected | Payload directed to file via `--out`; stdout emits receipt |
| `run.execute.success.truncated` | success | 0 | — | truncated | Result >500 tokens; returns `next_cursor` |
| `run.execute.success.echo_scrubbed` | success | 0 | — | echo_scrubbed | Upstream 400 echoed a credential; wire filter scrubbed to `[REDACTED_VAULT_TOKEN]` before sandbox |
| `run.execute.success.resumed_ask` | success | 0 | — | resumed_ask | Ask-resolved resume; frame_026 continues after human approval |
| `run.execute.success.announced` | success | 0 | — | announced | Service incident notice posted after quota window reset |
| `run.execute.denial.budget` | denial | 2 | policy.budget | exhausted | Frame ops/duration ceiling exhausted |
| `run.execute.denial.budget_cascade` | denial | 2 | policy.budget | starved | Pre-flight call-tree analysis detects starved child branch; invocation blocked |
| `run.execute.denial.trust` | denial | 2 | policy.trust | unproven | Draft routine executed in prod |
| `run.execute.denial.secrets_unproven` | denial | 2 | policy.trust | secret_floor | Draft routine resolving a `vault://` handle denied at pre-flight |
| `run.execute.denial.prod_tier2` | denial | 2 | policy.platform | tier2 | `E045_PROD_TIER1_MANDATE` on --env prod from tier 2 |
| `run.execute.denial.authorizer` | denial | 2 | policy.authorizer | forbidden | Prohibited table or column mutation |
| `run.execute.denial.network_jail` | denial | 2 | kernel.sandbox | syscall_42 | Trapped raw `connect()` via seccomp-bpf |
| `run.execute.denial.claim_held` | denial | 2 | db.claims | locked | Exclusive `--lock` ref already held |
| `run.execute.denial.federation_denied` | denial | 2 | policy.federation | unallowlisted | `E042_FEDERATION_DENIED`: peer not an active federated agent |
| `run.execute.denial.federation_cycle` | denial | 2 | policy.federation | cycle | `E041_FEDERATION_CYCLE`: workspace already in call_chain |
| `run.execute.crash.federation_unreachable` | crash | 4 | federation.transport | unreachable | `E055_FEDERATION_UNREACHABLE` after 1500ms poll |
| `run.execute.refusal.missing_secret`| refusal| 3 | policy.secrets | missing_key | Missing credential redirects to Cockpit URL |
| `run.execute.yield.ask` | yield | 6 | ping.ask | suspended | Routine hit `ctx.ping.ask`; frame checkpointed to `_pending_asks`, exits 6 until human resolves |
| `run.execute.yield.quota` | yield | 6 | api.quota | rate_limit | Suspends task; sets `yield_until` timestamp |
| `run.execute.refusal.static` | refusal | 3 | compile | bad_syntax | Pre-flight compile check failed; no guest ran |
| `run.execute.denial.quota` | denial | 2 | api.quota | hard_deny | Critical-priority task drained provider pool to 0; hard-denied, never yielded |
| `run.execute.success.resumed` | success | 0 | — | resumed | Daemon re-dispatches task on token refill |
| `run.execute.denial.occ_drift` | denial | 2 | db.engine | occ_fence | `E061_OCC_DRIFT`: OCC state_fence drifted during suspension; daemon frame resume aborted |
| `run.execute.crash.runtime` | crash | 4 | routine.runtime | exception | Guest language uncaught error |
| `run.execute.crash.poll_timeout` | crash | 4 | routine.runtime | timeout | `poll_until` exceeds 30-second ceiling |
| `run.execute.panic.secret_leak` | panic | 5 | kernel.panic | leak | `kill_and_alert` triggered on plaintext secret leak |
| `run.sql.success.populated` | success | 0 | — | populated | AST-vetted SQL commit |
| `run.sql.denial.authorizer_reviewed` | denial | 2 | policy.authorizer | schema_mod | raw ALTER via `capcli sql` denied at authorizer for reviewed caller, exit 2 |
| `run.sql.success.redirected` | success | 0 | — | redirected | SQL export payload directed to disk via `--out` |
| `run.sql.success.truncated` | success | 0 | — | truncated | SELECT result bounded at 10,000 rows |
| `run.sql.denial.ast` | denial | 2 | policy.ast | unbounded | Missing `WHERE` or `LIMIT` clause |
| `run.sql.denial.authorizer` | denial | 2 | policy.authorizer | schema_mod | Blocked `DROP TABLE` or system table write |
| `run.sql.denial.engine_busy` | denial | 2 | db.engine | timeout | SQLite transaction queue wait timeout |
| `run.sql.denial.audit_sink` | denial | 2 | audit.sink | stalled | Audit sink stalled: mutating write denied while the 5-minute buffer holds the failed write (fail-closed) |
| `run.sql.refusal.unparseable` | refusal | 3 | compile | bad_syntax | Malformed SQL string syntax |
| `run.sql.refusal.missing_intent` | refusal | 3 | missing_param | no_intent | Mutating write missing `-m` / `--intent` |
| `run.overview.success.populated` | success | 0 | — | populated | Situational KPI briefing (<500 tokens) |
| `run.overview.refusal.oversized` | refusal | 3 | validation | oversized | Aggregate briefing exceeded the 500-token ceiling; refused, not clipped |
| `run.search.success.populated` | success | 0 | — | populated | Matched capabilities and URP pointers |
| `run.search.success.empty` | success | 0 | — | empty | Zero hits; outputs semantic suggestions |
| `run.search.success.truncated` | success | 0 | — | truncated | Search results capped at 20 |
| `run.search.success.gaps` | success | 0 | — | gaps | Surfaces missing capabilities via `--since` |
| `run.inspect.success.routine` | success | 0 | — | populated | Pre-flight envelope with `can_invoke_now` |
| `run.inspect.success.quota` | success | 0 | — | populated | Headroom breakdown on `quota://` URP |
| `run.inspect.success.prompt` | success | 0 | — | populated | Artifact preflight envelope: token size, node outlines, bundle metadata for doc://prompts/ inspect |
| `run.inspect.success.pack` | success | 0 | — | populated | pack:// blueprint pre-flight envelope via capcli inspect |
| `run.inspect.refusal.unregistered_scheme` | refusal | 3 | missing_param | unregistered_scheme | tcp:// transport endpoint refused: not a registered URP scheme; remedy capcli sys swarm list |
| `run.inspect.success.ws` | success | 0 | — | populated | ws:// federated routine pre-flight envelope via capcli inspect |
| `run.inspect.refusal.not_found` | refusal | 3 | validation | not_found | Pack URP does not resolve |
| `run.inspect.refusal.missing_ptr` | refusal | 3 | missing_param | missing_arg | Unrecognized target pointer format |
| `run.inspect.refusal.removed_scheme` | refusal | 3 | missing_param | removed_scheme | hub:// removed scheme refused at parse with exit 3 |
| `run.inspect.success.masked` | success | 0 | — | redacted | Secret references rendered as [REDACTED_VAULT_TOKEN]; inspect exits 0 on all rungs |
| `run.inspect.success.plugin` | success | 0 | — | populated | Plugin CLI noun envelope: cli_noun, verbs, rung, generation for plugin:// id |
| `run.inspect.success.vault` | success | 0 | — | populated | Vault secret metadata envelope; value masked for vault:// name |
| `run.inspect.success.audit` | success | 0 | — | populated | Audit op causal summary for audit:// op id |
| `run.inspect.success.ask` | success | 0 | — | populated | Pending ask question, options, and frame for ask:// id |
| `run.inspect.success.policy` | success | 0 | — | populated | Policy bundle keys and digest for policy:// node |
| `run.inspect.success.db` | success | 0 | — | populated | DB entity inspection: columns, rows, write grants for db:// table |
| `run.abort.success.aborted` | success | 0 | — | aborted | Suspended frame purged; OCC fence released |
| `run.execute.success.attention` | success | 0 | — | attention | Commit landed with nonzero attention; `top` carries the pending ask and inbox rows |
| `run.abort.refusal.unknown_frame` | refusal | 3 | missing_param | unknown_frame | Abort target frame not suspended |

### 4.2 `db/` (6 verbs → 14 screens)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `db.lock.success.acquired` | success | 0 | — | acquired | Exclusive claim lease registered |
| `db.lock.denial.claim_held` | denial | 2 | db.claims | held | Target resource currently claimed |
| `db.lock.refusal.missing_reason` | refusal | 3 | missing_param | missing_arg | `--reason` required for locking |
| `db.unlock.success.released` | success | 0 | — | released | Claim lease released ahead of TTL |
| `db.unlock.denial.not_holder` | denial | 2 | policy.authorizer | unauthorized | Caller does not own the claim |
| `db.schema.success.populated` | success | 0 | — | populated | Live DDL schema introspected |
| `db.schema.success.empty` | success | 0 | — | empty | Empty database state |
| `db.snapshot.success.created` | success | 0 | — | created | Point-in-time snapshot committed |
| `db.snapshot.denial.prod_draft` | denial | 2 | policy.trust | unproven | Draft identity cannot snapshot prod; rule `policy.trust.unproven`, `E046_TRUST_VIOLATION` (production floor is pinned) |
| `db.restore.success.restored` | success | 0 | — | restored | DB state restored from snapshot |
| `db.restore.refusal.missing_id` | refusal | 3 | missing_param | missing_arg | Target snapshot ID missing |
| `db.restore.denial.active_locks` | denial | 2 | db.claims | active_locks | Active claims prevent state reversal |
| `db.dump.success.populated` | success | 0 | — | populated | Unified SQL schema and seed dump |
| `db.dump.success.truncated` | success | 0 | — | truncated | Dump output payload truncated |

### 4.3 `routine/` (7 verbs → 29 screens)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `routine.prove.success.passed` | success | 0 | — | passed | Dynamic fingerprint verified |
| `routine.prove.success.overview` | success | 0 | — | passed | Overview routine sim rehearsal passes (harness H7) |
| `routine.prove.refusal.syntax` | refusal | 3 | compile | bad_syntax | py_compile rejects malformed guest code |
| `routine.prove.refusal.param_cap` | refusal | 3 | validation | param_cap | 9 typed Param declarations vs the max-8 ceiling |
| `routine.prove.refusal.missing_docstring` | refusal | 3 | validation | missing_docstring | Required description/docstring absent |
| `routine.prove.refusal.oversized_output` | refusal | 3 | validation | oversized | Unpaginated output exceeds the 500-token envelope |
| `routine.prove.denial.shape` | denial | 2 | policy.authorizer | bad_shape | Execution violates declared limits |
| `routine.prove.denial.policy` | denial | 2 | policy.authorizer | illegal_leaf | Routine attempts forbidden leaf op |
| `routine.prove.denial.sandbox` | denial | 2 | kernel.sandbox | breach | Jail containment boundary violation |
| `routine.prove.crash.runtime` | crash | 4 | routine.runtime | exception | Uncaught exception in test pass |
| `routine.ship.success.shipped` | success | 0 | — | shipped | Routine promoted to new trust rung |
| `routine.ship.success.shipped_overview` | success | 0 | — | shipped_overview | Overview routine promoted after sim prove and human sign-off |
| `routine.ship.success.shipped_sync_orders` | success | 0 | — | shipped_sync_orders | sync_orders pinned on clean sim replay and batch sign-off |
| `routine.ship.success.rolled_back` | success | 0 | — | rolled_back | Canary telemetry trips auto-rollback |
| `routine.ship.success.queued` | success | 0 | — | queued | Enqueued for human review; zero code shipped |
| `routine.ship.success.queued_overview` | success | 0 | — | queued_overview | Overview enqueued for human review; zero code shipped |
| `routine.ship.denial.metrics` | denial | 2 | policy.authorizer | low_success | Success rate falls below 0.95 |
| `routine.ship.refusal.missing_reason`| refusal | 3 | missing_param | missing_arg | Elevation to pinned requires reason |
| `routine.ship.denial.trust` | denial | 2 | policy.trust | promotion_signoff | Pinned promotion denied without human or Tier-1 CI sign-off |
| `routine.pending.success.populated` | success | 0 | — | populated | Batch promotion candidates listed |
| `routine.pending.success.empty` | success | 0 | — | empty | No routines pending promotion |
| `routine.sweep.success.populated` | success | 0 | — | populated | Deduplication proposals generated |
| `routine.sweep.success.empty` | success | 0 | — | empty | No duplicate routines detected |
| `routine.stats.success.populated` | success | 0 | — | populated | Routine p50/p95 execution metrics |
| `routine.stats.refusal.not_found` | refusal | 3 | validation | not_found | Routine name does not exist |
| `routine.rollback.success.completed`| success | 0 | — | completed | Rollback committed as new version v6 restoring v3 state |
| `routine.rollback.denial.depth` | denial | 2 | policy.governance | depth_limit | Versioning cap on retained history: exceeds max rollback depth of 5 |
| `routine.rollback.refusal.not_found`| refusal | 3 | validation | not_found | Target version not found in history |
| `routine.retire.success.completed` | success | 0 | — | completed | Routine retired; bound ingress loudly dismantled (cron paused→dissolved by daemon, endpoint revoked) |
| `routine.retire.denial.active_deps` | denial | 2 | policy.dependency | deps_exist | In-memory routine DAG blocks retirement of active dependencies |
| `routine.retire.refusal.missing_reason` | refusal | 3 | missing_param | missing_arg | Prod retire of an operational routine demands --reason |
| `routine.retire.refusal.not_found` | refusal | 3 | validation | not_found | Target routine does not exist |

### 4.4 `api/` (9 verbs → 24 screens)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `api.sync.success.synced` | success | 0 | — | synced | Provider OpenAPI synced to catalog; sole spec-ingestion verb |
| `api.sync.denial.rate` | denial | 2 | api.quota | rate_limit | Sync call within 24h cooldown |
| `api.sync.refusal.missing_url` | refusal | 3 | missing_param | missing_arg | Upstream spec URL omitted |
| `api.diff.success.populated` | success | 0 | — | populated | Spec divergence detected |
| `api.diff.success.empty` | success | 0 | — | empty | Zero drift from active catalog |
| `api.catalog.success.populated` | success | 0 | — | populated | Imported catalog verbs listed |
| `api.catalog.success.empty` | success | 0 | — | empty | Zero APIs configured |
| `api.catalog.success.truncated` | success | 0 | — | truncated | Truncated at 500 verbs |
| `api.prove.success.passed` | success | 0 | — | passed | Rehearsal in sim verified |
| `api.prove.denial.sim_gap` | denial | 2 | policy.authorizer | sim_gap | Missing mock fixture in sim |
| `api.prove.denial.policy` | denial | 2 | policy.authorizer | forbidden | Verb egress rule rejected |
| `api.prove.crash.runtime` | crash | 4 | routine.runtime | exception | Upstream contract format failure |
| `api.ship.success.shipped` | success | 0 | — | shipped | Promoted to reviewed |
| `api.ship.success.graduated` | success | 0 | — | graduated | 100% schema match & shadow canary passed |
| `api.ship.denial.metrics` | denial | 2 | policy.authorizer | unproven | Fails synthetic contract replay |
| `api.ship.refusal.missing_reason` | refusal | 3 | missing_param | missing_arg | Missing elevation justification |
| `api.stats.success.populated` | success | 0 | — | populated | Quota usage and error metrics |
| `api.stats.refusal.not_found` | refusal | 3 | validation | not_found | Target provider not found |
| `api.retire.success.completed` | success | 0 | — | completed | API verb retired |
| `api.retire.refusal.not_found` | refusal | 3 | validation | not_found | Target verb not found |
| `api.rollback.success.completed` | success | 0 | — | completed | Reverts API spec to prior hash |
| `api.rollback.denial.depth` | denial | 2 | policy.authorizer | depth_limit | Exceeds max rollback limit of 5 |
| `api.rollback.refusal.not_found` | refusal | 3 | validation | not_found | Target version not found |
| `api.record.success.recorded` | success | 0 | — | recorded | Live response captured as JSON Schema contract |

### 4.5 `bind/` (10 verbs → 25 screens)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `bind.cron.success.bound` | success | 0 | — | bound | Schedule bound to routine |
| `bind.cron.denial.cap` | denial | 2 | policy.authorizer | cap_exceeded| Max 20 active schedules reached |
| `bind.cron.denial.interval` | denial | 2 | policy.authorizer | interval_low| Interval lower than 5-minute cap |
| `bind.cron.refusal.missing_intent` | refusal | 3 | missing_param | no_intent | Missing intent flag |
| `bind.webhook.success.bound` | success | 0 | — | bound | Inbound hook route activated |
| `bind.webhook.denial.cap` | denial | 2 | policy.authorizer | cap_exceeded| Max 50 active hooks reached |
| `bind.webhook.denial.unsigned` | denial | 2 | policy.authorizer | unsigned | Unsigned hooks rejected |
| `bind.webhook.denial.payload_size` | denial | 2 | policy.authorizer | too_large | Hook payload exceeds 64KB |
| `bind.webhook.refusal.missing_ingress`| refusal| 3 | missing_param | no_ingress | Missing public ingress URL/tunnel |
| `bind.federation.success.bound` | success | 0 | — | bound | Peer outbox siphon bound |
| `bind.federation.refusal.unversioned`| refusal| 3 | compile | no_version | Federated bind target must be versioned |
| `bind.endpoint.success.bound` | success | 0 | — | bound | Routine exposed as HTTP/MCP |
| `bind.endpoint.denial.trust` | denial | 2 | policy.trust | unpinned | Endpoint requires pinned trust |
| `bind.endpoint.denial.cap` | denial | 2 | policy.authorizer | cap_exceeded| Max 10 active endpoints reached |
| `bind.list.success.populated` | success | 0 | — | populated | Active bindings displayed |
| `bind.list.success.empty` | success | 0 | — | empty | Zero bindings active |
| `bind.inspect.success.populated` | success | 0 | — | populated | Binding configuration envelope |
| `bind.inspect.refusal.not_found` | refusal | 3 | validation | not_found | Target binding ID not found |
| `bind.pause.success.completed` | success | 0 | — | completed | Trigger paused |
| `bind.pause.success.resumed` | success | 0 | — | resumed | Trigger resumed via --resume |
| `bind.pause.refusal.not_found` | refusal | 3 | validation | not_found | Target binding ID not found |
| `bind.remove.success.completed` | success | 0 | — | completed | Trigger dismantled |
| `bind.remove.refusal.not_found` | refusal | 3 | validation | not_found | Target binding ID not found |
| `bind.keys.success.issued` | success | 0 | — | issued | API key stamped for endpoint (90d expiry) |
| `bind.keys.denial.cap` | denial | 2 | policy.authorizer | cap_exceeded| Max 25 keys reached |

### 4.6 `ping/` (5 verbs → 18 screens)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `ping.notify.success.dispatched` | success | 0 | — | dispatched | Notification dispatched |
| `ping.notify.denial.quiet_hours` | denial | 2 | policy.notify | quiet_hours | Blocked between 22:00 and 07:00 (notify engine policy) |
| `ping.notify.refusal.missing_intent` | refusal | 3 | missing_param | no_intent | Missing intent declaration |
| `ping.notify.refusal.unconfigured_channel` | refusal | 3 | policy.secrets | unconfigured_channel | Channel webhook missing in vault; fail-closed |
| `ping.notify.denial.delivery_failed` | denial | 2 | policy.notify | delivery_failed | Transport failed (HTTP 5xx/timeout/TLS); fail-closed, cites measured value |
| `ping.notify.refusal.unknown_principal` | refusal | 3 | validation | unknown_principal | Recipient principal not in agents registry |
| `ping.ask.yield.suspended` | yield | 6 | ping.ask | suspended | Human question queued with Cockpit URL; exits 6 — callers must treat as suspension, not success |
| `ping.ask.denial.options_cap` | denial | 2 | policy.notify | cap_exceeded | Exceeds 5 structured choices (option_gate) |
| `ping.ask.refusal.missing_intent` | refusal | 3 | missing_param | no_intent | Missing intent declaration |
| `ping.list.success.populated` | success | 0 | — | populated | Pending suspension questions |
| `ping.list.success.empty` | success | 0 | — | empty | Zero pending inquiries |
| `ping.resolve.success.resolved` | success | 0 | — | resolved | Choice selected; resumes task |
| `ping.resolve.success.rejected` | success | 0 | — | rejected | Deny choice selected; resumes task on the reject branch |
| `ping.resolve.denial.occ_conflict` | denial | 2 | policy.notify | occ_fence | Kernel OCC fence gate caught entity drift during suspension; resume denied |
| `ping.resolve.refusal.not_found` | refusal | 3 | validation | not_found | Invalid ask ID |
| `ping.resolve.denial.expired` | denial | 2 | policy.notify | expired | Timeout elapsed; fail-closed |
| `ping.expire.success.completed` | success | 0 | — | completed | Explicit expiration executed |
| `ping.expire.refusal.not_found` | refusal | 3 | validation | not_found | Target inquiry not found |

### 4.7 `rule/` (6 verbs → 15 screens)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `rule.show.success.populated` | success | 0 | — | populated | Compiled DDL / authorizer rules |
| `rule.show.refusal.not_found` | refusal | 3 | validation | not_found | Target rule/table not found |
| `rule.diff.success.populated` | success | 0 | — | populated | Schema/policy drift detected |
| `rule.diff.success.empty` | success | 0 | — | empty | Workspace in lockstep with rules |
| `rule.apply.success.applied` | success | 0 | — | applied | DDL applied in transaction |
| `rule.apply.success.dry_run` | success | 0 | — | dry_run | DDL impact preview on snapshot |
| `rule.apply.refusal.validation` | refusal | 3 | validation | rejected | Sub-check 2 semantic check fails |
| `rule.apply.refusal.lockfile` | refusal | 3 | lockfile_mismatch | drift | Lockfile root hash mismatch |
| `rule.validate.success.valid` | success | 0 | — | valid | Declarations pass Sub-checks 1 & 2 |
| `rule.validate.refusal.bundle_syntax` | refusal | 3 | compile | syntax | Malformed pack bundle YAML or Python syntax |
| `rule.validate.refusal.compat` | refusal | 3 | policy.pack | compat | min_kernel_version or policy version mismatch |
| `rule.validate.refusal.syntax` | refusal | 3 | compile | bad_syntax | Sub-check 1 YAML syntax failure |
| `rule.validate.refusal.semantics` | refusal | 3 | compile | circular_ref | Sub-check 2 circular dependency detected |
| `rule.plan.success.planned` | success | 0 | — | planned | Migration bundle generated (plan.json, align stub) |
| `rule.rehearse.success.rehearsed` | success | 0 | — | rehearsed | Four-phase migration rehearsed in sim (expand/align/contract/pin); pinned routines rehearsed |

### 4.8 `env/` (7 verbs → 19 screens)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `env.new.success.created` | success | 0 | — | created | New worktree namespace created |
| `env.new.denial.cap` | denial | 2 | policy.authorizer | cap_exceeded| Max 5 environments reached |
| `env.new.refusal.name_taken` | refusal | 3 | validation | collision | Environment name exists |
| `env.use.success.switched` | success | 0 | — | switched | Sticky context switched |
| `env.use.refusal.not_found` | refusal | 3 | validation | not_found | Target environment not found |
| `env.list.success.populated` | success | 0 | — | populated | Environments listed |
| `env.inspect.success.populated` | success | 0 | — | populated | Health, staleness, and drift status |
| `env.inspect.refusal.not_found` | refusal | 3 | validation | not_found | Target environment not found |
| `env.doctor.success.healthy` | success | 0 | — | healthy | Verified schema and clean worktree |
| `env.doctor.denial.drift` | denial | 2 | policy.authorizer | drift | Schema divergence detected |
| `env.merge.success.merged` | success | 0 | — | merged | DDL forwarded to production |
| `env.merge.denial.trust` | denial | 2 | policy.trust | unreviewed | Production merge requires reviewed |
| `env.merge.refusal.plan_conflict` | refusal | 3 | compile | conflict | Target schema migration plan conflict blocks DDL |
| `env.merge.refusal.lockfile` | refusal | 3 | lockfile_mismatch | drift | Lockfile out of sync |
| `env.merge.refusal.unmerged` | refusal | 3 | compile | unmerged | Git branch conflict blocks DDL forwarding |
| `env.remove.success.removed` | success | 0 | — | removed | Environment dismantled |
| `env.remove.denial.backup_unverified` | denial | 2 | policy.authorizer | backup_pending | Final prod backup push unverified; teardown ordering mandates backup first |
| `env.remove.denial.crypto_sig` | denial | 2 | policy.authorizer | confirmation | Prod requires out-of-band challenge signature |
| `env.remove.refusal.not_found` | refusal | 3 | validation | not_found | Target environment not found |

### 4.9 `sys/` (22 verbs → 64 screens)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `sys.help.success.stub` | success | 0 | — | stub | Minimalist help stub redirecting to search; host line cap in `manifest.json` `output_contract` |
| `sys.inbox.success.populated` | success | 0 | — | populated | Sensory events popped from the intake queue (cron/webhook sources; durable store TBD) |
| `sys.inbox.success.suppressed` | success | 0 | — | suppressed | Pop suppressed by an active Layer 1 claim; `suppressed` carries the held row |
| `sys.inbox.success.empty` | success | 0 | — | empty | No stimulus queued; exits clean (sensory grounding) |
| `sys.tail.success.populated` | success | 0 | — | populated | Live streaming audit records |
| `sys.tail.success.empty` | success | 0 | — | empty | No audit events within window |
| `sys.trace.success.populated` | success | 0 | — | populated | Causal DAG walk with `--explain` tree |
| `sys.trace.success.denial_trail` | success | 0 | — | denial_trail | Causal DAG walk of a denied op (`--explain`) |
| `sys.trace.success.prove` | success | 0 | — | prove | Causal DAG walk of a routine prove op |
| `sys.trace.refusal.not_found` | refusal | 3 | validation | not_found | Target operation ID missing |
| `sys.query.success.populated` | success | 0 | — | populated | SQL executed against `_audit` |
| `sys.query.success.empty` | success | 0 | — | empty | Zero matching audit rows |
| `sys.query.refusal.unparseable`| refusal | 3 | compile | bad_syntax | Malformed SQL audit query |
| `sys.replay.success.replayed` | success | 0 | — | replayed | Deterministic execution from log |
| `sys.replay.denial.external` | denial | 2 | policy.authorizer | external_op | Auto-replay of external `api.call` ops strictly forbidden (`api.replay: manual`); narrow window or re-dispatch fresh via `capcli run` — no flag bypass |
| `sys.replay.refusal.missing_from`| refusal| 3 | missing_param | missing_arg | Target timestamp or commit omitted |
| `sys.register.success.registered`| success| 0 | — | registered | Kernel-minted agent ID issued |
| `sys.register.denial.cap` | denial | 2 | policy.authorizer | cap_exceeded| Max agents exceeded |
| `sys.agents.success.populated` | success | 0 | — | populated | Registered agents listed |
| `sys.agents.success.empty` | success | 0 | — | empty | Zero registered agents |
| `sys.swarm.success.populated` | success | 0 | — | populated | Swarm nodes listed with topology mode, heartbeat, and ephemeral flag |
| `sys.swarm.success.empty` | success | 0 | — | empty | Zero swarm nodes registered at the Hub |
| `sys.swarm.success.reaped` | success | 0 | — | reaped | Expired swarm nodes reaped; agents expired and claims released per swarm.node_reap |
| `sys.revoke.success.revoked` | success | 0 | — | revoked | Agent credentials killed |
| `sys.revoke.refusal.not_found` | refusal | 3 | validation | not_found | Target agent ID not found |
| `sys.vault_set.success.vaulted` | success | 0 | — | vaulted | AES-256-GCM secret encrypted |
| `sys.vault_set.refusal.missing_val` | refusal | 3 | missing_param | missing_arg | Target secret value omitted |
| `sys.vault_import.success.imported` | success | 0 | — | imported | Scanned and bound `CAPCLI_SECRET_*` |
| `sys.vault_import.refusal.no_env_vars` | refusal | 3 | validation | not_found | No matching environment variables |
| `sys.doctor.success.nominal` | success | 0 | — | nominal | Host doctor readiness check |
| `sys.doctor.success.report` | success | 0 | — | report | Full YAML Trust Receipt |
| `sys.doctor.denial.drift` | denial | 2 | policy.authorizer | drift | Live DB differs from declaration |
| `sys.doctor.refusal.boot` | refusal | 3 | kernel.boot | missing_dep | All isolation providers failed on tier_1 (bwrap absent; container and microvm fallbacks exhausted) |
| `sys.doctor.success.clock_drift`| success| 0 | — | clock_skew | Host clock delta >500ms vs NTP (warning only) |
| `sys.doctor.panic.tamper` | panic | 5 | kernel.panic | tampered | Total media loss: ledger root + WORM checkpoint unreadable; kill_and_alert |
| `sys.doctor.success.recovery` | success | 0 | — | recovery | Break-glass recovery mode |
| `sys.doctor.refusal.lockfile` | refusal | 3 | lockfile_mismatch | drift | Lockfile root hash mismatch |
| `sys.doctor.success.quarantine_degraded` | success | 0 | — | quarantine_degraded | Row-level chain tamper: sha256 link broken at row 8,412; corrupted leaves isolated to the quarantine branch (`audit.quarantine.jsonl`); boot completes degraded (exit 0) — valid history operable, quarantined leaves fail-closed; operator clears with `sys doctor --ack-tamper` after restore + WORM re-verification |
| `sys.doctor.success.quarantine`| success | 0 | — | quarantine | Break-glass read-only quarantine ledger inspection (`CAPCLI_RECOVERY=1`); valid history verified |
| `sys.doctor.denial.thrashing` | denial | 2 | agent.thrashing| looping | 20 sustained denials in 5 minutes |
| `sys.backup.success.completed` | success | 0 | — | completed | Snapshot pushed to Git and S3 |
| `sys.backup.success.push_pending` | success | 0 | — | push_pending | Local snapshot complete; push recorded pending, retried on next push |
| `sys.recover.success.restored` | success | 0 | — | restored | Reconstructed from object store |
| `sys.recover.refusal.not_found` | refusal | 3 | validation | not_found | Recovery snapshot missing |
| `sys.recover.denial.active_locks`| denial | 2 | db.claims | active_locks | Active locks prevent state reversal |
| `sys.update.success.completed` | success | 0 | — | completed | Governed update to target; all 6 stages committed, trust rungs unchanged |
| `sys.update.denial.incompatible_downgrade` | denial | 2 | policy.update | incompatible_downgrade | Target below current schema generation; schema migrations never downgrade |
| `sys.update.refusal.unknown_stage` | refusal | 3 | validation | unknown_stage | Stage outside the 1-6 pipeline |
| `sys.init.success.initialized` | success | 0 | — | initialized | Ledger re-initialized after total media loss; dual confirmation completed |
| `sys.init.refusal.declined` | refusal | 3 | validation | declined | Operator declined the second confirmation; no state modified |
| `sys.init.denial.ledger_intact` | denial | 2 | policy.authorizer | ledger_intact | Healthy ledger refuses destructive --fresh re-init |
| `sys.vault_list.success.populated` | success | 0 | — | populated | Secret names listed; values never echoed |
| `sys.vault_list.success.empty` | success | 0 | — | empty | No secrets vaulted |
| `sys.audit_sample.success.sampled` | success | 0 | — | sampled | Cost evidence sampled from _audit; synthetic fixtures banned |
| `sys.recover.success.listed` | success | 0 | — | listed | Snapshot catalog points displayed |
| `sys.exec.success.completed` | success | 0 | — | completed | Isolated command executed in jail |
| `sys.exec.denial.sandbox` | denial | 2 | kernel.sandbox | violation | Attempted unconfined escape |
| `sys.exec.crash.runtime` | crash | 4 | routine.runtime | crash | Executable process crash |
| `sys.shim.success.deployed` | success | 0 | — | deployed | Native wrapper deployed; caller markers captured, secrets scrubbed |
| `sys.shim.denial.target_missing` | denial | 2 | kernel.shim | target_missing | Target binary missing or not executable |
| `sys.shim.crash.wrapper_deploy` | crash | 4 | kernel.shim | deploy_crash | Wrapper deploy crashed; partial wrapper torn down |
| `sys.serve.success.running` | success | 0 | — | running | IPC/WS/HTTP daemon active |
| `sys.serve.refusal.already_running`| refusal| 3 | compile | port_bound | Daemon process already running |
| `sys.serve.denial.port` | denial | 2 | db.engine | port_denied | Port 4040 binding rejected |

### 4.10 `doc/` (2 verbs → 5 screens)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `doc.read.success.populated` | success | 0 | — | populated | Full document returned bounded |
| `doc.read.success.sliced` | success | 0 | — | sliced | Progressive disclosure: leading sections under token cap; typed keyset envelope |
| `doc.read.refusal.not_found` | refusal | 3 | validation | not_found | Target document URP not found |
| `doc.outline.success.populated` | success | 0 | — | populated | Outline node tree with section indices |
| `doc.outline.refusal.not_found` | refusal | 3 | validation | not_found | Target document URP not found |

### 4.11 `pack/` (5 verbs → 14 screens)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `pack.new.success.created` | success | 0 | — | created | Blueprint scaffold committed to packs/ |
| `pack.new.refusal.name_taken` | refusal | 3 | validation | name_taken | Pack name already registered |
| `pack.new.refusal.shape_violation` | refusal | 3 | validation | shape_violation | Scaffold violates complexity or parameter bounds |
| `pack.bundle.success.packed` | success | 0 | — | packed | Bundle compiled to SHA-256 .cap archive |
| `pack.bundle.refusal.size_limit` | refusal | 3 | policy.pack | size_limit | World pack bundle exceeds 5MB ceiling |
| `pack.sync.success.synced` | success | 0 | — | synced | Registry index refreshed from capcli/registry |
| `pack.import.success.imported` | success | 0 | — | imported | Pinned bundle registered in local _packs at draft trust |
| `pack.import.refusal.checksum` | refusal | 3 | policy.pack | checksum | Bundle SHA-256 mismatch against pinned hash (wire gate) |
| `pack.scaffold.success.applied` | success | 0 | — | applied | Draft routine scaffolded from pack:// blueprint |
| `pack.scaffold.success.world` | success | 0 | — | applied | Dev environment scaffolded from pack:// world blueprint |
| `pack.scaffold.success.overview` | success | 0 | — | applied | Mandatory overview routine scaffolded (harness H6) |
| `pack.scaffold.refusal.missing_param` | refusal | 3 | missing_param | missing_param | Required pack parameter -p omitted |
| `pack.scaffold.refusal.checksum` | refusal | 3 | policy.pack | checksum | Bundle SHA-256 mismatch against registry index |
| `pack.scaffold.denial.target_exists` | denial | 2 | policy.authoring | target_exists | Target file or environment already exists |


### 4.12 `serve/` (5 verbs → 6 screens)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `serve.export.success.openapi` | success | 0 | — | exported | OpenAPI schema exported via serve export |
| `serve.export.success.mcp` | success | 0 | — | exported | MCP tool definition exported via serve export |
| `serve.start.success.started` | success | 0 | — | started | Daemon started on port 4040 |
| `serve.stop.success.stopped` | success | 0 | — | stopped | Daemon stopped; endpoints released |
| `serve.restart.success.restarted` | success | 0 | — | restarted | Daemon rebound on a new pid |
| `serve.status.success.running` | success | 0 | — | running | Daemon health, sessions, uptime |

### 4.13 `plugin/` (12 verbs → 12 screens)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `plugin.install.success.installed` | success | 0 | — | installed | Plugin installed from registry source |
| `plugin.link.success.linked` | success | 0 | — | linked | Dev plugin hot-reload symlink linked |
| `plugin.unlink.success.unlinked` | success | 0 | — | unlinked | Dev plugin symlink detached |
| `plugin.list.success.populated` | success | 0 | — | populated | Installed plugins listed with rung and generation |
| `plugin.inspect.success.inspected` | success | 0 | — | inspected | Plugin preflight envelope: commands, permissions, noun |
| `plugin.update.success.updated` | success | 0 | — | updated | Plugin updated to new generation via atomic swap |
| `plugin.enable.success.enabled` | success | 0 | — | enabled | Plugin projection mounted; noun live |
| `plugin.disable.success.disabled` | success | 0 | — | disabled | Plugin projection unmounted; noun parked |
| `plugin.uninstall.success.uninstalled` | success | 0 | — | uninstalled | Plugin uninstalled; state retained for GC |
| `plugin.search.success.matched` | success | 0 | — | matched | Registry search returned ranked matches |
| `plugin.logs.success.tailed` | success | 0 | — | tailed | Plugin ring-buffer logs tailed |
| `plugin.doctor.success.healthy` | success | 0 | — | healthy | Tri-Jail probes pass; syscall 42 trapping asserted |
---

### 4.14 `ws/` (4 verbs → 5 screens)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `ws.peers.success.empty` | success | 0 | — | empty | Zero federated peers registered |
| `ws.peers.success.populated` | success | 0 | — | populated | Federated peers listed with rung and allowlist state |
| `ws.dial.success.connected` | success | 0 | — | connected | Federation session opened to peer |
| `ws.status.success.running` | success | 0 | — | running | Active federation sessions and transports |
| `ws.cassettes.success.populated` | success | 0 | — | populated | Recorded peer replay cassettes listed |
---

### 4.15 `storage/` (5 verbs → 5 screens)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `storage.put.success.put` | success | 0 | — | put | Object stored; sha256 recorded |
| `storage.get.success.retrieved` | success | 0 | — | retrieved | Object fetched to disk via --out |
| `storage.url.success.presigned` | success | 0 | — | presigned | Time-boxed presigned URL issued |
| `storage.list.success.populated` | success | 0 | — | populated | Objects listed under prefix |
| `storage.remove.success.removed` | success | 0 | — | removed | Object tombstoned; prior versions retained |
---

## 5. Canonical Screen Fixtures

Every fixture is a `wireframe/v1` root in `CliEnvelope` shape (envelope law: kernel.md#Diagnostic-output-law): `$schema`, `id`, `command`, `context {env, tier, trust}`, optional `audit_op`, optional `attention`, `archetype`, `component`. Exactly one component per screen:

- `diagnostic` — states denial, refusal, crash, panic, yield (exits 2, 3, 4, 5, 6)
- `tree` — hierarchies, causal DAGs, inspection envelopes
- `receipt` — key-value summaries, reports, dry-run plans
- `document` — prose slices, keyset envelopes, help

Success screens classify by content: key-value summaries are `receipt`, hierarchies are `tree`, prose slices and help are `document`. The exit code derives from the `id` state segment; fixtures carry no `exit_code` and no `state_modified`. Carets, indents, branch glyphs, dividers, and key alignment are renderer output computed from component data; fixtures store none of them. The renderer (HTML canvas or Rust test harness) consumes the component and produces the terminal output. No separate `.txt` files exist in the repo. Each fixture below sits beside the terminal output its component renders; the harness asserts that output byte-for-byte (§6.2).

---

### 5.1 AST Blast-Radius Denial (`screens/run/sql/run.sql.denial.ast.json`)

Fixture (`wireframe/v1`):

```json
{
  "$schema": "wireframe/v1",
  "id": "run.sql.denial.ast",
  "scenario": {
    "db_urp": "db://orders",
    "intent": "batch ship"
  },
  "target": {
    "$slot": "db_urp",
    "$from": "scenario.db_urp",
    "$example": "db://orders"
  },
  "command": {
    "$interpolate": "capcli sql \"UPDATE orders SET status = 'shipped' WHERE status = 'processing'\" -m \"{{intent}}\"",
    "$bindings": {
      "intent": "scenario.intent"
    },
    "$example": "capcli sql \"UPDATE orders SET status = 'shipped' WHERE status = 'processing'\" -m \"batch ship\""
  },
  "elapsed_ms": {
    "$slot": "elapsed_ms",
    "$from": "live.elapsed_ms",
    "$type": "integer",
    "$example": 54
  },
  "context": {
    "env": "dev",
    "tier": "tier_1",
    "trust": "draft"
  },
  "audit_op": {
    "$slot": "audit_op",
    "$from": "live.audit_op",
    "$example": "op_9f2e"
  },
  "archetype": "diagnostic",
  "component": {
    "rule": "policy.query.update_delete.require_limit",
    "domain": "policy.ast",
    "layer": "AST",
    "culprit": {
      "$slot": "culprit",
      "$from": "live.culprit",
      "$example": "No LIMIT clause. Blast radius unbounded."
    },
    "measured": {
      "$slot": "measured",
      "$from": "live.measured",
      "$example": "matches potentially 847 rows (cap: 100)"
    },
    "remedy": "add LIMIT, or target specific primary key",
    "span": {
      "source": {
        "$slot": "source",
        "$from": "live.span.source",
        "$example": "UPDATE orders SET status = 'shipped' WHERE status = 'processing'"
      },
      "highlight": {
        "$slot": "highlight",
        "$from": "live.span.highlight",
        "$example": "UPDATE orders"
      }
    }
  }
}
```

Rendered output (what the HTML canvas and Rust harness produce):

```text
[dev:tier_1]  ✗  exit 2

  FAIL  policy.query.update_delete.require_limit
        UPDATE orders SET status = 'shipped' WHERE status = 'processing'
                                                                   ^^^^^^
        No LIMIT clause. Blast radius unbounded.

  audit_op: op_9f2e
  state_modified: false
  layer: AST
  measured: matches potentially 847 rows (cap: 100)
  remedy: add LIMIT, or target specific primary key
```

---

### 5.2 Causal DAG Tree Walk (`screens/sys/trace/sys.trace.success.populated.json`)

Fixture (`wireframe/v1`):

```json
{
  "$schema": "wireframe/v1",
  "id": "sys.trace.success.populated",
  "scenario": {
    "session_id": "ses_a992f",
    "root_intent": "fulfill urgent pending orders",
    "trace_op": "op_7c4f"
  },
  "target": {
    "$slot": "trace_op",
    "$from": "scenario.trace_op",
    "$example": "op_7c4f"
  },
  "command": {
    "$interpolate": "capcli sys audit trace {{trace_op}} --explain",
    "$bindings": {
      "trace_op": "scenario.trace_op"
    },
    "$example": "capcli sys audit trace op_7c4f --explain"
  },
  "elapsed_ms": {
    "$slot": "elapsed_ms",
    "$from": "live.elapsed_ms",
    "$type": "integer",
    "$example": 1268
  },
  "context": {
    "env": "dev",
    "tier": "tier_1",
    "trust": "draft",
    "data_shape": {
      "$slot": "data_shape",
      "$from": "context.data_shape",
      "$example": "populated"
    }
  },
  "archetype": "tree",
  "component": {
    "title": {
      "$interpolate": "Causal DAG Trace ({{trace_op}})",
      "$bindings": {
        "trace_op": "scenario.trace_op"
      },
      "$example": "Causal DAG Trace (op_7c4f)"
    },
    "root": {
      "$interpolate": "{{session_id}} session.start \"{{root_intent}}\"",
      "$bindings": {
        "session_id": "scenario.session_id",
        "root_intent": "scenario.root_intent"
      },
      "$example": "ses_a992f session.start \"fulfill urgent pending orders\""
    },
    "nodes": [
      {
        "label": {
          "$slot": "n0",
          "$from": "live.trace.nodes[0].label",
          "$example": "op_9f2c routine.dispatch_order@4"
        },
        "children": [
          {
            "label": {
              "$slot": "n0c0",
              "$from": "live.trace.nodes[0].children[0].label",
              "$example": "op_9f2d db.query (orders) ✓ [allowed] 12ms"
            },
            "children": []
          },
          {
            "label": {
              "$slot": "n0c1",
              "$from": "live.trace.nodes[0].children[1].label",
              "$example": "op_7c4f api.call (fedex.ship) ✓ [allowed] 340ms"
            },
            "children": [
              {
                "label": {
                  "$slot": "n0c1c0",
                  "$from": "live.trace.nodes[0].children[1].children[0].label",
                  "$example": "tracking 794644790133"
                },
                "children": []
              }
            ]
          },
          {
            "label": {
              "$slot": "n0c2",
              "$from": "live.trace.nodes[0].children[2].label",
              "$example": "op_9f2f db.execute (orders) ✓ [allowed] 18ms"
            },
            "children": [
              {
                "label": {
                  "$slot": "n0c2c0",
                  "$from": "live.trace.nodes[0].children[2].children[0].label",
                  "$example": "status = 'shipped' (1 row)"
                },
                "children": []
              }
            ]
          }
        ]
      }
    ],
    "footer": {
      "Root Intent": {
        "$interpolate": "\"{{root_intent}}\"",
        "$bindings": {
          "root_intent": "scenario.root_intent"
        },
        "$example": "\"fulfill urgent pending orders\""
      },
      "Authority": {
        "$slot": "authority",
        "$from": "live.trace.footer.authority",
        "$example": "user:root (via agt_7f3k)"
      },
      "Integrity": {
        "$slot": "integrity",
        "$from": "live.trace.footer.integrity",
        "$example": "valid hash link (chain verified)"
      }
    }
  }
}
```

Rendered output:

```text
[dev:tier_1]  Causal DAG Trace (op_7c4f)

  ses_a992f  session.start        "fulfill urgent pending orders"
  └── op_9f2c  routine.dispatch_order@4
        ├── op_9f2d  db.query (orders)         ✓ [allowed]  12ms
        ├── op_7c4f  api.call (fedex.ship)     ✓ [allowed]  340ms
        │     └── tracking  794644790133
        └── op_9f2f  db.execute (orders)       ✓ [allowed]  18ms
              └── status = 'shipped' (1 row)

  Root Intent: "fulfill urgent pending orders"
  Authority:   user:root (via agt_7f3k)
  Integrity:   valid hash link (chain verified)
```

---

### 5.3 YAML Trust Receipt (`screens/sys/doctor/sys.doctor.success.report.json`)

Fixture (`wireframe/v1`):

```json
{
  "$schema": "wireframe/v1",
  "id": "sys.doctor.success.report",
  "scenario": {
    "host": "host"
  },
  "target": {
    "$slot": "host",
    "$from": "scenario.host",
    "$example": "host"
  },
  "command": {
    "$interpolate": "capcli sys doctor --report",
    "$bindings": {},
    "$example": "capcli sys doctor --report"
  },
  "elapsed_ms": {
    "$slot": "elapsed_ms",
    "$from": "live.elapsed_ms",
    "$type": "integer",
    "$example": 1647
  },
  "context": {
    "env": "prod",
    "tier": "tier_1",
    "trust": "reviewed"
  },
  "archetype": "receipt",
  "component": {
    "title": {
      "$slot": "title",
      "$from": "live.title",
      "$example": "trust_receipt"
    },
    "groups": [
      {
        "title": {
          "$slot": "title_2",
          "$from": "live.groups[0].title",
          "$example": "trust_receipt"
        },
        "fields": {
          "status": {
            "$slot": "status",
            "$from": "live.groups[0].fields.status",
            "$example": "nominal (witness anchoring pending)"
          },
          "host_tier": {
            "$slot": "host_tier",
            "$from": "live.groups[0].fields.host_tier",
            "$example": "tier_1 (hardened Linux namespaces)"
          },
          "permitted_envs": {
            "$slot": "permitted_envs",
            "$from": "live.groups[0].fields.permitted_envs",
            "$example": "dev, sim, prod"
          },
          "workspace": {
            "$slot": "workspace",
            "$from": "live.groups[0].fields.workspace",
            "$example": "envs/prod/workspace.db"
          },
          "ledger_root_hash": {
            "$slot": "ledger_root_hash",
            "$from": "live.groups[0].fields.ledger_root_hash",
            "$example": "sha256:7f9a1b2c4d8e001fa882bc19488a09b2e4f019c"
          },
          "witness_store": {
            "$slot": "witness_store",
            "$from": "live.groups[0].fields.witness_store",
            "$example": "not configured — S3/R2 WORM probe unreachable (credentials absent from vault)"
          },
          "worm_checkpoint": {
            "$slot": "worm_checkpoint",
            "$from": "live.groups[0].fields.worm_checkpoint",
            "$example": "pending — ledger root is local-only until the first object-store anchor"
          },
          "audited_events": {
            "$slot": "audited_events",
            "$from": "live.groups[0].fields.audited_events",
            "$example": "14290 committed to _audit"
          },
          "policy_denials": {
            "$slot": "policy_denials",
            "$from": "live.groups[0].fields.policy_denials",
            "$example": "18 (intercepted pre-execution; state untouched)"
          },
          "unaudited_writes": {
            "$slot": "unaudited_writes",
            "$from": "live.groups[0].fields.unaudited_writes",
            "$example": "0"
          },
          "secret_leaks": {
            "$slot": "secret_leaks",
            "$from": "live.groups[0].fields.secret_leaks",
            "$example": "0"
          },
          "pinned_routines": {
            "$slot": "pinned_routines",
            "$from": "live.groups[0].fields.pinned_routines",
            "$example": "32"
          },
          "active_triggers": {
            "$slot": "active_triggers",
            "$from": "live.groups[0].fields.active_triggers",
            "$example": "4 crons, 3 webhooks, 1 endpoint"
          },
          "sleep_score": {
            "$slot": "sleep_score",
            "$from": "live.groups[0].fields.sleep_score",
            "$example": "100%"
          }
        }
      }
    ]
  }
}
```

Rendered output:

```text
[prod:tier_1]  capcli 0.4.2

trust_receipt:
  status:            nominal (witness anchoring pending)
  host_tier:         tier_1 (hardened Linux namespaces)
  workspace:         envs/prod/workspace.db
  ledger_root_hash:  sha256:7f9a1b2c4d8e001fa882bc19488a09b2e4f019c
  witness_store:     not configured — S3/R2 WORM probe unreachable (credentials absent from vault)
  worm_checkpoint:   pending — ledger root is local-only until the first object-store anchor
  audited_events:    14290 committed to _audit
  policy_denials:    18 (intercepted pre-execution; state untouched)
  unaudited_writes:  0
  secret_leaks:      0
  pinned_routines:   32
  active_triggers:   4 crons, 3 webhooks, 1 endpoint
  sleep_score:       100%
```

---

### 5.4 Pre-Flight Routine Inspection Envelope (`screens/run/inspect/run.inspect.success.routine.json`)

Fixture (`wireframe/v1`):

```json
{
  "$schema": "wireframe/v1",
  "id": "run.inspect.success.routine",
  "scenario": {
    "routine_urp": "cap://dispatch_order@4"
  },
  "target": {
    "$slot": "routine_urp",
    "$from": "scenario.routine_urp",
    "$example": "cap://dispatch_order@4"
  },
  "command": {
    "$interpolate": "capcli inspect {{routine_urp}}",
    "$bindings": {
      "routine_urp": "scenario.routine_urp"
    },
    "$example": "capcli inspect cap://dispatch_order@4"
  },
  "elapsed_ms": {
    "$slot": "elapsed_ms",
    "$from": "live.elapsed_ms",
    "$type": "integer",
    "$example": 2270
  },
  "context": {
    "env": "dev",
    "tier": "tier_1",
    "trust": "pinned",
    "data_shape": {
      "$slot": "data_shape",
      "$from": "context.data_shape",
      "$example": "populated"
    }
  },
  "archetype": "receipt",
  "component": {
    "title": null,
    "groups": [
      {
        "fields": {
          "trust": {
            "$slot": "trust",
            "$from": "live.groups[0].fields.trust",
            "$example": "pinned"
          },
          "runtime": {
            "$slot": "runtime",
            "$from": "live.groups[0].fields.runtime",
            "$example": "typescript (bun)"
          },
          "params": {
            "$slot": "params",
            "$from": "live.groups[0].fields.params",
            "$example": "order_id: string, carrier: string"
          },
          "description": {
            "$slot": "description",
            "$from": "live.groups[0].fields.description",
            "$example": "\"Dispatch paid order to carrier and update status\""
          }
        }
      },
      {
        "fields": {
          "limits": {
            "$slot": "limits",
            "$from": "live.groups[1].fields.limits",
            "$example": "50 fuel declared · 300s watchdog · 500 result tokens"
          }
        }
      },
      {
        "lines": [
          {
            "$slot": "lines_0",
            "$from": "live.groups[2].lines[0]",
            "$example": "manifest:"
          },
          {
            "$slot": "lines_1",
            "$from": "live.groups[2].lines[1]",
            "$example": "1. db.query    orders (read)"
          },
          {
            "$slot": "lines_2",
            "$from": "live.groups[2].lines[2]",
            "$example": "2. api.call    logistics.shipments.create"
          },
          {
            "$slot": "lines_3",
            "$from": "live.groups[2].lines[3]",
            "$example": "3. db.execute  orders (write)"
          }
        ]
      },
      {
        "fields": {
          "fuel_declared": {
            "$slot": "fuel_declared",
            "$from": "live.groups[3].fields.fuel_declared",
            "$example": "50"
          },
          "session_fuel_remaining": {
            "$slot": "session_fuel_remaining",
            "$from": "live.groups[3].fields.session_fuel_remaining",
            "$example": "80400"
          },
          "cadence_status": {
            "$slot": "cadence_status",
            "$from": "live.groups[3].fields.cadence_status",
            "$example": "nominal"
          },
          "ceiling_status": {
            "$slot": "ceiling_status",
            "$from": "live.groups[3].fields.ceiling_status",
            "$example": "nominal"
          },
          "can_invoke_now": {
            "$slot": "can_invoke_now",
            "$from": "live.groups[3].fields.can_invoke_now",
            "$example": "true"
          },
          "tightest_constraint": {
            "$slot": "tightest_constraint",
            "$from": "live.groups[3].fields.tightest_constraint",
            "$example": "null"
          }
        },
        "lines": [
          {
            "$slot": "lines_4",
            "$from": "live.groups[3].lines[0]",
            "$example": "budget_status:"
          }
        ]
      },
      {
        "fields": {
          "max_nesting_depth": {
            "$slot": "max_nesting_depth",
            "$from": "live.groups[4].fields.max_nesting_depth",
            "$example": "5"
          },
          "budget_inheritance": {
            "$slot": "budget_inheritance",
            "$from": "live.groups[4].fields.budget_inheritance",
            "$example": "min"
          },
          "child_routines": {
            "$slot": "child_routines",
            "$from": "live.groups[4].fields.child_routines",
            "$example": "[]"
          }
        },
        "lines": [
          {
            "$slot": "lines_5",
            "$from": "live.groups[4].lines[0]",
            "$example": "composition:"
          }
        ]
      },
      {
        "fields": {
          "total_runs": {
            "$slot": "total_runs",
            "$from": "live.groups[5].fields.total_runs",
            "$example": "214"
          },
          "success_rate": {
            "$slot": "success_rate",
            "$from": "live.groups[5].fields.success_rate",
            "$example": "99.1%"
          },
          "p50_duration": {
            "$slot": "p50_duration",
            "$from": "live.groups[5].fields.p50_duration",
            "$example": "340ms"
          },
          "p95_duration": {
            "$slot": "p95_duration",
            "$from": "live.groups[5].fields.p95_duration",
            "$example": "890ms"
          },
          "last_run_at": {
            "$slot": "last_run_at",
            "$from": "live.groups[5].fields.last_run_at",
            "$example": "2m ago"
          }
        },
        "lines": [
          {
            "$slot": "lines_6",
            "$from": "live.groups[5].lines[0]",
            "$example": "stats:"
          }
        ]
      }
    ]
  }
}
```

Rendered output:

```text
[dev:tier_1]  capcli inspect cap://dispatch_order@4

  trust:       pinned
  runtime:     typescript (bun)
  params:      order_id: string, carrier: string
  description: "Dispatch paid order to carrier and update status"

  limits:      8 ops · 15s · 500 result tokens

  manifest:
    1. db.query    orders (read)
    2. api.call    logistics.shipments.create
    3. db.execute  orders (write)

  budget_status:
    can_invoke_now:             true
    session_ops_remaining:      488
    session_duration_remaining: 555000ms
    session_fuel_remaining:     80400
    session_egress_remaining:   4181824 bytes
    session_rate_remaining:     287
    tightest_constraint:        null

  composition:
    max_nesting_depth:   5
    budget_inheritance:  min
    child_routines:      []

  stats:
    total_runs:    214
    success_rate:  99.1%
    p50_duration:  340ms
    p95_duration:  890ms
    last_run_at:   2m ago
```

---

### 5.5 Authorizer Denial of Raw DDL for Reviewed Caller (`screens/run/sql/run.sql.denial.authorizer_reviewed.json`)

Fixture (`wireframe/v1`):

```json
{
  "$schema": "wireframe/v1",
  "archetype": "diagnostic",
  "audit_op": {
    "$example": "op_9f2m",
    "$from": "live.audit_op",
    "$slot": "audit_op"
  },
  "command": {
    "$bindings": {},
    "$example": "capcli sql \"ALTER TABLE orders ADD COLUMN rush boolean\" --dry-run",
    "$interpolate": "capcli sql \"ALTER TABLE orders ADD COLUMN rush boolean\" --dry-run"
  },
  "component": {
    "culprit": {
      "$example": "Raw DDL denied at the C authorizer for reviewed principals; raw DDL is denied for draft and reviewed alike.",
      "$from": "live.culprit",
      "$slot": "culprit"
    },
    "domain": "policy.authorizer",
    "layer": "authorizer",
    "measured": {
      "$example": "statement rejected at prepare; 0 rows touched",
      "$from": "live.measured",
      "$slot": "measured"
    },
    "remedy": "declare the column in schema.yaml and ship it via the 4-phase migration pipeline (rule plan -> rule rehearse in sim -> rule apply schema)",
    "rule": "policy.authorizer.alter_table",
    "span": {
      "highlight": {
        "$example": "ALTER TABLE",
        "$from": "live.span.highlight",
        "$slot": "highlight"
      },
      "source": {
        "$example": "ALTER TABLE orders ADD COLUMN rush boolean",
        "$from": "live.span.source",
        "$slot": "source"
      }
    }
  },
  "context": {
    "env": "dev",
    "tier": "tier_1",
    "trust": "reviewed"
  },
  "elapsed_ms": {
    "$example": 121,
    "$from": "live.elapsed_ms",
    "$slot": "elapsed_ms",
    "$type": "integer"
  },
  "id": "run.sql.denial.authorizer_reviewed",
  "scenario": {
    "db_urp": "db://orders"
  },
  "target": {
    "$example": "db://orders",
    "$from": "scenario.db_urp",
    "$slot": "db_urp"
  }
}
```

Rendered output:

```text
[dev:tier_1]  denial  exit 2

  error[policy.authorizer]: raw DDL denied
   --> statement: ALTER TABLE orders ADD COLUMN rush boolean
    |
  culprit:  Raw DDL denied at the C authorizer for reviewed principals; raw DDL is denied for draft and reviewed alike.
  measured: statement rejected at prepare; 0 rows touched
  remedy:   declare the column in schema.yaml and ship it via the 4-phase migration pipeline
            (rule plan -> rule rehearse in sim -> rule apply schema)

  state_modified: false
```

---

### 5.6 Agent Thrashing Denial (`screens/sys/doctor/sys.doctor.denial.thrashing.json`)

Fixture (`wireframe/v1`):

```json
{
  "$schema": "wireframe/v1",
  "id": "sys.doctor.denial.thrashing",
  "scenario": {
    "host": "host"
  },
  "target": {
    "$slot": "host",
    "$from": "scenario.host",
    "$example": "host"
  },
  "command": {
    "$interpolate": "capcli sys doctor",
    "$bindings": {},
    "$example": "capcli sys doctor"
  },
  "elapsed_ms": {
    "$slot": "elapsed_ms",
    "$from": "live.elapsed_ms",
    "$type": "integer",
    "$example": 115
  },
  "context": {
    "env": "dev",
    "tier": "tier_1",
    "trust": "reviewed"
  },
  "archetype": "diagnostic",
  "component": {
    "domain": "agent.thrashing",
    "layer": "governance",
    "culprit": {
      "$slot": "culprit",
      "$from": "live.culprit",
      "$example": "agent agt_7f3k stuck in repetitive denial loop (rule: policy.query.update_delete.require_limit, target: db://orders)"
    },
    "measured": {
      "$slot": "measured",
      "$from": "live.measured",
      "$example": "denials_last_5m: 22 (threshold: 20)"
    },
    "remedy": "harness execution throttled; escalate to human or inspect remedy payload",
    "agent": {
      "$slot": "agent",
      "$from": "live.agent",
      "$example": "agt_7f3k"
    },
    "denials_last_5m": {
      "$slot": "denials_last_5m",
      "$from": "live.denials_last_5m",
      "$example": "22"
    },
    "rule_hit": {
      "$slot": "rule_hit",
      "$from": "live.rule_hit",
      "$example": "policy.query.update_delete.require_limit"
    },
    "target": {
      "$slot": "target",
      "$from": "live.target",
      "$example": "db://orders"
    },
    "harness_status": {
      "$slot": "harness_status",
      "$from": "live.harness_status",
      "$example": "stuck in repetitive denial loop"
    }
  }
}
```

Rendered output:

```text
[dev:tier_1]  ⚠  agent.thrashing

  agent:           agt_7f3k
  denials_last_5m: 22
  rule_hit:        policy.query.update_delete.require_limit
  target:          db://orders
  harness_status:  stuck in repetitive denial loop

  state_modified:  false
  layer:           governance
  remedy:          harness execution throttled; escalate to human or inspect remedy payload
```

---

### 5.7 Missing Vault Secret with Cockpit URL (`screens/run/execute/run.execute.refusal.missing_secret.json`)

Fixture (`wireframe/v1`):

```json
{
  "$schema": "wireframe/v1",
  "id": "run.execute.refusal.missing_secret",
  "scenario": {
    "routine_urp": "cap://stripe.refund_charge",
    "charge_id": "ch_1F2a9b",
    "amount_cents": "8400",
    "intent": "refund duplicate charge"
  },
  "target": {
    "$slot": "routine_urp",
    "$from": "scenario.routine_urp",
    "$example": "cap://stripe.refund_charge"
  },
  "command": {
    "$interpolate": "capcli run {{routine_urp}} -p charge_id={{charge_id}} -p amount_cents={{amount_cents}} -m \"{{intent}}\"",
    "$bindings": {
      "routine_urp": "scenario.routine_urp",
      "amount_cents": "scenario.amount_cents",
      "charge_id": "scenario.charge_id",
      "intent": "scenario.intent"
    },
    "$example": "capcli run cap://stripe.refund_charge -p charge_id=ch_1F2a9b -p amount_cents=8400 -m \"refund duplicate charge\""
  },
  "elapsed_ms": {
    "$slot": "elapsed_ms",
    "$from": "live.elapsed_ms",
    "$type": "integer",
    "$example": 294
  },
  "context": {
    "env": "dev",
    "tier": "tier_1",
    "trust": "reviewed"
  },
  "archetype": "diagnostic",
  "component": {
    "rule": "policy.secrets.missing",
    "domain": "policy.secrets",
    "layer": "vault",
    "culprit": {
      "$slot": "culprit",
      "$from": "live.culprit",
      "$example": "Secret 'stripe_secret_key' absent from vault and process env (CAPCLI_SECRET_* checked before suspension)."
    },
    "lines": [
      {
        "$slot": "lines_0",
        "$from": "live.lines[0]",
        "$example": "vault:// handles resolve at trust >= reviewed \u2014 floor passed, no trust denial"
      },
      {
        "$slot": "lines_1",
        "$from": "live.lines[1]",
        "$example": "headless execution suspends at the pre-call check (exit 3)"
      }
    ],
    "remedy": "Execution suspends (exit 3). The operator injects the value out-of-band \u2014 pipe it to `capcli sys vault set stripe_secret_key --in @-` (stdin, never argv), bind `CAPCLI_SECRET_STRIPE_SECRET_KEY` in the harness env, or use external client RPC \u2014 then the command is re-run. The agent passes only the opaque vault://stripe_secret_key handle; plaintext never enters agent context or process argv.",
    "capability": {
      "$slot": "routine_urp_2",
      "$from": "scenario.routine_urp",
      "$example": "cap://stripe.refund_charge"
    },
    "secret_ref": {
      "$slot": "secret_ref",
      "$from": "live.secret_ref",
      "$example": "vault://stripe_secret_key"
    }
  },
  "trailer": {
    "prompt": "doc://prompts/budget/execution_starved#1",
    "reason": {
      "$slot": "reason",
      "$from": "live.trailer.reason",
      "$example": "missing secret refusal: vault credential absent"
    },
    "serve": {
      "$slot": "serve",
      "$from": "live.trailer.serve",
      "$example": "L1"
    }
  }
}
```

Rendered output:

```text
[dev:tier_1]  ✗  exit 3

  FAIL  policy.secrets.missing
        capability: cap://stripe.refund_charge
        secret_ref: vault://stripe_secret_key

        Credential 'stripe_secret_key' not found in vault.

  state_modified: false
  layer: vault
  remedy: prompt human supervisor to inject credential via Cockpit (http://127.0.0.1:4040/vault)
```

---

### 5.8 Network Jail Syscall 42 Trapping (`screens/run/execute/run.execute.denial.network_jail.json`)

Fixture (`wireframe/v1`):

```json
{
  "$schema": "wireframe/v1",
  "id": "run.execute.denial.network_jail",
  "scenario": {
    "routine_urp": "cap://sneaky_exfil@1",
    "db_host": "10.0.0.5:5432",
    "intent": "replicate orders to analytics host"
  },
  "target": {
    "$slot": "routine_urp",
    "$from": "scenario.routine_urp",
    "$example": "cap://sneaky_exfil@1"
  },
  "command": {
    "$interpolate": "capcli run {{routine_urp}} -p db_host={{db_host}} -m \"{{intent}}\"",
    "$bindings": {
      "routine_urp": "scenario.routine_urp",
      "db_host": "scenario.db_host",
      "intent": "scenario.intent"
    },
    "$example": "capcli run cap://sneaky_exfil@1 -p db_host=10.0.0.5:5432 -m \"replicate orders to analytics host\""
  },
  "elapsed_ms": {
    "$slot": "elapsed_ms",
    "$from": "live.elapsed_ms",
    "$type": "integer",
    "$example": 73
  },
  "context": {
    "env": "dev",
    "tier": "tier_1",
    "trust": "draft"
  },
  "archetype": "diagnostic",
  "component": {
    "rule": "kernel.network.jail",
    "domain": "kernel.sandbox",
    "layer": "sandbox",
    "culprit": {
      "$interpolate": "Raw connect() to {{db_host}} trapped by seccomp-bpf filter (syscall 42).",
      "$bindings": {
        "db_host": "scenario.db_host"
      },
      "$example": "Raw connect() to 10.0.0.5:5432 trapped by seccomp-bpf filter (syscall 42)."
    },
    "remedy": "use ctx.api.call with an activated catalog verb",
    "target": {
      "$slot": "db_host",
      "$from": "scenario.db_host",
      "$example": "10.0.0.5:5432"
    },
    "caller": {
      "$slot": "caller",
      "$from": "live.caller",
      "$example": "routines/sneaky_exfil.py"
    },
    "lines": [
      {
        "$slot": "lines_0",
        "$from": "live.lines[0]",
        "$example": "syscall 42 (connect) trapped by seccomp-bpf"
      }
    ]
  },
  "trailer": {
    "prompt": "doc://prompts/budget/execution_starved#1",
    "reason": {
      "$slot": "reason",
      "$from": "live.trailer.reason",
      "$example": "network jail denial: sandbox egress trapped"
    },
    "serve": {
      "$slot": "serve",
      "$from": "live.trailer.serve",
      "$example": "L1"
    }
  }
}
```

Rendered output:

```text
[dev:tier_1]  ✗  exit 2

  FAIL  kernel.network.jail
        syscall 42 (connect) trapped by seccomp-bpf
        target: 10.0.0.5:5432
        caller: routines/sneaky_exfil.py

  state_modified: false
  layer: sandbox
  remedy: use ctx.api.call with an activated catalog verb
```

---

### 5.9 Quota Yield Frame Suspension (`screens/run/execute/run.execute.yield.quota.json`)

Fixture (`wireframe/v1`):

```json
{
  "$schema": "wireframe/v1",
  "id": "run.execute.yield.quota",
  "scenario": {
    "routine_urp": "cap://broadcast_newsletter@2",
    "routine_name": "broadcast_newsletter",
    "routine_version": 2,
    "audience": "followers",
    "intent": "daily digest broadcast"
  },
  "target": {
    "$slot": "routine_urp",
    "$from": "scenario.routine_urp",
    "$example": "cap://broadcast_newsletter@2"
  },
  "command": {
    "$interpolate": "capcli run {{routine_urp}} -p audience={{audience}} -m \"{{intent}}\"",
    "$bindings": {
      "routine_urp": "scenario.routine_urp",
      "audience": "scenario.audience",
      "intent": "scenario.intent"
    },
    "$example": "capcli run cap://broadcast_newsletter@2 -p audience=followers -m \"daily digest broadcast\""
  },
  "elapsed_ms": {
    "$slot": "elapsed_ms",
    "$from": "live.elapsed_ms",
    "$type": "integer",
    "$example": 651
  },
  "context": {
    "env": "prod",
    "tier": "tier_1",
    "trust": "pinned"
  },
  "archetype": "diagnostic",
  "component": {
    "rule": "policy.api.quota_exhausted",
    "domain": "api.quota",
    "culprit": {
      "$slot": "culprit",
      "$from": "live.culprit",
      "$example": "Provider quota exhausted: threads has 0/50 tokens left in the 24h rolling window."
    },
    "remedy": "task safely yielded; daemon will auto-resume at reset_at",
    "tokens_left": {
      "$slot": "tokens_left",
      "$from": "live.tokens_left",
      "$example": "0 / 50"
    },
    "reset_at": {
      "$slot": "reset_at",
      "$from": "live.reset_at",
      "$example": "18:00:00 UTC (in 4h 12m)"
    },
    "suspended_frame": {
      "$slot": "frame_id",
      "$from": "live.frame_id",
      "$example": "task_99a8b1"
    },
    "provider": {
      "$slot": "provider",
      "$from": "live.provider",
      "$example": "threads"
    },
    "verb": {
      "$slot": "api_verb",
      "$from": "live.api_verb",
      "$example": "threads.create_media_post"
    },
    "layer": "quota",
    "lines": [
      {
        "$interpolate": "routine {{routine_name}}@{{routine_version}} ({{frame_id}})",
        "$bindings": {
          "routine_name": "scenario.routine_name",
          "routine_version": "scenario.routine_version",
          "frame_id": "live.frame_id"
        },
        "$example": "routine broadcast_newsletter@2 (frame_018)"
      }
    ]
  }
}
```

Rendered output:

```text
[prod:tier_1]  ✗  exit 6

  YIELD  policy.api.quota_exhausted
         routine broadcast_newsletter@2 (frame_018)
         provider: threads
         verb:     threads.create_media_post

  state_modified:  false
  layer:           quota
  tokens_left:     0 / 50 (24h window)
  reset_at:        18:00:00 UTC (in 4h 12m)
  suspended_frame: task_99a8b1
  remedy:          task safely yielded; daemon will auto-resume at reset_at
```

---

### 5.10 NTP Clock Drift Diagnostic Warning (`screens/sys/doctor/sys.doctor.success.clock_drift.json`)

Fixture (`wireframe/v1`):

```json
{
  "$schema": "wireframe/v1",
  "id": "sys.doctor.success.clock_drift",
  "scenario": {
    "host": "host"
  },
  "target": {
    "$slot": "host",
    "$from": "scenario.host",
    "$example": "host"
  },
  "command": {
    "$interpolate": "capcli sys doctor",
    "$bindings": {},
    "$example": "capcli sys doctor"
  },
  "elapsed_ms": {
    "$slot": "elapsed_ms",
    "$from": "live.elapsed_ms",
    "$type": "integer",
    "$example": 2195
  },
  "context": {
    "env": "dev",
    "tier": "tier_1",
    "trust": "reviewed",
    "data_shape": {
      "$slot": "data_shape",
      "$from": "context.data_shape",
      "$example": "populated"
    }
  },
  "archetype": "receipt",
  "component": {
    "title": null,
    "groups": [
      {
        "fields": {
          "clock_drift_warning": {
            "$interpolate": "{{host}} delta vs NTP is 840ms (warning threshold: 500ms)",
            "$bindings": {
              "host": "scenario.host"
            },
            "$example": "host delta vs NTP is 840ms (warning threshold: 500ms)"
          },
          "causal ordering unaffected": {
            "$slot": "causal_ordering_unaffected",
            "$from": "live.groups[0].fields.causal_ordering_unaffected",
            "$example": "intact"
          }
        }
      },
      {
        "fields": {
          "host": {
            "$slot": "host_2",
            "$from": "live.groups[1].fields.host",
            "$example": "ws-07 (chronyd reachable, not yet synced)"
          },
          "remedy": "synchronize host system clock via 'chronyd' or 'ntpdate' when convenient; execution is not blocked"
        }
      }
    ]
  }
}
```

Rendered output:

```text
[dev:tier_1]  ✓  exit 0

  ⚠  clock drift warning: host delta vs NTP is 840ms (warning threshold: 500ms)
         causal ordering unaffected: intact

  host:            ws-07 (chronyd reachable, not yet synced)
  state_modified: false
  remedy:          synchronize host system clock via 'chronyd' or 'ntpdate' when convenient; execution is not blocked
```

---

### 5.11 Progressive Disclosure Doc Reading (`screens/doc/read/doc.read.success.sliced.json`)

Fixture (`wireframe/v1`):

```json
{
  "$schema": "wireframe/v1",
  "id": "doc.read.success.sliced",
  "scenario": {
    "doc_urp": "doc://refund-policy"
  },
  "target": {
    "$slot": "doc_urp",
    "$from": "scenario.doc_urp",
    "$example": "doc://refund-policy"
  },
  "command": {
    "$interpolate": "capcli doc read {{doc_urp}} --max-tokens 100",
    "$bindings": {
      "doc_urp": "scenario.doc_urp"
    },
    "$example": "capcli doc read doc://refund-policy --max-tokens 100"
  },
  "elapsed_ms": {
    "$slot": "elapsed_ms",
    "$from": "live.elapsed_ms",
    "$type": "integer",
    "$example": 1292
  },
  "context": {
    "env": "dev",
    "tier": "tier_1",
    "trust": "pinned",
    "data_shape": {
      "$slot": "data_shape",
      "$from": "context.data_shape",
      "$example": "truncated"
    }
  },
  "archetype": "document",
  "component": {
    "header_badge": {
      "$interpolate": "{{doc_urp}} (sections 1-2 of 5)",
      "$bindings": {
        "doc_urp": "scenario.doc_urp"
      },
      "$example": "doc://refund-policy (sections 1-2 of 5)"
    },
    "pagination": {
      "items": [
        {
          "section": {
            "$slot": "section",
            "$from": "live.pagination.items[0].section",
            "$type": "integer",
            "$example": 1
          },
          "heading": {
            "$slot": "heading",
            "$from": "live.pagination.items[0].heading",
            "$example": "Scope"
          },
          "tokens": {
            "$slot": "tokens",
            "$from": "live.pagination.items[0].tokens",
            "$type": "integer",
            "$example": 22
          }
        },
        {
          "section": {
            "$slot": "section_2",
            "$from": "live.pagination.items[1].section",
            "$type": "integer",
            "$example": 2
          },
          "heading": {
            "$slot": "heading_2",
            "$from": "live.pagination.items[1].heading",
            "$example": "Refund windows"
          },
          "tokens": {
            "$slot": "tokens_2",
            "$from": "live.pagination.items[1].tokens",
            "$type": "integer",
            "$example": 74
          }
        }
      ],
      "next_cursor": {
        "$interpolate": "{{doc_urp}}#3",
        "$bindings": {
          "doc_urp": "scenario.doc_urp"
        },
        "$example": "doc://refund-policy#3"
      },
      "has_more": {
        "$slot": "has_more",
        "$from": "live.pagination.has_more",
        "$type": "boolean",
        "$example": true
      }
    },
    "meta": {
      "document": {
        "$slot": "doc_urp_2",
        "$from": "scenario.doc_urp",
        "$example": "doc://refund-policy"
      },
      "tokens": {
        "$slot": "tokens_3",
        "$from": "live.meta.tokens",
        "$example": "96 (cap: 100)"
      },
      "has_more": {
        "$slot": "has_more_2",
        "$from": "live.meta.has_more",
        "$type": "boolean",
        "$example": true
      },
      "next_cursor": {
        "$interpolate": "{{doc_urp}}#3",
        "$bindings": {
          "doc_urp": "scenario.doc_urp"
        },
        "$example": "doc://refund-policy#3"
      }
    },
    "body": [
      {
        "$slot": "body_0",
        "$from": "live.body[0]",
        "$example": "1. Scope"
      },
      {
        "$slot": "body_1",
        "$from": "live.body[1]",
        "$example": "Refund routing and approval rules for the storefront."
      },
      {
        "$slot": "body_2",
        "$from": "live.body[2]",
        "$example": "2. Refund windows"
      },
      {
        "$slot": "body_3",
        "$from": "live.body[3]",
        "$example": "Standard window is 30 days. Extended window is 120 days and requires"
      },
      {
        "$slot": "body_4",
        "$from": "live.body[4]",
        "$example": "supervisor approval."
      }
    ]
  },
  "affordances": [
    {
      "rel": {
        "$slot": "rel",
        "$from": "live.affordances[0].rel",
        "$example": "next"
      },
      "command": {
        "$interpolate": "capcli doc outline {{doc_urp}}",
        "$bindings": {
          "doc_urp": "scenario.doc_urp"
        },
        "$example": "capcli doc outline doc://refund-policy"
      },
      "intent": {
        "$slot": "intent",
        "$from": "live.affordances[0].intent",
        "$example": "Outline node tree with section indices"
      },
      "risk": {
        "$slot": "risk",
        "$from": "live.affordances[0].risk",
        "$example": "safe"
      }
    }
  ]
}
```

Rendered output:

```text
[dev:tier_1]  doc://refund-policy (sections 1-2 of 5)

  tokens:       96 (cap: 100)
  has_more:     true
  next_cursor:  doc://refund-policy#3

  ────────────────────────────────────────────────────────────────────────────
  1. Scope
  Refund routing and approval rules for the storefront.
  2. Refund windows
  Standard window is 30 days. Extended window is 120 days and requires
  supervisor approval.
```

The machine payload carries the full keyset envelope inside the
document component (§6.1.2): `items` (typed section items), `meta.next_cursor`
(doc-pointer resume at section 3), `meta.has_more: true` — the
collection-law trio from `manifest.json` `output_contract.pagination`.

---

### 5.12 Minimalist Root Help Stub (`screens/sys/help/sys.help.success.stub.json`)

Host screen only; the trailer line renders after it as an additive final line. Line-cap accounting: `manifest.json` `output_contract.trailer.line_cap_law`.

Fixture (`wireframe/v1`):

```json
{
  "$schema": "wireframe/v1",
  "id": "sys.help.success.stub",
  "command": {
    "$interpolate": "capcli",
    "$bindings": {},
    "$example": "capcli"
  },
  "elapsed_ms": {
    "$slot": "elapsed_ms",
    "$from": "live.elapsed_ms",
    "$type": "integer",
    "$example": 1166
  },
  "context": {
    "env": "dev",
    "tier": "tier_1",
    "trust": "reviewed"
  },
  "archetype": "document",
  "component": {
    "header_badge": {
      "$slot": "header_badge",
      "$from": "live.header_badge",
      "$example": "capcli 0.4.2 — compiled execution firewall for AI agents"
    },
    "fields": {
      "Find actions": {
        "$slot": "find_actions",
        "$from": "live.fields.find_actions",
        "$example": "capcli search <query>"
      },
      "Pre-flight": {
        "$slot": "pre_flight",
        "$from": "live.fields.pre_flight",
        "$example": "capcli inspect <urp>"
      },
      "System status": {
        "$slot": "system_status",
        "$from": "live.fields.system_status",
        "$example": "capcli sys doctor"
      }
    },
    "body": [
      {
        "$slot": "body_0",
        "$from": "live.body[0]",
        "$example": "Usage: capcli <noun> <verb> [target] [flags]"
      },
      {
        "$slot": "body_1",
        "$from": "live.body[1]",
        "$example": "Capabilities are discovered dynamically, not listed in static help."
      }
    ]
  },
  "trailer": {
    "prompt": "doc://prompts/onboarding/human#1",
    "reason": {
      "$slot": "reason",
      "$from": "live.trailer.reason",
      "$example": "human operator requested onboarding tour"
    },
    "serve": {
      "$slot": "serve",
      "$from": "live.trailer.serve",
      "$example": "L1"
    }
  },
  "affordances": [
    {
      "rel": {
        "$slot": "rel",
        "$from": "live.affordances[0].rel",
        "$example": "next"
      },
      "command": {
        "$interpolate": "capcli sys doctor --boot-check",
        "$bindings": {},
        "$example": "capcli sys doctor --boot-check"
      },
      "intent": {
        "$slot": "intent",
        "$from": "live.affordances[0].intent",
        "$example": "Host doctor readiness check"
      },
      "risk": {
        "$slot": "risk",
        "$from": "live.affordances[0].risk",
        "$example": "safe"
      }
    }
  ]
}
```

Rendered output:

```text
capcli 0.4.2 — compiled execution firewall for AI agents

Usage: capcli <noun> <verb> [target] [flags]

Capabilities are discovered dynamically, not listed in static help.
  Find actions:    capcli search <query>
  Pre-flight:      capcli inspect <urp>
  System status:   capcli sys doctor
```

---

### 5.13 Commit With Nonzero Attention (`screens/run/execute/run.execute.success.attention.json`)

The commit receipt renders exactly as the zero-attention screen; the
`attention` key is machine-only and adds no human line. Cursor value is
illustrative: the cursor advances on every envelope render and the golden
runner never asserts it.

Fixture (`wireframe/v1`):

```json
{
  "$schema": "wireframe/v1",
  "id": "run.execute.success.attention",
  "scenario": {
    "routine_urp": "cap://dispatch_order@4",
    "routine_name": "dispatch_order",
    "routine_version": 4,
    "order_id": "ORD-1042",
    "carrier": "fedex",
    "intent": "fulfill urgent pending orders"
  },
  "target": {
    "$slot": "routine_urp",
    "$from": "scenario.routine_urp",
    "$example": "cap://dispatch_order@4"
  },
  "command": {
    "$interpolate": "capcli run {{routine_urp}} -p order_id={{order_id}} -p carrier={{carrier}} -m \"{{intent}}\"",
    "$bindings": {
      "routine_urp": "scenario.routine_urp",
      "carrier": "scenario.carrier",
      "order_id": "scenario.order_id",
      "intent": "scenario.intent"
    },
    "$example": "capcli run cap://dispatch_order@4 -p order_id=ORD-1042 -p carrier=fedex -m \"fulfill urgent pending orders\""
  },
  "elapsed_ms": {
    "$slot": "elapsed_ms",
    "$from": "live.elapsed_ms",
    "$type": "integer",
    "$example": 361
  },
  "context": {
    "env": "dev",
    "tier": "tier_1",
    "trust": "pinned",
    "data_shape": {
      "$slot": "data_shape",
      "$from": "context.data_shape",
      "$example": "populated"
    }
  },
  "audit_op": {
    "$slot": "audit_op",
    "$from": "live.audit_op",
    "$example": "op_9f2c"
  },
  "archetype": "receipt",
  "component": {
    "title": null,
    "groups": [
      {
        "fields": {
          "routine": {
            "$interpolate": "{{routine_name}}@{{routine_version}} (pinned)",
            "$bindings": {
              "routine_name": "scenario.routine_name",
              "routine_version": "scenario.routine_version"
            },
            "$example": "dispatch_order@4 (pinned)"
          },
          "session": {
            "$slot": "session",
            "$from": "live.groups[0].fields.session",
            "$example": "ses_a992f"
          },
          "intent": {
            "$interpolate": "\"{{intent}}\"",
            "$bindings": {
              "intent": "scenario.intent"
            },
            "$example": "\"fulfill urgent pending orders\""
          },
          "frame": {
            "$slot": "frame",
            "$from": "live.groups[0].fields.frame",
            "$example": "frame_021 (3/8 ops · 358ms)"
          }
        }
      },
      {
        "fields": {
          "order_id": {
            "$slot": "order_id",
            "$from": "scenario.order_id",
            "$example": "ORD-1042"
          },
          "carrier": {
            "$slot": "carrier",
            "$from": "scenario.carrier",
            "$example": "fedex"
          },
          "tracking": {
            "$slot": "tracking",
            "$from": "live.groups[1].fields.tracking",
            "$example": "794644790133"
          },
          "status": {
            "$slot": "status",
            "$from": "live.groups[1].fields.status",
            "$example": "shipped (1 row committed)"
          }
        },
        "lines": [
          {
            "$slot": "lines_0",
            "$from": "live.groups[1].lines[0]",
            "$example": "result:"
          }
        ]
      },
      {
        "fields": {
          "result_hash": {
            "$slot": "result_hash",
            "$from": "live.groups[2].fields.result_hash",
            "$example": "sha256:9c41e7b0d2a8f513c6ee"
          }
        }
      }
    ]
  },
  "attention": {
    "cursor": {
      "$slot": "cursor",
      "$from": "live.attention.cursor",
      "$example": "att_a992f_042"
    },
    "counts": {
      "critical": {
        "$slot": "critical",
        "$from": "live.attention.counts.critical",
        "$type": "integer",
        "$example": 1
      },
      "standard": {
        "$slot": "standard",
        "$from": "live.attention.counts.standard",
        "$type": "integer",
        "$example": 1
      },
      "background": {
        "$slot": "background",
        "$from": "live.attention.counts.background",
        "$type": "integer",
        "$example": 0
      }
    },
    "top": [
      {
        "id": {
          "$slot": "ask_id",
          "$from": "live.attention.top[0].id",
          "$example": "ask_88a"
        },
        "class": "critical",
        "source": {
          "$slot": "source",
          "$from": "live.attention.top[0].source",
          "$example": "ping.ask"
        },
        "summary": {
          "$interpolate": "Fraud score 0.83 on {{order_id}}. Approve dispatch?",
          "$bindings": {
            "order_id": "scenario.order_id"
          },
          "$example": "Fraud score 0.83 on ORD-1042. Approve dispatch?"
        },
        "affordance": {
          "rel": {
            "$slot": "rel",
            "$from": "live.attention.top[0].affordance.rel",
            "$example": "next"
          },
          "command": {
            "$interpolate": "capcli ping resolve ask_88a --choice approve",
            "$bindings": {},
            "$example": "capcli ping resolve ask_88a --choice approve"
          },
          "intent": {
            "$slot": "intent",
            "$from": "live.attention.top[0].affordance.intent",
            "$example": "Resolve the pending approval ask"
          },
          "risk": {
            "$slot": "risk",
            "$from": "live.attention.top[0].affordance.risk",
            "$example": "safe"
          }
        }
      },
      {
        "id": {
          "$slot": "event_id",
          "$from": "live.attention.top[1].id",
          "$example": "evt_ord_903"
        },
        "class": "standard",
        "source": {
          "$slot": "source_2",
          "$from": "live.attention.top[1].source",
          "$example": "_inbox"
        },
        "summary": {
          "$slot": "summary",
          "$from": "live.attention.top[1].summary",
          "$example": "Refund request queued via shopify_refunds intake"
        },
        "affordance": {
          "rel": {
            "$slot": "rel_2",
            "$from": "live.attention.top[1].affordance.rel",
            "$example": "next"
          },
          "command": {
            "$interpolate": "capcli sys inbox pop --channel webhook",
            "$bindings": {},
            "$example": "capcli sys inbox pop --channel webhook"
          },
          "intent": {
            "$slot": "intent_2",
            "$from": "live.attention.top[1].affordance.intent",
            "$example": "Drain the queued sensory events"
          },
          "risk": {
            "$slot": "risk_2",
            "$from": "live.attention.top[1].affordance.risk",
            "$example": "safe"
          }
        }
      }
    ],
    "suppressed": []
  }
}
```

Rendered output (identical to the zero-attention receipt; no attention line):

```text
[dev:tier_1]  capcli run cap://dispatch_order@4

  routine:   dispatch_order@4 (pinned)
  session:   ses_a992f
  intent:    "fulfill urgent pending orders"
  frame:     frame_021 (3/8 ops · 358ms)

  result:
    order_id:  ORD-1042
    carrier:   fedex
    tracking:  794644790133
    status:    shipped (1 row committed)

  result_hash: sha256:9c41e7b0d2a8f513c6ee
```

---

### 5.14 Claim-Suppressed Inbox Pop (`screens/sys/inbox/sys.inbox.success.suppressed.json`)

Zero counts, yet the key is present: suppression is active. The held row
waits on the Layer 1 claim release, which is also its dismiss path — no
per-item ack exists.

Fixture (`wireframe/v1`):

```json
{
  "$schema": "wireframe/v1",
  "id": "sys.inbox.success.suppressed",
  "scenario": {
    "channel": "webhook"
  },
  "target": {
    "$slot": "channel",
    "$from": "scenario.channel",
    "$example": "webhook"
  },
  "command": {
    "$interpolate": "capcli sys inbox pop --channel {{channel}}",
    "$bindings": {
      "channel": "scenario.channel"
    },
    "$example": "capcli sys inbox pop --channel webhook"
  },
  "elapsed_ms": {
    "$slot": "elapsed_ms",
    "$from": "live.elapsed_ms",
    "$type": "integer",
    "$example": 1004
  },
  "context": {
    "env": "dev",
    "tier": "tier_1",
    "trust": "draft",
    "data_shape": {
      "$slot": "data_shape",
      "$from": "context.data_shape",
      "$example": "populated"
    }
  },
  "archetype": "tree",
  "component": {
    "title": {
      "$slot": "title",
      "$from": "live.inbox.title",
      "$example": "popped"
    },
    "root": {
      "$slot": "root",
      "$from": "live.inbox.root",
      "$example": "events:"
    },
    "nodes": [],
    "footer": {
      "channel": {
        "$slot": "channel_2",
        "$from": "scenario.channel",
        "$example": "webhook"
      },
      "popped": {
        "$slot": "popped",
        "$from": "live.inbox.footer.popped",
        "$example": "0 events"
      },
      "remaining": {
        "$slot": "remaining",
        "$from": "live.inbox.footer.remaining",
        "$example": "1 held under active claim"
      },
      "note": {
        "$slot": "note",
        "$from": "live.inbox.footer.note",
        "$example": "claim orders:ORD-10 held by agt_9k2w; held rows stay invisible until release"
      }
    }
  },
  "attention": {
    "cursor": {
      "$slot": "cursor",
      "$from": "live.attention.cursor",
      "$example": "att_a992f_043"
    },
    "counts": {
      "critical": {
        "$slot": "critical",
        "$from": "live.attention.counts.critical",
        "$type": "integer",
        "$example": 0
      },
      "standard": {
        "$slot": "standard",
        "$from": "live.attention.counts.standard",
        "$type": "integer",
        "$example": 0
      },
      "background": {
        "$slot": "background",
        "$from": "live.attention.counts.background",
        "$type": "integer",
        "$example": 0
      }
    },
    "top": [],
    "suppressed": [
      {
        "id": "evt_ord_901",
        "class": "standard",
        "source": "_inbox",
        "summary": "Held under active Layer 1 claim orders:ORD-10 (holder agt_9k2w)",
        "affordance": {
          "rel": "inspect",
          "command": "capcli sys audit trace op_9f2c --explain",
          "intent": "Inspect the holding operation",
          "risk": "safe"
        }
      }
    ]
  }
}
```

Rendered output (tree with an empty walk; no attention line):

```text
[dev:tier_1]  popped

  events:

  channel:   webhook
  popped:    0 events
  remaining: 1 held under active claim
  note:      claim orders:ORD-10 held by agt_9k2w; held rows stay invisible until release
```

---

## 6. Fixture Schema & Rust Test Runner Contract

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

### 6.1.1 Trailer Slot

`output_contract.trailer` in `manifest.json` is the output contract's
only producer-facing slot, and the bridge is deterministic: the payload
shape is frozen once in `manifest.json` (`human_format` +
`machine_schema`), and the prompt engine and the wireframe fixtures
validate against that same schema. The wireframe knows the shape of a
trailer and nothing else about the producer.

- Human output: one optional final line, `trailer: <prompt> - <reason>`.
- JSON output: one optional additive envelope key, `next_action`, whose value validates against `machine_schema` in `manifest.json`.
- The wireframe validates shape and position against the frozen schema. It never evaluates a predicate, resolves a pointer, or originates a payload.
- A payload with `serve: blocked` is never rendered. Absent is the default.
- The slot leaves exit code and `state_modified` unchanged.
- Line-cap accounting lives in `manifest.json` `output_contract.trailer.line_cap_law`; this section carries no cap number.

The slot-naming bridge, stated once so it can never be confused: on a
`wireframe/v1` fixture the slot is the root key `trailer`, beside `component` —
the `human_field`, producer-facing slot above. When a
renderer emits the `--json` machine envelope, the key becomes `next_action`
per `output_contract.trailer.machine_field` in `manifest.json`. Fixtures
never serialize a `next_action` key.

### 6.1.2 Pagination Slot

Truncated screens carry the keyset envelope inside the component, mirroring
`output_contract.pagination.required_envelope_keys` in `manifest.json`:

- `document` components (6/10 on disk, every truncated or sliced screen):
  a `pagination` object `{ items, next_cursor, has_more }` at component
  level, with `items` as the typed leading items (not the full set) and
  `meta` mirroring `next_cursor` and `has_more`.
- `receipt` components: no fixture on disk carries pagination keys; every
  truncated screen is a `document`.

`next_cursor` is the keyset cursor a follow-up invocation passes to resume;
`has_more` is always `true` on a truncated screen. Non-truncated screens
carry none of these keys.

### 6.2 Runner Contract

Status: spec contract. The repository carries no `crates/` tree; the Python
validator enforces the checks in this section until the Rust harness exists.
No golden `.txt` files; the fixture component IS the golden source.

One mode — **structural match**. `cargo test --workspace` executes it against every screen.

For each screen:

1. Dispatch `command` against the real binary.
2. Extract `live.*` bindings from the emitted envelope (via the `CliEnvelope<T>` deserializer).
3. Walk the screen: every literal matches byte-exact; every `$slot` satisfies its `$type`/`$pattern`/`$enum` and equals the actual field; every `$interpolate` produces a string that equals the actual field.
4. Assert exit code equals the derivation from `id`; assert `state_modified: false` on non-zero exits.
5. Assert banned tokens absent, no pipe character, trailer present iff `_triggers.json` says so, no `next_action` on a screen with no trailer.

Strict instantiation (substitute `$example`, byte-compare) is a developer tool: `cargo xtask wireframe-strict`. It never runs in CI.

Cross-layer test (`assert_prompt_triggers_match_wireframe_screens`) is unchanged.

---

## 7. Edgeless Playable Canvas Implementation (`wireframe.html`)

The HTML canvas renders all screens by instantiating `$example` values from `wireframe/v1` screens. No `.txt` files are fetched. `TerminalPanel` implements the four component renderers defined in §6.1 (`diagnostic`, `tree`, `receipt`, `document`); it consumes component payloads, and carets, branch glyphs, dividers, and alignment are its output.

```
zoomable, node draggable, click inspect (renders from json shape), scenario select to highlight the flows in canvas
```

---

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
