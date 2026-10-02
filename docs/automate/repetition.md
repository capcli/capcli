# Repetition

Every routine in your registry started the same way: a human squinting at their terminal thinking *"wait, didn't I do this yesterday?"*

That's it. That's the origin story. No grand plan. Just déjà vu with a cost.

---

## Spotting it

The signal shows up in the audit spine, not in your feelings. Watch what your harness actually ran this week:

```bash
$ capcli sys audit query "SELECT capability, count(*) as runs
    FROM _audit WHERE decision = 'allow' GROUP BY capability
    ORDER BY runs DESC LIMIT 5"
```

```text
[dev:tier_1]  ✓  9ms

  capability                     runs
  ─────────────────────────────  ────
  sql.query (orders)             61
  cap://dispatch_order@4         38
  sql.query (inventory)          22
  cap://order_refund@7           11
  api.call (stripe.refund)       4
```

61 ad-hoc reads on `orders`. Eleven refund runs through a routine, plus 4 raw API calls. Somewhere in there, a human typed approximately the same intent 40 times, and an LLM re-derived the same SQL 40 times, each with a fresh chance to be wrong.

Repetition isn't just boring. Repetition is *ungoverned risk with a calendar*. Every ad-hoc re-run is another roll of the dice on a missing `WHERE`.

---

## The decision gate

Before turning repetition into a routine, ask:

1. **Is it the *same* work, or the same *shape*?** (Parameterize the shape, don't fossilize one query.)
2. **Does it mutate state?** (Reads can stay queries. Writes want to be routines — they need intent, budgets, and receipts.)
3. **How often will it run?** (Daily? Worth ceremony. Once a quarter? Leave it alone. Not everything needs to be a framework.)

If your answers are "same shape," "mutates," and "often" — congratulations, you have a routine. Condolences on your past self.

---

## What a routine buys you

Take the query your agent keeps re-deriving:

```bash
$ capcli sql "UPDATE orders SET status = 'processing' WHERE id = 'ord_9885' LIMIT 1" \
    -m "mark oldest pending order as processing"
```

Works. Fine. But every run: re-parsed by an LLM, re-checked, re-explained, zero accumulated history, and the only thing stopping `id = 'ord_9885'` from becoming `WHERE 1=1` is attention.

As a routine it becomes: named (`process_next_order`), versioned (`@2`), parameterized (`-p order_id=…`), budgeted (`6 ops · 20s`), sandboxed, rehearsed, measured (`p50 340ms · p95 890ms`), and promoted on evidence. Same work. Structurally different risk.

---

**Turn it into the real thing** → [routines.md](routines.md)
