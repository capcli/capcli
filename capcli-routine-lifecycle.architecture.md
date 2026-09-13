# capcli-routine-lifecycle.architecture.md *(final v2 — primitive-aware)*

> How routines are born, proven at the leaf level, promoted by evidence, and retired — **and how every atomic primitive inside them rides the environment axis.**

---

## 1. Scope

This document defines the routine lifecycle: the states a routine passes through, the gates at each transition, and how the **atomic primitives** (individual `db.exec`, `api.call` leaf ops) leverage environments so a routine can be *proven* before it's *trusted*.

Companions: `capcli-routine.architecture.md` (anatomy & execution), `capcli-env.architecture.md` (worlds). API verbs follow the same lifecycle (dormant → activate → prove → ship → live → retire) with the same trust ladder and human gates. See `architecture.md` §11.

---

## 2. The Stage Map

```
        draft ──> prove ──> ship ──> live ──> monitor
         │         │           │         │         │
       scaffold   AST+policy  human/CI   pinned   stats+decay
       (harness   + manifest  gate      service     │
        fs)       extraction  sim/dev               ▼
                                                     sweep / rollback / retire
```

| Stage | What happens | Who gates |
|---|---|---|
| **draft** | File scaffolded in `routines/` via harness native fs | nobody (creation is ungated) |
| **prove** | AST + policy + governance shape + **primitive manifest extraction**, zero execution, then real execution at draft trust with sample params; **fingerprint vs manifest proof** | kernel (env-scoped) |
| **ship** | draft → reviewed → pinned | **human/CI** — never the agent |
| **live** | Registered capability; callable via `capcli run` | policy gate per call |
| **monitor** | Stats, success rate, usage tracked continuously | kernel (evidence only) |
| **sweep** | Merge/dedupe proposals from maintenance cycle | human |
| **rollback** | Revert to prior version | agent may propose; pinned requires human |
| **retire** | Removed from callable surface; kept with provenance | auto for decay, human for merges |

**The asymmetry that makes it safe:** creation is free, *registration and execution* are gated. The kernel doesn't care how a file appeared — only whether it's allowed to run.

---

## 3. Stage Details

### draft — birth is ungated
```bash
# harness writes routines/refund_and_archive.py with native fs
capcli routine draft refund_and_archive      # scaffold + validate + manifest extract
# ⚠ near-duplicate exists: get_orders_status (similarity 0.91)
#   reuse it, or justify: --reason "..."
```
Duplicate-similarity check at birth slows bloat before it starts.

### prove — the first gate (manifest + fingerprint proof)
```bash
capcli routine prove refund_and_archive -p order_id=ORD-8842
```
Checks, then real execution, scoped environment:
- AST: no `subprocess`, `os`, raw `sqlite3`, HTTP clients
- Params: `Param` declarations typed and documented
- Policy: every primitive the routine calls is *reachable* at its declared trust
- Governance: LOC/tokens/params within limits
- Similarity: near-duplicates flagged, require `--reason`
- **Manifest extraction:** AST walks the `ctx.*` calls and records the declared primitive sequence:

```yaml
# stored with the version at draft time
refund_and_archive@17:
  manifest:
    - api.call: stripe.get_charge
    - db.query: entities (read)
    - api.call: stripe.refund_charge
    - db.txn: [db.exec:entities(update), db.exec:edges(insert)]
  estimated_cost_class: [2× http, 2× write]
```

- Runs at `draft` trust regardless of declared trust — proving never grants power
- System tables (`_audit`, `_api_quota`, `_budget_frames`) are readable during prove for evidence gathering. Agent never writes to them. Definitions live in `system-schema.yaml` (kernel-owned, read-only).
- **Defaults to sim/dev env**; proving against prod requires explicit `--env prod --reason`
- **Sim-mode aware:** each API verb in the manifest declares `sim_mode`. Prove adapts:
  - `sandbox` verbs call sandbox URL
  - `mock` verbs return fixtures (no HTTP)
  - `dry-run` verbs validate params only (no HTTP)
  - `skip` verbs are excluded; routine proves without them
  - `prod-only` verbs are excluded AND authorizer denies in sim/dev
