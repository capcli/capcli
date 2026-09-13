# pwa.architecture.md *(final v1 — governed world browser)*

> **The human-facing harness of capcli: a governed world browser where every object is a kernel artifact, every click is a `--json` call, every interaction is an audit event, and every surface is connected through the causal spine.**

---

## 1. Scope & Convictions

The PWA is the **human control plane**. Claude Code is the agent-facing harness. The PWA is where the human sits. Two harnesses, one gate.

Five convictions:

1. **The PWA is a renderer of governed queries, not a query creator.** The agent defines views. The kernel gates them. The PWA renders them. The human observes and approves. The human never writes SQL, never builds charts, never creates alerts from the PWA.

2. **Every pixel is a kernel artifact.** No data is invented. No chart is hand-drawn. No metric is computed client-side. The PWA renders what `--json` returns. If the kernel doesn't expose it, the PWA doesn't show it.

3. **The causal DAG is the navigation model.** Every node links to its causes and its effects. You never hit a dead end. You drill from session goal → routine → primitive op → SQL → policy rule → rows affected → result hash. The spine is the UX.

4. **Five interactions, no more.** Browse, approve, answer, recover, observe. The human never creates, never edits, never configures, never reasons. Those are the agent's and kernel's jobs.

5. **The PWA is the trust calibrator.** It exists so the human can see exactly what the agent can do, what it cannot, why, and how to verify. Calibrated trust — not blind faith, not paranoia.

---

## 2. Architecture Position

```
┌─────────────────────────────────────────────────────────────────┐
│  HUMAN HARNESS (PWA)                                            │
│  - Renders kernel JSON as drillable trees                       │
│  - Approves / rejects / vetoes                                  │
│  - Observes audit, stats, drift, budget                        │
│  - Triggers recovery                                            │
│  - Answers ping.ask                                             │
│  - Shows trust receipt                                          │
│  - NO reasoning, NO generation, NO agent logic                  │
│  - NO LLM, NO inference, NO summarization                      │
└──────────────────┬──────────────────────────────────────────────┘
                   │ @capcli/sdk (JSON + exit codes)
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  CAPCLI KERNEL                                                  │
│  - Gates, enforces, audits                                      │
│  - Returns { exit, json, text }                                 │
│  - Never reasons, never infers                                  │
│  - 9 nouns, exit codes as law                                   │
└──────────────────┬──────────────────────────────────────────────┘
                   │ CLI (JSON + exit codes)
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  AGENT HARNESS (Claude Code / Codex / Hermes / OpenClaw)        │
│  - Reasons, proposes, executes                                  │
│  - Writes routines, drafts schema.yaml                          │
│  - Queries audit mirror                                         │
│  - Proposes consolidations, activations                         │
│  - Learns from denials                                          │
└─────────────────────────────────────────────────────────────────┘
```

The PWA sits at the **top**. It is the thinnest layer. It renders what the kernel already computed. It approves what the kernel already gated. It recovers what the kernel already snapshotted.

### What the PWA is NOT

| Temptation | Why it's refused |
|---|---|
| A component of capcli | The PWA is a **client** of the kernel. It lives outside the workspace. |
| A replacement for the CLI | The CLI is the machine contract. The PWA calls the SDK. It's a renderer, not a replacement. |
| A second kernel | The PWA never gates, never enforces, never audits independently. It delegates everything. |
| A harness for agents | Agents use CLI. The PWA is for humans. Period. |
| An interactive terminal | No `[Y/n]`. No wizards. No prompts. The kernel returns exit codes; the PWA renders approval cards. |

---

## 3. The SDK Contract

The PWA communicates exclusively through `@capcli/sdk`:

```js
import { createKernel } from '@capcli/sdk'

const kernel = createKernel({
  workspace: './workspace',
  brand: {
    name: 'Acme Agent',
    cli: 'acme',
    nouns: { run: 'exec', db: 'store', routine: 'flow' }
  }
})
```

All methods return `{ exit, json, text }`:

| SDK method | PWA surface |
|---|---|
| `kernel.run(capability, opts)` | Approval execution |
| `kernel.db.query(sql, params)` | World browsing (Layer 1) |
| `kernel.db.exec(sql, params, intent)` | Governed writes (human-initiated) |
| `kernel.routine.prove(name, params, env)` | Routine evidence display |
| `kernel.search(query, filters)` | Capability discovery |
| `kernel.inspect(capability)` | Cost envelope rendering |
| `kernel.audit.tail(filters)` | Live audit stream (Layer 4) |
| `kernel.audit.trace(opId)` | Causal DAG drill-down |

**Exit codes drive UI state:**

| Exit | PWA behavior |
|---|---|
| `0` | Green. Render result. |
| `2` | Red card. Policy denied. Show rule, fix suggestion. |
| `3` | Yellow card. Validation failed. Show what's wrong. |
| `4` | Orange card. Runtime error. Show trace. |
| `5` | Black card. Audit write failed. Nothing ran. Critical. |

---

