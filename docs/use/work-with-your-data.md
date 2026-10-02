# Work With Your Data

Your harness loves your data. It wants to aggregate it, join it, and occasionally `DROP` it because it misinterpreted a pronoun.

Capcli puts a glass wall between your agent and the SQLite file. The harness can look, it can touch, but it can't break the glass.

---

## Where does it live?

Right now, your data lives in a **World**. A World is just Capcli's term for "the governed workspace and database you are currently looking at."

```bash
$ capcli env current
```

```text
[dev:tier_1]  env: dev
  workspace:  envs/dev/workspace.db
  schema:     14 tables, 3 views
  trust:      draft baseline
```

You're in `dev`. The database is `workspace.db`. The harness is allowed to make mistakes here.

---

## Looking at the shape

Your harness needs to know what tables exist before it writes a query. It doesn't read `.sql` files. It asks Capcli.

```bash
$ capcli db schema
```

```text
[dev:tier_1]  14 tables

  table             rows     cols   indexes   constraints
  ────────────────  ───────  ─────  ────────  ───────────
  orders            4,281    12     3         4 chk, 2 fk
  customers         1,102    8      2         1 chk
  inventory         8,492    9      4         3 chk, 1 fk
  ...
```

Need details on one?

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
  status           text      no         'pending' —

  indexes: idx_orders_status, idx_orders_customer
```

The harness reads this, builds the SQL, and runs it. You don't have to memorize your own schema.

---

## Changing the shape (Schema Evolution)

Your harness decides `orders` needs a `priority` column. It drafts the `ALTER TABLE`.

```bash
$ capcli sql "ALTER TABLE orders ADD COLUMN priority integer DEFAULT 0" \
    -m "add priority flag for rush shipping" --dry-run
```

```text
[dev:tier_1]  dry-run  ✓

  statement:      ALTER TABLE orders ADD COLUMN priority integer DEFAULT 0
  ast_check:      pass
  authorizer:     pass (alter on orders allowed in dev)
  intent:         declared
  schema_impact:  +1 column (priority)

  state_modified: false
```

It's safe. The harness runs it for real (without `--dry-run`). Capcli records the schema change in the audit spine.

If the harness tries something stupid, like dropping a table with foreign keys pointing to it:

```bash
$ capcli sql "DROP TABLE customers" -m "cleaning up"
```

```text
[dev:tier_1]  ✗  exit 2

  FAIL  policy.schema.drop.referenced
        DROP TABLE customers
        ^^^^^^^^^^^^^^^^^^^^
        Table is referenced by foreign key: orders(customer_id).

  state_modified: false
  remedy: drop dependent tables first, or remove foreign key constraints
```

Glass wall. Intact.

---

## The "Oh Shit" Button (Snapshots)

Your harness is about to run a massive batch update. You're nervous. Tell it to take a snapshot first.

```bash
$ capcli db snapshot -m "before harness touches inventory pricing"
```

```text
[dev:tier_1]  ✓  snapshot created

  id:       snap_8f2a9c
  size:     14.2 MB
  tables:   14
  audit:    op_9a1b
```

The harness runs the batch update. It messes up. It halves all prices instead of increasing them by 10%. Panic? No.

```bash
$ capcli db restore snap_8f2a9c -m "reverting botched pricing update"
```

```text
[dev:tier_1]  ✓  restored

  snapshot:  snap_8f2a9c
  tables:    14 restored
  audit:     op_9a2c
```

State rewound. The audit log records the snapshot *and* the restore. Nothing is hidden.

---

## Moving to Sim and Prod

Eventually, the data and the routines need to go to production.

```bash
$ capcli env use sim
```

```text
[sim:tier_1]  env: sim
  workspace:  envs/sim/workspace.db
  note:       prod-only API verbs physically denied here
```

In `sim`, the harness rehearses against mocked API fixtures and production-shaped data.
In `prod`, the harness is on a tight leash. Draft routines can't run. Unbounded writes are physically impossible.

You don't touch `prod` until the harness has proven it won't break things in `sim`.

---

## The one rule

**The harness never touches the SQLite file directly.**

No `sqlite3 workspace.db`. No raw Python `sqlite3` imports. Everything goes through `capcli sql` or `capcli db`.

If the harness bypasses Capcli, it bypasses the authorizer, the budget, and the audit spine. Capcli's lockfile and file permissions (`chmod 600`) make this structurally difficult, but the rule is absolute: *Capcli is the only door to the data.*

---

**Hit a boundary?** → [boundaries.md](boundaries.md)

**Want to know what the harness actually did?** → [audit.md](../understand/audit.md)
