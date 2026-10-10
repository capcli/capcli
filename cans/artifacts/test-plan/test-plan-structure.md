# Canonical Test Plan, Scenario Bible & Confusion Matrix Specification

`cans/artifacts/test-plan/test-plan-structure.md`

---

## 1. Directory Tree & Architecture

The test-plan layer is the **canonical specification and scenario bible** for AI agents and human engineers developing the `capcli` kernel, runtime crates, and harnesses. 

It does not contain executable fixtures (which reside in `cans/artifacts/wireframe/screens/`) nor does it contain Rust source code (which resides in `crates/`). Instead, it codifies **narrative behavioral contracts in decoupled YAML files**, mapping every physical invariant, failure boundary, and edge case to a strict **Test Confusion Matrix**.

Its primary objective is to **eliminate AI-generated test slop**—preventing autonomous code-generation agents from writing tautological assertions, mocking away the very invariants under test, failing to verify negative state side-effects, or asserting success on inverted errors.

```
cans/artifacts/test-plan/
  manifest.yaml
  matrix.yaml
  test-plan-structure.md
  cases/
    kernel_physics/
      kp_01_syscall_seccomp_trap.yaml
      kp_02_platform_tier2_degraded_boot.yaml
      kp_03_authorizer_prepare_time_abort.yaml
      kp_04_bytecode_openwrite_discrepancy.yaml
      kp_05_ntp_clock_drift_halt.yaml
      kp_06_tamper_hashchain_panic.yaml
      kp_07_secret_leak_memory_zeroize.yaml
      kp_08_missing_bwrap_tier1_abort.yaml
      kp_09_broken_tmpfs_scratch_isolation.yaml
      kp_10_posix_locking_compliance_probe.yaml
      kp_11_audit_sink_error_fail_closed.yaml
      kp_12_sigkill_subshell_transaction_rollback.yaml
      kp_13_unprivileged_userns_docker_check.yaml
      kp_14_dynamic_seccomp_profile_switch.yaml
      kp_15_root_help_stub_ceiling.yaml
      kp_15_sigterm_preemption_exit6_checkpoint.yaml
      kp_16_network_partition_sync_audit_exit5.yaml
    database_authorizer/
      da_01_unbounded_update_ast_kill.yaml
      da_02_where_tautology_bypass_kill.yaml
      da_03_multi_statement_injection.yaml
      da_04_system_table_write_denial.yaml
      da_05_ddl_trust_floor_enforcement.yaml
      da_06_connection_queue_busy_timeout.yaml
      da_07_prepared_statement_cache_invalidation.yaml
      da_08_column_immutability_enforcement.yaml
      da_09_table_imm_rows_delete_denial.yaml
      da_10_unbounded_delete_ast_kill.yaml
      da_11_foreign_key_cascade_authorizer_trap.yaml
      da_12_disallowed_sqlite_function_trap.yaml
      da_13_row_ceiling_transaction_overflow.yaml
    wire_egress/
      we_01_proactive_bucket_exhaustion.yaml
      we_02_dynamic_jsonpath_header_sync.yaml
      we_03_background_priority_yield_exit6.yaml
      we_04_vault_bearer_egress_injection.yaml
      we_05_unregistered_ip_outbound_block.yaml
      we_06_sim_mode_mock_fallback.yaml
      we_07_429_backoff_jitter_retry.yaml
      we_08_standard_priority_yield_floor.yaml
      we_09_critical_priority_pool_drain.yaml
      we_10_wire_payload_byte_cap_breach.yaml
      we_11_unimported_verb_egress_denial.yaml
      we_12_ephemeral_bearer_auto_refresh.yaml
      we_13_sim_rehearsal_isolated_quota.yaml
    budget_cascade/
      bc_01_downward_min_inheritance.yaml
      bc_02_session_ops_ceiling_starvation.yaml
      bc_03_leaf_op_51_hard_kill.yaml
      bc_04_duration_watchdog_cleanup.yaml
      bc_05_fuel_pool_depletion_exit2.yaml
      bc_06_priority_floor_preemption_exit6.yaml
      bc_07_suspended_task_refill_resume.yaml
      bc_08_nesting_depth_ceiling_refusal.yaml
      bc_09_rows_affected_pool_exhaustion.yaml
      bc_10_wire_egress_session_pool_cascade.yaml
      bc_11_parent_frame_reconciliation_audit.yaml
      bc_12_suspended_task_max_deferments_abort.yaml
      bc_13_inspect_preflight_can_invoke_verdict.yaml
      bc_14_hub_atomic_fuel_arbitration.yaml
      bc_15_spoke_prereserve_preemption_floor.yaml
    audit_dag/
      ad_01_sha256_prev_hash_linking.yaml
      ad_02_sink_failure_kernel_panic.yaml
      ad_03_causal_dag_parent_pointer.yaml
      ad_04_fpa_masking_redaction.yaml
      ad_05_w3c_traceparent_propagation.yaml
      ad_06_historical_replay_idempotency.yaml
      ad_07_jsonl_mirror_flush_cadence.yaml
      ad_08_denial_logging_effect_none.yaml
      ad_09_tamper_detection_root_worm_walk.yaml
      ad_10_genesis_event_hash_anchor.yaml
      ad_11_trace_traversal_root_intent.yaml
      ad_12_audit_query_parameterization.yaml
      ad_13_kms_witness_signature_checkpoint.yaml
    trust_ladder/
      tl_01_draft_write_to_prod_denial.yaml
      tl_02_tier2_pinned_execution_refusal.yaml
      tl_03_auto_promotion_conjunction_pass.yaml
      tl_04_canary_telemetry_auto_demote.yaml
      tl_05_unproven_template_draft_floor.yaml
      tl_06_training_wheels_call_graduation.yaml
      tl_07_bulk_operations_reviewed_floor.yaml
      tl_08_cross_agent_callee_reviewed_floor.yaml
      tl_09_monotonic_ascent_skip_denial.yaml
      tl_10_demotion_zero_resistance_pass.yaml
      tl_11_promotion_queue_sla_breach_alert.yaml
      tl_12_human_veto_rollback_trust.yaml
      tl_13_circuit_breaker_demotion_streak.yaml
    schema_evolution/
      se_01_yaml_syntax_gate1_refusal.yaml
      se_02_circular_dependency_gate2_refusal.yaml
      se_03_lockfile_hash_drift_gate3_refusal.yaml
      se_04_live_pragma_drift_gate4_refusal.yaml
      se_05_forward_ddl_snapshot_rollback.yaml
      se_06_env_merge_prod_dual_flag_gate.yaml
      se_07_shorthand_expansion_ddl_generation.yaml
      se_08_system_schema_tamper_boot_refusal.yaml
      se_09_seed_data_volume_cap_breach.yaml
      se_10_scoped_view_missing_principal_bind.yaml
      se_11_forward_only_migration_invariant.yaml
      se_12_git_worktree_isolation_boundary.yaml
      se_13_git_push_dry_run_merge_gate.yaml
      se_14_template_bundle_cap_breach.yaml
      se_15_template_kernel_compat_refusal.yaml
      se_16_template_ast_rewrite_draft_floor.yaml
    coordination_claims/
      cc_01_exclusive_lease_acquisition.yaml
      cc_02_contested_claim_rejection.yaml
      cc_03_daemon_ttl_lease_dissolution.yaml
      cc_04_routine_dependency_retire_block.yaml
      cc_05_process_uid_session_mismatch.yaml
      cc_06_sqlite_wal_begin_immediate_serialized.yaml
      cc_07_authoring_mutex_concurrent_edit.yaml
      cc_08_revoked_agent_token_abort.yaml
      cc_09_session_fork_token_inheritance.yaml
      cc_10_claims_lease_extension_holder_only.yaml
      cc_11_orphan_claim_process_crash_cleanup.yaml
      cc_12_cross_agent_event_tailing.yaml
      cc_13_disconnect_claims_auto_drop.yaml
      cc_14_heartbeat_loss_spoke_lease_eviction.yaml
    bindings_triggers/
      bt_01_cron_min_interval_enforcement.yaml
      bt_02_cron_catchup_fire_limit.yaml
      bt_03_webhook_hmac_signature_refusal.yaml
      bt_04_webhook_payload_ceiling_block.yaml
      bt_05_endpoint_unpinned_trust_denial.yaml
      bt_06_ask_fail_closed_timeout.yaml
      bt_07_orphan_schedule_retire_disable.yaml
      bt_08_webhook_rate_limit_throttle.yaml
      bt_09_endpoint_partner_key_hash_auth.yaml
      bt_10_ask_question_token_cap_breach.yaml
      bt_11_ask_options_count_ceiling.yaml
      bt_12_webhook_ingress_public_url_mandate.yaml
    vault_secrets/
      vs_01_missing_secret_cockpit_url_refusal.yaml
      vs_02_env_var_auto_binding.yaml
      vs_03_cli_parameter_injection_banned.yaml
      vs_04_aes_256_gcm_ciphertext_rest.yaml
      vs_05_draft_routine_secret_read_denial.yaml
      vs_06_vault_set_audit_masked_fingerprint.yaml
      vs_07_egress_proxy_token_refresh_zeroize.yaml
      vs_08_vault_export_plaintext_denial.yaml
      vs_09_biometric_faceid_cockpit_auth.yaml
      vs_10_secret_scope_environment_isolation.yaml
      vs_11_secret_rotation_in_memory_eviction.yaml
      vs_12_redacted_leak_detection_kill.yaml
    sdk_harness/
      sh_01_missing_frame_token_trap.yaml
      sh_02_api_call_inside_db_txn_prohibition.yaml
      sh_03_poll_until_aggregate_accounting.yaml
      sh_04_param_type_mismatch_exit3.yaml
      sh_05_overview_result_token_truncation.yaml
      sh_06_direct_socket_connect_trapped.yaml
      sh_07_manifest_reflection_prove_ipc.yaml
      sh_08_undeclared_leaf_anomaly_event.yaml
      sh_09_time_sleep_raw_loop_prohibition.yaml
      sh_10_ctx_storage_hmac_presigned_url.yaml
      sh_11_non_serializable_result_exit4.yaml
      sh_12_ctx_db_lock_distributed_lease.yaml
```

