# Structure

Day one, your agent explores. It runs reads, gets denied, refines queries, sketches a routine. That's the point of `dev`.

But loose exploration is a debt. The question is: how does "vibes and SELECT statements" become "explicit, inspectable structure"?

Answer: in stages, each one a small compile.

---

## Stage 1 — The schema is a guess that works

Your agent starts with reads against a blank-ish world:

```bash
$ capcli sql "SELECT id, total, status FROM orders WHERE status = 'pending' LIMIT 10"
```

```text
[dev:tier_1]  ✓  12ms

  rows: 10
  id          total    status
  ──────────  ───────  ───────
  ord_9921    142.00   pending
  ord_9918    89.50    pending
  ...
```

Fine. But queries against *undeclared* structure are queries against vibes. So the next step is writing `schema.yaml` — the domain tables, columns, constraints — and compiling it:

```bash
$ capcli rule apply schema -m "first real schema for orders domain" --dry-run
```

```text
[dev:tier_1]  dry-run  ✓

  gates:       1 syntax ✓ · 2 semantics ✓ · 3 lock ✓ · 4 drift ✓ · 5 migration ✓
  tables:      +14
  views:       +3
  ddl:         61 statements staged

  state_modified: false
```

Five gates pass, the DDL lands, and `world.sql` gets committed for readable diffs. Now the structure is *declared*, not implied. Declared structure can be checked. Implied structure can only be *prayed at*.

---

## Stage 2 — Structure you can inspect

Once declared, structure becomes a queryable object:

```bash
$ capcli db schema --table orders
```

```text
[dev:tier_1]  db://orders

  col              type      nullable   default   fk
  ───────────────  ────────  ─────────  ────────  ─────────────
  id               text      no         —         —
  customer_id      text      no         —         customers(id)
  total            integer   no         0         —
  ...
```

Your agent never greps a `.sql` file or reads a migration folder like an archaeologist. It asks the kernel what exists, and the kernel answers from the compiled declaration — cross-checked against live `PRAGMA`s, so the answer *cannot drift* from reality. Drift is `exit 3` at boot, not a surprise at 2am.

---

## Stage 3 — Structure that refuses to be wrong

The fun part. Declared structure is *enforced* structure:

- `UPDATE orders SET ...` without `WHERE id = ...`? AST denial, `exit 2`.
- A column marked `int~` (write-once)? The C authorizer makes `UPDATE` on it physically impossible.
- A table with `imm_rows: true`? Rows can never be deleted. Not "shouldn't." *Can't.*
- Someone edits `schema.yaml` by hand and the lockfile hash drifts? Boot refuses. `exit 3`.

```bash
$ capcli sql "UPDATE orders SET tracking = '794644790133' WHERE 1=1" -m "fix tracking"
```

```text
[dev:tier_1]  ✗  exit 2

  FAIL  policy.query.update_delete.deny_patterns
        UPDATE orders SET tracking = '794644790133' WHERE 1=1
                                                      ^^^^^^^^^^
        Tautology bypass detected. Matches denied pattern: * WHERE 1=1 *

  state_modified: false
  remedy: use a bounded predicate with LIMIT
```

The structure you declared is now a wall your agent bounces off of. This is what "explicit and inspectable" actually buys you: walls with receipts.

---

## The escalation ladder

```
exploratory reads
    ↓
schema.yaml declared + compiled
    ↓
routines: repeatable logic, versioned in routines/
    ↓
pinned routines: trusted, prod-eligible, endpoint-servable
```

Each rung is a compile + a trust promotion. Each rung costs a little ceremony and buys a lot of physics. You can stop anywhere. Stopping at "exploratory reads" forever is a choice — a bad one, but a choice.

---

## Why not just SQL migrations?

Because migrations are a *history* of structure. `schema.yaml` is a *declaration* of it. History tells you how you got here; declaration tells you what's true *now*, and gets cross-checked against the live database at every boot. Plus: your autonomous agent is the one editing it, and an agent with `ALTER TABLE` power is an agent that will eventually use it "helpfully."

**The full compiler deep-dive** → [../concepts/compiler.md](../concepts/compiler.md)

---

**What runs inside this structure** → [capabilities.md](capabilities.md)
