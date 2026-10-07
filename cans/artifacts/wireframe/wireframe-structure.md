# Canonical Wireframe, State Machine & Flow Engine Specification

---

## 1. Directory Tree & Architecture

The wireframe layer serves a dual purpose: an **interactive edgeless canvas** for humans and harnesses, and a **deterministic golden-file test fixture suite** for the Rust kernel.

Flow graphs, journey definitions, and multi-branch transition metadata are codified into `_flows.json`. Individual screen fixtures remain atomic, stateless, and congruent with runtime compiler and authorizer output.

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
```

### 1.1 Structural Invariants
* **Active Nouns:** Exactly 10 CLI nouns (`run`, `db`, `routine`, `api`, `bind`, `ping`, `rule`, `env`, `sys`, `doc`).
* **Pairing Law:** Every `.json` fixture has an identical `.txt` companion in the same folder. No orphan files. No empty directories.
* **Depth Ceiling:** File paths relative to `screens/` must remain exactly 3 path components: `{noun}/{verb}/{filename}`.
* **Sibling Invariants:** Min 3, max 16 verb directories per noun branch node.
* **Naming Law:** Strict 4-segment token syntax:
  ```
  {noun}.{verb}.{state}.{condition}.{json|txt}
  ```

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

Every screen ID referenced by a flow must exist as a fixture pair under `screens/` and as a row in §4 — the validator enforces closure. Flow prose in §5 quotes individual screens for walkthroughs; the routing itself lives only in `_flows.json`.

---

## 4. Complete Screen Inventory & State Matrix

This table is a context index: one scannable surface a reader loads
before drilling into fixture pairs. It indexes; it does not originate.
Fixture pairs under `screens/` are the source, `_states.json` owns
state and domain legality, and `_flows.json` owns routing. Every row
resolves to one fixture pair and every fixture pair has one row —
the validator enforces closure, and in any conflict the fixture wins.


### 4.1 `run/` (5 verbs $\\rightarrow$ 37 screen pairs)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `run.execute.success.populated` | success | 0 | — | populated | Deterministic execution and commit |
| `run.execute.success.redirected` | success | 0 | — | redirected | Payload directed to file via `--out`; stdout emits receipt |
| `run.execute.success.truncated` | success | 0 | — | truncated | Result $>500$ tokens; returns `next_cursor` |
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
| `run.sql.refusal.missing_intent` | refusal | 3 | compile | no_intent | Mutating write missing `-m` / `--intent` |
| `run.overview.success.populated` | success | 0 | — | populated | Situational KPI briefing ($<500$ tokens) |
| `run.overview.success.truncated` | success | 0 | — | truncated | Oversized overview clipped |
| `run.search.success.populated` | success | 0 | — | populated | Matched capabilities and URP pointers |
| `run.search.success.empty` | success | 0 | — | empty | Zero hits; outputs semantic suggestions |
| `run.search.success.truncated` | success | 0 | — | truncated | Search results capped at 20 |
| `run.search.success.gaps` | success | 0 | — | gaps | Surfaces missing capabilities via `--since` |
| `run.inspect.success.routine` | success | 0 | — | populated | Pre-flight envelope with `can_invoke_now` |
| `run.inspect.success.quota` | success | 0 | — | populated | Headroom breakdown on `quota://` URP |
| `run.inspect.success.template` | success | 0 | — | populated | Inspection envelope on `tpl://` blueprint |
| `run.inspect.refusal.missing_ptr` | refusal | 3 | missing_param | missing_arg | Unrecognized target pointer format |
| `run.inspect.denial.trust` | denial | 2 | policy.trust | unreadable | Draft routine secret inspection denied |

### 4.2 `db/` (6 verbs $\\rightarrow$ 14 screen pairs)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `db.lock.success.acquired` | success | 0 | — | acquired | Exclusive claim lease registered |
| `db.lock.denial.claim_held` | denial | 2 | db.claims | held | Target resource currently claimed |
| `db.lock.refusal.missing_reason` | refusal | 3 | validation | missing_arg | `--reason` required for locking |
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

