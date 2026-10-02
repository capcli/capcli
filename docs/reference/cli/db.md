# Command: capcli db

The storage path — one unified SQL surface, lease locks, schema introspection, and snapshots.

```bash
capcli sql "<query>" [-p k=v] [-m "<intent>"] [--dry-run]
capcli db <verb> [args] [--flags]
```

## Subcommands

| Verb | Syntax | Caller | Description |
|---|---|---|---|
| **sql** | `capcli sql "<query>" [-p k=v] [-m "<intent>"] [--dry-run]` | [both] | Unified read/write — the AST layer classifies the statement, the authorizer gates it. |
| **lock** | `capcli db lock <table>:<ref> --ttl <duration> --reason "..."` | [both] | Acquires a lease claim for multi-step operations. |
| **unlock** | `capcli db unlock <target>` | [both] | Releases a lease. |
| **schema** | `capcli db schema [--table]` | [both] | Displays the compiled DDL for the workspace. |
| **snapshot** | `capcli db snapshot` | [both] | Creates a transactionally clean point-in-time copy (`VACUUM INTO`). |
| **restore** | `capcli db restore <id>` | [both] | Atomically reverses database state to a snapshot. |
| **dump** | `capcli db dump` | [both] | Exports database state. |

## Unified SQL

There is one SQL surface. Reads dispatch read-only; writes cross the full [AST + authorizer pipeline](../../concepts/authorizer.md) and require intent:

```bash
# Read: free, bounded
$ capcli sql "SELECT ref, total_cents FROM orders WHERE status = 'pending' LIMIT 10"

# Write: bounded + declared
$ capcli sql "UPDATE orders SET status = 'processing' WHERE id = 'ord_9885' LIMIT 1" \
    -m "start fulfillment on oldest pending order"
```

Bound violations return [exit 2](../exit-codes.md#exit-2) with the measured blast radius cited — [denial anatomy](../exit-codes.md#fail-payload).

## Locks: leases, not locks

`db lock` writes a TTL lease into the `claims` system table ([schemas.md](../schemas.md)). If the holder crashes mid-run, the daemon's sweeper expires the lease — no orphaned locks, no deadlocks. The same lease rides a run invocation via the scoped `--lock <ref>` flag ([run.md](run.md)).

## Snapshots & recovery

Snapshots are `VACUUM INTO` copies taken automatically before every physical schema migration — restore is instant local rollback. The full recovery ladder (snapshot → git revision → offsite archive) is covered in [recovery.md](../../concepts/recovery.md); backup cadence and drift alarms are [governed](../limits.md#rate-governance).

## Invariants

* UPDATE and DELETE require `WHERE` and `LIMIT`; unbounded mutations die at parse time — [blast-radius caps](../limits.md#database-ceilings).
* Bulk operations in prod demand a pre-count; dev and sim waive it ([limits](../limits.md#database-ceilings)).
* System tables are read-only — the protection matrix is in [schemas.md](../schemas.md).
* DDL never runs through `sql` — schema changes are YAML edits compiled via [`capcli apply`](rule.md).
* Raw `workspace.db` access is denied; the kernel daemon is the sole gateway.

## Banned verbs

* `capcli db count` / `capcli db query` / `capcli db exec` → **retired.** Use the unified `capcli sql`.
* `capcli claim` → **retired.** Use `db lock` or `run --lock`.
