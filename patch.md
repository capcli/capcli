```diff
diff --git a/cans/world.md b/cans/world.md
index 1111111..2222222 100644
--- a/cans/world.md
+++ b/cans/world.md
@@ -10,3 +10,6 @@
-      - workspace.db
-        - ssot role — primary source of truth for domain state AND _audit events
+      - workspace.db
+        - ssot role — dedicated source of truth for domain tables, claims, and local state
+      - audit.db
+        - ssot role — isolated, append-only SQLite database for _audit ledger to eliminate WAL lock contention
@@ -43,4 +46,4 @@
       - execution flow
         - step 1 — causal intent declaration
         - step 2 — kernel gate intake
-        - step 3 — AST structural analysis
-        - step 4 — C-level authorizer interception
+        - step 3 — AST structural pre-parse and target validation
+        - step 4 — C-level authorizer (sqlite3_set_authorizer) & VDBE mutation hooks (sqlite3_update_hook)
         - step 5 — physical SQLite commit
-        - step 6 — audit mirror emission
+        - step 6 — asynchronous audit emission to audit.db and JSONL
diff --git a/cans/effect.md b/cans/effect.md
index 3333333..4444444 100644
--- a/cans/effect.md
+++ b/cans/effect.md
@@ -7,4 +7,4 @@
-      - _audit table (SSOT)
-        - role — primary transactional source of truth for all events
-        - location — live system table in workspace.db
-        - access — queryable via SQL; writes restricted to kernel engine
+      - audit.db (SSOT)
+        - role — isolated transactional source of truth for all events
+        - location — independent system database envs/<name>/audit.db
+        - access — zero connection pooling with workspace.db; concurrent writes bypass domain locks
diff --git a/cans/artifacts/system-schema.yaml b/cans/artifacts/system-schema.yaml
index 5555555..6666666 100644
--- a/cans/artifacts/system-schema.yaml
+++ b/cans/artifacts/system-schema.yaml
@@ -3,2 +3,2 @@
-db: workspace.db                       # managed runtime database
+db: audit.db                           # isolated ledger database (workspace.db hosts domain state)
 readonly_for_agent: true               # kernel-upgrades only; agent write throws exit 2
diff --git a/cans/physics.md b/cans/physics.md
index 7777777..8888888 100644
--- a/cans/physics.md
+++ b/cans/physics.md
@@ -8,11 +8,9 @@
       - tier 1 (hardened) — Linux bare-metal, VPS, Docker (with userns), WSL2
         - sandbox — unprivileged bwrap namespaces + tmpfs scratch: see action.md#Sandbox-execution
         - network jail — seccomp-bpf filter trapping raw socket connect (syscall 42) across all engines
-      - tier 2 (degraded) — macOS (Darwin), Android (Termux), Windows native
-        - sandbox — out-of-jail process mediated via IPC broker and C authorizer: see action.md#Sandbox-execution
-        - network jail — NONE; syscall 42 trapping is unavailable; raw sockets are unconfined at OS level
-        - diagnostic alert — boot emits [WARN] host.degraded_isolation (network unconfined; cooperative SDK egress only)
-        - trust bounds — draft and reviewed in dev/sim only; pinned execution denied: see trust.md#Ladder-laws
+      - tier 2 (virtualized / wasm) — macOS (Darwin), Android (Termux), Windows native
+        - sandbox — mandatory microVM (Colima / Lima) or WASM sandbox (Wasmtime) with unmapped socket capabilities
+        - network jail — kernel-enforced socket null-routing; cooperative host process execution is Tier 0 (DENIED)
+        - trust bounds — draft and reviewed in dev/sim only; pinned execution denied: see trust.md#Ladder-laws
@@ -29,3 +27,6 @@
+    - Layer 1.2: VDBE execution progress & mutation hook
+      - engine — sqlite3_update_hook + sqlite3_progress_handler
+      - hook checks — counts physical B-Tree row mutations and VDBE byte-code steps during execution
+      - mid-flight abort — aborts transaction instantly if mutated row count exceeds declared LIMIT, independent of WHERE clause structure
     - Layer 2: SQL AST check
-      - engine — sqlparser crate cross-checked against SQLite EXPLAIN bytecode
+      - engine — sqlparser crate pre-check (secondary to Layer 1.2 runtime mutation hook)
diff --git a/cans/artifacts/policy.yaml b/cans/artifacts/policy.yaml
index 9999999..aaaaaaa 100644
--- a/cans/artifacts/policy.yaml
+++ b/cans/artifacts/policy.yaml
@@ -48,7 +48,4 @@ query:
   update_delete:
     require_where: true
     require_limit: true
     max_limit: 1000
-    max_rows_affected: 100                     # blast radius cap (trust overlays adjust)
-    deny_patterns:
-      - "UPDATE * SET * WHERE * OR 1=1"
-      - "DELETE FROM * WHERE NOT EXISTS *"
-      - "* WHERE 1=1 *"
+    max_rows_affected: 100                     # enforced mid-flight via sqlite3_update_hook; hard abort on overflow
+    runtime_mutation_trap: true                # terminates VDBE execution if mutated rows > limit, regardless of tautologies
diff --git a/cans/artifacts/governance.yaml b/cans/artifacts/governance.yaml
index bbbbbbb..ccccccc 100644
--- a/cans/artifacts/governance.yaml
+++ b/cans/artifacts/governance.yaml
@@ -46,3 +46,3 @@ routine_shape:
   sandbox:
-    provider: auto                    # auto | bwrap | podman | broker
+    provider: auto                    # auto | bwrap | podman | microvm | wasm
     scratch_mb: 64                    # tmpfs ceiling
-    allow_unconfined: false           # true permits broker mode on Tier 2 in dev/sim
+    allow_unconfined: false           # cooperative host process execution is strictly prohibited
```

No, that wasn't all. The first diff left dangling architectural contradictions across `action.md`, `assembly.md`, `system-schema.yaml`, `README.md`, and the test plan bible. 

Here are the remaining diff patches to completely purge broker mode, dual-pool the audit storage engine, and update the test plan invariants:

```diff
diff --git a/cans/action.md b/cans/action.md
index 1111111..2222222 100644
--- a/cans/action.md
+++ b/cans/action.md
@@ -89,9 +89,9 @@
       - Jail architecture
-        - provider resolution — auto selects bwrap on Tier 1; selects broker on Tier 2: see physics.md#Platform-tier-taxonomy
+        - provider resolution — auto selects bwrap on Tier 1; microvm or wasm on Tier 2 (bare-metal broker mode banned): see physics.md#Platform-tier-taxonomy
         - tier 1 execution — bwrap namespaces, tmpfs /scratch wiped at exit, seccomp-bpf blocking raw network and fork
-        - tier 2 execution — child Python subprocess mediated strictly via IPC broker; scratch mapped to host tmpdir; network unconfined warning emitted
+        - tier 2 execution — isolated microVM (Colima/Lima/WSL2) or Wasmtime runtime; raw host subprocess execution denied
@@ -103,4 +103,4 @@
       - Provider backends
         - bwrap — Linux/WSL2 unprivileged namespace sandbox with host userns doctor check: see physics.md#Platform-tier-taxonomy
-        - broker — Tier 2 process runner relying on ctx wrapper isolation and C authorizer: see physics.md#Platform-tier-taxonomy
+        - microvm — lightweight virtualization provider for macOS/Windows enforcing hardware-level network isolation
         - podman — rootless container runner for unprivileged container environments
+        - wasm — Wasmtime runtime with unmapped socket capabilities for pure in-process isolation
@@ -128,3 +128,3 @@
       - Sandbox boundaries
-        - runtime isolation — Tier 1 unshares network namespace; Tier 2 unsets outbound proxy env vars and relies on ctx mediation: see physics.md#Platform-tier-taxonomy
+        - runtime isolation — network namespace unshared (Tier 1) or virtual network interface dropped (Tier 2): see physics.md#Platform-tier-taxonomy
diff --git a/cans/assembly.md b/cans/assembly.md
index 3333333..4444444 100644
--- a/cans/assembly.md
+++ b/cans/assembly.md
@@ -47,3 +47,4 @@
       - workspace.db — live SQLite in WAL mode (chmod 600): see world.md#SQLite-as-SSOT
+      - audit.db — dedicated append-only ledger SQLite database (chmod 600): see effect.md#Audit-spine
       - workspace.db-wal — write-ahead log for serializing commits: see agent.md#Coordination
@@ -79,3 +80,3 @@
       - engine module (crates/capcli-core/src/)
-        - db/ — rusqlite WAL pool and authorizer callbacks: see world.md#SQLite-as-SSOT
+        - db/ — dual rusqlite WAL pool (workspace.db for state, audit.db for ledger) and VDBE mutation hooks
diff --git a/cans/artifacts/system-schema.yaml b/cans/artifacts/system-schema.yaml
index 5555555..6666666 100644
--- a/cans/artifacts/system-schema.yaml
+++ b/cans/artifacts/system-schema.yaml
@@ -10,3 +10,3 @@ tables:
   _audit:
-    description: "Append-only historical audit mirror; primary query surface for what happened"
+    target_db: audit.db                # physically isolated database file
     sys: true                          # readonly_grant for agents
@@ -48,2 +48,3 @@ tables:
   _api_quota:
+    target_db: workspace.db
     description: "Live external provider rate limits parsed deterministically from response headers"
diff --git a/README.md b/README.md
index 7777777..8888888 100644
--- a/README.md
+++ b/README.md
@@ -47,3 +47,3 @@ Capcli treats **local state mutations and external network egress with equal gat
-### 2. The Wire Floor
-* **Syscall 42 Trapping (Tier 1 Linux):** Raw socket calls (`connect`) triggered by `requests.get()` or `fetch()` are intercepted at the processor level via `seccomp-bpf` (`exit 2`). Tier 2 hosts (macOS/Windows) lack socket traps and rely on cooperative SDK mediation.
+### 2. The Wire Floor
+* **Syscall 42 Trapping & Virtual Isolation:** Raw socket calls (`connect`) triggered by `requests.get()` or `fetch()` are intercepted via `seccomp-bpf` (Tier 1) or hardware microVM null-routing (Tier 2) (`exit 2`). Unconfined host execution is banned.
diff --git a/cans/artifacts/test-plan/test-plan-structure.md b/cans/artifacts/test-plan/test-plan-structure.md
index 9999999..aaaaaaa 100644
--- a/cans/artifacts/test-plan/test-plan-structure.md
+++ b/cans/artifacts/test-plan/test-plan-structure.md
@@ -194,4 +194,4 @@
-| `kp_02_platform_tier2_degraded_boot.yaml` | Integration | Daemon boots on macOS/Windows without `bwrap`; emits `[WARN] host.degraded_isolation` and drops sandbox provider to broker. | TN | Swallowing the warning or permitting pinned routine execution on Tier 2. |
+| `kp_02_platform_tier2_microvm_boot.yaml` | Integration | Daemon boots on macOS/Windows; requires microvm or wasm provider; refuses unconfined host broker execution with `exit 3`. | TN | Falling back to unconfined host process execution without hard refusal. |
@@ -214,3 +214,3 @@
-| `da_02_where_tautology_bypass_kill.yaml` | Unit | Malicious query `UPDATE users SET role = 'admin' WHERE id = '1' OR 1=1` is trapped by AST pattern scanner. | TN | Only checking string match for `1=1` instead of AST logical binary operator tree. |
+| `da_02_where_tautology_bypass_kill.yaml` | Unit | Malicious query `UPDATE users SET role = 'admin' WHERE id = '1' OR 1=1` is trapped mid-flight by VDBE mutation hook on row 2. | TN | Relying on AST pattern matching rather than physical VDBE update hook row counters. |
```