## 4. The Ten Layers

The PWA is organized as ten drillable layers. Each layer is a tree. Each node links to related nodes in other layers. The whole PWA is a **connected graph rendered as nested trees**.

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 10: IDENTITY                                             │
│  principals → agents → sessions → skills                        │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 9: LEARNING                                              │
│  search gaps → consolidation signals → decay → sweep reports    │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 8: RECOVERY                                              │
│  snapshots → restores → rollbacks → git history → hash chain    │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 7: APPROVAL                                              │
│  promotion queues → activations → migrations → merges → asks    │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 6: ENVIRONMENT                                           │
│  dev → sim → prod → worktrees → overlays → drift → merge state  │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 5: BUDGET                                                │
│  frames → cascades → consumption → exhaustion → session pools   │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 4: AUDIT                                                 │
│  events → causal DAGs → forensics → denials → fingerprints      │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 3: GOVERNANCE                                            │
│  policy rules → governance limits → schema DDL → trust overlays │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 2: CAPABILITY                                            │
│  routines → API verbs → views → binds → endpoints → keys        │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 1: WORLD                                                 │
│  tables → rows → columns → relations → CHECK constraints        │
└─────────────────────────────────────────────────────────────────┘
```

### Layer 1: World (Prisma Studio analog, governed)

**SDK calls:** `kernel.db.query()`, `kernel.db.exec()`, `kernel.inspect()`

```
workspace.db
│
├── customers
│   ├── cols: id, email!, name, phone~, tier=standard, metadata, created_at~
│   ├── chk: tier IN (...), email LIKE '%@%'
│   ├── rel: → orders.customer_id, → subscriptions.customer_id
│   ├── seed: 0 rows
│   ├── [Browse Rows] ← kernel.db.query("SELECT ... FROM customers LIMIT 50")
│   │   ├── filter: tier = premium, created_at > 7d
│   │   ├── sort: created_at desc
│   │   ├── masked: phone → ████, metadata.ssn → ████
│   │   └── click row → [History] → audit events touching this row
│   └── [Schema] ← kernel.inspect("customers")
│       ├── DDL preview
│       ├── CHECK constraints (clickable → enforced values)
│       └── provenance: prov: true → created_by, modified_by visible
│
├── orders
│   ├── cols: id, ref!, customer_id→customers, status=pending, total_cents, ...
│   ├── chk: total_cents >= 0, discount_cents <= total_cents
│   ├── rel: → customer, → items, → payments
│   ├── trig: validate_total (before insert)
│   ├── [Browse Rows]
│   ├── [Views that expose this table]
│   │   ├── pending_orders → rendered as filtered table
│   │   └── orders_by_status → rendered as grouped table
│   └── [Ops touching this table] ← kernel.audit.tail({capability: "db.exec"})
│       ├── last 24h: 47 reads, 12 writes, 2 denials
│       └── click denial → Layer 4 (audit forensics)
│
├── inventory
│   ├── [Low Stock Alert Card] ← view: low_stock_alerts
│   │   ├── SKU-042: 3 left (reorder: 10) ⚠
│   │   ├── SKU-117: 8 left (reorder: 15) ⚠
│   │   └── SKU-203: 5 left (reorder: 20) ⚠
│   └── [Browse Rows]
│
├── payments
│   ├── raw_response: mask=true → always ████
│   ├── [Browse Rows] (masked columns rendered as locked cells)
│   └── click locked cell → "masked by policy. principal: user:alice."
│
├── views/
│   ├── pending_orders → [Render as Table] [Render as Chart]
│   ├── low_stock_alerts → [Render as Alert Cards]
│   ├── customer_lifetime_value → [Render as Table] (scoped: principal)
│   └── click any view → shows SQL, exposes list, scoped flag
│
└── system/ (read-only badge)
    ├── _audit → [Browse] [Filter by event/capability/outcome]
    ├── _api_quota → [Live Quota Cards]
    ├── _api_catalog → [Verb Browser]
    ├── _budget_frames → [Frame Tree]
    ├── secrets → name visible, value: ████ (always)
    └── agents → [Identity Cards]
