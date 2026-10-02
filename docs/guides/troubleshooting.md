# Troubleshooting

Symptom → diagnosis → evidence → remediation. No guessing, no vibes — the ledger saw everything, which means the answer already exists and you just have to ask it.

---

## "It exited 2"

`exit 2` is a *denial*, and denials come with receipts. Read the failure block — the `remedy:` line is the fix, stated plainly:

| Symptom in the denial | Diagnosis | Remediation |
|---|---|---|
| `policy.query.update_delete.require_where` / `require_limit` | Unbounded mutation | Add `WHERE` + `LIMIT` |
| `policy.query.update_delete.deny_patterns` | `WHERE 1=1` bypass attempt | Bounded predicate |
| `policy.authorizer.trust_gate` | Rung too low for that column/table | Promote the routine, or stay in your lane |
| `policy.budget.ops_exhausted` | Frame or session ceiling | Split the work or raise declared limits |
| `E045_TIER2_PINNED_DENIED` | Pinned routine on a Tier 2 host | Run on a Tier 1 host. macOS doesn't get prod keys. |

Retrying the identical command will earn the identical denial, forever, with the patience of a mountain. Change the input, not your attitude.

## "It exited 3"

Refusal — the invocation itself is malformed. Ranked by frequency (the ledger sees your shame):

1. **Missing `-m`** on a write → add intent. Always. Every write, every time.
2. **Missing `-p` param** → the inspect envelope listed `params`; bind them all.
3. **Lockfile mismatch** → someone hand-edited YAML → `git checkout` the file, recompile.
4. **Clock drift > 500ms** → sync NTP. Claims need causality; causality needs a clock.
5. **Boot abort** (missing python/git/bwrap) → `capcli sys doctor` names the exact dependency.

## "My harness is stuck / looping"

```bash
$ capcli ping list --pending
```

A suspended routine means there's an `ask://` waiting on a human. Also check yields:

```text
[dev:tier_1]  ✗  exit 6

  FAIL  api.quota
        provider: threads
        remaining: 0 (window: 50/50 calls in 24h)
        yield_until: 2026-10-03T09:12:00Z
        task: parked → _suspended_tasks (task_a41f)

  state_modified: false
  remedy: no action required; task resumes at refill
```

`exit 6` is not an error — the task is parked, not lost. Polling the API to "check if quota recovered" burns the very quota you're waiting for. Walk away; it wakes itself.

## "Something weird happened at 03:00"

The event exists. Trace it:

```bash
$ capcli sys audit trace <op-id> --explain
```

```text
[dev:tier_1]  op_9f2e → op_9f2d → op_9f2c → root

  root intent:    "fulfill paid order for customer checkout"
  session:        goal: dispatch ORD-8842
  routine:        dispatch_order@4 (pinned)
  ops:            db.query → api.call(logistics.shipments.create) → db.execute
```

Walk from any leaf to the root intent. Every 03:00 mystery ends in a human sentence, because mandatory `-m` made sure of that before anything ran.

## "The kernel refuses to boot"

```bash
$ capcli sys doctor --boot-check
```

Boot refusals, in order of likelihood: lockfile hash mismatch (hand-edited YAML), clock drift, missing host dependency (python ≥ 3.11, git ≥ 2.30, bwrap ≥ 0.8 on Linux), tamper detected in the audit chain. The last one means the kernel *chose* not to run rather than run on a lie — that's the feature working, not the system failing.

True emergency (disk full, sink down): `CAPCLI_RECOVERY=1` boots a stripped kernel — read-only `sql`, `db dump`, `sys audit tail`, `sys backup` only. Enough to evacuate evidence, not enough to make things worse.

## "The daemon / cockpit won't start"

```bash
$ capcli sys serve --status
```

Then `--restart`. The daemon owns `127.0.0.1:4040` and the IPC surface your `sql` calls ride on. If the audit sink is the problem, expect `exit 5` and the five-minute in-memory buffer conversation — see [../reference/errors.md](../reference/errors.md).

---

**Data actually damaged?** → [recovery.md](recovery.md) — that's a five-minute procedure, not a weekend.
