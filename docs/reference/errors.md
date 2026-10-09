# Errors & Diagnostic Remedies (user reference)

Status: **candidate extraction — unverified.** Moved out of
`cans/artifacts/prompt/prompt-structure.md` in the three-layer rewrite:
remedies are user-facing completeness (this page), not agent prompts.
Legality of every command, screen, exit, and domain below must be verified
against its `cans/` owner (`cans/interface.md`, `cans/physics.md`, the
noun's canonical file) before this page is treated as published reference.
Screens using `warning` / `alarm` / `rollback` / `suspended` states are
illegal under the current wireframe state taxonomy (wireframe P0-2) and
are flagged by that audit, not legalised here.

Remedies close a single failed command. Multi-stage agent work is a
prompt campaign — see `cans/artifacts/prompt/prompt-structure.md`.

---

Every single refusal, denial, yield, and crash condition across all 11 CLI nouns possesses an exact, top-loaded Line 1 remedy:

```
[dev:tier_1]  ✗  exit {code} | ACTION: {command}
  FAIL  {domain}.{condition}
        {statement_or_culprit}
        ^^^^^^^^^^^^^^^^^^^^^^
        {diagnostic_explanation}

  audit_op: {op_id}
  state_modified: false
  layer: {layer}
  remedy: {remedy_text}
```

### 7.1 `run` Remedies (11 Conditions)

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R01 | `run.sql.denial.ast` | 2 | `policy.ast` | `unbounded` | `ACTION: capcli sql "<q> LIMIT 10" --dry-run` | `remedy: add LIMIT, or target specific primary key` |
| R02 | `run.sql.denial.authorizer` | 2 | `policy.authorizer` | `schema_mod` | `ACTION: capcli rule diff` | `remedy: direct DDL prohibited; modify schema.yaml` |
| R03 | `run.sql.denial.engine_busy` | 2 | `db.engine` | `timeout` | `ACTION: capcli sql "<q>" --retry-busy 3` | `remedy: transaction queue wait exceeded 5000ms; retry query` |
| R04 | `run.sql.refusal.missing_intent` | 3 | `compile` | `no_intent` | `ACTION: capcli sql "<q>" -m "<rationale>"` | `remedy: mutating operations require causal -m rationale` |
| R05 | `run.execute.denial.budget` | 2 | `policy.budget` | `exhausted` | `ACTION: capcli inspect cap://<name>` | `remedy: frame ceiling exceeded; increase max_ops in @routine` |
| R06 | `run.execute.denial.budget_cascade` | 2 | `policy.budget` | `starved` | `ACTION: capcli inspect cap://<name>` | `remedy: parent budget cannot fund worst-case child branch` |
| R07 | `run.execute.denial.network_jail` | 2 | `kernel.sandbox` | `syscall_42` | `ACTION: capcli search "<provider>"` | `remedy: raw socket connect trapped; use ctx.api.call` |
| R08 | `run.execute.refusal.missing_secret` | 3 | `policy.secrets` | `missing_key` | `ACTION: open http://127.0.0.1:4040/vault` | `remedy: credential not in vault; inject via Cockpit UI` |
| R09 | `run.execute.crash.poll_timeout` | 4 | `routine.runtime` | `timeout` | `ACTION: capcli inspect cap://<name>` | `remedy: poll_until ceiling exceeded 30s; bind webhook instead` |
| R10 | `run.execute.panic.secret_leak` | 5 | `kernel.panic` | `leak` | `ACTION: capcli sys doctor --boot-check` | `remedy: plaintext secret detected in stdout; zeroized buffers` |
| R11 | `run.execute.yield.quota` | 6 | `api.quota` | `rate_limit` | `ACTION: capcli sys inbox pop` | `remedy: task yielded; daemon will auto-resume at reset_at` |

---

### 7.2 `db` Remedies (5 Conditions)

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R12 | `db.lock.denial.claim_held` | 2 | `db.claims` | `held` | `ACTION: capcli sql "SELECT * FROM claims"` | `remedy: lease held by another session; yield or await TTL` |
| R13 | `db.lock.refusal.missing_reason` | 3 | `validation` | `missing_arg` | `ACTION: capcli db lock <ref> --reason "<why>"` | `remedy: exclusive lock leases mandate --reason flag` |
| R14 | `db.unlock.refusal.not_holder` | 3 | `policy.authorizer` | `unauthorized` | `ACTION: capcli sql "SELECT holder FROM claims"` | `remedy: acting agent ID does not own target lease` |
| R15 | `db.snapshot.denial.prod_draft` | 2 | `policy.trust` | `forbidden` | `ACTION: capcli env use sim` | `remedy: draft trust cannot snapshot prod; switch to sim` |
| R16 | `db.restore.denial.active_locks` | 2 | `db.claims` | `active_locks` | `ACTION: capcli sql "SELECT * FROM claims"` | `remedy: active business claims prevent state reversal` |

---

### 7.3 `routine` Remedies (6 Conditions)

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R17 | `routine.new.refusal.shape_violation` | 3 | `validation` | `bad_shape` | `ACTION: head -n 150 routines/<name>.py` | `remedy: routine exceeds limits: 150 LOC, 2000 tokens, 8 params` |
| R18 | `routine.prove.denial.policy` | 2 | `policy.authorizer` | `illegal_leaf` | `ACTION: capcli inspect cap://<name>` | `remedy: forbidden leaf: external API calls banned in db.txn` |
| R19 | `routine.ship.denial.trust` | 2 | `policy.trust` | `tier2_refusal` | `ACTION: capcli run <cap> --env sim` | `remedy: E045 pinned trust forbidden on Tier 2 macOS/Win` |
| R20 | `routine.ship.rollback.canary` | 0 | `policy.authorizer` | `rolled_back` | `ACTION: capcli routine prove <name> --env sim` | `remedy: canary telemetry spike triggered auto-rollback` |
| R21 | `routine.rollback.denial.depth` | 2 | `policy.authorizer` | `depth_limit` | `ACTION: capcli routine stats <name>` | `remedy: target version exceeds max rollback depth of 5` |
| R22 | `routine.retire.denial.active_deps` | 2 | `policy.authorizer` | `deps_exist` | `ACTION: capcli inspect cap://<name>` | `remedy: active routines or crons depend on this capability` |

---

### 7.4 `api` Remedies (4 Conditions)

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R23 | `api.sync.denial.rate` | 2 | `api.quota` | `rate_limit` | `ACTION: capcli api diff <provider>` | `remedy: spec sync within 24h cooldown; inspect local diff` |
| R24 | `api.sync.refusal.missing_url` | 3 | `missing_param` | `missing_arg` | `ACTION: capcli api import <p> <path> <m> --spec <u>` | `remedy: upstream OpenAPI spec URL or file path required` |
| R25 | `api.prove.denial.sim_gap` | 2 | `policy.authorizer` | `sim_gap` | `ACTION: capcli api record <verb> -p k=v` | `remedy: missing mock fixture in sim; record live cassette` |
| R26 | `api.prove.crash.runtime` | 4 | `routine.runtime` | `exception` | `ACTION: capcli api diff <provider>` | `remedy: upstream API payload violates catalog schema types` |

---

### 7.5 `bind` Remedies (5 Conditions)

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R27 | `bind.cron.denial.interval` | 2 | `policy.authorizer` | `interval_low` | `ACTION: capcli bind cron <n> <c> "*/5 * * * *"` | `remedy: cron schedules cannot run faster than 5-minute cap` |
| R28 | `bind.webhook.denial.unsigned` | 2 | `policy.authorizer` | `unsigned` | `ACTION: capcli bind webhook <n> <p> <e> <c> --driver <s>` | `remedy: unsigned webhooks rejected; configure driver HMAC` |
| R29 | `bind.webhook.denial.payload_size` | 2 | `policy.authorizer` | `too_large` | `ACTION: capcli inspect bind://<name>` | `remedy: hook payload exceeds 64KB memory buffer ceiling` |
| R30 | `bind.webhook.refusal.missing_ingress` | 3 | `compile` | `no_ingress` | `ACTION: capcli bind webhook <n> <p> <e> <c> --tunnel` | `remedy: missing public ingress URL; supply --tunnel for dev` |
| R31 | `bind.endpoint.denial.trust` | 2 | `policy.trust` | `unpinned` | `ACTION: capcli routine ship <r> pinned --reason "<w>"` | `remedy: public HTTP/MCP endpoints require pinned trust` |

---

### 7.6 `ping` Remedies (4 Conditions)

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R32 | `ping.notify.denial.quiet_hours` | 2 | `policy.authorizer` | `quiet_hours` | `ACTION: capcli sys inbox pop` | `remedy: notification blocked between 22:00 and 07:00` |
| R33 | `ping.ask.denial.options_cap` | 2 | `policy.authorizer` | `cap_exceeded` | `ACTION: capcli ping ask <p> "<q>" --options "a,b"` | `remedy: ctx.ping.ask exceeds maximum of 5 structured choices` |
| R34 | `ping.resolve.denial.occ_conflict` | 2 | `db.engine` | `stale_state` | `ACTION: capcli run <routine_name>` | `remedy: OCC fence violated during suspension; re-run from turn 0` |
| R35 | `ping.resolve.denial.expired` | 2 | `policy.notify` | `expired` | `ACTION: capcli ping expire <ask_id>` | `remedy: inquiry timeout elapsed; fail-closed without mutation` |

---

### 7.7 `rule` Remedies (3 Conditions)

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R36 | `rule.validate.refusal.syntax` | 3 | `compile` | `bad_syntax` | `ACTION: capcli rule validate` | `remedy: Gate 1 YAML syntax failure; check schema indentation` |
| R37 | `rule.validate.refusal.semantics` | 3 | `compile` | `circular_ref` | `ACTION: capcli rule validate` | `remedy: Gate 2 circular dependency detected in table FK graph` |
| R38 | `rule.apply.refusal.lockfile` | 3 | `lockfile_mismatch`| `drift` | `ACTION: capcli rule validate` | `remedy: lockfile root hash mismatch; recompile in dev` |

---

### 7.8 `env` Remedies (4 Conditions)

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R39 | `env.new.denial.cap` | 2 | `policy.authorizer` | `cap_exceeded` | `ACTION: capcli env list` | `remedy: maximum 5 environments reached; remove stale worktrees` |
| R40 | `template.pack.denial.size_limit` | 2 | `policy.template` | `size_limit`| `ACTION: capcli template pack <dir>` | `remedy: world template bundle exceeds 5MB ceiling; prune assets or split the bundle` |
| R41 | `env.remove.denial.crypto_sig` | 2 | `policy.authorizer` | `confirmation` | `ACTION: open http://127.0.0.1:4040/admin` | `remedy: production teardown requires hardware challenge signature` |
| R42 | `env.merge.refusal.plan_conflict` | 3 | `compile` | `conflict` | `ACTION: git pull origin main` | `remedy: target schema migration plan conflict; rebase worktree` |

---

### 7.9 `sys` Remedies (5 Conditions)

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R43 | `sys.doctor.refusal.boot` | 3 | `compile` | `missing_dep` | `ACTION: capcli sys doctor` | `remedy: host missing python3.11 or sandbox provider (bwrap)` |
| R44 | `sys.register.denial.cap` | 2 | `policy.authorizer` | `cap_exceeded` | `ACTION: capcli sys agent list` | `remedy: maximum registered agents reached; revoke idle tokens` |
| R45 | `sys.doctor.warning.clock_drift` | 0 | `host.ntp` | `clock_skew` | `ACTION: sudo chronyd -q || sudo ntpdate pool.ntp.org`| `remedy: host clock skewed >500ms; monotonic fallback active` |
| R46 | `sys.doctor.alarm.thrashing` | 2 | `agent.thrashing` | `looping` | `ACTION: capcli sys audit trace latest --explain` | `remedy: 20 sustained denials in 5m; harness throttled` |
| R47 | `sys.exec.crash.runtime` | 5 | `kernel.panic` | `crash` | `ACTION: export CAPCLI_RECOVERY=1 && capcli sys doctor` | `remedy: unrecoverable media failure; boot emergency recovery` |

---

### 7.10 `doc` Remedy (1 Condition)

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R48 | `doc.read.success.sliced` | 0 | `doc.slice` | `sliced` | `ACTION: capcli doc read <ptr> --section <next>` | `remedy: document rendered in bounded 100-token slice; advance section` |
