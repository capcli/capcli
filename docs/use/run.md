# Run

You found it. You inspected it. Now you do the thing.

One command. Physics handles the rest.

---

## Run a routine

```bash
$ capcli run dispatch_order -p order_id=ORD-8842 -p carrier=fedex \
    -m "fulfill paid order for customer checkout"
```

```
[dev:tier_1]  dispatch_order@4  ✓  1.2s

  status:    dispatched
  tracking:  794644790133
  ops_used:  3/8
  audit:     op_9f2c → op_9f2d → op_9f2e
```

Three primitives fired. Under budget. Logged. Done.

Your harness didn't write a try/catch. Didn't check rate limits. Didn't remember to audit. Capcli did all of it because it *can't not*.

---

## Run raw SQL (read)

Reads don't need intent. They're free. Bounded, but free.

```bash
$ capcli sql "SELECT id, total, status FROM orders WHERE status = 'pending' LIMIT 10"
```

```
[dev:tier_1]  ✓  12ms

  rows: 10
  id          total    status
  ──────────  ───────  ───────
  ord_9921    142.00   pending
  ord_9918    89.50    pending
  ...
```

AST checked it. Authorizer allowed it. SQLite executed it. Rows came back.

---

## Run raw SQL (write)

Writes need intent. Always. No exceptions. No "I forgot."

```bash
$ capcli sql "UPDATE orders SET status = 'processing' WHERE id = 'ord_9885' LIMIT 1" \
    -m "mark oldest pending order as processing"
```

```
[dev:tier_1]  ✓  18ms

  rows_affected: 1
  ops_used:      1
  audit:         op_4f8a
```

Forgot the `-m`?

```bash
$ capcli sql "UPDATE orders SET status = 'processing' WHERE id = 'ord_9885' LIMIT 1"
```

```
[dev:tier_1]  ✗  exit 3

  FAIL  policy.query.writes_require_intent
        Mutating write without causal intent declaration.

  state_modified: false
  remedy: add -m "why you're doing this"
```

The kernel doesn't care *what* your intent is. It cares that you *have* one. Audit trail demands causality.

---

## Dry-run: "what would happen?"

Before you actually mutate, see the plan.

```bash
$ capcli sql "UPDATE orders SET status = 'shipped' WHERE status = 'processing' LIMIT 50" \
    -m "batch ship processing orders" \
    --dry-run
```

```
[dev:tier_1]  dry-run  ✓

  statement:     UPDATE orders SET status = 'shipped' WHERE status = 'processing' LIMIT 50
  ast_check:     pass
  authorizer:    pass (write on orders allowed)
  intent:        declared
  estimated_rows: 34
  blast_radius:  bounded (LIMIT 50)

  state_modified: false
  note:           no execution occurred
```

You see the plan. Nothing touched. Your harness reads this, decides it's safe, then runs it for real without `--dry-run`.

---

## What happens under the hood

Every `run` and `sql` command passes through five gates. You don't configure them. You don't think about them. They just exist.

```
Stage 0 — session token verified
Stage 1 — intent bound, blast radius checked
Stage 2 — AST parsed, patterns scanned
Stage 3 — authorizer callback + EXPLAIN cross-check
Stage 4 — SQLite executes, audit event emitted
```

If any stage fails, execution stops. State untouched. You get an exit code and a reason.

---

## Exit codes you'll actually see

| Code | Meaning | State |
|---|---|---|
| `0` | Success. Committed. Logged. | Modified. |
| `2` | Denied. Policy, AST, authorizer, or budget said no. | Untouched. |
| `3` | Refused. Missing intent, bad syntax, missing param, lockfile mismatch. | Untouched. |
| `4` | Crash. Runtime exception in sandbox. | Rolled back. |
| `5` | Panic. Audit sink unreachable. Nothing runs unaudited. | Untouched. |
| `6` | Yield. Quota exhausted. Task suspended until refill. | Untouched. |

Your harness reads these. It knows what to do. You don't have to.

---

## Locks: "I need exclusive access"

Multi-step operations that can't be interrupted:

```bash
$ capcli run reconcile_inventory -p warehouse=WEST \
    -m "nightly warehouse reconciliation" \
    --lock inventory:WEST --ttl 300
```

```
[dev:tier_1]  reconcile_inventory@2  ✓  42s

  lock:        inventory:WEST (acquired, ttl 300s)
  ops_used:    18/50
  audit:       op_7a1b → ... → op_7a2c
  lock:        released
```

The lock is a lease in `_claims`. If your harness crashes mid-run, the lock expires after TTL. No orphaned locks. No deadlocks.

---

## What your harness actually does

You say: "ship order 8842 via fedex"

Your harness does:

1. `capcli search "dispatch"` → finds `cap://dispatch_order@4`
2. `capcli inspect cap://dispatch_order@4` → checks `can_invoke_now`
3. Sees `true` → `capcli run dispatch_order -p order_id=ORD-8842 -p carrier=fedex -m "..."`
4. Reads exit code. Reads output. Reports to you.

Four words from you. Three commands from the harness. One shipped order.

---

## The one rule

**Writes need intent. Reads don't.**

That's the whole contract. Everything else is physics.

```bash
# Read: free
capcli sql "SELECT ..."

# Write: needs -m
capcli sql "UPDATE ..." -m "why"

# Run: needs -m if the routine mutates
capcli run dispatch_order -p ... -m "why"
```

No intent, no write. `exit 3`. Every time. No exceptions.

---

**Hit a wall?** → [boundaries.md](boundaries.md)

**Need to work with your actual data?** → [work-with-your-data.md](work-with-your-data.md)