- **Partial manifest match:** when verbs are skipped, prove reports "3/4 primitives matched." The gap is visible. Ship evidence shows exactly what wasn't proven.
- Params come from `capcli sys audit sample` — real historical values, not invented fixtures
- Full audit, tagged `stage: prove`
- **Fingerprint proof:** after execution, the runtime fingerprint (actual leaf ops executed) is compared against the declared manifest. Divergence = warning (conditional branch taken, or undeclared op attempted). Proving proves the declaration, not just "it didn't crash."

The routine now *declares what it will touch* before it ever runs.

### ship — evidence up, authority down
```bash
capcli db query "SELECT * FROM routine_stats WHERE capability = 'refund_and_archive'"
# runs: 31, success_rate: 0.97, p95: 640ms
capcli routine ship refund_and_archive --to reviewed \
    --reason "97% success over 31 sim runs; replaces 3-op sequence seen 47×"
```
- Agent gathers evidence from the audit mirror; **human/CI approves promotion to pinned**
- **Evidence block includes manifest diff vs previous version**: promotion review sees "v18 adds `api.call X`" without reading the raw diff
- **Evidence block includes sim gaps**: if any verb was `skip` or `prod-only`, the evidence shows: "sim proved 3/4 verbs. 1 verb (gov.file_tax_return) was prod-only. First 3 prod calls require human approval." The human sees the gap before granting authority.
- Prod promotion additionally requires merge from the routine's dev/sim branch

### Auto-promotion: draft → reviewed (low-risk only)
Human attention is the bottleneck. Mechanical verification should not require a human.
Auto-promotion from draft to reviewed is permitted when ALL thresholds are met:

| Condition | Threshold |
|---|---|
| `sim_runs` | ≥ 10 |
| `success_rate` | ≥ 0.95 |
| `manifest_match_rate` | 1.0 |
| `policy_denials` | 0 |
| `fingerprint_drift_events` | 0 |

- Logged as `event: routine.auto_promoted` with `from: draft, to: reviewed, evidence: {...}`.
- Human can veto retroactively: `capcli routine rollback <name> --to-trust draft`.
- **reviewed → pinned is ALWAYS human-gated.** Pinned means relaxed caps and unattended prod execution. That decision is never automated.
- Promotion queues: `capcli routine ship --queue`. Human reviews in batches. Governance sets `max_promotion_queue_age_hours: 48`; stale queues alarm via `sys doctor`.

### Promotion Queue Mechanics
The trust ladder creates a human bottleneck at scale. Queues convert per-routine review into batch review.

- **Queue command:** `capcli routine ship <name> --to reviewed --queue`. Routine enters pending state. Not promoted. Not callable at new trust level.
- **Batch review:** `capcli routine pending` shows all queued promotions with evidence summaries (sim runs, success rate, manifest diff). Human approves/rejects in bulk.
- **SLA enforcement:** Governance sets `max_promotion_queue_age_hours: 48`. If a routine sits in queue past SLA, `sys doctor` emits `promotion.sla_breached` warning. Kernel does NOT auto-promote on timeout — it nags.
- **CI-driven promotion:** A pipeline runs `routine prove --env sim`, checks evidence thresholds, and calls `routine ship --to reviewed --by ci:github-actions --queue`. The authority gate is the CI config (reviewed like code), not a human clicking approve per routine.
- **Audit trail:** Queue entry = `event: routine.queued`. Approval = `event: routine.promoted` with `via: queue_batch_<id>`. Rejection = `event: routine.promotion_rejected` with reason.
- **Veto window:** After batch approval, routines enter a 1-hour veto window before trust actually changes. Any principal can `capcli routine rollback <name> --to-trust draft` during this window without needing override authority.

This keeps the authority gate intact while removing the human from the hot path for mechanical draft→reviewed transitions.

### live — governed service
Callable via `capcli run`, `ctx` composition, schedules, watches. Every call crosses the gate; trust level sets caps. Runtime fingerprint continuously compared to manifest — drift triggers `governance.anomaly`.

Every invocation pushes a **budget frame** onto the call stack. The frame tracks ops consumed, duration elapsed, spend incurred, rows affected. Child routines inherit the tightest constraint: `min(declared, parent_remaining)`. Session-level counters (spend, rate, rows) never reset via composition. Budget exhaustion = clean exit 2 with the exact frame, dimension, and remaining cited.