### 1.1 Structural Invariants
* **Decoupled Specifications:** `test-plan-structure.md` defines the global framework, linter laws, and catalog. The case specifications exist **strictly inside atomic YAML files** within `cases/{domain}/`.
* **Zero Inline Case Bloat:** Individual test case scenarios are never embedded directly within this document; only structural templates, schemas, and catalog summaries are permitted here.
* **1:1 Codebase Alignment:** Every case file corresponds directly to integration tests in `crates/capcli-core/tests/` or end-to-end tests in `crates/capcli-cli/tests/e2e/`.

---

## 2. Test Hierarchy & Tier Taxonomy

Every case file targets an exact tier in the monorepo architecture:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        TIER 3: END-TO-END (E2E)                        │
│   • Black-box static binary invocation (`capcli <noun> <verb>`)        │
│   • Process subshell boundary: Exit Codes (0, 2, 3, 4, 5, 6)           │
│   • Golden wireframe CLI transcript validation                         │
│   • Location: crates/capcli-cli/tests/e2e/                             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                      TIER 2: INTEGRATION (INTEG)                       │
│   • Multi-subsystem coordination (e.g. SQLite WAL + C Authorizer)      │
│   • Real IPC sockets (`kernel.sock`), real tmpfs, bwrap namespaces     │
│   • HTTP mocking via wiremock, real crypto operations                  │
│   • Location: crates/capcli-core/tests/integration/                    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                         TIER 1: UNIT (UNIT)                            │
│   • Pure isolated functions (AST parser, token-bucket math)            │
│   • Petgraph acyclic graph checks, shorthand expansions                │
│   • Zero mocks, zero network, deterministic single-thread              │
│   • Location: crates/capcli-core/tests/unit/                           │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. The Anti-Slop Confusion Matrix

AI agents generating tests frequently hallucinate false confidence through **test slop**: mocking out the component being tested, asserting tautologies, or writing inverted tests where an unexpected error code passes the test.

The **Test Confusion Matrix** categorizes test assertions relative to **Physical World Reality**:

```
                              ACTUAL ENGINE REALITY
                       Invariant Upheld       Invariant Breached
                    ┌──────────────────────┬──────────────────────┐
    TEST     Pass   │    TRUE POSITIVE     │    FALSE POSITIVE    │
   RESULT           │   (Valid Contract)   │    (AI SLOP BUG)     │
                    ├──────────────────────┼──────────────────────┤
             Fail   │    FALSE NEGATIVE    │    TRUE NEGATIVE     │
                    │   (Flaky / Brittle)  │   (Valid Denial)     │
                    └──────────────────────┴──────────────────────┘
```

### 3.1 Confusion Matrix Quadrant Definitions

| Quadrant | Engine State | Test Assertion | Classification | Remediation Requirement |
|---|---|---|---|---|
| **True Positive (TP)** | Engine successfully commits valid mutation within policy bounds. | Test asserts `exit 0`, `state_modified: true`, row presence, and valid SHA-256 chain link. | **Valid Success Assertion** | Must verify subsequent state reads and ledger linkages. |
| **True Negative (TN)** | Engine intercepts illegal mutation (e.g., unbounded UPDATE). | Test asserts `exit 2/3`, `state_modified: false`, diagnostic span, and proves **zero rows mutated**. | **Valid Denial Assertion** | Must execute direct database query to prove zero side effects occurred. |
| **False Positive (FP)** | Engine has a critical bypass, leak, or silent mutation. | Test passes because the agent used `.is_ok()`, asserted on generic strings, or mocked the authorizer. | **AI SLOP (CRITICAL RISK)** | **STRICTLY PROHIBITED.** Caught by Anti-Slop Linter Laws. |
| **False Negative (FN)** | Engine behaves correctly, but test fails due to nondeterminism. | Test fails because it asserted on raw timestamps, unstable JSON key order, or unseeded randoms. | **FLAKY TEST (DEBT)** | **STRICTLY PROHIBITED.** Replace with normalized projections or virtual clocks. |

---

## 4. Anti-Slop Linter Laws (AS-Laws)

Every test written by an autonomous developer agent must strictly satisfy these eight structural laws. Any test failing an AS-Law must be rejected at CI compile-time:

### AS-01: Banned Mocking Law
* **Rule:** Tests verifying security boundaries (`sqlite3_set_authorizer`, AST checks, `seccomp-bpf`, AES-256 vault decryption, token-bucket counters) must **never mock** the boundary mechanism.
* **Slop Vector:** Agent mocks `AuthorizerCallback` to return `SQLITE_OK` in a unit test to make an invalid query pass.
* **Enforcement:** Static analysis prohibits `mockall` or manual mock traits on any type inside `crates/capcli-core/src/db/authorizer.rs` or `crates/capcli-core/src/routine/jail.rs`.

### AS-02: Zero-Mutation Verification Law
* **Rule:** Every test asserting a non-zero exit code (`exit 2`, `exit 3`, `exit 4`, `exit 5`, `exit 6`) **must physically query the underlying SQLite substrate** following the failed command to prove `state_modified == false` and table row counts remain identical.
* **Slop Vector:** Agent asserts `output.exit_code == 2` on an unbounded `UPDATE`, but the authorizer failed and actually mutated 500 rows before the process died.
* **Enforcement:** Test must run `SELECT count(*) FROM <table>` directly on `workspace.db` before and after execution and assert strict equality.

### AS-03: Typed Exit & Diagnostic Match Law
* **Rule:** Prohibit asserting `.is_err()` or `.is_ok()` without explicitly validating the integer exit code and parsing the structured `CliEnvelope<T>` diagnostic block.
* **Slop Vector:** Agent writes `assert!(cmd.is_err())`. A syntax error in test setup triggers `exit 3`, but the test was intended to verify an AST blast-radius denial (`exit 2`).
* **Enforcement:** Tests must match both `exit_code == N` AND verify the presence of `diagnostic.domain`, `diagnostic.culprit`, and `diagnostic.remedy`.

