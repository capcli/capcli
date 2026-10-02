# Command: `capcli rule`

Compiles, validates, diffs, and applies declarative YAML schemas and governance bounds.

```bash
capcli rule <verb> [target] [--flags]
```

---

## Subcommands

| Verb | Syntax | Description |
|---|---|---|
| **`show`** | `capcli rule show [target=schema\|policy\|governance]` | Dumps compiled AST rules for the active workspace. |
| **`diff`** | `capcli rule diff [target=schema] [--git]` | Compares working directory YAML against Git HEAD or live DB PRAGMAs. |
| **`apply`** | `capcli rule apply [target=schema] [--dry-run] -m "<why>"` | Runs the 5-Gate Compiler and executes forward DDL migrations. |
| **`validate`**| `capcli rule validate` | Offline CI gate verifying syntax and acyclic relations. |

*(Ergonomic alias: `capcli apply` directly aliases `capcli rule apply schema`)*.

---

## In Practice

```bash
$ capcli rule apply schema --dry-run -m "add priority column"
```

```text
[dev:tier_1]  rule apply (schema)  ✓  dry-run

  gate_1:  syntax — YAML parsed, shorthands expanded
  gate_2:  semantics — graph acyclic, compile order resolved
  gate_3:  manifest — capcli.lock verified
  gate_4:  live drift — 0 undeclared columns vs PRAGMAs
  gate_5:  migration safety — DDL proven on snapshot, rollback verified

  plan:      ALTER TABLE orders ADD COLUMN priority TEXT DEFAULT 'standard';
  snapshot:  snap_migration_043 would be created first

  state_modified: false
  note:           no DDL applied — dry-run
```

All five gates fire; none of the DDL does. Drop `--dry-run` and the same plan executes in one transaction behind a fresh snapshot — gates re-run for real, state advances, the chain gets its `rule.apply` event.

---

## The 5-Gate Compiler Pipeline

1. **Gate 1: Syntax:** Validates YAML structure and expands shorthand DDL keywords. Throws `exit 3` on failure.
2. **Gate 2: Semantics:** Constructs relational graph via `petgraph`. Cycle detection rejects circular foreign keys (`exit 3`).
3. **Gate 3: Manifest Lock:** Checks live SHA-256 hash against `capcli.lock`. Mismatch halts boot in prod/sim (`exit 3`).
4. **Gate 4: Live Drift:** Compares live SQLite table PRAGMAs against declarations. Undeclared columns throw `exit 3`.
5. **Gate 5: Migration Safety:** Dry-runs DDL on an isolated snapshot. Rollback failure aborts migration (`exit 3`).

---

## Shorthand DDL Expansions

| Shorthand | Expands To | Description |
|---|---|---|
| `pk` | `INTEGER PRIMARY KEY AUTOINCREMENT` | Auto-incrementing integer key. |
| `text pk` | `TEXT PRIMARY KEY` | String primary key. |
| `text!` | `TEXT NOT NULL UNIQUE` | Unique non-nullable string. |
| `int~` | `INTEGER` + Authorizer Write Lock | Write-once immutable column. |
| `text=val` | `TEXT DEFAULT 'val'` | Default text value. |
| `int ref=t.c` | `INTEGER REFERENCES t(c)` | Foreign key constraint. |
| `blob ref=storage` | `TEXT` (JSON object metadata) | Managed object store pointer. |
| `mask=true` | Authorizer redaction hook | Format-Preserving Anonymization in sim. |
| `imm_rows: true`| C Authorizer intercept | Disallows `UPDATE` and `DELETE` on table. |
| `imm_cols: [...]`| C Authorizer intercept | Disallows `UPDATE` on listed columns. |

---

## Banned Operations
* `capcli config set` ➔ **Banned.** Dynamic policy mutation is forbidden. Edit YAML and Git commit.
* Manual DDL (`capcli sql "ALTER TABLE..."`) ➔ **Banned.** All DDL must originate from `schema.yaml`.
