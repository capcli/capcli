# Provenance

Every action has an origin. Every change has a history. Provenance is the machinery that keeps those two from becoming "approximately remembered" — because in an agent-driven system, approximately remembered is a synonym for *litigated*.

---

## The chain

Mandatory `-m` intent is where provenance starts — not as paperwork, but as the root of a causal DAG:

```
root intent:  "fulfill paid order for customer checkout"     ← human-meaningful sentence
    └── session goal: dispatch ORD-8842
            └── routine.run: dispatch_order@4 (pinned)
                    ├── db.query        op_9f2c
                    ├── api.call        op_9f2d
                    └── db.execute      op_9f2e   ← leaf: the actual mutation
```

Every event carries `caused_by`, `intent`, `intent_chain`. Every leaf can walk to its root:

```bash
$ capcli sys audit trace op_9f2e --explain
```

```text
[dev:tier_1]  op_9f2e → op_9f2d → op_9f2c → root

  root intent:    "fulfill paid order for customer checkout"
  session:        goal: dispatch ORD-8842
  routine:        dispatch_order@4 (pinned)
  ops:            db.query → api.call(logistics.shipments.create) → db.execute
```

## Why it's tamper-proof *by construction*

Provenance here isn't a log file — it's the hash-chained `_audit` spine (per-row SHA-256, verified at boot, checkpointed to WORM object storage). Three properties follow, and they're structural:

1. **Agents can't gaslight.** "I optimized the database by removing redundant user records" is a sentence that dies when the trace shows `sql.query (delete) → denied`. The ledger's version wins; your LLM's recollection is commentary.
2. **Humans can't quietly rewrite.** Edit a row, break a link, and every *subsequent* event invalidates. The kernel refuses to boot on fiction.
3. **The kernel can't un-see.** Even kernel actions — env merges, vault sets, agent registrations — are events in the same chain. No layer sits above the story.

## Provenance survives deletion

Subtraction is a first-class operation here — routines retire, bindings remove, keys expire. Provenance doesn't:

- Retired routines keep their run history (max 25 versions kept, rollback depth 5).
- `routine rollback <name> --to-trust draft` rewrites *trust*, and the rewrite itself is an event.
- Restores are events. Denials are events (`effect: none` — the attempt happened even though the effect didn't).

The only thing you can't do in this system is make history *not have happened*. Given what this system is for — supervising probabilistic actors — that's the correct number of exceptions: zero.

## What it's for, practically

- **Post-mortems:** incident → `trace --explain` → root intent → the human sentence that started it. Post-mortems stop being archaeology.
- **Promotion cases:** trust climbs on *cited* evidence (`provenance: promotion evidence at op_7a1b`), not testimony.
- **Compliance:** the receipt (`sys doctor --report`) is the export: `ledger_root_hash`, `audited_events`, `policy_denials`, `secret_leaks: 0`.

---

**Next** → [progressive-disclosure.md](progressive-disclosure.md) — why these docs feed you concepts exactly as late as possible.
