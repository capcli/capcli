# Canonical Wireframe, State Machine & Flow Engine Specification

---

## 1. Directory Tree & Architecture

The wireframe layer serves a dual purpose: an **interactive edgeless canvas** for humans and harnesses, and a **deterministic golden-file test fixture suite** for the Rust kernel.

Flow graphs, journey definitions, and multi-branch transition metadata are completely decoupled into `flows.json`. Individual screen fixtures remain atomic, stateless, and uncoupled from orchestration.

```
cans/artifacts/wireframe/
  manifest.json
  flows.json
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
      author/
        new/
        prove/
      promote/
        ship/
        pending/
      maintain/
        sweep/
        stats/
        rollback/
        demote/
        retire/
    api/
      catalog/
        sync/
        diff/
        list/
      lifecycle/
        activate/
        prove/
        ship/
      maintain/
        stats/
        retire/
        rollback/
    bind/
      triggers/
        cron/
        webhook/
        endpoint/
      manage/
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
      audit/
        tail/
        trace/
        query/
        replay/
      agent/
        register/
        list/
        revoke/
      vault/
        set/
        import_env/
      core/
        inbox/
        doctor/
        backup/
        recover/
        exec/
        serve/
```

### 1.1 Structural Invariants
* **Active Nouns:** Exactly 9 CLI nouns (`run`, `db`, `routine`, `api`, `bind`, `ping`, `rule`, `env`, `sys`).
* **Pairing Law:** Every `.json` fixture has an identical `.txt` companion in the same folder. No orphan files. No empty directories.
* **Depth Ceiling:** File paths relative to `screens/` must remain between 3 and 5 directory components.
* **Sibling Invariants:** Min 3, max 12 siblings per branch node.
* **Naming Law:**
  ```
  {noun}.{verb}.{state}.{condition}.{json|txt}
  ```

---

## 2. Core Manifests & States

### 2.1 `manifest.json`

```json
{
  "version": 1,
  "policy_version": 5,
  "governance_version": 8,
  "schema_version": 3,
  "lockfile": "capcli.lock",
  "compiled_at": "2026-03-31T00:00:00Z",
  "nouns": [
    "run", "db", "routine", "api", "bind",
    "ping", "rule", "env", "sys"
  ],
  "state_axes": {
    "exit_code": [0, 2, 3, 4, 5, 6],
    "trust": ["draft", "reviewed", "pinned"],
    "env": ["dev", "sim", "prod"],
    "tier": ["tier_1", "tier_2"],
    "budget": ["active", "exhausted", "yielded"],
    "data": ["populated", "empty", "truncated", "redirected"],
    "denial_domain": [
      "policy.authorizer",
      "policy.ast",
      "policy.budget",
      "policy.trust",
      "db.engine",
      "db.claims",
      "api.upstream",
      "api.quota",
      "routine.runtime",
      "kernel.sandbox",
      "kernel.panic",
      "host.ntp"
    ]
  },
  "output_contract": {
    "prefix": "[{env}:{tier}]",
    "human_format": "rustc-style diagnostic with atomic blocks and horizontal dividers",
    "machine_format": "--json structured envelope",
    "banned_characters": ["│", "|", "├", "└"],
    "divider_character": "─",
    "denial_keys": ["domain", "culprit", "remedy", "state_modified"],
    "truncation": {
      "max_result_tokens": 500,
      "emits": ["truncated", "next_cursor"]
    },
    "help_stub_max_lines": 6,
    "banned_flags": ["--force", "--override-budget", "--force-prod"],
    "payload_redirection": "--out writes payload to file; stdout emits <30 token receipt"
  }
}
```

### 2.2 `_states.json`

```json
{
  "0": {
    "label": "success",
    "state_modified": true,
    "diagnostic": null,
    "audit": "committed to _audit with result_hash"
  },
  "2": {
    "label": "denial",
    "state_modified": false,
    "domains": [
      "policy.authorizer",
      "policy.ast",
      "policy.budget",
      "policy.trust",
      "db.engine",
      "db.claims",
      "api.quota",
      "kernel.sandbox"
    ],
    "diagnostic_required": ["domain", "culprit", "remedy"],
    "denial_ux": {
      "cite_measured_value": true,
      "suggest_remediation": true,
      "budget_cites_level": true,
      "budget_cites_remaining": true,
      "budget_cites_ancestors": true
    }
  },
  "3": {
    "label": "refusal",
    "state_modified": false,
    "domains": [
      "compile",
      "validation",
      "boot",
      "missing_param",
      "lockfile_mismatch",
      "schema_hash_mismatch",
      "host.ntp"
    ],
    "diagnostic_required": ["domain", "culprit", "remedy"]
  },
  "4": {
    "label": "crash",
    "state_modified": false,
    "domains": ["routine.runtime"],
    "rollback": "clean",
    "diagnostic_required": ["domain", "culprit", "remedy"]
  },
  "5": {
    "label": "panic",
    "state_modified": false,
    "domains": ["kernel.panic"],
    "boot_refusal": true,
    "diagnostic_required": ["domain", "culprit", "remedy"]
  },
  "6": {
    "label": "yield",
    "state_modified": false,
    "domains": ["api.quota"],
    "suspension": true,
    "diagnostic_required": ["domain", "culprit", "remedy", "yield_until", "deferments"],
    "resume": "daemon re-queues via _suspended_tasks on token refill"
  }
}
```

---

## 3. Decoupled Flow & Journey Engine (`flows.json`)

All choreography, branching paths, multiple inputs/outputs, and operational user journeys are codified centrally. Screen fixtures never hold route references.

