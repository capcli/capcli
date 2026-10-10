# Repetition

Automation starts with a sentence every operator eventually says: *I keep doing this.*

This page covers the recognition half of that moment — spotting repeated work in the record, judging whether repetition deserves a routine, and handing the pattern over to codification. The mechanics of building the routine live in [Codification](../agents/codification.md).

---

## Where repetition hides

Repeated work rarely announces itself. It hides in four places:

| Hiding place | What it looks like |
|---|---|
| **Your own turns** | The same query, refund flow, or report assembled by hand every morning |
| **Audit fingerprints** | Identical leaf sequences recurring across sessions in `routine_fingerprints` |
| **Gap reports** | `capcli run search gaps --since 7d` lists multi-step chains no routine covers |
| **Denial clusters** | The same bounded write retried manually after the same remedy, turn after turn |

The ledger remembers what memory smooths over. A pattern executed nine times feels like "occasionally"; the count in `_audit` is exact.

---

## The recognition pass

```bash
capcli run search gaps --since 7d
capcli sys audit query "SELECT command, count(*) FROM _audit GROUP BY command HAVING count(*) > 5"
```

Read the output as a census, not a to-do list. Each candidate gets three questions:

1. **Count.** How many times in the window? Twice is coincidence; a steady cadence is a workload.
2. **Variance.** What changes between runs — values only, or structure too? Value-only variance maps cleanly onto typed parameters.
3. **Cost of failure.** What breaks when step three of five never runs? Atomicity matters precisely where partial completion misleads.

A candidate passing all three questions moves to codification. A candidate failing any one stays manual, and the record keeps accumulating evidence either way.

---

## Patterns that repeat well

- **Fixed pipelines.** Refund, onboarding, reconciliation: same steps, same order, different subject each time.
- **Briefings.** Domain counts and status rollups an agent rebuilds from raw tables at session start. The `overview` routine exists for exactly this shape.
- **Bounded batches.** Chunked updates with identical guards, chunk after chunk, day after day.
- **Provider rituals.** A catalog verb sequence — fetch, validate, record, diff — repeated per provider.

## Patterns that repeat badly

- **Exploration.** Queries whose structure changes as understanding grows. Codifying exploration freezes a half-formed question.
- **Judgement calls.** Sequences where a human picks the next step from intermediate results. The branching lives in the reasoning, not the record.
- **Rare rescues.** Disaster steps executed twice a year. A checklist in a document serves them better than a rehearsed routine.

---

## From recognition to routine

Recognition ends with a named candidate and a parameter list. Codification takes it from there: scaffold, shape gate, sim proving, evidence-based promotion.

```
notice → count → judge variance → name the candidate → codify → prove → promote
```

Promotion is a separate decision with separate evidence. Details: [Promotion](promotion.md). The command surface for the resulting routine: [routine.md](routine.md).

---

**Agent-facing codification contract:** → [Codification](../agents/codification.md)
**What happens after the routine exists:** → [Promotion](promotion.md)
