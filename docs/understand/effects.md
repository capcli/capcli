# Ops, Effects, Events, & Provenance

People say "operation," "effect," "event," and "provenance" like they're synonyms. They're four different things — and the difference is the difference between a system you can debug and a log file you can skim while it lies to you.

---

## 1. Four Words, Four Layers

| Word | What it is | Where it lives | Can it be undone? |
|---|---|---|---|
| **Operation** | one atomic capability call — `op_9f2c` | the execution frame | it happens or it doesn't |
| **Effect** | the state change it caused | domain tables in `workspace.db` | yes — snapshots rewind state |
| **Event** | the immutable record of it | `_audit`, mirrored to JSONL | no — append-only, hash-chained |
| **Provenance** | the lineage behind it | version hashes + the causal DAG | no — pinned permanently |

An operation is a verb. An effect is a scar on the World. An event is the signed statement that the verb happened. Provenance is the family tree explaining *why*.

---

## 2. One Run, Decoded

You've seen this command before. Now look at what it's actually made of:

```bash
$ capcli run dispatch_order -p order_id=ORD-8842 -p carrier=fedex \
    -m "fulfill paid order for customer checkout"
```

```text
[dev:tier_1]  dispatch_order@4  ✓  1.2s

  status:    dispatched
  tracking:  794644790133
  ops_used:  3/8
  audit:     op_9f2c → op_9f2d → op_9f2e
```

Three operations: `op_9f2c → op_9f2d → op_9f2e`. Each one got its own id, its own gate check, its own audit row. Want to see the whole decomposition — ops, effects, and the intent that caused them? Ask the spine to walk the tree:

```bash
$ capcli sys audit trace op_9f2e
```

```text
[dev:tier_1]  Causal DAG Trace (op_9f2e)

  ses_a992f  session.start        "fulfill urgent pending orders"
    └── op_9f2c  routine.dispatch_order@4
          ├── op_9f2d  db.query (orders)         ✓ [allowed]  12ms
          ├── op_9f2e  api.call (fedex.ship)     ✓ [allowed]  340ms
          │     └── tracking: 794644790133
          └── op_9f2f  db.execute (orders)       ✓ [allowed]  18ms
                └── status = 'shipped' (1 row)

  Root Intent: "fulfill urgent pending orders"
  Authority:   user:alice (via agt_7f3k)
  Integrity:   valid hash link (chain verified)
```

Label the lines and the four words separate cleanly:

* **Operations:** `op_9f2c` (the routine), `op_9f2d` (a read), `op_9f2e` (an API call), `op_9f2f` (a write).
* **Effects:** `tracking: 794644790133` came back; `status = 'shipped' (1 row)` landed in `orders`.
* **Events:** every line of that trace *is* an `_audit` row — including the session start and the routine frame.
* **Provenance:** the `caused_by` links tying each leaf to its parent, the version (`dispatch_order@4`), the authority (`user:alice` via `agt_7f3k`), and the hash chain verifying it all.

---

## 3. The Distinctions That Earn Their Keep

**An operation can be denied — then the event exists and the effect doesn't.** Denials are first-class events with `rows_affected: 0` and `effect: none`, mathematically guaranteed by `state_modified: false`. You don't just audit what changed; you audit every wall your agent bumped into while trying to change things.

**Effects rewind. Events never do.** `capcli db restore` rewinds state to a snapshot — and the restore itself becomes a new event. Recovery is recorded, never hidden. Snapshots are the undo button for effects; there is no undo button for history, and that asymmetry is deliberate: [recovery.md](recovery.md).

**Provenance makes "which version did that?" a one-query question.** `code_hash` and `manifest_hash` are permanently linked per version, `promoted_by` records who elevated it, and `promoted_through` records the dev → sim → prod journey. The DAG ties the effect to the exact code that caused it.

**The ledger records outcomes, not noise.** Raw stdout and stderr are discarded at the terminal boundary. The canonical JSON outcome — rows, hashes, duration, exit code — is what gets hashed. The event says what happened, not what the process muttered while happening.

---

## 4. Event Anatomy

Every event row carries the same sections, whether it records a triumph or a denial:

```
identity    event · ts · env · stage · channel · trace_id
actor       agent · session · principal
causality   caused_by · intent · intent_chain
payload     capability · sql · params (recorded verbatim, for replay)
policy      decision (allow/denied) · rules_matched
outcome     rows_affected · result_hash · duration_ms · exit_code
```

Two details worth noticing: the payload is stored verbatim so history can be replayed deterministically, and `env` and `stage` are stamped on every leaf — sim events and prod events live in distinct namespaces and can never collide.

---

## 5. Zero Ghost Actions

The coverage rule is absolute: every CLI verb, binding, and environment transition advances the hash chain. If the audit sink can't take the write, the kernel halts with `exit 5` rather than execute unaudited. Nothing mutates off the record.

So the test of "what happened here" is never "what does the agent claim" — it's "what does the spine say." If it isn't in the memory spine, it didn't happen. If it is, it can't be erased.

---

## The One Rule

**Operations act. Effects change state. Events remember. Provenance explains why.**

And only one of the four can be rewound — the state. History is load-bearing.

---

**The spine itself, and how it refuses to be gaslit** → [audit.md](audit.md)

**Rewinding effects with snapshots** → [recovery.md](recovery.md)

**Exact audit structures and query surfaces** → [reference/audit.md](../reference/audit.md)
