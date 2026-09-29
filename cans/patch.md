### Part 1/3: Declarative Schemas, Policy & Budget Core Engine

Unified patch applying deterministic physical units (`fuel`, `egress_bytes`, `tokens`) and purging all fiat USD strings and floats.

```diff
diff --git a/cans/artifacts/system-schema.yaml b/cans/artifacts/system-schema.yaml
--- a/cans/artifacts/system-schema.yaml
+++ b/cans/artifacts/system-schema.yaml
@@ -109,7 +109,8 @@ tables:
       declared_max_duration_ms: int!   # declared timeout ceiling
       consumed_ops: int=0              # primitive executions consumed
       consumed_duration_ms: int=0      # wall-clock milliseconds consumed
-      consumed_spend_usd: text=0.00    # egress USD consumed (stored as fixed-point text)
+      consumed_fuel: int=0             # normalized gas consumed (integer)
+      consumed_egress_bytes: int=0     # physical wire egress payload bytes
       consumed_rows: int=0             # rows affected consumed
       consumed_api_calls: int=0        # HTTP egress operations consumed
       outcome: text=active             # frame completion state

diff --git a/cans/artifacts/governance.yaml b/cans/artifacts/governance.yaml
--- a/cans/artifacts/governance.yaml
+++ b/cans/artifacts/governance.yaml
@@ -48,7 +48,7 @@ routine_shape:
       budget_inheritance: min          # child effective = min(declared, parent_remaining)
       ops_cascade: true                # child ops consume from parent's pool
       duration_cascade: true           # child time consumes from parent's clock
-      spend_scope: session             # spend is session-level, not per-routine
+      fuel_scope: session              # fuel is session-level, not per-routine
       rate_scope: session              # rate is session-level, not per-routine
       rows_scope: trust_session        # rows per trust level per session
       result_tokens_scope: routine     # each routine caps its own output independently
@@ -56,7 +56,7 @@ routine_shape:
       budget_exhaustion: deny          # exhausted budget = exit 2, never silent truncation
       cascade: true
-      session_scoped: [spend_usd, writes_per_minute, capability_calls_per_minute, rows_affected]
+      session_scoped: [fuel, egress_bytes, writes_per_minute, capability_calls_per_minute, rows_affected]
       routine_scoped_cascade: [ops, duration_ms]
       routine_scoped_independent: [result_tokens]
   versions:

diff --git a/cans/artifacts/policy.yaml b/cans/artifacts/policy.yaml
--- a/cans/artifacts/policy.yaml
+++ b/cans/artifacts/policy.yaml
@@ -137,10 +137,10 @@ api:
   prod_first_calls:
     enforce: false                       # killed: un-simulated calls proven via synthetic contracts
     require_contract_proof: true         # OpenAPI schema + dry-run verification replaces human sign-off
-  spend:
-    per_day_usd: 50
-    confirm_above_usd: 100                     # human gate reserved strictly for real budget impact
-    per_call_confirm_usd: 25
+  fuel:
+    per_session_fuel: 100000             # integer gas allocation per session
+    max_call_egress_bytes: 5242880       # 5MB physical wire limit per egress dispatch
+    confirm_above_fuel: 50000            # gate reserved for high wire/compute impact
   rate_limit:                                    # live quota from provider responses
     model: proactive_token_bucket                # client-side bucket is PRIMARY authority
     default_capacity: 60                         # burst ceiling
@@ -204,7 +204,7 @@ env:
     intent: required                           # reads too? no — writes; reads stay free
     confirm_above: { rows: 10 }                # tighter thresholds
     vacuum: deny
-    api: { spend: { per_day_usd: 200 } }
+    api: { fuel: { per_session_fuel: 500000 } }
     serve: { bind: "127.0.0.1" }               # public lives behind a proxy
   sim:
     rate: { writes_per_minute: 1000 }          # fast iteration

diff --git a/cans/budget.md b/cans/budget.md
--- a/cans/budget.md
+++ b/cans/budget.md
@@ -25,7 +25,8 @@
       - Consumed counters
         - consumed_ops: int=0
         - consumed_duration_ms: int=0
-        - consumed_spend_usd: int=0
+        - consumed_fuel: int=0
+        - consumed_egress_bytes: int=0
         - consumed_rows: int=0
         - consumed_api_calls: int=0
       - Bookkeeping
@@ -35,11 +36,11 @@
     - Events
       - budget.frame_push
         - Payload: frame_id, routine@version, parent_frame, session, env
         - declared: { max_ops: 50, max_duration_seconds: 300 }
-        - inherited_remaining: { ops: 38, duration_ms: 254800, spend_usd: 41.60 }
+        - inherited_remaining: { ops: 38, duration_ms: 254800, fuel: 82000, egress_bytes: 4194304 }
         - inherited_remaining is the parent-side min() already computed per dimension
       - budget.frame_pop
-        - consumed: { ops: 4, duration_ms: 1200, spend_usd: 0.80 }
-        - returned_to_parent: { ops: 34, duration_ms: 253600, spend_usd: 40.80 }
+        - consumed: { ops: 4, duration_ms: 1200, fuel: 1600, egress_bytes: 12480 }
+        - returned_to_parent: { ops: 34, duration_ms: 253600, fuel: 80400, egress_bytes: 4181824 }
         - Parent sees exactly what the child burned — pools reconcile per frame
       - Frame push/pop are audit events; tailable live via `sys audit tail --follow`
     - Telemetry streaming — frame lifecycle pushes over WebSocket/SSE: see interface.md#Daemon-API-&-telemetry-surface
@@ -69,10 +70,10 @@
       - Duration
         - Unit: wall-clock milliseconds
         - Scope: per-routine plus session
         - Cascade: child time consumes the parent's clock
-      - Spend
-        - Unit: USD incurred by egress
+      - Fuel & Wire Egress
+        - Unit: deterministic integer gas & socket payload bytes
         - Scope: one pool per session
         - Cascade: no bypass via splitting — single session pool
       - Rows affected
         - Unit: rows written or affected
@@ -87,7 +88,7 @@
         - Cascade: none — each routine caps its own output independently
     - Composition flags (artifacts/governance.yaml)
       - budget_inheritance: min — child effective = min(declared, parent_remaining)
       - ops_cascade: true, duration_cascade: true
-      - spend_scope: session, rate_scope: session, rows_scope: trust_session
+      - fuel_scope: session, rate_scope: session, rows_scope: trust_session
       - result_tokens_scope: routine
       - max_nesting_depth: 5 caps composition depth
       - budget_exhaustion: deny — exhausted budget = exit 2, never silent truncation
@@ -99,8 +100,8 @@
       - constraint resolution
         - tightest dimension — tightest_constraint names dimension nearest exhaustion
         - limit string — effective_limits formats min(ceiling, parent_remaining)
-      - budget_status.cascade: session_ops_remaining 488, session_duration_remaining_ms 555000
-      - session_spend_remaining_usd 37.6, session_rate_remaining 287
+      - budget_status.cascade: session_ops_remaining 488, session_duration_remaining_ms 555000
+      - session_fuel_remaining 80400, session_egress_bytes_remaining 4181824, session_rate_remaining 287
       - tightest_constraint names the first dimension to block (null while headroom lasts)
       - composition.effective_limits: "min(50, session_remaining)" strings per dimension
       - composition block: max_nesting_depth, child_routines list, budget_inheritance
@@ -118,7 +119,7 @@
         - Rows surface in cost_envelope.live_quota: limit, remaining, reset_at, status per provider
       - Enforcement
-        - Static per_day_usd spend caps are the floor under dynamic quota
+        - Static session fuel caps and wire limits are the floor under dynamic quota
         - Pre-call deny at deny_at_remaining → exit 2 before egress: see physics.md#Fail-closed-stance
         - Remote 429 triggers backoff retry; persistent exhaustion surfaces upstream provider limits cleanly
         - Live remaining/reset_at/budget status before invoking: see action.md#External-APIs
@@ -165,5 +166,5 @@
     - No `budget` noun, no `--override-budget`: see interface.md#Refusals
-    - Spend-cap forensics localize to the leaf op; fix the policy, not the routine: see effect.md#Failure-forensics
+    - Fuel-cap forensics localize to the leaf op; fix the policy, not the routine: see effect.md#Failure-forensics
```