### AS-04: Deterministic Clock & Space Law
* **Rule:** System wall-clock dependencies (`SystemTime::now()`, NTP, sleep loops) are banned from tests. Tests must step through time deterministically via a simulated synthetic clock (`MockClock`).
* **Slop Vector:** Agent writes `tokio::time::sleep(Duration::from_millis(100))` to test token bucket refills, resulting in CI race conditions and non-deterministic failures.
* **Enforcement:** Token-bucket and claim TTL tests must use explicit epoch ticks injected via the engine API.

### AS-05: Causal Ledger Integrity Law
* **Rule:** Every test asserting a successful mutating write (`exit 0`) must verify the cryptographic link in `_audit`: `prev_hash` must equal the SHA-256 of the prior row, and `result_hash` must match the canonical JSON hash of the output.
* **Slop Vector:** Agent checks that a row was added to `orders`, but the audit pipeline failed silently and wrote zero audit records.
* **Enforcement:** Test asserts `_audit` table sequence ID increment and runs `capcli-core::audit::verify_chain()`.

### AS-06: Tautology Prohibition Law
* **Rule:** Assertions where the expected value is derived from the function output under test are banned.
* **Slop Vector:** `let res = calculate_fuel(&input); assert_eq!(res, calculate_fuel(&input));`
* **Enforcement:** The expected value must be an immutable literal hardcoded in the test specification.

### AS-07: Platform Tier Boundary Law
* **Rule:** Tests for pinned trust must explicitly run in two configurations: Tier 1 (must pass) and Tier 2 (must fail with `E045_TIER2_PINNED_DENIED`).
* **Slop Vector:** Agent runs pinned test on a macOS dev machine; the engine permits it because an unconfined flag was leaked, masking a Tier 2 security violation.
* **Enforcement:** Mock platform probe to inject `PlatformTier::Tier2` and assert immediate hard denial.

### AS-08: Sandbox Scratch Wipe Law
* **Rule:** Tests executing sandboxed routines (`sys exec --sandbox` or `run`) must assert that the `/scratch` tmpfs directory is physically wiped clean after execution.
* **Slop Vector:** Guest routine leaves leaked files or residual state on the host filesystem undetected.
* **Enforcement:** Integration harness asserts that the scratch directory UUID does not exist post-execution.

---

## 5. Narrative Case Specification Schema

All case files in `cases/{domain}/` must adhere strictly to the following YAML schema:

```yaml
# Schema template for cans/artifacts/test-plan/cases/{domain}/{case_id}.yaml
$schema: "test-plan/case/v1"
case_id: "string (e.g. da_01_unbounded_update_ast_kill)"
title: "string (concise narrative title)"
domain: "kernel_physics | database_authorizer | wire_egress | budget_cascade | audit_dag | trust_ladder | schema_evolution | coordination_claims | bindings_triggers | vault_secrets | sdk_harness"
target_tier: "unit | integration | e2e"
target_crate: "crates/capcli-core | crates/capcli-cli | crates/capcli-daemon"

invariant:
  law_reference: "string (e.g. cans/physics.md#Layer-2:-SQL-AST-check)"
  statement: "string (the physical invariant being guaranteed)"
  blast_radius_if_breached: "string (worst-case enterprise fallout if broken)"

confusion_matrix:
  quadrant: "true_positive | true_negative"
  slop_risk: "string (how an AI agent might fake this test)"
  anti_slop_mitigation: "string (how AS-laws prevent the fake test)"

setup:
  env: "dev | sim | prod"
  platform_tier: "tier_1 | tier_2"
  caller_identity:
    principal: "string"
    agent_id: "string"
    trust: "draft | reviewed | pinned"
  initial_state:
    schema_yaml: "string | null"
    tables:
      - name: "string"
        row_count: 0
    vault_secrets: []

execution:
  trigger: "cli_subcommand | rust_api | json_rpc"
  command: "string (e.g. capcli sql \"UPDATE orders SET status = 'shipped'\" -m \"test\")"
  input_params: {}

expected_observations:
  exit_code: 0
  state_modified: false
  diagnostic:
    domain: "string"
    culprit: "string"
    remedy: "string"
  database:
    row_count_delta: 0
    tables_mutated: []
  wire:
    packets_transmitted: 0
    syscall_42_trapped: false
  audit:
    event_emitted: "string"
    chain_valid: true
    state_modified_field: false

anti_slop_assertions:
  - rule: "AS-02"
    verification: "string (exact SQL check performed post-execution)"
  - rule: "AS-03"
    verification: "string (exact structured envelope check)"
```

---

## 6. Master Test Plan Bible & Case Catalog

This catalog is the definitive index of physical laws, edge cases, and failure modes across `capcli`. Every case below is codified in its respective atomic YAML file in `cases/` (minimum 12–16 cases per domain, 146 cases total).

### 6.1 Kernel Physics (`cases/kernel_physics/`)

| Case ID | Target Tier | Invariant & Scenario Narrative | Matrix | Banned Slop Pattern |
|---|---|---|---|---|
| `kp_01_syscall_seccomp_trap.yaml` | Integration | Guest routine attempts raw `connect()` via socket syscall 42; `seccomp-bpf` traps and kills execution with `exit 2`. | TN | Mocking the guest process or skipping the actual kernel jail harness. |
| `kp_02_platform_tier2_microvm_boot.yaml` | Integration | Daemon boots on macOS/Windows; requires microvm or wasm provider; refuses unconfined host broker execution with `exit 3`. | TN | Falling back to unconfined host process execution without hard refusal. |
| `kp_03_authorizer_prepare_time_abort.yaml` | Unit | Statement with unpermitted column access is blocked inside `sqlite3_set_authorizer` during `prepare_v2` before single byte executes. | TN | Catching error at execution time instead of at prepare time. |
| `kp_04_bytecode_openwrite_discrepancy.yaml` | Unit | Statement masquerading as read (SELECT invoking mutating function) triggers `OpenWrite` VDBE opcode; Layer 1.5 traps and kills. | TN | Relying only on regex or simple keyword matching for "SELECT". |
| `kp_05_ntp_clock_drift_warning.yaml` | Integration | Host clock skew vs NTP exceeds 500ms; kernel emits diagnostic warning and switches internal sequencing to CLOCK_MONOTONIC without halting execution. | TP | Aborting boot on transient NTP skew instead of falling back to monotonic causal ordering. |
| `kp_06_tamper_hashchain_quarantine.yaml` | Integration | Row 4 in `_audit` table has its payload modified; next boot detects broken SHA-256 chain, routes corrupted sequence to `audit.quarantine.jsonl`, and alerts without bricking clean state reads. | TN | Aborting entire kernel boot instead of isolating corrupted leaves to quarantine. |
| `kp_07_secret_leak_memory_zeroize.yaml` | Unit | Subshell CLI completes execution; in-memory decrypted AES-256 vault buffer is overwritten with zeroes via `zeroize`. | TP | Asserting variable scope drop without reading raw pointer memory to verify zeroization. |
| `kp_08_missing_bwrap_tier1_fallback.yaml` | Integration | Linux host missing `bwrap` binary or unprivileged userns automatically fails over to rootless container provider (`crun`/`podman`) and passes validation. | TP | Failing boot when alternative hardened container backends are installed. |
| `kp_09_broken_tmpfs_scratch_isolation.yaml` | Integration | Guest routine writes temporary files to `/scratch`; post-execution probe verifies host directory was cleanly wiped. | TP | Asserting process success without asserting scratch directory removal on host. |
| `kp_10_posix_locking_compliance_probe.yaml` | Unit | Kernel checks SQLite WAL POSIX advisory lock support on target volume; non-compliant network mounts (NFS/CIFS) rejected. | TN | Allowing DB creation on network filesystems lacking advisory lock support. |
| `kp_11_audit_sink_error_quarantine.yaml` | Integration | SQLite write failure on `audit.db` triggers fallback write to `audit.quarantine.jsonl`; alerts via dead-letter without crashing runtime frame. | TN | Halting entire process with exit 5 when out-of-band quarantine ledger is available. |
| `kp_12_sigkill_subshell_transaction_rollback.yaml` | Integration | Subprocess running guest routine receives SIGKILL; kernel WAL supervisor detects dead PID and rolls back uncommitted transaction. | TN | Leaving dangling locks in `claims` or leaving SQLite WAL in busy uncommitted state. |
| `kp_13_unprivileged_userns_docker_check.yaml` | Integration | Host running inside Docker without unprivileged user namespaces automatically falls over to gVisor or microVM isolation without security degradation. | TP | Refusing boot inside containers instead of routing to supported containerized isolation providers. |
| `kp_14_dynamic_seccomp_profile_switch.yaml` | Unit | Jail runner applies distinct dynamic seccomp profiles per runtime (`profile_python` vs `profile_bun_node` vs `profile_binary`). | TP | Applying universal permissive seccomp profile across all language runtimes. |
| `kp_15_root_help_stub_ceiling.yaml` | E2E | `capcli --help` outputs strictly <= 6 lines and exits 0; references `search` and forbids dumping full command tree. | TP | Allowing standard bloated CLI help output that blows LLM context windows. |
| `kp_15_sigterm_preemption_exit6_checkpoint.yaml` | Integration | Host SIGTERM hits a disposable worker mid-frame; trap flushes cursor checkpoint, drops claims, parks frame in `_suspended_tasks` with `exit 6`, emits `swarm.preemption_yield`. | TN | Asserting exit 6 without proving the parked frame, checkpoint cursor, and released claims. |
| `kp_16_network_partition_sync_audit_exit5.yaml` | Integration | Spoke-Hub connection lost during sync audit delivery; ephemeral spoke aborts immediately with `exit 5`, no local spool, no exit 0 without central audit receipt. | TN | Buffering the audit event to local disk and completing locally — the fail-open ghost path. |

