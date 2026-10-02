# Recovery Guide

Something mutated state that shouldn't have. Breathe. Recovery here is a Tuesday, not a war story.

You will need: one snapshot ID, one honest `-m`. Total time: under a minute. Dramatic sighing: optional.

---

## Step 0 — Check whether you actually need this

Non-zero exits guarantee `state_modified: false`. The failed `UPDATE` that exited 2? It *never happened* — the denial is the proof. Before restoring anything, read the receipt:

```bash
$ capcli sys audit tail --since 15m
```

```text
[dev:tier_1]  4 events

  ts          event                    decision   agent      capability
  ──────────  ───────────────────────  ─────────  ─────────  ──────────────────
  ...         sql.query                denied     agt_7f3k   orders (update)
  ...         run.archive_old_orders   allow      agt_7f3k   cap://archive_old_orders@3
  ...
```

Denied rows changed nothing. The rows you're restoring from may only be the *allowed* ones.

## Step 1 — Find your snapshot

If you followed the religion, there's a pre-mutation snapshot on file (snap before risky work — it's one cheap command):

```bash
$ capcli db snapshot -m "before harness touches inventory pricing"
```

```text
[dev:tier_1]  ✓  snap_8f2a9c

  created:  2026-10-02T03:10:00Z
  size:     1.9 MB
  note:     before harness touches inventory pricing
```

No snapshot? `sys recover <commit>` works from Git history and WORM-object checkpoints. The ledger root hash is checkpointed to Object Lock storage with KMS signatures — the recovery points exist even when discipline didn't.

## Step 2 — Restore

```bash
$ capcli db restore snap_8f2a9c -m "reverting botched pricing update"
```

```text
[dev:tier_1]  ✓  restored

  snapshot:  snap_8f2a9c
  restored:  envs/dev/workspace.db
  note:      reverting botched pricing update
  audit:     op_8c11 (restore is an event; the ledger keeps score)
```

The restore itself lands in the spine. You cannot restore your way out of history — the reversion is *part of* the history now. Tamper-evidence survives restoration; that's the point of tamper-evidence.

## Step 3 — Explain what happened

```bash
$ capcli sys audit trace <op-id> --explain
```

Root intent, session, routine, ops — the causal chain from the damage back to the sentence that caused it. Post-mortems here write themselves, which is the entire design goal.

## If the kernel won't boot (tamper / sink failure)

- Tamper in the hash chain → boot refuses (`exit 3`) rather than run on fiction. Evacuate: `CAPCLI_RECOVERY=1` → read-only `sql`, `db dump`, `sys audit tail`, `sys backup`.
- Audit sink down → kernel panics (`exit 5`) instead of running unaudited. Fix the disk/permissions, restart. The 5-minute in-memory buffer bought you most of your events back.

## The habits that make this boring

1. **Snapshot before risky writes.** One command, no drama.
2. **`-m` like you mean it.** Recovery traces are only as good as the intent at the root.
3. **Rehearse in sim.** Most "recovery" is just "the rehearsal caught it first."
4. **Keep the DLQ tidy** — failed webhooks purge FIFO after 30 days / 1000 items. Loudly.

---

**The machinery behind this** → [../understand/recovery.md](../understand/recovery.md) · **Routine versions went bad?** → `capcli routine rollback <name>` in [../reference/commands/routine.md](../reference/commands/routine.md)
