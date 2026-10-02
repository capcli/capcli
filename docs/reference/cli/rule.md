# Command: capcli rule

Compiles, validates, diffs, and applies the declarative YAML blueprints — `schema.yaml`, `system-schema.yaml`, `policy.yaml`, `governance.yaml`. Configuration is code: blueprints are compiled into the `capcli.lock` hash, never interpreted at runtime. The compiler theory lives in [compiler.md](../../concepts/compiler.md); this page is the verb surface.

```bash
capcli rule <verb> [target] [--flags]
```

## Subcommands

| Verb | Syntax | Caller | Description |
|---|---|---|---|
| **show** | `capcli rule show [target=schema\|policy\|governance]` | [both] | Dumps the compiled rules for the active workspace. |
| **diff** | `capcli rule diff [target=schema] [--git]` | [both] | Compares working-tree YAML against Git HEAD or the live database PRAGMAs. |
| **apply** | `capcli rule apply [target=schema] [--dry-run] -m "<why>"` | [both] | Runs the compiler and executes forward DDL migrations. |
| **validate** | `capcli rule validate` | [both] | Offline CI gate — syntax and acyclic-relation check with no kernel required. |

**Ergonomic alias:** `capcli apply` is exactly `capcli rule apply schema`.

## What apply does

One sentence: your YAML passes the [5-gate compiler](../../concepts/compiler.md) — syntax, semantics, manifest lock, live drift, migration safety — and lands as deterministic DDL inside a snapshot-paired transaction. Any gate failure is an [exit 3](../exit-codes.md#exit-3) with the state untouched. `--dry-run` prints the exact physical SQL without mutating anything.

The micro-DDL shorthand (`pk`, `int~`, `mask=true`, …) is expanded in [schemas.md](../schemas.md) — the expansion table lives there, not here.

## Invariants

* A single byte of drift between the YAML on disk and `capcli.lock` refuses boot in prod and sim ([lockfile law](../limits.md#invariants)).
* DDL trust floors apply: `ALTER` requires reviewed, `DROP` is denied, `VACUUM` requires pinned — [blast-radius caps](../limits.md#database-ceilings).
* Schema shape ceilings (tables, columns, indexes, views) → [limits](../limits.md#workspace-storage).
* Migrations are forward-only; snapshots serve as the rollback path ([recovery.md](../../concepts/recovery.md)).
* `system-schema.yaml` is kernel-owned — direct apply is banned; it changes only via kernel releases.

## Banned operations

* `capcli config set` → **banned.** Dynamic policy mutation is forbidden — edit the YAML and git commit.
* Manual DDL (`capcli sql "ALTER TABLE ..."`) → **banned.** All DDL originates from `schema.yaml` through this noun.