### 6.2 Database Floor & C-Authorizer (`cases/database_authorizer/`)

| Case ID | Target Tier | Invariant & Scenario Narrative | Matrix | Banned Slop Pattern |
|---|---|---|---|---|
| `da_01_unbounded_update_ast_kill.yaml` | E2E | `UPDATE orders SET status = 'shipped'` without `WHERE` or `LIMIT` dies immediately with `exit 2`; zero rows touched. | TN | Asserting exit 2 without verifying with `SELECT count(*)` that zero rows were changed. |
| `da_02_where_tautology_bypass_kill.yaml` | Unit | Malicious query `UPDATE users SET role = 'admin' WHERE id = '1' OR 1=1` is trapped mid-flight by VDBE mutation hook on row 2. | TN | Relying on AST pattern matching rather than physical VDBE update hook row counters. |
| `da_03_multi_statement_injection.yaml` | Unit | Input `SELECT 1; DROP TABLE users;` passed to query engine is rejected by AST multi-statement parser rule. | TN | Splitting statements with string `.split(';')` rather than AST tokenizer validation. |
| `da_04_system_table_write_denial.yaml` | Integration | Agent issues `INSERT INTO _budget_frames VALUES (...)`; C-authorizer on `workspace.db` rejects write to system table with `SQLITE_DENY`. | TN | Granting agent write permissions to system tables in test fixture setup. |
| `da_05_ddl_trust_floor_enforcement.yaml` | E2E | Draft caller runs `ALTER TABLE orders ADD COLUMN rush boolean`; rejected with `exit 2` (ALTER requires `reviewed`). | TN | Running test in `dev` with elevated `reviewed` trust pre-configured. |
| `da_06_connection_queue_busy_timeout.yaml` | Integration | Two concurrent transactions contend for SQLite WAL lock; second transaction blocks until `busy_timeout` then fails cleanly with `exit 2`. | TN | Using uncontrolled threads without lock step synchronization. |
| `da_07_prepared_statement_cache_invalidation.yaml` | Unit | Table schema is migrated; cached VDBE prepared statement detects schema cookie change and recompiles cleanly. | TP | Restarting the entire process to wipe cache rather than testing in-flight invalidation. |
| `da_08_column_immutability_enforcement.yaml` | Unit | Column defined with immutable shorthand (`int~`) rejects UPDATE attempt via C-authorizer `deny_columns_write`. | TN | Checking column update block in application logic rather than inside SQLite authorizer. |
| `da_09_table_imm_rows_delete_denial.yaml` | Unit | Table tagged `imm_rows: true` rejects DELETE statements via SQLite authorizer returning `SQLITE_DENY`. | TN | Allowing DELETE to succeed and checking soft-delete flags. |
| `da_10_unbounded_delete_ast_kill.yaml` | E2E | `DELETE FROM audit_staging` without WHERE clause killed at prepare-time with `exit 2`. | TN | Catching error post-delete or assuming dry-run mode automatically. |
| `da_11_foreign_key_cascade_authorizer_trap.yaml` | Integration | Deleting row triggers cascading delete on child table where child table has immutable constraint; authorizer halts cascade. | TN | Disabling foreign keys in test SQLite connection. |
| `da_12_disallowed_sqlite_function_trap.yaml` | Unit | Query invoking `load_extension('evil.so')` or `writefile('/etc/passwd')` denied by authorizer function allowlist. | TN | Relying on filesystem permissions rather than SQLite authorizer function intercept. |
| `da_13_row_ceiling_transaction_overflow.yaml` | Integration | Transaction inserting 501 rows in single batch exceeds 500-row insert ceiling; aborted cleanly with `exit 2`. | TN | Truncating input array silently instead of aborting transaction. |

### 6.3 Wire Floor & Quota Brokerage (`cases/wire_egress/`)

| Case ID | Target Tier | Invariant & Scenario Narrative | Matrix | Banned Slop Pattern |
|---|---|---|---|---|
| `we_01_proactive_bucket_exhaustion.yaml` | Unit | Proactive token bucket has 0 tokens remaining; client-side pre-call check aborts before packet reaches wire. | TN | Asserting network timeout instead of local client-side rate refusal. |
| `we_02_dynamic_jsonpath_header_sync.yaml` | Integration | Provider returns `X-Business-Use-Case-Usage` JSON header; kernel dynamic parser updates local quota bucket via JSONPath. | TP | Using fixed RFC headers only and ignoring nested JSON header paths. |
| `we_03_background_priority_yield_exit6.yaml` | E2E | Background task hits quota floor (<15 tokens); frame is suspended, committed to `_suspended_tasks`, returns `exit 6`. | TN | Killing task as hard failure (`exit 2`) instead of graceful yield (`exit 6`). |
| `we_04_vault_bearer_egress_injection.yaml` | Integration | Routine calls `ctx.api.call("stripe.charges")`; kernel proxy injects vaulted Authorization header; secret never enters guest memory. | TP | Inspecting guest runtime memory and finding the secret in plaintext. |
| `we_05_unregistered_ip_outbound_block.yaml` | Integration | Outbound HTTP request targets raw IP address (`192.168.1.50`); kernel egress proxy rejects call (domain allowlist only). | TN | Permitting raw IP connection in test harness environment. |
| `we_06_sim_mode_mock_fallback.yaml` | Integration | Verb in `sim` environment has `sim_mode: mock`; kernel serves fixture from `apis/<provider>.mock.yaml` without touching wire. | TP | Allowing packet to leak to external test server during simulation run. |
| `we_07_429_zero_bucket_yield.yaml` | Integration | Remote API returns HTTP 429; kernel zeros out local token bucket, suspends executing frame into `_suspended_tasks` (exit 6), and locks egress until `Retry-After`. | TN | Continuing outbound attempts when external shared quota is exhausted. |
| `we_08_standard_priority_yield_floor.yaml` | Unit | Standard priority task checks quota; available tokens equal 5; task yields cleanly with `exit 6`. | TN | Allowing standard task to drain bucket down to 0 like a critical task. |
| `we_09_critical_priority_pool_drain.yaml` | Unit | Critical priority task checks quota; available tokens equal 3; task permitted to consume down to 0 tokens. | TP | Blocking critical task at background threshold (15 tokens). |
| `we_10_wire_payload_byte_cap_breach.yaml` | Integration | Egress proxy detects outbound POST payload size exceeding 65,536 bytes; blocks call before socket transmission. | TN | Streaming oversized request to physical server before checking limit. |
| `we_11_unimported_verb_egress_denial.yaml` | Unit | Routine attempts to invoke unimported or retired OpenAPI verb; proxy rejects call with `exit 2`. | TN | Auto-importing external endpoints on invoke without prior catalog import. |
| `we_12_ephemeral_bearer_auto_refresh.yaml` | Integration | Egress proxy detects bearer token expiration (`expires_at < now`); executes OAuth token refresh flow before dispatching main request. | TP | Passing expired token and expecting remote API 401 handling. |
| `we_13_sim_rehearsal_isolated_quota.yaml` | Integration | High-volume replay executed in `sim` environment burns sim quota bucket; prod bucket balance remains 100% untouched. | TP | Sharing a single quota bucket across environments. |

