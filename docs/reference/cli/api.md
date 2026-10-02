# Command: capcli api

Manages external provider catalogs — OpenAPI synchronization, verb lifecycles, and quota telemetry. Egress itself never happens here: calls run through [`capcli run`](run.md) or `ctx.api.call` inside routines.

```bash
capcli api <verb> [args] [--flags]
```

## Subcommands

| Verb | Syntax | Caller | Description |
|---|---|---|---|
| **sync** | `capcli api sync <provider> <url> [--interval 7d] [--dry-run]` | [both] | Imports and compiles the OpenAPI spec into `apis/<provider>.yaml`. |
| **diff** | `capcli api diff <provider>` | [both] | Compares the compiled spec against the upstream `spec_hash`. |
| **catalog** | `capcli api catalog <provider> [--state <state>]` | [both] | Lists verbs filtered by state (`dormant`, `active`, `deprecated`, `retired`). |
| **activate** | `capcli api activate <provider.verb> -m "<why>"` | [both] | Moves a verb from dormant to active at draft trust. |
| **prove** | `capcli api prove <provider.verb> [-p k=v] [--env sim]` | [both] | Dry-runs against simulated mocks or schema fixtures. |
| **ship** | `capcli api ship <provider.verb> <reviewed\|pinned> [--reason "<why>"]` | [human] | Promotes an API verb up the trust ladder. |
| **stats** | `capcli api stats <provider> [--deep] [--summary]` | [both] | Token-bucket quotas and latency metrics. |
| **deactivate** | `capcli api deactivate <provider.verb> [--reason "<why>"]` | [both] | Reverts an active verb back to dormant. |
| **retire** | `capcli api retire <provider.verb> [--reason "<why>"]` | [both] | Permanently disables the verb while preserving provenance. |
| **rollback** | `capcli api rollback <provider.verb> [version]` | [both] | Restores a prior verb configuration. |

## Catalog law

* **Spec quarantine:** the harness is banned from reading raw OpenAPI files — the kernel alone parses, compiles, and prunes them ([spec ceilings](../limits.md#api-wire)).
* **Verb lifecycle:** `dormant` → `active` → `deprecated` → `retired`. Dormant verbs never expire — the unactivated surface stays discoverable forever.
* **Activation** requires intent and lands at draft trust; activation velocity is [capped](../limits.md#rate-governance).
* **Training wheels:** un-simulated verbs carry a first-prod-call counter with a [24-hour window](../limits.md#api-wire) per unapproved call; graduation to normal governance is automatic on call 4 ([training wheels](../../concepts/trust-engine.md#training-wheels)).

## Simulation modes

| Mode | Behavior |
|---|---|
| `sandbox` | Routes to the provider sandbox URL via `apis/<provider>.sim.yaml`. |
| `mock` | Returns the canned fixture from `apis/<provider>.mock.yaml`. |
| `dry-run` | Validates the payload schema and returns `{ "simulated": true }`. |
| `skip` | Excluded from execution; omitted from the fingerprint. |
| `prod-only` | Real egress, prod only — calling it in dev or sim is an [exit 2](../exit-codes.md#exit-2). |

Default resolution: `sandbox` when a sim overlay exists, `dry-run` otherwise; `prod-only` must always be declared explicitly.

## Invariants

* Provider, catalog, and active-verb ceilings → [limits](../limits.md#api-wire).
* Sync cadence has a [minimum interval](../limits.md#api-wire) — no hourly hammering of provider URLs.
* Dormant verbs are not callable, period. Egress runs exclusively through the kernel proxy; raw sockets die in the [network jail](../../concepts/sandboxing.md).
* Secrets are injected at the egress boundary and never appear in env, context, or audit — the vault workflow lives in [apis.md](../../workflows/apis.md#vault).

## Banned verbs

* `capcli api call` → **banned.** Use `capcli run` or `ctx.api.call` inside guest code.
* `capcli api import --pick` → **banned.** Verbs are synced in full to preserve schema integrity.
