# Command: capcli env

World management — provision, switch, inspect, merge, and deprovision isolated environments. The theory of the three worlds lives in [environments.md](../../concepts/environments.md).

```bash
capcli env <verb> [args] [--flags]
```

## Subcommands

| Verb | Syntax | Caller | Description |
|---|---|---|---|
| **new** | `capcli env new <name> [--seed prod] [--from <path\|git-url\|ptr>] [--from-branch <b>]` | [both] | Provisions an isolated worktree; `--seed prod` forks prod data with sensitive columns masked. |
| **use** | `capcli env use <name>` | [both] | Sets the sticky environment context for subsequent commands. |
| **list** | `capcli env list` | [both] | Enumerates environments. |
| **inspect** | `capcli env inspect` | [both] | Flags schema drift and data staleness. |
| **doctor** | `capcli env doctor` | [both] | Health check — unmerged prod routines, stale sim seeds. |
| **merge** | `capcli env merge <name> [target=prod] -m "<why>"` | [both] | Promotes a world: git merge → snapshot target → forward DDL. |
| **remove** | `capcli env remove <name>` | [human] | Deprovisions an environment — prod demands dual confirmation. |

## Worlds are worktrees

Each environment is an isolated git worktree under `envs/<name>/` with its own gitignored `workspace.db`. Sim and prod quota accounting is independent — rehearsals never burn prod limits. Capacity is capped at [five concurrent worlds](../limits.md#workspace-storage).

## Seeding & masking

`--seed prod` forks production data into sim with sensitive columns run through [Format-Preserving Anonymization](../../concepts/environments.md#fpa) — typed, valid, fake. A sim fork that grows stale past its [freshness threshold](../limits.md#routine-shape) triggers a re-seed nag from `env doctor`.

## Merging to prod

The merge pipeline snapshots the target database, merges the git branch, and applies the forward DDL diff atomically. Prod merges additionally require a [Tier 1](../../concepts/sandboxing.md#tiers) host and verified remote push credentials (`git push --dry-run` gate). No world exists unbacked — backup push is mandatory on mutation.

## Removing prod

Prod deprovisioning requires **both** `--confirm-backup` and `--confirm-prod` — [two confirm flags](../limits.md#invariants), by design. The full offboarding sequence (survey → preserve → teardown) is choreographed in [recovery.md](../../concepts/recovery.md).

## Invariants

* Draft routines cannot write to prod — the overlay denies them outright ([trust ladder](../../concepts/trust-engine.md)).
* Environment transitions are audit events (`env.*`) on the [spine](../audit.md).
* Backup cadence and drift alarms are [governed](../limits.md#rate-governance).