```json
{
  "$schema": "wireframe/flows/v1",
  "version": 1,
  "journeys": {
    "journey_human_onboarding": {
      "name": "S0–S10 Human Onboarding & First Write",
      "color": "#58a6ff",
      "entry": "sys.core.doctor.success.nominal",
      "terminal": "sys.core.doctor.success.nominal",
      "description": "Probe host -> deliberate AST blast denial -> bounded write -> snapshot restore -> trust receipt"
    },
    "journey_execution_crucible": {
      "name": "Cascade Starvation, Jail Traps & Contention",
      "color": "#f85149",
      "entry": "run.inspect.success.routine",
      "terminal": "run.execute.success.populated",
      "description": "Exhaustion at child frame boundary -> syscall 42 trap -> concurrency lease recovery"
    },
    "journey_trust_promotion": {
      "name": "Draft to Pinned Canary Promotion",
      "color": "#3fb950",
      "entry": "routine.author.prove.success.passed",
      "terminal": "routine.promote.ship.success.shipped",
      "description": "Sim replay verification -> 1-hour canary telemetry window -> Tier 1 pinned lock"
    },
    "journey_quota_preemption": {
      "name": "Wire Quota Starvation, Yield & Auto-Resume",
      "color": "#d29922",
      "entry": "run.execute.yield.quota",
      "terminal": "run.execute.resume.quota",
      "description": "Background task reaches dry pool -> Exit 6 suspension -> daemon parks frame -> refill triggers auto-resume"
    },
    "journey_schema_evolution": {
      "name": "Forward DDL & Snapshot Auto-Reversal",
      "color": "#a371f7",
      "entry": "rule.diff.success.populated",
      "terminal": "env.merge.success.merged",
      "description": "YAML diff -> Gate 2 circular ref block -> dry-run failure -> atomic snapshot reversal"
    },
    "journey_tamper_forensics": {
      "name": "Integrity Panic & Break-Glass Recovery",
      "color": "#f0883e",
      "entry": "sys.core.doctor.panic.tamper",
      "terminal": "sys.core.doctor.recovery_mode",
      "description": "Broken SHA-256 chain -> emergency panic -> CAPCLI_RECOVERY=1 diagnostic re-entry"
    }
  },
  "transitions": [
    {
      "id": "t_onboarding_boot_to_read",
      "journeys": ["journey_human_onboarding"],
      "from": ["sys.core.doctor.success.nominal"],
      "to": ["run.sql.success.populated"],
      "trigger": "exec_read",
      "label": "capcli sql 'SELECT id FROM orders LIMIT 5'",
      "arrow_type": "progress"
    },
    {
      "id": "t_onboarding_deliberate_denial",
      "journeys": ["journey_human_onboarding"],
      "from": ["run.sql.success.populated"],
      "to": ["run.sql.denial.ast"],
      "trigger": "exec_unbounded_write",
      "label": "capcli sql 'UPDATE orders SET status = shipped'",
      "arrow_type": "denial",
      "ui": {
        "button_text": "Trigger Deliberate Denial",
        "hotkey": "x"
      }
    },
    {
      "id": "t_denial_hub_to_explain",
      "journeys": ["journey_human_onboarding", "journey_execution_crucible"],
      "from": [
        "run.sql.denial.ast",
        "run.execute.denial.budget",
        "run.execute.denial.budget_cascade",
        "run.execute.denial.network_jail",
        "run.execute.denial.tier2_pinned"
      ],
      "to": ["sys.audit.trace.success.populated"],
      "trigger": "inspect_trace",
      "label": "capcli sys audit trace <op_id> --explain",
      "arrow_type": "denial",
      "ui": {
        "button_text": "Diagnose Cause (--explain)",
        "hotkey": "d"
      }
    },
    {
      "id": "t_trace_remedy_to_bounded_write",
      "journeys": ["journey_human_onboarding"],
      "from": ["sys.audit.trace.success.populated"],
      "to": ["run.sql.success.populated"],
      "trigger": "apply_remedy",
      "label": "Append WHERE id = 'ORD-8842' LIMIT 1 -m 'reconcile status'",
      "arrow_type": "success",
      "ui": {
        "button_text": "Execute Remediated Write",
        "hotkey": "r"
      }
    },
    {
      "id": "t_snapshot_restore_verification",
      "journeys": ["journey_human_onboarding"],
      "from": ["db.snapshot.success.created"],
      "to": ["db.restore.success.restored"],
      "trigger": "verify_restore",
      "label": "capcli db restore snap_migration_004",
      "arrow_type": "progress"
    },
    {
      "id": "t_quota_yield_fork",
      "journeys": ["journey_quota_preemption"],
      "from": ["run.execute.yield.quota"],
      "to": [
        "run.execute.resume.quota",
        "sys.core.inbox.success.populated"
      ],
      "trigger": "quota_resolution",
      "arrow_type": "yield",
      "branch_labels": {
        "run.execute.resume.quota": "Tokens refilled (>15 unreserved headroom)",
        "sys.core.inbox.success.populated": "Deferments exceeded (>5) -> sensory alert"
      }
    },
    {
      "id": "t_canary_veto_branch",
      "journeys": ["journey_trust_promotion"],
      "from": ["routine.promote.ship.success.shipped"],
      "to": [
        "routine.maintain.stats.success.populated",
        "routine.promote.ship.rollback.canary"
      ],
      "trigger": "telemetry_evaluation",
      "arrow_type": "progress",
      "branch_labels": {
        "routine.maintain.stats.success.populated": "Telemetry clean over 1 hour -> stable",
        "routine.promote.ship.rollback.canary": "Anomaly or policy denial detected -> circuit breaker"
      }
    },
    {
      "id": "t_canary_auto_rollback_to_demote",
      "journeys": ["journey_trust_promotion"],
      "from": ["routine.promote.ship.rollback.canary"],
      "to": ["routine.maintain.demote.success.circuit_breaker"],
      "trigger": "auto_demote",
      "label": "Revert routine trust pointer to draft",
      "arrow_type": "denial"
    },
    {
      "id": "t_tamper_to_recovery_breakglass",
      "journeys": ["journey_tamper_forensics"],
      "from": ["sys.core.doctor.panic.tamper"],
      "to": ["sys.core.doctor.recovery_mode"],
      "trigger": "break_glass",
      "label": "Export CAPCLI_RECOVERY=1",
      "arrow_type": "denial",
      "ui": {
        "button_text": "Enter Recovery Break-Glass",
        "hotkey": "!"
      }
    }
  ]
}
```

