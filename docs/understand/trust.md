# Trust

Your agent wrote a routine in `dev` on a Tuesday. It works. It's charming. It's also, statistically, a raccoon with a keyboard.

Capcli's answer is the **trust ladder**: three rungs — `draft`, `reviewed`, `pinned` — that decide how much blast radius a capability is allowed.

---

## The rungs

| Rung | Rows it may touch | Where it runs | Who gets there |
|---|---|---|---|
| **draft** | 10 / write | dev only | Everyone. This is where you're born. |
| **reviewed** | 100 / write | dev + sim | `routine ship reviewed` + proof |
| **pinned** | 500 / write | dev + sim + prod | `routine ship pinned` + proof + a reason |

Trust is per-*capability*, not per-agent. The routine climbs; the agent doesn't. A Nobel laureate prompt gets draft limits on a draft routine. A Tuesday raccoon gets the same. The kernel doesn't read résumés.

---

## Watch a promotion

```bash
$ capcli routine ship order_refund reviewed --reason "89 runs, 97.8% success in sim"
```

```text
[dev:tier_1]  ✓  promoted

  capability:  cap://order_refund@7
  trust:       draft → reviewed
  evidence:    89 sim runs · 97.8% success · p95 1100ms (within envelope)
  ceiling:     rows_affected cap now 100/run
```

The promotion *cites its evidence*. No vibes, no "I tested it in staging once." Latency rehearsed, success counted, envelope checked — p95 above 70% of the timeout ceiling is an automatic denial, because "slow" is just "down" wearing a trench coat.

---

## What the rungs physically gate

Trust isn't a badge. It's compiled into the authorizer:

```bash
$ capcli sql "SELECT value FROM secrets WHERE name = 'stripe_key'"
```

```text
[dev:tier_1]  ✗  exit 2

  FAIL  policy.authorizer.trust_gate
        SELECT value FROM secrets WHERE name = 'stripe_key'
               ^^^^^
        Column 'value' denied for caller trust level: draft

  state_modified: false
  layer: authorizer
  remedy: draft trust cannot read secrets; promote routine to reviewed
```

Same query, same agent, same database — but from inside a `reviewed` routine, the answer arrives with the value masked per policy. The gate is at the C level, at prepare-time. There is no prompt clever enough to charm `sqlite3_prepare_v2`.

Also gated: draft routines can't be dependencies (callee floor: `reviewed`), pinned routines refuse to run on Tier 2 hosts (`exit 2`), and imported templates enter at draft with **zero promotional credit** — pre-pinned imports are banned, because "trust me, it worked on another machine" is how incidents get their LinkedIn profiles.

---

## Trust can fall, not just climb

Sustained failure — success rate cratering, anomaly spikes, policy denials — auto-demotes the routine back to `draft`. A circuit breaker, not a performance review. The routine gets benched; its history doesn't get erased (provenance survives retirement, see [recovery.md](recovery.md)).

You can veto a promotion too: `routine rollback --to-trust draft` walks it back down. Trust is a dial you control, not a ladder you're stuck on.

---

## Trust × environments

Two axes, and people love to confuse them:

- **Trust axis** bounds the *capability*: how big a hole it can dig.
- **Environment axis** bounds the *state*: which dirt it's allowed to dig in (`dev` / `sim` / `prod`).

Draft routine in prod? Refused. Pinned routine in dev? Fine — pins aren't punishment. The full matrix lives in [environments.md](environments.md).

---

## The one-liner

> Draft is a suggestion you make to dev. Reviewed is a promise you make to sim. Pinned is a vow you make to prod.

Promotions come with evidence. Demotions come automatically. And nothing, *nothing*, inherits trust it didn't earn inside *this* kernel.

---

**Who's holding the ladder** → [identity.md](identity.md)

**How you rehearse before you prove** → [../automate/rehearsal.md](../automate/rehearsal.md)
