# Promotion

The routine passed rehearsal. The evidence is on file. Now it asks for a bigger blast radius, and the kernel asks: *"on what basis?"*

Promotion is the ceremony where trust climbs: **draft → reviewed → pinned.**

---

## The climb

```bash
$ capcli routine ship order_refund reviewed --reason "89 runs, 97.8% success, p95 1100ms in envelope"
```

```text
[dev:tier_1]  ✓  promoted

  capability:  cap://order_refund@7
  trust:       draft → reviewed
  evidence:    89 sim runs · 97.8% success · p95 1100ms (within envelope)
  ceiling:     rows_affected cap now 100/run
  veto:        routine rollback order_refund --to-trust draft
```

Same ceremony, higher stakes:

```bash
$ capcli routine ship dispatch_order pinned --reason "214 runs, 99.1% success, six weeks clean"
```

```text
[dev:tier_1]  ✓  promoted

  capability:  cap://dispatch_order@4
  trust:       reviewed → pinned
  evidence:    214 runs · 99.1% success · p95 890ms (within envelope)
  ceiling:     rows_affected cap now 500/run · prod-eligible · endpoint-servable
  veto:        routine rollback dispatch_order --to-trust draft
```

Note the third line of each: **the veto ships with the promotion.** Trust you can't take back isn't trust, it's a hostage situation.

---

## What each rung unlocks

| Rung | Rows / write | Runs in | Unlocks |
|---|---|---|---|
| **draft** | 10 | dev | Nothing. Gratitude. |
| **reviewed** | 100 | dev, sim | Bigger batches, secret access (masked per policy), routine dependencies |
| **pinned** | 500 | dev, sim, **prod** | Prod writes, `bind endpoint` serving (REST + MCP), cron-bound production jobs |

And what it *costs*: pinned routines refuse to run on Tier 2 hosts (`exit 2` — degraded isolation doesn't get prod keys), promotion demands rehearsed evidence (p95 within 70% of ceiling), and sustained failure triggers the circuit-breaker demotion back to `draft`. The ladder has no elevator down to "sorry, exceptions."

---

## The review queue

You don't have to babysit promotions in real time. Queue them for a human with a calendar:

```bash
$ capcli routine ship archive_old_orders reviewed --queue
```

```text
[dev:tier_1]  ⏳  queued

  capability:  cap://archive_old_orders@3
  evidence:    41 runs · 68.3% success · p95 2100ms
  review:      pending human approval
```

(In this fictional-but-verbatim-per-the-contract example, the evidence is *terrible* — 68.3% — and the queue is exactly where it belongs. The auto-demotion circuit is already sharpening its pencil.)

---

## Promotion rules that surprise people

1. **Evidence is non-negotiable.** No proof, no rung. Confidence is not a parameter.
2. **Imports start at draft.** A pre-pinned routine from another world is banned — zero trust inheritance. "It worked in the other repo" is a *story*, not *evidence*.
3. **Deps need rungs.** A routine calling another routine needs the callee at `reviewed`+. Drafts can't be load-bearing.
4. **API verbs climb the same ladder.** `api activate` → draft + training wheels; `api ship` promotes. Same physics, different noun.
5. **Demotion is automatic.** Success craters, the routine benches itself. You get the memo, not the bill.

---

**Now it runs while you sleep** → [operation.md](operation.md)