```

**Interaction model:**
- Browse = `kernel.db.query()` rendered as a table
- Filter/sort = params appended to the query
- Edit cell = generates `kernel.db.exec()` form → kernel gates → audit records
- Click row → shows audit history for that row
- Click column header → shows policy rules governing that column
- System tables = read-only badge, no edit button

### Layer 2: Capability (the registry browser)

**SDK calls:** `kernel.search()`, `kernel.inspect()`, `kernel.audit.tail()`

```
capabilities/
│
├── routines/ (47 active, 3 draft, 2 retired)
│   │
│   ├── refund_and_archive@17
│   │   ├── trust: reviewed ← trust ladder visualization
│   │   ├── env journey: dev ✓ → sim ✓ → prod ✓ (merged)
│   │   ├── manifest (declared):
│   │   │   1. api.call stripe.get_charge      [sandbox] ✓
│   │   │   2. db.query entities (read)         ✓
│   │   │   3. api.call stripe.refund_charge   [sandbox] ✓
│   │   │   4. db.txn [2× db.exec]             ✓
│   │   ├── fingerprint (actual, last 31 runs):
│   │   │   matched: 31/31 (1.0)
│   │   │   drift events: 0
│   │   │   [click → diff view: manifest vs fingerprint]
│   │   ├── stats:
│   │   │   runs: 31, success: 0.97, p95: 640ms
│   │   │   [click → per-leaf cost attribution]
│   │   ├── budget frames: [click → Layer 5]
│   │   ├── versions: [17, 16, 15, ...] → click → diff
│   │   ├── promoted_by: user:alice, via: queue_batch_003
│   │   ├── [Promote] → Layer 7 (approval)
│   │   ├── [Rollback] → Layer 8 (recovery)
│   │   └── [Retire] → confirmation + provenance pointer
│   │
│   ├── archive_old_orders@3
│   │   ├── trust: draft
│   │   ├── sim gaps: 1 verb (gov.file_tax_return) prod-only
│   │   │   └── "first 3 prod calls need human approval"
│   │   └── prove status: 2/3 primitives matched
│   │
│   └── [retired] find_orders_by_status@5
│       ├── consolidated_from: [orders_by_status@2]
│       └── provenance pointer → original routine
│
├── apis/
│   ├── stripe (400 verbs)
│   │   ├── active (12) → verb cards
│   │   ├── dormant (385) → search, filter, browse
│   │   ├── deprecated (2) → loud badge
│   │   └── sync history → diffs, spec_hash changes
│   │
│   ├── gov (3 verbs)
│   │   └── file_tax_return [prod-only] trust:draft
│   │       ├── sim_mode: prod-only → "cannot prove in sim"
│   │       ├── first_prod_calls_remaining: 3
│   │       └── [Approve First Prod Call] → Layer 7
│   │
│   └── hardware (8 verbs)
│       └── notify_device [mock]
│           └── fixture: apis/hardware.mock.yaml → [Browse Fixture]
│
├── views/ (from schema.yaml)
│   ├── pending_orders → [Render] [Show SQL] [Show Exposes]
│   ├── low_stock_alerts → [Render as Alert Cards]
│   └── customer_lifetime_value → [Render] (scoped: principal)
│
├── binds/
│   ├── cron: weekly_cleanup @ "0 3 * * 0" → [Pause] [Resume] [Remove]
│   ├── webhook: stripe.charge.refunded → [Inspect Payload Schema]
│   └── endpoint: order_status@12 → [Health Check] [API Keys] [Request Log]
│
└── search analytics/
    ├── top queries: ["refund" ×47, "invoice" ×20]
    ├── gaps: "invoice" searched 20×, never invoked → GAP
    └── denial patterns: require_where: 14 denials
```

### Layer 3: Governance (the physics viewer)

**SDK calls:** `kernel.inspect()`, `kernel.audit.tail({event: "governance.deny"})`

```
governance/
│
├── policy.yaml (v4) → rendered as interactive tree
│   ├── authorizer.tables → click table → see what's allowed/denied
│   ├── query.update_delete → require_where: true
│   │   └── [click → shows all denials for this rule]
│   ├── trust overlays → draft/reviewed/pinned caps
│   ├── budget cascade → inheritance: min
│   └── fail_closed contract → refuse_boot conditions
│
├── governance.yaml (v7) → rendered as limits with live usage
│   ├── registry: 47/300 routines used → progress bar
│   ├── routine_shape: max LOC 150 → largest: 142
│   ├── execution: max_ops 50 → budget frame history
│   ├── overrides: 3 active → git commits
│   └── maintenance: consolidation Sun 03:00, next in 2d
│
├── schema.yaml (v12) → rendered as interactive ERD
│   ├── tables as nodes, rel: as edges
│   ├── click table → columns, types, CHECK, triggers, seed
│   ├── click edge → "orders.customer_id → customers.id"
│   └── [Diff vs live DB] → drift highlighted
│
├── system-schema.yaml (v3) → read-only badge
│   └── "kernel-owned. agent-readable. never agent-editable."
│
└── quad-lock status
    ├── schema: v12 ✓
    ├── system-schema: v3 ✓
    ├── policy: v4 ✓
    ├── governance: v7 ✓
    └── [Any mismatch → red banner, refuse boot warning]
