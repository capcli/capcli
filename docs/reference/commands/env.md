# Command: `capcli env`

Spawning a universe is one command. Deleting production takes two keys.

The world path noun. Environments are isolated physical worlds — separate `workspace.db`, separate quota partitions, separate Git worktrees — not folders with different `.env` files and the same lies. Environment bounds data; trust bounds capabilities. The axes are orthogonal, and both are enforced.

```bash
capcli env <verb> [args] [--flags]
```

---

## Subcommands

| Verb | Syntax | Description |
|---|---|---|
| **`new`** | `capcli env new <name> [--seed prod] [--from <path\|git-url\|ptr>] [--from-branch <b>]` | Provisions an isolated world under `envs/<name>/`. |
| **`use`** | `capcli env use <name>` | Sets the sticky context every command targets. |
| **`list`** | `capcli env list` | Audits provisioned environments. |
| **`inspect`** | `capcli env inspect <name>` | Flags schema drift and data staleness per world. |
| **`doctor`** | `capcli env doctor` | Checks for unmerged production routines and stale sim seeds. |
| **`merge`** | `capcli env merge <name> [target=prod] [-m "<why>"]` | Atomic promotion: git merge, snapshot, forward DDL, lockfile re-lock. |
| **`remove`** | `capcli env remove <name>` | Deprovisions a world. Prod demands dual confirmation. |

---

## 1. Birth: `env new`

```bash
$ capcli env new sim --seed prod
```

```text
[sim:tier_1]  ✓  environment created

  env:        envs/sim/
  workspace:  envs/sim/workspace.db
  seeded:     from prod (masking enforced)
  fpa:        emails → anon_8812@sim.local · types stay valid
  worktree:   isolated git branch
  audit:      op_11d4
```

Seeding from prod applies Format-Preserving Anonymization: sensitive columns are scrambled into *valid* fake data — emails that pass RFC validation, cards that pass Luhn. Your agent rehearses against production-shaped reality without seeing one byte of human PII.

`--from` provisions from a world template (path, git URL, or pointer): the bundle passes Gates 1–2 before anything touches disk, unpacks strictly into a dev worktree, and caps seeds at 50 rows per table. Prod direct-init from a template is denied.

Ceiling: **5 concurrent environments** — `dev`, `sim`, `prod`, plus two experiment branches. The sixth world is a planning problem, not a command.

---

## 2. The Sticky Context: `env use`

```bash
$ capcli env use sim
```

```text
[sim:tier_1]  env: sim
  workspace:  envs/sim/workspace.db
  note:       prod-only API verbs physically denied here
```

`env use` sets the sticky context. Every subsequent command — `run`, `sql`, `inspect` — targets that world, and the `[env:tier]` prefix on every output line confirms it. The universal `--env <name>` flag overrides it for a single invocation without moving the sticky context.

---

## 3. Drift Patrol: `env doctor` / `env inspect`

```bash
$ capcli env doctor
```

```text
[dev:tier_1]  env doctor  ✓

  unmerged_prod_routines:  0
  schema_drift:            none
  sim_seed_age:            fresh (re-seed nag at 14d)
  environments:            3/5
```

`env inspect` goes deeper per world: schema drift, data staleness, what's unmerged. Sim data older than 14 days triggers a re-seed nag — a flight simulator running 2022 traffic is just a lie with a joystick.

---

## 4. Promotion: `env merge`

```bash
$ capcli env merge dev prod -m "promote dispatch pipeline v4 to production"
```

```text
[prod:tier_1]  ✓  merged

  source:    envs/dev/ (git branch merged)
  target:    envs/prod/
  snapshot:  taken before DDL (pre-merge safety)
  ddl:       forward diff applied
  lockfile:  re-locked
  push:      verified via git push --dry-run
  audit:     op_88b1
```

The merge pipeline is atomic: merge the git branch, snapshot the target database, apply the forward DDL diff, re-lock the lockfile. Two gates fire before any of it: prod merges require a Tier 1 host and verified remote push credentials. An unbacked world is refused on principle.

---

## 5. The 2-Key Submarine Rule: `env remove prod`

Deleting production requires two distinct confirmation keys, inserted simultaneously, like launching a missile from a submarine:

```bash
$ capcli env remove prod --confirm-backup --confirm-prod
```

```text
[prod:tier_1]  ✓  environment removed

  target:      envs/prod/
  backup_ref:  snap_prod_pre_destroy_99f1 (verified in object store)
  git_branch:  archived to refs/archive/prod-2026-10-01
```

* Forget `--confirm-backup`? Refused (`exit 3`). You must prove a verified backup snapshot exists offsite.
* Forget `--confirm-prod`? Refused (`exit 3`). You must explicitly acknowledge you are destroying production.
* Try `-f` or `--force`? **Syntax error.** Brute-force flags are permanently banned.

---

## Invariants & Rules

* **Max 5 concurrent environments.** The ceiling is structural, not advisory.
* **Draft writes are physically denied in prod.** Unproven code cannot touch live state. No flag changes this.
* **No world exists unbacked** — git and object-store push are required on mutation.
* **FPA masking is enforced on every prod seed.** Sim never sees real PII, by physics rather than by promise.
* **`--force` is a syntax error anywhere on this noun.** Destruction is a ceremony, not an accident.

---

**The full environments mental model** → [../../understand/environments.md](../../understand/environments.md)

**Worlds and the storage trinity** → [../../understand/world.md](../../understand/world.md)

**Run things inside a world** → [run.md](run.md)
