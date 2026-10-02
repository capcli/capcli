# See It

No architecture lecture. No diagrams. Just you, a terminal, and Capcli doing its job.

Follow along. Type these. Watch what happens.

---

## You walk in blind

```bash
$ capcli search "order"
```

```
[dev:tier_1]  3 results

  cap://dispatch_order@4     routine    pinned    "Dispatch paid order to carrier"
  cap://order_refund@2       routine    reviewed  "Refund and archive cancelled order"
  db://orders                table      —         "Core order state"
```

Three things. Typed pointers. Trust rungs. Descriptions under 60 tokens each. You didn't read a schema file. You didn't grep a codebase. You asked, it answered.

---

## You poke one before touching it

```bash
$ capcli inspect cap://dispatch_order@4
```

```
[dev:tier_1]  cap://dispatch_order@4

  trust:       pinned
  runtime:     typescript (bun)
  params:      order_id: string, carrier: string
  limits:      8 ops · 15s · 500 result tokens
  budget:      can_invoke_now: true
               session_ops_remaining: 492
               tightest_constraint: null
  manifest:    db.query → api.call(logistics.shipments.create) → db.execute
  stats:       214 runs · 99.1% success · p50 340ms · p95 890ms
```

One command. Zero roundtrips. You know the cost before you spend it. You know it'll fit your session budget. You know the exact call sequence. No surprises hiding in line 47 of a script.

---

## You run it

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

Three primitives. Under budget. Logged. You didn't write a try/catch. You didn't check rate limits. You didn't remember to audit. Capcli did all of it because it *can't not*.

---

## Now try to be stupid

```bash
$ capcli sql "DELETE FROM orders" 
```

```
[dev:tier_1]  ✗ exit 2

  FAIL  policy.query.update_delete.require_where
        DELETE FROM orders
        ^^^^^^^^^^^^^^^^^^
        Missing WHERE clause. Unbounded delete denied.

  state_modified: false
  remedy: add WHERE + LIMIT, or use chunked loop via ctx.db.execute
```

You tried to nuke the table. Capcli said no. Not "are you sure?" Not "maybe don't." *No.* The SQL never reached SQLite. The authorizer killed it at `sqlite3_prepare_v2`. State untouched.

And it told you *why* and *what to do instead*. Denials teach. Every denial carries the same [FAIL payload — rule, culprit, state, remedy](../reference/exit-codes.md#exit-2) — so your harness can self-correct instead of guessing.

---

## Try harder. Be creative about it.

```bash
$ capcli sql "UPDATE orders SET status='shipped' WHERE 1=1" \
    -m "ship everything"
```

```
[dev:tier_1]  ✗ exit 2

  FAIL  policy.query.update_delete.deny_patterns
        UPDATE orders SET status='shipped' WHERE 1=1
                                         ^^^^^^^^^^
        Tautology bypass detected. Matches denied pattern: * WHERE 1=1 *

  state_modified: false
  remedy: use a bounded predicate with LIMIT
```

You tried the classic `WHERE 1=1` trick. AST caught it. No negotiation.

---

## What actually happened?

```bash
$ capcli sys audit tail --since 5m
```

```
[dev:tier_1]  6 events

  ts          event                    decision   agent      capability
  ──────────  ───────────────────────  ─────────  ─────────  ──────────────────
  ...         run.dispatch_order       allow      agt_7f3k   cap://dispatch_order@4
  ...         db.exec                  allow      agt_7f3k   orders (read)
  ...         api.call                 allow      agt_7f3k   logistics.shipments.create
  ...         db.exec                  allow      agt_7f3k   orders (write)
  ...         sql.query                denied     agt_7f3k   orders (delete)
  ...         sql.query                denied     agt_7f3k   orders (update)
```

Six rows. Every attempt — successful or blocked. Agent, capability, decision. [Hash-chained, append-only](../concepts/memory-spine.md). You can't edit this. You can't delete rows. You can't pretend the `DELETE FROM orders` never happened.

---

## The receipt before you close the laptop

```bash
$ capcli sys doctor --report
```

```yaml
trust_receipt:
  status:            nominal
  workspace:         envs/dev/workspace.db
  ledger_root_hash:  sha256:7f9a1b...
  audited_events:    847
  policy_denials:    2 (pre-execution; state untouched)
  unaudited_writes:  0
  secret_leaks:      0
  pinned_routines:   3
  sleep_score:       100%
```

Zero unaudited writes. Zero leaks. Two denials that *protected* you. You close the laptop. You sleep.

---

## What you just saw

No prompts. No "please be careful." No middleware checking a boolean flag.

A compiled C authorizer. A syscall-level network jail. A budget cage that counts ops. An append-only hash chain that boots or refuses.

That's the whole pitch. You just watched it work.

---

**Ready to install it?** → [install.md](install.md)

**Want to do it yourself?** → [first-task.md](first-task.md)
