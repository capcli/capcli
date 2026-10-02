# Troubleshooting

Every failure in Capcli is a receipt: the rule that fired, the statement that died, `state_modified: false`, and a `remedy:` line. Read those four things and you're most of the way home. Each family below runs **problem → diagnosis → evidence → remediation**.

---

## Triage

| You're seeing | It means | § |
|---|---|---|
| `✗ exit 2` + a `FAIL` rule id | A policy wall said no. Nothing changed. | 1 |
| `✗ exit 3` | Refusal: missing intent, drift, or a lying clock. | 2 |
| `✗ exit 5` | Audit sink unreachable. Loud, rare, deliberate. | 3 |
| `✗ exit 6` | Quota dry. Task parked, not dead. | 4 |
| Boot refuses entirely | Tamper evidence in the audit chain. | 5 |
| `⚠ host.degraded_isolation` | You're on Tier 2. Physics, not a bug. | 6 |

`exit 0` and `exit 4` have their own page: [reference/exit-codes.md](../reference/exit-codes.md).

---

## 1. `✗ exit 2` — the wall said no

**Problem.** The command died with `exit 2` and a `FAIL` line. **Diagnosis.** The rule id and the `remedy:` line *are* the diagnosis:

```bash
$ capcli run experimental_cleanup -p dry=true -m "test cleanup" --env prod
```

```
[prod:tier_1]  ✗  exit 2

  FAIL  policy.trust.draft_writes_denied
        capability: cap://experimental_cleanup@1
        trust: draft
        env: prod

  state_modified: false
  audit: op_71b2
  remedy: promote to reviewed via routine ship, or run in dev/sim
```

**Evidence.** Want the causal story — who asked, and what chain led to the wall? Trace the op id:

```bash
$ capcli sys audit trace op_71b2 --explain
```

```
[prod:tier_1]  audit trace  ✓  op_71b2 (denied leaf)

  ses_c41d  session.start            "test cleanup"
    └── op_71b1  run.experimental_cleanup@1
          └── op_71b2  invoke        ✗  denied pre-execution

  rule:           policy.trust.draft_writes_denied
  state_modified: false
```

**Remediation.** Do what the remedy says — `capcli routine ship experimental_cleanup reviewed --reason "..."`, or drop back to dev/sim. Twenty denials in five minutes and the kernel flags your harness as thrashing: change the approach, don't retry harder.

---

## 2. `✗ exit 3` — the kernel refused

Refusals are compile-time and boot-time problems. Three classics.

### The write with no why

```bash
$ capcli sql "UPDATE orders SET status = 'shipped' WHERE id = 'ORD-8842' LIMIT 1"
```

```
[dev:tier_1]  ✗  exit 3

  FAIL  policy.query.writes_require_intent
        UPDATE orders SET status = 'shipped' WHERE id = 'ORD-8842' LIMIT 1
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        Mutating write without causal intent declaration.

  state_modified: false
  remedy: add -m "why you're doing this"
```

The kernel doesn't care what your intent is. It cares that you have one. Add `-m "why"` and the same write lands with `rows_affected: 1`.

### You edited `routines/` by hand

Someone — probably you, probably at midnight — edited `routines/dispatch_order.ts` without bumping the version. The lockfile noticed:

```bash
$ capcli run dispatch_order -p order_id=ORD-8842 -p carrier=fedex -m "fulfill order"
```

```
[dev:tier_1]  ✗  exit 3

  FATAL  kernel.boot.lockfile_mismatch
         Compiled capcli.lock root hash does not match working tree.
         expected: sha256:88a1f2c9...
         computed: sha256:00b9911e... (tainted: routines/dispatch_order.ts)
  state_modified: false
  remedy: discard uncommitted changes via git checkout, or run 'capcli rule apply'
```

Silent edits are banned. Restore the file, redo the change through the front door.

### Your clock is lying

```bash
$ capcli sys doctor --boot-check
```

```
[dev:tier_1]  ✗  exit 3

  FATAL  kernel.boot.clock_drift_exceeded
         Host clock delta vs NTP is 840ms (maximum allowable: 500ms).
  state_modified: false
  remedy: synchronize host system clock via 'chronyd' or 'ntpdate'
```

Locks, quota windows, and ask deadlines hang off the host clock. Past 500ms of drift, the kernel refuses to boot rather than corrupt them.

---

## 3. `✗ exit 5` — the ledger went dark

