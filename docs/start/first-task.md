# First Task

You're not going to write the SQL. You're not going to write the API client. You're going to tell your harness what you want, and watch it figure out the physics.

Open your terminal. Paste this prompt to your agent:

> "Find the orders table. Show me the 5 most recent pending orders. Then, take the oldest one of those five and mark it as 'processing'."

Sit back. Here is exactly what your harness is going to do, and what you will see on the screen.

---

## Step 1: The harness looks around

It doesn't guess. It asks Capcli what exists.

```bash
$ capcli search "order"
```

```text
[dev:tier_1]  2 results

  db://orders                 table      —         "Core order state"
  cap://dispatch_order@4      routine    pinned    "Dispatch paid order to carrier"
```

It sees the table. It sees a routine. For now, it just needs the table.

---

## Step 2: The safe read

The harness drafts a read query. Reads are cheap. Capcli lets them through as long as they aren't trying to download the entire database.

```bash
$ capcli sql "SELECT id, customer_id, total, status, created_at 
              FROM orders 
              WHERE status = 'pending' 
              ORDER BY created_at DESC 
              LIMIT 5"
```

```text
[dev:tier_1]  ✓  14ms

  rows: 5
  
  id          customer_id  total   status   created_at
  ──────────  ───────────  ──────  ───────  ───────────────────
  ord_9921    cust_441     142.00  pending  2024-05-12 09:14:22
  ord_9918    cust_882     89.50   pending  2024-05-12 08:45:10
  ord_9902    cust_109     310.00  pending  2024-05-11 16:20:05
  ord_9899    cust_441     45.00   pending  2024-05-11 14:10:12
  ord_9885    cust_773     112.75  pending  2024-05-11 11:05:33  <-- oldest
```

Five rows. Bounded. Fast. The harness now knows `ord_9885` is the target.

---

## Step 3: The harness gets lazy (and gets caught)

The harness decides to update the status. But instead of targeting the specific ID, it writes a sloppy query based on the status.

```bash
$ capcli sql "UPDATE orders SET status = 'processing' WHERE status = 'pending'"
```

```text
[dev:tier_1]  ✗  exit 2

  FAIL  policy.query.update_delete.require_bounded
        UPDATE orders SET status = 'processing' WHERE status = 'pending'
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        Unbounded update denied. Predicate matches multiple rows.

  state_modified: false
  remedy: target specific primary key or add LIMIT
```

**Boom. `exit 2`.** 

The C authorizer intercepted it at prepare-time. The SQL never touched the database engine. Zero rows were updated. State is untouched. 

Capcli didn't just block it; it told the harness *why* and *how to fix it*. 

---

## Step 4: The harness learns and retries

Your agent reads the `remedy` field. It corrects its mistake and targets the exact primary key it found in Step 2.

```bash
$ capcli sql "UPDATE orders SET status = 'processing' WHERE id = 'ord_9885' LIMIT 1" \
    -m "mark oldest pending order as processing"
```

```text
[dev:tier_1]  ✓  18ms

  rows_affected: 1
  ops_used:      1/50
  audit:         op_4f8a
```

Success. One row changed. One op burned. One audit hash generated.

---

## Step 5: You check the receipt

You don't trust the harness. You trust the ledger. You ask Capcli what actually happened in the last two minutes.

```bash
$ capcli sys audit tail --since 2m
```

```text
[dev:tier_1]  3 events

  ts          event             decision   capability      intent
  ──────────  ────────────────  ─────────  ──────────────  ────────────────────────────
  ...         sql.query         allow      db://orders     "show 5 recent pending"
  ...         sql.query         denied     db://orders     "update pending to processing"
  ...         sql.query         allow      db://orders     "mark oldest pending as processing"
```

Three events. The read. The blocked write. The successful write. 
Hash-chained. Append-only. 

---

## What just happened?

1. You gave a vague English instruction.
2. Your harness translated it into structural commands.
3. Capcli allowed the safe read.
4. Capcli structurally murdered the sloppy write (`exit 2`).
5. The harness self-corrected using the denial feedback.
6. Capcli allowed the precise write.
7. Everything was logged to the append-only spine.

You didn't write a try/catch block. You didn't check row counts. You didn't manually write an audit log. 

You drank your coffee.

---

**Ready to unpack the pieces?** → [what-just-happened.md](what-just-happened.md)
