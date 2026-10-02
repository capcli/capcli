# Migration: Changing the World Without a Fire Drill

Schema change day in a normal shop: someone runs `ALTER TABLE` in a terminal at 5pm, the migration locks the table for forty minutes, and everyone pretends the rollback script exists. In Capcli, schema lives in one declarative file, changes travel through a compiler with five gates, and rollback is a snapshot restore. Here is the entire supported path.

---

## 1. The one law: no manual DDL

`ALTER TABLE` through `capcli sql` is banned. `DROP TABLE` is banned. Manual DDL is how schemas drift, and drift is how audits stop meaning anything:

```bash
$ capcli sql "ALTER TABLE orders ADD COLUMN priority TEXT DEFAULT 'standard'" \
    -m "add priority flag"
```

```
[dev:tier_1]  ✗  exit 2

  FAIL  policy.authorizer.manual_ddl_denied
        ALTER TABLE orders ADD COLUMN priority TEXT DEFAULT 'standard'
        ^^^^^^^^^^^^^
        Manual DDL is banned. All schema change originates in schema.yaml.

  state_modified: false
  layer: authorizer
  remedy: edit schema.yaml, then run capcli rule apply schema
```

Even if it weren't banned, the lockfile would bite you: DDL that doesn't come from the compiler doesn't match `capcli.lock`. There is one door. Use it.

---

## 2. Edit `schema.yaml`

You want `orders` to carry a priority. Open the agent-owned file and say so:

```yaml
tables:
  orders:
    columns:
      priority: text='standard'     # new
```

Bump the `version` root while you're in there. That is the entire manual step.

---

## 3. See the drift: `rule diff`

Before compiling anything, look at what you actually changed — working YAML against git HEAD:

```bash
$ capcli rule diff schema --git
```

```
[dev:tier_1]  rule diff (schema, vs HEAD)  ✓  1 change

  version:   14 → 15
  columns:   orders + priority (text, default 'standard')
  live_db:   0 undeclared columns (PRAGMAs match HEAD)
```

Drop `--git` and the same command diffs your YAML against the live database's PRAGMAs — Gate 4's check, available on demand.

---

## 4. Preview the exact DDL: dry-run

```bash
$ capcli rule apply schema --dry-run
```

```
[dev:tier_1]  rule apply (schema)  ✓  dry-run

  plan:      ALTER TABLE orders ADD COLUMN priority TEXT DEFAULT 'standard';
  snapshot:  snap_migration_043 would be created first
  rollback:  DDL test transaction reverses cleanly on snapshot

  state_modified: false
```

This is the artifact a human reviews before anything ships: the exact physical SQL, and proof the snapshot path works. No state changes yet.

---

## 5. Apply through the 5-Gate Compiler

```bash
$ capcli rule apply schema -m "add priority flag for rush shipping"
```

```
[dev:tier_1]  rule apply (schema)  ✓  migrated v14 → v15

  gate_1:  syntax — YAML parsed, shorthands expanded
  gate_2:  semantics — graph acyclic, compile order resolved
  gate_3:  manifest — capcli.lock verified, re-locked
  gate_4:  live drift — 0 undeclared columns vs PRAGMAs
  gate_5:  migration safety — DDL proven on snap_migration_043, rollback verified
  ddl:     1 statement, one transaction
  audit:   op_5c11 → op_5c12
```

The gates, in order: **Syntax** (valid YAML, clean shorthand expansion), **Semantics** (petgraph rejects circular references), **Manifest Lock** (hashes vs `capcli.lock`), **Live Drift** (PRAGMA scan vs declarations), **Migration Safety** (the DDL dry-runs in an isolated transaction on a snapshot, and the rollback must reverse cleanly). Any gate fails → `exit 3`, nothing changed, snapshot auto-restored. In CI, `capcli rule validate` runs the offline checks before a commit even reaches a human.

Note the snapshot in the output. It was taken *before* the DDL ran. That's not a courtesy — that's your rollback.

---

## 6. There is no down-migration

Forward only. Down-migrations are banned by invariant, so the rollback for a bad migration is the Gate 5 snapshot pairing:

```bash
$ capcli db restore snap_migration_043 -m "revert schema v15"
```

```
[dev:tier_1]  ✓  state restored

  active_db:  envs/dev/workspace.db (restored to snap_migration_043)
  audit:      op_5c19
```

Then fix `schema.yaml`, bump again, apply again. The version line only moves forward; reality can still rewind.

---

## 7. Promote to prod: `env merge`

Dev has v15 and the evidence that it works. Prod still has v14. One command moves the world — and it refuses to move without git:

```bash
$ capcli env merge dev prod -m "schema v15: orders.priority"
```

```
[prod:tier_1]  env merge (dev → prod)  ✓  schema v15 live

  git:       branch merged, remote push verified
  snapshot:  snap_prod_pre_merge_77b2 (prod DB snapshotted first)
  ddl:       forward diff applied (v14 → v15)
  lockfile:  capcli.lock re-locked
  audit:     op_6a01 → op_6a02 → op_6a03
```

The merge snapshots prod, merges the git branch, applies the forward DDL diff, and re-locks the lockfile. Cross-world DDL without a git merge is denied outright. And run it from a Tier 1 host — prod promotion doesn't happen on Tier 2 machines.

---

## The one rule

**Schema is declared, compiled, and forward-only.** You edit YAML, the compiler proves it, a snapshot catches you, and git carries it to prod. Nobody types DDL at a database ever again.

---

**Exact `rule` command contracts?** → [reference/commands/rule.md](../reference/commands/rule.md)

**How the five gates think?** → [concepts/compiler.md](../concepts/compiler.md)

**Need to rewind a migration?** → [recovery.md](recovery.md)