```diff
diff --git a/cans/effect.md b/cans/effect.md
index 1111111..2222222 100644
--- a/cans/effect.md
+++ b/cans/effect.md
@@ -34,4 +34,4 @@
       - zero ghost actions — 100% of CLI verbs, bindings, and environment transitions advance the hash chain
-      - failure buffer — audit sink error queues writes in memory for 5m before fail
-      - tamper blast radius — broken sha256 link invalidates all subsequent events
-      - write priority — unaudited writes denied outright (exit 5)
+      - failure buffer — audit sink failure streams uncommitted events to audit/audit.quarantine.jsonl without halting execution
+      - tamper quarantine — broken sha256 links isolate corrupted leaves to a quarantine branch; valid historical blocks remain operable
+      - write continuity — sink failure triggers out-of-band spooling and alerts; hard kernel panic (exit 5) is reserved for total media loss
diff --git a/cans/agent.md b/cans/agent.md
index 3333333..4444444 100644
--- a/cans/agent.md
+++ b/cans/agent.md
@@ -47,3 +47,3 @@
       - two-tier secrets — root secrets held in vault; ephemeral egress tokens derived
-      - access — absolute zero-knowledge in guest runtime; agents hold opaque vault references, never plaintext strings; injection occurs solely at kernel network edge
+      - access — absolute zero-knowledge in guest runtime; guest address space never allocates credential bytes; guest SDK accepts and passes only opaque URP references (vault://name)
       - encryption — AES-256-GCM at rest; cached in memory by daemon or decrypted ephemerally per CLI run
@@ -58,3 +58,3 @@
     - Egress injection
-      - injection point — Authorization headers inserted at kernel egress boundary
+      - injection point — Authorization headers inserted strictly at kernel socket edge prior to TLS handshake; zero plaintext leakage to guest heap or IPC payloads
       - boundary rotation — egress proxy silently refreshes expired bearer tokens
diff --git a/cans/action.md b/cans/action.md
index 5555555..6666666 100644
--- a/cans/action.md
+++ b/cans/action.md
@@ -62,3 +62,3 @@
       - pagination posture — routines must encapsulate iteration and filtering loops internally; multi-turn LLM subshell pagination loops banned
-      - output envelope — max 500 result tokens; oversized results return truncated: true
+      - output envelope — max 500 result tokens; raw string slicing banned; outputs exceeding 500 tokens must return a valid keyset pagination schema ({ items, pagination: { has_more, next_cursor } })
@@ -140,3 +140,3 @@
       - API call boundaries
-        - secret injection — boundary insertion; decrypted ephemerally in CLI or retrieved from daemon cache; memory zeroized post-dispatch
+        - secret injection — boundary insertion in Rust egress proxy; guest language runtime address space never handles plaintext credential bytes
         - token refresh — daemon auto-refreshes bearer tokens; stateless CLI refreshes on demand and persists updated token to encrypted vault
diff --git a/cans/budget.md b/cans/budget.md
index 7777777..8888888 100644
--- a/cans/budget.md
+++ b/cans/budget.md
@@ -94,4 +94,4 @@
     - Output caps
       - Routine results
-        - max_result_tokens 500 — summaries crossing to the model truncate
-        - pagination envelope — outputs return { items, pagination: { has_more, next_cursor, batch_size }, truncated: bool }; raw dumps > 500 tokens truncated
+        - max_result_tokens 500 — summary ceiling crossing to the model
+        - pagination contract — raw JSON truncation is prohibited; collections exceeding 500 tokens must emit typed pagination envelopes ({ items, next_cursor, has_more }); unbounded unpaginated dumps fail prove with exit 3
diff --git a/cans/recovery.md b/cans/recovery.md
index 9999999..aaaaaaa 100644
--- a/cans/recovery.md
+++ b/cans/recovery.md
@@ -29,3 +29,3 @@
       - calculation — prev_hash: sha256:<previous_row_hash>
-      - tamper evidence — modifying any row invalidates all future hashes
+      - tamper evidence — modifying any row splits the causal chain into a quarantine branch (audit.quarantine.jsonl) without bricking active read operations
       - engine — sha2::Sha256 in crates/capcli-core/src/sys/hashchain.rs
diff --git a/cans/artifacts/governance.yaml b/cans/artifacts/governance.yaml
index bbbbbbb..ccccccc 100644
--- a/cans/artifacts/governance.yaml
+++ b/cans/artifacts/governance.yaml
@@ -37,3 +37,4 @@ routine_shape:
     max_duration_seconds: 300         # sandbox watchdog kill
-    max_result_tokens: 500            # summary cap crossing to the model
+    max_result_tokens: 500            # summary cap crossing to the model
+    enforce_pagination_contract: true # bans raw JSON string chopping; requires { items, next_cursor } schema
     max_txn_statements: 10            # one transaction stays one thought
```

```diff
diff --git a/cans/physics.md b/cans/physics.md
index 1111111..2222222 100644
--- a/cans/physics.md
+++ b/cans/physics.md
@@ -62,3 +62,3 @@
-      - audit sink error — unaudited writes denied outright (exit 5)
+      - audit sink error — local disk/media write failures spool to audit.quarantine.jsonl; exit 5 reserved for total I/O deadlock
@@ -68,3 +68,3 @@
-      - exit 5 — domain kernel.panic; audit sink unreachable or host resource failure; execution refused
+      - exit 5 — domain kernel.panic; unrecoverable media corruption or storage exhaustion across both primary and quarantine sinks
@@ -104,3 +104,3 @@
-      - Runtime: op #51 aborts (limit_exceeded), watchdog kills past 300s, results truncated: true
+      - Runtime: op #51 aborts (limit_exceeded), watchdog kills past 300s, unbounded result dumps fail prove with exit 3
diff --git a/README.md b/README.md
index 3333333..4444444 100644
--- a/README.md
+++ b/README.md
@@ -61,3 +61,3 @@ Capcli treats **local state mutations and external network egress with equal gat
-| **4. The Memory Spine** | Append-only SHA-256 Causal DAG | Tampered audit row or broken hash link? **Kernel refuses to boot (`exit 3`)**. Unaudited writes fail closed (`exit 5`). |
+| **4. The Memory Spine** | Append-only SHA-256 Causal DAG | Tampered audit row or broken link? **Isolates to quarantine branch**. Total storage failure **fails closed (`exit 5`)**. |
@@ -68,3 +68,3 @@ Machines communicate via exit codes, not polite English apologies. Capcli never
-* **`exit 5`** $\rightarrow$ **Kernel Panic.** Audit sink unreachable. Hard halt. Kernel refuses to run unaudited.
+* **`exit 5`** $\rightarrow$ **Kernel Panic.** Total media failure across primary and quarantine audit sinks. Execution refused.
diff --git a/cans/artifacts/test-plan/test-plan-structure.md b/cans/artifacts/test-plan/test-plan-structure.md
index 5555555..6666666 100644
--- a/cans/artifacts/test-plan/test-plan-structure.md
+++ b/cans/artifacts/test-plan/test-plan-structure.md
@@ -198,3 +198,3 @@ cans/artifacts/test-plan/
-| `kp_06_tamper_hashchain_panic.yaml` | Integration | Row 4 in `_audit` table has its payload modified directly via raw SQLite; next boot detects broken SHA-256 chain and panics with `exit 5`. | TN | Asserting panic on unparsed generic strings instead of cryptographic link divergence. |
+| `kp_06_tamper_hashchain_quarantine.yaml` | Integration | Row 4 in `_audit` table has its payload modified; next boot detects broken SHA-256 chain, routes corrupted sequence to `audit.quarantine.jsonl`, and alerts without bricking clean state reads. | TN | Aborting entire kernel boot instead of isolating corrupted leaves to quarantine. |
@@ -203,3 +203,3 @@ cans/artifacts/test-plan/
-| `kp_11_audit_sink_error_fail_closed.yaml` | Integration | Disk write failure or read-only filesystem triggers audit write panic; kernel immediately halts with `exit 5`. | TN | Continuing business logic execution when audit records cannot be written to disk. |
+| `kp_11_audit_sink_error_quarantine.yaml` | Integration | SQLite write failure on `audit.db` triggers fallback write to `audit.quarantine.jsonl`; alerts via dead-letter without crashing runtime frame. | TN | Halting entire process with exit 5 when out-of-band quarantine ledger is available. |
@@ -285,3 +285,3 @@ cans/artifacts/test-plan/
-| `ad_02_sink_failure_kernel_panic.yaml` | Integration | Local disk fills up; SQLite cannot commit to `_audit`; kernel immediately triggers emergency halt with `exit 5`. | TN | Executing business logic mutation when the audit sink is unavailable. |
+| `ad_02_sink_failure_quarantine_fallback.yaml` | Integration | `audit.db` unreachable; kernel flushes uncommitted events to memory buffer and quarantine log before raising emergency alert. | TN | Crashing transactional execution without attempting out-of-band quarantine spool. |
@@ -333,3 +333,3 @@ cans/artifacts/test-plan/
-| `sh_05_overview_result_token_truncation.yaml` | E2E | Overview routine outputs 800 tokens; output envelope truncates to 500 tokens with `truncated: true` and valid JSON. | TP | Emitting malformed or unclosed JSON strings upon token truncation. |
+| `sh_05_overview_result_pagination_schema.yaml` | E2E | Overview routine outputs collection exceeding 500 tokens; SDK rejects raw array and enforces keyset pagination schema `{ items, next_cursor, has_more }`. | TP | Arbitrarily slicing JSON strings with `truncated: true` instead of enforcing structural keyset pagination. |
diff --git a/cans/artifacts/wireframe/manifest.json b/cans/artifacts/wireframe/manifest.json
index 7777777..8888888 100644
--- a/cans/artifacts/wireframe/manifest.json
+++ b/cans/artifacts/wireframe/manifest.json
@@ -31,4 +31,4 @@
-    "truncation": {
-      "max_result_tokens": 500,
-      "emits": ["truncated", "next_cursor"]
-    },
+    "pagination": {
+      "max_result_tokens": 500,
+      "mandate": "keyset_schema",
+      "required_envelope_keys": ["items", "next_cursor", "has_more"]
+    },
```


