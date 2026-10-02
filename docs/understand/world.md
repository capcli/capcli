# World

You type `capcli` in a directory. Behind the curtain, a "World" boots.

Fancy name. Simple idea: **a World is Capcli's governed workspace — the database, the schema, the routines, the audit spine, the whole state domain where work happens.** One folder. One story. Zero ambiguity about what's real.

---

## Check what world you're in

```bash
$ capcli env current
```

```text
[dev:tier_1]  env: dev
  workspace:  envs/dev/workspace.db
  schema:     14 tables, 3 views
  trust:      draft baseline
```

That's it. You're in `dev`. The state you're allowed to break lives at `envs/dev/workspace.db`. The schema describing it is compiled from `schema.yaml`. Every mutation is hashed into the audit spine inside the same file.

One SQLite file is the single source of truth for *both* your orders *and* the receipt that you touched them. Reality and its paper trail, holding hands. Forever.

---

## What's actually in there?

| Thing | What it is | Can your agent touch it directly? |
|---|---|---|
| `workspace.db` | SQLite WAL database — domain tables + `_audit` | **No.** Kernel-mediated only. chmod 600. |
| `schema.yaml` | Declarative domain schema (tables, views) | Yes — in dev, that's its job. |
| `policy.yaml` / `governance.yaml` | Behavioral + structural law | Edit and git-commit. Never mutated at runtime. |
| `capcli.lock` | Compiled hash of all of the above | No. Touch it and boot refuses (`exit 3`). |
| `routines/` | Versioned capability scripts | Yes — author, prove, ship. |
| `world.sql` | Reproducible DDL + seed dump | Auto-committed after migrations. |

Your agent can *propose* changes to almost all of it. It can *directly execute* precisely none of it. There's a difference, and that difference is the entire product.

---

## Starting from nothing

A World doesn't need to pre-exist for you to start. Blank directory? The first `rule apply` compiles `schema.yaml`, and the genesis sequence writes the first four events into `_audit`: rule applied, first read, first denial, first allowed write.

```text
genesis: rule.apply → sql.query (read) → sql.query (denied write) → sql.query (ok write)
```

A world is born with a scar. Its first act is getting told "no." If that isn't parenting, what is?

---

## World is not the explanation for everything

Here's the trap: "World" is a container word. It tells you *where*, never *why*.

- Why was the write denied? That's [trust.md](trust.md).
- Why did the task yield? That's [budgets.md](budgets.md).
- Why can't the agent see secrets? That's [identity.md](identity.md).
- What even happened? That's [audit.md](audit.md).

The World holds the stage. The physics runs the play.

---

## One folder per environment

Worlds are partitioned: `envs/dev/`, `envs/sim/`, `envs/prod/`. Separate databases, separate rate buckets, separate trust baselines.

```bash
$ capcli env list
```

```text
[dev:tier_1]  2 envs

  env    workspace             trust       last_activity
  ─────  ────────────────────  ──────────  ─────────────────
  dev    envs/dev/workspace.db  draft       2 minutes ago
  sim    envs/sim/workspace.db  reviewed    3 days ago
```

Ruining `dev` is a rite of passage. Ruining `sim` is a drill. Ruining `prod` is *structurally impossible* without a pinned routine and a deliberate `-m`. Details → [environments.md](environments.md).

---

**How messy sketches become structure** → [structure.md](structure.md)

**What you can actually run in a World** → [capabilities.md](capabilities.md)