```

### Layer 4: Audit (the spine)

**SDK calls:** `kernel.audit.tail()`, `kernel.audit.trace()`, `kernel.db.query()` (audit mirror views)

```
audit/
│
├── live tail ← kernel.audit.tail({follow: true})
│   ├── op_000041  db.exec  UPDATE orders  ✓  4ms  [prod]
│   ├── op_000042  api.call  stripe.refund  ✗  policy-denied
│   ├── op_000043  routine.run  refund_archive@17  ✓  640ms  [sim]
│   └── op_000044  budget.exhausted  frame_005  ✗
│
├── click any event → full event card
│   ├── event, ts, env, stage, agent, session, principal
│   ├── capability, intent, intent_chain (clickable breadcrumbs)
│   ├── policy_decision: allow | denied
│   ├── rules_matched: [require_where, require_limit]
│   ├── rows_affected, result_hash, duration_ms
│   ├── sim_mode: sandbox | mock | dry-run | skip | prod-only
│   ├── budget_frame: frame_003 → [click → Layer 5]
│   ├── caused_by: op_000038 → [click → parent event]
│   └── [Trace Full DAG] → visual causal graph
│
├── denial forensics ← kernel.audit.trace(opId, {explain: true})
│   ├── Decision: denied
│   ├── Layer: AST gate (Layer 2)
│   ├── Rule: require_where + require_limit
│   ├── Fix: "UPDATE orders SET status = :status WHERE id = :id LIMIT 1"
│   └── intent_quality: low
│
├── fingerprints ← routine_fingerprints view
│   ├── refund_and_archive@17: match_rate 1.0, drift 0
│   └── archive_old_orders@3: match_rate 0.67, gap: prod-only verb
│
├── primitive cost ← primitive_cost view
│   ├── stripe.refund_charge: avg 280ms, $0.35/call, 97% success
│   └── db.exec entities: avg 12ms, free, 100% success
│
├── shared subsequences ← shared_subsequences view
│   └── [db.query orders → api.call stripe.get_charge]: 47 occurrences
│       └── [Propose Consolidation]
│
└── search log ← capability.search events
    ├── "refund" × 47 → invoked 44× → healthy
    ├── "invoice" × 20 → invoked 0× → GAP
    └── "archive" × 12 → invoked 12× → healthy
```

### Layer 5: Budget (the cascade visualizer)

**SDK calls:** `kernel.db.query()` (`_budget_frames`), `kernel.inspect()`

```
budget/
│
├── session ses_a9 (active)
│   ├── declared: ops ∞, duration ∞, spend $50
│   ├── consumed: ops 12, duration 8.2s, spend $3.40
│   │
│   ├── frame_002 (refund_and_archive@17)
│   │   ├── declared: ops 50, duration 300s
│   │   ├── inherited: min(50, ∞) = 50
│   │   ├── consumed: ops 4, duration 640ms, spend $0.80
│   │   └── status: active
│   │
│   ├── frame_003 (archive_old_orders@3)
│   │   ├── consumed: ops 20, duration 42s
│   │   ├── status: EXHAUSTED
│   │   └── denial card:
│   │       "routine B (frame_004) exhausted ops: 20/20"
│   │       "session remaining: 488 ops"
│   │
│   └── frame_004 (notify_team@1)
│       ├── consumed: ops 1, duration 200ms
│       └── status: active
│
├── session spend pool
│   ├── total: $50.00, consumed: $3.40, remaining: $46.60
│   ├── per-provider: stripe $2.80, gov $0.00, hw $0.60
│   └── [time-series spend chart]
│
├── rate limits
│   ├── writes_per_minute: 12/60 → gauge
│   └── capability_calls_per_minute: 45/300 → gauge
│
└── budget denial history
    └── [click → full trace for each denial]