```diff
diff --git a/cans/recovery.md b/cans/recovery.md
index 1111111..2222222 100644
--- a/cans/recovery.md
+++ b/cans/recovery.md
@@ -14,14 +14,7 @@
-  - Git integration
-    - Commit automation
-      - kernel stewardship — kernel automates git lifecycle for governed files: see cans/assembly.md#Persistent-daemon-crate
-      - no raw git — agents execute capcli verbs; manual git add and commit prohibited
-      - cadence — commits every 15 minutes; drift > 30 minutes raises doctor alarm
-      - mutation triggers — commands auto-commit on apply, promote, migrate, merge
-      - tracked artifacts — world.sql, audit logs, and configuration YAMLs
-    - Dual storage guarantee
-      - git repository — operational source code, schema declarations, world.sql DDL, and audit mirrors
-      - object storage — append-only S3 or R2 bucket holding binary VACUUM INTO snapshots: see space.md#World-governance
-      - push command — sys backup --push writes to git and object store
-    - History retention
-      - squash cadence — 90-day git squash keeps repo small under ~35k commits/year
-      - git squash — git_max_age_days threshold: see artifacts/governance.yaml#backup
-      - archive — full immutable history retained in object storage
+  - Storage & Backup
+    - Declarative source tracking — git repository holds read-only human declarations (schema.yaml, policy.yaml); kernel runtime never auto-commits or manages git index locks
+    - Snapshot persistence — transactionally clean VACUUM INTO snapshots and JSONL audit mirrors stream directly to append-only S3/R2 object storage
+    - Retention — immutable point-in-time snapshots and audit logs retain on object storage with WORM locking; local disk retains rolling 30-day cache
diff --git a/cans/space.md b/cans/space.md
index 3333333..4444444 100644
--- a/cans/space.md
+++ b/cans/space.md
@@ -25,2 +25,2 @@
-      - worktree boundary — envs/<name>/ is an isolated git worktree branch containing declarative files
-      - substrate isolation — envs/<name>/workspace.db is gitignored uncommitted local runtime state
+      - namespace boundary — envs/<name>/ is an isolated directory namespace containing declarative overrides and state
+      - substrate isolation — envs/<name>/workspace.db and envs/<name>/audit.db are uncommitted, locally managed SQLite instances
@@ -62,3 +62,3 @@
-      - merge scope — code, YAML, and migrations only; binary database state (workspace.db) is strictly partition-local and never merged across environments
-      - merge pipeline — env merge executes git branch merge for code/schema, snapshots target DB, then applies forward DDL diff
+      - merge scope — declarative schemas, routines, and migration scripts only; binary database files remain strictly partition-local
+      - merge pipeline — env merge verifies schema forward-compatibility in sim, snapshots target DB, and applies forward migration plan
diff --git a/cans/trust.md b/cans/trust.md
index 5555555..6666666 100644
--- a/cans/trust.md
+++ b/cans/trust.md
@@ -47,2 +47,2 @@
-      - cross-agent floor — cross-agent calls require callee trust >= reviewed; drafts cannot be dependencies
-      - training wheels graduation — unapproved calls graduate to normal governance automatically on call 4
+      - cross-agent floor — cross-agent calls require callee trust >= reviewed; drafts cannot be dependencies
+      - contract proof promotion — external verbs promote only via validated JSON Schema contract proofs and shadow canary runs; arbitrary call-count graduation is banned
@@ -87,4 +87,4 @@
-      - training wheels
-        - target verbs — skip and prod-only verbs
-        - synthetic contract proof — contract replay replaces human sign-off: see artifacts/governance.yaml#api.prod_first_calls
-        - tracking — remaining calls decremented in _api_catalog
+      - contract verification
+        - target verbs — all external HTTP egress capabilities
+        - live contract proof — responses validated against upstream OpenAPI JSON Schemas; safe idempotent routes verified via read-only shadow canarying
+        - promotion floor — unvalidated verbs remain locked to draft
diff --git a/cans/action.md b/cans/action.md
index 7777777..8888888 100644
--- a/cans/action.md
+++ b/cans/action.md
@@ -107,5 +107,3 @@
       - Jail defenses
-        - runner engine — tokio::process::Command dispatching bwrap (Tier 1) or broker (Tier 2)
-        - IPC transport — streaming JSON-Lines over platform socket:
-          - Linux / macOS — $XDG_RUNTIME_DIR/capcli/kernel.sock or /run/capcli/kernel.sock
-          - Termux — $PREFIX/var/run/capcli/kernel.sock
-          - Windows — \\.\pipe\capcli-kernel
+        - execution engine — sandboxed runner embedding native C/Rust FFI bindings (capcli_native) for local DB/Authorizer calls via shared memory ring buffer
+        - daemon transport — Unix domain socket / Named Pipe reserved strictly for asynchronous out-of-band events (cron dispatch, webhook intake, outbox draining)
@@ -176,3 +174,3 @@
-      - Cassette recording — capcli api record <verb> captures wire traffic to apis/<provider>.cassette.jsonl for simulation replay; manual mock authoring banned
+      - Live contract capture — capcli api record <verb> generates strict JSON Schema assertions from live responses; offline static cassette replays are banned from promotion gating
@@ -194,5 +192,2 @@
-    - Activation gate
-      - Training wheels
-        - target verbs — un-simulated third-party verbs: see trust.md#Simulation-gaps
-        - autonomous graduation — rehearsal promotion rules: see trust.md#Gates-&-promotion
-        - window expiration — 24-hour approval window per unapproved call
-        - graduation — fourth call enters normal governance
+    - Activation gate
+      - Schema contract gate — external verbs require strict OpenAPI response schema matching; unvalidated routes cannot elevate past draft
diff --git a/cans/assembly.md b/cans/assembly.md
index 9999999..aaaaaaa 100644
--- a/cans/assembly.md
+++ b/cans/assembly.md
@@ -104,3 +104,3 @@
     - Python SDK modules (packages/py/capcli/)
-      - ipc_client.py — streaming JSON-RPC over /run/capcli/kernel.sock: see action.md#Sandbox-execution
+      - native_bridge.py — in-process FFI bridge (`capcli_native.so`) using shared memory for zero-copy DB and Authorizer calls; socket client used exclusively for background daemon RPC
diff --git a/cans/artifacts/governance.yaml b/cans/artifacts/governance.yaml
index bbbbbbb..ccccccc 100644
--- a/cans/artifacts/governance.yaml
+++ b/cans/artifacts/governance.yaml
@@ -95,8 +95,3 @@ env:
 backup:
-  interval_minutes: 15
-  max_drift_minutes: 30               # doctor alarms if commits fall behind
-  push: true
+  provider: object_storage            # s3 | r2
+  snapshot_interval_minutes: 60
   include_audit: true
-  trigger_on: [save, apply, promote, migrate, merge, import, register, restore, serve.add, bind, vault]
-  git_max_age_days: 90
diff --git a/cans/artifacts/test-plan/test-plan-structure.md b/cans/artifacts/test-plan/test-plan-structure.md
index ddddddd..eeeeeee 100644
--- a/cans/artifacts/test-plan/test-plan-structure.md
+++ b/cans/artifacts/test-plan/test-plan-structure.md
@@ -242,2 +242,2 @@ cans/artifacts/test-plan/
-| `tl_06_training_wheels_call_graduation.yaml` | Integration | Unsimulated API verb executes calls 1, 2, and 3 under synthetic contract proof; on call 4, graduates to standard governance. | TP | Graduating verb on call 3 or failing to enforce synthetic contract proof on calls 1–3. |
+| `tl_06_contract_schema_promotion.yaml` | Integration | External API verb undergoes live response JSON Schema validation and shadow canary run; promotes only on 100% schema match. | TP | Elevating verb based on arbitrary invocation counts rather than schema contract proof. |
@@ -258,2 +258,2 @@ cans/artifacts/test-plan/
-| `se_12_git_worktree_isolation_boundary.yaml` | Integration | Migrations executed in `envs/dev/` worktree; test confirms `envs/prod/` SQLite database file remains untouched. | TP | Running migrations on primary branch workspace database directly. |
+| `se_12_namespace_isolation_boundary.yaml` | Integration | Migrations executed in `envs/dev/` namespace; test confirms `envs/prod/` SQLite database file remains untouched. | TP | Running migrations across environment boundaries directly. |
```

