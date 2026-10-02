# Migration Guide

Your schema needs to change. In most stacks this is a horror anthology. Here it's a compile, a dry-run, and a receipt — because DDL that your autonomous agent can improvise is how companies meet their regulators.

One law above all: **all DDL originates from `schema.yaml`, through the 5-Gate compiler.** `capcli sql "ALTER TABLE …"` is banned, and the ban is enforced by the same physics that bans `DROP TABLE`.

---

## The procedure

**1. Edit `schema.yaml`.** Your harness does this in the dev worktree — it's agent-writable there. Shorthand keeps it terse:

```yaml
orders:
  id: text pk
  customer_id: int ref=customers.id
  total: int=val_0
  tracking: text
  note: text
```

**2. Validate offline (the CI gate):**

```bash
$ capcli rule validate
```

Syntax and acyclic relations, checked without touching state. Cycles in the FK graph die here — `exit 3`, Gate 2, via petgraph, before your database even knows you were thinking.

**3. Diff against reality:**

```bash
$ capcli rule diff schema --git
```

Working YAML vs Git HEAD and live PRAGMAs. You see exactly what will change, in order, with no "surprise column" theater.

**4. Dry-run the migration:**

```bash
$ capcli rule apply schema -m "add tracking + note to orders" --dry-run
```

```text
[dev:tier_1]  dry-run  ✓

  gates:       1 syntax ✓ · 2 semantics ✓ · 3 lock ✓ · 4 drift ✓ · 5 migration ✓
  tables:      +0 modified 1 (orders)
  ddl:         2 statements staged (ADD COLUMN ×2)

  state_modified: false
```

Gate 5 rehearsed the DDL on an isolated snapshot — if the rollback fails, the migration *aborts before starting*. "We'll fix the down-migration later" is not a plan the compiler accepts.

**5. Snapshot.** (Two seconds of insurance: [recovery.md](recovery.md).)

**6. Apply for real:**

```bash
$ capcli rule apply schema -m "add tracking + note to orders"
```

Forward-only DDL executes, `world.sql` auto-commits with readable diffs, `capcli.lock` re-hashes, the `rule.apply` event lands in the ledger. Down migrations are for disasters, not for mood swings — restore from snapshot instead.

---

## The gates, so you know what "no" means

| Gate | Checks | Failure |
|---|---|---|
| 1 Syntax | YAML structure, shorthand expansion | `exit 3` |
| 2 Semantics | Relational graph, FK cycles | `exit 3` |
| 3 Manifest Lock | SHA-256 vs `capcli.lock` | halts boot in prod/sim (`exit 3`) |
| 4 Live Drift | PRAGMAs vs declarations | `exit 3` |
| 5 Migration Safety | DDL dry-run + rollback on isolated snapshot | aborts (`exit 3`) |

Five chances to be wrong *cheaply*. The alternative is one chance to be wrong expensively, later, at 2am, in production. The gates are the friend who takes your car keys.

## Migration across environments

Dev compiles freely → `env merge` promotes toward prod (audited, `[human]`-gated, receipted) → sim/prod verify the lockfile at boot, so a config that drifted through Git games refuses to run. Schema evolution is *promoted with evidence*, like everything else here.

## Limits that keep migrations honest

100 agent-authored tables max; seed rows capped at 50/table (templates are skeletons, not data smugglers); undeclared live columns are Gate 4 refusals, not "probably fine."

---

**Why YAML is compiled at all** → [../concepts/compiler.md](../concepts/compiler.md) · **Exact verb table** → [../reference/commands/rule.md](../reference/commands/rule.md)
