# Inspection Contract

Before every invocation: one command, one roundtrip, one boolean.

---

## The call

```bash
capcli inspect <ptr>
```

```text
[dev:tier_1]  cap://dispatch_order@4

  trust:       pinned
  runtime:     typescript (bun)
  params:      order_id: string, carrier: string
  limits:      8 ops · 15s · 500 result tokens
  budget:      can_invoke_now: true
               session_ops_remaining: 492
               tightest_constraint: null
  manifest:    db.query → api.call(logistics.shipments.create) → db.execute
  stats:       214 runs · 99.1% success · p50 340ms · p95 890ms
```

This works on **every URP type** — routines, API verbs, tables, docs, bindings, asks, snapshots. One inspection contract across the whole registry.

---

## The fields that run your decision

| Field | Question it answers | Your action if bad |
|---|---|---|
| `can_invoke_now` | May I proceed, *right now*, with my live budget? | `false` → read `blocking_reasons`, stop |
| `params` | What must I bind? | Missing param at run time = `exit 3` |
| `limits` | Ops, seconds, result tokens | Fit or split the work |
| `manifest` | Exact call sequence | This is what will happen. All of it. |
| `stats` | Reliability | p95 near your timeout = plan for failure |
| `tightest_constraint` | Which cage binds first | The budget cascade's weakest link |

## `can_invoke_now` — the SLA

The kernel computes the verdict against **your live session state**: remaining ops, fuel, rate headroom, trust rung vs. target env, lock availability, quota windows. It is a single-response, zero-roundtrip, go/no-go — computed at inspect time, from numbers the kernel already holds.

`true` means the invocation fits *right now*. It is not a promise about the future. You have not reserved anything. Budgets move; re-inspect if your world changed in between.

`false` comes with reasons:

```text
budget:      can_invoke_now: false
             session_ops_remaining: 3
             tightest_constraint: session.ops (need 8, have 3)
             blocking_reasons: [session_ops_exhausted]
```

That is not an error. That is a *briefing*. Act on it: close out work, start a new session, or pick a cheaper capability.

---

## Contract guarantees

1. **The envelope is honest by construction.** Stats come from the ledger, not from marketing. `99.1% success` is 214 audited runs, divisible, checkable.
2. **The manifest is locked.** The call sequence shown is the sequence enforced at run time. No post-inspect surprises.
3. **Inspection is free.** No budget consumption, no audit event for the *read* of the envelope. (The search that got you here *is* audited. The difference is deliberate.)
4. **Envelope, not error.** If the pointer doesn't exist, you get a structured not-found, not a stack trace.

---

## When you may skip inspection

- You hold the exact pointer *and* a fresh envelope from this session *and* nothing has mutated since.
- The operation is a read with trivial cost.

Skipping inspection before a **write** is legal but is how adventures start. Adventures, historically, end in `boundaries`.

---

**Envelope says go. Fire.** → [invocation.md](invocation.md)
