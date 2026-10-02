# Effects

Four words that sound identical and mean different things. Your agent conflates them constantly. You shouldn't.

```
operation    → what you attempted
effect       → what state actually changed
event        → the record of the attempt
provenance   → the causal chain linking records to intent
```

---

## Operation: the attempt

You (or your agent) issue a command. That's it. An operation is a *wish* with a syntax.

```bash
$ capcli sql "UPDATE orders SET status = 'processing' WHERE id = 'ord_9885' LIMIT 1" \
    -m "mark oldest pending order as processing"
```

At this point, nothing has happened. Nothing is guaranteed to happen. The universe owes you nothing. SQLite hasn't allocated a byte.

## Effect: the change

If the gates pass *and* execution commits, the effect is the actual state delta. Rows changed, rows affected, state modified. Real. Measurable. Recoverable — because snapshots.

```text
[dev:tier_1]  ✓  18ms

  rows_affected: 1
  ops_used:      1
  audit:         op_4f8a
```

Here's the part worth tattooing somewhere: **denials have no effect, but they still have events.** A blocked `DELETE FROM orders` changed zero rows — and it's in the ledger forever, with `effect: none` stamped on it. Getting caught is also history.

## Event: the record

Every operation — allowed or denied — emits an audit event into `_audit`. Append-only. Hash-chained. The event records what was attempted, by whom, under which intent, and the outcome:

```text
  ts          event                    decision   agent      capability
  ──────────  ───────────────────────  ─────────  ─────────  ──────────────────
  ...         run.dispatch_order       allow      agt_7f3k   cap://dispatch_order@4
  ...         sql.query                denied     agt_7f3k   orders (delete)
```

The raw stdout of your routine is *discarded* — the kernel hashes a canonical JSON outcome instead. No log noise, no prompt leakage, just the receipt. If the sink can't record it, the kernel refuses to run at all (`exit 5`). Unrecorded reality is not reality here.

## Provenance: the chain

Events link upward through `caused_by` pointers — op → routine → session goal — with the intent you declared at the start stamped at the root.

```bash
$ capcli sys audit trace op_9f2e --explain
```

```text
[dev:tier_1]  op_9f2e → op_9f2d → op_9f2c → root

  root intent:    "fulfill paid order for customer checkout"
  session:        goal: dispatch ORD-8842
  routine:        dispatch_order@4 (pinned)
  ops:            db.query → api.call(logistics.shipments.create) → db.execute
```

Follow the chain from any leaf and you reach a *human sentence*. That's the whole point of mandatory `-m`: every mutation must be able to answer "and why did you do that?" with something other than "vibes."

---

## Why the distinction matters

Your agent will report "I updated the orders table." Cool story. Which of these happened?

| What it said | What could be true |
|---|---|
| "Updated orders" | Operation allowed, effect = 1 row. Fine. |
| "Updated orders" | Operation denied, effect = 0 rows. It's summarizing its *wish*. |
| "Updated orders" | Operation crashed, transaction rolled back. Also a wish. |

The audit spine is how you stop arguing with a confident toddler. `state_modified: false` on every non-zero exit is a *law*, not a suggestion. The ledger's version of events wins, every time, and it's cryptographically incapable of taking the toddler's side.

---

**The tamper-evidence machinery in detail** → [audit.md](audit.md)

**How effects get attributed to actors** → [identity.md](identity.md)
