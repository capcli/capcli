# Routines

Repetition found. Sentence written. Now the mechanism.

A **routine** is a versioned, sandboxed, multi-step script — TypeScript or Python — that bundles database queries, external API calls, and business logic into one atomic unit. This is where your ad-hoc loop goes to become a hardened civil servant: described, bounded, hashed, and on the books.

---

## The scaffold

Don't start from a blank file. Start from the compliant one:

```bash
$ capcli routine new refund_order
```

```
[dev:tier_1]  refund_order@1  ✓  scaffolded

  path:         routines/refund_order.ts
  runtime:      typescript (bun)
  trust:        draft
  description:  (required — 5 word minimum)
  shape:        0/150 loc · 0/8 params · 0/3 imports
  audit:        op_31a7
```

The kernel wrote you a starter that already satisfies every governance bound. Every routine begins at `draft`, version `1` — no exceptions, no imported prestige.

---

## What you fill in

The scaffold carries the `@routine` decorator — the part the kernel reads, not the part you execute:

```typescript
export default routine(
  {
    name: "refund_order",
    trust: "draft",
    idempotent: true,
    description: "Refund cancelled order and archive",
    limits: { ops: 6, duration_s: 20 },
  },
  async (ctx) => {
    const order = await ctx.db.query(
      "SELECT id, total, status FROM orders WHERE id = ? LIMIT 1",
      [ctx.params.order_id],
    );
    await ctx.api.call("stripe.refund_charge", { amount: order[0].total }, "issue refund for cancelled order");
    await ctx.db.txn(async () => {
      /* mark order refunded, insert archive row */
    });
    return { refunded: order[0].id };
  },
);
```

Notice what your code *doesn't* do. No `try/catch` politics. No rate-limit math. No audit logging. The `ctx` object hands you governed primitives — `ctx.db.query`, `ctx.db.execute`, `ctx.api.call`, `ctx.db.txn` — and every one already passes through the authorizer, the budget cage, and the audit spine.

Your script composes. The kernel enforces.

---

## The shape police

Your LLM would love to write a 600-line monolith with fourteen parameters and a utility-class hierarchy. **Capcli hates that.** The kernel measures physical dimensions before anything registers, proves, or ships:

| Dimension | Ceiling | Why |
|---|---|---|
| Lines of code | **150** | You're writing an atomic procedure, not Django. |
| File size | **2,000 tokens** | Inspecting it shouldn't bankrupt a context window. |
| Parameters | **8** | Fourteen args means your design is bad and you should feel bad. |
| Routine imports | **3** | No twelve-layer lasagna. |
| Description | **5 words min, 60 tokens max** | If agents can't search for it, it doesn't ship. |

Breach any of these and the intake gate kills it, with the receipts:

```bash
$ capcli routine prove mega_sync --env sim
```

```
[sim:tier_1]  mega_sync@1  ✗  exit 2

  FAIL  governance.deny — routine_shape.loc
        file has 342 LOC, max is 150

  state_modified: false
  remedy: split it, or adjust governance config
```

You don't argue with the gate. You split the routine.

---

## The manifest: a promise with a hash

Alongside the code, every routine carries a **manifest** — its declaration of what it will touch: the call sequence of API verbs, database targets with access mode, transaction wrappers, an estimated cost class, and per-verb sim modes.

At prove time the `@routine` decorator is reflected over the kernel socket and hashed — `manifest_hash`, pinned forever next to `code_hash`. From that moment the manifest is a promise. If the code ever touches a table the manifest didn't declare, that's not a warning. That's a governance anomaly.

---

## One prove pass

You wrote `routines/refund_order.ts`. You think it works. The kernel doesn't care what you think:

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

Declared versus executed, compared leaf by leaf. Zero denials, zero drift, one clean audit chain.

That's the shape of trust: small, described, and doing exactly what it said it would. What each of those numbers *means* — and which ones gate promotion — is the next two pages.

---

## Versions, or: no silent edits

Edit a routine's file directly, without a version bump, and the lockfile trips instantly — `exit 3`. Concurrent edits to the same routine file lock each other out — `exit 2`. Every real change becomes a new version with new hashes, and the registry remembers who created each version and who promoted it.

This sounds bureaucratic right up until a routine misbehaves in prod and you need to know *exactly* what ran. Then it sounds like salvation.

---

## The One Rule

**Name it, bound it, hash it.**

A routine is your repetition with a government job: small enough to inspect, described well enough to find, versioned tightly enough to trust.

---

**What's this `--env sim` business? Rehearse before you rely:** → [rehearsal.md](rehearsal.md)

**Exact command contracts — prove, ship, stats, rollback, sweep, retire:** → [reference/commands/routine.md](../reference/commands/routine.md)

**Why drafts can never touch prod:** → [understand/trust.md](../understand/trust.md)