### 4.3 `routine/` (8 verbs $\\rightarrow$ 26 screen pairs)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `routine.new.success.created` | success | 0 | — | created | Routine scaffold committed |
| `routine.new.refusal.name_taken` | refusal | 3 | validation | collision | Routine name already registered |
| `routine.new.refusal.shape_violation` | refusal | 3 | validation | bad_shape | Scaffold violates LOC or param limits |
| `routine.new.refusal.template_compat` | refusal | 3 | policy.template | compat_fail | Template policy_version mismatch exits 3 |
| `routine.prove.success.passed` | success | 0 | — | passed | Dynamic fingerprint verified |
| `routine.prove.denial.shape` | denial | 2 | policy.authorizer | bad_shape | Execution violates declared limits |
| `routine.prove.denial.policy` | denial | 2 | policy.authorizer | illegal_leaf | Routine attempts forbidden leaf op |
| `routine.prove.denial.sandbox` | denial | 2 | kernel.sandbox | breach | Jail containment boundary violation |
| `routine.prove.crash.runtime` | crash | 4 | routine.runtime | exception | Uncaught exception in test pass |
| `routine.ship.success.shipped` | success | 0 | — | shipped | Routine promoted to new trust rung |
| `routine.ship.success.rolled_back` | success | 0 | — | rolled_back | Canary telemetry trips auto-rollback |
| `routine.ship.denial.metrics` | denial | 2 | policy.authorizer | low_success | Success rate falls below 0.95 |
| `routine.ship.refusal.missing_reason`| refusal | 3 | validation | missing_arg | Elevation to pinned requires reason |
| `routine.ship.denial.trust` | denial | 2 | policy.trust | tier2_refusal | Pinned promotion denied on Tier 2 |
| `routine.pending.success.populated` | success | 0 | — | populated | Batch promotion candidates listed |
| `routine.pending.success.empty` | success | 0 | — | empty | No routines pending promotion |
| `routine.sweep.success.populated` | success | 0 | — | populated | Deduplication proposals generated |
| `routine.sweep.success.empty` | success | 0 | — | empty | No duplicate routines detected |
| `routine.stats.success.populated` | success | 0 | — | populated | Routine p50/p95 execution metrics |
| `routine.stats.refusal.not_found` | refusal | 3 | validation | not_found | Routine name does not exist |
| `routine.rollback.success.completed`| success | 0 | — | completed | Reverts pointer to prior version |
| `routine.rollback.denial.depth` | denial | 2 | policy.authorizer | depth_limit | Exceeds max rollback depth of 5 |
| `routine.rollback.refusal.not_found`| refusal | 3 | validation | not_found | Target version not found in history |
| `routine.retire.success.completed` | success | 0 | — | completed | Routine retired from service |
| `routine.retire.denial.active_deps` | denial | 2 | policy.authorizer | deps_exist | Callee dependencies block retirement |
| `routine.retire.refusal.not_found` | refusal | 3 | validation | not_found | Target routine does not exist |

### 4.4 `api/` (8 verbs $\\rightarrow$ 23 screen pairs)

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
| `api.ship.refusal.missing_reason` | refusal | 3 | validation | missing_arg | Missing elevation justification |
| `api.stats.success.populated` | success | 0 | — | populated | Quota usage and error metrics |
| `api.stats.refusal.not_found` | refusal | 3 | validation | not_found | Target provider not found |
| `api.retire.success.completed` | success | 0 | — | completed | API verb deactivated to dormant |
| `api.retire.refusal.not_found` | refusal | 3 | validation | not_found | Target verb not found |
| `api.rollback.success.completed` | success | 0 | — | completed | Reverts API spec to prior hash |
| `api.rollback.denial.depth` | denial | 2 | policy.authorizer | depth_limit | Exceeds max rollback limit of 5 |
| `api.rollback.refusal.not_found` | refusal | 3 | validation | not_found | Target version not found |

### 4.5 `bind/` (10 verbs $\\rightarrow$ 26 screen pairs)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `bind.cron.success.bound` | success | 0 | — | bound | Schedule bound to routine |
| `bind.cron.denial.cap` | denial | 2 | policy.authorizer | cap_exceeded| Max 20 active schedules reached |
| `bind.cron.denial.interval` | denial | 2 | policy.authorizer | interval_low| Interval lower than 5-minute cap |
| `bind.cron.refusal.missing_intent` | refusal | 3 | compile | no_intent | Missing intent flag |
| `bind.webhook.success.bound` | success | 0 | — | bound | Inbound hook route activated |
| `bind.webhook.denial.cap` | denial | 2 | policy.authorizer | cap_exceeded| Max 50 active hooks reached |
| `bind.webhook.denial.unsigned` | denial | 2 | policy.authorizer | unsigned | Unsigned hooks rejected |
| `bind.webhook.denial.payload_size` | denial | 2 | policy.authorizer | too_large | Hook payload exceeds 64KB |
| `bind.webhook.refusal.missing_ingress`| refusal| 3 | compile | no_ingress | Missing public ingress URL/tunnel |
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

