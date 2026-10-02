# Audit Reference

The `_audit` spine: exact structure, exact query surfaces. The short version lives in [../understand/audit.md](../understand/audit.md) — this is the contract.

---

## Storage hierarchy

| Surface | Role | Access |
|---|---|---|
| `_audit` (in `workspace.db`) | SSOT for all events — live system table | Read via `sys audit query`; writes are kernel-only |
| `audit/*.jsonl` (mirror) | Read-only export, flushed to disk + git | Diffable, cold-recovery source; mirror lag SLA: 5 minutes |

Genesis sequence, on every fresh world: `rule.apply → sql.query (read) → sql.query (write denied) → sql.query (write ok)`. A world's first event is a denial. The universe has a sense of humor, and it's a strict one.

## Event anatomy

```yaml
# canonical fields on every event
identity:      event, ts, env, stage, channel, trace_id
actor:         agent, session, principal
causality:     caused_by, intent, intent_chain
payload:       capability, sql, params        # recorded verbatim for replay
policy:        decision (allow|denied), rules_matched
outcome:       rows_affected, result_hash, duration_ms, exit_code
```

Raw stdout/stderr is **discarded** — the kernel hashes a canonical JSON outcome exclusively. No prompt leakage, no log noise, just receipts.

## Kernel event types

`bind.create` / `bind.delete` · `vault.set` · `env.switch` / `env.merge` · `sys.agent.register` / `sys.agent.revoke` · `capability.search` · `db.exec` · `routine.run` · `api.sync` · `api.activate` · `api.token_refresh` · `api.call` (sim) · `api.first_prod_call` · `budget.frame_push` / `budget.frame_pop` · `serve.request`

Synthetic onboarding/lifecycle event types are denied at the write. If it didn't happen, it can't be logged; that's the entire point of a spine.

## Integrity laws

1. **100% of verbs advance the chain.** Every CLI verb, binding transition, env transition — all of it hashes in. Zero ghost actions.
2. **Denials are events too**, stamped `effect: none`. Blocked attempts are history.
3. **Per-row SHA-256 chain**, verified against the root ledger hash; external checkpoints go to S3 Object Lock (WORM) with KMS signatures.
4. **Tamper blast radius:** one broken link invalidates every subsequent event. Integrity walk runs on boot; tamper = kernel refuses to boot (`exit 3`).
5. **Sink failure = panic.** The audit queue buffers 5 minutes in memory, then the kernel halts with `exit 5`. Nothing runs unaudited. Nothing.
6. **`_audit` is physically append-only** — mutations die at the C authorizer:

```text
[dev:tier_1]  ✗  exit 2

  FAIL  policy.authorizer.immutable_system_table
        DELETE FROM _audit WHERE decision = 'denied'
        ^^^^^^^^^^^^^^^^^^
        System table '_audit' is strictly append-only.

  state_modified: false
  layer: authorizer
```

Deleting history is a query that can't run. Writing history is the only option, and the kernel does that automatically.

## Query surfaces

```bash
capcli sys audit tail [--follow] [--capability <urp>] [--since 1h]
capcli sys audit trace <op-id> [--explain]
capcli sys audit query "<sql>" [-p k=v]        # bounded, read-only, against _audit
capcli sys audit replay --from <point> [--dry-run]   # isolated forked state
```

`trace --explain` walks the causal DAG (op → routine → session goal) back to the root intent, and *explains denials along the way* — it's the replacement for the retired `policy explain`, and it's better: it cites rows instead of opinions.

---

**The integer verdicts** → [exit-codes.md](exit-codes.md) · **The failures catalog** → [errors.md](errors.md)