### 6.4 Budget Cage & Frame Cascade (`cases/budget_cascade/`)

| Case ID | Target Tier | Invariant & Scenario Narrative | Matrix | Banned Slop Pattern |
|---|---|---|---|---|
| `bc_01_downward_min_inheritance.yaml` | Unit | Parent frame (ops=20) inspects child routine (declared ops=50); pre-flight static analysis detects child starvation and returns `can_invoke_now: false`. | TP | Permitting invocation when declared child branch exceeds available parent headroom. |
| `bc_02_session_ops_ceiling_starvation.yaml` | Integration | Ten child routines execute 5 ops each; total session ops ceiling (50) is reached; 11th call dies with `exit 2`. | TN | Resetting session counters across child frame pushes. |
| `bc_03_leaf_op_51_hard_kill.yaml` | E2E | Routine without declared custom limit attempts op #51; kernel watchdog halts frame with `exit 2` at boundary. | TN | Allowing half-executed state mutations on the 51st operation. |
| `bc_04_duration_watchdog_cleanup.yaml` | Integration | Guest routine enters infinite loop; watchdog timer trips at 300s (simulated); process killed, transaction rolled back. | TN | Leaking orphaned child processes or zombie threads after kill. |
| `bc_05_fuel_pool_depletion_exit2.yaml` | Unit | Routine exceeds session fuel allocation (100,000 units); kernel denies subsequent primitive invocation. | TN | Continuing execution with negative fuel balance. |
| `bc_06_priority_floor_preemption_exit6.yaml` | Integration | Background task executes when tokens_available < 15; frame preempted with exit 6 and parked in _suspended_tasks. | TN | Permitting background tasks to drain quota below 15 tokens. |
| `bc_07_suspended_task_refill_resume.yaml` | Integration | Daemon cron detects quota refill epoch passed; picks up frame from `_suspended_tasks` and re-dispatches to completion. | TP | Manually resuming task via test command rather than verifying daemon auto-dispatch. |
| `bc_08_nesting_depth_ceiling_refusal.yaml` | Unit | Call stack exceeds 5 nested routine invocations; kernel frame push aborts with `exit 2` (`max_nesting_depth_exceeded`). | TN | Permitting unbounded recursion between routine callers. |
| `bc_09_rows_affected_pool_exhaustion.yaml` | Integration | Routine attempts batch write affecting 150 rows under a 100-row trust pool ceiling; transaction aborted with `exit 2`. | TN | Committing the first 100 rows and discarding the remaining 50. |
| `bc_10_wire_egress_session_pool_cascade.yaml` | Unit | Session-level egress bytes pool (4MB) exhausted across multiple child routines; subsequent API calls blocked. | TN | Scoping wire bytes exclusively per routine rather than across the session. |
| `bc_11_parent_frame_reconciliation_audit.yaml` | Integration | Child routine pops; kernel emits `budget.frame_pop` event returning unburned ops and fuel to parent frame pool. | TP | Dropping parent frame state or failing to reconcile balances upon child exit. |
| `bc_12_suspended_task_max_deferments_abort.yaml` | Integration | Suspended task deferred 5 times hits yield_max_deferments ceiling; daemon aborts task with exit 2 to prevent starvation loops. | TN | Indefinitely deferring suspended tasks across infinite quota refills. |
| `bc_13_inspect_preflight_can_invoke_verdict.yaml` | Unit | `inspect` evaluates routine against depleted session ops; returns `can_invoke_now: false` and lists tightest constraint. | TN | Returning `can_invoke_now: true` when ops headroom is 0. |
| `bc_14_hub_atomic_fuel_arbitration.yaml` | Integration | 50 spokes burn against one session pool; every deduction executes atomically on Hub workspace.db; the primitive past exhaustion halts with `exit 2`, final consumed exactly 10000. | TN | Running spokes sequentially or mocking per-spoke counters so the overspend race never exists. |
| `bc_15_spoke_prereserve_preemption_floor.yaml` | Integration | Spokes pre-reserve 1000-fuel blocks via RPC and burn locally; Hub low-token floor yields all non-critical spokes with `exit 6` on one tick, critical spoke exempt. | TN | Reading local block totals without Hub reconciliation, or yielding one spoke at a time. |

### 6.5 Memory Spine & Causal DAG (`cases/audit_dag/`)

| Case ID | Target Tier | Invariant & Scenario Narrative | Matrix | Banned Slop Pattern |
|---|---|---|---|---|
| `ad_01_sha256_prev_hash_linking.yaml` | Unit | Each new row in `_audit` hashes previous row's `prev_hash` + fields; proves immutable linear ledger. | TP | Using autoincrement ID alone without validating cryptographic hash chain. |
| `ad_02_sink_failure_quarantine_fallback.yaml` | Integration | `audit.db` unreachable; kernel flushes uncommitted events to memory buffer and quarantine log before raising emergency alert. | TN | Crashing transactional execution without attempting out-of-band quarantine spool. |
| `ad_03_causal_dag_parent_pointer.yaml` | Unit | Child primitive execution records parent operation ID in `caused_by`; tree traversal walks cleanly back to session root. | TP | Leaving `caused_by` null on nested routine calls. |
| `ad_04_fpa_masking_redaction.yaml` | Unit | Column marked `mask=true` is queried; audit payload and CLI terminal redact value via Format-Preserving Anonymization. | TP | Asserting redaction using raw black box unicode glyphs (████) in machine JSON payloads. |
| `ad_05_w3c_traceparent_propagation.yaml` | Integration | Inbound HTTP request carries W3C `traceparent`; kernel captures trace ID and binds all subsequent leaf operations to it. | TP | Generating random internal trace IDs and ignoring incoming W3C header. |
| `ad_06_historical_replay_idempotency.yaml` | Integration | Historical session replayed in `sim`; database ops succeed, external HTTP calls flagged `replay: manual` are not dispatched. | TN | Accidental physical re-dispatch of external HTTP mutations during replay. |
| `ad_07_jsonl_mirror_flush_cadence.yaml` | Integration | High-frequency DB writes occur; integration verifies JSONL export mirror is synchronized within 5-minute hard SLA. | TP | Asserting in-memory queue state without verifying physical JSONL file on disk. |
| `ad_08_denial_logging_effect_none.yaml` | Integration | Query blocked by C-authorizer; audit log writes record with `decision: denied`, `effect: none`, and specific rule ID. | TN | Skipping audit logging when an operation is denied. |
| `ad_09_tamper_detection_root_worm_walk.yaml` | Integration | Scheduled integrity walk checks local hash chain against simulated offsite S3 WORM root checkpoint; detects divergence. | TN | Asserting ledger health without checking root anchor witness. |
| `ad_10_genesis_event_hash_anchor.yaml` | Unit | First audit event in newly provisioned world verifies `prev_hash` is initialized to deterministic 64-zero SHA-256 anchor. | TP | Using arbitrary or random seed values for genesis block parent hash. |
| `ad_11_trace_traversal_root_intent.yaml` | Unit | `sys audit trace <op-id>` walks DAG upwards through multiple routine frames to output the initial user session intent. | TP | Returning partial trace or truncating at first subroutine boundary. |
| `ad_12_audit_query_parameterization.yaml` | E2E | `sys audit query` command rejects raw string concatenation; requires `-p key=val` parameter bindings. | TN | Permitting raw unparameterized SQL against system audit mirror. |
| `ad_13_kms_witness_signature_checkpoint.yaml` | Integration | Kernel witness worker periodically signs current ledger root hash with KMS key and appends to `witness.log`. | TP | Stamping checkpoints without cryptographic digital signature. |