### 4.6 `ping/` (5 verbs $\\rightarrow$ 14 screen pairs)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `ping.notify.success.dispatched` | success | 0 | — | dispatched | Notification dispatched |
| `ping.notify.denial.quiet_hours` | denial | 2 | policy.authorizer | quiet_hours | Blocked between 22:00 and 07:00 |
| `ping.notify.refusal.missing_intent` | refusal | 3 | compile | no_intent | Missing intent declaration |
| `ping.ask.success.suspended` | success | 0 | — | suspended | Human question queued with Cockpit URL |
| `ping.ask.denial.options_cap` | denial | 2 | policy.authorizer | cap_exceeded| Exceeds 5 structured choices |
| `ping.ask.refusal.missing_intent` | refusal | 3 | compile | no_intent | Missing intent declaration |
| `ping.list.success.populated` | success | 0 | — | populated | Pending suspension questions |
| `ping.list.success.empty` | success | 0 | — | empty | Zero pending inquiries |
| `ping.resolve.success.resolved` | success | 0 | — | resolved | Choice selected; resumes task |
| `ping.resolve.denial.occ_conflict`| denial | 2 | db.engine | stale_state | Touched rows modified during suspension; OCC fence violated |
| `ping.resolve.refusal.not_found` | refusal | 3 | validation | not_found | Invalid ask ID |
| `ping.resolve.denial.expired` | denial | 2 | policy.notify | expired | Timeout elapsed; fail-closed |
| `ping.expire.success.completed` | success | 0 | — | completed | Explicit expiration executed |
| `ping.expire.refusal.not_found` | refusal | 3 | validation | not_found | Target inquiry not found |

### 4.7 `rule/` (4 verbs $\\rightarrow$ 12 screen pairs)

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

### 4.8 `env/` (7 verbs $\\rightarrow$ 20 screen pairs)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `env.new.success.created` | success | 0 | — | created | New worktree namespace created |
| `env.new.denial.cap` | denial | 2 | policy.authorizer | cap_exceeded| Max 5 environments reached |
| `env.new.refusal.name_taken` | refusal | 3 | validation | collision | Environment name exists |
| `env.new.refusal.bundle_too_large` | refusal | 3 | policy.template | size_overflow | Bundle exceeds 5MB ceiling |
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
| `env.merge.refusal.unmerged` | refusal | 3 | compile | unmerged | Git branch conflict blocks DDL forwarding: env branches diverge on schema declaration |
| `env.remove.success.removed` | success | 0 | — | removed | Environment dismantled |
| `env.remove.denial.prod_flags` | denial | 2 | policy.authorizer | prod_flags | Prod removal requires dual confirmation flags; neither was present |
| `env.remove.denial.crypto_sig` | denial | 2 | policy.authorizer | confirmation | Prod requires out-of-band challenge signature |
| `env.remove.refusal.not_found` | refusal | 3 | validation | not_found | Target environment not found |

### 4.9 `sys/` (16 verbs $\\rightarrow$ 45 screen pairs)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `sys.help.success.stub` | success | 0 | — | stub | 6-line minimalist help stub redirecting to search |
| `sys.inbox.success.populated` | success | 0 | — | populated | Sensory events popped from queue |
| `sys.inbox.success.empty` | success | 0 | — | empty | Sensory inbox completely drained |
| `sys.tail.success.populated` | success | 0 | — | populated | Live streaming audit records |
| `sys.tail.success.empty` | success | 0 | — | empty | No audit events within window |
| `sys.trace.success.populated` | success | 0 | — | populated | Causal DAG walk with `--explain` tree |
| `sys.trace.refusal.not_found` | refusal | 3 | validation | not_found | Target operation ID missing |
| `sys.query.success.populated` | success | 0 | — | populated | SQL executed against `_audit` |
| `sys.query.success.empty` | success | 0 | — | empty | Zero matching audit rows |
| `sys.query.refusal.unparseable`| refusal | 3 | compile | bad_syntax | Malformed SQL audit query |
| `sys.replay.success.replayed` | success | 0 | — | replayed | Deterministic execution from log |
| `sys.replay.denial.external` | denial | 2 | policy.authorizer | external_op | HTTP calls require manual flag |
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
| `sys.doctor.refusal.boot` | refusal | 3 | compile | missing_dep | Host missing python3.11 or supported sandbox provider (bwrap/crun/microvm) |
| `sys.doctor.success.clock_drift`| success| 0 | — | clock_skew | Host clock delta $>500$ms vs NTP (warning only; monotonic fallback active) |
| `sys.doctor.panic.tamper` | panic | 5 | kernel.panic | tampered | Audit SHA-256 chain broken with quarantine sink unreachable; kill_and_alert, boot refused |
| `sys.doctor.success.recovery` | success | 0 | — | recovery | Break-glass recovery mode (CAPCLI_RECOVERY=1): policy disabled, audit sink online, diagnostics only |
| `sys.doctor.refusal.lockfile` | refusal | 3 | lockfile_mismatch | drift | Lockfile root hash mismatch |
| `sys.doctor.success.tamper` | success | 0 | — | tampered | Audit SHA-256 chain broken; corrupted block isolated to quarantine |
| `sys.doctor.success.quarantine`| success | 0 | — | quarantine | Quarantine ledger inspection active |
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

