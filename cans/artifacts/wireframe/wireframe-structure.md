# Canonical Wireframe, State Machine & Flow Engine Specification

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
    db/
      lock/
      unlock/
      schema/
      snapshot/
      restore/
      dump/
    routine/
      new/
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
    bind/
      cron/
      webhook/
      endpoint/
      export/
      list/
      inspect/
      pause/
      resume/
      remove/
      keys/
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
      tail/
      trace/
      query/
      replay/
      register/
      agents/
      revoke/
      vault_set/
      vault_import/
      doctor/
      backup/
      recover/
      exec/
      serve/
    doc/
      read/
      outline/
      inspect/
    template/
      new/
      list/
      inspect/
      validate/
      pack/
      apply/
```

### 1.1 Structural Invariants
* **Active Nouns:** Exactly 11 CLI nouns (`run`, `db`, `routine`, `api`, `bind`, `ping`, `rule`, `env`, `sys`, `doc`, `template`).
* **Single-Source Law:** Every screen has exactly one `.json` fixture. No `.txt` files are committed. The JSON shape IS the screen; renderers (HTML canvas, Rust test harness) consume it directly.
* **Depth Ceiling:** File paths relative to `screens/` must remain exactly 3 path components: `{noun}/{verb}/{filename}.json`.
* **Sibling Invariants:** Min 3, max 16 verb directories per noun branch node.
* **Naming Law:** Strict 4-segment token syntax:
  ```
  {noun}.{verb}.{state}.{condition}.json
  ```
* **Root Aliases:** Exactly four ergonomic root shortcuts are legal invocation grammar (cans/interface.md#CLI-surface): `capcli sql` ≡ `capcli run sql`, `capcli search` ≡ `capcli run search`, `capcli inspect` ≡ `capcli run inspect`, and `capcli apply` ≡ `capcli rule apply schema`. These four root aliases may appear in fixture `command` strings; no other root shortcuts exist — everything else is `capcli <noun> <verb>`.
* **Run Execute Form:** `capcli run <cap://...>` is the execute invocation (cans/interface.md#CLI-surface: `execute — run <capability>`); `execute` names the screen family and the fixture directory and does not appear in the typed command, and no `capcli run execute ...` form exists.
* **Compound-Verb Mapping:** Screen IDs and directories keep underscore verb segments (`sys.vault_set`, `sys.vault_import`), while the invocation grammar follows cans/interface.md#CLI-surface: `capcli sys vault set <key> <val>`, `capcli sys vault import-env`, `capcli sys agent register|revoke`, `capcli sys audit tail|trace|query|replay`. The underscore form names the fixture; the spaced form is what the user types.
* **Dynamic Environment Namespaces:** Environments are user-provisionable namespaces (`env new <slug>`, cans/interface.md#CLI-surface). `state_axes.env` in `manifest.json` lists only the kernel-reserved roots (`dev`, `sim`, `prod`); values like `staging` or `lab` are legal fixtures of dynamically provisioned namespaces (see `env_policy` in `manifest.json`).

---

## 2. Core Manifests & States

### 2.1 `manifest.json`

Canonical file: `manifest.json` (same directory). It owns the noun list, the state axes, and the output contract; this document points at it and does not reproduce it.

The domain registry lives only in `_states.json`. This manifest carries no copy of it; consumers read `_states.json` directly.

Naming convention, both artifact directories (`wireframe/`, `prompt/`): a leading underscore marks internal engine configuration and graph state — `_states.json`, `_flows.json`, `_triggers.json`. A clean name marks an externally consumable compiler artifact — `manifest.json`.

### 2.2 `_states.json`

Canonical file: `_states.json` (same directory). It is the single home of the state taxonomy: exit code → label, exit → legal domains, exit → required diagnostic fields. Not reproduced here by design.

The law in one paragraph: six states, one per exit — `success` 0, `denial` 2, `refusal` 3, `crash` 4, `panic` 5, `yield` 6 (cans/physics.md#Exit-code-law). The screen-ID state slot takes exactly these labels; severity and lifecycle words (`warning`, `tamper`, `suspended`, `rolled_back`) live in the condition slot. A domain determines its exit: `api.quota` alone is dual-registered (exit 2 Critical, exit 6 Background). Exit 6 covers both quota yields and `ping.ask` frame suspensions (cans/action.md suspension contract).

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


### 4.1 `run/` (6 verbs → 40 screens)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `run.execute.success.populated` | success | 0 | — | populated | Deterministic execution and commit |
| `run.execute.success.redirected` | success | 0 | — | redirected | Payload directed to file via `--out`; stdout emits receipt |
| `run.execute.success.truncated` | success | 0 | — | truncated | Result >500 tokens; returns `next_cursor` |
| `run.execute.denial.budget` | denial | 2 | policy.budget | exhausted | Frame ops/duration ceiling exhausted |
| `run.execute.denial.budget_cascade` | denial | 2 | policy.budget | starved | Pre-flight call-tree analysis detects starved child branch; invocation blocked |
| `run.execute.denial.trust` | denial | 2 | policy.trust | unproven | Draft routine executed in prod |
| `run.execute.denial.tier2_pinned` | denial | 2 | policy.trust | tier2 | `E045_TIER2_PINNED_DENIED` on macOS/Win |
| `run.execute.denial.authorizer` | denial | 2 | policy.authorizer | forbidden | Prohibited table or column mutation |
| `run.execute.denial.network_jail` | denial | 2 | kernel.sandbox | syscall_42 | Trapped raw `connect()` via seccomp-bpf |
| `run.execute.denial.claim_held` | denial | 2 | db.claims | locked | Exclusive `--lock` ref already held |
| `run.execute.refusal.missing_secret`| refusal| 3 | policy.secrets | missing_key | Missing credential redirects to Cockpit URL |
| `run.execute.yield.ask` | yield | 6 | ping.ask | suspended | Routine hit `ctx.ping.ask`; frame checkpointed to `_pending_asks`, exits 6 until human resolves |
| `run.execute.yield.quota` | yield | 6 | api.quota | rate_limit | Suspends task; sets `yield_until` timestamp |
| `run.execute.denial.quota` | denial | 2 | api.quota | hard_deny | Critical-priority task drained provider pool to 0; hard-denied, never yielded |
| `run.execute.success.resumed` | success | 0 | — | resumed | Daemon re-dispatches task on token refill |
| `run.execute.crash.runtime` | crash | 4 | routine.runtime | exception | Guest language uncaught error |
| `run.execute.crash.poll_timeout` | crash | 4 | routine.runtime | timeout | `poll_until` exceeds 30-second ceiling |
| `run.execute.panic.secret_leak` | panic | 5 | kernel.panic | leak | `kill_and_alert` triggered on plaintext secret leak |
| `run.sql.success.populated` | success | 0 | — | populated | AST-vetted SQL commit |
| `run.sql.success.dry_run` | success | 0 | — | dry_run | Execution plan preview with impact metrics |
| `run.sql.success.redirected` | success | 0 | — | redirected | SQL export payload directed to disk via `--out` |
| `run.sql.success.truncated` | success | 0 | — | truncated | SELECT result bounded at 10,000 rows |
| `run.sql.denial.ast` | denial | 2 | policy.ast | unbounded | Missing `WHERE` or `LIMIT` clause |
| `run.sql.denial.authorizer` | denial | 2 | policy.authorizer | schema_mod | Blocked `DROP TABLE` or system table write |
| `run.sql.denial.engine_busy` | denial | 2 | db.engine | timeout | SQLite transaction queue wait timeout |
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
| `run.inspect.success.prompt` | success | 0 | — | populated | Prompt L2 envelope only; no body content |
| `run.inspect.refusal.missing_ptr` | refusal | 3 | missing_param | missing_arg | Unrecognized target pointer format |
| `run.inspect.denial.trust` | denial | 2 | policy.trust | unreadable | Draft routine secret inspection denied |
| `run.abort.success.aborted` | success | 0 | — | aborted | Suspended frame purged; OCC fence released |
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
| `db.snapshot.denial.prod_draft` | denial | 2 | policy.trust | forbidden | Draft identity cannot snapshot prod |
| `db.restore.success.restored` | success | 0 | — | restored | DB state restored from snapshot |
| `db.restore.refusal.missing_id` | refusal | 3 | missing_param | missing_arg | Target snapshot ID missing |
| `db.restore.denial.active_locks` | denial | 2 | db.claims | active_locks | Active claims prevent state reversal |
| `db.dump.success.populated` | success | 0 | — | populated | Unified SQL schema and seed dump |
| `db.dump.success.truncated` | success | 0 | — | truncated | Dump output payload truncated |

### 4.3 `routine/` (8 verbs → 35 screens)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `routine.new.success.created` | success | 0 | — | created | Routine scaffold committed |
| `routine.new.success.overview` | success | 0 | — | created | Mandatory overview routine scaffolded (harness H6) |
| `routine.new.refusal.name_taken` | refusal | 3 | validation | collision | Routine name already registered |
| `routine.new.refusal.shape_violation` | refusal | 3 | validation | bad_shape | Scaffold violates param or complexity limits |
| `routine.new.refusal.near_duplicate` | refusal | 3 | validation | near_duplicate | Similarity >= 0.85 without a justifying `--reason` |
| `routine.new.denial.file_locked` | denial | 2 | policy.authoring | file_locked | Concurrent edit blocked by the authoring mutex |
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
| `routine.ship.success.rolled_back` | success | 0 | — | rolled_back | Canary telemetry trips auto-rollback |
| `routine.ship.success.queued` | success | 0 | — | queued | Enqueued for human review; zero code shipped |
| `routine.ship.denial.metrics` | denial | 2 | policy.authorizer | low_success | Success rate falls below 0.95 |
| `routine.ship.refusal.missing_reason`| refusal | 3 | missing_param | missing_arg | Elevation to pinned requires reason |
| `routine.ship.denial.trust` | denial | 2 | policy.trust | tier2_refusal | Pinned promotion denied on Tier 2 |
| `routine.pending.success.populated` | success | 0 | — | populated | Batch promotion candidates listed |
| `routine.pending.success.empty` | success | 0 | — | empty | No routines pending promotion |
| `routine.sweep.success.populated` | success | 0 | — | populated | Deduplication proposals generated |
| `routine.sweep.success.empty` | success | 0 | — | empty | No duplicate routines detected |
| `routine.stats.success.populated` | success | 0 | — | populated | Routine p50/p95 execution metrics |
| `routine.stats.refusal.not_found` | refusal | 3 | validation | not_found | Routine name does not exist |
| `routine.rollback.success.completed`| success | 0 | — | completed | Reverts pointer to prior version |
| `routine.rollback.denial.depth` | denial | 2 | policy.governance | depth_limit | Versioning cap on retained history: exceeds max rollback depth of 5 |
| `routine.rollback.refusal.not_found`| refusal | 3 | validation | not_found | Target version not found in history |
| `routine.retire.success.completed` | success | 0 | — | completed | Routine retired; bound ingress loudly dismantled (cron paused→dissolved by daemon, endpoint revoked) |
| `routine.retire.denial.active_deps` | denial | 2 | policy.governance | deps_exist | In-memory routine DAG blocks retirement of active dependencies |
| `routine.retire.refusal.missing_reason` | refusal | 3 | missing_param | missing_arg | Prod retire of an operational routine demands --reason |
| `routine.retire.refusal.not_found` | refusal | 3 | validation | not_found | Target routine does not exist |

### 4.4 `api/` (10 verbs → 26 screens)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `api.sync.success.synced` | success | 0 | — | synced | OpenAPI spec compiled to catalog |
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
| `api.retire.success.completed` | success | 0 | — | completed | API verb deactivated to dormant |
| `api.retire.refusal.not_found` | refusal | 3 | validation | not_found | Target verb not found |
| `api.rollback.success.completed` | success | 0 | — | completed | Reverts API spec to prior hash |
| `api.rollback.denial.depth` | denial | 2 | policy.authorizer | depth_limit | Exceeds max rollback limit of 5 |
| `api.rollback.refusal.not_found` | refusal | 3 | validation | not_found | Target version not found |
| `api.import.success.imported` | success | 0 | — | imported | OpenAPI endpoint imported to catalog at draft |
| `api.import.refusal.missing_spec` | refusal | 3 | missing_param | missing_spec | Import requires a spec source |
| `api.record.success.recorded` | success | 0 | — | recorded | Live response captured as JSON Schema contract |

### 4.5 `bind/` (10 verbs → 26 screens)

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
| `bind.endpoint.success.bound` | success | 0 | — | bound | Routine exposed as HTTP/MCP |
| `bind.endpoint.denial.trust` | denial | 2 | policy.trust | unpinned | Endpoint requires pinned trust |
| `bind.endpoint.denial.cap` | denial | 2 | policy.authorizer | cap_exceeded| Max 10 active endpoints reached |
| `bind.export.success.openapi` | success | 0 | — | exported | Bound OpenAPI schema exported |
| `bind.export.success.mcp` | success | 0 | — | exported | Bound MCP tool definition exported |
| `bind.list.success.populated` | success | 0 | — | populated | Active bindings displayed |
| `bind.list.success.empty` | success | 0 | — | empty | Zero bindings active |
| `bind.inspect.success.populated` | success | 0 | — | populated | Binding configuration envelope |
| `bind.inspect.refusal.not_found` | refusal | 3 | validation | not_found | Target binding ID not found |
| `bind.pause.success.completed` | success | 0 | — | completed | Trigger paused |
| `bind.pause.refusal.not_found` | refusal | 3 | validation | not_found | Target binding ID not found |
| `bind.resume.success.completed` | success | 0 | — | completed | Trigger resumed |
| `bind.resume.refusal.not_found` | refusal | 3 | validation | not_found | Target binding ID not found |
| `bind.remove.success.completed` | success | 0 | — | completed | Trigger dismantled |
| `bind.remove.refusal.not_found` | refusal | 3 | validation | not_found | Target binding ID not found |
| `bind.keys.success.issued` | success | 0 | — | issued | API key stamped for endpoint (90d expiry) |
| `bind.keys.denial.cap` | denial | 2 | policy.authorizer | cap_exceeded| Max 25 keys reached |

### 4.6 `ping/` (5 verbs → 17 screens)

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
| `ping.resolve.denial.occ_conflict` | denial | 2 | policy.notify | occ_fence | Kernel OCC fence gate caught entity drift during suspension; resume denied |
| `ping.resolve.refusal.not_found` | refusal | 3 | validation | not_found | Invalid ask ID |
| `ping.resolve.denial.expired` | denial | 2 | policy.notify | expired | Timeout elapsed; fail-closed |
| `ping.expire.success.completed` | success | 0 | — | completed | Explicit expiration executed |
| `ping.expire.refusal.not_found` | refusal | 3 | validation | not_found | Target inquiry not found |

### 4.7 `rule/` (6 verbs → 14 screens)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `rule.show.success.populated` | success | 0 | — | populated | Compiled DDL / authorizer rules |
| `rule.show.refusal.not_found` | refusal | 3 | validation | not_found | Target rule/table not found |
| `rule.diff.success.populated` | success | 0 | — | populated | Schema/policy drift detected |
| `rule.diff.success.empty` | success | 0 | — | empty | Workspace in lockstep with rules |
| `rule.apply.success.applied` | success | 0 | — | applied | DDL applied in transaction |
| `rule.apply.success.dry_run` | success | 0 | — | dry_run | DDL impact preview on snapshot |
| `rule.apply.denial.trust` | denial | 2 | policy.trust | unproven | `ALTER` requires reviewed trust |
| `rule.apply.refusal.validation` | refusal | 3 | validation | rejected | Gate 2 semantic check fails |
| `rule.apply.refusal.lockfile` | refusal | 3 | lockfile_mismatch | drift | Lockfile root hash mismatch |
| `rule.validate.success.valid` | success | 0 | — | valid | Declarations pass Gates 1 & 2 |
| `rule.validate.refusal.syntax` | refusal | 3 | compile | bad_syntax | Gate 1 YAML syntax failure |
| `rule.validate.refusal.semantics` | refusal | 3 | compile | circular_ref | Gate 2 circular dependency detected |
| `rule.plan.success.planned` | success | 0 | — | planned | Migration bundle generated (plan.json, backfill stub) |
| `rule.prove.success.proven` | success | 0 | — | proven | Migration rehearsed in sim (expand, backfill, SLA) |

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

### 4.9 `sys/` (16 verbs → 47 screens)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `sys.help.success.stub` | success | 0 | — | stub | Minimalist help stub redirecting to search; host line cap in `manifest.json` `output_contract` |
| `sys.inbox.success.populated` | success | 0 | — | populated | Sensory events popped from the intake queue (cron/webhook sources; durable store TBD) |
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
| `sys.revoke.success.revoked` | success | 0 | — | revoked | Agent credentials killed |
| `sys.revoke.refusal.not_found` | refusal | 3 | validation | not_found | Target agent ID not found |
| `sys.vault_set.success.vaulted` | success | 0 | — | vaulted | AES-256-GCM secret encrypted |
| `sys.vault_set.refusal.missing_val` | refusal | 3 | missing_param | missing_arg | Target secret value omitted |
| `sys.vault_import.success.imported`| success| 0 | — | imported | Scanned and bound `CAPCLI_SECRET_*`|
| `sys.vault_import.refusal.no_env_vars`|refusal|3 | validation | not_found | No matching environment variables |
| `sys.doctor.success.nominal` | success | 0 | — | nominal | Host doctor readiness check |
| `sys.doctor.success.report` | success | 0 | — | report | Full YAML Trust Receipt |
| `sys.doctor.denial.drift` | denial | 2 | policy.authorizer | drift | Live DB differs from declaration |
| `sys.doctor.refusal.boot` | refusal | 3 | compile | missing_dep | Host missing python3.11 or supported sandbox provider |
| `sys.doctor.success.clock_drift`| success| 0 | — | clock_skew | Host clock delta >500ms vs NTP (warning only) |
| `sys.doctor.panic.tamper` | panic | 5 | kernel.panic | tampered | Total media loss: ledger root + WORM checkpoint unreadable; kill_and_alert |
| `sys.doctor.success.recovery` | success | 0 | — | recovery | Break-glass recovery mode |
| `sys.doctor.refusal.lockfile` | refusal | 3 | lockfile_mismatch | drift | Lockfile root hash mismatch |
| `sys.doctor.panic.quarantine`| panic | 5 | kernel.panic | tampered | Row-level chain tamper: sha256 link broken, block quarantined to `audit.quarantine.jsonl`; kernel halts boot (exit 5) until restore + WORM re-anchor |
| `sys.doctor.success.quarantine`| success | 0 | — | quarantine | Break-glass read-only quarantine ledger inspection (`CAPCLI_RECOVERY=1`); valid history verified |
| `sys.doctor.denial.thrashing` | denial | 2 | agent.thrashing| looping | 20 sustained denials in 5 minutes |
| `sys.backup.success.completed` | success | 0 | — | completed | Snapshot pushed to Git and S3 |
| `sys.backup.denial.push_fail` | denial | 2 | policy.authorizer | push_fail | Remote S3/Git push rejected |
| `sys.recover.success.restored` | success | 0 | — | restored | Reconstructed from object store |
| `sys.recover.refusal.not_found` | refusal | 3 | validation | not_found | Recovery snapshot missing |
| `sys.recover.denial.active_locks`| denial | 2 | db.claims | active_locks | Active locks prevent state reversal |
| `sys.exec.success.completed` | success | 0 | — | completed | Isolated command executed in jail |
| `sys.exec.denial.sandbox` | denial | 2 | kernel.sandbox | violation | Attempted unconfined escape |
| `sys.exec.crash.runtime` | crash | 4 | routine.runtime | crash | Executable process crash |
| `sys.serve.success.running` | success | 0 | — | running | IPC/WS/HTTP daemon active |
| `sys.serve.refusal.already_running`| refusal| 3 | compile | port_bound | Daemon process already running |
| `sys.serve.denial.port` | denial | 2 | db.engine | port_denied | Port 4040 binding rejected |

### 4.10 `doc/` (3 verbs → 6 screens)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `doc.read.success.populated` | success | 0 | — | populated | Full document returned bounded |
| `doc.read.success.sliced` | success | 0 | — | sliced | Progressive disclosure: leading sections under token cap; typed keyset envelope |
| `doc.read.refusal.not_found` | refusal | 3 | validation | not_found | Target document URP not found |
| `doc.outline.success.populated` | success | 0 | — | populated | Outline node tree with section indices |
| `doc.outline.refusal.not_found` | refusal | 3 | validation | not_found | Target document URP not found |
| `doc.inspect.success.populated` | success | 0 | — | populated | Document metadata, tokens, and node count |

### 4.11 `template/` (6 verbs → 15 screens)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `template.new.success.created` | success | 0 | — | created | Blueprint scaffold committed to templates/ |
| `template.new.refusal.name_taken` | refusal | 3 | validation | name_taken | Template name already registered |
| `template.new.refusal.shape_violation` | refusal | 3 | validation | shape_violation | Scaffold violates complexity or parameter bounds |
| `template.list.success.populated` | success | 0 | — | populated | Catalog of routine and world templates |
| `template.list.success.empty` | success | 0 | — | empty | Zero templates registered |
| `template.inspect.success.populated` | success | 0 | — | populated | Typed inputs, capabilities, and seed counts pre-flight |
| `template.inspect.refusal.not_found` | refusal | 3 | validation | not_found | Template URP does not resolve |
| `template.validate.success.valid` | success | 0 | — | valid | Passes Gate 1 (syntax) and Gate 2 (semantics) |
| `template.validate.refusal.syntax` | refusal | 3 | compile | syntax | Malformed YAML or Python syntax |
| `template.validate.refusal.compat` | refusal | 3 | policy.template | compat | min_kernel_version or policy version mismatch |
| `template.pack.success.packed` | success | 0 | — | packed | Bundle compiled to SHA-256 .cap archive |
| `template.pack.denial.size_limit` | denial | 2 | policy.template | size_limit | World template bundle exceeds 5MB ceiling |
| `template.apply.success.applied` | success | 0 | — | applied | Draft routine or dev environment scaffolded |
| `template.apply.refusal.missing_param` | refusal | 3 | missing_param | missing_param | Required template parameter -p omitted |
| `template.apply.denial.target_exists` | denial | 2 | policy.authoring | target_exists | Target file or environment already exists |

---

## 5. Canonical Screen Fixtures

Every fixture is a `wireframe/v2` root in `CliEnvelope` shape (envelope law: cans/physics.md#Diagnostic-output-law): `$schema`, `id`, `command`, `context {env, tier, trust}`, optional `audit_op`, `archetype`, `component`. Exactly one component per screen:

- `diagnostic` — states denial, refusal, crash, panic, yield (exits 2, 3, 4, 5, 6)
- `tree` — hierarchies, causal DAGs, inspection envelopes
- `receipt` — key-value summaries, reports, dry-run plans
- `document` — prose slices, keyset envelopes, help

Success screens classify by content: key-value summaries are `receipt`, hierarchies are `tree`, prose slices and help are `document`. The exit code derives from the `id` state segment; fixtures carry no `exit_code` and no `state_modified`. Carets, indents, branch glyphs, dividers, and key alignment are renderer output computed from component data; fixtures store none of them. The renderer (HTML canvas or Rust test harness) consumes the component and produces the terminal output. No separate `.txt` files exist in the repo. Each fixture below sits beside the terminal output its component renders; the harness asserts that output byte-for-byte (§6.2).

---

### 5.1 AST Blast-Radius Denial (`screens/run/sql/run.sql.denial.ast.json`)

Fixture (`wireframe/v2`):

```json
{
  "$schema": "wireframe/v2",
  "id": "run.sql.denial.ast",
  "target": "db://orders",
  "command": "capcli sql \"UPDATE orders SET status = 'shipped' WHERE status = 'processing'\" -m \"batch ship\"",
  "context": {
    "env": "dev",
    "tier": "tier_1",
    "trust": "draft"
  },
  "audit_op": "op_9f2e",
  "archetype": "diagnostic",
  "component": {
    "rule": "policy.query.update_delete.require_limit",
    "domain": "policy.ast",
    "layer": "AST",
    "culprit": "No LIMIT clause. Blast radius unbounded.",
    "measured": "matches potentially 847 rows (cap: 100)",
    "remedy": "add LIMIT, or target specific primary key",
    "span": {
      "source": "UPDATE orders SET status = 'shipped' WHERE status = 'processing'",
      "highlight": "sing'"
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

Fixture (`wireframe/v2`):

```json
{
  "$schema": "wireframe/v2",
  "id": "sys.trace.success.populated",
  "target": "op_7c4f",
  "command": "capcli sys audit trace op_7c4f --explain",
  "context": {
    "env": "dev",
    "tier": "tier_1",
    "trust": "draft",
    "data_shape": "populated"
  },
  "archetype": "tree",
  "component": {
    "title": "Causal DAG Trace (op_7c4f)",
    "root": "ses_a992f session.start \"fulfill urgent pending orders\"",
    "nodes": [
      {
        "label": "op_9f2c routine.dispatch_order@4",
        "children": [
          {
            "label": "op_9f2d db.query (orders) ✓ [allowed] 12ms",
            "children": []
          },
          {
            "label": "op_7c4f api.call (fedex.ship) ✓ [allowed] 340ms",
            "children": [
              {
                "label": "tracking 794644790133",
                "children": []
              }
            ]
          },
          {
            "label": "op_9f2f db.execute (orders) ✓ [allowed] 18ms",
            "children": [
              {
                "label": "status = 'shipped' (1 row)",
                "children": []
              }
            ]
          }
        ]
      }
    ],
    "footer": {
      "Root Intent": "\"fulfill urgent pending orders\"",
      "Authority": "user:alice (via agt_7f3k)",
      "Integrity": "valid hash link (chain verified)"
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
  Authority:   user:alice (via agt_7f3k)
  Integrity:   valid hash link (chain verified)
```

---

### 5.3 YAML Trust Receipt (`screens/sys/doctor/sys.doctor.success.report.json`)

Fixture (`wireframe/v2`):

```json
{
  "$schema": "wireframe/v2",
  "id": "sys.doctor.success.report",
  "target": "sys://host",
  "command": "capcli sys doctor --report",
  "context": {
    "env": "prod",
    "tier": "tier_1",
    "trust": "reviewed"
  },
  "archetype": "receipt",
  "component": {
    "title": "trust_receipt",
    "groups": [
      {
        "title": "trust_receipt",
        "fields": {
          "status": "nominal (witness anchoring pending)",
          "host_tier": "tier_1 (hardened Linux namespaces)",
          "workspace": "envs/prod/workspace.db",
          "ledger_root_hash": "sha256:7f9a1b2c4d8e001fa882bc19488a09b2e4f019c",
          "witness_store": "not configured — S3/R2 WORM probe unreachable (credentials absent from vault)",
          "worm_checkpoint": "pending — ledger root is local-only until the first object-store anchor",
          "audited_events": "14290 committed to _audit",
          "policy_denials": "18 (intercepted pre-execution; state untouched)",
          "unaudited_writes": "0",
          "secret_leaks": "0",
          "pinned_routines": "32",
          "active_triggers": "4 crons, 3 webhooks, 1 endpoint",
          "sleep_score": "100%"
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

Fixture (`wireframe/v2`):

```json
{
  "$schema": "wireframe/v2",
  "id": "run.inspect.success.routine",
  "target": "cap://dispatch_order@4",
  "command": "capcli inspect cap://dispatch_order@4",
  "context": {
    "env": "dev",
    "tier": "tier_1",
    "trust": "pinned",
    "data_shape": "populated"
  },
  "archetype": "receipt",
  "component": {
    "title": null,
    "groups": [
      {
        "fields": {
          "trust": "pinned",
          "runtime": "typescript (bun)",
          "params": "order_id: string, carrier: string",
          "description": "\"Dispatch paid order to carrier and update status\""
        }
      },
      {
        "fields": {
          "limits": "8 ops · 15s · 500 result tokens"
        }
      },
      {
        "lines": [
          "manifest:",
          "1. db.query    orders (read)",
          "2. api.call    logistics.shipments.create",
          "3. db.execute  orders (write)"
        ]
      },
      {
        "fields": {
          "can_invoke_now": "true",
          "session_ops_remaining": "488",
          "session_duration_remaining": "555000ms",
          "session_fuel_remaining": "80400",
          "session_egress_remaining": "4181824 bytes",
          "session_rate_remaining": "287",
          "tightest_constraint": "null"
        },
        "lines": [
          "budget_status:"
        ]
      },
      {
        "fields": {
          "max_nesting_depth": "5",
          "budget_inheritance": "min",
          "child_routines": "[]"
        },
        "lines": [
          "composition:"
        ]
      },
      {
        "fields": {
          "total_runs": "214",
          "success_rate": "99.1%",
          "p50_duration": "340ms",
          "p95_duration": "890ms",
          "last_run_at": "2m ago"
        },
        "lines": [
          "stats:"
        ]
      }
    ]
  },
  "affordances": [
    {
      "rel": "next",
      "command": "capcli routine new sync_orders",
      "intent": "Routine scaffold committed",
      "risk": "mutating",
      "requires_intent": true
    }
  ]
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

### 5.5 Dry-Run Schema Impact Plan (`screens/run/sql/run.sql.success.dry_run.json`)

Fixture (`wireframe/v2`):

```json
{
  "$schema": "wireframe/v2",
  "id": "run.sql.success.dry_run",
  "target": "db://orders",
  "command": "capcli sql \"ALTER TABLE orders ADD COLUMN priority integer DEFAULT 0\" --dry-run -m \"add priority flag for rush shipping\"",
  "context": {
    "env": "dev",
    "tier": "tier_1",
    "trust": "draft",
    "data_shape": "dry_run"
  },
  "archetype": "receipt",
  "component": {
    "title": null,
    "groups": [
      {
        "fields": {
          "statement": "ALTER TABLE orders ADD COLUMN priority integer DEFAULT 0",
          "ast_check": "pass",
          "authorizer": "pass (alter on orders allowed in dev)",
          "intent": "declared (\"add priority flag for rush shipping\")",
          "schema_impact": "+1 column (priority)",
          "estimated_rows": "4281",
          "blast_radius": "schema-only (non-destructive)"
        }
      },
      {
        "fields": {
          "note": "no execution occurred"
        }
      }
    ]
  },
  "affordances": [
    {
      "rel": "next",
      "command": "capcli sql \"SELECT id, customer_email, product_id, quantity, status, total FROM orders\"",
      "intent": "SELECT result bounded at 10,000 rows",
      "risk": "safe",
      "requires_intent": false
    }
  ]
}
```

Rendered output:

```text
[dev:tier_1]  dry-run  ✓

  statement:      ALTER TABLE orders ADD COLUMN priority integer DEFAULT 0
  ast_check:      pass
  authorizer:     pass (alter on orders allowed in dev)
  intent:         declared ("add priority flag for rush shipping")
  schema_impact:  +1 column (priority)
  estimated_rows: 4281
  blast_radius:   schema-only (non-destructive)

  state_modified: false
  note:           no execution occurred
```

---

### 5.6 Agent Thrashing Denial (`screens/sys/doctor/sys.doctor.denial.thrashing.json`)

Fixture (`wireframe/v2`):

```json
{
  "$schema": "wireframe/v2",
  "id": "sys.doctor.denial.thrashing",
  "target": "sys://host",
  "command": "capcli sys doctor",
  "context": {
    "env": "dev",
    "tier": "tier_1",
    "trust": "reviewed"
  },
  "archetype": "diagnostic",
  "component": {
    "domain": "agent.thrashing",
    "layer": "governance",
    "culprit": "agent agt_7f3k stuck in repetitive denial loop (rule: policy.query.update_delete.require_limit, target: db://orders)",
    "measured": "denials_last_5m: 22 (threshold: 20)",
    "remedy": "harness execution throttled; escalate to human or inspect remedy payload",
    "agent": "agt_7f3k",
    "denials_last_5m": "22",
    "rule_hit": "policy.query.update_delete.require_limit",
    "target": "db://orders",
    "harness_status": "stuck in repetitive denial loop"
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

Fixture (`wireframe/v2`):

```json
{
  "$schema": "wireframe/v2",
  "id": "run.execute.refusal.missing_secret",
  "target": "cap://stripe.refund_charge",
  "command": "capcli run cap://stripe.refund_charge -p charge_id=ch_1F2a9b -p amount_cents=8400 -m \"refund duplicate charge\"",
  "context": {
    "env": "dev",
    "tier": "tier_1",
    "trust": "draft"
  },
  "archetype": "diagnostic",
  "component": {
    "rule": "policy.secrets.missing",
    "domain": "policy.secrets",
    "layer": "vault",
    "culprit": "Credential 'stripe_secret_key' not found in vault.",
    "remedy": "prompt human supervisor to inject credential via Cockpit (http://127.0.0.1:4040/vault)",
    "capability": "cap://stripe.refund_charge",
    "secret_ref": "vault://stripe_secret_key"
  },
  "trailer": {
    "prompt": "prompt://budget/execution_starved@1",
    "reason": "missing secret refusal: vault credential absent",
    "serve": "L1"
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

Fixture (`wireframe/v2`):

```json
{
  "$schema": "wireframe/v2",
  "id": "run.execute.denial.network_jail",
  "target": "cap://sneaky_exfil@1",
  "command": "capcli run cap://sneaky_exfil@1 -p db_host=10.0.0.5:5432 -m \"replicate orders to analytics host\"",
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
    "culprit": "Raw connect() to 10.0.0.5:5432 trapped by seccomp-bpf filter (syscall 42).",
    "remedy": "use ctx.api.call with an activated catalog verb",
    "target": "10.0.0.5:5432",
    "caller": "routines/sneaky_exfil.py",
    "lines": [
      "syscall 42 (connect) trapped by seccomp-bpf"
    ]
  },
  "trailer": {
    "prompt": "prompt://budget/execution_starved@1",
    "reason": "network jail denial: sandbox egress trapped",
    "serve": "L1"
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

Fixture (`wireframe/v2`):

```json
{
  "$schema": "wireframe/v2",
  "id": "run.execute.yield.quota",
  "target": "cap://broadcast_newsletter@2",
  "command": "capcli run cap://broadcast_newsletter@2 -p audience=followers -m \"daily digest broadcast\"",
  "context": {
    "env": "prod",
    "tier": "tier_1",
    "trust": "pinned"
  },
  "archetype": "diagnostic",
  "component": {
    "rule": "policy.api.quota_exhausted",
    "domain": "api.quota",
    "culprit": "Provider quota exhausted: threads has 0/50 tokens left in the 24h window.",
    "remedy": "task safely yielded; daemon will auto-resume at reset_at",
    "tokens_left": "0 / 50 (24h window)",
    "reset_at": "18:00:00 UTC (in 4h 12m)",
    "suspended_frame": "task_99a8b1",
    "provider": "threads",
    "verb": "threads.create_media_post",
    "layer": "quota",
    "lines": [
      "routine broadcast_newsletter@2 (frame_018)"
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

Fixture (`wireframe/v2`):

```json
{
  "$schema": "wireframe/v2",
  "id": "sys.doctor.success.clock_drift",
  "target": "sys://host",
  "command": "capcli sys doctor",
  "context": {
    "env": "dev",
    "tier": "tier_1",
    "trust": "reviewed",
    "data_shape": "populated"
  },
  "archetype": "receipt",
  "component": {
    "title": null,
    "groups": [
      {
        "fields": {
          "⚠  clock drift warning": "host delta vs NTP is 840ms (warning threshold: 500ms)",
          "causal ordering unaffected": "intact"
        }
      },
      {
        "fields": {
          "host": "ws-07 (chronyd reachable, not yet synced)",
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

Fixture (`wireframe/v2`):

```json
{
  "$schema": "wireframe/v2",
  "id": "doc.read.success.sliced",
  "target": "doc://refund-policy",
  "command": "capcli doc read doc://refund-policy --max-tokens 100",
  "context": {
    "env": "dev",
    "tier": "tier_1",
    "trust": "pinned",
    "data_shape": "truncated"
  },
  "archetype": "document",
  "component": {
    "header_badge": "doc://refund-policy (sections 1-2 of 5)",
    "pagination": {
      "items": [
        {
          "section": 1,
          "heading": "Scope",
          "tokens": 22
        },
        {
          "section": 2,
          "heading": "Refund windows",
          "tokens": 74
        }
      ],
      "next_cursor": "doc://refund-policy#3",
      "has_more": true
    },
    "meta": {
      "document": "doc://refund-policy",
      "tokens": "96 (cap: 100)",
      "has_more": true,
      "next_cursor": "doc://refund-policy#3"
    },
    "body": [
      "1. Scope",
      "Refund routing and approval rules for the storefront.",
      "2. Refund windows",
      "Standard window is 30 days. Extended window is 120 days and requires",
      "supervisor approval."
    ]
  },
  "affordances": [
    {
      "rel": "next",
      "command": "capcli doc outline doc://refund-policy",
      "intent": "Outline node tree with section indices",
      "risk": "safe",
      "requires_intent": false
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

Fixture (`wireframe/v2`):

```json
{
  "$schema": "wireframe/v2",
  "id": "sys.help.success.stub",
  "command": "capcli",
  "context": {
    "env": "dev",
    "tier": "tier_1",
    "trust": "reviewed"
  },
  "archetype": "document",
  "component": {
    "header_badge": "capcli 0.4.2 — compiled execution firewall for AI agents",
    "fields": {
      "Find actions": "capcli search <query>",
      "Pre-flight": "capcli inspect <urp>",
      "System status": "capcli sys doctor"
    },
    "body": [
      "Usage: capcli <noun> <verb> [target] [flags]",
      "Capabilities are discovered dynamically, not listed in static help."
    ]
  },
  "trailer": {
    "prompt": "prompt://onboarding/human@1",
    "reason": "human operator requested onboarding tour",
    "serve": "L1"
  },
  "affordances": [
    {
      "rel": "next",
      "command": "capcli sys doctor --boot-check",
      "intent": "Host doctor readiness check",
      "risk": "safe",
      "requires_intent": false
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

## 6. Fixture Schema & Rust Test Runner Contract

### 6.1 Screen Fixture Schema (`screens/run/sql/run.sql.denial.ast.json`)

A fixture JSON is the serialized `CliEnvelope` payload of the screen and the
single source the renderer consumes (envelope law: cans/physics.md#Diagnostic-output-law).
The root carries the invocation, the runtime context, the audit op, and exactly
one layout component. The HTML canvas and the Rust test harness both render from
this shape. No separate `.txt` file exists.

```json
{
  "$schema": "wireframe/v2",
  "id": "run.sql.denial.ast",
  "command": "capcli sql \"UPDATE orders SET status = 'shipped' WHERE status = 'processing'\" -m \"batch ship\"",
  "context": { "env": "dev", "tier": "tier_1", "trust": "draft" },
  "audit_op": "op_9f2e",
  "archetype": "diagnostic",
  "component": {
    "rule": "policy.query.update_delete.require_limit",
    "domain": "policy.ast",
    "layer": "AST",
    "span": {
      "source": "UPDATE orders SET status = 'shipped' WHERE status = 'processing'",
      "highlight": "processing"
    },
    "culprit": "No LIMIT clause. Blast radius unbounded.",
    "measured": "matches potentially 847 rows (cap: 100)",
    "remedy": "add LIMIT, or target specific primary key"
  }
}
```

Root field law:

- `$schema` is `wireframe/v2`. `id` is the screen identity; noun and verb are its first two segments and appear nowhere else.
- `command` states the invocation the screen answers; any target pointer lives inside the command string.
- `target` names the single invocation target when the command carries one (248/259 fixtures on disk) and is absent on targetless commands.
- `context` is the `CliEnvelope` context frame: `env`, `tier`, `trust`, plus optional `data_shape` (63/259 fixtures on disk). The renderer derives the `[{env}:{tier}]` badge from it.
- `audit_op` names the audit operation the envelope reports. It appears when the screen reports one and is absent otherwise.
- `archetype` is exactly one of `diagnostic`, `tree`, `receipt`, `document` (archetype law: cans/physics.md#Diagnostic-output-law). `component` carries that archetype's payload and nothing else.
- `trailer` appears only on screens named in `_triggers.json` (§6.1.1).
- `affordances` is an optional root key on exit-0 fixtures only (state segment `success`; archetype `receipt`, `tree`, or `document`). Each entry is `{ rel, command, intent, risk, requires_intent }` (cans/interface.md#CLI-surface Success affordances); `command` is the target screen's fixture `command` string verbatim, sourced from `_flows.json` transitions, and `risk` is `mutating` exactly when `requires_intent` is `true`. It is a machine envelope key: renderers never emit it as a human output line, and its presence or absence changes no exit, state, or payload byte. Shape: `output_contract.affordances.machine_schema` in `manifest.json`.

Derived-state law:

- The exit code derives from the `id` state segment: `success` 0, `denial` 2, `refusal` 3, `crash` 4, `panic` 5, `yield` 6. Fixtures carry no `exit_code`; state and domain legality lives in `_states.json`.
- Fixtures carry no `state_modified`. A non-zero exit carries `state_modified: false` as a kernel invariant (cans/physics.md#Exit-code-law). Success screens take `state_modified` from the exit-0 variants in `_states.json` (`committed`, `dry_run`, `suspended`, `resumed`). A renderer emits a `state_modified` row from the derived value only; the fixture never stores it.
- A stored `state_modified` key at envelope root, inside `component.groups[].fields`, inside `component.footer`, or inside `component.fields` carries the same ban at every depth; `_states.json` and the exit are the single home of the value.
- A diagnostic component carries `domain` once, in the component. Success components carry no `domain`.
- Archetype dispatch is deterministic: states `denial`, `refusal`, `crash`, `panic`, `yield` are `diagnostic`; `success` resolves to `receipt`, `tree`, or `document` by content (key-value summary, hierarchy, prose slice or help).
- Visual typography is renderer output, never fixture data: caret strings and their column offsets, indentation, tree branch glyphs (`├──`, `└──`, `│`), divider lines (`─`), and key-column alignment are computed by the component renderers from component data.

Component law:

- **diagnostic** — `{ rule?, domain, layer?, span?, culprit, measured?, remedy, lines?, suspended_frame?, tokens_left?, reset_at?, ask_id?, pending_asks?, ...fields }`. `domain`, `culprit`, and `remedy` are present on every diagnostic fixture (137/137 on disk); `remedy` is a single string. `rule` (116/137 on disk) is the violated rule id, stored once here; `layer` (73/137 on disk) names the enforcement layer. Required fields per exit live in `_states.json` `diagnostic_required` and every fixture carries its exit's required set. `span` is `{ source, highlight?, detail? }`: `source` is the offending source text, `highlight` is the exact substring the renderer underlines with carets at its computed offset, `detail` carries indented span context lines. `measured` cites the measured value on denials that carry one. `lines` is an optional array of verbatim content strings (96/137 on disk). Every other key at component root is a screen-specific field row captured by the flattened fields map; no diagnostic fixture carries a nested `fields` key (0/137 on disk), and field values are strings or list values. A flattened key is the rendered field label: one complete label, never a truncated sentence fragment; the value carries the data. Exit 6 components additionally carry `suspended_frame`, plus the domain fields registered in `_states.json` (`api.quota` → `tokens_left`, `reset_at`; `ping.ask` → `ask_id`, `pending_asks`).
- **tree** — `{ title, root, nodes, footer? }`. `title` is the header line after the badge. `root` is a string (19/19 on disk): the rendered root line. `nodes` is an ordered array of `{ label, children }` (121 nodes on disk); `children` recurses with the same shape and is present on every node, empty at leaves. The renderer computes indentation and branch glyphs from nesting; the node label carries the full line text. `footer` is an optional ordered key-value block rendered after the walk.
- **receipt** — `{ title, groups }`. `title` renders as the receipt heading and is `null` on fixtures that carry no heading (87/93 null, 6/93 string on disk). `groups` is an ordered array of `{ title?, fields?, lines? }` (190 groups on disk): `title` renders as the group's heading line (8/190 on disk; a `name` key appears on 0/190), `fields` is an ordered key-value map the renderer aligns into label columns (160/190), `lines` carries verbatim content lines the renderer indents under the group (55/190). Key order in `fields` is render order.
- **document** — `{ header_badge, pagination?, meta?, fields?, body }`. `header_badge` is the document header line after the context badge. `pagination` is the keyset envelope of a truncated or sliced payload (§6.1.2). `meta` is an ordered key-value map (9/10 on disk) carrying slice accounting and the pagination cursor mirror. `fields` is an ordered key-value map (9/10 on disk) carrying the screen's rows. `body` is an ordered array of prose strings (10/10 on disk); the renderer emits divider lines and wraps body text.

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
`wireframe/v2` fixture the slot is the root key `trailer`, beside `component` —
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

### 6.2 Rust Integration Test Runner

Status: spec contract. The repository carries no `crates/` tree; the Python
validator enforces the checks in this section until the Rust harness exists.
No golden `.txt` files; the fixture component IS the golden source.

The runner deserializes every fixture as an `AtomicFixture`, renders the
expected terminal output procedurally from its component, dispatches the
command against the real binary, and asserts byte-identical stdout plus the
exit code derived from the fixture `id`. Diagnostic spans render through the
kernel's `miette` / `codespan` pipeline, so fixtures validate the real CLI
formatting engine.

```rust
// crates/capcli-cli/tests/e2e/test_wireframe_fixtures.rs — contract path; no crates/ tree exists in the repo today

use std::fs;
use std::path::Path;
use glob::glob;
use serde::Deserialize;

/// Runtime context frame — mirrors `context` in every fixture (§6.1).
#[derive(Deserialize)]
struct Context {
    env: String,
    tier: String,
    trust: String,
    data_shape: Option<String>,
}

/// Semantic span. Caret runs and offsets are computed at render time
/// from `source` + `highlight`; fixtures store neither.
#[derive(Deserialize)]
struct Span {
    source: String,
    highlight: Option<String>,
    detail: Option<String>,
}

/// Archetype A payload (§6.1 component law). Required fields per exit
/// live in `_states.json` `diagnostic_required`; every fixture carries
/// its exit's set. Screen-specific field rows are flattened at component
/// root (see `fields`); no fixture carries a nested `fields` key.
#[derive(Deserialize)]
struct DiagnosticComponent {
    rule: Option<String>,
    domain: String,
    layer: Option<String>,
    span: Option<Span>,
    culprit: String,
    measured: Option<String>,
    remedy: String,
    lines: Option<Vec<String>>,
    suspended_frame: Option<String>,
    tokens_left: Option<String>,
    reset_at: Option<String>,
    ask_id: Option<String>,
    pending_asks: Option<String>,
    #[serde(flatten)]
    fields: serde_json::Map<String, serde_json::Value>,
}

/// Archetype B node; `children` recurses and is present on every node,
/// empty at leaves. Branch glyphs and indentation are computed at
/// render time from nesting; the label carries the full line text.
#[derive(Deserialize)]
struct TreeNode {
    label: String,
    #[serde(default)]
    children: Vec<TreeNode>,
}

/// Archetype B root: the rendered root line as a plain string.
type TreeRoot = String;

/// Archetype B payload (§6.1 component law).
#[derive(Deserialize)]
struct TreeComponent {
    title: String,
    root: TreeRoot,
    nodes: Vec<TreeNode>,
    footer: Option<serde_json::Map<String, serde_json::Value>>,
}

/// Archetype C group; key order in `fields` is render order.
#[derive(Deserialize)]
struct ReceiptGroup {
    title: Option<String>,
    fields: Option<serde_json::Map<String, serde_json::Value>>,
    lines: Option<Vec<String>>,
}

/// Archetype C payload (§6.1 component law). `title` is `null` on
/// fixtures that carry no heading.
#[derive(Deserialize)]
struct ReceiptComponent {
    title: Option<String>,
    groups: Vec<ReceiptGroup>,
}

/// Archetype D pagination envelope (§6.1.2): typed leading items plus
/// the keyset cursor state. Every truncated or sliced screen on disk is
/// a `document` carrying this object.
#[derive(Deserialize)]
struct DocumentPagination {
    items: Vec<serde_json::Value>,
    next_cursor: String,
    has_more: bool,
}

/// Archetype D payload (§6.1 component law). `meta` carries slice
/// accounting and the pagination cursor mirror; `fields` carries the
/// screen's rows. Both are ordered key-value maps.
#[derive(Deserialize)]
struct DocumentComponent {
    header_badge: String,
    pagination: Option<DocumentPagination>,
    meta: Option<serde_json::Map<String, serde_json::Value>>,
    fields: Option<serde_json::Map<String, serde_json::Value>>,
    body: Vec<String>,
}

/// The four layout components, dispatched on the `archetype` key.
#[derive(Deserialize)]
#[serde(tag = "archetype", content = "component")]
enum ComponentPayload {
    #[serde(rename = "diagnostic")]
    Diagnostic(DiagnosticComponent),
    #[serde(rename = "tree")]
    Tree(TreeComponent),
    #[serde(rename = "receipt")]
    Receipt(ReceiptComponent),
    #[serde(rename = "document")]
    Document(DocumentComponent),
}

/// Exit-0 next action (§6.1 root field law; cans/interface.md#CLI-surface
/// Success affordances). The command is a fixture command string verbatim.
#[derive(Deserialize)]
struct Affordance {
    rel: String,
    command: String,
    intent: String,
    risk: String,
    requires_intent: bool,
}

/// Root fixture: a serialized CliEnvelope payload (§6.1).
/// Exit code and state_modified are derived, never stored.
#[derive(Deserialize)]
struct AtomicFixture {
    #[serde(rename = "$schema")]
    schema: String,
    id: String,
    target: Option<String>,
    command: String,
    context: Context,
    audit_op: Option<String>,
    #[serde(flatten)]
    payload: ComponentPayload,
    trailer: Option<serde_json::Value>,
    affordances: Option<Vec<Affordance>>,
}

impl AtomicFixture {
    /// Exit code law: derived from the `id` state segment (§6.1).
    fn expected_exit_code(&self) -> i32 {
        match self.id.split('.').nth(2) {
            Some("success") => 0,
            Some("denial") => 2,
            Some("refusal") => 3,
            Some("crash") => 4,
            Some("panic") => 5,
            Some("yield") => 6,
            other => panic!("{}: illegal state segment {:?}", self.id, other),
        }
    }
}

/// Procedural component renderers — the single source of terminal layout.
/// Carets, indents, branch glyphs, dividers, and key alignment exist only here.
fn render_diagnostic(context: &Context, c: &DiagnosticComponent) -> String;
fn render_tree(context: &Context, c: &TreeComponent) -> String;
fn render_receipt(context: &Context, c: &ReceiptComponent) -> String;
fn render_document(context: &Context, c: &DocumentComponent) -> String;

fn render_fixture(fixture: &AtomicFixture) -> String {
    match &fixture.payload {
        ComponentPayload::Diagnostic(c) => render_diagnostic(&fixture.context, c),
        ComponentPayload::Tree(c) => render_tree(&fixture.context, c),
        ComponentPayload::Receipt(c) => render_receipt(&fixture.context, c),
        ComponentPayload::Document(c) => render_document(&fixture.context, c),
    }
}

#[test]
fn execute_wireframe_golden_tests() {
    let root = Path::new("cans/artifacts/wireframe/screens");

    for entry in glob(&format!("{}/**/*.json", root.display())).unwrap() {
        let json_path = entry.unwrap();
        let content = fs::read_to_string(&json_path).unwrap();
        let fixture: AtomicFixture = serde_json::from_str(&content).unwrap();

        // 1. Procedural render of the component = expected stdout
        let expected = render_fixture(&fixture);

        // 2. Dispatch the fixture's command against the real binary
        let output = capcli_test_exec(&fixture.command);

        // 3. Derived-state assertions (§6.1): exit code from the id,
        //    state_modified from the kernel invariant.
        assert_eq!(output.exit_code, fixture.expected_exit_code(),
            "Exit mismatch at {}", fixture.id);
        if fixture.expected_exit_code() != 0 {
            assert_eq!(output.state_modified, false,
                "state_modified invariant failed at {}", fixture.id);
        }

        // 4. Golden rendering: stdout is byte-identical to the
        //    procedural component render.
        assert_eq!(output.stdout, expected,
            "Render mismatch at {}", fixture.id);

        // 5. Global negatives (asserted once here for all screens)
        for banned in ["--force", "--override-budget", "--force-prod", "--verbose"] {
            assert!(!output.stdout.contains(banned),
                "{}: banned token '{}'", fixture.id, banned);
        }
        assert!(!output.stdout.contains('|'),
            "{}: pipe character forbidden", fixture.id);
        if fixture.trailer.is_none() {
            assert!(!output.stdout.contains("trailer:"),
                "{}: trailer on fixture with no trailer", fixture.id);
        }

        assert!(output.stderr.is_empty(),
            "{}: unexpected stderr: {}", fixture.id, output.stderr);
    }
}
```

Trailer checks, applied by the runner to every fixture:

Trailer presence on a screen is decided solely by `cans/artifacts/prompt/_triggers.json`. This section carries no trailer-screen list.

Predicate branches on a single screen are trigger-level tests: the runner evaluates each `_triggers.json` predicate for that screen against the runtime context and asserts the selected pointer, the fixture carries the one trailer instance for the branch its context represents, and no second fixture for the same screen id is created for another branch.

a. **Schema.** A `trailer` payload validates against `machine_schema` in `manifest.json`.
b. **Position.** The human trailer is the final rendered line; the machine trailer is an additive envelope key.
c. **State neutrality.** For every trailer-carrying fixture, a twin assertion runs the same command with no trailer: output is identical except the trailer line/key is absent.
d. **Correspondence.** Every `_triggers.json` entry resolves to a fixture on disk, and every `_flows.json` transition endpoint resolves to a fixture.
e. **Negative space.** A fixture with no `trailer` renders no `trailer:` line and no `next_action` key.

Cross-layer referential test:

```rust
#[test]
fn assert_prompt_triggers_match_wireframe_screens() {
    let triggers_raw = fs::read_to_string("cans/artifacts/prompt/_triggers.json").unwrap();
    let triggers: serde_json::Value = serde_json::from_str(&triggers_raw).unwrap();

    for t in triggers["triggers"].as_array().unwrap() {
        let screen_id = t["screen_id"].as_str().unwrap();
        let parts: Vec<&str> = screen_id.split('.').collect();
        let path = format!(
            "cans/artifacts/wireframe/screens/{}/{}/{}.json",
            parts[0], parts[1], screen_id
        );
        assert!(Path::new(&path).exists(),
            "Trigger {} references missing fixture: {}", t["id"], path);
    }
}
```

---

## 7. Edgeless Playable Canvas Implementation (`wireframe.html`)

The HTML canvas renders all screens directly from `.json` fixture shapes. No `.txt` files are fetched. `TerminalPanel` implements the four component renderers defined in §6.1 (`diagnostic`, `tree`, `receipt`, `document`); it consumes component payloads, and carets, branch glyphs, dividers, and alignment are its output.

```
zoomable, node draggable, click inspect (renders from json shape), scenario select to highlight the flows in canvas
```