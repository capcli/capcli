# Command: `capcli env`

The world path: provision, switch, inspect, promote, and deprovision environments. Five isolated worlds maximum — because "spin up another staging" is how companies end up with eleven stagings and zero trust in any of them.

```bash
capcli env <verb> [args] [--flags]
```

---

## Subcommands

| Verb | Syntax | Caller | Description |
|---|---|---|---|
| **`new`** | `capcli env new <name> [--seed prod] [--from <path\|git-url\|ptr>] [--from-branch <b>]` | `[harness]` | Provisions a fresh world, optionally seeded with masked prod data. |
| **`use`** | `capcli env use <name>` | `[harness]` | Switches the active world. |
| **`list`** | `capcli env list` | `[harness]` | Enumerates worlds, trust baselines, and last activity. |
| **`inspect`** | `capcli env inspect` | `[harness]` | Dives into the active world's surfaces. |
| **`current`** | `capcli env current` | `[harness]` | One-glance banner: env, workspace, schema, trust baseline. |
| **`doctor`** | `capcli env doctor` | `[harness]` | Per-world health (drift, commits, mirror lag). |
| **`merge`** | `capcli env merge <name> [target=prod] -m "<why>"` | `[human]` | Promotes a world's state toward another (audited, receipted). |
| **`remove`** | `capcli env remove <name> [--confirm-backup] [--confirm-prod]` | `[human]` | Deprovisions a world. The double-confirm on prod is not decorative. |

---

## Live examples

```bash
$ capcli env current
```

```text
[dev:tier_1]  env: dev
  workspace:  envs/dev/workspace.db
  schema:     14 tables, 3 views
  trust:      draft baseline
```

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

```bash
$ capcli env use sim
```

Switching re-stamps every subsequent output prefix — `[sim:tier_1]` from here on, on every line, so nobody ever asks "wait, which database was that?" during a post-mortem again.

## Seeding rules

- `--seed prod` into `sim` applies **format-preserving masking** (`mask=true` columns) — real shapes, fake blood, zero real customers harmed.
- `--from <git-url|ptr>` imports world templates; imports enter at **draft trust with zero promotional credit**. Pre-pinned imports are banned. "It worked in the other repo" is archaeology, not evidence.
- Seed rows cap at 50/table — a template is a skeleton, not a data exfiltration vehicle.

## The prod removes

```bash
$ capcli env remove prod --confirm-backup --confirm-prod
```

Two explicit flags. The command is `[human]`-gated. Deleting production is allowed *exactly once* per invocation, with receipts — like all irreversible things here, it's structured, confirmed, and recorded in the spine.

---

**Narrative** → [../../understand/environments.md](../../understand/environments.md) · **World concept** → [../../understand/world.md](../../understand/world.md)
