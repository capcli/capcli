# Rehearsal

You wouldn't let a new hire push to prod on day one. You *especially* wouldn't let a new hire who is probabilistic by construction push to prod on day one.

Rehearsal is `sim`: your routine, running for real, against a world that can't hurt you.

---

## The move

```bash
$ capcli routine prove order_refund -p order_id=ORD-8842 --env sim
```

```text
[sim:tier_1]  order_refund@7  ✓  3 proofs · 0 violations

  runs:          3
  env:           sim (seeded from prod, masked)
  api calls:     3 (sandbox mode — zero real wire)
  rows_affected: capped at 100 (reviewed ceiling)
  p50 / p95:     410ms / 1100ms (envelope: 20s)
  violations:    0 schema · 0 policy · 0 budget
  evidence:      recorded → promotion-eligible
```

Three full replays. Real DDL, real budget frames, real audit events — against seeded, masked `sim` data. Every `ctx.api.call` routes to provider sandboxes or recorded fixtures, so no packet of yours ever leaves the building. The routine thinks it's working. In a sense, it is.

That output is not encouragement. It's a **receipt**. `0 violations` is what you show whoever owns `prod` when they ask "and you tested this how?"

---

## What sim actually is

A full separate world: `envs/sim/workspace.db`, seeded from prod with sensitive columns masked, plus its own rate-limit partitions — so a rehearsal can't burn real quota and can't leak real customers. It's prod's stunt double: same skeleton, fake blood.

API verbs have three rehearsal modes, compiled per provider:

| Mode | What it does |
|---|---|
| `sandbox` | Calls the *provider's* sandbox URL. |
| `mock` | Returns a canned fixture. No wire at all. |
| `dry-run` | Validates the payload schema, returns `simulated: true`. |

Newly activated API verbs get **training wheels**: the first 3 calls are forced through synthetic contract replays against historical audit logs. Survive to call 4 without a schema violation? Graduated. It's driver's ed, but for HTTP.

---

## Rehearsal grades the envelope, not just the result

Passing isn't "it worked once." The kernel records the *shape* of the performance:

- **Latency vs ceiling** — p95 above 70% of the timeout ceiling fails promotion. Slow is just down in a trench coat.
- **Success rate** — counted across runs, not remembered across vibes.
- **Budget fit** — declared ops vs consumed ops. Declaring 50 and using 4 is fine; declaring 6 and crashing at 7 is a failed rehearsal.
- **First prod call is still watched** — even after promotion, the first real invocation is an audited event (`api.first_prod_call`) with an approver on record. Trust, but verify, but *also* keep verifying.

---

## The one rule

> If it hasn't succeeded in sim, it hasn't succeeded. It has merely *not yet failed* in front of the right audience.

---

**Turn the receipt into rungs** → [promotion.md](promotion.md)
