# Operation

A promoted routine is an employee now. It has a desk (the registry), a performance file (`routine_stats`), and a permanent record (the audit DAG).

Employees need management: reviews, transfers, discipline, and — eventually, inevitably — retirement. Skipping the management is how companies end up with forty thousand lines of dead cron nobody dares delete.

---

## Watching it work

The health check takes one command:

```bash
$ capcli routine stats order_refund --deep
```

```
[prod:tier_1]  order_refund@7

  runs:      89
  success:   97.8%
  p50:       410ms
  p95:       1100ms
  versions:  7 kept (25 max)
```

89 runs, 97.8% success, latency flat. That's an employee earning its keep. `--deep` adds the per-leaf breakdown — which primitive burns the fuel, which step owns the p95.

For the live view, watch the spine itself:

```bash
$ capcli sys audit tail --follow --capability cap://order_refund@7
```

```
[prod:tier_1]  streaming _audit (ctrl-c to stop)

  op_b1e2  routine.order_refund@7    ✓  410ms
  op_b1e3  db.query (orders)         ✓  12ms
  op_b1e4  api.call (stripe.refund)  ✓  340ms
  op_b1e5  db.execute (orders)       ✓  18ms
```

Every leaf, every duration, every hash link — streaming as it happens. Boring is the goal. Interesting is a diagnosis waiting to be run.

---

## Changing it

Routine needs a fix? Edit the file. The version bumps. New `code_hash`, new `manifest_hash`, same provenance chain — created by which agent, promoted by which human, through which environments, all carried forward.

What you cannot do is edit quietly. Direct tampering with a versioned file trips the lockfile instantly — `exit 3` — and concurrent edits to the same routine lock each other out with `exit 2`. Silent edits are how traditional scripts rot. Versioned edits are how routines age in place.

When a version misbehaves, rewind instead of patching in panic: `capcli routine rollback <name> --to-version N`. Depth caps at 5. The registry keeps 25 versions. The hashes outlive them all.

---

## When it misbehaves

The kernel watches performance so you don't have to:

- **Success below 0.70 over 20 runs** — the routine is auto-demoted back to `draft`. No committee. No appeal. Straight down.
- **Structural rot** — a table it reads gets dropped, an API verb it calls gets deprecated — the routine is quarantined.
- **Quota runs dry** — `exit 6`. The task yields and parks itself until refill. Not a failure. A nap.

Demotion is deliberately frictionless — dropping trust never argues with a gate. Earning it back does. That asymmetry is the product.

---

## Subtraction: the sweep

Routines decay. They go unused, start failing, or multiply into near-duplicates of each other. The kernel tracks all three:

```bash
$ capcli routine sweep --since 30d
```

```
[prod:tier_1]  3 candidates flagged

  legacy_billing@8    dead:      unused 44 days
  churn_alert@2       failing:   success 61% over 28 runs
  sync_inv_a@3        duplicate: 0.91 fingerprint match with sync_inventory@3
```

Thirty days of silence flags a retire candidate. Success under 70% flags a failing routine. Fingerprint similarity above the threshold flags a duplicate. The weekly `sys doctor` scan proposes merges and consolidations the same way.

Proposes. Never executes. Sweeps suggest; humans dispose.

---

## Retiring with dignity

In traditional engineering, someone `git rm`s an old script, and three cron jobs and two dashboards die silently six weeks later.

In Capcli, you retire:

```bash
$ capcli routine retire legacy_billing -m "superseded by billing_v2"
```

```
[dev:tier_1]  ✓  retired

  capability:  cap://legacy_billing@8
  status:      retired
  dependents:  0 active dependencies verified
  audit:       op_11d4
```

Two invariants make this safe:

1. **Dependency protection.** If another routine or a cron schedule still calls `cap://legacy_billing@8`, retirement is refused — `exit 2`. Detach the consumers first.
2. **Provenance survives.** The script becomes uncallable, but its version hashes stay pinned in the causal DAG forever. Historical replays keep working. The story of what it did cannot be deleted, because nothing can delete it.

Retiring a routine with a bound schedule disables that schedule loudly, on purpose. No orphans. No mysteries six weeks later.

---

## The One Rule

**A routine must be as easy to subtract as it was to add.**

Automation you can't safely remove isn't automation. It's sediment.

---

**Something specific broke?** → [guides/troubleshooting.md](../guides/troubleshooting.md)

**Deeper recovery mechanics:** → [understand/recovery.md](../understand/recovery.md)

**Every maintenance command contract — stats, rollback, sweep, retire:** → [reference/commands/routine.md](../reference/commands/routine.md)