### monitor → decay — the counter-force
```bash
capcli routine sweep                       # dead, failing, duplicate signals
capcli routine rollback refund_and_archive --to-version 16
capcli routine retire find_orders_by_status --reason "merged into orders_by_status"
```
- Unused 30d → retire candidate; success < 0.7 → rollback candidate
- Retirement keeps provenance pointers; deletion never happens

---

## 4. The Environment Axis

Trust and environment are **two axes of one ladder**. A routine doesn't just earn trust — it *travels*:

```
dev (born draft)  →  sim (tested, evidence)  →  prod (pinned, merged)
```

| Env role | Lifecycle meaning |
|---|---|
| `dev` | Birthplace. Draft routines live here; experimentation is cheap |
| `sim` | Proving ground. Seeded from prod (masked); replay real history against the routine |
| `prod` | Destination. Draft writes denied; only reviewed/pinned + merged code runs |

Promotion commands carry `--env`; `env doctor` flags routines running in prod without merge. **Reaching prod = merge + pin sign-off**, never a runtime promotion.

---

## 5. Atomic Primitives × Environments — the deep part 🔬

A routine is a DAG of atomic ops. The lifecycle isn't just routine-level — **each primitive leverages the env axis independently.** This is where rehearsal becomes physics.

### 5.1 Every primitive is env-scoped by birth

```json
{
  "event": "db.exec",
  "env": "sim",
  "stage": "test",
  "routine": "refund_and_archive@17",
  "capability": "db.exec",
  ...
}
```

`env` and `stage` ride every leaf event. The same routine, same params, produces a *distinguishable* event stream per world — which is what makes everything below possible.

### 5.2 Idempotency keys are env-scoped

```
key = f(routine_version, params, env)
```

A sim run and a prod run of the same routine get **different keys**. Rehearsal can never collide with production; replaying sim never double-fires a prod provider call. The key namespace is world-local.

### 5.3 Rehearsal = same primitives, different world

```bash
capcli env use sim
capcli run refund_and_archive -p order_id=ORD-8842   # full primitive DAG executes
capcli sys audit tail --routine refund_and_archive        # inspect every leaf
capcli env use prod
capcli run refund_and_archive -p order_id=ORD-8842   # now with confidence
```

- `db.*` primitives execute against sim's forked state — real schema, masked data
- `api.*` primitives adapt to `sim_mode`:
  - `sandbox` — hit sandbox providers (env overlay swaps `base_url`)
  - `mock` — kernel returns canned fixture from `apis/*.mock.yaml` (no HTTP)
  - `dry-run` — kernel validates params and policy, returns `simulated: true` (no HTTP)
  - `skip` — excluded from execution; routine proves without this verb
  - `prod-only` — authorizer denies execution in sim/dev; verb is excluded
- `schedule`/`notify` primitives fire in the sim world: notifications route to `#sim-notifications` via overlay

The routine's primitives don't know or care which world they're in. Prove the code in a world that costs nothing.

### 5.4 Primitive-level diff — sim vs prod expectation

After a sim run, the audit mirror gives per-primitive evidence:

```bash
capcli db query "
  SELECT capability, count(*) n, sum(rows_affected) rows, avg(duration_ms) p50
  FROM _audit
  WHERE routine = 'refund_and_archive@17' AND env = 'sim'
  GROUP BY capability"
```

→ "this routine makes 2 api calls, 2 db writes, touches 3 rows." When the same routine later runs in prod, deviation from the rehearsed profile (5 writes instead of 2) is a **loud anomaly**. Primitives give you an *execution fingerprint* per environment.

### 5.5 Cross-env replay — history as test data

```bash
capcli env use sim
capcli sys audit replay --from prod --since 7d
```

Prod's actual primitive streams re-execute in sim: every leaf op re-runs against forked state, **current policy enforced**, external primitives marked `replay: manual`. A routine version is validated against *what really happened*, and the audit mirror shows where the new version's primitives diverge from history's.

### 5.6 Failure forensics per primitive

When a live run fails, the spine localizes it to the exact leaf:

```bash
capcli sys audit trace op_000123
# → refund_and_archive@17 (prod)
#    ├─ api.call stripe.get_charge     ✓ 310ms
#    ├─ api.call stripe.refund_charge  ✗ policy-denied: spend cap exceeded
#    └─ db.exec (never reached)
```

Rollback decisions become primitive-informed: the *routine* isn't broken; the *spend policy* is. Fix the right thing.

### 5.7 Manifest vs Fingerprint Drift