---
Ready for **Part 2/3** (`action.md`, `effect.md`, `trust.md`, `assembly.md`, `overview.md`, `physics.md`). Confirm to proceed.

### Part 2/3: Runtime Engines, Assembly & Capability Specs

Unified patch replacing fiat references with deterministic fuel, wire byte ceilings, and integer metrics across runtime domains and assembly specs.

```diff
diff --git a/cans/action.md b/cans/action.md
--- a/cans/action.md
+++ b/cans/action.md
@@ -23,7 +23,7 @@
         - tokens — file size, parameter schema, result caps
         - duration — p50, p95, timeout ceiling
         - storage — writes, reads, max rows affected
         - concurrency — active locks, max ops per run
-        - api metrics — quota, daily spend remaining, sim mode
+        - api metrics — quota, session fuel remaining, wire byte limit, sim mode
         - composition — nesting depth, child routines, budget cascade
         - pre-flight check — can_invoke_now boolean verdict
     - Routines
@@ -72,7 +72,7 @@
         - input typing — order_id: Param[str]
         - api read — ctx.api.call with secret injection
         - db read — ctx.db.query with AST check
-        - api write — ctx.api.call with pre-call spend check
+        - api write — ctx.api.call with pre-call fuel check
         - db write — ctx.db.txn context wrapping ctx.db.execute
         - return value — summary-sized dict
     - Shape constraints
@@ -121,7 +121,7 @@
         - nesting ceiling — see artifacts/governance.yaml#routine_shape
         - import ceiling — see artifacts/governance.yaml#routine_shape
         - cross-agent deduplication — near-duplicate across agents forces merge or fork
-        - counter scopes — spend, rate, rows session-scoped
+        - counter scopes — fuel, wire bytes, rate, rows session-scoped
         - constraint direction — cages tighten downward
         - min cascade law — see budget.md#Cascade
         - sim mode propagation — child gaps propagate up: see space.md#Rehearsal-&-sim
@@ -154,7 +154,7 @@
         - pending asks — queries _pending_asks count and unresolved vault requests
         - sensory inbox — queries queued inbound events without pulling payloads
         - active locks — reads active lease locks from claims and db locks
-        - budget headroom — reads consumed spend and remaining session quota
+        - budget headroom — reads consumed fuel and remaining session quota
         - system health — nominal status, drift alarms, or thrash warnings
         - result constraint — dense summary strictly under 500 tokens
         - invocation trigger — standard zero-step executed at session boot
@@ -204,7 +204,7 @@
       - Mirror view definitions
         - shared_subsequences — aggregates frequent n-grams to propose routines
-        - primitive_cost — groups duration p50/p95 and USD spend per leaf
+        - primitive_cost — groups duration p50/p95, fuel, and wire bytes per leaf
         - primitive_failures — isolates leaf failures by version and sequence
         - op_frequency — tracks atomic op calls across sessions
       - Consolidation — merge clustering via fingerprint similarity: see time.md#Consolidation

diff --git a/cans/effect.md b/cans/effect.md
--- a/cans/effect.md
+++ b/cans/effect.md
@@ -118,7 +118,7 @@
     - Forensic mirror views
       - diagnostic trace — causal tree walk for failures: see #Query-surfaces
       - primitive_failures — aggregates failures by version, leaf seq, and capability
-      - primitive_cost — aggregates duration and spend per leaf primitive
+      - primitive_cost — aggregates duration, fuel, and wire payload bytes per leaf primitive
     - Forensic quarantine — prevents auto-retry on unhandled runtime faults: see physics.md#Exit-code-law
   - Provenance
     - Artifact lineage

diff --git a/cans/trust.md b/cans/trust.md
--- a/cans/trust.md
+++ b/cans/trust.md
@@ -45,7 +45,7 @@
     - Pinned promotion
       - full autonomy — autonomous pin unlocked via invariant & mutation tests
-      - boundary safety — high spend or schema migrations governed by hard-coded budget caps
+      - boundary safety — high fuel consumption or schema migrations governed by hard-coded budget caps
     - Promotion queue
       - mechanics — capcli routine ship <name> reviewed --queue
       - inspection — capcli routine pending surfaces batch candidates
@@ -68,7 +68,7 @@
     - Cost evidence
       - profiling metrics
         - latency — p50 and p95 duration per leaf primitive
-        - spend — USD incurred per primitive
+        - fuel — integer compute fuel and socket wire bytes incurred per primitive
       - parameter sampling
         - source — real historical values from capcli sys audit sample
         - synthetic fixtures — banned for ship evidence

diff --git a/cans/assembly.md b/cans/assembly.md
--- a/cans/assembly.md
+++ b/cans/assembly.md
@@ -25,7 +25,7 @@
       - system-schema.yaml — kernel-managed system surfaces: see world.md#Dual-schema
       - world.sql — deterministic DDL export for fresh instances: see world.md#SQLite-as-SSOT
     - Governance specifications
-      - governance.yaml — structural limits, LOC, and spend caps: see artifacts/governance.yaml
+      - governance.yaml — structural limits, LOC, and fuel caps: see artifacts/governance.yaml
       - policy.yaml — behavioral authorizer and AST rules: see physics.md#Two-layer-enforcement
       - sealing.rules — cross-domain boundaries and sealing laws: see cans/_rules.yaml
   - Instance workspace substrate
@@ -160,8 +160,8 @@
         - sim_mock.rs — serves canned fixtures from apis/*.mock.yaml: see space.md#Sim-mode-taxonomy
         - refresh.rs — auto-rotates ephemeral bearer tokens: see artifacts/governance.yaml#api
       - Execution gates
         - quota_gate.rs — fails closed if bucket tokens < 1: see budget.md#Quotas
-        - spend_gate.rs — enforces daily USD limits: see artifacts/policy.yaml#api.spend
+        - fuel_gate.rs — enforces session fuel and wire payload caps: see artifacts/policy.yaml#api.fuel
         - sim_gate.rs — denies prod-only verbs in dev and sim: see space.md#Policy-overlays
-      - Domain telemetry — tracks rate bucket token drain, egress spend, and retry counts
+      - Domain telemetry — tracks rate bucket token drain, wire egress bytes, fuel consumption, and retry counts
     - Domain 5: Event & schedule bindings (bind/)
@@ -215,7 +215,7 @@
       - state.tsx — raw relational schema inspector, masked cell renderer, and table row counts
       - capability.tsx — routine version inspector, static manifest diffs, and dynamic leaf fingerprints
       - audit.tsx — live virtualized audit tail, causal DAG breadcrumbs, and denial explanation dialogs
-      - budget.tsx — session frame cascade tree, spend gauges, and live proactive token-bucket meters
+      - budget.tsx — session frame cascade tree, fuel gauges, wire byte meters, and live proactive token-bucket meters
       - approvals.tsx — human promotion queue, canary veto timers, and interactive ping.ask dialogs
       - vault.tsx — out-of-band credential injection with mobile biometric/FaceID authorization
       - recovery.tsx — VACUUM snapshot catalog and point-in-time rollback trigger

diff --git a/cans/physics.md b/cans/physics.md
--- a/cans/physics.md
+++ b/cans/physics.md
@@ -100,7 +100,7 @@
       - exit 2 — invariant or governance block; state untouched (state_modified: false)
         - domain db.engine — SQLite check constraints, foreign key violations, busy timeout
         - domain policy.authorizer — C-level table/column write denied
-        - domain policy.budget — frame limits or session op/spend ceilings exhausted
+        - domain policy.budget — frame limits or session op/fuel ceilings exhausted
         - domain policy.trust — action forbidden by caller trust rung (e.g. draft touching prod)
       - exit 3 — compile-time refusal, validation failure, boot lockfile mismatch, or missing parameter
       - exit 4 — domain routine.runtime; uncaught Python sandbox exception or type crash; transaction cleanly rolled back

diff --git a/cans/agent.md b/cans/agent.md
--- a/cans/agent.md
+++ b/cans/agent.md
@@ -50,7 +50,7 @@
   - Sessions and boundaries
     - Session lifecycle
       - scoping — session id rides every budget frame, audit event, and claim
-      - tracking — session counters govern spend, rate, and rows affected
+      - tracking — session counters govern fuel, wire bytes, rate, and rows affected
       - workspace anchor — CAPCLI_WORKSPACE env var or --workspace flag anchors root; cd reliance banned
     - Harness execution boundary

diff --git a/cans/interface.md b/cans/interface.md
--- a/cans/interface.md
+++ b/cans/interface.md
@@ -25,7 +25,7 @@
         - tokens — file size, parameter schema, result caps
         - duration — p50, p95, timeout ceiling
         - storage — writes, reads, max rows affected
         - concurrency — active locks, max ops per run
-        - api metrics — quota, daily spend remaining, sim mode
+        - api metrics — quota, session fuel remaining, sim mode
         - composition — nesting depth, child routines, budget cascade
         - pre-flight check — can_invoke_now boolean verdict
     - Storage path: db noun
@@ -143,7 +143,7 @@
       - Layer 2: Capability Inspector — routine catalog, version diffs, OpenAPI verb states, and manifest-vs-fingerprint graphs
       - Layer 3: Policy & Governance — live policy authorizer rules, lockfile SHA256 integrity, and rate ceilings
       - Layer 4: Audit Spine — live streaming event tail, causal DAG trace explorer, and machine denial decoders
-      - Layer 5: Budget & Telemetry — call stack frame trees, spend consumption meters, and token-bucket drain gauges
+      - Layer 5: Budget & Telemetry — call stack frame trees, fuel consumption meters, wire byte counters, and token-bucket drain gauges
       - Layer 6: Promotion & Approvals — staged routine promotions, DDL forward migration previews, and canary veto timers
       - Layer 7: Human Interaction (Ask) — structured question resolution cards with fail-closed timeout indicators
       - Layer 8: Vault & Biometrics — out-of-band credential injection screen with mobile biometric/FaceID support
```

