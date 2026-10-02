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

## In Practice

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

Zero unaudited writes. Zero leaks. Two denials that *protected* you. `unaudited_writes: 0` is the entire product in one field — the receipt you read before closing the laptop.

---

## Invariants & Break-Glass Flags

* **The NTP Boot Gate:** Host clock delta > 500ms vs NTP aborts kernel boot (`exit 3`).
* **Audit Write Priority:** If the audit sink (`_audit` or JSONL mirror) fails to flush, execution halts immediately with **`exit 5` (Kernel Panic)**. Nothing runs unaudited.
* **Emergency Recovery Mode (`CAPCLI_RECOVERY=1`):**
  * Disables behavioral policy enforcement (`policy.yaml`).
  * Loads *only* `schema.yaml` and the audit sink.
  * Verbs restricted to: `sql` (read-only), `db dump`, `sys audit tail`, and `sys backup`.
* **Zeroize Memory Sanitation:** Plane-text secrets decrypted from vault are scrubbed from RAM with zeros immediately post-egress.