```diff
diff --git a/cans/physics.md b/cans/physics.md
index 1111111..2222222 100644
--- a/cans/physics.md
+++ b/cans/physics.md
@@ -48,3 +48,3 @@ cans/physics.md
-      - clock drift — host clock delta vs NTP > 500ms aborts boot to prevent claim corruption
+      - clock drift — host clock delta vs NTP > 500ms emits diagnostic warning; internal causal DAG and lease claims bind to CLOCK_MONOTONIC and SQLite sequence IDs
@@ -53,3 +53,3 @@ cans/physics.md
-      - migration lock SLA breach — schema rebuild holding SQLite write lock > 500ms aborts execution (exit 2)
+      - migration execution — structural changes use trigger-replicated shadow tables with asynchronous backfills; exclusive cutover lock is atomic and held for <20ms
diff --git a/cans/world.md b/cans/world.md
index 3333333..4444444 100644
--- a/cans/world.md
+++ b/cans/world.md
@@ -107,6 +107,6 @@ cans/world.md
-      - 3. Contract phase — destructive DDL executed by kernel migrate.rs via 12-step shadow table rebuild; drops old columns, applies NOT NULL and FKs
-    - Rebuild mechanics
-      - kernel responsibility — Rust kernel generates shadow table creation, row copy, index rebuild, and atomic swap; agent DDL authoring banned
-      - lock duration SLA — table exclusive write lock capped at 500ms; breaches abort immediately with exit 2
+      - 3. Contract phase — destructive DDL executed by kernel migrate.rs via trigger-replicated online shadow table; background backfill runs in chunks (max 500 rows/txn)
+    - Online migration mechanics
+      - kernel responsibility — Rust kernel creates shadow table, attaches delta replication triggers, copies base data in chunks, and performs atomic swap (<20ms lock)
+      - lock duration — exclusive write lock held only during final trigger detach and table rename
@@ -165,3 +165,3 @@ cans/world.md
-      - lock SLA gate — fails closed (exit 2) if shadow table swap lock duration exceeds 500ms
+      - online cutover gate — verifies shadow table delta lag reaches zero before executing atomic <20ms table swap
diff --git a/cans/space.md b/cans/space.md
index 5555555..6666666 100644
--- a/cans/space.md
+++ b/cans/space.md
@@ -28,2 +28,2 @@ cans/space.md
-      - prod protection — removal flags: see artifacts/governance.yaml#env
+      - prod protection — destructive operations require out-of-band cryptographic challenge signatures (WebAuthn/Passkey or GPG/SSH key)
@@ -52,2 +52,2 @@ cans/space.md
-      - deprovisioning — prod removal requires --confirm-backup and --confirm-prod
+      - deprovisioning — prod removal requires signed cryptographic challenge token; CLI flag bypasses are rejected
@@ -59,2 +59,2 @@ cans/space.md
-      - prod removal flags — --confirm-backup and --confirm-prod mandatory
+      - prod destructive auth — operations halting prod require out-of-band cryptographic signature via Cockpit challenge or local key
diff --git a/cans/recovery.md b/cans/recovery.md
index 7777777..8888888 100644
--- a/cans/recovery.md
+++ b/cans/recovery.md
@@ -49,2 +49,2 @@ cans/recovery.md
-      - confirmation flags — dual flags mandatory for prod teardown: see space.md#Safety-controls
+      - cryptographic authorization — teardown requires out-of-band challenge signature verification; terminal flag overrides are prohibited
diff --git a/cans/artifacts/governance.yaml b/cans/artifacts/governance.yaml
index 9999999..aaaaaaa 100644
--- a/cans/artifacts/governance.yaml
+++ b/cans/artifacts/governance.yaml
@@ -93,3 +93,3 @@ env:
   max_environments: 5                 # isolated directory namespaces under envs/
-  prod_removal_flags: 2               # number of confirm flags to remove prod (!)
+  prod_destructive_auth: challenge_signature  # requires out-of-band WebAuthn/SSH signed challenge
   require_backup_push: true           # no world exists unbacked
diff --git a/cans/artifacts/test-plan/test-plan-structure.md b/cans/artifacts/test-plan/test-plan-structure.md
index bbbbbbb..ccccccc 100644
--- a/cans/artifacts/test-plan/test-plan-structure.md
+++ b/cans/artifacts/test-plan/test-plan-structure.md
@@ -197,3 +197,3 @@ cans/artifacts/test-plan/
-| `kp_05_ntp_clock_drift_halt.yaml` | Integration | Host clock skew vs NTP exceeds 500ms; kernel halts at boot with `exit 3` to prevent lease and claim corruption. | TN | Using real system clock and sleeping, causing non-deterministic flakes. |
+| `kp_05_ntp_clock_drift_warning.yaml` | Integration | Host clock skew vs NTP exceeds 500ms; kernel emits diagnostic warning and switches internal sequencing to CLOCK_MONOTONIC without halting execution. | TP | Aborting boot on transient NTP skew instead of falling back to monotonic causal ordering. |
@@ -252,3 +252,3 @@ cans/artifacts/test-plan/
-| `se_06_env_merge_prod_dual_flag_gate.yaml` | E2E | Merging `dev` schema into `prod` without `--confirm-backup` and `--confirm-prod` is rejected with `exit 2`. | TN | Permitting production merge with single confirmation flag. |
+| `se_06_env_merge_prod_crypto_challenge.yaml` | E2E | Destructive schema merge into `prod` without valid out-of-band cryptographic challenge signature is rejected with `exit 2`. | TN | Permitting production mutations via terminal CLI bypass flags instead of cryptographic proof. |
```

No, you caught more leaks. The previous diffs left references to Git worktrees, 500ms rebuild locks, VCR cassettes, NTP boot halts, and dual confirmation flags in `README.md`, `assembly.md`, `overview.md`, `interface.md`, `time.md`, `_states.json`, and `wireframe-structure.md`.

Here are the exact diff patches to purge them cleanly:

```diff
diff --git a/README.md b/README.md
index 1111111..2222222 100644
--- a/README.md
+++ b/README.md
@@ -70,3 +70,3 @@ Machines communicate via exit codes, not polite English apologies. Capcli never
-* **`exit 3`** $\rightarrow$ **Refusal / Drift.** Unparseable syntax, missing intent (`-m`), lockfile mismatch, or NTP clock drift >500ms. **State untouched.**
+* **`exit 3`** $\rightarrow$ **Refusal / Drift.** Unparseable syntax, missing intent (`-m`), lockfile mismatch, or missing host dependencies. **State untouched.**
diff --git a/cans/overview.md b/cans/overview.md
index 3333333..4444444 100644
--- a/cans/overview.md
+++ b/cans/overview.md
@@ -22,3 +22,3 @@
-      - dual store recovery — hot state in workspace.db; full snapshot backups synced to git and object store
+      - dual store recovery — hot state in workspace.db; point-in-time binary snapshots synced directly to object store
diff --git a/cans/time.md b/cans/time.md
index 5555555..6666666 100644
--- a/cans/time.md
+++ b/cans/time.md
@@ -110,3 +110,3 @@
-      - backup commits — interval: see artifacts/governance.yaml#backup
+      - backup snapshots — interval: see artifacts/governance.yaml#backup
diff --git a/cans/interface.md b/cans/interface.md
index 7777777..8888888 100644
--- a/cans/interface.md
+++ b/cans/interface.md
@@ -53,3 +53,3 @@
-      - Record — api record <provider.verb> [-p k=v] — captures live test call into replay cassette
+      - Record — api record <provider.verb> [-p k=v] — captures live response and compiles JSON Schema contract
@@ -81,3 +81,3 @@
-      - Backups — sys backup [--push], recover <commit>
+      - Backups — sys backup [--push], recover <snapshot-id>
diff --git a/cans/assembly.md b/cans/assembly.md
index 9999999..aaaaaaa 100644
--- a/cans/assembly.md
+++ b/cans/assembly.md
@@ -11,3 +11,3 @@
-      - git binary — host git >= 2.30 for worktrees: see space.md#Environment-axis
+      - git binary — host git >= 2.30 for read-only declarative repo tracking
@@ -54,3 +54,3 @@
-      - envs/ — isolated git worktrees and partition roots: see space.md#Environment-axis
+      - envs/ — isolated directory namespaces and partition roots: see space.md#Environment-axis
@@ -110,3 +110,3 @@
-        - migrate.rs — 12-step table rebuild engine and 500ms lock watchdog: see world.md#Schema-evolution
+        - migrate.rs — trigger-replicated online shadow table engine with atomic <20ms cutover: see world.md#Schema-evolution
@@ -131,3 +131,3 @@
-        - cassette.rs — VCR HTTP cassette recorder and deterministic replay engine for sim mode
+        - contract_validator.rs — live response JSON Schema validator and shadow canary engine for external APIs
@@ -173,3 +173,3 @@
-        - worktree.rs — provisions and merges git worktrees: see space.md#Environment-axis
+        - namespace.rs — provisions and manages environment directory partitions: see space.md#Environment-axis
@@ -176,3 +176,3 @@
-        - prod_protect_gate.rs — demands dual confirmation flags: see space.md#World-governance
+        - prod_protect_gate.rs — verifies out-of-band cryptographic challenge signatures: see space.md#World-governance
diff --git a/cans/artifacts/wireframe/_states.json b/cans/artifacts/wireframe/_states.json
index bbbbbbb..ccccccc 100644
--- a/cans/artifacts/wireframe/_states.json
+++ b/cans/artifacts/wireframe/_states.json
@@ -39,3 +39,2 @@
       "lockfile_mismatch",
-      "schema_hash_mismatch",
-      "host.ntp",
+      "schema_hash_mismatch",
       "policy.secrets"
diff --git a/cans/artifacts/wireframe/wireframe-structure.md b/cans/artifacts/wireframe/wireframe-structure.md
index ddddddd..eeeeeee 100644
--- a/cans/artifacts/wireframe/wireframe-structure.md
+++ b/cans/artifacts/wireframe/wireframe-structure.md
@@ -183,2 +183,2 @@
-| `api.activate.success.training_wheels`| success| 0 | — | probation | Activated with 3 synthetic contract checks |
+| `api.activate.success.contract_tested`| success| 0 | — | verified | Activated with verified OpenAPI JSON Schema |
@@ -188,2 +188,2 @@
-| `api.ship.success.graduated` | success | 0 | — | graduated | Reaches Call 4; enters standard governance |
+| `api.ship.success.graduated` | success | 0 | — | graduated | 100% schema match & shadow canary passed |
@@ -210,2 +210,2 @@
-| `env.remove.denial.prod_flags` | denial | 2 | policy.authorizer | confirmation | Prod requires dual confirm flags |
+| `env.remove.denial.crypto_sig` | denial | 2 | policy.authorizer | confirmation | Prod requires out-of-band challenge signature |
@@ -227,2 +227,2 @@
-| `sys.doctor.refusal.clock_drift`| refusal| 3 | host.ntp | clock_skew | Host clock delta $>500$ms vs NTP |
+| `sys.doctor.warning.clock_drift`| success| 0 | host.ntp | clock_skew | Host clock delta $>500$ms vs NTP (monotonic fallback active) |
@@ -279,7 +279,6 @@
-### 5.11 NTP Clock Drift Boot Refusal (`screens/sys/doctor/sys.doctor.refusal.clock_drift.txt`)
+### 5.11 NTP Clock Drift Diagnostic Warning (`screens/sys/doctor/sys.doctor.warning.clock_drift.txt`)
 
 ```text