---
Ready for **Part 3/3** (`capcli.playbook.md`, `capcli.landing-copy.md`, `README.md`). Confirm to proceed.


### Part 3/3: Playbook & Landing Copy

Unified patch purging fiat spend from execution frames, telemetry briefings, and architectural copy.

```diff
diff --git a/cans/artifacts/capcli.playbook.md b/cans/artifacts/capcli.playbook.md
--- a/cans/artifacts/capcli.playbook.md
+++ b/cans/artifacts/capcli.playbook.md
@@ -410,14 +410,14 @@
 def overview():
     low_stock = ctx.db.query("SELECT sku, stock FROM products WHERE stock < 20 LIMIT 5")
     pending = ctx.db.query("SELECT count(*) as count FROM orders WHERE status = 'pending'")[0]["count"]
-    spend = ctx.db.query("SELECT consumed_spend_usd FROM _budget_frames WHERE outcome = 'active' ORDER BY created_at DESC LIMIT 1")
+    fuel = ctx.db.query("SELECT consumed_fuel FROM _budget_frames WHERE outcome = 'active' ORDER BY created_at DESC LIMIT 1")
     asks = ctx.db.query("SELECT count(*) as count FROM _pending_asks WHERE status = 'pending'")[0]["count"]
     inbox_qty = ctx.db.query("SELECT count(*) as count FROM _inbox WHERE processed = 0")[0]["count"]
     locks = ctx.db.query("SELECT target FROM _claims WHERE expires_at > strftime('%s','now')")
     
     return {
         "low_stock_alerts": low_stock,
         "pending_orders": pending,
-        "active_spend_usd": float(spend[0]["consumed_spend_usd"]) if spend else 0.0,
+        "consumed_fuel": fuel[0]["consumed_fuel"] if fuel else 0,
         "pending_human_asks": asks,
         "inbox_backlog": inbox_qty,
         "active_locks": [l["target"] for l in locks],
@@ -438,7 +438,7 @@
 {
   "low_stock_alerts": [],
   "pending_orders": 0,
-  "active_spend_usd": 0.0,
+  "consumed_fuel": 0,
   "pending_human_asks": 0,
   "inbox_backlog": 0,
   "active_locks": [],
@@ -470,7 +470,7 @@
 {
   "low_stock_alerts": [],
   "pending_orders": 0,
-  "active_spend_usd": 0.0,
+  "consumed_fuel": 0,
   "pending_human_asks": 0,
   "inbox_backlog": 0,
   "active_locks": [],
@@ -600,16 +600,16 @@
 [BUDGET_CASCADE]
 FRAME_PUSH:        frame_008 (process_wholesale_order@1)
 PARENT_FRAME:      session_root
 OPS_LIMIT:         min(declared: 8, session_remaining: 50)   -> 8 ops
 DURATION_LIMIT:    min(declared: 15s, session_remaining: 300s) -> 15s
-SPEND_LIMIT:       min(declared: $5.00, session_remaining: $20.00) -> $5.00
+FUEL_LIMIT:        min(declared: 5000, session_remaining: 50000) -> 5000 fuel
 
 [ROUTINE_EXECUTED]
 STATUS:            SUCCESS (Exit 0)
 RESULT:            {"status": "success", "order_id": 1, "charge_id": "pi_mock_9918", "remaining_stock": 98}
 
 [BUDGET_CASCADE]
 FRAME_POP:         frame_008 closed.
-CONSUMED:          5 ops, 0.42s duration, $0.44 spend
-RECONCILED:        Returned to session pool -> ops_remaining: 45, spend_remaining: $19.56
+CONSUMED:          5 ops, 0.42s duration, 850 fuel (1420 bytes egress)
+RECONCILED:        Returned to session pool -> ops_remaining: 45, fuel_remaining: 49150
 AUDIT_LOG:         budget.frame_pop committed to _audit [event_id: op_009]
 ```

