# Command: `capcli db`

The storage path: schema introspection, lease locks, and point-in-time snapshots. Note what's *missing* — no `db query`, no `db exec`. Those retired verbs are banned; all querying flows through the unified [`capcli sql`](run.md), because two doors into one database is one door too many.

```bash
capcli db <verb> [target] [--flags]
```

---

## Subcommands

| Verb | Syntax | Caller | Description |
|---|---|---|---|
| **`schema`** | `capcli db schema [--table <name>]` | `[harness]` | Lists tables, or one table's columns, from the compiled declaration. |
| **`lock`** | `capcli db lock <table>:<ref> --ttl <duration> --reason "..."` | `[harness]` | Acquires an exclusive lease in `_claims`. |
| **`unlock`** | `capcli db unlock <target>` | `[harness]` | Releases a held lease early. |
| **`snapshot`** | `capcli db snapshot [-m "<why>"]` | `[harness]` | Hot point-in-time backup via SQLite `VACUUM INTO`. |
| **`restore`** | `capcli db restore <snap_id> -m "<why>"` | `[human]` | Restores database state from a snapshot. |
| **`dump`** | `capcli db dump` | `[human]` | Deterministic DDL + seed export (the `world.sql` shape). |

---

## Schema

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

Live `PRAGMA`s are cross-checked against `schema.yaml` at boot — drift is `exit 3` *before* it becomes 2am.

## Snapshot & restore

```bash
$ capcli db snapshot -m "before harness touches inventory pricing"
```

```text
[dev:tier_1]  ✓  snap_8f2a9c

  created:  2026-10-02T03:10:00Z
  size:     1.9 MB
  note:     before harness touches inventory pricing
```

`VACUUM INTO` is safe under active traffic — no torn pages, no `cp`-while-writing roulette. Restore:

```bash
$ capcli db restore snap_8f2a9c -m "reverting botched pricing update"
```

Point-in-time, receipt on file, ledger intact (the restore is itself an audited event — you can't restore your way out of history).

## Locks

Lease-based, TTL'd, reason-tagged. Crash = expiry = no ghost locks, no deadlocks. `db lock` replaces the retired `claim` verb, and `run --lock` covers the routine case in one flag.

## Banned verbs (documented on purpose)

- `capcli db count` / `db query` / `db exec` → **retired.** Use `capcli sql`.
- Manual DDL via `capcli sql "ALTER TABLE …"` → **banned.** All DDL originates in `schema.yaml` via the 5-Gate compiler ([rule.md](rule.md)).

---

**Narrative** → [../../use/work-with-your-data.md](../../use/work-with-your-data.md) · **Recovery deep-dive** → [../../understand/recovery.md](../../understand/recovery.md)