### 4.10 `doc/` (3 verbs $\\rightarrow$ 6 screen pairs)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `doc.read.success.populated` | success | 0 | — | populated | Full document returned bounded |
| `doc.read.success.sliced` | success | 0 | — | sliced | Progressive disclosure: section + token cap |
| `doc.read.refusal.not_found` | refusal | 3 | validation | not_found | Target document URP not found |
| `doc.outline.success.populated` | success | 0 | — | populated | Outline node tree with section indices |
| `doc.outline.refusal.not_found` | refusal | 3 | validation | not_found | Target document URP not found |
| `doc.inspect.success.populated` | success | 0 | — | populated | Document metadata, tokens, and node count |

---

## 5. Canonical Screen Fixtures

Every terminal transcript follows strict typographic rules:
1. **Header Badge:** Standardized `[{env}:{tier}]` runtime context prefix.
2. **Visual Spans:** Source SQL or parameters underlined with carets (`^^^^`) directly pinpointing violations.
3. **Indented Blocks:** Two-space hierarchical indentation; clean label columns.
4. **Dividers:** Horizontal character lines (`─`) for separation. No random vertical pipe borders.
5. **Machine/Human Duality:** Clean human presentation by default; JSON structure strictly matches `--json`.

---

### 5.1 AST Blast-Radius Denial (`screens/run/sql/run.sql.denial.ast.txt`)

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

### 5.2 Causal DAG Tree Walk (`screens/sys/trace/sys.trace.success.populated.txt`)

```text
[dev:tier_1]  Causal DAG Trace (op_9f2e)

  ses_a992f  session.start        "fulfill urgent pending orders"
  └── op_9f2c  routine.dispatch_order@4
        ├── op_9f2d  db.query (orders)         ✓ [allowed]  12ms
        ├── op_9f2e  api.call (fedex.ship)     ✓ [allowed]  340ms
        │     └── tracking: 794644790133
        └── op_9f2f  db.execute (orders)       ✓ [allowed]  18ms
              └── status = 'shipped' (1 row)

  Root Intent: "fulfill urgent pending orders"
  Authority:   user:alice (via agt_7f3k)
  Integrity:   valid hash link (chain verified)
```

---

### 5.3 YAML Trust Receipt (`screens/sys/doctor/sys.doctor.success.report.txt`)

```text
[prod:tier_1]  capcli 0.4.2

trust_receipt:
  status:            nominal
  host_tier:         tier_1 (hardened Linux namespaces)
  workspace:         envs/prod/workspace.db
  ledger_root_hash:  sha256:7f9a1b2c4d8e001fa882bc19488a09b2e4f019c
  audited_events:    14290 committed to _audit
  policy_denials:    18 (intercepted pre-execution; state untouched)
  unaudited_writes:  0
  secret_leaks:      0
  pinned_routines:   32
  active_triggers:   4 crons, 3 webhooks, 1 endpoint
  deployment:        headless_daemon (systemd Linux)
```

---

### 5.4 Pre-Flight Routine Inspection Envelope (`screens/run/inspect/run.inspect.success.routine.txt`)

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

### 5.5 Dry-Run Schema Impact Plan (`screens/run/sql/run.sql.success.dry_run.txt`)

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

### 5.6 Agent Thrashing Denial (`screens/sys/doctor/sys.doctor.denial.thrashing.txt`)

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

### 5.7 Missing Vault Secret with Cockpit URL (`screens/run/execute/run.execute.refusal.missing_secret.txt`)

```text
[dev:tier_1]  ✗  exit 3

  FAIL  policy.secrets.missing
        capability: cap://stripe.refund_charge
        secret_ref: vault://stripe_secret

        Credential 'stripe_secret' not found in vault.
        Direct CLI parameter injection is banned to prevent prompt leakage.

  state_modified: false
  layer: vault
  remedy: prompt human supervisor to inject credential via Cockpit (http://127.0.0.1:4040/vault)
```

---

### 5.8 Network Jail Syscall 42 Trapping (`screens/run/execute/run.execute.denial.network_jail.txt`)

```text
[dev:tier_1]  ✗  exit 2

  FAIL  kernel.network.jail
        syscall 42 (connect) trapped by seccomp-bpf
        target: 10.0.0.5:5432
        caller: routines/sneaky_exfil.py

        Raw network egress prohibited from guest sandboxes.

  state_modified: false
  layer: sandbox
  remedy: use ctx.api.call with an activated catalog verb
```

---

### 5.9 Quota Yield Frame Suspension (`screens/run/execute/run.execute.yield.quota.txt`)

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

### 5.11 NTP Clock Drift Diagnostic Warning (`screens/sys/doctor/sys.doctor.success.clock_drift.txt`)

The rule (cans/physics.md): clock delta vs NTP > 500ms emits a diagnostic warning on an exit-0 screen — causal ordering and lease claims bind to CLOCK_MONOTONIC and SQLite sequence IDs, so drift degrades audit timestamps only and never refuses execution.