@@ -647,7 +647,7 @@
   workspace:     envs/sim/workspace.db (forked from snap_migration_001)
   masking:       fpa_active (customer_email -> anon_*@sim.local)
   egress_engine: mock_local (apis/stripe.sim.yaml)
-  spend_cap:     $0.00 (isolated)
+  egress_mode:   isolated (mock_local)
 ```

@@ -825,7 +825,7 @@
 Opens phone PWA dashboard (`https://capcli.local:4040`):
 * **Orders Processed Overnight:** 4 ($612.00 captured).
 * **Inventory Stock:** Decremented accurately; zero negative drift.
-* **Token Spend:** $0.02 (Zero exploratory burn; overview baseline held).
+* **Session Fuel Burned:** 3,400 (Zero exploratory burn; overview baseline held).
 * **Unreviewed Code in Prod:** Exactly 0 lines.
 
 *(Closes phone. Doesn't open terminal. The coffee business is running itself.)*

diff --git a/cans/artifacts/capcli.landing-copy.md b/cans/artifacts/capcli.landing-copy.md
--- a/cans/artifacts/capcli.landing-copy.md
+++ b/cans/artifacts/capcli.landing-copy.md
@@ -38,7 +38,7 @@
 It provides the three things an LLM can never give itself:
 1. **Physical Laws:** A C-level database authorizer and OS sandboxes that make catastrophic writes physically impossible.
-2. **Hard Budget Cages:** Spend, ops, and duration ceilings that halt runaway processes instantly (`exit 2`).
+2. **Hard Budget Cages:** Fuel, wire bytes, ops, and duration ceilings that halt runaway processes instantly (`exit 2`).
 3. **An Immutable Spine:** A tamper-evident SHA256 audit log where every intent, query, and leaf event is permanently recorded.
 
 ---
@@ -64,7 +64,7 @@
 | The Scenario | Hermes Alone | Hermes + Capcli |
 | :--- | :--- | :--- |
 | **Unbounded State Mutation** | **Corrupts production.** Blindly overwrites records across table boundaries without constraints. | **Impossible.** Killed at C-authorizer & AST layers before statement execution (`exit 2`). |
-| **An Infinite Error Loop** | **Drains your bank account.** Burns hundreds in token compute unnoticed. | **Killed instantly.** Watchdog timer cuts execution at the exact spend ceiling. |
+| **An Infinite Error Loop** | **Drains your bank account.** Burns hundreds in token compute unnoticed. | **Killed instantly.** Watchdog timer cuts execution at the exact fuel and op ceiling. |
 | **Handling API Credentials** | **Leaks keys.** Plaintext tokens dumped into context or local bash files. | **Zero leaks.** Keys injected by kernel at perimeter; agent never sees raw strings. |
 | **Repeated Daily Operations** | **High token waste.** Re-reasons the same workflow daily from scratch. | **Zero token burn.** Invokes hash-pinned routines like compiled muscle memory. |
 | **Testing a Risky New Action** | **Tests on live users.** Real customers get bad refunds and broken links. | **Forced rehearsal.** Must pass invariant replay simulation before promotion. |
```

---
All 3 parts completed. Every trace of fiat currency in the kernel and specification is completely purged and replaced with deterministic physical gas (`fuel`), wire bytes, and integer limits.

### Part 1/2: Core Schemas, Policy & Governance

Unified patch adding multi-window quota tracking, structured JSON usage header parsers (Meta Graph API style), transient in-flight polling rules, and the `exit 6` yield persistence table.

```diff
diff --git a/cans/artifacts/system-schema.yaml b/cans/artifacts/system-schema.yaml
--- a/cans/artifacts/system-schema.yaml
+++ b/cans/artifacts/system-schema.yaml
@@ -52,6 +52,9 @@ tables:
       bucket_capacity: int!            # max token burst size
       tokens_available: int!           # current proactive client-side token count
       refill_rate_per_s: real!         # token drip rate per second
+      window_seconds: int=0            # rolling window size in seconds (0 = steady token bucket)
+      quota_type: text=token_bucket    # token_bucket or sliding_window
+      cost_per_call: int=1             # token weight consumed per call
       last_provider_remaining: int=-1  # last observed provider X-RateLimit-Remaining
       reset_at: int=0                  # unix epoch seconds for quota reset
       last_reconciled_at: int!         # timestamp of last header reconciliation
@@ -59,6 +62,7 @@ tables:
       last_updated: int!               # timestamp of last header extraction
     chk:
       - "last_provider_remaining >= -1"
+      - "quota_type IN ('token_bucket', 'sliding_window')"
     idx:
       - [[provider, env]]
       - [[provider, scope_key, env]]
@@ -113,9 +117,10 @@ tables:
       consumed_rows: int=0             # rows affected consumed
       consumed_api_calls: int=0        # HTTP egress operations consumed
+      yield_until: int=0               # unix epoch seconds for scheduled resumption on exit 6
       outcome: text=active             # frame completion state
       created_at: int!
       closed_at: int
     chk:
-      - "outcome IN ('active', 'success', 'exhausted', 'denied', 'error')"
+      - "outcome IN ('active', 'success', 'exhausted', 'denied', 'error', 'yielded')"
     idx:
       - [[session, env]]
       - [[routine, version]]
@@ -207,3 +212,20 @@ tables:
     idx:
       - [[capability, version]]
+
+  _suspended_tasks:
+    description: "Daemon-managed background tasks paused via exit 6 awaiting quota refill"
+    sys: true
+    columns:
+      id: pk
+      frame_id: text! ref=_budget_frames.frame_id
+      session: text!
+      routine: text!
+      version: int!
+      params: json!
+      priority: text=standard          # critical, standard, background
+      resume_at: int!                  # unix epoch seconds
+      deferments: int=0                # deferral count against yield_max_deferments
+      status: text=pending             # pending, dispatched, aborted
+    chk:
+      - "status IN ('pending', 'dispatched', 'aborted')"
+    idx:
+      - [[status, resume_at]]
+      - [frame_id]

diff --git a/cans/artifacts/policy.yaml b/cans/artifacts/policy.yaml
--- a/cans/artifacts/policy.yaml
+++ b/cans/artifacts/policy.yaml
@@ -148,8 +148,17 @@ api:
     default_capacity: 60                         # burst ceiling
     refill_rate_per_sec: 1.0                     # steady-state token drip
     pre_call_gate: true                          # fail-closed: tokens < 1 → exit 2 immediately
     header_calibration:                          # reactive headers used ONLY to recalibrate bucket
       reconcile_on_response: true                # sync local bucket down if provider reports lower
+      parser_engine: dynamic                     # standard_rfc or json_path
       reset_header: "X-RateLimit-Reset"
       remaining_header: "X-RateLimit-Remaining"
+      json_usage_header: "X-Business-Use-Case-Usage" # structured JSON header support
+      utilization_jsonpath: "$.*.call_count"
+      wait_seconds_jsonpath: "$.*.estimated_time_to_regain_access"
+  in_flight_polling:
+    allow_transient: true                        # permits short-interval status polling in routines
+    max_poll_duration_seconds: 30                # hard ceiling for async container/job verification
+    min_poll_interval_seconds: 2                 # prevents tight busy-waiting
+    count_as_single_op: true                     # whole poll loop registers as 1 aggregate op
     audit:
       record_before_after: true                  # quota_before/quota_after on every api.call event
       denial_cites_remaining: true               # exit 2 message includes remaining + reset_at

diff --git a/cans/artifacts/governance.yaml b/cans/artifacts/governance.yaml
--- a/cans/artifacts/governance.yaml
+++ b/cans/artifacts/governance.yaml
@@ -38,6 +38,8 @@ routine_shape:
   yield_enabled: true
   earmark_max_ttl_hours: 4
   yield_max_deferments: 5
+  max_in_flight_poll_seconds: 30       # async 2-step media/container polling duration cap
+  max_suspended_tasks: 100             # daemon queue capacity for yielded frames
     sandbox:
       provider: auto                  # auto | bwrap | podman | broker
       scratch_mb: 64                  # tmpfs ceiling
@@ -124,7 +126,7 @@ watch:
   webhook:
     max_payload_bytes: 65536
     events_per_minute: 100            # DDoS guard on the mailbox
   poll:
-    min_interval_minutes: 5           # no tight-loop polling
+    min_interval_minutes: 5           # no tight-loop polling (in-flight api.poll_until exempt)
     max_poll_watches: 10              # polling costs egress budget
   dead_letter:
     max_age_days: 30
```

---
Ready for **Part 2/2** (`action.md`, `budget.md`, `assembly.md` for `ctx.api.poll_until`, daemon task resumption, and multi-window quota logic). Confirm to proceed.




### Part 2/2: Runtime SDK, Engine Specs & Daemon Resumption Queue

Unified patch adding the `ctx.api.poll_until()` primitive, multi-window sliding quotas, structured JSON header extraction, and the daemon `exit 6` resumption worker.

```diff
diff --git a/cans/action.md b/cans/action.md
--- a/cans/action.md
+++ b/cans/action.md
@@ -109,6 +109,7 @@
         - execution model — strictly sequential
         - transaction integrity — ctx.api.call strictly forbidden inside ctx.db.txn blocks
+        - transient polling — atomic ctx.api.poll_until permitted; raw time.sleep loops banned
         - banned patterns — ctx.on listeners, reactive streams, subscriptions
         - failure modes — callbacks break DAG linearity, txn boundaries, replay
         - architecture law — events start routines, routines never consume events
@@ -176,6 +177,7 @@
       - External api methods
         - ctx.api.call(verb, params, intent) — governed HTTP egress
+        - ctx.api.poll_until(verb, params, condition, timeout_s, interval_s) — kernel-managed in-flight polling (1 aggregate op)
         - egress retry — automatic backoff and jitter on 429/503 upstream responses
         - ctx.api.verify(verb, key) — key validation check
       - Blob storage methods
@@ -201,6 +203,7 @@
         - missing secret fallback — missing secret_ref auto-binds from CAPCLI_SECRET_* before triggering headless exit 3 or ask prompt
         - pre-call quota — deny before network dispatch: see budget.md#Quotas
         - idempotency — kernel-minted key persisted before egress
+        - in-flight wait — poll_until executes sleep in Rust runtime; Python interpreter never busy-waits
       - Sandbox boundaries
         - runtime isolation — Tier 1 unshares network namespace; Tier 2 unsets outbound proxy env vars and relies on ctx mediation: see physics.md#Platform-tier-taxonomy
         - transport bridge — local IPC permitted exclusively to kernel endpoint

diff --git a/cans/budget.md b/cans/budget.md
--- a/cans/budget.md
+++ b/cans/budget.md
@@ -32,7 +32,8 @@
       - Bookkeeping
         - created_at, closed_at: int timestamps
-        - outcome chk-constrained: active, success, exhausted, denied, error
+        - yield_until: int timestamp for scheduled re-entry on quota depletion
+        - outcome chk-constrained: active, success, exhausted, denied, error, yielded
         - Indexes: [session, env], [routine, version], [parent_frame]
     - Events
       - budget.frame_push
@@ -115,6 +116,9 @@
       - Local bucket — token-bucket throttle regulates client-side egress cadence
+      - Multi-window tracking — supports dual-rate partitions (burst bucket + rolling window ceilings e.g. 24h / 86400s)
       - Gate decision — local bucket empty pauses dispatch up to timeout; hard limit exhaustion throws exit 2
-      - Header calibration — provider headers calibrate local drift downward
+      - Dynamic header calibration — reconciles RFC standard headers or extracts structured JSON payloads (e.g. X-Business-Use-Case-Usage) via JSONPath
       - Remote 429 handling — automatic exponential backoff with jitter in kernel proxy before reporting error
       - Storage
@@ -155,7 +159,8 @@
     - Policy
       - budget_exhaustion: yield_or_deny — governed by priority class (artifacts/governance.yaml)
-      - Yield signal — dry pool + Background/Standard task returns `yield_until` timestamp (exit 6)
+      - Yield signal — dry pool + Background/Standard task marks frame 'yielded', persists to _suspended_tasks, and returns exit 6
+      - Task resumption — daemon monitors resume_at timestamps and automatically re-queues execution on token refill
       - Hard deny — dry pool + Critical task throws exit 2 (see physics.md#Exit-code-law)
       - No partial execution past budget — routine fails cleanly, no half-executed side effects
       - Runtime: op #51 aborts (limit_exceeded), watchdog kills past 300s, results truncated: true

diff --git a/cans/assembly.md b/cans/assembly.md
--- a/cans/assembly.md
+++ b/cans/assembly.md
@@ -126,6 +126,7 @@
       - context_db.py — ctx.db query, execute, txn, and lock wrappers: see action.md#The-ctx-contract
       - context_api.py — ctx.api call and verify egress wrappers: see action.md#The-ctx-contract
+      - context_api.py — exposes poll_until IPC bridge to kernel runtime
       - context_storage.py — ctx.storage put, get, and url wrappers: see action.md#The-ctx-contract
       - context_ping.py — ctx.ping notify and ask suspension handlers: see action.md#The-ctx-contract
       - ipc_client.py — streaming JSON-RPC over /run/capcli/kernel.sock: see action.md#Sandbox-execution
@@ -158,6 +159,7 @@
     - Domain 4: External API gateway (api/)
       - Subsystem modules
         - catalog.rs — manages OpenAPI YAML specs in apis/: see action.md#Catalog-synchronization
-        - quota.rs — client token bucket tracking in _api_quota: see budget.md#Quotas
+        - quota.rs — dual-window token bucket and rolling window accounting in _api_quota: see budget.md#Quotas
+        - header_parser.rs — extracts RFC headers and parses nested JSON usage payloads: see artifacts/policy.yaml#api
         - egress.rs — reqwest HTTP proxy with secret injection: see agent.md#Egress-injection
         - sim_mock.rs — serves canned fixtures from apis/*.mock.yaml: see space.md#Sim-mode-taxonomy
@@ -194,6 +196,7 @@
     - Persistent daemon crate (crates/capcli-daemon/src/)
       - daemon surface
         - server.rs — axum HTTP/WS server on 127.0.0.1:4040: see interface.md#Administrative-cockpit-pwa
+        - yield_queue.rs — evaluates _suspended_tasks and re-dispatches tasks on quota refill
         - ipc.rs — tokio Unix domain socket listener on kernel.sock: see action.md#Sandbox-execution
         - cron.rs — croner schedule evaluator daemon: see time.md#Schedule-&-maintenance
         - webhook.rs — inbound HMAC signature verification: see action.md#Bindings
```

---
All edits completed. The kernel now supports:
1. **Multi-window rate limits** (e.g. 10 burst + 250 rolling 24h).
2. **Structured JSON usage header parsing** for vendor APIs like Meta.
3. **`ctx.api.poll_until()`** for 2-step media/container workflows without burning op ceilings or hallucinating busy-waits.
4. **Persistent task resumption** for `exit 6` yields in `_suspended_tasks`.


### Part 1/2: Declarative Earmark Substrate, Authorizer Tables & Brokerage Policy

Unified patch defining the missing `_budget_earmarks` table, integrating `tokens_earmarked` into `_api_quota`, locking agent writes at Layer 1 authorizer, and enforcing preemption rules.

```diff
diff --git a/cans/artifacts/system-schema.yaml b/cans/artifacts/system-schema.yaml
--- a/cans/artifacts/system-schema.yaml
+++ b/cans/artifacts/system-schema.yaml
@@ -51,6 +51,7 @@ tables:
       env: text!                       # sim and prod track quotas independently
       bucket_capacity: int!            # max token burst size
       tokens_available: int!           # current proactive client-side token count
+      tokens_earmarked: int=0          # reserved tokens ring-fenced from global pool
       refill_rate_per_s: real!         # token drip rate per second
       window_seconds: int=0            # rolling window size in seconds (0 = steady token bucket)
       quota_type: text=token_bucket    # token_bucket or sliding_window
@@ -229,3 +230,26 @@ tables:
     idx:
       - [[status, resume_at]]
       - [frame_id]
+
+  _budget_earmarks:
+    description: "Proactive quota reservations ring-fencing tokens for planned tasks"
+    sys: true
+    columns:
+      id: pk
+      earmark_id: text!~              # unique reservation handle (e.g. emk_sched_01)
+      provider: text!                 # provider slug (e.g. threads, stripe)
+      verb: text!                     # target API verb
+      scope_key: text=global          # per-account partition (e.g. act_123)
+      agent: text!                    # agent claiming the allocation
+      session: text!                  # session context
+      priority: text=standard         # critical, standard, background
+      tokens_reserved: int!           # count of reserved slots
+      tokens_consumed: int=0          # count already burned
+      expires_at: int!                # unix epoch seconds (TTL)
+      status: text=active             # active, released, expired, exhausted
+    chk:
+      - "status IN ('active', 'released', 'expired', 'exhausted')"
+      - "priority IN ('critical', 'standard', 'background')"
+      - "tokens_consumed <= tokens_reserved"
+    idx:
+      - [[provider, verb, status]]
+      - [[expires_at, status]]
+      - [earmark_id]

diff --git a/cans/artifacts/policy.yaml b/cans/artifacts/policy.yaml
--- a/cans/artifacts/policy.yaml
+++ b/cans/artifacts/policy.yaml
@@ -23,6 +23,8 @@ authorizer:
       allow: [read]
     _api_catalog:
       allow: [read]
+    _budget_earmarks:
+      allow: [read]
     _budget_frames:
       allow: [read]
     secrets:
@@ -75,7 +77,7 @@ query:
     confirm_above: { rows: 50000 }             # raised: human gate only on massive blast radius
 
   system_tables:
-    deny_write: [_audit, _api_quota, _api_catalog, _budget_frames, secrets, agents, claims, _pending_asks, _watch_cursors, _capability_embeddings, routine_stats, _system_schema]
+    deny_write: [_audit, _api_quota, _api_catalog, _budget_earmarks, _budget_frames, secrets, agents, claims, _pending_asks, _watch_cursors, _capability_embeddings, routine_stats, _system_schema]
     deny_read: []                              # reads allowed; writes are kernel-internal
 
 # ───────────────────────────────────────────────────────────────
@@ -165,6 +167,16 @@ api:
       record_before_after: true                  # quota_before/quota_after on every api.call event
       denial_cites_remaining: true               # exit 2 message includes remaining + reset_at
     env_scoped: true                             # sim and prod track independently
+  brokerage:
+    min_trust_to_earmark: reviewed               # drafts cannot lock enterprise quota
+    max_earmark_ratio: 0.8                       # no single reservation can lock > 80% of bucket
+    max_earmarks_per_session: 10                 # anti-hoarding per session
+    preemption:
+      background_yield_threshold: 15             # background tasks yield (exit 6) if unreserved tokens < 15
+      critical_bypass_earmark: true              # critical tasks can borrow unburned earmarks in emergency
+    lease:
+      max_ttl_hours: 24                          # max lifespan for a reserved slice
+      decay_sweep_interval_minutes: 5            # daemon sweeper frequency
   external_writes:
     require_intent: true
     require_trust: reviewed

diff --git a/cans/artifacts/governance.yaml b/cans/artifacts/governance.yaml
--- a/cans/artifacts/governance.yaml
+++ b/cans/artifacts/governance.yaml
@@ -36,8 +36,9 @@ routine_shape:
   priority_classes: [critical, standard, background]
   preemption_enabled: true
   yield_enabled: true
-  earmark_max_ttl_hours: 4
+  earmark_max_ttl_hours: 24            # aligned with 24h rolling windows
   yield_max_deferments: 5
+  max_active_earmarks: 50              # registry-wide active earmark ceiling
   max_in_flight_poll_seconds: 30       # async 2-step media/container polling duration cap
   max_suspended_tasks: 100             # daemon queue capacity for yielded frames
     sandbox:
```

---
Ready for **Part 2/2** (`action.md`, `budget.md`, `assembly.md` for `ctx.quota` SDK contracts, kernel reservation logic, and daemon lease decay sweeper). Confirm to proceed.

### Part 2/2: Runtime SDK Contracts, Engine Specs & Daemon Sweeper

Unified patch exposing `ctx.quota` in the Python SDK, integrating `earmark_id` debiting into the egress gateway, and adding the daemon decaying lease sweeper.

```diff
diff --git a/cans/action.md b/cans/action.md
--- a/cans/action.md
+++ b/cans/action.md
@@ -176,7 +176,7 @@
       - External api methods
-        - ctx.api.call(verb, params, intent) — governed HTTP egress
+        - ctx.api.call(verb, params, intent, earmark_id=None) — governed HTTP egress (draws from earmark if provided)
         - ctx.api.poll_until(verb, params, condition, timeout_s, interval_s) — kernel-managed in-flight polling (1 aggregate op)
         - egress retry — automatic backoff and jitter on 429/503 upstream responses
         - ctx.api.verify(verb, key) — key validation check
+      - Quota brokerage methods
+        - ctx.quota.inspect(verb) — returns total, available, earmarked, and unreserved headroom
+        - ctx.quota.earmark(provider, verb, tokens, ttl_hours, intent) — claims and ring-fences token allocation
+        - ctx.quota.release(earmark_id) — explicitly dissolves unburned reservation back to global pool
       - Blob storage methods
         - ctx.storage.put(name, data, mime) — uploads blob and returns metadata
@@ -202,6 +202,7 @@
         - token refresh — daemon auto-refreshes bearer tokens; stateless CLI refreshes on demand and persists updated token to encrypted vault
         - missing secret fallback — missing secret_ref auto-binds from CAPCLI_SECRET_* before triggering headless exit 3 or ask prompt
         - pre-call quota — deny before network dispatch: see budget.md#Quotas
+        - earmark debit — if earmark_id present, debits tokens_consumed from _budget_earmarks; bypasses global bucket check
         - idempotency — kernel-minted key persisted before egress
         - in-flight wait — poll_until executes sleep in Rust runtime; Python interpreter never busy-waits

diff --git a/cans/budget.md b/cans/budget.md
--- a/cans/budget.md
+++ b/cans/budget.md
@@ -52,10 +52,12 @@
   - Cascade
     - Proactive Brokerage
-      - Hard Earmarks — `_budget_earmarks` locks quota slices pre-execution; invisible to global pool
+      - Hard Earmarks — `_budget_earmarks` locks quota slices pre-execution; ring-fenced from global pool
+      - Headroom arithmetic — unreserved_headroom = tokens_available - tokens_earmarked
       - Priority Classes — Critical, Standard, Background (see artifacts/governance.yaml#priority)
-      - Preemption — Critical tasks physically pause Background tasks if global pool is dry
-      - Decaying Leases — Earmarks carry TTL; daemon tick auto-dissolves unburned tokens to global pool
+      - Preemption — Background tasks yield via exit 6 when unreserved_headroom < background_yield_threshold (15)
+      - Earmark lifecycle — creation via ctx.quota.earmark, debit via ctx.api.call(earmark_id), release via ctx.quota.release
+      - Decaying Leases — Earmarks carry TTL; daemon sweeper auto-dissolves unburned tokens to global pool on expiration
 
     - min() law
       - Child effective limit = min(declared need, governance ceiling, parent_remaining, session_ceiling)

diff --git a/cans/assembly.md b/cans/assembly.md
--- a/cans/assembly.md
+++ b/cans/assembly.md
@@ -127,6 +127,7 @@
       - context_api.py — ctx.api call and verify egress wrappers: see action.md#The-ctx-contract
       - context_api.py — exposes poll_until IPC bridge to kernel runtime
+      - context_quota.py — ctx.quota inspect, earmark, and release SDK wrappers
       - context_storage.py — ctx.storage put, get, and url wrappers: see action.md#The-ctx-contract
       - context_ping.py — ctx.ping notify and ask suspension handlers: see action.md#The-ctx-contract
       - ipc_client.py — streaming JSON-RPC over /run/capcli/kernel.sock: see action.md#Sandbox-execution
@@ -161,6 +162,7 @@
         - catalog.rs — manages OpenAPI YAML specs in apis/: see action.md#Catalog-synchronization
         - quota.rs — dual-window token bucket and rolling window accounting in _api_quota: see budget.md#Quotas
+        - earmark.rs — atomic reservation transactions and earmark balance ledger: see budget.md#Cascade
         - header_parser.rs — extracts RFC headers and parses nested JSON usage payloads: see artifacts/policy.yaml#api
         - egress.rs — reqwest HTTP proxy with secret injection: see agent.md#Egress-injection
         - sim_mock.rs — serves canned fixtures from apis/*.mock.yaml: see space.md#Sim-mode-taxonomy
@@ -197,6 +199,7 @@
         - server.rs — axum HTTP/WS server on 127.0.0.1:4040: see interface.md#Administrative-cockpit-pwa
         - yield_queue.rs — evaluates _suspended_tasks and re-dispatches tasks on quota refill
+        - earmark_sweeper.rs — periodic daemon worker dissolving expired earmarks back to available quota
         - ipc.rs — tokio Unix domain socket listener on kernel.sock: see action.md#Sandbox-execution
         - cron.rs — croner schedule evaluator daemon: see time.md#Schedule-&-maintenance
         - webhook.rs — inbound HMAC signature verification: see action.md#Bindings
```

---
All patches applied. The system now has:
1. **Ring-fenced quota slices** via `_budget_earmarks` and `tokens_earmarked`.
2. **`ctx.quota` SDK primitives** (`inspect`, `earmark`, `release`) for proactive multi-agent planning.
3. **Egress proxy binding** drawing directly from assigned `earmark_id` handles.
4. **Preemption rules** yielding low-priority tasks when unreserved headroom drops below 15.
5. **Decaying lease sweeper** automatically returning expired tokens to the global pool.8