---

## 4. Complete Screen Inventory & State Matrix

### 4.1 `run/` (5 verbs $\rightarrow$ 33 screen pairs)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `run.execute.success.populated` | success | 0 | — | populated | Deterministic execution and commit |
| `run.execute.success.redirected` | success | 0 | — | redirected | Payload written to file via `--out`; stdout emits receipt |
| `run.execute.success.truncated` | success | 0 | — | truncated | Result $>500$ tokens; returns `next_cursor` |
| `run.execute.denial.budget` | denial | 2 | policy.budget | exhausted | Frame ops/duration ceiling exhausted |
| `run.execute.denial.budget_cascade` | denial | 2 | policy.budget | starved | Child frame clipped by parent/session `min()` |
| `run.execute.denial.trust` | denial | 2 | policy.trust | unproven | Draft routine executed in prod |
| `run.execute.denial.tier2_pinned` | denial | 2 | policy.trust | tier2 | `E045_TIER2_PINNED_DENIED` on macOS/Win |
| `run.execute.denial.authorizer` | denial | 2 | policy.authorizer | forbidden | Prohibited table or column mutation |
| `run.execute.denial.network_jail` | denial | 2 | kernel.sandbox | syscall_42 | Trapped raw `connect()` via seccomp-bpf |
| `run.execute.denial.claim_held` | denial | 2 | db.claims | locked | Exclusive `--lock` ref already held |
| `run.execute.suspended.ask` | success | 0 | — | suspended | Pauses frame; enqueues in `_pending_asks` |
| `run.execute.yield.quota` | yield | 6 | api.quota | rate_limit | Suspends task; sets `yield_until` timestamp |
| `run.execute.resume.quota` | success | 0 | — | resumed | Daemon re-dispatches task on token refill |
| `run.execute.crash.runtime` | crash | 4 | routine.runtime | exception | Guest language uncaught error |
| `run.execute.crash.poll_timeout` | crash | 4 | routine.runtime | timeout | `poll_until` exceeds 30-second ceiling |
| `run.execute.panic.secret_leak` | panic | 5 | kernel.panic | leak | `kill_and_alert` triggered on plaintext secret leak |
| `run.sql.success.populated` | success | 0 | — | populated | AST-vetted SQL commit |
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
| `run.inspect.success.routine` | success | 0 | — | populated | Pre-flight envelope and budget cascade |
| `run.inspect.success.quota` | success | 0 | — | populated | Headroom breakdown on `quota://` URP |
| `run.inspect.refusal.missing_ptr` | refusal | 3 | missing_param | missing_arg | Unrecognized target pointer format |
| `run.inspect.denial.trust` | denial | 2 | policy.trust | unreadable | Draft routine secret inspection denied |

### 4.2 `db/` (6 verbs $\rightarrow$ 14 screen pairs)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `db.lock.success.acquired` | success | 0 | — | acquired | Exclusive claim lease registered |
| `db.lock.denial.claim_held` | denial | 2 | db.claims | held | Target resource currently claimed |
| `db.lock.refusal.missing_reason` | refusal | 3 | validation | missing_arg | `--reason` required for locking |
| `db.unlock.success.released` | success | 0 | — | released | Claim lease released ahead of TTL |
| `db.unlock.refusal.not_holder` | refusal | 3 | policy.authorizer | unauthorized | Caller does not own the claim |
| `db.schema.success.populated` | success | 0 | — | populated | Live DDL schema introspected |
| `db.schema.success.empty` | success | 0 | — | empty | Empty database state |
| `db.snapshot.success.created` | success | 0 | — | created | Point-in-time snapshot committed |
| `db.snapshot.denial.trust` | denial | 2 | policy.trust | forbidden | Snapshots restricted to pinned trust |
| `db.restore.success.restored` | success | 0 | — | restored | DB state restored from snapshot |
| `db.restore.refusal.missing_id` | refusal | 3 | missing_param | missing_arg | Target snapshot ID missing |
| `db.restore.denial.active_locks` | denial | 2 | db.claims | active_locks | Active claims prevent state reversal |
| `db.dump.success.populated` | success | 0 | — | populated | Unified SQL schema and seed dump |
| `db.dump.success.truncated` | success | 0 | — | truncated | Dump output payload truncated |