At runtime, the kernel compares the executing fingerprint against the declared manifest:

- **Match:** routine behaves as declared
- **Divergence:** conditional branch taken for the first time, or undeclared op attempted → `governance.anomaly` event logged
- **New leaf added between versions:** automatically cited during `promote` review

The routine's *actual* behavior is diffable against its *declared* behavior, per version.

### 5.8 The primitive contract (summary)

| Primitive property | Env leverage |
|---|---|
| Identity | every event carries `env` + `stage` |
| Idempotency | keys namespaced per env — no cross-world collisions |
| Rehearsal | identical DAG executes in any world; cost asymmetry is the safety |
| Fingerprint | per-env primitive profiles; deviations are anomalies |
| Manifest | static declaration extracted at validate; drift detected at runtime |
| Replay | history re-executes per env; externals confirmed manually |
| Forensics | failures localize to leaf ops within their world |
| Sim mode | each verb declares how it behaves in sim; prove adapts; gaps are visible |

---

## 6. Versioning & Provenance

```yaml
refund_and_archive:
  version: 17
  code_hash: sha256:9d2e...
  manifest_hash: sha256:a1b2...
  created_by: agt_7f3k
  promoted_by: user:alice
  promoted_through: [dev, sim, prod]       # the journey is recorded
  consolidated_from: [...]                 # if merged
```

- Edits create versions; replay verifies hash
- The promotion path itself is provenance — you can ask *how* a pinned routine earned prod
- Merge/rollback never delete; pointers preserve the graph

---

## 7. Full Command Census

```bash
capcli routine draft <name> [--reason]              # create + validate + manifest extract
capcli routine prove <name> [-p k=v] [--env sim]    # proves manifest vs fingerprint
capcli routine ship <name> --to reviewed|pinned [--env X] --reason "..."
capcli routine sweep [--since 30d]                  # consolidate report + propose
capcli routine stats <name> [--deep]                # per-leaf duration/spend/failure
capcli routine rollback <name> --to-version N
capcli routine retire <name> [--reason]
capcli sys audit sample --capability X              # test-param extraction
capcli sys audit trace <op-id>                      # primitive forensics
```

---

## 8. Anti-Decisions

- **No ungated execution.** File creation is free; running is never. The gate is at registration, not at birth
- **No self-promotion.** Trust ascends through human/CI gates only; evidence is agent work, authority is human work
- **No prod testing of draft writes.** Prod policy denies them — rehearsal belongs in sim, by construction
- **No cross-env key reuse.** Idempotency namespaces are world-local; rehearsal can never touch production effects
- **No deletion.** Retirement with pointers; rollback un-retires. The history graph only grows
- **No routine-level-only lifecycle.** Primitives are first-class citizens of the lifecycle — env, stage, key, manifest, and fingerprint at the leaf
- **No silent manifest drift.** Undeclared ops trigger anomalies, not silent acceptance
- **No pretending external systems are simulatable.** Verbs without sandboxes declare sim_mode. Prove reports the gap. Ship shows what wasn't proven. The cage labels the wall
- **No budget bypass via composition.** Session-level counters don't reset when routines call sub-routines. The cage tightens downward, never widens

---

## 9. Invariants

1. Every routine passes draft → prove → ship; no stage may be skipped
2. Every transition is an audit event with agent, principal, intent/reason
3. Proving executes at draft trust in sim/dev; prod shipping requires merge + pin
4. Prove extracts the primitive manifest; prove runs prove it against the runtime fingerprint
5. Every primitive event carries `env` + `stage`; execution fingerprints are per-world
6. Idempotency keys are env-scoped; no key ever spans worlds
7. Rehearsal (sim) and service (prod) are the same code path in different worlds — provable, diffable, replayable
8. Decay and sweep run on schedule; accumulation never outpaces subtraction for long
9. Manifest drift at runtime is a governed anomaly, never silently accepted
10. Budget cascades downward; child effective = min(declared, parent_remaining); denial cites the exact frame, dimension, and remaining
11. Sim mode is per-verb; prove adapts; gaps are visible in evidence; first prod calls of un-simulated verbs require human approval

---

## The One-Liner

> **Routines are born free but run gated — proven in sim by their own atoms, promoted by evidence and human authority, pinned in prod only by merge; and every primitive, from manifest declaration to retirement, carries the name of the world it touched.**