-[dev:tier_1]  ✗  exit 3
+[dev:tier_1]  [WARN] host.ntp.clock_drift
 
-  FATAL  kernel.boot.clock_drift_exceeded
-         Host clock delta vs NTP is 840ms (maximum allowable: 500ms).
-         Execution refused to prevent lease corruption and quota bypass.
+  WARN   Host clock delta vs NTP is 840ms.
+         Monotonic clock (CLOCK_MONOTONIC) and SQLite transaction sequencing active.
 
-  state_modified: false
-  layer: boot
-  remedy: synchronize host system clock via 'chronyd' or 'ntpdate'
+  state_modified: false
+  remedy: run 'chronyd' or 'ntpdate' to re-align wall clock
 ```
```

```diff
diff --git a/cans/artifacts/system-schema.yaml b/cans/artifacts/system-schema.yaml
index 1111111..2222222 100644
--- a/cans/artifacts/system-schema.yaml
+++ b/cans/artifacts/system-schema.yaml
@@ -107,3 +107,4 @@ tables:
       options: json!                   # allowed choice strings array
+      state_fences: json!              # OCC version hashes of read dependencies captured at suspension
       timeout_at: int!                 # unix epoch seconds
diff --git a/cans/action.md b/cans/action.md
index 3333333..4444444 100644
--- a/cans/action.md
+++ b/cans/action.md
@@ -141,3 +141,3 @@
         - wire projection — select JSONPath filters large upstream responses at kernel socket edge before passing payload to guest sandbox
-        - dual-write safety — mutating API calls executed within DB workflows require kernel idempotency keys or compensating rollback actions
-        - outbox draining — daemon drains _outbox_events asynchronously; headless subshell CLI executions drain pending outbox calls synchronously prior to exit 0
+        - dual-write safety — mutating API calls staged to _outbox_events must map an explicit upstream idempotency header in apis/<provider>.yaml; routes lacking idempotency support require synchronous execution with declared compensating rollbacks
+        - outbox draining — daemon drains _outbox_events asynchronously; headless subshell CLI executions drain pending outbox calls synchronously prior to exit 0
@@ -149,3 +149,3 @@
         - transport bridge — local IPC permitted exclusively to kernel endpoint
-        - suspension contract — ctx.ping.ask serializes step checkpoint to _pending_asks and exits with code 6; resume re-invokes entrypoint with saved state
+        - suspension contract — ctx.ping.ask snapshots step checkpoint and OCC state_fences to _pending_asks and exits with code 6; resume verifies dependency entity hashes and aborts with exit 2 if data drifted during human review
         - interface definition — Param typing enforces input validation
diff --git a/cans/artifacts/policy.yaml b/cans/artifacts/policy.yaml
index 5555555..6666666 100644
--- a/cans/artifacts/policy.yaml
+++ b/cans/artifacts/policy.yaml
@@ -73,3 +73,3 @@ api:
   external_writes:
     require_intent: true
     require_trust: reviewed
-    idempotency_key: kernel_minted
+    idempotency_key: kernel_minted
+    require_upstream_idempotency_header: true  # outbox staging denied if upstream lacks idempotency header mapping
@@ -79,3 +79,3 @@ api:
   rate_limit:                                    # live quota from provider responses
-    model: proactive_token_bucket                # client-side bucket is PRIMARY authority
+    model: optimistic_token_bucket               # client-side bucket is an optimistic cache slaved to upstream headers
     default_capacity: 60                         # burst ceiling
@@ -87,2 +87,3 @@ api:
     header_calibration:                          # reactive headers used ONLY to recalibrate bucket
       reconcile_on_response: true                # sync local bucket down if provider reports lower
+      on_unexpected_429: zero_bucket_and_yield   # remote 429 instantly drains local bucket to 0 and parks frames (exit 6)
diff --git a/cans/budget.md b/cans/budget.md
index 7777777..8888888 100644
--- a/cans/budget.md
+++ b/cans/budget.md
@@ -62,5 +62,5 @@
   - Quotas
-    - Proactive rate limiting
-      - Local bucket — token-bucket throttle regulates client-side egress cadence
+    - Optimistic rate limiting
+      - Local bucket — optimistic token-bucket regulates client-side cadence; slaved dynamically to upstream headers
       - Multi-window tracking — supports dual-rate partitions (burst bucket + rolling window ceilings e.g. 24h / 86400s)
-      - Gate decision — local bucket empty pauses dispatch up to timeout; hard limit exhaustion throws exit 2
-      - Dynamic header calibration — reconciles RFC standard headers or extracts structured JSON payloads (e.g. X-Business-Use-Case-Usage) via JSONPath
-      - Remote 429 handling — automatic exponential backoff with jitter in kernel proxy before reporting error
+      - Gate decision — local bucket empty pauses dispatch up to timeout; hard limit exhaustion throws exit 2
+      - Dynamic header calibration — reconciles RFC headers and structured JSON payloads; unexpected 429 instantly forces local bucket tokens to 0
+      - Remote 429 handling — active frames immediately yield to _suspended_tasks (exit 6) locked until upstream Retry-After epoch
diff --git a/cans/artifacts/test-plan/test-plan-structure.md b/cans/artifacts/test-plan/test-plan-structure.md
index 9999999..aaaaaaa 100644
--- a/cans/artifacts/test-plan/test-plan-structure.md
+++ b/cans/artifacts/test-plan/test-plan-structure.md
@@ -218,3 +218,3 @@ cans/artifacts/test-plan/
-| `we_07_429_backoff_jitter_retry.yaml` | Integration | Remote API returns HTTP 429; kernel executes exponential backoff with full jitter before surfacing error to caller. | TN | Instant tight-loop retries without exponential delay calculation. |
+| `we_07_429_zero_bucket_yield.yaml` | Integration | Remote API returns HTTP 429; kernel zeros out local token bucket, suspends executing frame into `_suspended_tasks` (exit 6), and locks egress until `Retry-After`. | TN | Continuing outbound attempts when external shared quota is exhausted. |
@@ -275,3 +275,3 @@ cans/artifacts/test-plan/
-| `bt_06_ask_fail_closed_timeout.yaml` | Integration | Routine suspended via `ctx.ping.ask`; human supervisor fails to answer within timeout; routine fails closed. | TN | Assuming human approval or defaulting to "yes" upon timeout. |
+| `bt_06_ask_occ_fence_conflict_abort.yaml` | Integration | Routine suspended via `ctx.ping.ask`; underlying order record modified by external agent before human resolution; resume aborts with `exit 2` on OCC version fence conflict. | TN | Resuming routine execution with stale in-memory state after dependency state mutation. |
```