### 4.3 `routine/` (8 verbs $\rightarrow$ 24 screen pairs)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `routine.author.new.success.created` | success | 0 | — | created | Routine scaffold committed |
| `routine.author.new.refusal.name_taken` | refusal | 3 | validation | collision | Routine name already registered |
| `routine.author.new.refusal.shape_violation` | refusal | 3 | validation | bad_shape | Scaffold violates LOC or param limits |
| `routine.author.prove.success.passed` | success | 0 | — | passed | Dynamic fingerprint verified |
| `routine.author.prove.denial.shape` | denial | 2 | policy.authorizer | bad_shape | Execution violates declared limits |
| `routine.author.prove.denial.policy` | denial | 2 | policy.authorizer | illegal_leaf | Routine attempts forbidden leaf op |
| `routine.author.prove.denial.sandbox` | denial | 2 | kernel.sandbox | breach | Jail containment boundary violation |
| `routine.author.prove.crash.runtime` | crash | 4 | routine.runtime | exception | Uncaught exception in test pass |
| `routine.promote.ship.success.shipped` | success | 0 | — | shipped | Routine promoted to new trust rung |
| `routine.promote.ship.rollback.canary` | success | 0 | — | rolled_back | Canary telemetry trips auto-rollback |
| `routine.promote.ship.denial.metrics` | denial | 2 | policy.authorizer | low_success | Success rate falls below 0.90 |
| `routine.promote.ship.refusal.missing_reason`| refusal | 3 | validation | missing_arg | Elevation to pinned requires reason |
| `routine.promote.ship.denial.trust` | denial | 2 | policy.trust | tier2_refusal | Pinned promotion denied on Tier 2 |
| `routine.promote.pending.success.populated` | success | 0 | — | populated | Batch promotion candidates listed |
| `routine.promote.pending.success.empty` | success | 0 | — | empty | No routines pending promotion |
| `routine.maintain.sweep.success.populated` | success | 0 | — | populated | Deduplication proposals generated |
| `routine.maintain.sweep.success.empty` | success | 0 | — | empty | No duplicate routines detected |
| `routine.maintain.stats.success.populated` | success | 0 | — | populated | Routine p50/p95 execution metrics |
| `routine.maintain.stats.refusal.not_found` | refusal | 3 | validation | not_found | Routine name does not exist |
| `routine.maintain.rollback.success.completed`| success | 0 | — | completed | Reverts pointer to prior version |
| `routine.maintain.rollback.denial.depth` | denial | 2 | policy.authorizer | depth_limit | Exceeds max rollback depth of 5 |
| `routine.maintain.rollback.refusal.not_found`| refusal | 3 | validation | not_found | Target version not found in history |
| `routine.maintain.demote.success.circuit_breaker`| success| 0 | — | demoted | Auto-demotes failing routine to draft |
| `routine.maintain.retire.success.completed` | success | 0 | — | completed | Routine retired from service |
| `routine.maintain.retire.denial.active_deps` | denial | 2 | policy.authorizer | deps_exist | Callee dependencies block retirement |
| `routine.maintain.retire.refusal.not_found` | refusal | 3 | validation | not_found | Target routine does not exist |

### 4.4 `api/` (8 verbs $\rightarrow$ 21 screen pairs)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `api.catalog.sync.success.synced` | success | 0 | — | synced | OpenAPI spec compiled to catalog |
| `api.catalog.sync.denial.rate` | denial | 2 | api.quota | rate_limit | Sync call within 24h cooldown |
| `api.catalog.sync.refusal.missing_url` | refusal | 3 | missing_param | missing_arg | Upstream spec URL omitted |
| `api.catalog.diff.success.populated` | success | 0 | — | populated | Spec divergence detected |
| `api.catalog.diff.success.empty` | success | 0 | — | empty | Zero drift from active catalog |
| `api.catalog.list.success.populated` | success | 0 | — | populated | Imported catalog verbs listed |
| `api.catalog.list.success.empty` | success | 0 | — | empty | Zero APIs configured |
| `api.catalog.list.success.truncated` | success | 0 | — | truncated | Truncated at 500 verbs |
| `api.lifecycle.activate.success.activated` | success | 0 | — | activated | Dormant verb shifted to active draft |
| `api.lifecycle.activate.denial.cap` | denial | 2 | policy.authorizer | cap_exceeded| Max 50 active verbs reached |
| `api.lifecycle.activate.denial.rate` | denial | 2 | policy.authorizer | rate_limit | Exceeded 10 activations/hour |
| `api.lifecycle.activate.refusal.missing_intent`| refusal| 3 | compile | no_intent | Missing intent flag on activation |
| `api.lifecycle.prove.success.passed` | success | 0 | — | passed | Rehearsal in sim verified |
| `api.lifecycle.prove.denial.sim_gap` | denial | 2 | policy.authorizer | sim_gap | Missing mock fixture in sim |
| `api.lifecycle.prove.denial.policy` | denial | 2 | policy.authorizer | forbidden | Verb egress rule rejected |
| `api.lifecycle.prove.crash.runtime` | crash | 4 | routine.runtime | exception | Upstream contract format failure |
| `api.lifecycle.ship.success.shipped` | success | 0 | — | shipped | Promoted; enters training wheels |
| `api.lifecycle.ship.success.graduated` | success | 0 | — | graduated | Reaches Call 4; enters full autonomy |
| `api.lifecycle.ship.denial.metrics` | denial | 2 | policy.authorizer | unproven | Fails synthetic contract replay |
| `api.lifecycle.ship.refusal.missing_reason` | refusal | 3 | validation | missing_arg | Missing elevation justification |
| `api.maintain.stats.success.populated` | success | 0 | — | populated | Quota usage and error metrics |
| `api.maintain.stats.refusal.not_found` | refusal | 3 | validation | not_found | Target provider not found |
| `api.maintain.retire.success.completed` | success | 0 | — | completed | API verb deactivated to dormant |
| `api.maintain.retire.refusal.not_found` | refusal | 3 | validation | not_found | Target verb not found |
| `api.maintain.rollback.success.completed` | success | 0 | — | completed | Reverts API spec to prior hash |
| `api.maintain.rollback.denial.depth` | denial | 2 | policy.authorizer | depth_limit | Exceeds max rollback limit of 10 |
| `api.maintain.rollback.refusal.not_found` | refusal | 3 | validation | not_found | Target version not found |