```text
[dev:tier_1]  ✓  exit 0

  ⚠  clock drift warning: host delta vs NTP is 840ms (warning threshold: 500ms)
         causal ordering unaffected: CLOCK_MONOTONIC + SQLite sequence IDs
         lease claims and causal DAG bind to monotonic time; wall-clock drift degrades audit timestamps only

  host:            ws-07 (chronyd reachable, not yet synced)
  state_modified: false
  remedy:          synchronize host system clock via 'chronyd' or 'ntpdate' when convenient; execution is not blocked
```

---

### 5.12 Progressive Disclosure Doc Reading (`screens/doc/read/doc.read.success.sliced.txt`)

```text
[dev:tier_1]  doc://refund-policy (section 3)

  outline_node: 3. Stripe integration notes
  tokens:       84 (cap: 100)
  has_more:     false

  ────────────────────────────────────────────────────────────────────────────
  Outbound refunds must include `charge_id` and idempotent client request UUID.
  Never refund a charge older than 120 days via automated routines; delegate
  to human supervisor via `ctx.ping.ask`.
```

---

### 5.13 Minimalist Root Help Stub (`screens/sys/help/sys.help.success.stub.txt`)

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

```json
{
  "$schema": "wireframe/v2",
  "screen_id": "run.sql.denial.ast",
  "noun": "run",
  "verb": "sql",
  "target": "db://orders",
  "command": "capcli sql \"UPDATE orders SET status = 'shipped' WHERE status = 'processing'\" -m \"batch ship\"",
  "state": {
    "exit_code": 2,
    "domain": "policy.ast",
    "trust": "draft",
    "env": "dev",
    "tier": "tier_1",
    "state_modified": false,
    "data_shape": null
  },
  "diagnostic": {
    "domain": "policy.ast",
    "culprit": "No LIMIT clause. Blast radius unbounded.",
    "remedy": "add LIMIT, or target specific primary key",
    "layer": "AST",
    "measured": "matches potentially 847 rows (cap: 100)"
  },
  "txt_pair": "screens/run/sql/run.sql.denial.ast.txt",
  "txt_sha256": null,
  "test_assertions": {
    "exit_code": 2,
    "state_modified": false,
    "stdout_contains": [
      "[dev:tier_1]  ✗  exit 2",
      "FAIL  policy.query.update_delete.require_limit",
      "No LIMIT clause. Blast radius unbounded.",
      "state_modified: false",
      "layer: AST",
      "remedy: add LIMIT, or target specific primary key"
    ],
    "stdout_not_contains": [
      "--force",
      "SyntaxError",
      "panic"
    ],
    "stderr_empty": true,
    "json_keys_required": ["domain", "culprit", "remedy", "state_modified", "layer"],
    "json_field_values": {
      "state_modified": false,
      "domain": "policy.ast"
    }
  }
}
```

### 6.1.1 Trailer Slot

`output_contract.trailer` in `manifest.json` is the output contract's
only producer-facing slot, and the bridge is deterministic: the payload
shape is frozen once in `manifest.json` (`human_format` +
`machine_schema`), and the prompt engine and the wireframe fixtures
validate against that same schema. The wireframe knows the shape of a
trailer and nothing else about the producer — no campaign or bank
inventory, no screen-to-trailer mapping, no trigger predicate, and no
token budget appears in a wireframe file, fixture, or runner check.
Which screens carry a trailer and what each payload says are producer
facts, single-sourced in `cans/artifacts/prompt/_triggers.json`.

- Human output: one optional final line, `trailer: <prompt> - <reason>`.
- JSON output: one optional additive envelope key, `next_action`, whose
  value validates against `machine_schema` in `manifest.json`:
  required keys `prompt` (`prompt://{bank}/{slug}@{version}`), `reason`,
  and `serve` (`L1` or `blocked`).
- The wireframe validates shape and position against the frozen schema.
  It never evaluates a predicate, resolves a pointer, or originates a
  payload. Human and machine parity of the content is a producer
  obligation; each rendering is verbatim.
- A payload with `serve: blocked` is never rendered. Absent is the
  default: a screen with no trailer renders exactly as it renders
  without the slot. The slot never reorders, rewrites, or suppresses
  host-screen output, and it leaves exit code and `state_modified`
  unchanged.

One optional top-level block on a screen fixture pair carries a trailer:

```json
"trailer": {
  "human": "<prompt> - <reason>",
  "json": { "prompt": "prompt://{bank}/{slug}@{version}", "reason": "<reason>", "serve": "L1" }
}
```

The `.txt` pair renders `trailer: <prompt> - <reason>` as its final
line, and `test_assertions.stdout_contains` includes that exact line.
The fixture block is a schema instance, never a second mapping: a
trailer appears in a fixture only when `_triggers.json` names that
screen, and the cross-layer check in §6.2 enforces the correspondence.

### 6.2 Rust Integration Test Runner