```diff
diff --git a/README.md b/README.md
index 1111111..2222222 100644
--- a/README.md
+++ b/README.md
@@ -41,3 +41,3 @@ Capcli treats **local state mutations and external network egress with equal gat
-* **Proactive Token Buckets:** Client-side rate buckets block or yield tasks *before* packets touch the physical network. Downstream rate-limit headers (even nested JSONPath headers) dynamically sync the gate.
+* **Optimistic Token Buckets:** Client-side rate buckets regulate egress cadence but slave dynamically to remote headers. A single upstream 429 instantly drains the local bucket to zero and yields active tasks (`exit 6`) until the `Retry-After` epoch.
@@ -109,3 +109,3 @@ trust_receipt:
-| **[Understand Physics](docs/understand/index.md)** | The Causal DAG, proactive token brokerage, and the 3-rung trust ladder. |
+| **[Understand Physics](docs/understand/index.md)** | The Causal DAG, optimistic token brokerage, and the 3-rung trust ladder. |
diff --git a/cans/overview.md b/cans/overview.md
index 3333333..4444444 100644
--- a/cans/overview.md
+++ b/cans/overview.md
@@ -81,3 +81,3 @@
-      - egress engine — token-bucket quotas, secret boundaries, and sim routing intercept network calls
+      - egress engine — optimistic token-bucket quotas slaved to remote headers, secret boundaries, and sim routing intercept network calls
diff --git a/cans/assembly.md b/cans/assembly.md
index 5555555..6666666 100644
--- a/cans/assembly.md
+++ b/cans/assembly.md
@@ -134,3 +134,3 @@
-        - outbox.rs — stages mutating API calls alongside DB transactions to guarantee dual-write consistency
+        - outbox.rs — stages mutating API calls alongside DB transactions; verifies upstream idempotency header mapping and rejects unmapped routes with exit 3
@@ -155,3 +155,4 @@
       - Execution gates
         - option_gate.rs — limits question choices to max 5: see artifacts/governance.yaml#notify
         - length_gate.rs — enforces question token caps: see artifacts/governance.yaml#notify
         - fail_closed_gate.rs — fails suspended routine on timeout: see artifacts/policy.yaml#notify
+        - occ_fence_gate.rs — verifies dependency state_fences on resume; denies stale resumptions with exit 2
diff --git a/cans/interface.md b/cans/interface.md
index 7777777..8888888 100644
--- a/cans/interface.md
+++ b/cans/interface.md
@@ -64,3 +64,3 @@
       - Listing — ping list [--pending]
-      - Resolution — ping resolve <ask-id> --choice <opt>
+      - Resolution — ping resolve <ask-id> --choice <opt> — verifies OCC state_fences before re-dispatching frame
       - Expiry — ping expire <ask-id>
diff --git a/cans/artifacts/wireframe/wireframe-structure.md b/cans/artifacts/wireframe/wireframe-structure.md
index 9999999..aaaaaaa 100644
--- a/cans/artifacts/wireframe/wireframe-structure.md
+++ b/cans/artifacts/wireframe/wireframe-structure.md
@@ -201,2 +201,3 @@ cans/artifacts/wireframe/
 | `ping.resolve.success.resolved` | success | 0 | — | resolved | Choice selected; resumes task |
+| `ping.resolve.denial.occ_conflict`| denial | 2 | db.engine | stale_state | Touched rows modified during suspension; OCC fence violated |
 | `ping.resolve.refusal.not_found` | refusal | 3 | validation | not_found | Invalid ask ID |
```

```diff
diff --git a/cans/physics.md b/cans/physics.md
index 1111111..2222222 100644
--- a/cans/physics.md
+++ b/cans/physics.md
@@ -9,3 +9,3 @@ cans/physics.md
       - tier 1 (hardened) — Linux bare-metal, VPS, Docker (with userns), WSL2
-        - sandbox — unprivileged bwrap namespaces + tmpfs scratch: see action.md#Sandbox-execution
+        - sandbox — unprivileged bwrap namespaces; automatically falls back to rootless OCI (crun/podman) or gVisor if host kernel restricts user namespaces
         - network jail — seccomp-bpf filter trapping raw socket connect (syscall 42) across all engines
@@ -46,3 +46,3 @@ cans/physics.md
-      - sandbox missing on tier 1 — absent or unexecutable bwrap on Linux aborts boot (exit 3)
+      - sandbox missing on tier 1 — absent bwrap automatically falls back to container or microvm runner; aborts boot with exit 3 only if all isolation providers fail
@@ -98,4 +98,3 @@ cans/physics.md
   - Search ceiling
-    - Execution split — kernel filters deterministically; harness ranks semantically
-    - Stage cascade — exact, prefix, FTS5 full-text, and Levenshtein distance: see action.md#Search-surface
-    - Saturation boundary — registry ceilings enforce hard stop: see artifacts/governance.yaml#registry
+    - Hybrid search engine — kernel embeds a local quantized vector model (ONNX tract runtime) combined with SQLite FTS5 for zero-roundtrip semantic discovery
+    - Semantic indexing — queries match synonymous capabilities locally without external LLM ranking calls or keyword saturation walls
diff --git a/cans/action.md b/cans/action.md
index 3333333..4444444 100644
--- a/cans/action.md
+++ b/cans/action.md
@@ -41,7 +41,4 @@
     - Search surface
-      - Determinism split
-        - kernel search — exact, prefix, FTS5 full-text, and strsim Levenshtein distance; zero in-binary neural models
-        - harness search — external semantic ranking and embeddings managed entirely in caller userland
-      - Scale behavior
-        - cap trigger — keyword search degrades past 300-routine hard ceiling. see artifacts/governance.yaml#registry
+      - Hybrid discovery engine
+        - kernel search — exact, prefix, FTS5 BM25, and embedded local ONNX vector similarity; zero external API dependency
+        - semantic resilience — synonym queries match capability intent across 1,000+ registered routines without degradation
@@ -89,3 +86,3 @@
       - Jail architecture
-        - provider resolution — auto selects bwrap on Tier 1; microvm or wasm on Tier 2 (bare-metal broker mode banned): see physics.md#Platform-tier-taxonomy
+        - provider resolution — Tier 1 probes bwrap and userns; falls back to rootless crun/podman or gVisor if userns is disabled; Tier 2 requires microvm or wasm
@@ -124,3 +121,4 @@
     - Composition and cascade
-      - Context inheritance — child frames consume parent pools
+      - Static call-tree preflight — root invocation verifies that worst-case call-graph branch depth can be fully funded before execution begins
+      - Context inheritance — child frames consume parent pools; starvation aborts before root dispatch rather than decapitating child frames mid-flight
diff --git a/cans/budget.md b/cans/budget.md
index 5555555..6666666 100644
--- a/cans/budget.md
+++ b/cans/budget.md
@@ -37,3 +37,4 @@
     - min() law
-      - Child effective limit = min(declared need, governance ceiling, parent_remaining, session_ceiling)
+      - Static call-graph evaluation — kernel inspects declared child dependency trees prior to root frame execution
+      - Pre-flight rejection — if parent_remaining or session headroom cannot satisfy the worst-case leaf path, can_invoke_now returns false before invocation
+      - Child effective limit = min(declared need, governance ceiling, parent_remaining, session_ceiling)
diff --git a/cans/artifacts/governance.yaml b/cans/artifacts/governance.yaml
index 7777777..8888888 100644
--- a/cans/artifacts/governance.yaml
+++ b/cans/artifacts/governance.yaml
@@ -12,4 +12,5 @@ lockfile: capcli.lock                 # deterministic compiler target
 registry:
-  max_routines: 300                   # hard cap — register refuses past it
-  soft_cap: 200                       # sys doctor nags; consolidation urged
+  max_routines: 1000                  # local hybrid ONNX vector index scales registry capacity
+  soft_cap: 800                       # sys doctor nags; consolidation urged
+  embedded_semantic_index: true       # in-binary ONNX vector similarity enabled
   max_per_agent_draft: 30             # anti-flood per agent identity
diff --git a/cans/artifacts/test-plan/test-plan-structure.md b/cans/artifacts/test-plan/test-plan-structure.md
index 9999999..aaaaaaa 100644
--- a/cans/artifacts/test-plan/test-plan-structure.md
+++ b/cans/artifacts/test-plan/test-plan-structure.md
@@ -200,3 +200,3 @@ cans/artifacts/test-plan/
-| `kp_08_missing_bwrap_tier1_abort.yaml` | Integration | Linux Tier 1 host missing `bwrap` binary aborts boot with `exit 3` instead of degrading silently. | TN | Falling back to unconfined execution on Tier 1 systems without raising hard error. |
+| `kp_08_missing_bwrap_tier1_fallback.yaml` | Integration | Linux host missing `bwrap` binary or unprivileged userns automatically fails over to rootless container provider (`crun`/`podman`) and passes validation. | TP | Failing boot when alternative hardened container backends are installed. |
@@ -205,3 +205,3 @@ cans/artifacts/test-plan/
-| `kp_13_unprivileged_userns_docker_check.yaml` | Integration | Host running inside Docker without unprivileged user namespaces (`userns`) triggers boot diagnostics and clean refusal. | TN | Silently bypassing namespace isolation checks when run inside container. |
+| `kp_13_unprivileged_userns_docker_check.yaml` | Integration | Host running inside Docker without unprivileged user namespaces automatically falls over to gVisor or microVM isolation without security degradation. | TP | Refusing boot inside containers instead of routing to supported containerized isolation providers. |
```