### 4.5 `bind/` (9 verbs $\rightarrow$ 21 screen pairs)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `bind.triggers.cron.success.bound` | success | 0 | — | bound | Schedule bound to routine |
| `bind.triggers.cron.denial.cap` | denial | 2 | policy.authorizer | cap_exceeded| Max 20 active schedules reached |
| `bind.triggers.cron.denial.interval` | denial | 2 | policy.authorizer | interval_low| Interval lower than 5-minute cap |
| `bind.triggers.cron.refusal.missing_intent` | refusal | 3 | compile | no_intent | Missing intent flag |
| `bind.triggers.webhook.success.bound` | success | 0 | — | bound | Inbound hook route activated |
| `bind.triggers.webhook.denial.cap` | denial | 2 | policy.authorizer | cap_exceeded| Max 50 active hooks reached |
| `bind.triggers.webhook.denial.unsigned` | denial | 2 | policy.authorizer | unsigned | Unsigned hooks rejected |
| `bind.triggers.webhook.denial.payload_size` | denial | 2 | policy.authorizer | too_large | Hook payload exceeds 64KB |
| `bind.triggers.webhook.refusal.missing_ingress`| refusal| 3 | compile | no_ingress | Missing public ingress URL/tunnel |
| `bind.triggers.endpoint.success.bound` | success | 0 | — | bound | Routine exposed as HTTP/MCP |
| `bind.triggers.endpoint.denial.trust` | denial | 2 | policy.trust | unpinned | Endpoint requires pinned trust |
| `bind.triggers.endpoint.denial.cap` | denial | 2 | policy.authorizer | cap_exceeded| Max 10 active endpoints reached |
| `bind.manage.list.success.populated` | success | 0 | — | populated | Active bindings displayed |
| `bind.manage.list.success.empty` | success | 0 | — | empty | Zero bindings active |
| `bind.manage.inspect.success.populated` | success | 0 | — | populated | Binding configuration envelope |
| `bind.manage.inspect.refusal.not_found` | refusal | 3 | validation | not_found | Target binding ID not found |
| `bind.manage.pause.success.completed` | success | 0 | — | completed | Trigger paused |
| `bind.manage.pause.refusal.not_found` | refusal | 3 | validation | not_found | Target binding ID not found |
| `bind.manage.resume.success.completed` | success | 0 | — | completed | Trigger resumed |
| `bind.manage.resume.refusal.not_found` | refusal | 3 | validation | not_found | Target binding ID not found |
| `bind.manage.remove.success.completed` | success | 0 | — | completed | Trigger dismantled |
| `bind.manage.remove.refusal.not_found` | refusal | 3 | validation | not_found | Target binding ID not found |
| `bind.manage.keys.success.issued` | success | 0 | — | issued | API key stamped for endpoint |
| `bind.manage.keys.denial.cap` | denial | 2 | policy.authorizer | cap_exceeded| Max 25 keys reached |

### 4.6 `ping/` (5 verbs $\rightarrow$ 11 screen pairs)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `ping.notify.success.dispatched` | success | 0 | — | dispatched | Notification dispatched |
| `ping.notify.denial.quiet_hours` | denial | 2 | policy.authorizer | quiet_hours | Blocked between 22:00 and 07:00 |
| `ping.notify.refusal.missing_intent` | refusal | 3 | compile | no_intent | Missing intent declaration |
| `ping.ask.success.suspended` | success | 0 | — | suspended | Human question queued |
| `ping.ask.denial.options_cap` | denial | 2 | policy.authorizer | cap_exceeded| Exceeds 5 structured choices |
| `ping.ask.refusal.missing_intent` | refusal | 3 | compile | no_intent | Missing intent declaration |
| `ping.list.success.populated` | success | 0 | — | populated | Pending suspension questions |
| `ping.list.success.empty` | success | 0 | — | empty | Zero pending inquiries |
| `ping.resolve.success.resolved` | success | 0 | — | resolved | Choice selected; resumes task |
| `ping.resolve.refusal.not_found` | refusal | 3 | validation | not_found | Invalid ask ID |
| `ping.resolve.denial.expired` | denial | 2 | policy.authorizer | expired | Timeout elapsed; fail-closed |
| `ping.expire.success.completed` | success | 0 | — | completed | Explicit expiration executed |
| `ping.expire.refusal.not_found` | refusal | 3 | validation | not_found | Target inquiry not found |

### 4.7 `rule/` (4 verbs $\rightarrow$ 11 screen pairs)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `rule.show.success.populated` | success | 0 | — | populated | Compiled DDL / authorizer rules |
| `rule.show.refusal.not_found` | refusal | 3 | validation | not_found | Target rule/table not found |
| `rule.diff.success.populated` | success | 0 | — | populated | Schema/policy drift detected |
| `rule.diff.success.empty` | success | 0 | — | empty | Workspace in lockstep with rules |
| `rule.apply.success.applied` | success | 0 | — | applied | DDL applied in transaction |
| `rule.apply.denial.trust` | denial | 2 | policy.trust | unproven | `ALTER` requires reviewed trust |
| `rule.apply.refusal.validation` | refusal | 3 | validation | rejected | Gate 2 semantic check fails |
| `rule.apply.denial.lockfile` | denial | 2 | policy.authorizer | drift | Lockfile root hash mismatch |
| `rule.validate.success.valid` | success | 0 | — | valid | Declarations pass Gates 1 & 2 |
| `rule.validate.refusal.syntax` | refusal | 3 | compile | bad_syntax | Gate 1 YAML syntax failure |
| `rule.validate.refusal.semantics` | refusal | 3 | compile | circular_ref | Gate 2 circular dependency detected |

### 4.8 `env/` (7 verbs $\rightarrow$ 15 screen pairs)

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
| `env.merge.refusal.unmerged` | refusal | 3 | compile | conflict | Git branch conflict blocks DDL |
| `env.merge.denial.lockfile` | denial | 2 | policy.authorizer | drift | Lockfile out of sync |
| `env.remove.success.removed` | success | 0 | — | removed | Environment dismantled |
| `env.remove.denial.prod_flags` | denial | 2 | policy.authorizer | confirmation | Prod requires dual confirm flags |
| `env.remove.refusal.not_found` | refusal | 3 | validation | not_found | Target environment not found |

### 4.9 `sys/` (15 verbs $\rightarrow$ 35 screen pairs)

