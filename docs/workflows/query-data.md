# Work With Your Data

Your harness loves your data. It wants to aggregate it, join it, and occasionally `DROP` it because it misinterpreted a pronoun. Capcli puts a glass wall between your agent and the SQLite file: the harness can look, it can touch, but only through the kernel. `capcli sql` is the only door — no `sqlite3 workspace.db`, no raw Python `sqlite3` imports. Bypass Capcli and you bypass the authorizer, the budget, and the audit spine, so the lockfile and file permissions (`chmod 600`) make it structurally difficult.

## Where data lives

`capcli env current` → `env: dev · workspace: envs/dev/workspace.db · 14 tables, 3 views`.

You're in `dev` — the environment where the harness is allowed to make mistakes. Sim and prod are separate worlds ([environment theory](../concepts/environments.md)). Need the shape first? `capcli db schema --table orders`, or `capcli inspect db://orders` ([discover.md](discover.md)).

## Read: free, bounded

Reads don't need intent. They're free — bounded, but free.

```bash
$ capcli sql "SELECT id, total, status FROM orders WHERE status = 'pending' LIMIT 10"
```

AST checked it. [Authorizer](../concepts/authorizer.md) allowed it. SQLite executed it — `✓ 12ms · rows: 10`. Rows came back. (SELECT ceiling: [limits](../reference/limits.md#database-ceilings).)

## Write: intent required

**Writes need intent. Reads don't.** Every mutating command takes `-m` — the causal motivation that lands in the audit trail. No `-m`, no write:

```bash
$ capcli sql "UPDATE orders SET status = 'processing' WHERE id = 'ord_9885' LIMIT 1" \
    -m "mark oldest pending order as processing"
```

```text
[dev:tier_1]  ✓  18ms
  rows_affected: 1  ·  ops_used: 1/50  ·  audit: op_4f8a
```

Forgot the `-m`?

```text
[dev:tier_1]  ✗  exit 3
  FAIL  policy.query.writes_require_intent
        Mutating write without causal intent declaration.
  state_modified: false · remedy: add -m "why you're doing this"
```

[Exit 3](../reference/exit-codes.md#exit-3), every time. The kernel doesn't care *what* your intent is. It cares that you *have* one — the audit trail demands causality.

Long intent? Skip the shell-escaping lottery: `-m @intent.txt` reads a file, `-p data=@payload.json` does the same for params, and `@-` pulls from stdin. It also bypasses ARG_MAX.

## Dry-run: what would happen?

Before you mutate, see the plan — same command, plus `--dry-run`:

```bash
$ capcli sql "UPDATE orders SET status = 'shipped' WHERE status = 'processing' LIMIT 50" \
    -m "batch ship processing orders" --dry-run
```

```text
[dev:tier_1]  dry-run  ✓
  ast_check: pass  ·  authorizer: pass  ·  intent: declared
  estimated_rows: 34  ·  blast_radius: bounded (LIMIT 50)
  state_modified: false
```

You see the plan. Nothing touched. Happy? Run it again without `--dry-run`.

## Locks: exclusive access

Multi-step operations that can't be interrupted take a lease:

```bash
$ capcli run reconcile_inventory -p warehouse=WEST -m "nightly warehouse reconciliation" \
    --lock inventory:WEST --ttl 300
```

The lock is a lease in `_claims` — acquired, held for the run, released on exit. Crash mid-run and it expires after TTL. No orphaned locks. No deadlocks.

## Snapshots & restore: the "Oh Shit" button

Big batch update coming. You're nervous. Snapshot first:

```bash
$ capcli db snapshot -m "before harness touches inventory pricing"
```

```text
[dev:tier_1]  ✓  snapshot created  ·  snap_8f2a9c  ·  14.2 MB  ·  14 tables
```

The harness runs the batch. It halves all prices instead of raising them 10%. Panic? No.

```bash
$ capcli db restore snap_8f2a9c -m "reverting botched pricing update"
```

```text
[dev:tier_1]  ✓  restored  ·  snap_8f2a9c  ·  14 tables
```

State rewound. The audit spine records the snapshot *and* the restore. Nothing is hidden. ([Recovery theory](../concepts/recovery.md).)

## Changing the shape

Schema changes don't happen through ad-hoc DDL from your agent. Edit `schema.yaml`, then apply:

```bash
$ capcli apply -m "add priority flag for rush shipping"
```

`capcli apply` is the alias for `capcli rule apply schema` — the [compiler](../concepts/compiler.md) diffs `schema.yaml` against the live database, generates the DDL, and records every migration in the audit spine. Add `--dry-run` to preview first. ([rule syntax](../reference/cli/rule.md) · [db syntax](../reference/cli/db.md).)

## Moving to sim and prod

```bash
$ capcli env use sim                                    # rehearse against masked, production-shaped data
$ capcli env merge prod -m "quarterly schema migration" # when sim proof is in
```

In prod, draft writes are denied outright — unproven code can't touch it. ([Environments](../concepts/environments.md).)

Hit a wall? [Every exit code, decoded](../reference/exit-codes.md). Want to see what the harness actually did? → [reference/audit.md](../reference/audit.md)
