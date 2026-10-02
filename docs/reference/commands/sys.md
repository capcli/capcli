# Command: `capcli sys`

Kernel diagnostics, cryptographic audit inspection, identity registries, encrypted vault, and disaster recovery.

```bash
capcli sys <verb> [args] [--flags]
```

---

## Subcommands

| Verb | Syntax | Description |
|---|---|---|
| **`doctor`** | `capcli sys doctor [--boot-check] [--report] [--json]` | Probes host OS, sandbox tier (Tier 1 vs 2), runtime engines, and emits trust receipts. |
| **`inbox`** | `capcli sys inbox pop [--channel <name>]` | Consumes sensory queued events from webhooks, crons, or partners. |
| **`audit tail`**| `capcli sys audit tail [--follow] [--capability <urp>] [--since 1h]` | Streams immutable event log with causal hashes. |
| **`audit trace`**| `capcli sys audit trace <op-id> [--explain]` | Walks causal DAG upstream to root intent; explains denials. |
| **`audit query`**| `capcli sys audit query "<sql>" [-p k=v]` | Runs bounded read-only queries against `_audit` table. |
| **`audit replay`**| `capcli sys audit replay --from <point> [--dry-run]` | Replays historical events against isolated forked state. |
| **`agent`** | `capcli sys agent <register\|list\|revoke> [args]` | Manages OS-bound agent identities and capability tokens. |
| **`vault`** | `capcli sys vault <set\|import-env> [args]` | Encrypts root credentials into AES-256-GCM storage. |
| **`backup`** | `capcli sys backup [--push]` | Creates VACUUM snapshots and syncs Git + WORM storage. |
| **`recover`** | `capcli sys recover <commit\|snap_id>` | Restores database and workspace state from a recovery point. |
| **`exec`** | `capcli sys exec "<cmd>" --sandbox` | Executes a one-shot command inside the `bwrap` network jail. |
| **`serve`** | `capcli sys serve <--start\|--stop\|--restart\|--status>` | Controls the persistent axum daemon on `127.0.0.1:4040`. |

---

## Invariants & Break-Glass Flags

* **The NTP Boot Gate:** Host clock delta > 500ms vs NTP aborts kernel boot (`exit 3`).
* **Audit Write Priority:** If the audit sink (`_audit` or JSONL mirror) fails to flush, execution halts immediately with **`exit 5` (Kernel Panic)**. Nothing runs unaudited.
* **Emergency Recovery Mode (`CAPCLI_RECOVERY=1`):**
  * Disables behavioral policy enforcement (`policy.yaml`).
  * Loads *only* `schema.yaml` and the audit sink.
  * Verbs restricted to: `sql` (read-only), `db dump`, `sys audit tail`, and `sys backup`.
* **Zeroize Memory Sanitation:** Plaintext secrets decrypted from vault are scrubbed from RAM with zeros immediately post-egress.

---

## Live example: the doctor

```bash
$ capcli sys doctor
```

```text
[dev:tier_1]  capcli 0.4.2

  host:       linux x86_64
  tier:       1 (hardened)
  sandbox:    bwrap 0.8.1
  engine:     bun 1.2.4
  python:     3.12.1
  git:        2.44.0
  lockfile:   capcli.lock ✓
  schema:     schema.yaml ✓
  policy:     policy.yaml ✓
  governance: governance.yaml ✓

  status:     ready
```

## Live example: the trust receipt

```bash
$ capcli sys doctor --report
```

```yaml
trust_receipt:
  status:            nominal
  workspace:         envs/dev/workspace.db
  ledger_root_hash:  sha256:7f9a1b...
  audited_events:    847
  policy_denials:    2 (pre-execution; state untouched)
  unaudited_writes:  0
  secret_leaks:      0
  pinned_routines:   3
  sleep_score:       100%
```

## Live example: causal trace

```bash
$ capcli sys audit trace op_9f2e --explain
```

```text
[dev:tier_1]  op_9f2e → op_9f2d → op_9f2c → root

  root intent:    "fulfill paid order for customer checkout"
  session:        goal: dispatch ORD-8842
  routine:        dispatch_order@4 (pinned)
  ops:            db.query → api.call(logistics.shipments.create) → db.execute
```

---

**Narrative** → [../../use/boundaries.md](../../use/boundaries.md) · **Audit contract** → [../audit.md](../audit.md)
