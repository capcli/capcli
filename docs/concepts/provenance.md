# Provenance

In most systems, history is a courtesy. Logs get rotated, rotated logs get "lost," and lost logs get described in the post-mortem as "unavailable."

In Capcli, history is a contract.

Every action knows where it came from. Every version knows exactly which code it was. Every retirement leaves a body you can autopsy. **Nothing forgets. That's the feature.**

---

## The chain of custody for one action

Ask "why did my database change" in a normal stack and you get archaeology: grep timestamps, correlate deploy logs, interview the intern. Ask Capcli, and it walks the family tree:

```bash
$ capcli sys audit trace op_9f2e --explain
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

Four mechanisms made that answer possible:

1. **Intent rides every op.** Mutating operations require `-m`; missing intent is a refusal (`exit 3`) before a single row moves. The goal propagates down the chain — session goal → routine intent → op intent — and the full chain is stamped on every leaf event.
2. **Every leaf event hashes into the spine.** Each row in `_audit` chains to the row before it via SHA-256. The table is strictly append-only and kernel-written. You can query it. You cannot edit it. The kernel would rather not boot than run on a broken chain.
3. **Causality is a pointer, not a guess.** `caused_by` links each op to its parent operation. The DAG isn't reconstructed from timestamps after the fact — it was recorded as it happened.
4. **Denials get the same treatment.** A blocked `DELETE FROM orders` is an event with `effect: none`. The walls your agent bumped into are part of its history too.

---

## Version provenance: code that can't lie about itself

Every capability version pins two hashes: **`code_hash`** (the bytes that run) and **`manifest_hash`** (the declared shape — which tables, which verbs, what costs). The pair is recorded per version alongside `created_by` and `promoted_by`.

Consequences:

- **No silent edits.** Touch the code, get a new version. There is no path where the routine you proved this morning is subtly not the routine that ran this afternoon.
- **The journey is recorded.** `promoted_through` remembers the `[dev, sim, prod]` progression. Merged routines remember their origins via `consolidated_from`.
- **Proofs attach to versions, not vibes.** When `routine prove` compares the runtime fingerprint against the static manifest, both sides are hash-pinned. Drift isn't a feeling — it's a mismatch between two hashes.

This is what "trust" is made of here: not a person vouching for the code, but the code being unable to misrepresent itself.

---

## Retirement is an archive, not a shredder

`routine retire` makes a capability uncallable. It does not make it unknown.

The provenance graph survives retirement by design: past events still point at `routine@version`, retired versions still resolve to their hashes, and the audit spine still holds every run they ever took. API verbs retire the same way — uncallable, preserved.

Which means the question "who called the thing we killed, and what did it do?" always has an answer — because the question arrives *after* the retirement, and the answer was written down *before* it.

---

## Replay works because history can't be rewritten

`sys audit replay --from <point>` re-executes recorded history against forked state. This only works because the record is immutable: replay trusts the ledger precisely because nothing else was ever allowed to touch it.

Two guardrails worth knowing:

- **Replay runs under *current* policy**, not the policy of the day being replayed. History is a record, not a time machine for rules.
- **External effects are flagged `replay: manual`.** Auto-replaying a Stripe call is exactly the kind of thing this architecture exists to prevent. The kernel will not re-bill reality on your behalf.

---

## The One Rule

**Nothing forgets. That's the feature.**

Provenance isn't a compliance feature you enable for audit season. It's the reason replay, forensics, promotion evidence, and sleep-at-night all work the same way: the ledger said so, and the ledger cannot be persuaded otherwise.

---

**The full anatomy — operations, effects, events, and where provenance lives in them** → [../understand/effects.md](../understand/effects.md)

**Exact audit structures and query surfaces** → [../reference/audit.md](../reference/audit.md)

**Watch the spine refuse to be tampered with** → [../understand/audit.md](../understand/audit.md)