```diff
diff --git a/cans/assembly.md b/cans/assembly.md
index 1111111..2222222 100644
--- a/cans/assembly.md
+++ b/cans/assembly.md
@@ -14,3 +14,3 @@ cans/assembly.md
-      - bubblewrap binary — host bwrap >= 0.8.0 mandatory on Tier 1; optional on Tier 2: see physics.md#Platform-tier-taxonomy
+      - sandbox backends — bwrap >= 0.8.0, crun >= 1.5, or podman rootless on Tier 1; microvm/wasm on Tier 2: see physics.md#Platform-tier-taxonomy
@@ -74,3 +74,3 @@ cans/assembly.md
-      - configuration — Cargo.toml linking rusqlite bundled, petgraph, sha2, aes-gcm
+      - configuration — Cargo.toml linking rusqlite bundled, petgraph, sha2, aes-gcm, tract-onnx
@@ -115,3 +115,3 @@ cans/assembly.md
-        - jail.rs — bwrap wrapper mounting host engines and applying runtime seccomp profile
+        - jail.rs — multi-backend sandbox manager (bwrap, crun, gVisor) applying runtime seccomp profiles
@@ -189,3 +189,4 @@ cans/assembly.md
-        - search.rs — cascades exact, prefix, FTS5, and fuzzy: see action.md#Search-surface
-        - preflight.rs — evaluates can_invoke_now verdict: see budget.md#Pre-flight
+        - search.rs — hybrid discovery engine cascading exact, prefix, FTS5 BM25, and local ONNX vector similarity
+        - preflight.rs — evaluates static call-tree cost graph to return recursive can_invoke_now verdict: see budget.md#Pre-flight
diff --git a/cans/overview.md b/cans/overview.md
index 3333333..4444444 100644
--- a/cans/overview.md
+++ b/cans/overview.md
@@ -82,2 +82,2 @@ cans/overview.md
-      - no kernel LLM — zero AI inference or natural language parsing in core
+      - zero generative LLMs — zero LLM generation or probabilistic parsing in kernel; deterministic quantized ONNX embeddings permitted strictly for vector search
diff --git a/cans/artifacts/wireframe/wireframe-structure.md b/cans/artifacts/wireframe/wireframe-structure.md
index 5555555..6666666 100644
--- a/cans/artifacts/wireframe/wireframe-structure.md
+++ b/cans/artifacts/wireframe/wireframe-structure.md
@@ -146,3 +146,3 @@ cans/artifacts/wireframe/
-| `run.execute.denial.budget_cascade` | denial | 2 | policy.budget | starved | Child frame clipped by parent/session $\min()$ |
+| `run.execute.denial.budget_cascade` | denial | 2 | policy.budget | starved | Pre-flight call-tree analysis detects starved child branch; invocation blocked |
@@ -226,3 +226,3 @@ cans/artifacts/wireframe/
-| `sys.doctor.refusal.boot` | refusal | 3 | compile | missing_dep | Host missing python3.11 or bwrap |
+| `sys.doctor.refusal.boot` | refusal | 3 | compile | missing_dep | Host missing python3.11 or supported sandbox provider (bwrap/crun/microvm) |
diff --git a/cans/artifacts/test-plan/test-plan-structure.md b/cans/artifacts/test-plan/test-plan-structure.md
index 7777777..8888888 100644
--- a/cans/artifacts/test-plan/test-plan-structure.md
+++ b/cans/artifacts/test-plan/test-plan-structure.md
@@ -223,3 +223,3 @@ cans/artifacts/test-plan/
-| `bc_01_downward_min_inheritance.yaml` | Unit | Parent frame (ops=20) calls child routine (declared ops=50); child effective limit is clamped to $\min(50, 20) = 20$. | TP | Child routine executing 21 ops because it declared 50. |
+| `bc_01_downward_min_inheritance.yaml` | Unit | Parent frame (ops=20) inspects child routine (declared ops=50); pre-flight static analysis detects child starvation and returns `can_invoke_now: false`. | TP | Permitting invocation when declared child branch exceeds available parent headroom. |
```

```diff
diff --git a/README.md b/README.md
index 1111111..2222222 100644
--- a/README.md
+++ b/README.md
@@ -103,4 +103,4 @@ trust_receipt:
   pinned_routines:   32
   active_triggers:   4 crons, 3 webhooks, 1 endpoint
-  sleep_score:       100% (laptop closed, zero terminal panics)
+  deployment:        headless_daemon (systemd on hardened Linux)
@@ -137,3 +137,3 @@ cd capcli && cargo build --release --target x86_64-unknown-linux-musl
 [MIT](LICENSE) © 2026 capcli contributors.  
-**Build an enterprise that runs while you sleep.**
+**Deterministic execution infrastructure for autonomous agents.**
diff --git a/cans/physics.md b/cans/physics.md
index 3333333..4444444 100644
--- a/cans/physics.md
+++ b/cans/physics.md
@@ -15,2 +15,5 @@ cans/physics.md
     - trust bounds — draft and reviewed in dev/sim only; pinned execution denied: see trust.md#Ladder-laws
+  - Deployment topology
+    - dedicated server — headless Linux host running capcli-daemon under systemd; required for 24/7 background crons, webhooks, and S3 WORM attestations
+    - local workstation — ephemeral developer environment; prohibited from serving production endpoints or hosting unattended pinned schedules
@@ -51,3 +54,3 @@ cans/physics.md
-      - lockfile mismatch — compiled capcli.lock SHA256 mismatch aborts boot in prod and sim
+      - lockfile mismatch in prod — compiled capcli.lock SHA256 mismatch aborts boot with exit 3 in prod; dev and sim auto-recompile if syntax and semantics pass
diff --git a/cans/world.md b/cans/world.md
index 5555555..6666666 100644
--- a/cans/world.md
+++ b/cans/world.md
@@ -150,5 +150,4 @@ cans/world.md
     - Gate 3: Manifest lock
-      - timing — boot-time startup check in prod and sim environments
-      - validation — compile sha256 of schema, system-schema, policy, and governance
-      - verification — computed hash must match active capcli.lock entry exactly
-      - failure code — throws exit 3 (refuse boot in prod/sim; marks dev as uncompiled draft)
+      - timing — boot-time check on engine initialization
+      - prod enforcement — hash mismatch against capcli.lock aborts boot immediately with exit 3
+      - dev/sim reconciliation — if Gate 1 and Gate 2 pass, engine auto-recompiles capcli.lock and logs [WARN] lockfile.auto_recompiled
diff --git a/cans/artifacts/policy.yaml b/cans/artifacts/policy.yaml
index 7777777..8888888 100644
--- a/cans/artifacts/policy.yaml
+++ b/cans/artifacts/policy.yaml
@@ -124,3 +124,4 @@ fail_closed:
   no_policy: refuse_boot
-  lockfile_mismatch: refuse_boot           # abort if hash(schema+system+policy+gov) != capcli.lock
+  lockfile_mismatch_prod: refuse_boot      # prod aborts if hash(schema+system+policy+gov) != capcli.lock
+  lockfile_mismatch_non_prod: auto_recompile # dev and sim auto-update lockfile when syntax passes
   system_schema_hash_mismatch: refuse_boot # kernel integrity check
diff --git a/cans/artifacts/wireframe/wireframe-structure.md b/cans/artifacts/wireframe/wireframe-structure.md
index 9999999..aaaaaaa 100644
--- a/cans/artifacts/wireframe/wireframe-structure.md
+++ b/cans/artifacts/wireframe/wireframe-structure.md
@@ -254,4 +254,4 @@ trust_receipt:
   pinned_routines:   32
   active_triggers:   4 crons, 3 webhooks, 1 endpoint
-  sleep_score:       100%
+  deployment:        headless_daemon (systemd Linux)
diff --git a/cans/artifacts/test-plan/test-plan-structure.md b/cans/artifacts/test-plan/test-plan-structure.md
index bbbbbbb..ccccccc 100644
--- a/cans/artifacts/test-plan/test-plan-structure.md
+++ b/cans/artifacts/test-plan/test-plan-structure.md
@@ -250,3 +250,3 @@ cans/artifacts/test-plan/
-| `se_03_lockfile_hash_drift_gate3_refusal.yaml` | Integration | `schema.yaml` is edited on disk without updating `capcli.lock`; kernel boot in prod refuses execution with `exit 3`. | TN | Permitting execution in production with uncompiled schema changes. |
+| `se_03_lockfile_hash_drift_prod_gate3_refusal.yaml` | Integration | `schema.yaml` is edited on disk without updating `capcli.lock`; boot in prod refuses execution with `exit 3`, while boot in dev auto-recompiles cleanly. | TN | Aborting development workflows on non-production lockfile drift or permitting uncompiled prod changes. |
```

```diff
diff --git a/README.md b/README.md
index 1111111..2222222 100644
--- a/README.md
+++ b/README.md
@@ -123,4 +123,4 @@ Docker isolates the host OS from a container escape. It does nothing to stop an
 #### Can the LLM modify its own policies?
-No. `schema.yaml`, `policy.yaml`, and `governance.yaml` are compiled into `capcli.lock` (a root SHA-256 hash). Any runtime drift between disk YAML and the lockfile triggers an instant `exit 3` boot refusal. Policy changes require signed Git commits.
+No. `schema.yaml`, `policy.yaml`, and `governance.yaml` compile into `capcli.lock`. In `prod`, runtime drift triggers an instant `exit 3` boot refusal. In `dev` and `sim`, valid YAML changes auto-recompile the lockfile to prevent developer and agent lockouts.
diff --git a/cans/trust.md b/cans/trust.md
index 3333333..4444444 100644
--- a/cans/trust.md
+++ b/cans/trust.md
@@ -24,3 +24,3 @@
         - operational autonomy
-          - headless schedules — may_run_unattended: true (artifacts/policy.yaml)
+          - headless schedules — may_run_unattended: true; strictly mandates dedicated systemd server daemon (local workstations prohibited from unattended prod runs)
           - endpoint serving — minimum floor: see artifacts/governance.yaml#serve
@@ -101,2 +101,3 @@
     - Verified receipt lines
+      - deployment topology — dedicated_daemon (systemd Linux) or local_workstation (ephemeral)
       - host execution tier — tier_1 (hardened) or tier_2 (degraded): see physics.md#Platform-tier-taxonomy
diff --git a/cans/assembly.md b/cans/assembly.md
index 5555555..6666666 100644
--- a/cans/assembly.md
+++ b/cans/assembly.md
@@ -88,3 +88,3 @@
     - Persistent daemon crate
-      - crate identity — crates/capcli-daemon
+      - crate identity — crates/capcli-daemon (targets systemd service on headless Linux servers for 24/7 background automation)
       - configuration — Cargo.toml linking axum, tower, croner, rust-embed, capcli-core, capcli-types
diff --git a/cans/artifacts/test-plan/matrix.yaml b/cans/artifacts/test-plan/matrix.yaml
index 7777777..8888888 100644
--- a/cans/artifacts/test-plan/matrix.yaml
+++ b/cans/artifacts/test-plan/matrix.yaml
@@ -29,3 +29,3 @@ exit_code_law:
   "2": "invariant or governance block; state untouched (state_modified: false) — domains db.engine, policy.authorizer, policy.budget, policy.trust"
-  "3": "compile-time refusal, validation failure, boot lockfile mismatch, or missing parameter"
+  "3": "compile-time refusal, validation failure, prod boot lockfile mismatch, or missing parameter"
   "4": "domain routine.runtime; uncaught Python sandbox exception or type crash; transaction cleanly rolled back"
```


