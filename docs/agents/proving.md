# Proving Contract (Agent-Facing)

Evidence is the only currency that purchases trust. Here is the exchange rate.

---

## What you must produce

| For | Produce | Via |
|---|---|---|
| Routine promotion | Rehearsal outcomes: runs, violations=0, p50/p95 in envelope | `routine prove --env sim` |
| API activation | Contract replay passes (calls 1–3) | `api activate` + training wheels |
| API promotion | Sim-mode proof + reasons | `api prove`, `api ship` |
| Any prod-adjacent claim | Ledger-cited facts only | `sys audit trace`, `routine stats` |

**Every claim you make to a human should be ledger-citable.** "It works" is not evidence. "87 sim runs, 97.8% success, p95 1100ms, violations 0, evidence at op_7a1b" is evidence. Same information, but only one of them survives an audit walk.

## Reading your own receipts

```bash
capcli routine stats <name> --deep
```

```text
[dev:tier_1]  cap://order_refund@7

  trust:       reviewed
  runs:        89 total · 87 sim · 2 dev
  success:     97.8% (87/89)
  p50 / p95:   410ms / 1100ms
  envelope:    6 ops · 20s · 500 result tokens
  violations:  0 schema · 0 policy · 0 budget (last 30d)
  ops_used:    avg 4.1 / 6 declared
  provenance:  promotion evidence at op_7a1b
```

## The hard gates (not adjustable, not appealable)

- **p95 > 70% of timeout ceiling** ⇒ promotion denied. Rehearse against the envelope, not against hope.
- **Any violation (schema/policy/budget)** ⇒ not promotion-eligible. Zero. Not "one, but minor."
- **Training wheels incomplete** (api verbs) ⇒ no standard governance until call 4 passes.
- **Tier 2 host** ⇒ pinned rungs unreachable (`exit 2`). Physically, not politically.
- **Auto-demotion** ⇒ sustained failure (< 70% success) benches the routine. Your proof must be *current*, not vintage.

## What is NOT evidence

- Tests the routine's author wrote about itself. (Fox, henhouse, clipboard.)
- Your confidence, however sincere.
- Stack Overflow answers, tutorials, or the phrase "it should work."
- Success in *another* world. Imports enter at draft; zero trust inheritance. "It worked in the other repo" is archaeology, not evidence.

## When evidence contradicts you

The ledger wins. Full stop. If your memory of events and `_audit` disagree, your memory is wrong — this is not an insult, it is the entire reason the spine is append-only and hash-chained. Two observers, one cryptographically guaranteed to be honest. Choose accordingly.

---

**The boundary this all hangs from** → [contract.md](contract.md)