```rust
// crates/capcli-cli/tests/e2e/test_wireframe_fixtures.rs

use std::fs;
use std::path::Path;
use glob::glob;
use serde::Deserialize;

#[derive(Deserialize)]
struct TestAssertions {
    exit_code: i32,
    state_modified: bool,
    stdout_contains: Vec<String>,
    #[serde(default)]
    stdout_not_contains: Vec<String>,
    stderr_empty: bool,
}

#[derive(Deserialize)]
struct WireframeFixture {
    screen_id: String,
    command: String,
    test_assertions: TestAssertions,
    txt_pair: String,
}

#[test]
fn execute_wireframe_golden_tests() {
    let root = Path::new("cans/artifacts/wireframe/screens");
    
    for entry in glob(&format!("{}/**/*.json", root.display())).unwrap() {
        let json_path = entry.unwrap();
        let content = fs::read_to_string(&json_path).unwrap();
        let fixture: WireframeFixture = serde_json::from_str(&content).unwrap();

        // 1. Assert companion .txt file exists
        let txt_path = json_path.with_extension("txt");
        assert!(txt_path.exists(), "Missing TXT pairing for {}", json_path.display());

        // 2. Assert TXT has zero raw table pipe characters
        let txt_content = fs::read_to_string(&txt_path).unwrap();
        assert!(!txt_content.contains('|'), "Pipe character | forbidden in {}", txt_path.display());

        // 3. Dispatch CLI harness command
        let output = capcli_test_exec(&fixture.command);

        // 4. Assert exit code and strict rollback invariant
        assert_eq!(output.exit_code, fixture.test_assertions.exit_code, "Exit mismatch at {}", fixture.screen_id);
        assert_eq!(output.state_modified, fixture.test_assertions.state_modified, "State modified invariant failed at {}", fixture.screen_id);

        // 5. Assert atomic output needles
        for needle in &fixture.test_assertions.stdout_contains {
            assert!(output.stdout.contains(needle), "{}: Missing expected output needle '{}'", fixture.screen_id, needle);
        }
        for banned in &fixture.test_assertions.stdout_not_contains {
            assert!(!output.stdout.contains(banned), "{}: Output contains banned token '{}'", fixture.screen_id, banned);
        }

        // Global negative: the parser-banned flags (cans/interface.md#Refusals)
        // appear in no screen's output. Asserted once here, for every fixture;
        // fixtures carry only screen-specific negatives.
        for banned in ["--force", "--override-budget", "--force-prod", "--verbose"] {
            assert!(!output.stdout.contains(banned), "{}: Output contains banned token '{}'", fixture.screen_id, banned);
        }

        if fixture.test_assertions.stderr_empty {
            assert!(output.stderr.is_empty(), "{}: Expected empty stderr, received: {}", fixture.screen_id, output.stderr);
        }
    }
}
```

Trailer checks, applied by the runner in §6.2 to every fixture:

a. **Schema.** A `trailer` block carries exactly `human` (string) and
   `json` (object), and `json` validates against `machine_schema` in
   `manifest.json` `output_contract.trailer` — required `prompt`,
   `reason`, `serve`; `prompt` matching the frozen `prompt://` pattern.
b. **Position.** The human trailer is the final line of the `.txt`
   pair; the machine trailer is an additive envelope key. Every other
   key, value, exit code, and `state_modified` matches the
   trailer-free rendering.
c. **State neutrality.** For every trailer-carrying fixture, a twin
   assertion runs the same command with no trailer supplied: output is
   identical except the trailer line/key is absent.
d. **Correspondence.** Every `_triggers.json` entry resolves to a
   fixture pair on disk, and every `_flows.json` transition endpoint
   and §4 row resolves to a fixture pair (see the cross-layer test
   below). A renamed screen fails the runner before any trailer is
   served against a dead `screen_id`.
e. **Negative space.** Every fixture without a `trailer` block asserts
   `stdout_not_contains: ["trailer:", "next_action"]`.

Cross-layer referential test — one assertion set, run by the same
runner, covering the prompt and wireframe layers together
(`crates/capcli-cli/tests/e2e/test_wireframe_fixtures.rs` when the
kernel lands; enforced today by the workspace validator):

```rust
#[test]
fn assert_prompt_triggers_match_wireframe_screens() {
    let triggers_raw = fs::read_to_string("cans/artifacts/prompt/_triggers.json").unwrap();
    let triggers: serde_json::Value = serde_json::from_str(&triggers_raw).unwrap();

    for t in triggers["triggers"].as_array().unwrap() {
        let screen_id = t["screen_id"].as_str().unwrap();
        let parts: Vec<&str> = screen_id.split('.').collect();

        // Assert exact fixture file exists
        let path = format!("cans/artifacts/wireframe/screens/{}/{}/{}.json", parts[0], parts[1], screen_id);
        assert!(Path::new(&path).exists(), "Trigger {} references missing fixture: {}", t["id"], path);
    }
}
```

