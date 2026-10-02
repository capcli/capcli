# Sessions

You've been using Capcli for an hour and haven't needed the word "session."

That's on purpose.

Sessions are not part of the first-time experience. You ran a query, you invoked a routine, you hit a denial — no session required. Capcli quietly scoped that work, spent from an anonymous budget, and wrote all of it to the ledger. You didn't ask, so it didn't make you.

This page exists for the moment you *do* need to ask. That moment usually sounds like one of these:

- "This job is going to outlive one command. How do I keep it scoped?"
- "Whose budget is this actually burning?"
- "The task yielded overnight — where did it go?"

---

## The human sentence

**A session is Capcli's temporary scope for a piece of governed work.**

"Piece of governed work" is doing the lifting. A session is not a login and not a conversation. It's a scope: one engagement, one pool of budget, one line in the ledger that ties together everything that happened inside it.

Here's where it sits in the identity chain:

```
principal   →   agent   →   session   →   op
user:alice      agt_7f3k     ses_a9       op_9f2c
(human or       (registered  (temporary   (one leaf in
 root holder)    harness)     scope)       the causal DAG)
```

A principal holds authority. An agent is a registered harness instance acting for one. A session is the scope that agent works in for one engagement. Ops are the leaves that scope produces. Every audit event carries the whole chain.

---

## The token that binds it

When the kernel opens a session, it mints a capability token — an HMAC session handle stored in the `_sessions` system table. That token binds two things at once:

- **The principal** — whose authority the work runs under.
- **The frame** — the budget scope the work spends from.

You pass it with `--session <token>`, or you let `CAPCLI_SESSION` (or the workspace's active context) carry it across turns so a long engagement survives many CLI invocations. Two properties worth knowing:

- **Kernel-issued only.** Tokens and ids are minted by the kernel. Self-declared identities are denied. You don't get to invent yourself.
- **It rides everything.** The session id stamps every budget frame, every audit event, every claim. Nothing inside the scope escapes the scope.

Child agents can fork a session and inherit a scoped parent token — subtasks draw from the family budget instead of minting fresh spending power.

---

## The budget you're spending from

A session isn't just identity — it's the accounting unit. Every dimension of the budget cage has a session-level pool: ops, duration, fuel, wire bytes, rows, rate.

You've already seen one of these numbers without knowing its name:

```bash
$ capcli inspect cap://dispatch_order@4
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

`session_ops_remaining: 492` — the ops left in the pool this session is drawing down. It's in `inspect` because the kernel won't let you buy what you can't afford: the `can_invoke_now` verdict is computed against it.

### Splitting is not escaping

Frame limits cascade by `min()`: a child routine gets the tightest of its declared need, the governance ceiling, the parent's remaining budget, and the session ceiling. Split a 100-op routine into ten 10-op sub-routines and you still hit the session ops ceiling, because session-level counters never reset through composition.

The cage tightens. It never widens.

---

## Yield: when the scope parks itself

Say a background routine burns through a provider's daily quota mid-run. The session doesn't crash, and it doesn't leak:

```text
[prod:tier_1]  ✗  exit 6

  YIELD  policy.api.quota_exhausted
         routine broadcast_newsletter@2 (frame_018)
         provider: threads
         verb:     threads.create_media_post

  state_modified:  false
  layer:           quota
  tokens_left:     0 / 50 (24h window)
  reset_at:        18:00:00 UTC (in 4h 12m)
  suspended_frame: task_99a8b1
  remedy:          task safely yielded; daemon will auto-resume at reset_at
```

That's `exit 6`. The frame is marked `yielded`, serialized into `_suspended_tasks` with its place in the DAG, and the daemon watches the refill epoch. When the window reopens, the work resumes on its own. The session was the thing patient enough to wait — and when you come back, it's still scoping the exact same piece of governed work.

---

## Where the exact semantics live

This page is the human version. The machine version — token validation, `--session` and `--by` checked against the active registry, fork semantics — is a contract, and it's written like one: [../agents/contract.md](../agents/contract.md).

If you're an agent (or you're wiring one up), read that, not this.

---

## The One Rule

**A session is scope, not state.** The work is temporary; the record of the work is permanent.

---

**The full budget cascade, dimension by dimension** → [../understand/budgets.md](../understand/budgets.md)

**Who the identities are and what they're allowed to hold** → [../understand/identity.md](../understand/identity.md)

**What a session's ops become once they've happened** → [provenance.md](provenance.md)
