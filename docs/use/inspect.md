# Inspect

You found something. Now you want to know: *can I actually run this right now, and what will it cost?*

One command. Zero roundtrips. Full go/no-go verdict.

---

## The move

```bash
$ capcli inspect cap://dispatch_order@4
```

```
[dev:tier_1]  cap://dispatch_order@4

  trust:       pinned
  runtime:     python (python3)
  params:      order_id: string, carrier: string
  description: "Dispatch paid order to carrier and update status"

  limits:      8 ops · 15s · 500 result tokens

  manifest:
    1. db.query    orders (read)
    2. api.call    logistics.shipments.create
    3. db.execute  orders (write)

  budget_status:
    can_invoke_now:            true
    session_ops_remaining:     488
    session_duration_remaining: 555000ms
    session_fuel_remaining:    80400
    session_egress_remaining:  4181824 bytes
    session_rate_remaining:    287
    tightest_constraint:       null

  composition:
    max_nesting_depth:  5
    budget_inheritance: min
    child_routines:     []

  stats:
    total_runs:    214
    success_rate:  99.1%
    p50_duration:  340ms
    p95_duration:  890ms
    last_run_at:   2m ago
```

One command. Everything you need to decide whether to proceed.

---

## Reading the envelope

Three sections. Three questions answered.

| Section | Answers |
|---|---|
| **manifest** | What will it actually touch? |
| **budget_status** | Can I run it *right now*? |
| **stats** | How reliable is it historically? |

You don't read source code. You don't trace dependencies. You read the envelope.

---

## The verdict: `can_invoke_now`

This is the whole point of inspect. One boolean. Zero ambiguity.

```
can_invoke_now: true    → go ahead
can_invoke_now: false   → don't. read blocking_reasons.
```

When it's false:

```
[dev:tier_1]  cap://nightly_reconciliation@2

  budget_status:
    can_invoke_now:    false
    blocking_reasons:
      - "session_ops_remaining: 3 (needs 12)"
      - "tightest_constraint: ops"
    tightest_constraint: ops
```

Your harness reads this. It doesn't guess. It doesn't try anyway. It either waits, asks you, or picks a different approach.

---

## Inspect an API verb

```bash
$ capcli inspect cap://stripe.refund_charge
```

```
[dev:tier_1]  cap://stripe.refund_charge

  trust:       reviewed
  sim_mode:    sandbox
  cost_class:  write
  idempotent:  true
  method:      POST
  path:        /v1/refunds

  quota:
    provider:          stripe
    bucket_capacity:   60
    tokens_available:  47
    refill_rate:       1.0/s
    reset_at:          14m

  budget_status:
    can_invoke_now:    true
    session_fuel_remaining: 80400
    tightest_constraint: null

  stats:
    total_runs:    89
    success_rate:  97.8%
    p50_duration:  410ms
    p95_duration:  1100ms
```

You see the live quota. You see how many tokens are left and which priority floor gates your class. You know *before* you burn a call whether you can afford it.

---

## Inspect a table

```bash
$ capcli inspect db://orders
```

```
[dev:tier_1]  db://orders

  columns:     12
  rows:        4,281
  indexes:     3
  views:       2 (orders_recent, orders_by_customer)
  constraints: 4 chk, 2 fk

  access:
    read:    allowed (all trust levels)
    write:   allowed (reviewed+)
    drop:    denied
    alter:   requires reviewed

  recent_activity:
    reads_last_hour:   34
    writes_last_hour:  7
    denials_last_hour: 1
```

You see the shape. You see the access rules. You see recent traffic. No `PRAGMA table_info`. No grepping schema files.

---

## Inspect a doc

```bash
$ capcli inspect doc://refund-policy
```

```
[dev:tier_1]  doc://refund-policy

  type:       markdown spec
  tokens:     340
  updated:    3d ago
  outline:
    1. Eligibility windows
    2. Partial refund rules
    3. Stripe integration notes
    4. Edge cases
```

You don't read the whole thing. You see the outline. If you need node 3, you fetch it:

```bash
$ capcli doc read doc://refund-policy#3 --max-tokens 100
```

Progressive disclosure. You pull what you need, not the whole blob.

---

## Inspect a binding

```bash
$ capcli inspect bind://nightly_sync
```

```
[dev:tier_1]  bind://nightly_sync

  type:        cron
  capability:  cap://inventory_sync@3
  schedule:    0 3 * * *
  trust:       reviewed
  status:      active
  last_fire:   14h ago
  next_fire:   10h from now
  catchup:     max 1 fire on restart
```

You see when it runs. You see what it calls. You see if it's healthy. No crontab grepping.

---

## What your harness does with this

You say: "refund order 9885"

Your harness does:

1. `capcli search "refund"` → finds `cap://order_refund@7`
2. `capcli inspect cap://order_refund@7` → checks `can_invoke_now`
3. Sees `true` → proceeds to invocation
4. Sees `false` → reads `blocking_reasons`, tells you why, suggests alternatives

You said four words. Your harness made two calls. You got a refund. You didn't read a single line of code.

---

## When inspect says no

The denial isn't a wall. It's a map.

```
blocking_reasons:
  - "session_ops_remaining: 3 (needs 12)"
  - "tightest_constraint: ops"
```

Your harness reads this and decides:
- Wait for the session to reset?
- Ask you to start a new session?
- Pick a lighter capability?
- Yield and retry later?

The point: inspect teaches. It doesn't just block. It says *why* and *what's tight*.

---

## The one rule

**Inspect before you invoke if you're unsure.**

If your harness already knows the signature and the budget is obviously fine, skip inspect and go straight to `run`. No ceremony needed.

But if you're in unfamiliar territory — new routine, new API verb, unfamiliar table — inspect first. Two seconds. Saves you a denial.

---

**Know what it does? Now run it** → [run.md](run.md)

**Need to work with real data?** → [work-with-your-data.md](work-with-your-data.md)
