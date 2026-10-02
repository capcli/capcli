# Inspection

One call. One response. One boolean.

`capcli inspect <ptr> --json` resolves a pre-flight envelope for any URP type. `db://` returns shape, access rules, and recent traffic. `doc://` returns outline nodes — `doc read` fetches the targeted leaf, never the blob. `bind://` returns trigger health. The SLA: a single response, zero roundtrips — the complete go/no-go verdict before you spend a single op.

---

## The move

```bash
$ capcli inspect cap://dispatch_order@4 --json
```

```
{
  "exit": 0,
  "json": {
    "ptr": "cap://dispatch_order@4",
    "trust": "pinned",
    "runtime": "typescript (bun)",
    "params": { "order_id": "string", "carrier": "string" },
    "limits": { "ops": 8, "duration": "15s", "result_tokens": 500 },
    "manifest": [
      "db.query    orders (read)",
      "api.call    logistics.shipments.create",
      "db.execute  orders (write)"
    ],
    "budget_status": {
      "can_invoke_now": true,
      "session_ops_remaining": 488,
      "session_fuel_remaining": 80400,
      "tightest_constraint": null
    },
    "composition": {
      "max_nesting_depth": 5,
      "child_routines": [],
      "budget_inheritance": "min"
    },
    "stats": { "total_runs": 214, "success_rate": 0.991, "p50_ms": 340, "p95_ms": 890 }
  },
  "text": "[dev:tier_1]  cap://dispatch_order@4  ✓  can_invoke_now"
}
```

Decode: three sections answer three questions. The **manifest** says what it touches. **budget_status** says whether you can afford it right now. **stats** say whether to trust it historically.

---

## The verdict law

`can_invoke_now` is a boolean. There is no "probably." `true` → proceed to [invocation.md](invocation.md). `false` → do not call; read `blocking_reasons`, act on them, or pick a different capability.

```bash
$ capcli inspect cap://nightly_reconciliation@2 --json
```

```
{
  "exit": 0,
  "json": {
    "ptr": "cap://nightly_reconciliation@2",
    "budget_status": {
      "can_invoke_now": false,
      "blocking_reasons": ["session_ops_remaining: 3 (needs 12)", "tightest_constraint: ops"],
      "tightest_constraint": "ops"
    }
  },
  "text": "[dev:tier_1]  cap://nightly_reconciliation@2  ✗  can_invoke_now: false"
}
```

A `false` verdict is cheaper than the denial you were about to earn. Warnings (`warn_at_remaining`) are non-blocking. `sim_gaps` ride along in the same block, so you know up front which verbs would resolve to mocks.

---

## Envelope dimensions

The envelope is a cost envelope. Every dimension is declared before you spend:

| Dimension | Answers |
|---|---|
| `tokens` | File size, parameter schema, result caps |
| `duration` | p50, p95, timeout ceiling |
| `storage` | Writes, reads, max rows affected |
| `concurrency` | Active locks, max ops per run |
| `api` | Live quota, session fuel remaining, sim mode |
| `composition` | Nesting depth, child routines, budget cascade — `budget_inheritance: min` means a child's effective limit is `min(declared, governance ceiling, parent remaining, session ceiling)`; cages tighten downward, plan accordingly |

---

## API verbs: read the bucket before you burn it

Inspecting an API verb adds the live quota block:

```bash
$ capcli inspect cap://stripe.refund_charge --json
```

```
{
  "exit": 0,
  "json": {
    "ptr": "cap://stripe.refund_charge",
    "trust": "reviewed",
    "state": "active",
    "sim_mode": "sandbox",
    "quota": {
      "bucket_capacity": 60,
      "tokens_available": 47,
      "tokens_earmarked": 10,
      "unreserved_headroom": 37,
      "refill_rate": "1.0/s"
    },
    "budget_status": { "can_invoke_now": true, "session_fuel_remaining": 80400 }
  },
  "text": "[dev:tier_1]  cap://stripe.refund_charge  ✓  can_invoke_now"
}
```

Earmarks matter: `unreserved_headroom` is what is actually yours — tokens ring-fenced by someone else's `ctx.quota.earmark` are not spendable by you. `sim_mode` tells you whether a rehearsal of this verb hits a sandbox endpoint, a fixture, or nothing. One verb, every URP — progressive disclosure is the law: pull what you need, not the archive.

---

**Verdict is true? Spend it** → [invocation.md](invocation.md)

**Want the human view of this envelope?** → [../use/inspect.md](../use/inspect.md)
