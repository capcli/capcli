# Command: capcli sys

Kernel diagnostics, audit inspection, identity registries, the encrypted vault, and disaster recovery. The deepest noun — and the only one that cannot be aliased by cockpit clients.

```bash
capcli sys <verb> [args] [--flags]
```

## Subcommands

| Verb | Syntax | Caller | Description |
|---|---|---|---|
| **doctor** | `capcli sys doctor [--boot-check] [--report] [--json]` | [both] | Probes host OS, platform tier, runtime engines; `--report` emits a trust receipt. |
| **inbox** | `capcli sys inbox pop [--channel <name>]` | [both] | Consumes sensory events queued by webhooks, crons, or partners. |
| **audit tail** | `capcli sys audit tail [--follow] [--capability <urp>] [--since 1h]` | [both] | Streams the immutable event log. |
| **audit trace** | `capcli sys audit trace <op-id> [--explain]` | [both] | Walks the causal DAG upstream to the root intent; explains denials. |
| **audit query** | `capcli sys audit query "<sql>" [-p k=v]` | [both] | Bounded read-only queries over `_audit` ([audit.md](../audit.md)). |
| **audit replay** | `capcli sys audit replay --from <point> [--dry-run]` | [both] | Re-executes history against isolated forked state. |
| **agent** | `capcli sys agent <register\|list\|revoke> [args]` | [human] | Manages OS-bound agent identities and capability tokens. |
| **vault** | `capcli sys vault set <key> <val>` / `capcli sys vault import-env` | [human] | Encrypts root credentials into AES-256-GCM storage. |
| **backup** | `capcli sys backup [--push]` | [both] | Creates VACUUM snapshots and syncs Git + WORM object storage. |
| **recover** | `capcli sys recover <commit\|snap_id>` | [human] | Restores database and workspace state from a recovery point. |
| **exec** | `capcli sys exec "<cmd>" --sandbox` | [both] | Runs a one-shot command inside the network jail. |
| **serve** | `capcli sys serve --start\|--stop\|--restart\|--status` | [both] | Controls the persistent axum daemon on `127.0.0.1:4040`. |

## Boot gates

* **NTP gate:** host clock drift beyond the [boot threshold](../limits.md#invariants) aborts the kernel — leases, quota windows, and ask deadlines all depend on monotonic time.
* **Lockfile gate:** a `capcli.lock` hash mismatch refuses boot ([invariants](../limits.md#invariants)).
* **Audit write priority:** if the audit sink fails, execution halts with [exit 5](../exit-codes.md#exit-5) after a short in-memory buffer — nothing runs unaudited.
* `--boot-check` verifies all of the above without the daemon; `--json` is the machine contract a harness parses at session start (stage H0).

## Trust receipts

`sys doctor --report` computes a receipt directly from the audit mirror: execution tier, sandbox provider, audited operation count, policy denials, unaudited writes (verified zero), secret exposure (verified zero), backup age, and recovery drill status. The receipt lines are enumerated in [cans/trust.md](../../../cans/trust.md) — Trust receipts.

## Emergency recovery mode

`CAPCLI_RECOVERY=1` is the break-glass path: behavioral policy is disabled, only `schema.yaml` and the audit sink load, and the verb surface shrinks to read-only `sql`, `db dump`, `sys audit tail`, and `sys backup`. Entry is itself an audit event. The recovery ladder and re-entry context live in [recovery.md](../../concepts/recovery.md).

## Daemon & cockpit

`sys serve` runs the persistent axum daemon on `127.0.0.1:4040` — HTTP POST `/rpc` for JSON-RPC, `WS /ws/audit` for live event tailing. The daemon serves the administrative cockpit PWA at the same address; the cockpit holds zero authority of its own (see [cans/interface.md](../../../cans/interface.md) — Administrative cockpit PWA, or open http://127.0.0.1:4040).

## Vault law

Secrets live in the `secrets` system table, AES-256-GCM at rest, memory-decrypted only at boot, and never visible to agents — `value` is masked in every query result, trace, and audit mirror. Plaintext buffers are zeroized from RAM immediately post-egress. Draft trust cannot read secrets at all ([trust ladder](../../concepts/trust-engine.md)).

## Identity law

Agent ids are kernel-minted — self-declaration is denied, and `--by` is validated against OS process credentials. Three kernel principals run unattended: `capcli-cron`, `capcli-watch`, `capcli-serve`. Revocation is instant with no grace period. The identity model is covered in [identity.md](../../concepts/identity.md).