### 6.6 Trust Ladder & Promotion (`cases/trust_ladder/`)

| Case ID | Target Tier | Invariant & Scenario Narrative | Matrix | Banned Slop Pattern |
|---|---|---|---|---|
| `tl_01_draft_write_to_prod_denial.yaml` | E2E | Caller with `draft` trust attempts mutating write in `prod` environment; denied with `exit 2` (`draft_writes: deny`). | TN | Permitting draft writes in prod when `--intent` is provided. |
| `tl_02_tier2_pinned_execution_refusal.yaml` | E2E | Host is Tier 2 (macOS); caller executes routine with `pinned` trust; denied with `exit 2` (`E045_TIER2_PINNED_DENIED`). | TN | Bypassing platform check because host machine happens to be Darwin in CI. |
| `tl_03_auto_promotion_conjunction_pass.yaml` | Integration | Routine meets all 5 auto-promotion metrics in sim (100% replay pass, zero denials, zero drift); promotes to `reviewed`. | TP | Promoting routine when 4 of 5 metrics pass and 1 fails. |
| `tl_04_canary_telemetry_auto_demote.yaml` | Integration | Promoted routine experiences error spike during 1-hour canary window; autonomous watchdog auto-demotes trust to `draft`. | TN | Leaving failing routine in `pinned` state awaiting manual human intervention. |
| `tl_05_unproven_template_draft_floor.yaml` | Unit | Newly imported routine template enters system; kernel forces trust rung to `draft` regardless of bundle claim. | TN | Trusting template manifest declaration of "pinned". |
| `tl_06_contract_schema_promotion.yaml` | Integration | External API verb undergoes live response JSON Schema validation and shadow canary run; promotes only on 100% schema match. | TP | Elevating verb based on arbitrary invocation counts rather than schema contract proof. |
| `tl_07_bulk_operations_reviewed_floor.yaml` | E2E | Routine at draft trust attempts bulk update (>10 rows); rejected at policy gate (`bulk_operations` requires `reviewed`). | TN | Allowing draft routines to execute bulk updates in development environments. |
| `tl_08_cross_agent_callee_reviewed_floor.yaml` | Unit | Routine authored by Agent A calls Routine authored by Agent B; call rejected because callee is currently in `draft`. | TN | Permitting draft routines to be cross-imported between autonomous agents. |
| `tl_09_monotonic_ascent_skip_denial.yaml` | E2E | Human runs `routine ship <name> pinned` on a routine currently in `draft`; rejected (must graduate to `reviewed` first). | TN | Permitting elevation skips directly from draft to pinned. |
| `tl_10_demotion_zero_resistance_pass.yaml` | Unit | Demotion command (`routine rollback --to-trust draft`) executes immediately without waiting for gate metrics or confirmation. | TP | Adding artificial friction or approval queues to demotion paths. |
| `tl_11_promotion_queue_sla_breach_alert.yaml` | Integration | Routine resides in human review queue for 49 hours; `sys doctor` raises `promotion.sla_breached` alarm (threshold: 48h). | TN | Silently letting routines languish in pending review queues indefinitely. |
| `tl_12_human_veto_rollback_trust.yaml` | Integration | Human inspector vetoes promoted routine during canary window; routine immediately rolled back to `draft` and unpinned. | TP | Requiring a code rebuild or new version bump to execute human veto rollback. |
| `tl_13_circuit_breaker_demotion_streak.yaml` | Integration | Routine has 20 consecutive runs with success rate <0.70; autonomous circuit-breaker demotes routine to `draft`. | TN | Allowing a broken pinned routine to repeatedly fail in production without auto-demotion. |

### 6.7 Schema Evolution & Validation Gates (`cases/schema_evolution/`)

| Case ID | Target Tier | Invariant & Scenario Narrative | Matrix | Banned Slop Pattern |
|---|---|---|---|---|
| `se_01_yaml_syntax_gate1_refusal.yaml` | Unit | `schema.yaml` contains invalid YAML indentation or tab characters; Gate 1 parser halts with `exit 3`. | TN | Letting YAML parser panic instead of returning structured diagnostic refusal. |
| `se_02_circular_dependency_gate2_refusal.yaml` | Unit | Table A references Table B; Table B references Table A; Gate 2 petgraph cycle check aborts with `exit 3`. | TN | Attempting DDL creation and relying on SQLite runtime error. |
| `se_03_lockfile_hash_drift_prod_gate3_refusal.yaml` | Integration | `schema.yaml` is edited on disk without updating `capcli.lock`; boot in prod refuses execution with `exit 3`, while boot in dev auto-recompiles cleanly. | TN | Aborting development workflows on non-production lockfile drift or permitting uncompiled prod changes. |
| `se_04_live_pragma_drift_gate4_refusal.yaml` | Integration | Table column added directly to SQLite via external tool; `sys doctor` PRAGMA check detects drift and refuses boot. | TN | Silently merging unmanaged columns into compiled schema. |
| `se_05_forward_ddl_snapshot_rollback.yaml` | Integration | Gate 5 executes test DDL on temporary snapshot; transaction fails; snapshot auto-restores; live DB untouched. | TN | Running migration on live database without verifying clean rollback on snapshot. |
| `se_06_env_merge_prod_crypto_challenge.yaml` | E2E | Destructive schema merge into `prod` without valid out-of-band cryptographic challenge signature is rejected with `exit 2`. | TN | Permitting production mutations via terminal CLI bypass flags instead of cryptographic proof. |
| `se_07_shorthand_expansion_ddl_generation.yaml` | Unit | Shorthand notation (`int~`, `text!`, `pk`, `mask=true`) compiles deterministically to correct SQLite DDL dialect. | TP | Manually writing SQL DDL in test rather than asserting compiled output from YAML shorthands. |
| `se_08_system_schema_tamper_boot_refusal.yaml` | Integration | Agent modifies `system-schema.yaml` on disk; boot hash check verifies system schema integrity and halts boot with `exit 3`. | TN | Permitting runtime alterations to kernel system tables. |
| `se_09_seed_data_volume_cap_breach.yaml` | Unit | Table definition specifies 51 seed rows; Gate 1 shorthand compiler rejects schema (max 50 rows per seed table). | TN | Allowing large datasets to bypass migration gates disguised as seed data. |
| `se_10_scoped_view_missing_principal_bind.yaml` | Unit | View declares `scoped: principal` but SQL query omits `:principal` bind variable; Gate 2 compile check halts with `exit 3`. | TN | Allowing scoped view creation without enforcing parameter binding compile check. |
| `se_11_forward_only_migration_invariant.yaml` | Integration | Agent attempts down-migration script; kernel rejects execution; mandates VACUUM snapshot restore for backward recovery. | TN | Implementing down-migration SQL execution path in engine. |
| `se_12_namespace_isolation_boundary.yaml` | Integration | Migrations executed in `envs/dev/` namespace; test confirms `envs/prod/` SQLite database file remains untouched. | TP | Running migrations across environment boundaries directly. |
| `se_13_git_push_dry_run_merge_gate.yaml` | Integration | Production merge pipeline runs `git push --dry-run` to verify remote credentials before committing physical DDL changes. | TP | Applying DDL changes locally when remote git repository is unreachable. |
| `se_14_template_bundle_cap_breach.yaml` | Integration | World template bundle exceeding 5MB denied at `capcli template pack` with `exit 2` (`policy.template` size limit). | TN | Extracting unverified large archives to `/tmp` before validating file size. |
| `se_15_template_kernel_compat_refusal.yaml` | Unit | Template declaring `min_kernel_version: 0.5.0` on a 0.4.2 kernel refused intake with `exit 3`. | TN | Ignoring template manifest compatibility constraints during unpack. |
| `se_16_template_ast_rewrite_draft_floor.yaml` | Integration | Routine instantiated via `capcli template scaffold` rewrites routine name via AST, locks trust rung to `draft` (v1), and logs `routine.draft`. | TP | Allowing imported templates to inherit `pinned` trust or running bash sed replacement. |

