# Proving

Trust is earned with receipts, not vibes.

The ladder has three rungs — draft, reviewed, pinned — and one direction of travel. You climb by accumulating evidence the kernel verifies itself: prove passes, telemetry, invariant suites. No self-promotion: a running routine cannot ship itself, and elevation skips are denied.

---

## The evidence pipeline

```
prove passes  →  telemetry accumulates in routine_stats  →  ship gate checks the math  →  parole window watches
```

Each stage produces a receipt. The receipts are the rung.

---

## Stage 1: prove passes

Every `capcli routine prove <name> --env sim` pass is recorded: manifest match, policy denials, drift events, duration. Prove samples real historical parameter values from the audit mirror — synthetic fixtures are banned as ship evidence. The mechanics live in [rehearsal.md](rehearsal.md). This is H7: the last step of your onboarding journey, and the first step of every promotion.

---

## Stage 2: telemetry in routine_stats

```bash
$ capcli routine stats order_refund --deep
```

```
[dev:tier_1]  order_refund@7  ✓  stats

  total_runs:     89
  success_rate:   97.8%
  p50_duration:   410ms
  p95_duration:   1100ms
```

At ship time the kernel checks `routine_stats` and the audit mirror directly. You can't argue with a table you can't edit.

---

## Stage 3: the promotion math

`capcli routine ship <name> reviewed|pinned` runs a conjunction — every metric must pass:

| Metric | Gate |
|---|---|
| Invariant suite | 100% pass |
| Success rate | ≥ 0.95 |
| Manifest match | executed ⊆ declared, zero undeclared leaves |
| Policy denials | exactly 0 |
| Fingerprint drift | exactly 0 |
| Latency | p95 ≤ 70% of declared timeout |

```bash
$ capcli routine ship order_refund reviewed \
    --reason "conjunction passed across rehearsal window"
```

```
[dev:tier_1]  order_refund@7  ✓  promoted to reviewed

  invariant_suite_passed:  true
  success_rate:            0.978 (>= 0.95)
  manifest_subset_match:   true
  policy_denials:          0
  fingerprint_drift:       0
  p95_duration:            1100ms (ceiling: 70% of 20s)
  audit:                   routine.auto_promoted (5-point record)
```

Fail one metric — any single one — and the case routes to the human queue (`routine ship <name> reviewed --queue`, then `capcli routine pending`). 94.9% is not 95%. The audit event records the 5-point metric record; the gate checks six. The ledger is exact even when the nickname isn't.

---

## Stage 4: the parole window

Promotion isn't the finish line — it's the start of a 1-hour canary telemetry window. Error spikes, policy denials, or runtime crashes inside that hour fire an autonomous circuit breaker: the promotion is revoked and the routine drops straight back to draft. Humans keep retroactive veto too (`rollback --to-trust draft`).

You fix the bug. You re-prove. Reality remains intact.

---

## API verbs prove too

`capcli api prove <provider.verb> --env sim` rehearses remote calls against mocks or sandbox endpoints. Newly activated un-simulated verbs run with training wheels: each first prod call carries a 24-hour approval window, and the fourth call graduates into normal governance. Unapproved ≠ unrecorded — every call lands in the ledger either way.

---

## Trust decays

Rungs are earned, then defended. Success below 0.70 over 20 runs auto-demotes a routine to draft. Trust that isn't maintained is trust that gets subtracted.

---

## The receipt

```bash
$ capcli sys doctor --report
```

```
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

Computed directly from the audit mirror. Zero unaudited writes. Zero leaks. Two denials that *protected* you. That's the receipt you operate on — and the one you hand to the human who asks why an agent is allowed near prod.

---

**Ready to codify more?** → [codification.md](codification.md)

**The human view of the ladder** → [../understand/trust.md](../understand/trust.md) · [../automate/promotion.md](../automate/promotion.md)