| Screen ID | State | Exit | Domain | Condition | Description |
|---|---|---|---|---|---|
| `sys.audit.tail.success.populated` | success | 0 | — | populated | Live streaming audit records |
| `sys.audit.tail.success.empty` | success | 0 | — | empty | No audit events within window |
| `sys.audit.trace.success.populated` | success | 0 | — | populated | Causal DAG walk with `--explain` |
| `sys.audit.trace.refusal.not_found` | refusal | 3 | validation | not_found | Target operation ID missing |
| `sys.audit.query.success.populated` | success | 0 | — | populated | SQL executed against `_audit` |
| `sys.audit.query.success.empty` | success | 0 | — | empty | Zero matching audit rows |
| `sys.audit.query.refusal.unparseable`| refusal | 3 | compile | bad_syntax | Malformed SQL audit query |
| `sys.audit.replay.success.replayed` | success | 0 | — | replayed | Deterministic execution from log |
| `sys.audit.replay.denial.external` | denial | 2 | policy.authorizer | external_op | HTTP calls require manual flag |
| `sys.audit.replay.refusal.missing_from`| refusal| 3 | missing_param | missing_arg | Target timestamp or commit omitted |
| `sys.agent.register.success.registered`| success| 0 | — | registered | Kernel-minted agent ID issued |
| `sys.agent.register.denial.cap` | denial | 2 | policy.authorizer | cap_exceeded| Max agents exceeded |
| `sys.agent.list.success.populated` | success | 0 | — | populated | Registered agents listed |
| `sys.agent.list.success.empty` | success | 0 | — | empty | Zero registered agents |
| `sys.agent.revoke.success.revoked` | success | 0 | — | revoked | Agent credentials killed |
| `sys.agent.revoke.refusal.not_found` | refusal | 3 | validation | not_found | Target agent ID not found |
| `sys.vault.set.success.vaulted` | success | 0 | — | vaulted | AES-256-GCM secret encrypted |
| `sys.vault.set.refusal.missing_val` | refusal | 3 | missing_param | missing_arg | Target secret value omitted |
| `sys.vault.import_env.success.imported`| success| 0 | — | imported | Scanned and bound `CAPCLI_SECRET_*`|
| `sys.vault.import_env.refusal.no_env_vars`|refusal|3 | validation | not_found | No matching environment variables |
| `sys.core.inbox.success.populated` | success | 0 | — | populated | Sensory events popped from queue |
| `sys.core.inbox.success.empty` | success | 0 | — | empty | Sensory inbox completely drained |
| `sys.core.doctor.success.nominal` | success | 0 | — | nominal | Verified Trust Receipt emitted |
| `sys.core.doctor.denial.drift` | denial | 2 | policy.authorizer | drift | Live DB differs from lockfile |
| `sys.core.doctor.refusal.boot` | refusal | 3 | compile | missing_dep | Host missing python3.11 or bwrap |
| `sys.core.doctor.refusal.clock_drift`| refusal| 3 | host.ntp | clock_skew | Host clock delta $>500$ms vs NTP |
| `sys.core.doctor.panic.tamper` | panic | 5 | kernel.panic | tampered | Audit SHA-256 chain broken |
| `sys.core.doctor.recovery_mode` | success | 0 | — | recovery | `CAPCLI_RECOVERY=1` break-glass active |
| `sys.core.backup.success.completed` | success | 0 | — | completed | Snapshot pushed to Git and S3 |
| `sys.core.backup.denial.push_fail` | denial | 2 | policy.authorizer | push_fail | Remote S3/Git push rejected |
| `sys.core.recover.success.restored` | success | 0 | — | restored | Reconstructed from object store |
| `sys.core.recover.refusal.not_found` | refusal | 3 | validation | not_found | Recovery snapshot missing |
| `sys.core.recover.denial.active_locks`| denial | 2 | db.claims | active_locks | Active locks prevent state reversal |
| `sys.core.exec.success.completed` | success | 0 | — | completed | Isolated command executed in jail |
| `sys.core.exec.denial.sandbox` | denial | 2 | kernel.sandbox | violation | Attempted unconfined escape |
| `sys.core.exec.crash.runtime` | crash | 4 | routine.runtime | crash | Executable process crash |
| `sys.core.serve.success.running` | success | 0 | — | running | IPC/WS/HTTP daemon active |
| `sys.core.serve.refusal.already_running`| refusal| 3 | compile | port_bound | Daemon process already running |
| `sys.core.serve.denial.port` | denial | 2 | db.engine | port_denied | Port 4040 binding rejected |

---

## 5. Atomic Output Contract & Canonical Screen Fixtures

Every terminal transcript is constructed of three atomic components:
1. **HEADER:** Environment/Tier badge, command status, target identifier.
2. **BODY:** Diagnostic metrics, culprit details, observed limits, and data tables.
3. **FOOTER:** `state_modified` boolean, audit linkage, actionable remediation, and token receipt.

Dividers must be horizontal rules (`─`). No vertical bars (`│`, `|`, `├`, `└`) are permitted.

### 5.1 AST Blast-Radius Denial (`screens/run/sql/run.sql.denial.ast.txt`)

```text
⟨run.sql.denial.ast⟩
⟨exit 2⟩ policy.ast

[dev:tier_2] ERROR: UNBOUNDED MUTATION REJECTED
────────────────────────────────────────────────────────────────────────────────
Statement:       UPDATE orders SET status = 'shipped'
Culprit:         AST blast-radius check failed: missing WHERE and LIMIT clauses
Require Where:   true (provided: false)
Require Limit:   true (provided: false, ceiling: 1000)
Max Limit:       1000
────────────────────────────────────────────────────────────────────────────────
state_modified:  false
audit_event:     db.exec.denied (uncommitted)
remedy:          Append explicit WHERE clause and LIMIT <= 1000 (e.g. WHERE id = 'ORD-1' LIMIT 1)
────────────────────────────────────────────────────────────────────────────────
⟨agent parses: --json envelope with domain, culprit, remedy, state_modified⟩
⟨human reads: atomic header, body, footer blocks above with horizontal rules only⟩
```

### 5.2 Network Jail Syscall 42 Trapping (`screens/run/execute/run.execute.denial.network_jail.txt`)

