# Command: `capcli db`

Where the World keeps its truth — and the only door to it.

The storage path noun. One SQLite file (`workspace.db`) holds domain state *and* the audit spine, and nothing touches it except the kernel. Every verb here crosses the same AST and authorizer layers as `run` — there is no side door, and the file is `chmod 600` in case you get ideas.

```bash
capcli db <verb> [args] [--flags]
```

---

## Subcommands

| Verb | Syntax | Description |
|---|---|---|
| **`sql`** | `capcli db sql "<statement>" [-p k=v] [-m "intent"] [--dry-run]` | Unified read/write via AST detection. `SELECT` runs read-only, no intent required; `INSERT`/`UPDATE`/`DELETE` enforce bounds and demand `-m`. |
| **`lock`** | `capcli db lock <table>:<ref> --ttl <duration> --reason "..."` | Acquires an exclusive lease recorded in `_claims`. |
| **`unlock`** | `capcli db unlock <target>` | Releases a lease before its TTL expires. |
| **`schema`** | `capcli db schema [--table <name>]` | Dumps the table roster, or one table's compiled shape. |
| **`snapshot`** | `capcli db snapshot -m "<why>"` | Atomic `VACUUM INTO` copy of the live database. |
| **`restore`** | `capcli db restore <id> -m "<why>"` | Rewinds state to a snapshot. The rewind itself is audited. |
| **`dump`** | `capcli db dump` | Full export of the world's state. One of the four verbs allowed in recovery mode. |

---

## 1. Locks: Leases, Not Prayers

Multi-step work that can't be interrupted takes a lease. If your harness dies mid-run, the TTL expires it — no orphaned locks, no deadlocks, no 2 AM phone call.

```bash
$ capcli db lock inventory:WEST --ttl 300 --reason "nightly warehouse reconciliation"
```

```text
[dev:tier_1]  ✓  lock acquired

  target:    inventory:WEST
  ttl:       300s
  lease:     recorded in _claims (auto-expired by daemon tick)
  audit:     op_7a1b
```

```bash
$ capcli db unlock inventory:WEST
```

```text
[dev:tier_1]  ✓  lock released

  target:    inventory:WEST
  audit:     op_7a2c
```

The same lease is available inline on the hot path: `capcli run <capability> --lock <ref> --ttl <duration>` acquires, runs, and releases in one command. For the unified `sql` verb and its gate-by-gate walkthrough, see [run.md](run.md) — same gates, same physics.

---

## 2. Know the Shape: `db schema`

Your harness doesn't read `.sql` files. It asks.

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

Bare `capcli db schema` lists every table with rows, columns, indexes, and constraints. The harness reads this, drafts the SQL, and runs it. You never memorize your own schema — and neither does it.

---

## 3. The "Oh Shit" Button: `snapshot` / `restore`

Snapshots are native SQLite `VACUUM INTO`: transactionally clean, byte-identical copies taken while readers keep reading and writers keep writing. The kernel takes them automatically before every schema migration, before world merges, and every 15 minutes via background maintenance — you only take one manually when *you're* about to do something brave.

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

The harness halves every price instead of raising them. Panic? No:

```bash
$ capcli db restore snap_8f2a9c -m "reverting botched pricing update"
```

```text
[dev:tier_1]  ✓  restored

  snapshot:  snap_8f2a9c
  tables:    14 restored
  audit:     op_9a2c
```

State rewound. The audit ledger records the snapshot *and* the restore — you don't hide the mistake, you log the recovery. Rollback is the snapshot; down-migrations don't exist.

---

## Banned Operations

* **`db count`, `db query`, `db exec`** ➔ **Retired. Banned.** Use the unified `sql` — AST detection decides read from write. There is exactly one query surface, not three.
* **`claim`** ➔ **Banned.** Use `db lock` or `run --lock`.
* **Manual DDL** (`sql "ALTER TABLE ..."`, `DROP TABLE`) ➔ **Banned.** All schema change originates in `schema.yaml` and ships through the 5-Gate compiler — see [rule.md](rule.md).
* **ORMs and query builders** ➔ **Banned.** Raw SQL crosses the authorizer directly; generated SQL just crosses it more expensively.
* **Direct file access** ➔ `workspace.db` sits behind the kernel daemon with `chmod 600`. `sqlite3 workspace.db`, raw drivers, and external ORM sockets are denied at the perimeter. Capcli is the only door to the data.

---

**Working with your data, in prose** → [../../use/work-with-your-data.md](../../use/work-with-your-data.md)

**Snapshot mechanics and break-glass** → [../../understand/recovery.md](../../understand/recovery.md)

**Schema changes go through the compiler** → [rule.md](rule.md)
