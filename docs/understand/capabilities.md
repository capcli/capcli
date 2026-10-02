# Capabilities

Everything runnable in Capcli is a **capability**. Local script, Stripe endpoint, your cleanup job — same interface, same law.

That's not an abstraction for elegance. It's an abstraction for *safety*: one door, one bouncer, no side doors.

---

## One prefix to rule them all

```bash
$ capcli search "order"
```

```text
[dev:tier_1]  3 results

  cap://dispatch_order@4     routine    pinned    "Dispatch paid order to carrier"
  cap://order_refund@2       routine    reviewed  "Refund and archive cancelled order"
  db://orders                table      —         "Core order state"
```

Notice: the Stripe verb `cap://stripe.refund_charge` isn't `api://something`. It's `cap://`. To the kernel, anything that can be discovered, inspected, and invoked is a capability — whether it executes TypeScript in a sandbox or HTTP against a vendor.

One surface means one gate. No "well, *external* calls don't need intent" loophole. Everything carries a trust rung. Everything fits a budget. Everything lands in the audit spine.

---

## The three verbs of the common surface

Every capability, regardless of kind, supports the same three moves:

```
DISCOVER → INSPECT → INVOKE
```

**Discover** — `capcli search "<intent>"` — typed pointers, ranked, ≤60-token descriptions.

**Inspect** — `capcli inspect <ptr>` — the pre-flight envelope:

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

Cost, blast radius, reliability, and a single boolean go/no-go verdict — `can_invoke_now` — computed against your *live* session budget. One roundtrip. Zero guessing.

**Invoke** — `capcli run <name> -p k=v -m "why"` — the gates fire, the physics decides.

---

## The kinds, briefly

| Kind | Where it lives | Example |
|---|---|---|
| **Routine** | `routines/*.ts` / `*.py`, versioned, sandboxed | `cap://dispatch_order@4` |
| **API verb** | `apis/<provider>.yaml`, synced from OpenAPI | `cap://stripe.refund_charge` |
| **Table / view** | compiled from `schema.yaml` | `db://orders` |
| **Doc** | `docs/` inside the workspace | `doc://refund-policy` |
| **Binding** | cron / webhook / endpoint | `bind://nightly_sync` |

Different runtimes. Identical contract. That's the trick that lets your harness treat "call Stripe" and "run local script" with the same two brain cells.

---

## Why discovery beats memorization

Your agent's context window is expensive and leaky. A 5MB Swagger spec in a prompt is how you end up with an agent that "knows" 4,000 endpoints and understands none.

Capcli flips it: capabilities sit **dormant** in the registry until searched. Zero context cost until needed. Then a 60-token description, an inspect envelope, and nothing else. The registry ceiling (300 routines) isn't a limit — it's the size at which search still *works*.

And when search finds nothing? That's a signal too:

```bash
$ capcli run search gaps --since 7d
```

```text
[dev:tier_1]  2 gaps detected

  query: "inventory sync"     searches: 8    invocations: 0    signal: missing capability
  query: "customer export"    searches: 5    invocations: 0    signal: missing capability
```

Eight searches, zero invocations — the hole announced itself.

---

## The contract your harness follows

Your harness never "just runs" a capability. It executes the loop:

1. `capcli search "intent"` → resolve a pointer
2. `capcli inspect <pointer>` → read `can_invoke_now`
3. `true` → `capcli run <name> -p ... -m "intent"`; `false` → read the blockers and *adapt*

If that looks like a big ceremony for one call — it's three cheap reads versus one unbounded side effect. Your insurance company calls that a bargain.

---

**What an invocation leaves behind** → [effects.md](effects.md)
