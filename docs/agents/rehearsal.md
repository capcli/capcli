# Rehearsal

You are probabilistic. Production is not.

The contract gives you a dry-run flag and a simulator. Use them in order: plan first, prove second, execute last.

---

## Level 1: `--dry-run` — the plan without the physics

Every mutating surface accepts `--dry-run`: `run`, `sql`, `rule apply`, `api sync`, `sys audit replay`. Gates run; state doesn't.

```bash
$ capcli run dispatch_order -p order_id=ORD-8842 -p carrier=fedex \
    -m "fulfill paid order for customer checkout" --dry-run --json
```

```
{
  "exit": 0,
  "json": {
    "simulated": true,
    "capability": "cap://dispatch_order@4",
    "manifest": [
      "db.query    orders (read)",
      "api.call    logistics.shipments.create",
      "db.execute  orders (write)"
    ],
    "estimated_cost_class": "1x read, 1x http, 1x write",
    "state_modified": false
  },
  "text": "[dev:tier_1]  dry-run  ✓"
}
```

Decode: `simulated: true` plus `state_modified: false`. The manifest is the exact call sequence the real run will follow. If the plan surprises you here, imagine how it would have surprised you in prod. This is H2 of the harness onboarding journey — plan before you execute.

---

## Level 2: `routine prove --env sim` — real execution, fake world

Dry-run checks the plan. Prove *executes* it — sandboxed, against masked data, egress routed to sim:

```bash
$ capcli routine prove refund_order -p order_id=ORD-9912 -p amount=50 \
    --env sim --json
```

```
{
  "exit": 0,
  "json": {
    "capability": "cap://refund_order@1",
    "manifest_declared": [
      "db.query",
      "api.call(stripe.refund)",
      "db.execute"
    ],
    "manifest_executed": [
      "db.query",
      "api.call(stripe.refund)",
      "db.execute"
    ],
    "match": "100% subset",
    "policy_denials": 0,
    "drift_events": 0,
    "audit_chain": ["op_992a", "op_992b", "op_992c"]
  },
  "text": "[sim:tier_1]  refund_order@1  ✓  prove passed (412ms)"
}
```

Decode: prove runs at draft trust regardless of what the decorator declares, samples real historical parameter values from the audit mirror, and compares the *executed* leaf sequence against the *declared* manifest. Synthetic fixtures are banned as evidence — you are rehearsing against history, not fiction.

---

## The subset law

Manifest matching is not string equality. It's a subset contract:

- **executed ⊆ declared** — every leaf that ran must have been declared.
- **defensive branching is free** — early returns and guards that skipped declared leaves pass without penalty; skipped verbs report a fractional match (3/4).
- **undeclared leaves are anomalies** — executing a primitive you never declared fires `governance.anomaly` and zeroes your promotion math.

A fractional match is a defensive branch. An undeclared leaf is drift. Learn the difference before you debug the wrong one.

---

## What sim actually is

- Data is seeded from prod with sensitive columns masked — emails become `anon_*@sim.local`, format-preserving.
- Per-verb sim modes are declared in the manifest: `sandbox` (provider test endpoint via overlay), `mock` (canned fixture), `dry-run` (parameter and policy check only), `skip` (excluded from the fingerprint), `prod-only` (resolves to schema-validated mocks in sim — physical egress denied outside prod).
- Quota is partitioned by env: sim rehearsals burn sim quota only. You cannot accidentally spend prod rate budget from a rehearsal.
- Sim gaps ride along in inspect's `budget_status`, so the mocks never surprise you mid-proof.

---

## The latency gate

Rehearsal p95 above 70% of the declared timeout ceiling denies promotion. A prove that passes functionally but drags temporally is a failed prove. If p95 is near the ceiling, split the work — don't widen the ceiling.

---

**Proof passed? Earn the rung** → [proving.md](proving.md)

**What humans call this** → [../automate/rehearsal.md](../automate/rehearsal.md)