The same closure applies in the other directions: every `_flows.json`
transition endpoint exists as a fixture pair, and every §4 row exists
as a fixture pair. Screen IDs originate in exactly one place — the
fixture filenames under `screens/` — and §4, `_flows.json`, and
`_triggers.json` index them under validator enforcement.

---

## 7. Edgeless Playable Canvas Implementation (`wireframe.html`)

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>capcli State Machine & Wireframe Engine</title>
<style>
  :root {
    --bg: #0d1117; --panel: #161b22; --border: #30363d;
    --text: #c9d1d9; --green: #3fb950; --red: #f85149;
    --yellow: #d29922; --purple: #a371f7; --blue: #58a6ff;
  }
  body { margin: 0; padding: 0; background: var(--bg); color: var(--text); font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; overflow: hidden; display: flex; height: 100vh; }
  #canvas-container { flex: 1; height: 100%; position: relative; cursor: grab; }
  #canvas-container:active { cursor: grabbing; }
  svg { width: 100%; height: 100%; }
  #hud { position: absolute; top: 16px; left: 16px; display: flex; gap: 8px; z-index: 10; flex-wrap: wrap; max-width: 60%; }
  .hud-btn { background: var(--panel); border: 1px solid var(--border); color: var(--text); padding: 8px 12px; cursor: pointer; border-radius: 4px; font-family: monospace; font-size: 11px; }
  .hud-btn:hover { border-color: var(--blue); color: #fff; }
  #terminal-panel { width: 620px; height: 100%; background: var(--panel); border-left: 1px solid var(--border); display: flex; flex-direction: column; }
  #terminal-header { padding: 12px 16px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
  #terminal-body { padding: 16px; flex: 1; overflow-y: auto; white-space: pre-wrap; font-size: 12px; line-height: 1.5; color: #c9d1d9; }
  #terminal-actions { padding: 12px 16px; border-top: 1px solid var(--border); display: flex; gap: 8px; flex-wrap: wrap; }
  .action-btn { background: #21262d; border: 1px solid var(--border); color: #fff; padding: 6px 10px; cursor: pointer; border-radius: 4px; font-size: 11px; font-family: monospace; }
  .action-btn:hover { border-color: var(--green); }
  .node rect { stroke-width: 2px; rx: 6px; cursor: pointer; }
  .node text { font-size: 11px; fill: var(--text); pointer-events: none; font-family: monospace; }
  .edge { stroke: var(--border); stroke-width: 2px; marker-end: url(#arrow); fill: none; }
  .edge.denial { stroke: var(--red); stroke-dasharray: 4; }
  .edge.yield { stroke: var(--yellow); stroke-dasharray: 6; }
</style>
</head>
<body>

<div id="canvas-container">
  <div id="hud">
    <button class="hud-btn" onclick="focusJourney('journey_human_onboarding')">1. Human Onboarding (S0-S10)</button>
    <button class="hud-btn" onclick="focusJourney('journey_harness_onboarding')">2. Harness Onboarding (H0-H7)</button>
    <button class="hud-btn" onclick="focusJourney('journey_execution_crucible')">3. Execution Crucible</button>
    <button class="hud-btn" onclick="focusJourney('journey_trust_promotion')">4. Trust Ladder</button>
    <button class="hud-btn" onclick="focusJourney('journey_quota_preemption')">5. Quota Yield/Resume</button>
    <button class="hud-btn" onclick="focusJourney('journey_schema_evolution')">6. DDL Evolution</button>
    <button class="hud-btn" onclick="focusJourney('journey_tamper_forensics')">7. Forensics & Panic</button>
    <button class="hud-btn" onclick="focusJourney('journey_human_in_the_loop')">8. Ask & Resolution</button>
  </div>
  <svg id="viewport">
    <defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#30363d" />
      </marker>
    </defs>
    <g id="scene"></g>
  </svg>
</div>

<div id="terminal-panel">
  <div id="terminal-header">
    <span id="screen-id-display" style="font-weight: 600;">select a state node</span>
    <span id="exit-badge"></span>
  </div>
  <div id="terminal-body">Click any node on the canvas to inspect real CLI diagnostic output...</div>
  <div id="terminal-actions"></div>
</div>

<script>
let transform = { x: 0, y: 0, k: 1 };
const scene = document.getElementById('scene');
const viewport = document.getElementById('viewport');
let isPanning = false, startPoint = { x: 0, y: 0 };
let flowsData = null;

viewport.addEventListener('mousedown', (e) => {
  isPanning = true;
  startPoint = { x: e.clientX - transform.x, y: e.clientY - transform.y };
});
window.addEventListener('mousemove', (e) => {
  if (!isPanning) return;
  transform.x = e.clientX - startPoint.x;
  transform.y = e.clientY - startPoint.y;
  updateTransform();
});
window.addEventListener('mouseup', () => isPanning = false);
viewport.addEventListener('wheel', (e) => {
  e.preventDefault();
  const factor = e.deltaY < 0 ? 1.1 : 0.9;
  transform.k *= factor;
  updateTransform();
});

function updateTransform() {
  scene.setAttribute('transform', `matrix(${transform.k} 0 0 ${transform.k} ${transform.x} ${transform.y})`);
}

fetch('_flows.json')
  .then(r => r.json())
  .then(data => { flowsData = data; renderGraph(data); });

const EXIT_BY_STATE = { success: 0, denial: 2, refusal: 3, crash: 4, panic: 5, yield: 6 };
const NODE_W = 180, NODE_H = 36, COL_W = 220, ROW_H = 80, ORIGIN = { x: 50, y: 100 }, COLS = 6;

function exitCodeFor(screenId) {
  return EXIT_BY_STATE[screenId.split('.')[2]] ?? 0;
}

function renderGraph(data) {
  const ids = new Set();
  data.transitions.forEach(t => { t.from.forEach(id => ids.add(id)); t.to.forEach(id => ids.add(id)); });
  Object.values(data.journeys).forEach(j => { ids.add(j.entry); ids.add(j.terminal); });

  const pos = new Map();
  [...ids].sort().forEach((id, i) => {
    pos.set(id, { x: ORIGIN.x + (i % COLS) * COL_W, y: ORIGIN.y + Math.floor(i / COLS) * ROW_H });
  });

  const svgNS = 'http://www.w3.org/2000/svg';

  data.transitions.forEach(t => {
    t.from.forEach(fromId => t.to.forEach(toId => {
      const a = pos.get(fromId), b = pos.get(toId);
      const path = document.createElementNS(svgNS, 'path');
      path.setAttribute('class', `edge ${t.arrow_type || ''}`.trim());
      path.setAttribute('d', `M ${a.x + NODE_W} ${a.y + NODE_H / 2} L ${b.x} ${b.y + NODE_H / 2}`);
      scene.appendChild(path);
    }));
  });

  pos.forEach((pt, id) => {
    const g = document.createElementNS(svgNS, 'g');
    g.setAttribute('class', 'node');
    g.setAttribute('transform', `translate(${pt.x}, ${pt.y})`);
    g.onclick = () => {
      const parts = id.split('.');
      loadScreen(id, `screens/${parts[0]}/${parts[1]}/${id}.txt`, exitCodeFor(id));
    };
    const rect = document.createElementNS(svgNS, 'rect');
    rect.setAttribute('width', NODE_W);
    rect.setAttribute('height', NODE_H);
    rect.setAttribute('fill', '#161b22');
    rect.setAttribute('stroke', '#30363d');
    const text = document.createElementNS(svgNS, 'text');
    text.setAttribute('x', 10);
    text.setAttribute('y', 22);
    text.textContent = id.length > 22 ? id.slice(0, 20) + '\u2026' : id;
    g.appendChild(rect);
    g.appendChild(text);
    scene.appendChild(g);
  });
}

function loadScreen(screenId, txtPath, exitCode) {
  document.getElementById('screen-id-display').textContent = screenId;
  const badge = document.getElementById('exit-badge');
  badge.textContent = `Exit ${exitCode}`;
  badge.style.color = exitCode === 0 ? 'var(--green)' : (exitCode === 6 ? 'var(--yellow)' : 'var(--red)');
  
  fetch(txtPath)
    .then(r => r.text())
    .then(text => {
      document.getElementById('terminal-body').textContent = text;
      renderOutActions(screenId);
    })
    .catch(() => {
      document.getElementById('terminal-body').textContent = "Failed to load fixture transcript.";
    });
}

function renderOutActions(screenId) {
  const container = document.getElementById('terminal-actions');
  container.innerHTML = '';
  if (!flowsData) return;

  const transitions = flowsData.transitions.filter(t => t.from.includes(screenId));
  transitions.forEach(t => {
    t.to.forEach(targetId => {
      const btn = document.createElement('button');
      btn.className = 'action-btn';
      btn.textContent = t.ui?.button_text || `Transition -> ${targetId}`;
      btn.onclick = () => {
        const parts = targetId.split('.');
        const txtPath = `screens/${parts[0]}/${parts[1]}/${targetId}.txt`;
        loadScreen(targetId, txtPath, exitCodeFor(targetId));
      };
      container.appendChild(btn);
    });
  });
}

function focusJourney(journeyId) {
  if (!flowsData) return;
  const journey = flowsData.journeys[journeyId];
  if (journey) {
    document.getElementById('screen-id-display').textContent = `Journey: ${journey.name}`;
    document.getElementById('terminal-body').textContent = journey.description;
    const parts = journey.entry.split('.');
    const txtPath = `screens/${parts[0]}/${parts[1]}/${journey.entry}.txt`;
    loadScreen(journey.entry, txtPath, exitCodeFor(journey.entry));
  }
}
</script>
</body>
</html>
```