### 6.8 Coordination & Claims (`cases/coordination_claims/`)

| Case ID | Target Tier | Invariant & Scenario Narrative | Matrix | Banned Slop Pattern |
|---|---|---|---|---|
| `cc_01_exclusive_lease_acquisition.yaml` | Unit | Agent acquires claim on `orders:ORD-10` with TTL 60s; record inserted into `claims` table. | TP | Acquiring claim without mandatory `--reason` or TTL. |
| `cc_02_contested_claim_rejection.yaml` | Integration | Agent B attempts to claim `orders:ORD-10` while Agent A holds active lease; Agent B request denied with `exit 2`. | TN | Overwriting active claim or extending lease without holder credentials. |
| `cc_03_daemon_ttl_lease_dissolution.yaml` | Integration | Claim TTL expires; daemon sweeper tick purges expired claim; resource unlocks without manual unlock call. | TP | Requiring manual intervention to clear expired leases. |
| `cc_04_routine_dependency_retire_block.yaml` | Unit | Routine A is imported by Routine B; agent attempts `routine retire A`; rejected due to active DAG dependency. | TN | Retiring routine and leaving dependent callers with dangling references. |
| `cc_05_process_uid_session_mismatch.yaml` | Integration | Caller passes `--by agt_7f3k` but host OS process UID does not match registration credentials; denied with `exit 3`. | TN | Trusting CLI `--by` argument without validating OS process credentials. |
| `cc_06_sqlite_wal_begin_immediate_serialized.yaml` | Integration | Multiple threads initiate write transactions concurrently; SQLite `BEGIN IMMEDIATE` serializes execution without deadlocks. | TP | Using `BEGIN DEFERRED` which leads to `SQLITE_BUSY` runtime transaction deadlocks. |
| `cc_07_authoring_mutex_concurrent_edit.yaml` | Integration | Two agents attempt simultaneous write to `routines/payout.py`; second agent blocked by filesystem authoring mutex (exit 2). | TN | Allowing concurrent file overwrite without mutual exclusion lock. |
| `cc_08_revoked_agent_token_abort.yaml` | Unit | Agent identity revoked in `agents` table; subsequent call using previously issued HMAC session token rejected with `exit 2`. | TN | Permitting revoked credentials to execute actions until session expiration. |
| `cc_09_session_fork_token_inheritance.yaml` | Integration | Parent session forks child agent; child inherits scoped HMAC token tied to sub-budget frame. | TP | Child session generating new un-scoped root capability tokens. |
| `cc_10_claims_lease_extension_holder_only.yaml` | Unit | Non-owner agent attempts to extend TTL on existing claim; kernel authorizer rejects update with `exit 2`. | TN | Permitting any caller to extend arbitrary resource locks. |
| `cc_11_orphan_claim_process_crash_cleanup.yaml` | Integration | Process dies abruptly while holding database claim; daemon cleanup worker successfully dissolves lease after TTL elapses. | TP | Requiring manual database intervention to recover from process crashes. |
| `cc_12_cross_agent_event_tailing.yaml` | Integration | Agent A executes mutation; Agent B actively monitoring via `sys audit tail` receives live event envelope via Unix domain socket. | TP | Agent B polling SQLite with high-frequency busy-wait queries. |
| `cc_13_disconnect_claims_auto_drop.yaml` | Integration | Spoke socket severed at t0+10s with TTL 300s unexpired; Hub drops both held claims under `disconnect_policy: auto_drop` and rolls back the open transaction; second agent re-acquires instantly. | TP | Waiting out the TTL or deleting claims rows by hand and crediting the disconnect cleanup. |
| `cc_14_heartbeat_loss_spoke_lease_eviction.yaml` | Integration | Spoke heartbeats stop; reaper tick at heartbeat delta 301s > lease_ttl 300s marks agent `expired`, purges both leases, emits `swarm.node_reap` (reason: ttl_expired, claims_released_count: 2). | TP | Expiring the agent by hand or letting real wall-clock time lapse. |

### 6.9 Bindings & Inbound Triggers (`cases/bindings_triggers/`)

| Case ID | Target Tier | Invariant & Scenario Narrative | Matrix | Banned Slop Pattern |
|---|---|---|---|---|
| `bt_01_cron_min_interval_enforcement.yaml` | Unit | Agent attempts `bind cron` with `* * * * *` (1 min); rejected by governance rule (`min_interval_minutes: 5`). | TN | Allowing sub-5-minute cron schedules without throwing policy denial. |
| `bt_02_cron_catchup_fire_limit.yaml` | Integration | Daemon was down for 2 hours; on restart, missed 24 fires; cron evaluator executes exactly 1 catchup fire. | TP | Firing all 24 missed runs in a tight burst. |
| `bt_03_webhook_hmac_signature_refusal.yaml` | Integration | Inbound webhook payload has invalid or missing HMAC signature; kernel rejects at ingress before routine dispatch. | TN | Dispatching webhook to routine before verifying provider HMAC signature. |
| `bt_04_webhook_payload_ceiling_block.yaml` | Integration | Inbound webhook payload exceeds 65,536 bytes; kernel ingress rejects with HTTP 413. | TN | Buffering oversized payloads in memory. |
| `bt_05_endpoint_unpinned_trust_denial.yaml` | E2E | Agent attempts `bind endpoint` on a `draft` routine; rejected with `exit 2` (endpoints require `pinned` trust). | TN | Exposing unpinned or draft routines over HTTP. |
| `bt_06_ask_occ_fence_conflict_abort.yaml` | Integration | Routine suspended via `ctx.ping.ask`; underlying order record modified by external agent before human resolution; resume aborts with `exit 2` on OCC version fence conflict. | TN | Resuming routine execution with stale in-memory state after dependency state mutation. |
| `bt_07_orphan_schedule_retire_disable.yaml` | Integration | Bound routine is retired via `routine retire`; daemon automatically pauses or dissolves associated cron schedule. | TP | Leaving active cron triggers targeting non-existent or retired routines. |
| `bt_08_webhook_rate_limit_throttle.yaml` | Integration | Inbound webhooks exceed 100 events/minute rate cap; kernel returns HTTP 429 and drops payload into dead letter queue. | TN | Processing inbound webhooks without burst rate-limiting. |
| `bt_09_endpoint_partner_key_hash_auth.yaml` | Integration | HTTP request to bound endpoint validates `Authorization: Bearer <key>` against hashed partner keys; rejects invalid keys with 401. | TN | Storing partner API keys in plaintext in the database. |
| `bt_10_ask_question_token_cap_breach.yaml` | Unit | `ctx.ping.ask` question string contains 101 tokens; option gate halts execution (limit: 100 tokens). | TN | Permitting unbounded long-form prompts in human interactive questions. |
| `bt_11_ask_options_count_ceiling.yaml` | Unit | `ctx.ping.ask` supplied with 6 response options; gate rejects suspension request (maximum allowed options: 5). | TN | Permitting unbounded choice menus in structured human inquiries. |
| `bt_12_webhook_ingress_public_url_mandate.yaml` | Unit | Registering external webhook binding with localhost or loopback IP (`127.0.0.1`) without tunnel rejected. | TN | Allowing loopback callback addresses for external webhook providers. |

### 6.10 Vault & Zero-Knowledge Secrets (`cases/vault_secrets/`)

