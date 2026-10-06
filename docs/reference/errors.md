# Errors & Diagnostic Remedies (user reference)

Status: **candidate extraction — row-verified against wireframe fixtures
2026-10-07, not yet published reference.** Moved out of
`cans/artifacts/prompt/prompt-structure.md` in the three-layer rewrite:
remedies are user-facing completeness (this page), not agent prompts.
Every row below was checked against its `cans/` owner (`cans/interface.md`,
`cans/physics.md`, the noun's canonical file) and its wireframe fixture.
Publication is blocked on two owner rulings logged in
`cans/_collab/conflicts.md`: the `api sync` verb (C-1) and the exit-5 scope
for secret leaks (C-6). Rows touching those seams are flagged inline.

Scope: this page is a **selected catalogue, not an exhaustive index** —
45 remedy rows against 223 wireframe screens (115 non-success). Success
outcomes are not remedies and do not appear here. Remedies close a single
failed command; multi-stage agent work is a prompt campaign — see
`cans/artifacts/prompt/prompt-structure.md`. Where a remedy says
"inspect", inspection is diagnosis, never the fix; the fix is stated in
the same row.

---

Diagnostic format (kernel-emitted; the `ACTION:` line is the remedy in
one line):

```
[dev:tier_1]  ✗  exit {code} | ACTION: {remedy}
  FAIL  {domain}.{condition}
        {statement_or_culprit}
        ^^^^^^^^^^^^^^^^^^^^^^
        {diagnostic_explanation}

  audit_op: {op_id}
  state_modified: false
  layer: {layer}
  remedy: {remedy_text}
```

### 7.1 `run` Remedies

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R01 | `run.sql.denial.ast` | 2 | `policy.ast` | `unbounded` | `ACTION: capcli sql "<q> LIMIT 10" --dry-run` | `remedy: add LIMIT, or target specific primary key` |
| R02 | `run.sql.denial.authorizer` | 2 | `policy.authorizer` | `schema_mod` | `ACTION: capcli rule apply schema` | `remedy: declare removal in schema.yaml and apply via capcli rule apply schema` |
| R03 | `run.sql.denial.engine_busy` | 2 | `db.engine` | `timeout` | `ACTION: capcli inspect db://orders` | `remedy: write lock held; wait exceeded 5000ms; retry after holder commits or inspect the claim` |
| R04 | `run.sql.refusal.missing_intent` | 3 | `compile` | `no_intent` | `ACTION: capcli sql "<q>" -m "<rationale>"` | `remedy: mutating operations require causal -m rationale` |
| R05 | `run.execute.denial.budget` | 2 | `policy.budget` | `exhausted` | `ACTION: split the work into chunked routines` | `remedy: frame ops ceiling exhausted; split into chunked routines, or raise declared max_ops in a new routine version` |
| R06 | `run.execute.denial.budget_cascade` | 2 | `policy.budget` | `starved` | `ACTION: shrink the child manifest, or invoke the child earlier in the parent DAG` | `remedy: child starved by min() cascade; shrink the child manifest, or invoke the child earlier while ops remain` |
| R07 | `run.execute.denial.network_jail` | 2 | `kernel.sandbox` | `syscall_42` | `ACTION: replace raw socket egress with ctx.api.call (activated catalog verb)` | `remedy: raw socket connect trapped; use ctx.api.call with an activated catalog verb` |
| R08 | `run.execute.refusal.missing_secret` | 3 | `policy.secrets` | `missing_key` | `ACTION: inject the credential via the Cockpit vault screen (127.0.0.1:4040/vault)` | `remedy: credential not in vault; a human injects it via Cockpit — never as a CLI parameter` |
| R09 | `run.execute.crash.poll_timeout` | 4 | `routine.runtime` | `timeout` | `ACTION: set timeout_s to 30 or less, or restructure into a scheduled watch` | `remedy: poll_until ceiling exceeded 30s; set timeout_s ≤30, or restructure into a scheduled watch` |
| R10 | `run.execute.panic.secret_leak` | 5 | `kernel.panic` | `leak` | `ACTION: strip the credential from the routine result, rotate the secret via the Cockpit vault, then re-prove in sim` | `remedy: plaintext secret detected; strip, rotate, re-prove (exit-5 scope: conflict C-6, pending physics ruling)` |
| R11 | `run.execute.yield.quota` | 6 | `api.quota` | `rate_limit` | `ACTION: none — task auto-resumes at reset_at` | `remedy: task safely yielded; daemon will auto-resume at reset_at (capcli inspect quota://<provider> shows headroom)` |

---

### 7.2 `db` Remedies

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R12 | `db.lock.denial.claim_held` | 2 | `db.claims` | `held` | `ACTION: wait for lease expiry or holder release, then retry` | `remedy: lease held by another session; wait for expiry or release, then retry (diagnosis: capcli inspect db://orders)` |
| R13 | `db.lock.refusal.missing_reason` | 3 | `validation` | `missing_arg` | `ACTION: capcli db lock <table>:<ref> --ttl <duration> --reason "<why>"` | `remedy: exclusive lock leases mandate --reason flag` |
| R14 | `db.unlock.denial.not_holder` | 2 | `policy.authorizer` | `unauthorized` | `ACTION: ask the holder to run capcli db unlock <target>, or wait for TTL expiry` | `remedy: caller does not own the claim; ask the holder to unlock, or wait for TTL expiry` |
| R15 | `db.snapshot.denial.prod_draft` | 2 | `policy.trust` | `forbidden` | `ACTION: prove the acting identity in sim and promote to reviewed, then retry the snapshot` | `remedy: draft trust cannot snapshot prod; prove identity in sim, promote to reviewed, retry` |
| R16 | `db.restore.denial.active_locks` | 2 | `db.claims` | `active_locks` | `ACTION: wait for lease expiry or holder release, then re-run capcli db restore <snapshot_id>` | `remedy: active claims prevent state reversal; release or expire them, then restore` |

---

### 7.3 `routine` Remedies

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R17 | `routine.new.refusal.shape_violation` | 3 | `validation` | `bad_shape` | `ACTION: split the scaffold into composed routines under 150 LOC with at most 8 params each` | `remedy: routine exceeds shape limits (150 LOC, 2000 tokens, 8 params); split into composed routines` |
| R18 | `routine.prove.denial.policy` | 2 | `policy.authorizer` | `illegal_leaf` | `ACTION: declare the migration in schema.yaml via capcli rule apply, or drop the DDL from the routine` | `remedy: forbidden leaf: undeclared DDL/ALTER at draft trust` |
| R19 | `routine.ship.denial.trust` | 2 | `policy.trust` | `tier2_refusal` | `ACTION: run the promotion from a tier_1 host` | `remedy: pinned promotion denied on Tier 2 (platform ceiling: reviewed); promote from a tier_1 host (Linux, WSL2, or Docker with userns)` |
| R21 | `routine.rollback.denial.depth` | 2 | `policy.authorizer` | `depth_limit` | `ACTION: roll back incrementally to a version within 5 of the pointer, or ship a new version reverting the change` | `remedy: target version exceeds max rollback depth of 5` |
| R22 | `routine.retire.denial.active_deps` | 2 | `policy.authorizer` | `deps_exist` | `ACTION: retire or rebind the dependents first, then re-run retire` | `remedy: active routines or crons depend on this capability` |

---

### 7.4 `api` Remedies

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R23 | `api.sync.denial.rate` | 2 | `api.quota` | `rate_limit` | `ACTION: wait for the 24h cooldown, or capcli api catalog <provider>` | `remedy: spec sync within 24h cooldown; inspect the live catalog while waiting (verb surface: conflict C-1)` |
| R24 | `api.sync.refusal.missing_url` | 3 | `missing_param` | `missing_arg` | **blocked — do not publish until the `api sync` ruling (C-1) lands** | `remedy: upstream OpenAPI spec URL or file path required; canonical command form depends on the C-1 ruling` |
| R25 | `api.prove.denial.sim_gap` | 2 | `policy.authorizer` | `sim_gap` | `ACTION: add a schema-validated mock fixture for the verb to apis/<provider>.mock.yaml, then re-run the prove` | `remedy: missing mock fixture in sim; add the fixture, then re-run the prove` |
| R26 | `api.prove.crash.runtime` | 4 | `routine.runtime` | `exception` | `ACTION: re-sync the provider spec once upstream fixes the schema, then re-run the prove` | `remedy: upstream contract format failure: response schema declares a union type the compiler cannot accept` |

---

### 7.5 `bind` Remedies

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R27 | `bind.cron.denial.interval` | 2 | `policy.authorizer` | `interval_low` | `ACTION: capcli bind cron <n> <c> "*/5 * * * *"` | `remedy: cron schedules cannot run faster than 5-minute cap` |
| R28 | `bind.webhook.denial.unsigned` | 2 | `policy.authorizer` | `unsigned` | `ACTION: capcli sys vault set <key> <val>, then re-run capcli bind webhook ... --ingress <url> (or --tunnel)` | `remedy: unsigned webhooks rejected; store the provider signing secret via sys vault set, then re-run bind webhook` |
| R29 | `bind.webhook.denial.payload_size` | 2 | `policy.authorizer` | `too_large` | `ACTION: trim provider event payloads or split events` | `remedy: hook payload exceeds 64KB memory buffer ceiling (65,536 bytes); trim or split provider events` |
| R30 | `bind.webhook.refusal.missing_ingress` | 3 | `compile` | `no_ingress` | `ACTION: capcli bind webhook <n> <p> <e> <c> --tunnel` | `remedy: missing public ingress URL; supply --tunnel for dev` |
| R31 | `bind.endpoint.denial.trust` | 2 | `policy.trust` | `unpinned` | `ACTION: capcli routine ship <r> pinned --reason "<w>"` | `remedy: public HTTP/MCP endpoints require pinned trust` |

---

### 7.6 `ping` Remedies

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R32 | `ping.notify.denial.quiet_hours` | 2 | `policy.authorizer` | `quiet_hours` | `ACTION: re-dispatch after 07:00, or use ping ask` | `remedy: notification blocked between 22:00 and 07:00; re-dispatch after 07:00, or use ping ask (urgent asks bypass quiet hours)` |
| R33 | `ping.ask.denial.options_cap` | 2 | `policy.authorizer` | `cap_exceeded` | `ACTION: capcli ping ask <principal> "<q>" --options "a,b" --intent "<why>"` | `remedy: ctx.ping.ask exceeds maximum of 5 structured choices; reduce to 5 or fewer` |
| R34 | `ping.resolve.denial.occ_conflict` | 2 | `db.engine` | `stale_state` | `ACTION: re-inspect the drifted rows and re-issue the ask against current state` | `remedy: OCC fence violated during suspension; re-inspect drifted rows, re-issue the ask, then resume the frame` |
| R35 | `ping.resolve.denial.expired` | 2 | `policy.notify` | `expired` | `ACTION: re-issue capcli ping ask ... if still relevant` | `remedy: inquiry timeout elapsed; expired inquiries never assume consent; fail-closed without mutation` |

---

### 7.7 `rule` Remedies

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R36 | `rule.validate.refusal.syntax` | 3 | `compile` | `bad_syntax` | `ACTION: capcli rule validate` | `remedy: Gate 1 YAML syntax failure; remove or rename the duplicate key, then re-run capcli rule validate` |
| R37 | `rule.validate.refusal.semantics` | 3 | `compile` | `circular_ref` | `ACTION: capcli rule validate` | `remedy: Gate 2 circular dependency in table ref graph; break the cycle by removing one ref= edge or introducing a junction table` |
| R38 | `rule.apply.refusal.lockfile` | 3 | `lockfile_mismatch`| `drift` | `ACTION: restore drifted sources from git HEAD, or recompile capcli.lock via the reviewed apply path` | `remedy: lockfile root hash mismatch; restore sources or recompile via the reviewed apply path` |

---

### 7.8 `env` Remedies

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R39 | `env.new.denial.cap` | 2 | `policy.authorizer` | `cap_exceeded` | `ACTION: dismantle an unused environment (capcli env remove <name>) before provisioning another` | `remedy: maximum 5 environments reached; remove a stale worktree first` |
| R40 | `env.new.refusal.bundle_too_large` | 3 | `policy.template` | `size_overflow`| `ACTION: prune bundle assets below the 5MB ceiling or split the bundle, then retry env new` | `remedy: template bundle exceeds 5MB ceiling; prune assets or split the bundle` |
| R41 | `env.remove.denial.crypto_sig` | 2 | `policy.authorizer` | `confirmation` | `ACTION: complete the out-of-band challenge signature in Cockpit, then re-run capcli env remove prod` | `remedy: production teardown requires out-of-band challenge signature` |
| R42 | `env.merge.refusal.plan_conflict` | 3 | `compile` | `conflict` | `ACTION: resolve the migration plan conflict in declaration order, then re-run capcli env merge` | `remedy: target schema migration plan conflict blocks DDL; resolve in declaration order, then re-run merge` |

---

### 7.9 `sys` Remedies

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R43 | `sys.doctor.refusal.boot` | 3 | `compile` | `missing_dep` | `ACTION: capcli sys doctor --boot-check` | `remedy: host missing sandbox provider bwrap on tier_1 (floor 0.8.0); install bubblewrap >= 0.8.0, then re-run capcli sys doctor --boot-check` |
| R44 | `sys.register.denial.cap` | 2 | `policy.authorizer` | `cap_exceeded` | `ACTION: capcli sys agent revoke <agent-id> for a dormant agent, then re-register` | `remedy: maximum registered agents reached; revoke a dormant agent, then re-register` |
| R46 | `sys.doctor.denial.thrashing` | 2 | `agent.thrashing` | `looping` | `ACTION: escalate to human or inspect the remedy payload (trace: capcli sys audit trace <op-id> --explain)` | `remedy: 20 sustained denials in 5m; harness throttled; escalate to human` |
| R47 | `sys.exec.crash.runtime` | 4 | `routine.runtime` | `crash` | `ACTION: reproduce via capcli sys exec "python3 -X faulthandler etl.py" --sandbox and pin the failing native extension` | `remedy: native extension SIGSEGV; reproduce under capcli sys exec --sandbox and pin the failing extension` |

---

### Removed rows (success screens are not remedies)

- R20 `routine.ship.success.rolled_back` — exit 0, `state_modified: true`;
  belongs with the promotion reference, not the error catalogue.
- R45 `sys.doctor.success.clock_drift` — exit 0 diagnostic warning
  (monotonic fallback active; execution is not blocked); documented with
  the doctor screen, not here. No `host.ntp` domain exists at exit 0.
- R48 `doc.read.success.sliced` — exit 0 bounded read; documented in
  `docs/use/inspect.md`. There is no `--section` flag in v1; leaf
  selection rides `doc outline` node ids.