```text
⟨run.execute.denial.network_jail⟩
⟨exit 2⟩ kernel.sandbox

[dev:tier_1] ERROR: NETWORK JAIL BREACH TRAPPED
────────────────────────────────────────────────────────────────────────────────
Target:          sync_inventory@1
Culprit:         Raw socket connect() (syscall 42) trapped by seccomp-bpf filter
Attempted Wire:  api.supplier.com:443
Sandbox Mode:    bwrap (tier_1 hardened isolation)
Policy Floor:    Raw network egress prohibited from guest routines
────────────────────────────────────────────────────────────────────────────────
state_modified:  false
audit_event:     sandbox.breach (uncommitted)
remedy:          Route external calls via ctx.api.call using declared apis/ catalog verbs
────────────────────────────────────────────────────────────────────────────────
⟨agent parses: --json envelope with domain, culprit, remedy, state_modified⟩
⟨human reads: atomic header, body, footer blocks above with horizontal rules only⟩
```

### 5.3 Cascade Budget Starvation (`screens/run/execute/run.execute.denial.budget_cascade.txt`)

```text
⟨run.execute.denial.budget_cascade⟩
⟨exit 2⟩ policy.budget

[prod:tier_1] ERROR: CASCADE BUDGET STARVATION
────────────────────────────────────────────────────────────────────────────────
Target:          dispatch_order@2 -> record_metric@1 (frame_004)
Culprit:         Child execution clipped by parent frame_001 min() remaining headroom
Declared Need:   10 ops
Parent Headroom: 3 ops
Attempted Op:    db.exec
Blocking Level:  routine
Session Pool:    3 ops remaining
────────────────────────────────────────────────────────────────────────────────
state_modified:  false
audit_event:     budget.exhausted (uncommitted)
remedy:          Raise parent op budget or decouple child as an asynchronous worker
────────────────────────────────────────────────────────────────────────────────
⟨agent parses: --json envelope with domain, culprit, remedy, state_modified, measured, remaining⟩
⟨human reads: atomic header, body, footer blocks above with horizontal rules only⟩
```

### 5.4 Quota Preemption Yield (`screens/run/execute/run.execute.yield.quota.txt`)

```text
⟨run.execute.yield.quota⟩
⟨exit 6⟩ api.quota

[prod:tier_1] YIELD: PROVIDER QUOTA DEPLETED
────────────────────────────────────────────────────────────────────────────────
Provider:        stripe
Priority:        background
Unreserved Pool: 0 tokens available
Yield Until:     2026-03-31T12:00:00Z (epoch: 1774958400)
Task Frame:      frame_009 persisted to _suspended_tasks
Deferments:      1/5
────────────────────────────────────────────────────────────────────────────────
state_modified:  false
audit_event:     api.yield (suspended)
remedy:          Task parked cleanly; daemon will automatically re-queue on token refill
────────────────────────────────────────────────────────────────────────────────
⟨agent parses: --json envelope with yield_until, deferments, priority, state_modified⟩
⟨human reads: atomic header, body, footer blocks above with horizontal rules only⟩
```

### 5.5 Secret Exposure Emergency Panic (`screens/run/execute/run.execute.panic.secret_leak.txt`)

```text
⟨run.execute.panic.secret_leak⟩
⟨exit 5⟩ kernel.panic

[dev:tier_1] PANIC: PLAINTEXT SECRET LEAK DETECTED
────────────────────────────────────────────────────────────────────────────────
Action:          kill_and_alert triggered
Secret Target:   vault://stripe_key
Detected Value:  sk_live_████
Buffer Action:   Stdout destroyed, memory buffers zeroized, process terminated
Integrity Floor: Credentials may never cross process boundaries in plaintext
────────────────────────────────────────────────────────────────────────────────
state_modified:  false
audit_event:     vault.leak_incident (stamped)
remedy:          Inspect routine source to eliminate debug logging of vaulted secrets
────────────────────────────────────────────────────────────────────────────────
⟨agent parses: --json envelope with domain, culprit, remedy, state_modified⟩
⟨human reads: atomic header, body, footer blocks above with horizontal rules only⟩
```

### 5.6 Platform Tier Degradation Denial (`screens/run/execute/run.execute.denial.tier2_pinned.txt`)

```text
⟨run.execute.denial.tier2_pinned⟩
⟨exit 2⟩ policy.trust

[prod:tier_2] ERROR: E045_TIER2_PINNED_DENIED
────────────────────────────────────────────────────────────────────────────────
Target:          settle_ledger@4 (pinned)
Host Platform:   darwin (tier_2 degraded isolation)
Missing Defense: Linux unprivileged namespaces + seccomp-bpf syscall filter
Trust Floor:     Pinned routines demand Tier 1 hardened environments
────────────────────────────────────────────────────────────────────────────────
state_modified:  false
audit_event:     trust.tier_denied (uncommitted)
remedy:          Downgrade routine to reviewed for dev/sim or execute on a Tier 1 Linux host
────────────────────────────────────────────────────────────────────────────────
⟨agent parses: --json envelope with domain, culprit, remedy, state_modified⟩
⟨human reads: atomic header, body, footer blocks above with horizontal rules only⟩
```

---

## 6. Fixture Schema & Rust Test Runner Contract

### 6.1 Pure Atomic Screen Fixture Schema (`screens/run/execute/run.execute.denial.budget_cascade.json`)

