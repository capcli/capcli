# Trust: Draft, Reviewed, Pinned

Your agent is 100% confident in code it wrote eleven seconds ago. That's not confidence — that's amnesia with good posture.

So before describing the ladder, let's be honest about why a ladder needs to exist at all:

* **Agents hallucinate.** They'll describe a refactor they never ran and a test suite that never existed.
* **Code drifts.** Version 4 is not version 3, and six weeks later nobody remembers what changed.
* **Evidence beats vibes.** A measured success rate is a fact. A review comment saying "looks good to me" is a vibe.

Capcli doesn't ask whether code *seems* fine. It asks what the code has **proven** — and it makes the answer a physical property, not a policy memo.

---

## 1. The Ladder

Three rungs, climbed in order, never skipped:

| Rung | What it means | What it buys |
|---|---|---|
| **draft** | unproven, exploratory | Runs in `dev`. Sandboxed egress, `WHERE` required, no secrets, 10-row write ceiling |
| **reviewed** | proven in sim, signed off | Bulk updates unlocked, 100-row ceiling, can serve as a cross-agent dependency |
| **pinned** | hardened operational baseline | Unattended execution — headless crons and endpoints, 500-row ceiling. Requires a Tier 1 host |

Remember the two axes: **trust bounds capabilities; environments bound state.** They pair by convention — dev with draft, sim with reviewed, prod with pinned — but they are independent ([environments.md](environments.md)). A reviewed routine in prod is a visitor; a pinned routine in dev is on vacation.

And trust is never inherited. Imported routines and world templates enter strictly at draft, version 1 — there are no pre-pinned downloads, no matter how shiny the blueprint.

---

## 2. The Rung Is Physical

This is not a label in a config file. Try to run a draft routine in prod:

```bash
$ capcli run experimental_cleanup -p dry=true \
    -m "test cleanup in prod" --env prod
```

```text
[prod:tier_1]  ✗  exit 2

  FAIL  policy.trust.draft_writes_denied
        capability: cap://experimental_cleanup@1
        trust: draft
        env: prod

  state_modified: false
  layer: trust
  remedy: promote to reviewed via routine ship, or run in dev/sim
```

The overlay says no, the authorizer says no, the kernel says no — three locks on one door. Related walls, all attested: invoking a *pinned* routine on a Tier 2 host throws `exit 2` (`E045_TIER2_PINNED_DENIED`), because pinned execution demands hardware containment. And a running routine cannot `ship` itself — trust escalation requires human or CI authority.

---

## 3. The Ship Gate: All Metrics, No Vibes

First, prove it in simulation, against masked history:

```bash
$ capcli routine prove refund_order -p order_id=ORD-9912 -p amount=50 \
    --env sim
```

```text
[sim:tier_1]  refund_order@1  ✓  prove passed (412ms)

  manifest_declared: db.query → api.call(stripe.refund) → db.execute
  manifest_executed: db.query → api.call(stripe.refund) → db.execute
  match:             100% subset
  policy_denials:    0
  drift_events:      0
  audit:             op_992a → op_992b → op_992c
```

Then ship it. The kernel reads `routine_stats` and the audit mirror directly — the conjunction has to pass on every metric at once:

| Metric | Threshold |
|---|---|
| Invariant suite | 100% pass |
| Success rate | ≥ 95% |
| Manifest match | executed ⊆ declared, zero undeclared leaves |
| Policy denials | exactly 0 |
| Fingerprint drift | exactly 0 |
| Latency | p95 ≤ 70% of declared max duration |

```bash
$ capcli routine ship refund_order reviewed \
    --reason "passed quarterly compliance rehearsal"
```

```text
[dev:tier_1]  refund_order@1  ✓  promoted to reviewed

  invariant_suite_passed:   true
  success_rate:             0.96
  manifest_subset_match:    true
  policy_denials:           0
  fingerprint_drift_events: 0
  p95_duration:             610ms (≤ 70% of declared max)
  audit:                    op_11d6 (routine.auto_promoted)
```

Fail even one metric and there is no partial credit: the routine routes to the human approval queue (`capcli routine ship <name> reviewed --queue`, inspected with `capcli routine pending`). Humans batch-approve from evidence, and the queue that ages past its SLA raises an alarm rather than silently rotting.

---

## 4. The 1-Hour Parole Window

Promotion is not a diploma. It's parole.

For the first **60 minutes** after promotion, the kernel runs canary telemetry against live traffic — error rates, latency, denials. An anomaly spike or a policy denial fires an autonomous circuit breaker: the promotion is revoked on the spot and the routine drops straight back to `draft`. No human has to be awake at 03:00 for the rollback to happen.

Humans keep two forms of after-the-fact control: a retroactive veto (`routine rollback` to draft trust), and demotion that meets zero gate resistance — falling is always easier than climbing. Sustained failure needs no human at all: success below 0.70 across 20 runs auto-demotes the routine to draft.

---

## 5. Retirement Keeps the Receipts

Nothing is ever deleted — not even the things you're glad to be rid of:

```bash
$ capcli routine retire legacy_billing -m "superseded by billing_v2"
```

```text
[dev:tier_1]  ✓  retired

  capability:  cap://legacy_billing@8
  status:      retired
  dependents:  0 active dependencies verified
  audit:       op_11d4
```

Retired means uncallable — but the version hashes stay in the causal DAG forever, so historical replays and forensic traces still resolve. Two protections do the housekeeping: retirement is refused (`exit 2`) while active dependencies still call the routine, and version history is bounded at 25 versions kept with rollback depth 5, so the registry stays lean while the ledger stays complete. No immortal routines — decay and consolidation are part of the design, not an apology.

The full pipeline — rehearsal, evidence, promotion, operation, subtraction — is walked end-to-end in [automate/promotion.md](../automate/promotion.md), and every exact command contract lives in [reference/commands/routine.md](../reference/commands/routine.md).

---

## The One Rule

**Trust is earned in sim, granted by gates, and revoked by telemetry.**

Not by vibes. Not by seniority. By numbers with hashes attached — and a circuit breaker that doesn't need your permission to trip.

---

**The other axis: where state lives** → [environments.md](environments.md)

**The promotion pipeline, end to end** → [automate/promotion.md](../automate/promotion.md)

**Exact `prove` / `ship` / `rollback` / `retire` contracts** → [reference/commands/routine.md](../reference/commands/routine.md)
