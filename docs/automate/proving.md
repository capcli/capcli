# Proving

You think the routine works. Sweet. The kernel doesn't traffic in thoughts.

`capcli routine prove` is where belief gets exchanged for evidence. The pass runs your code in a sandbox jail — no host network, tmpfs scratch, wiped on exit — against masked sim data, with egress routed to fixtures. Then it does the part that actually matters: it compares what the code *declared* it would do against the leaf events that *actually* hit the audit trail.

---

## Reading the receipt

```bash
$ capcli routine prove refund_order -p order_id=ORD-9912 -p amount=50 \
    --env sim
```

```
[sim:tier_1]  refund_order@1  ✓  prove passed (412ms)

  manifest_declared: db.query → api.call(stripe.refund) → db.execute
  manifest_executed: db.query → api.call(stripe.refund) → db.execute
  match:             100% subset
  policy_denials:    0
  drift_events:      0
  audit:             op_992a → op_992b → op_992c
```

Line by line:

- **`manifest_declared`** — the promise, extracted from the `@routine` decorator and hashed before execution.
- **`manifest_executed`** — the runtime fingerprint: actual leaf events aggregated from the audit mirror.
- **`match: 100% subset`** — everything executed was declared. Executed must be a subset of declared. Always.
- **`policy_denials: 0`** — the run hit no authorizer wall, AST rule, or budget cage.
- **`drift_events: 0`** — the fingerprint never diverged from the manifest mid-flight.
- **`audit`** — the causal chain, traceable forever.

Two quiet mercies hide inside the subset law. Branches you declared but didn't take — early returns, defensive guards — pass without penalty. And skipped verbs report fractional match, not zero.

The law isn't "execute everything you declared." It's **"declare everything you execute."**

---

## What failure looks like

Add one undeclared write — a quick little status update you forgot to put in the manifest:

```bash
$ capcli routine prove refund_order -p order_id=ORD-9912 -p amount=50 \
    --env sim
```

```
[sim:tier_1]  refund_order@2  ✗  exit 3

  manifest_declared: db.query → api.call(stripe.refund) → db.execute
  manifest_executed: db.query → api.call(stripe.refund) → db.execute → db.execute
  match:             not a subset (1 undeclared leaf)
  policy_denials:    0
  drift_events:      1
  audit:             op_992a → op_992b → op_992c → op_992d
```

One undeclared leaf. That's a `governance.anomaly` event in the trail and a failed prove.

The fix is always the same: declare it in the manifest, or delete the write. Never "hide it better."

---

## Where the test parameters come from

Not from your imagination. Prove samples real historical values — actual parameter combinations from past audit events — via `capcli sys audit sample`.

Synthetic fixtures are banned as ship evidence. Confidence manufactured from inputs you invented is just fiction with latency numbers attached.

---

## The 5-point auto-promotion math

When a routine's telemetry is cold enough, the kernel can promote draft → reviewed without a human in the loop. The bar is a conjunction — **every** metric must pass:

| Metric | Threshold | What 94.9% gets you |
|---|---|---|
| Invariant suite | 100% pass | Denied. |
| Historical success rate | ≥ 95.0% | Denied. |
| Manifest match | 100% subset | Denied. |
| Policy denials | exactly 0 | Denied. |
| Fingerprint drift | exactly 0 | Denied. |
| Latency ceiling | p95 ≤ 70% of declared timeout | Denied. |

Fail one metric and the promotion is blocked. The routine goes to the human approval queue instead — a near-miss is a question, and questions are what humans are for.

Each threshold guards against a different lie:

- **Invariants** — boundary and idempotency assertions. Does it hold its edges?
- **Success rate** — did history actually bear it out?
- **Manifest** — did it touch only what it declared?
- **Denials** — did it run clean, or ricochet off walls?
- **Drift** — did execution stay identical to declaration?
- **p95 headroom** — is it fast enough to degrade gracefully under load?

---

## The One Rule

**Confidence is a number the kernel measured.**

Not a feeling. Not a code review. Not "it worked on my machine." A measured, hash-pinned, replayable fact.

---

**Passed the math? Time to climb the ladder:** → [promotion.md](promotion.md)

**Every command and flag for prove:** → [reference/commands/routine.md](../reference/commands/routine.md)

**Where leaf events live forever:** → [understand/audit.md](../understand/audit.md)