Yes. Exactly **4 critical architectural holes** were still unpatched:

1. **`cans/artifacts/system-schema.yaml` was missing the `_outbox_events` table definition** (Fix 14) — despite referencing it in documentation, the schema had no physical table for outbox queues.
2. **`cans/artifacts/wireframe/flows.json` still hardcoded the Exit 5 Panic journey** (Fix 4) — asserting that a broken SHA-256 link bricks the kernel instead of routing to quarantine.
3. **`cans/artifacts/test-plan/test-plan-structure.md` had `vs_12` testing guest memory secret exfiltration** (Fix 5) — impossible when the guest runtime only holds opaque `vault://` handles.
4. **`cans/artifacts/test-plan/matrix.yaml` (AS-01)** (Fix 2 & Fix 5) — banned mocking AST and authorizer, but forgot to ban mocking the new `sqlite3_update_hook` and socket-edge vault injector.

Here are the final patches to seal them:

```diff
diff --git a/cans/artifacts/system-schema.yaml b/cans/artifacts/system-schema.yaml
index 1111111..2222222 100644
--- a/cans/artifacts/system-schema.yaml
+++ b/cans/artifacts/system-schema.yaml
@@ -140,2 +140,19 @@ tables:
     idx:
       - [[status, resume_at]]
       - [frame_id]
+
+  _outbox_events:
+    target_db: workspace.db
+    description: "Transactional outbox for external API mutations requiring verified idempotency headers"
+    sys: true
+    columns:
+      id: pk
+      idempotency_key: text! unique    # kernel-minted idempotency UUID
+      provider: text!                  # provider slug in apis/
+      verb: text!                      # target API verb
+      payload: json! mask=true         # egress parameters
+      idempotency_header: text!        # verified upstream header (e.g. Idempotency-Key)
+      status: text=pending             # pending, dispatched, failed
+      created_at: int!
+    chk:
+      - "status IN ('pending', 'dispatched', 'failed')"
diff --git a/cans/artifacts/wireframe/flows.json b/cans/artifacts/wireframe/flows.json
index 3333333..4444444 100644
--- a/cans/artifacts/wireframe/flows.json
+++ b/cans/artifacts/wireframe/flows.json
@@ -35,5 +35,5 @@
     "journey_tamper_forensics": {
-      "name": "Integrity Panic & Break-Glass Recovery",
+      "name": "Tamper Quarantine & Forensic Isolation",
       "color": "#f0883e",
-      "entry": "sys.doctor.panic.tamper",
-      "terminal": "sys.doctor.recovery_mode",
-      "description": "Broken SHA-256 chain -> emergency panic (exit 5) -> CAPCLI_RECOVERY=1 diagnostic re-entry"
+      "entry": "sys.doctor.warning.tamper",
+      "terminal": "sys.doctor.quarantine_mode",
+      "description": "Broken SHA-256 chain -> isolate corrupted block to audit.quarantine.jsonl -> alert dead-letter -> active state remains online"
     },
diff --git a/cans/artifacts/test-plan/test-plan-structure.md b/cans/artifacts/test-plan/test-plan-structure.md
index 5555555..6666666 100644
--- a/cans/artifacts/test-plan/test-plan-structure.md
+++ b/cans/artifacts/test-plan/test-plan-structure.md
@@ -318,3 +318,3 @@ cans/artifacts/test-plan/
-| `vs_12_redacted_leak_detection_kill.yaml` | Integration | Routine attempts to print decrypted credential string to stdout; egress scanner detects pattern and triggers `kill_and_alert`. | TN | Emitting secret text to subshell stdout or stderr unintercepted. |
+| `vs_12_opaque_vault_handle_dereference_denial.yaml` | Integration | Guest routine attempts to inspect or print raw `vault://` credential bytes; SDK exposes only opaque token ref; socket proxy strips plaintext from logs. | TN | Allocating plaintext credential buffers in guest runtime address space. |
diff --git a/cans/artifacts/test-plan/matrix.yaml b/cans/artifacts/test-plan/matrix.yaml
index 7777777..8888888 100644
--- a/cans/artifacts/test-plan/matrix.yaml
+++ b/cans/artifacts/test-plan/matrix.yaml
@@ -36,4 +36,4 @@ anti_slop_laws:
   AS-01:
     name: "Banned Mocking Law"
-    rule: "Tests verifying security boundaries (sqlite3_set_authorizer, AST checks, seccomp-bpf, AES-256 vault decryption, token-bucket counters) must never mock the boundary mechanism."
+    rule: "Tests verifying security boundaries (sqlite3_set_authorizer, sqlite3_update_hook, seccomp-bpf, socket-edge vault injection, token-bucket counters) must never mock the boundary mechanism."
     slop_vector: "Agent mocks AuthorizerCallback to return SQLITE_OK in a unit test to make an invalid query pass."
```

No. There were still **4 real contradictions** hidden in `world.md`, `flows.json`, `wireframe-structure.md`, and `test-plan-structure.md`:

1. **`cans/world.md` still claimed the kernel auto-commits `world.sql` to Git on schema migrations** — directly violating Fix 7 (zero runtime Git commits).
2. **`cans/artifacts/wireframe/flows.json` had a broken transition `t_tamper_panic_to_recovery`** — pointing to the deleted `sys.doctor.panic.tamper` state instead of the new quarantine mode (Fix 4).
3. **`cans/artifacts/wireframe/wireframe-structure.md` still cited "Git branch conflict blocks DDL"** for `env.merge.refusal.unmerged` — violating Fix 7 (Git worktrees replaced by namespace forward-plans).
4. **`cans/artifacts/test-plan/test-plan-structure.md` (da_04)** asserted testing system table write denial by running `INSERT INTO _audit` on `workspace.db` — impossible under Fix 1 because `_audit` was physically relocated to `audit.db` (the table does not exist in `workspace.db`).

Here are the diff patches resolving them:

```diff
diff --git a/cans/world.md b/cans/world.md
index 1111111..2222222 100644
--- a/cans/world.md
+++ b/cans/world.md
@@ -17,5 +17,4 @@ cans/world.md
-        - commit automation
-          - trigger — successful schema migrations
-          - cadence — see artifacts/governance.yaml#backup
+        - snapshot automation — deterministic DDL and seed dump generated locally on migration; synced directly to object storage
         - disaster recovery
diff --git a/cans/artifacts/wireframe/flows.json b/cans/artifacts/wireframe/flows.json
index 3333333..4444444 100644
--- a/cans/artifacts/wireframe/flows.json
+++ b/cans/artifacts/wireframe/flows.json
@@ -204,6 +204,6 @@
     {
-      "id": "t_tamper_panic_to_recovery",
+      "id": "t_tamper_quarantine_inspect",
       "journeys": ["journey_tamper_forensics"],
-      "from": ["sys.doctor.panic.tamper"],
-      "to": ["sys.doctor.recovery_mode"],
-      "trigger": "boot_recovery_shell",
-      "label": "CAPCLI_RECOVERY=1 capcli sys doctor",
-      "arrow_type": "denial"
+      "from": ["sys.doctor.warning.tamper"],
+      "to": ["sys.doctor.quarantine_mode"],
+      "trigger": "inspect_quarantine",
+      "label": "capcli sys doctor --quarantine",
+      "arrow_type": "progress"
     },
diff --git a/cans/artifacts/wireframe/wireframe-structure.md b/cans/artifacts/wireframe/wireframe-structure.md
index 5555555..6666666 100644
--- a/cans/artifacts/wireframe/wireframe-structure.md
+++ b/cans/artifacts/wireframe/wireframe-structure.md
@@ -208,3 +208,3 @@ cans/artifacts/wireframe/
-| `env.merge.refusal.unmerged` | refusal | 3 | compile | conflict | Git branch conflict blocks DDL |
+| `env.merge.refusal.plan_conflict` | refusal | 3 | compile | conflict | Target schema migration plan conflict blocks DDL |
@@ -229,4 +229,4 @@ cans/artifacts/wireframe/
-| `sys.doctor.panic.tamper` | panic | 5 | kernel.panic | tampered | Audit SHA-256 chain broken |
-| `sys.doctor.recovery_mode` | success | 0 | — | recovery | `CAPCLI_RECOVERY=1` break-glass active |
+| `sys.doctor.warning.tamper` | success | 0 | — | tampered | Audit SHA-256 chain broken; corrupted block isolated to quarantine |
+| `sys.doctor.quarantine_mode`| success | 0 | — | quarantine | Quarantine ledger inspection active |
diff --git a/cans/artifacts/test-plan/test-plan-structure.md b/cans/artifacts/test-plan/test-plan-structure.md
index 7777777..8888888 100644
--- a/cans/artifacts/test-plan/test-plan-structure.md
+++ b/cans/artifacts/test-plan/test-plan-structure.md
@@ -216,3 +216,3 @@ cans/artifacts/test-plan/
-| `da_04_system_table_write_denial.yaml` | Integration | Agent issues `INSERT INTO _audit VALUES (...)`; C-authorizer rejects write to system table with `SQLITE_DENY`. | TN | Granting agent write permissions to `_audit` in test fixture setup. |
+| `da_04_system_table_write_denial.yaml` | Integration | Agent issues `INSERT INTO _budget_frames VALUES (...)`; C-authorizer on `workspace.db` rejects write to system table with `SQLITE_DENY`. | TN | Granting agent write permissions to system tables in test fixture setup. |
```