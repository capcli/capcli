# Command: `capcli run`

Where intentions meet the authorizer. The authorizer wins every time.

The hot path noun. Every capability invocation — routine, API verb, or raw SQL — funnels through here and across the same five gates. You declare intent; the kernel handles the physics.

```bash
capcli run <verb> [args] [--flags]
```

---

## Subcommands

| Verb | Syntax | Description |
|---|---|---|
| **`execute`** | `capcli run <capability> [-p k=v] [-m "intent"]` | Invokes a routine or API verb through the full gate pipeline. |
| **`sql`** | `capcli sql "<query>" [-p k=v] [-m "intent"] [--dry-run]` | Unified AST-gated query & execution. Reads are free; writes need intent. |
| **`overview`** | `capcli run overview [--as <principal>]` | Single-shot domain situational briefing, capped under 500 tokens. |
| **`search`** | `capcli search <query> [--type <domain>] [--trust X] [--env X]` | Typed-pointer search across the unified registry. |
| **`search gaps`** | `capcli run search gaps --since 7d` | Surfaces queries that get searched but never invoked — missing capabilities. |
| **`inspect`** | `capcli inspect <ptr>` | Pre-flight envelope across all pointer types: cost, verdict, manifest, stats. |

*(Ergonomic aliases: `capcli sql`, `capcli search`, and `capcli inspect` invoke the run noun directly — no `run` prefix required.)*

---

## 1. The Hot Path: `run <capability>`

```bash
$ capcli run dispatch_order -p order_id=ORD-8842 -p carrier=fedex \
    -m "fulfill paid order for customer checkout"
```

```text
[dev:tier_1]  dispatch_order@4  ✓  1.2s

  status:    dispatched
  tracking:  794644790133
  ops_used:  3/8
  audit:     op_9f2c → op_9f2d → op_9f2e
```

Three primitives fired. Under budget. Logged — you didn't write a try/catch; the kernel *can't not*. Every invocation crosses five gates: session token → intent binding → AST scan → authorizer + EXPLAIN cross-check → execution with audit emission. Fail any stage and execution stops with an exit code. State untouched.

---

## 2. Raw SQL: Same Gates, One Command

```bash
$ capcli sql "UPDATE orders SET status = 'processing' WHERE id = 'ord_9885' LIMIT 1" \
    -m "mark oldest pending order as processing"
```

```text
[dev:tier_1]  ✓  18ms

  rows_affected: 1
  ops_used:      1
  audit:         op_4f8a
```

Now try to be stupid:

```bash
$ capcli sql "DELETE FROM orders"
```

```text
[dev:tier_1]  ✗ exit 2

  FAIL  policy.query.update_delete.require_where
        DELETE FROM orders
        ^^^^^^^^^^^^^^^^^^
        Missing WHERE clause. Unbounded delete denied.

  state_modified: false
  remedy: add WHERE + LIMIT, or use chunked loop via ctx.db.execute
```

The SQL never reached SQLite — it died at `sqlite3_prepare_v2`, and the denial named the rule, the offending span, and the fix. Denials teach. Add `--dry-run` to preview any write's plan — AST verdict, authorizer verdict, estimated rows — with nothing applied.

---

## 3. Look Before You Leap: `inspect`

```bash
$ capcli inspect cap://dispatch_order@4
```

```text
[dev:tier_1]  cap://dispatch_order@4

  trust:       pinned
  runtime:     typescript (bun)
  params:      order_id: string, carrier: string

  envelope:
    can_invoke_now:   true
    tokens:           500 result cap · file within 2,000-token ceiling
    duration:         p50 340ms · p95 890ms · timeout 15s
    storage:          reads orders · writes orders · max rows 500 (pinned)
    concurrency:      active locks: none · ops 8/run (kernel ceiling 50)
    api:              quota bucket 60 @ 1.0/s · session fuel 80400 · sim_mode: sandbox
    composition:      nesting ≤ 5 · child_routines: [] · inheritance: min

  manifest:    db.query → api.call(logistics.shipments.create) → db.execute
  stats:       214 runs · 99.1% success · p50 340ms · p95 890ms
```

`can_invoke_now` is the whole point: one boolean, zero ambiguity, zero roundtrips. When it's `false`, `blocking_reasons` names the tightest constraint, and your harness waits, yields, or picks a lighter capability instead of guessing. The envelope resolves for every pointer type — `cap://`, `db://`, `doc://`, `bind://` — same shape every time.

---

## 4. Where Am I? `run overview`

```bash
$ capcli run overview
```

```text
[prod:tier_1]  overview@1  ✓  24ms

  environment: prod (Tier 1 Hardened)
  schema:      v14 (nominal, 0 drift)
  policy:      v5 (locked, hash: sha256:77a1...)
  last_action: 3m ago (db.execute: orders.ORD-9912 status='shipped')
  active_lock: none
  drift_alert: 0 uncommitted changes
  next_step:   ready for incoming triggers
```

The Ground Zero briefing: environment, schema, policy, last committed action, locks, drift — dense, sub-500 tokens, the standard first move of every session. An agent grounded in deterministic reality doesn't re-bill customers it already refunded. Pass `--as <principal>` to see the world through a scoped principal's eyes.

---

## 5. Find It — or Find the Hole: `search`

`capcli run search "order"` returns typed pointers with trust rungs and sub-60-token descriptions — filterable by `--type`, `--trust`, and `--env`. And sometimes the interesting result is the one that *doesn't* exist:

```bash
$ capcli run search gaps --since 7d
```

```text
[dev:tier_1]  2 gaps detected

  query: "inventory sync"     searches: 8    invocations: 0    signal: missing capability
  query: "customer export"    searches: 5    invocations: 0    signal: missing capability
```

Eight searches, zero invocations. The registry noticed the hole before you did.

---

## Invariants & Rules

* **Writes need intent — and bounds.** No `-m`, no mutation: `exit 3`, `policy.query.writes_require_intent`. UPDATE/DELETE require WHERE + LIMIT in dev, sim, and prod — physics doesn't do environments.
* **The budget cage counts ops.** Every primitive is an op. Routine ceiling 50, session ceiling 500. Exhaustion is `exit 2` — never silent truncation. Result payloads cap at 500 tokens (`truncated: true`).
* **The registry law.** All capabilities resolve through the unified registry. A TypeScript routine and a Stripe endpoint are both `cap://` — search it, inspect it, run it.
* **Bypass flags don't exist.** `--force`, `--override-budget`, and `--force-prod` are syntax errors. `--verbose` is banned — the audit spine is the verbosity: `sys audit tail`.

---

**Canonical grammar for every noun** → [cli.md](../cli.md)

**Every exit code, exactly** → [exit-codes.md](../exit-codes.md)

**The run surface in plain prose** → [../../use/run.md](../../use/run.md)
