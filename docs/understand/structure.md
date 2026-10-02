# Structure

Your agent's first hour in a new World is improv theater: bounded reads, bounded writes, the occasional denied `DELETE` that teaches it manners. That's fine. Exploration is what `dev` is for.

But loose is not a destination. A table shape that exists only in your harness's chat history is a shape nobody can inspect, validate, or replay. At some point, the World itself has to know what it contains — and this page is about that turn: how something exploratory becomes explicit, structured, and inspectable.

---

## 1. The Turn: Write It Down

The signal is repetition. Your agent keeps selecting from the same three tables with the same joins. So you stop improvising the shape and declare it — not in SQL, in YAML:

```yaml
# schema.yaml — the file you own
tables:
  orders:
    description: "Transactional order root with discount integrity trigger"
    prov: true                        # kernel stamps created_by / modified_by
    columns:
      id: pk                          # integer autoincrement primary key
      ref: text!                      # unique, required text
      customer_id: int ref=customers.id
      total_cents: int=0
      status: text=pending
    chk:                              # physical SQLite CHECK constraints
      - "status IN ('pending', 'processing', 'completed', 'cancelled')"
    idx:
      - [ref]                         # index on ref
```

Read that back. Every line is a decision the kernel can enforce:

* **`description`** is mandatory. A table that can't be described can't be searched, and unsearchable means unregistrable.
* **`prov: true`** turns on provenance columns — the kernel injects `created_by` and `modified_by` on every write.
* **Shorthands** carry real semantics: `pk`, `text!` (unique), `int~` (write-once immutable), `ref=` (foreign key), `mask=true` (anonymized in sim forks).
* **`chk:`** and **`trig:`** compile into physical SQLite constraints and kernel-vetted triggers.

---

## 2. Reading the Shape Back

Declared structure is inspectable structure. You never parse a migration file or interrogate the database by hand:

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

Need the details of one table? Ask for it:

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

Your harness reads this, builds correct SQL, and moves on. Nobody memorizes a schema that can be queried in 12ms.

---

## 3. The Compiled View

The deeper question isn't "what tables exist" — it's "does the live database still match the declaration?" That's `rule show`:

```bash
$ capcli rule show schema
```

```text
[dev:tier_1]  schema  ✓  compiled v14

  source:       schema.yaml (agent-authored · 14 tables · 3 views)
  system:       system-schema.yaml (kernel-owned · hash verified)
  unified_ddl:  workspace.db (single compiled DDL)
  drift:        0 undeclared columns · 0 undeclared tables
  lockfile:     capcli.lock verified
```

Two files, two owners, one DDL. Your YAML compiles into the physical database; PRAGMA checks compare the live tables against the declaration; the lockfile pins the compiled hashes so prod can't drift silently. If undeclared columns show up, the kernel treats that as drift and refuses to carry on — see the gates below.

---

## 4. The Gates: Validation Is the Bouncer

Declarations don't get the benefit of the doubt. Every schema passes five gates before it touches reality:

| Gate | When | Catches | Fail |
|---|---|---|---|
| **1. Syntax** | parse-time | broken YAML, shorthands that don't expand | `exit 3` |
| **2. Semantics** | compile-time | dangling `ref=` targets, circular references, scoped views missing `:principal` | `exit 3` |
| **3. Manifest lock** | boot (prod/sim) | compiled hash ≠ `capcli.lock` | refuse boot |
| **4. Live drift** | `sys doctor` | undeclared columns or tables in the live DB | `exit 3` |
| **5. Migration safety** | apply-time | DDL that won't cleanly roll back on a snapshot | auto-restore, `exit 3` |

And there are hard ceilings on the declared shape itself: max 100 agent-authored tables, 30 columns per table, 10 indexes, 50 views, and at most 50 seed rows per table. Structure is welcome; sprawl is not.

---

## 5. Changing the Shape

Structure isn't frozen — it's versioned. The lifecycle is the same every time: edit `schema.yaml`, bump the version, preview, apply:

```bash
$ capcli rule apply schema --dry-run -m "add priority column for rush shipping"
```

```text
[dev:tier_1]  dry-run  ✓

  plan:      ALTER TABLE orders ADD COLUMN priority INTEGER DEFAULT 0
  gate_5:    test migration on snapshot passed (rollback verified)
  snapshot:  verified (no mutation)

  state_modified: false
  note:           no execution occurred
```

The dry-run prints the exact physical DDL the compiler will execute — YAML in, SQL out, and only now does SQL enter the picture at all. Apply it for real and the kernel snapshots first, executes in a transaction, and emits a schema migration event into the ledger. Two invariants are worth memorizing:

* **Raw DDL is banned.** `capcli sql "ALTER TABLE ..."` doesn't work — all DDL originates from `schema.yaml`. There is one front door, and you're looking at it.
* **Migrations are forward-only.** There are no down-migrations. Snapshots are the rollback — see [recovery.md](recovery.md).

The full walk-through of evolving a World without tears lives in [guides/migration.md](../guides/migration.md), and the exact command contracts in [reference/commands/rule.md](../reference/commands/rule.md).

---

## The One Rule

**Structure is declared, compiled, and diffed — never accumulated.**

If it isn't in `schema.yaml`, it isn't in the World. And if it's in the World but not in the file, the kernel refuses to pretend that's fine.

---

**Where this compiled World physically lives** → [world.md](world.md)

**How declared tables become searchable capabilities** → [capabilities.md](capabilities.md)
