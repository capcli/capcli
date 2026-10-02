# Promotion

A draft routine is a hypothesis with a hash. Nice. Nobody lets hypotheses touch production.

Capcli's trust ladder has three rungs — **draft → reviewed → pinned** — and every ascent is a gate crossing with a receipt. The ladder is monotonic: one rung at a time, and skipping is denied. Nobody, including you, gets to fast-forward trust.

---

## The move: ship

```bash
$ capcli routine ship refund_order reviewed \
    --reason "passed quarterly compliance rehearsal"
```

```
[dev:tier_1]  refund_order@1  ✓  promoted

  rung:       draft → reviewed
  evidence:   invariants 100% · success 97.8% · manifest 100% subset
  denials:    0 · drift 0 · p95 within 70% ceiling
  parole:     60-minute canary window armed
  audit:      op_9c31
```

The kernel checks `routine_stats` and the audit mirror directly. If the 5-point math passed, the rung is granted — and one `routine.auto_promoted` event lands in the trail carrying the full metric record.

`--reason` isn't demanded by the gate; it's for the humans reading the trail later. Write it anyway.

---

## When the math says no

Get a 94.9% success rate and the conjunction fails:

```bash
$ capcli routine ship churn_alert reviewed --reason "want it live this week"
```

```
[dev:tier_1]  churn_alert@2  ✗  exit 2

  metric:    success_rate 94.9% (threshold: >= 95.0%)
  verdict:   auto-promotion denied — single-metric failure
  queue:     capcli routine pending
  state:     draft (unchanged)
```

State untouched. Trust untouched. The path to promotion is now human, and humans review in batches:

```bash
$ capcli routine ship churn_alert reviewed --queue
```

```
[dev:tier_1]  ✓  queued for human approval

  candidate:  churn_alert@2
  batch:      1 awaiting review
```

```bash
$ capcli routine pending
```

```
[dev:tier_1]  1 candidate waiting

  churn_alert@2    reviewed    waiting 4h    success 94.9% · denials 0 · drift 0
```

A human approves the batch with a single audit event. If the queue sits longer than 48 hours, `sys doctor` raises `promotion.sla_breached` — stale approvals are their own kind of failure.

---

## The 60-minute parole window

You passed the math. You got the rung. **Now you're on probation.**

For the first hour of live traffic, the kernel watches the newly promoted routine like a hawk watches a rodent: error rates, latency, policy denials. One anomaly spike, one runtime crash, one denial — and the circuit breaker fires:

- The promotion is revoked, instantly and autonomously.
- The routine drops straight back to `draft`.
- The audit trail records why.

You fix the bug. You rehearse again. You prove again. Reality remains intact. That's the whole point of parole — trust is revocable at exactly the speed it was granted.

Humans can veto retroactively too: `capcli routine rollback <name> --to-trust draft` unwinds a rung without gate resistance. Demotion never has to argue with anyone. Earning it back does.

---

## Changing your mind about a version

A subtle edge-case bug ships in v4? Don't push a frantic midnight hotfix. Rewind the pointer:

```bash
$ capcli routine rollback dispatch_order --to-version 3 \
    -m "v4 fails on international postal codes"
```

```
[prod:tier_1]  ✓  rolled back

  pointer:     cap://dispatch_order
  active:      version 3 (hash: sha256:88a1b...)
  superseded:  version 4 (deactivated)
  audit:       op_77c2
```

One command. The old verified hash is active again; the buggy version is deactivated, not deleted.

The memory has edges: **rollback depth caps at 5 versions**, and the registry keeps **25 historical versions** per routine — older ones prune from disk while their audit hashes stay pinned forever.

---

## What you can never do

- **Skip rungs.** draft → pinned in one hop is denied.
- **Ship from inside.** A running routine cannot `ship` itself — trust escalation requires a human or CI principal.
- **Force it.** `--force` is banned at the syntax level. There is no "please."

Pinned is the top rung: hardened production baseline, headless schedules allowed, strictly Tier 1 hardware — a Tier 2 host invoking a pinned routine gets `exit 2` (`E045_TIER2_PINNED_DENIED`) before anything evaluates. Shipping toward prod also demands the branch be merged into the prod worktree and a full replay invariant pass in sim.

---

## The One Rule

**Trust is climbed one rung at a time and revoked in one heartbeat.**

Slow to earn. Instant to lose. Always recorded.

---

**It's promoted. Now you operate it — monitor, change, and eventually subtract:** → [operation.md](operation.md)

**The ladder underneath the ladder — rungs, bounds, laws:** → [understand/trust.md](../understand/trust.md)

**What every exit code means:** → [reference/exit-codes.md](../reference/exit-codes.md)
