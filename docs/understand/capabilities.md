# Capabilities

An agent that has memorized 300 function signatures isn't a colleague. It's a hallucination generator with good posture.

Capcli's answer is a single **capability surface**: everything callable — routines, API verbs, tables and views — lives in one registry, answers to one shape, and is used through one rhythm.

---

## 1. Everything Callable Is a Capability

Three kinds of things, one surface:

* **Routines** — versioned, sandboxed procedures: `cap://dispatch_order@4`
* **API verbs** — activated slices of an imported provider spec: `cap://stripe.refund_charge`
* **Tables and views** — the declared data surface: `db://orders`

Different jobs, identical governance. Every capability record answers the same three questions:

| Question | Fields |
|---|---|
| Who am I? | kind, name, version |
| Where am I allowed? | trust rung, environment |
| What do I cost? | cost envelope — tokens, writes, duration, quota |

That uniformity is the point. A `db://` view and a pinned routine differ in *what* they can do, never in *how* they're governed: same trust gates, same budget cages, same audit events.

---

## 2. Pointers, Not Paths

`cap://dispatch_order@4` — a name and a version. The version is not decoration:

* Every version is hash-pinned: `code_hash` and `manifest_hash` are permanently linked. Edit the code silently and you've changed its identity — so silent edits are banned; a change forces a new version.
* History is bounded and deep: 25 versions kept, rollback depth 5. Rewinding the pointer is one command, and the superseded version stays on record.

Pointers are cheap to carry and expensive to fake. That's why everything in the workspace is one — including the non-callable stuff you'll meet later (`doc://`, `snap://`, `bind://`, `ask://`). One addressing scheme for the whole World.

---

## 3. Trust Rides in the Search Results

You never greet a capability blind. The registry tells you its rung before you touch it:

```bash
$ capcli search "refund"
```

```text
[dev:tier_1]  3 results

  cap://order_refund@7          routine    reviewed   "Refund cancelled order and archive"
  cap://stripe.refund_charge    api-verb   draft      "Issue partial or full Stripe refund"
  doc://refund-policy           doc        —          "Business rules for refund eligibility"
```

The trust column is the one that saves your evening. `reviewed` has survived simulation; `draft` has a ceiling of 10 rows and no access to secrets. You see the blast radius before you see the code — and API verbs carry states of their own (`dormant` → `active` → `deprecated` → `retired`), so an imported-but-unproven verb is discoverable but uncallable.

How rungs get earned is its own story: [trust.md](trust.md).

---

## 4. The Rhythm: Discover → Inspect → Invoke

Why do these three verbs exist as the universal move, for humans and harnesses alike?

**Discover**, because nobody memorizes. Search cascades from exact match through prefix and fuzzy to semantic ranking, and returns pointers with short descriptions — under 60 tokens each, never raw blobs. Type `refund`, get pointers. Type `refnd`, fuzzy forgives you.

**Inspect**, because invoking blind costs state, quota, and fuel:

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

One command, zero roundtrips: what it touches (manifest), what it costs (limits), whether you can afford it *right now* (`can_invoke_now`), and how often it has behaved (stats).

**Invoke**, because it's the only door. Params in, gated effect out, leaf events recorded. No side channel exists — and that's what makes the record complete.

And here's the part nobody tells you: the rhythm is optional. Direct invocation is permitted whenever the signature is known. Search and inspect fire on cache miss or ambiguity — progressive disclosure, not ceremony. Your harness runs the loop when it's uncertain and skips it when it isn't.

---

## 5. One Surface Means One Physics

Because every capability passes the same gates, composition stays boring — in the best sense:

* Calling a routine from another agent is still a gated call: cross-agent callees must hold `reviewed` or higher. Drafts can't be dependencies.
* Hitting a table from raw SQL bypasses search but not the kernel — the same authorizer and ledger cover inline db ops.
* The registry has a ceiling (300 routines hard cap) because search degrades into noise past it. Past the cap, the answer is consolidation and retirement, not accumulation.

When your harness writes its next routine, it declares what it will call, the kernel fingerprints what it actually called, and any undeclared leaf becomes a governance anomaly. The surface stays honest even as it grows.

---

## The One Rule

**If it's callable, it's a pointer with a rung and a receipt.**

Name, version, trust, environment, cost — and a hash-chained record of every invocation. That's a capability. Everything else is detail.

---

**What an invocation actually emits** → [effects.md](effects.md)

**How trust rungs are earned and revoked** → [trust.md](trust.md)

**The machine-facing version of this contract** → [agents/invocation.md](../agents/invocation.md)