```json
{
  "$schema": "wireframe/v2",
  "screen_id": "run.execute.denial.budget_cascade",
  "noun": "run",
  "verb": "execute",
  "target": "dispatch_order@2",
  "command": "capcli run dispatch_order@2 --env prod -m 'process batch'",
  "state": {
    "exit_code": 2,
    "domain": "policy.budget",
    "trust": "pinned",
    "env": "prod",
    "tier": "tier_1",
    "state_modified": false,
    "data_shape": null
  },
  "diagnostic": {
    "domain": "policy.budget",
    "culprit": "child routine record_metric@1 (frame_004) clipped by parent frame_001 min() headroom",
    "remedy": "raise declared limits on parent routine or decouple child as an asynchronous worker",
    "layer": "budget",
    "measured": {
      "parent_remaining_ops": 3,
      "child_declared_ops": 10,
      "attempted_op": "db.exec"
    },
    "remaining": {
      "blocking_level": { "ops": 0, "duration_ms": 254800, "fuel": 80400 },
      "session": { "ops": 3, "duration_ms": 555000, "fuel": 80400, "egress_bytes": 4181824 },
      "ancestors": [
        { "frame": "frame_001", "remaining_ops": 3 }
      ]
    },
    "blocking_level": "routine"
  },
  "txt_pair": "screens/run/execute/run.execute.denial.budget_cascade.txt",
  "txt_sha256": null,
  "test_assertions": {
    "exit_code": 2,
    "state_modified": false,
    "stdout_contains": [
      "[prod:tier_1]",
      "CASCADE BUDGET STARVATION",
      "clipped by parent frame_001",
      "parent_remaining_ops: 3",
      "state_modified:  false"
    ],
    "stdout_not_contains": [
      "--override-budget",
      "--force",
      "partial commit"
    ],
    "stderr_empty": true,
    "json_keys_required": ["domain", "culprit", "remedy", "state_modified", "measured", "remaining"],
    "json_field_values": {
      "state_modified": false,
      "domain": "policy.budget"
    }
  }
}
```

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

        // 2. Assert TXT has zero vertical line characters
        let txt_content = fs::read_to_string(&txt_path).unwrap();
        assert!(!txt_content.contains('│'), "Vertical character │ forbidden in {}", txt_path.display());
        assert!(!txt_content.contains('├'), "Vertical character ├ forbidden in {}", txt_path.display());
        assert!(!txt_content.contains('└'), "Vertical character └ forbidden in {}", txt_path.display());

        // 3. Dispatch CLI harness command
        let output = capcli_test_exec(&fixture.command);

        // 4. Assert exit code and strict rollback invariant
        assert_eq!(output.exit_code, fixture.test_assertions.exit_code, "Exit mismatch at {}", fixture.screen_id);
        assert_eq!(output.state_modified, fixture.test_assertions.state_modified, "State modified invariant failed at {}", fixture.screen_id);

        // 5. Assert atomic header, body, and footer content needles
        for needle in &fixture.test_assertions.stdout_contains {
            assert!(output.stdout.contains(needle), "{}: Missing expected output needle '{}'", fixture.screen_id, needle);
        }
        for banned in &fixture.test_assertions.stdout_not_contains {
            assert!(!output.stdout.contains(banned), "{}: Output contains banned token '{}'", fixture.screen_id, banned);
        }

        if fixture.test_assertions.stderr_empty {
            assert!(output.stderr.is_empty(), "{}: Expected empty stderr, received: {}", fixture.screen_id, output.stderr);
        }
    }
}
```

---

## 7. Edgeless Playable Canvas Implementation (`wireframe.html`)

A single, zero-dependency HTML file (`<450` lines) combining SVG canvas rendering with an interactive terminal simulator. It reads `manifest.json` for node inventory, `flows.json` for graph topology and buttons, and screens for transcripts.

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
  body { margin: 0; padding: 0; background: var(--bg); color: var(--text); font-family: monospace; overflow: hidden; display: flex; height: 100vh; }
  #canvas-container { flex: 1; height: 100%; position: relative; cursor: grab; }
  #canvas-container:active { cursor: grabbing; }
  svg { width: 100%; height: 100%; }
  #hud { position: absolute; top: 16px; left: 16px; display: flex; gap: 8px; z-index: 10; }
  .hud-btn { background: var(--panel); border: 1px solid var(--border); color: var(--text); padding: 8px 12px; cursor: pointer; border-radius: 4px; font-family: monospace; }
  .hud-btn:hover { border-color: var(--blue); color: #fff; }
  #terminal-panel { width: 580px; height: 100%; background: var(--panel); border-left: 1px solid var(--border); display: flex; flex-direction: column; }
  #terminal-header { padding: 12px 16px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
  #terminal-body { padding: 16px; flex: 1; overflow-y: auto; white-space: pre-wrap; font-size: 12px; line-height: 1.4; color: #58a6ff; }
  #terminal-actions { padding: 12px 16px; border-top: 1px solid var(--border); display: flex; gap: 8px; flex-wrap: wrap; }
  .action-btn { background: #21262d; border: 1px solid var(--border); color: #fff; padding: 6px 10px; cursor: pointer; border-radius: 4px; font-size: 11px; }
  .action-btn:hover { border-color: var(--green); }
  .node rect { stroke-width: 2px; rx: 6px; cursor: pointer; }
  .node text { font-size: 12px; fill: var(--text); pointer-events: none; }
  .edge { stroke: var(--border); stroke-width: 2px; marker-end: url(#arrow); fill: none; }
  .edge.denial { stroke: var(--red); stroke-dasharray: 4; }
  .edge.yield { stroke: var(--yellow); stroke-dasharray: 6; }
</style>
</head>
<body>

<div id="canvas-container">
  <div id="hud">
    <button class="hud-btn" onclick="focusJourney('journey_human_onboarding')">1. Onboarding (S0-S10)</button>
    <button class="hud-btn" onclick="focusJourney('journey_execution_crucible')">2. Execution Crucible</button>
    <button class="hud-btn" onclick="focusJourney('journey_trust_promotion')">3. Trust Ladder</button>
    <button class="hud-btn" onclick="focusJourney('journey_quota_preemption')">4. Quota Yield/Resume</button>
    <button class="hud-btn" onclick="focusJourney('journey_schema_evolution')">5. DDL Evolution</button>
    <button class="hud-btn" onclick="focusJourney('journey_tamper_forensics')">6. Forensics & Panic</button>
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
    <span id="screen-id-display">select a state node</span>
    <span id="exit-badge"></span>
  </div>
  <div id="terminal-body">Click any node on the canvas to play CLI output...</div>
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

fetch('flows.json')
  .then(r => r.json())
  .then(data => { flowsData = data; });

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
        // Resolve target screen file path and simulate transition
        const parts = targetId.split('.');
        const txtPath = `screens/${parts[0]}/${parts[1]}/${targetId}.txt`;
        loadScreen(targetId, txtPath, 0);
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
  }
}
</script>
</body>
</html>
```