| Case ID | Target Tier | Invariant & Scenario Narrative | Matrix | Banned Slop Pattern |
|---|---|---|---|---|
| `vs_01_missing_secret_cockpit_url_refusal.yaml` | E2E | Routine requests missing secret `stripe_key`; headless run exits 3, outputs Cockpit URL; zero param leakage. | TN | Accepting secret values passed directly as CLI command-line flags. |
| `vs_02_env_var_auto_binding.yaml` | Integration | Host environment has `CAPCLI_SECRET_STRIPE_KEY`; kernel auto-ingests and binds to vault reference without prompt. | TP | Printing environment variable value into audit log or stdout. |
| `vs_03_cli_parameter_injection_banned.yaml` | Unit | Agent attempts `capcli run cap://pay --secret sk_live_123`; CLI parser rejects inline credential parameter. | TN | Permitting `--secret` or inline API tokens in CLI argument lists. |
| `vs_04_aes_256_gcm_ciphertext_rest.yaml` | Unit | Secrets table in `workspace.db` inspected directly; values stored as verified AES-256-GCM ciphertext. | TP | Storing credentials in plaintext or Base64 encoding. |
| `vs_05_draft_routine_secret_read_denial.yaml` | Unit | Routine running at `draft` trust attempts to access credential from vault; policy gate halts run with `exit 2`. | TN | Granting draft routines access to live credentials in dev environment. |
| `vs_06_vault_set_audit_masked_fingerprint.yaml` | Integration | Secret provisioned via `sys vault set`; audit log writes `vault.set` event containing masked string and SHA-256 prefix. | TP | Logging plaintext secret or unmasked credential data to `_audit`. |
| `vs_07_egress_proxy_token_refresh_zeroize.yaml` | Integration | Egress proxy auto-refreshes ephemeral OAuth bearer token; intermediate decrypted buffers zeroized immediately. | TP | Caching decrypted token strings in global heap without zeroization guards. |
| `vs_08_vault_export_plaintext_denial.yaml` | E2E | User executes `capcli sys vault dump`; kernel refuses command (dumping plaintext credentials structurally impossible). | TN | Implementing credential export or print commands in CLI interface. |
| `vs_09_biometric_faceid_cockpit_auth.yaml` | Integration | Cockpit RPC endpoint receives vault injection request; requires valid WebAuthn client signature before encrypting secret. | TP | Allowing vault injection via unauthenticated HTTP POST. |
| `vs_10_secret_scope_environment_isolation.yaml` | Unit | Secret configured with `scope: prod` cannot be queried or injected when session environment is `sim` or `dev`. | TN | Allowing dev/sim environments to pull production secrets. |
| `vs_11_secret_rotation_in_memory_eviction.yaml` | Integration | Secret rotated in vault; daemon in-memory decrypted cache evicted instantly; subsequent call uses new credential. | TP | Retaining stale decrypted secrets in daemon process memory. |
| `vs_12_opaque_vault_handle_dereference_denial.yaml` | Integration | Guest routine attempts to inspect or print raw `vault://` credential bytes; SDK exposes only opaque token ref; socket proxy strips plaintext from logs. | TN | Allocating plaintext credential buffers in guest runtime address space. |

### 6.11 SDK & Guest Harness Contract (`cases/sdk_harness/`)

| Case ID | Target Tier | Invariant & Scenario Narrative | Matrix | Banned Slop Pattern |
|---|---|---|---|---|
| `sh_01_missing_frame_token_trap.yaml` | Integration | Python script imports `capcli` SDK and runs directly without kernel runner; trapped with immediate exit 3. | TN | Allowing guest script to execute outside sandboxed runner wrapper. |
| `sh_02_api_call_inside_db_txn_prohibition.yaml` | Unit | Guest script attempts `ctx.api.call()` inside `with ctx.db.txn():`; SDK throws transaction isolation error. | TN | Allowing long-running network calls inside open database transactions. |
| `sh_03_poll_until_aggregate_accounting.yaml` | Integration | Routine calls `ctx.api.poll_until()` which loops 5 times; kernel charges routine exactly 1 aggregate operation. | TP | Charging 5 independent operations and prematurely exhausting budget. |
| `sh_04_param_type_mismatch_exit3.yaml` | Unit | Routine expects `order_id: Param[int]`; caller supplies `"abc"`; SDK input validation rejects with `exit 3`. | TN | Passing unvalidated types to routine body and crashing at runtime (`exit 4`). |
| `sh_05_overview_result_pagination_schema.yaml` | E2E | Overview routine outputs collection exceeding 500 tokens; SDK rejects raw array and enforces keyset pagination schema `{ items, next_cursor, has_more }`. | TP | Arbitrarily slicing JSON strings with `truncated: true` instead of enforcing structural keyset pagination. |
| `sh_06_direct_socket_connect_trapped.yaml` | Integration | Python script executes `socket.create_connection()`; trapped by seccomp syscall 42 filter; exits 2. | TN | Permitting guest runtime to bypass `ctx.api.call()` via standard networking libraries. |
| `sh_07_manifest_reflection_prove_ipc.yaml` | Integration | `@routine` decorator introspects function AST and parameters; streams declared manifest over Unix domain socket during prove. | TP | Reading manifests by parsing raw source text with regex. |
| `sh_08_undeclared_leaf_anomaly_event.yaml` | Integration | Routine executes undeclared database write; dynamic fingerprint compares against manifest and logs `governance.anomaly`. | TN | Silently executing undeclared operations without emitting anomaly audit event. |
| `sh_09_time_sleep_raw_loop_prohibition.yaml` | Unit | Python script calls `time.sleep()`; SDK linter or runtime watchdog flags busy-wait loop; mandates `ctx.api.poll_until()`. | TN | Permitting blocking sleep loops in sandboxed agent routines. |
| `sh_10_ctx_storage_hmac_presigned_url.yaml` | Integration | `ctx.storage.url('invoice.pdf', ttl=3600)` generates valid HMAC-signed temporary access link. | TP | Returning unsigned or public direct URLs to private object storage. |
| `sh_11_non_serializable_result_exit4.yaml` | Unit | Routine attempts to return a non-JSON serializable object (e.g., active file descriptor); SDK traps and exits 4 cleanly. | TN | Raising raw unhandled runtime exception without standard CLI diagnostic envelope. |
| `sh_12_ctx_db_lock_distributed_lease.yaml` | Integration | Routine acquires lock via `ctx.db.lock("inventory:10")`; verifies lock is recorded in `claims` and auto-cleared on exit. | TP | Managing locks exclusively in memory without persisting to system claims table. |

---

## 7. Machine Validation & Test Generation Protocol

When an autonomous software engineering agent is tasked with adding or modifying code in `capcli`, it must execute the following deterministic protocol:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   AUTONOMOUS AGENT TEST GENERATION                     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
       1. CONSULT TEST PLAN: Locate case in `cases/{domain}/`
          • Parse invariant, target tier, and setup contract
                                    │
                                    ▼
       2. VERIFY CONFUSION MATRIX: Check Matrix Quadrant & Slop Risk
          • Identify required AS-Laws (e.g. AS-02 Zero-Mutation)
                                    │
                                    ▼
       3. AUTHOR TEST IN CRATE: Implement in `crates/{target}/tests/`
          • Tier 1 (Unit) ───────► crates/capcli-core/tests/unit/
          • Tier 2 (Integration) ─► crates/capcli-core/tests/integration/
          • Tier 3 (E2E) ────────► crates/capcli-cli/tests/e2e/
                                    │
                                    ▼
       4. RUN ANTI-SLOP LINTER: Scan test AST for violations
          • Fail on `assert!(true)`, missing `exit_code` checks,
            unverified state mutations, or banned mock usage
                                    │
                                    ▼
       5. EXECUTE TEST SUITE: Verify deterministic pass/fail
          • Run `cargo test --test <name>` across both Tier 1 & Tier 2
```

### 7.1 Automated CI Gate
The CI pipeline runs a dedicated AST test-linter (`cargo check-tests`) that validates all Rust tests against this test plan before running `cargo test`:
1. Every test must be annotated with `#[test_case("case_id")]` referencing an active case in `cases/`.
2. Tests tagged with `quadrant: true_negative` must contain an AST path executing an independent state-verification query.
3. Tests violating any **Anti-Slop Linter Law (AS-01 to AS-08)** fail CI immediately with a compile error.