```

### Layer 6: Environment (the world switcher)

**SDK calls:** `kernel.inspect()`, `kernel.audit.tail({env: X})`

```
environments/
│
├── prod ← [active] red badge
│   ├── schema: v12, policy: v4, governance: v7
│   ├── quad-lock: ✓
│   ├── routines: 47 active, 3 draft (writes denied)
│   ├── drift: none
│   ├── last backup: 2 min ago → [Verify Hash]
│   └── [Diff vs sim]
│
├── sim
│   ├── seeded from: prod @ snap_2026_09_10
│   ├── masking: enforced
│   ├── stale: 2 days → [nag: re-seed from prod]
│   ├── API overlays: apis/*.sim.yaml active
│   └── notify routes to: #sim-notifications
│
├── dev
│   ├── schema drift vs prod: +1 column (discount_cents)
│   ├── unmerged routines: 2 → "merge to prod?"
│   └── trust overlay: draft max_rows 100 (looser)
│
└── [New Environment] → env new --seed prod → masking enforced
```

### Layer 7: Approval (the authority surface)

**SDK calls:** `kernel.run()`, `kernel.inspect()`, `kernel.audit.tail({event: "routine.queued"})`

```
approvals/
│
├── pending promotions (queue)
│   ├── refund_and_archive@18 → reviewed
│   │   ├── evidence: 12 sim runs, 100% success, manifest matched
│   │   ├── manifest diff vs v17: +1 api.call (new verb)
│   │   ├── sim gaps: none
│   │   ├── [Approve] [Reject + reason]
│   │   └── SLA: 48h, 12h remaining
│   │
│   └── archive_old_orders@4 → reviewed
│       ├── sim gaps: 1 verb (gov.file_tax_return) prod-only
│       └── "first 3 prod calls need human approval"
│
├── pending activations
│   ├── stripe.create_dispute → activate
│   │   ├── governance: 12/50 active slots used
│   │   └── [Approve] [Reject]
│   │
│   └── gov.file_tax_return → first prod call approval
│       ├── prod_call_number: 1 of 3
│       ├── approval_window: 24h, 18h remaining
│       └── [Approve This Call] [Deny]
│
├── pending migrations
│   ├── schema v12 → v13: add discount_cents to orders
│   │   ├── DDL: ALTER TABLE orders ADD COLUMN ...
│   │   ├── snapshot: snap_migration_004
│   │   ├── [Approve] [Reject] [Preview DDL] [Preview Rollback]
│   │
│   └── policy v4 → v5: add new rate limit
│       └── [Show Affected Routines]
│
├── pending merges (consolidation)
│   ├── merge: orders_by_status@2 + find_orders@3 → orders_query@1
│   │   ├── fingerprint similarity: 0.92
│   │   └── [Approve Merge] [Reject] [Fork Instead]
│   │
│   └── extract: common sub-routine from 5 routines
│       └── [Approve Extraction] [Reject]
│
├── pending asks (ctx.ping.ask)
│   ├── ask_007: "Should I refund ORD-8842? Amount: $42.00"
│   │   ├── options: [approve, reject, modify_amount]
│   │   ├── timeout: 60 min, 23 min remaining
│   │   └── [Answer] → kernel resumes
│   │
│   └── ask_008: "Low stock on SKU-042. Reorder 50 units?"
│       └── [Answer]
│
└── approval history
    ├── approved: 47 promotions, 12 activations, 8 migrations
    ├── rejected: 3 promotions (reason: insufficient evidence)
    └── vetoed: 1 (within 1h veto window)
```

### Layer 8: Recovery (the undo console)

**SDK calls:** `kernel.db.query()`, `kernel.run()`, `kernel.audit.tail()`

```
recovery/
│
├── snapshots
│   ├── snap_onboarding_001 → 2026-09-01 → [Restore] [Inspect]
│   ├── snap_migration_004 → 2026-09-10 → [Restore] [Inspect]
│   └── snap_auto_2026_09_12 → 15 min ago → [Restore] [Inspect]
│
├── git recovery points ← sys recover --list
│   ├── abc123 → 2h ago → schema v12, 47 routines → [Recover]
│   ├── def456 → 6h ago → schema v11, 45 routines → [Recover]
│   └── ghi789 → 1d ago → schema v11, 44 routines → [Recover]
│
├── routine rollbacks
│   ├── refund_and_archive: v17 → v16 → v15 → ...
│   │   └── [Rollback to v16] → confirmation → audit event
│   └── archive_old_orders: v3 → v2 → v1
│
├── object storage (S3/GCS/B2)
│   ├── last push: 15 min ago
│   ├── [Verify Last Backup] → download + hash compare
│   └── hash chain: verified ✓
│
├── hash chain verification
│   ├── last verified: 2026-09-12 04:00
│   ├── status: ✓ intact
│   └── [Verify Now]
│
└── worst-case recovery
    ├── "harness wiped everything"
    ├── git clone <remote> + capcli sys recover abc123
    └── [Simulate Recovery] → dry-run in temp env
```

### Layer 9: Learning (the growth observer)

**SDK calls:** `kernel.search()`, `kernel.audit.tail()`, `kernel.db.query()` (audit mirror views)

```
learning/
│
├── search gaps (last 7d)
│   ├── "invoice" searched 20×, never invoked → GAP
│   │   └── [Propose Activation] or [Propose Routine]
│   └── "refund" searched 47×, invoked 44× → healthy
│
├── consolidation signals
│   ├── fingerprint similarity > 0.90: 3 clusters
│   ├── shared_subsequences: 5 common n-grams
│   └── next sweep: Sun 03:00 (in 2d)
│
├── decay candidates
│   ├── dead_after_days: 30
│   │   └── find_old_records@2: last used 34d ago → [Retire] [Keep]
│   ├── fail_threshold: 0.7
│   │   └── batch_notify@4: success 0.62 → [Rollback] [Investigate]
│   └── stale_sim: sim data 16d old → [Re-seed from prod]
│
├── denial patterns
│   ├── require_where: 14 denials this week
│   ├── spend.per_day_usd: 3 denials
│   └── intent_quality: low: 7 events
│
├── routine formation pipeline
│   ├── raw ops → repeated patterns: 3 candidates
│   │   └── [db.query orders → api.call stripe.get_charge]: 47×
│   └── [Propose Routine] → harness drafts → kernel gates → human approves
│
└── trust receipt ← sys doctor --report
    ├── ✓ 23 operations audited
    ├── ✓ 2 denied before execution (explained)
    ├── ✓ 0 unaudited writes
    ├── ✓ 1 routine proven in sim
    ├── ✓ 1 routine promoted to reviewed
    ├── ✓ 0 secrets exposed
    ├── ✓ recovery tested successfully
    └── [Share Trust Card] → copyable artifact
```

### Layer 10: Identity (who is acting)

**SDK calls:** `kernel.inspect()`, `kernel.audit.tail()`

```
identity/
│
├── principals
│   ├── user:alice → [active]
│   │   ├── agents: agt_7f3k, agt_9m2p
│   │   ├── sessions today: 4
│   │   ├── approvals granted: 12
│   │   └── [Revoke All Agents]
│   │
│   └── partner:stripe → [active]
│       ├── API keys: 2 (1 expiring in 12d)
│       └── [Rotate Key] [Revoke]
│
├── agents
│   ├── agt_7f3k (Claude Code)
│   │   ├── status: active
│   │   ├── routines authored: 12
│   │   ├── denials this week: 3
│   │   ├── [Revoke] → instant, no grace period
│   │   └── skill_origin: refund-workflow
│   │
│   └── agt_9m2p (Codex)
│       └── routines authored: 3
│
├── kernel principals (unattended executors)
│   ├── capcli-cron → schedules
│   ├── capcli-watch → webhooks
│   └── capcli-serve → endpoints
│
└── skill origin propagation
    ├── enabled: true
    ├── format: lowercase-hyphens
    └── audit_field: triggered_by_skill
```

---

## 5. Navigation Model — Everything Connects

The PWA is not ten disconnected pages. It is **one connected graph**. Every node links to related nodes in other layers. The causal DAG is the navigation model.

```
Click a TABLE ROW (Layer 1)
  → see AUDIT EVENTS that touched it (Layer 4)
    → click an EVENT → see the ROUTINE that called it (Layer 2)
      → click the ROUTINE → see its MANIFEST (Layer 2)
        → click a MANIFEST ENTRY → see the API VERB (Layer 2)
          → click the VERB → see its QUOTA (Layer 1 system)
            → click the QUOTA → see the BUDGET FRAME (Layer 5)
              → click the FRAME → see the SESSION (Layer 10)
                → click the SESSION → see the AGENT (Layer 10)
                  → click the AGENT → see the PRINCIPAL (Layer 10)
```

Every click is a `--json` call. Every render is a kernel artifact. No data is invented. No chart is hand-drawn.

**Cross-layer linking rules:**

| From | To | Trigger |
|---|---|---|
| Audit event → Routine | `caused_by` / `routine` field | Click event |
| Routine → Budget frame | `frame_id` in audit event | Click routine |
| Budget frame → Session | `session` field | Click frame |
| Session → Agent | `agent` field | Click session |
| Agent → Principal | `principal` field | Click agent |
| Table row → Audit events | `capability` + `target` match | Click row |
| API verb → Quota | `_api_quota` lookup | Click verb |
| Denial → Policy rule | `rules_matched` field | Click denial |
| Policy rule → All denials | Audit query filter | Click rule |
| View → Exposed tables | `exposes` field | Click view |
| Migration → Snapshot | `snapshot` field | Click migration |
| Routine version → Code hash | `code_hash` field | Click version |

---

## 6. Interaction Patterns (exactly five)

| Pattern | What it does | Example |
|---|---|---|
| **Browse** | Read-only drill-down | Click table → rows → row → history |
| **Approve** | Exercise human authority | Promotion queue → evidence → approve/reject |
| **Answer** | Respond to kernel questions | ping.ask → choose option → kernel resumes |
| **Recover** | Undo, restore, rollback | Snapshot → restore. Routine → rollback. |
| **Observe** | Watch live state | Audit tail, quota gauges, budget frames |

**No other interactions.** No "create." No "edit." No "configure." The agent creates. The kernel gates. The PWA approves, observes, and recovers.

---

## 7. Rendering Model

Every kernel `--json` output maps to a UI component:

| JSON shape | Renders as |
|---|---|
| Array of objects | Table with filter/sort |
| Single object with nested fields | Card with expandable sections |
| Object with `outcome: denied` | Red denial card with fix suggestion |
| Object with `caused_by` | Clickable breadcrumb → parent event |
| Array with `ts` field | Time-series chart |
| Object with `remaining` / `limit` | Gauge / progress bar |
| Object with `sim_mode` | Badge: sandbox / mock / dry-run / skip / prod-only |
| Object with `trust` | Trust ladder: draft → reviewed → pinned |
| Object with `env` | Environment badge: dev / sim / prod (prod in red) |
| Object with `manifest` vs `fingerprint` | Side-by-side diff view |
| Object with `chk` constraints | Constraint list with enforced values |
| Object with `mask=true` | Locked cell: ████ |
| Object with `prov: true` | Provenance footer: created_by, modified_by |
| Object with `exit: 2` | Red banner + rule citation + fix |
| Object with `exit: 5` | Black banner + "audit write failed. nothing ran." |
| Object with `budget_status.can_invoke_now: false` | Orange banner + blocking reasons |

---

## 8. Real-Time Model

| Data | Update mechanism | Frequency |
|---|---|---|
| Audit tail | WebSocket / SSE from `kernel.audit.tail({follow: true})` | Real-time |
| API quota | Poll `_api_quota` every 30s | Near-real-time |
| Budget frames | Push on frame push/pop events | Real-time |
| Routine stats | Poll `routine stats` every 5m | Periodic |
| Search gaps | Poll `search gaps` every 1h | Periodic |
| Environment drift | Poll `env doctor` every 15m | Periodic |
| Hash chain | Daily verify (governance schedule) | Scheduled |
| Backup status | Poll `sys doctor` every 15m | Periodic |
| Approval queues | Poll `routine pending` every 2m | Periodic |
| Pending asks | Poll `ping list --pending` every 30s | Near-real-time |

---

## 9. Mini ERP — Business Views

The PWA renders **governed views** as dashboard cards. Views are defined in `schema.yaml` by the agent, gated by the kernel, approved by the human. The PWA renders them.

```
┌─────────────────────────────────────────────────────────────┐
│  MINI ERP — Orders & Inventory                              │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────┐         │
│  │ Orders Today │  │ Revenue 7d  │  │ Low Stock  │         │
│  │     47       │  │  $12,340    │  │  3 SKUs    │         │
│  │  ↑ 12%       │  │  ↑ 8%       │  │  ⚠ alert   │         │
│  └─────────────┘  └─────────────┘  └────────────┘         │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Orders by Status (view: orders_by_status)            │   │
│  │ pending: 12  │ fulfilled: 34 │ refunded: 1           │   │
│  │ [filter: date range ▼] [filter: customer ▼]          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Inventory (view: low_stock_alerts)                    │   │
│  │ SKU-042: 3 left (reorder: 10) ⚠                     │   │
│  │ SKU-117: 8 left (reorder: 15) ⚠                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Routine Health (audit mirror)                         │   │
│  │ refund_and_archive@17: 97% success, 640ms            │   │
│  │ weekly_cleanup@1: EXHAUSTED (ops 20/20) ⚠            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Budget (session ses_a9)                               │   │
│  │ ops: 12/50 │ duration: 8s/300s │ $3.40/$50           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Rules:**
- Every card is a governed view or audit query. No ad-hoc SQL.
- Charts render from views. The view defines the shape.
- Filters are params on `kernel.db.query()`.
- Time-series data comes from audit mirror GROUP BY.
- Alerts are routines: `bind cron → check → ping notify`. The PWA shows alert status. It doesn't create them.

---

## 10. Onboarding Integration

The PWA renders the onboarding journey from `onboarding.architecture.md`:

| Onboarding stage | PWA rendering |
|---|---|
| Stage 0: Install & verify | `sys doctor` output as a health checklist |
| Stage 1: Intent capture | Harness renders. PWA shows the approved result. |
| Stage 2: Minimal world proposal | `rule apply --dry-run` as a preview card |
| Stage 3: First safe read | `db query` result as a table |
| Stage 4: Designed denial | Exit 2 rendered as a red teaching card |
| Stage 5: First governed write | Exit 0 + audit trace as a green confirmation |
| Stage 6: Recovery proof | Snapshot → restore as a two-step flow |
| Stage 7: Capability discovery | `search` + `inspect` + `run` as a three-step wizard |
| Stage 8: Routine formation | Manifest + fingerprint as a side-by-side |
| Stage 9: Promotion | Evidence block + approve button |
| Stage 10: Trust receipt | `sys doctor --report` as a shareable card |

The PWA does NOT generate onboarding content. The harness generates it from intent. The PWA renders the results.

---

## 11. White-Label & SDK

The PWA uses `@capcli/sdk` brand config:

```js
const kernel = createKernel({
  workspace: './workspace',
  brand: {
    name: 'Acme Agent',
    cli: 'acme',
    tagline: 'Your governed workspace',
    nouns: { run: 'exec', db: 'store', routine: 'flow' }
  }
})
```

The PWA renders branded nouns throughout:
- "Routines" becomes "Flows"
- "db" becomes "store"
- "run" becomes "exec"

What never changes in the PWA:
- Exit codes (0/2/3/4/5)
- JSON output contract
- Audit event format
- System table names
- `[env]` output prefix
- Causal DAG structure
- Approval flow mechanics

---

## 12. Technology Stack

| Layer | Choice | Reason |
|---|---|---|
| Framework | SvelteKit / SolidStart | Reactive, small bundle, SSR optional |
| State | Kernel JSON as single source | No client-side data model |
| Real-time | WebSocket / SSE | Audit tail, quota updates |
| Offline | Service worker cache | Last-known state cached |
| Auth | Session token from kernel | `--as <principal>` mapped to session |
| Rendering | Component library per JSON shape | Table, card, gauge, DAG, diff |
| Charts | Deterministic from audit data | No chart builder. Views define shape. |
| PWA | Manifest + service worker | Installable, offline-capable |
| No LLM | Zero inference | The PWA never reasons |

---

## 13. Anti-Decisions

| Temptation | Why it's refused |
|---|---|
| SQL editor | `db query` is the read path. The PWA renders results. Ad-hoc exploration is the agent's job. |
| Chart builder | Charts render from governed views. The agent defines views. The PWA doesn't invent queries. |
| Alert builder UI | Alerts are routines: `bind cron → check → ping notify`. The PWA shows alert status. |
| Routine editor | Routines are Python files. The harness writes them. The PWA approves them. |
| Schema editor | schema.yaml is agent-authored. The PWA shows the ERD. The agent edits. |
| Policy editor | policy.yaml is human-edited in files. The PWA shows the rules. No GUI edit path. |
| Agent reasoning | The PWA never infers, never generates, never summarizes with LLM. |
| Interactive prompts | No `[Y/n]`. No wizards. The kernel returns exit codes. The PWA renders approval cards. |
| Direct SQLite access | All reads through `kernel.db.query()`. All writes through `kernel.db.exec()`. The kernel is the only door. |
| Dashboard builder | No drag-drop widgets. Views are governed. The PWA renders them. Period. |
| trigger.dev task runner | The PWA doesn't trigger routines. The agent triggers. The PWA approves and observes. |
| Metabase ad-hoc queries | No saved questions. No question builder. Views are schema.yaml artifacts. |
| Grafana alert rules | Alerts are routines + ping. Not PWA features. |
| Multi-user collaboration | The PWA is single-principal. One human, one view. No shared dashboards. |
| Mobile native app | PWA. Service worker. Offline cache. No native app. |
| Write-path for config | No `config set` equivalent. Config is files + git + review. |
| `--force` buttons | Exceptions are governance overrides, never UI flags. |
| Bulk approval without evidence | Every approval shows evidence block. No "approve all" without review. |
| Silent recovery | Every restore/rollback is an audit event. The PWA shows the event after. |
| PWA-generated schema | The harness authors. The PWA renders. Never the reverse. |
| PWA as audit source | The PWA never writes to `_audit`. It reads. The kernel writes. |
| Real-time editing | No collaborative editing. The PWA is observe + approve. Not a shared editor. |

---

## 14. Invariants

1. Every PWA interaction is a kernel SDK call. No client-side computation of governance state.
2. Every approval is an audit event. The PWA records who approved, when, and what evidence was shown.
3. Every denial rendered in the PWA cites the exact rule, layer, and fix. No mysterious errors.
4. The PWA never writes to system tables. It reads `_audit`, `_api_quota`, `_budget_frames`. The kernel writes them.
5. The PWA never creates routines, schemas, or policies. It approves them. Creation is the agent's job.
6. Every view rendered in the PWA is a governed view from `schema.yaml`. No ad-hoc queries.
7. The causal DAG is navigable from any node to any ancestor. No dead ends.
8. Masked columns are always masked. The PWA never reveals `mask=true` values.
9. Exit codes drive UI state. The PWA never interprets stdout text. It branches on exit codes.
10. The PWA is single-principal. One human, one session, one view. No multi-tenant.
11. Recovery operations require confirmation. No one-click destructive actions.
12. The PWA renders `--json` output. It never parses human-readable text.
13. Real-time data comes from the kernel. The PWA never caches stale state past its TTL.
14. The PWA is a client, not a component. It lives outside the workspace. It communicates via SDK.
15. The quad-lock status is always visible. Any mismatch renders as a red banner.

---

## 15. The Comparison Table (what it is, what it isn't)

| Tool | What it does | capcli PWA equivalent |
|---|---|---|
| Prisma Studio | Browse DB tables | Layer 1: World (governed reads) |
| Datadog APM | Trace drill-down | Layer 4: Audit (causal DAG) |
| GitHub PR review | Approve/reject gates | Layer 7: Approval |
| AWS IAM console | Who can do what | Layer 3: Governance + Layer 10: Identity |
| Git history viewer | Recovery, rollback | Layer 8: Recovery |
| Metabase | Ad-hoc queries, charts | **NOT this.** Views are governed. No ad-hoc. |
| trigger.dev | Task runner dashboard | **NOT this.** The PWA doesn't trigger. |
| Grafana | Alert rules, dashboards | **NOT this.** Alerts are routines. |
| pgAdmin | DB admin tool | **NOT this.** No direct DB access. |
| Airtable | Spreadsheet-like UI | **NOT this.** No free-form editing. |
| Retool | Internal tool builder | **NOT this.** No custom forms. |

The capcli PWA is: **Prisma Studio × Datadog APM × GitHub PR review × AWS IAM × Git history viewer**, scoped to one SQLite workspace, one audit spine, one gate.

---

## The One-Liner

> **The capcli PWA is a governed world browser: ten layers of drillable trees connected by the causal DAG, rendered from kernel JSON, interacted with through exactly five patterns (browse, approve, answer, recover, observe), where every click is a `--json` call, every render is a kernel artifact, every approval is an audit event, and the human never creates, never edits, never reasons — they see, they decide, they undo. The agent builds. The kernel gates. The PWA shows. The human decides.**