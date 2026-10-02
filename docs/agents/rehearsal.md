# Rehearsal Contract (Agent-Facing)

"Will this work?" is a question you answer *before* the blast radius is real.

---

## The calls

```bash
# Routine rehearsal in simulation
capcli routine prove <name> [-p k=v] [--env sim]

# API verb contract proof
capcli api prove <provider.verb> [-p k=v] [--env sim]

# SQL plan without execution
capcli sql "<query>" -m "<intent>" --dry-run
```

```text
[dev:tier_1]  dry-run  ✓

  statement:     UPDATE orders SET status = 'shipped' WHERE status = 'processing' LIMIT 50
  ast_check:     pass
  authorizer:    pass (write on orders allowed)
  intent:        declared
  estimated_rows: 34
  blast_radius:  bounded (LIMIT 50)

  state_modified: false
  note:           no execution occurred
```

`--dry-run` runs the full gate stack — intent, AST, authorizer, EXPLAIN cross-check — and reports the verdict with **zero execution**. The closest thing to time travel your toolchain offers.

## Sim modes for API verbs

| Mode | Wire behavior | Use |
|---|---|---|
| `sandbox` | Provider's sandbox URL | Contract-shape check against live-ish vendor |
| `mock` | Canned fixture, no packets | Logic check, zero external dependence |
| `dry-run` | Schema validation, `simulated: true` | Payload-shape check |

Newly activated verbs run their first 3 calls as forced synthetic contract replays (training wheels); call 4 is standard governance. This is not optional and not skippable. The training wheels are welded on.

---

## Your obligations during rehearsal

1. **Rehearse the parameter space, not one lucky case.** Edge params (`LIMIT` boundaries, empty sets, max rows) are where denials live.
2. **Read the envelope, not just the verdict.** p95 vs. timeout ceiling matters: above 70% of ceiling, promotion is denied. Slow is a pre-crash with better manners.
3. **Count violations, not successes.** `0 schema · 0 policy · 0 budget` is the pass condition. One violation disqualifies — there is no partial credit in physics.
4. **Record what you learned.** Rehearsal outcomes are audit events; your future promotion case cites them. Evidence you didn't generate doesn't exist.

## What rehearsal does NOT prove

- Prod-only failure modes (auth drift, quota neighbors, NTP quirks).
- Your judgment. The first prod call remains a distinct, watched event (`api.first_prod_call`, approver on record).

Rehearsal raises confidence from "vibes" to "measured." It does not raise it to "certainty" — nothing does; that's why the ledger exists.

---

**When the real call goes sideways anyway** → [feedback.md](feedback.md)