**Problem.** Everything fails instantly, including things that worked a minute ago. **Diagnosis.** The audit sink — `_audit` or its JSONL mirror — can't flush (full disk, bad permissions). It gets a short buffer to catch up; past that, Capcli refuses to run anything unaudited, so it runs nothing:

```bash
$ capcli run dispatch_order -p order_id=ORD-8842 -p carrier=fedex \
    -m "fulfill paid order"
```

```
[prod:tier_1]  ✗  exit 5

  FATAL  kernel.panic
         Audit sink unreachable: JSONL mirror failed to flush.
         Unaudited writes are physically impossible. Execution refused.
  state_modified: false
  remedy: free disk space or fix audit mirror permissions, then retry
```

**Remediation.** Fix the host, re-run. Nothing ran half-logged — `state_modified: false` is a guarantee, not a hope.

---

## 4. `✗ exit 6` — parked, not dead

**Problem.** A background task exited with `exit 6` and nothing looks broken. **Diagnosis.** Nothing *is* broken. The provider's token bucket ran dry, so the task parked itself in `_suspended_tasks` until the refill epoch — the daemon watches `resume_at` and re-queues it when tokens return:

```bash
$ capcli run nightly_backfill -m "top up search index"
```

```
[dev:tier_1]  ✗  exit 6

  YIELD  api.quota
  frame:               frame_021 (nightly_backfill@2)
  priority:            background
  unreserved_headroom: 9 tokens (yield threshold: 15)
  parked_in:           _suspended_tasks
  resume:              automatic on token refill
  state_modified:      false
  remedy:              wait for refill; do not retry in a loop
```

**Remediation.** Wait. Retrying burns the last tokens and buys nothing. Critical-priority tasks never yield — they deny hard (`exit 2`) so a human sees them immediately.

---

## 5. Boot refuses — tamper evidence

**Problem.** Nothing runs. Every command dies at startup. **Diagnosis.** At boot the kernel walks the audit hash chain from genesis to head. Somewhere a row's recomputed hash doesn't match its stored `prev_hash` — the ledger was edited. The kernel halts rather than execute on top of a lie:

```bash
$ capcli sys doctor --boot-check
```

```
[prod:tier_1]  ✗  exit 3

  FATAL  kernel.boot.audit_chain_divergence
         Hash chain walk failed at row #102: recomputed hash does not
         match stored prev_hash. All later hashes are invalid.
  state_modified: false
  remedy: restore from a verified recovery point (capcli sys recover), then investigate
```

**Remediation.** Restore from a recovery point — [recovery.md](recovery.md) has the commands — then find out who touched the ledger. Rebooting on a loop won't help; the math doesn't forgive. The offsite WORM checkpoint still holds the true root hash, which is how you prove what changed.

---

## 6. `⚠ host.degraded_isolation` — you're on Tier 2

**Problem.** Every command prints `[dev:tier_2]  ⚠ host.degraded_isolation`, and pinned routines refuse to run. **Diagnosis.** You're on macOS or Windows. Those kernels have no unprivileged namespaces — no `bwrap`, no `seccomp-bpf` — so the kernel degrades to broker mediation and tells you at boot (`sys doctor` reports `tier: 2 (degraded)`, `sandbox: broker`). Draft and reviewed work in dev and sim runs fine. Pinned production execution does not:

```bash
$ capcli run dispatch_order -p order_id=ORD-8842 -p carrier=fedex \
    -m "fulfill paid order"
```

```
[dev:tier_2]  ✗  exit 2

  FAIL  E045_TIER2_PINNED_DENIED
        capability: cap://dispatch_order@4
        trust: pinned
        host_tier: 2
  state_modified: false
  remedy: pinned execution requires a Tier 1 Linux host (bwrap + seccomp-bpf)
```

**Remediation.** None in the sense you're hoping for. Put the kernel on Linux — bare metal, a VPS, Docker with userns, or WSL2 — for pinned prod execution. Physics wins every time.

---

## The pattern

Read the `FAIL` id. Trust `state_modified: false` — nothing happened. Do the `remedy`. Still confused? `capcli sys audit trace <op-id> --explain` walks the family tree. The wall talks; this page is just the translation.

---

**State wrong and you need it back?** → [recovery.md](recovery.md)

**The full exit-code contract?** → [reference/exit-codes.md](../reference/exit-codes.md)

**More denials, decoded?** → [boundaries.md](../use/boundaries.md)
