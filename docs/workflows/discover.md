# Discover

You don't memorize. You search. Your harness doesn't memorize either. It searches. The registry exists so neither of you has to carry 300 routine signatures in your head like some kind of organic man page.

## The move

```bash
$ capcli search "refund"
```

```
[dev:tier_1]  3 results

  cap://order_refund@7          routine    reviewed   "Refund cancelled order and archive"
  cap://stripe.refund_charge    api-verb   draft      "Issue partial or full Stripe refund"
  doc://refund-policy           doc        —          "Business rules for refund eligibility"
```

Three typed pointers. Trust rung visible. Descriptions under 60 tokens each. You didn't grep a codebase. You asked a word, got answers.

Every result is a **Universal Resource Pointer** (URP) — typed, addressable, runnable:

| Prefix | Points to | Example |
|---|---|---|
| `cap://` | Routines and API verbs | `cap://order_refund@7` |
| `db://` | Tables, views, constraints | `db://orders` |
| `doc://` | Markdown specs, playbooks | `doc://refund-policy` |
| `bind://` | Crons, webhooks, endpoints | `bind://nightly_sync` |
| `vault://` | Secret references | `vault://stripe_secret` |
| `snap://` | Recovery snapshots | `snap://snap_migration_004` |
| `ask://` | Pending human questions | `ask://ask_7f2c` |

The registry itself has a ceiling — max 300 routines, nagged at the soft cap of 200, because past that keyword search degrades into noise. All registry ceilings: [reference/limits.md](../reference/limits.md).

## The search cascade

Under the hood, search runs four stages — `exact → prefix → fuzzy → semantic`. Type `refund`, exact hits. Type `refnd`, fuzzy catches the typo. Type "money back", semantic finds the refund routine even though the word "money" appears nowhere in its name. You don't configure any of this. It just works.

## Finding gaps

Sometimes the interesting result is the one that *doesn't exist*.

```bash
$ capcli search gaps --since 7d
```

```
[dev:tier_1]  2 gaps detected

  query: "inventory sync"     searches: 8    invocations: 0    signal: missing capability
  query: "customer export"    searches: 5    invocations: 0    signal: missing capability
```

Eight searches for "inventory sync" in seven days. Zero invocations. Nothing exists to handle it. Build it — or tell your harness to. The registry noticed the hole before you did.

---

## The inspect envelope

```bash
$ capcli inspect cap://dispatch_order@4
```

```
[dev:tier_1]  cap://dispatch_order@4

  trust:       pinned
  limits:      8 ops · 15s · 500 result tokens

  manifest:    db.query → api.call(logistics.shipments.create) → db.execute
  budget:      can_invoke_now: true · session_ops_remaining: 492
               tightest_constraint: null
  composition: budget_inheritance: min
  stats:       214 runs · 99.1% success · p50 340ms · p95 890ms
```

One command. Zero roundtrips. The envelope answers everything:

| Section | Answers |
|---|---|
| **manifest** | What will it actually touch? |
| **budget** | Can I run it *right now*? |
| **composition** | What does it spawn, and [whose budget do children inherit](../concepts/budgets.md#the-min-law)? |
| **stats** | How reliable is it historically? |

Tokens, duration, storage, concurrency, live API quota, composition — all pre-flight. You know the cost before you spend it.

### The verdict: `can_invoke_now`

The whole point is one boolean. `true` → go ahead. `false` → don't; read `blocking_reasons`:

```
  budget_status:
    can_invoke_now:    false
    blocking_reasons:
      - "session_ops_remaining: 3 (needs 12)"
      - "tightest_constraint: ops"
```

Your harness reads this. It doesn't guess. It doesn't try anyway.

---

## Inspecting each type

Same command, every URP, different envelope.

**An API verb** — live quota rides along:

```bash
$ capcli inspect cap://stripe.refund_charge
```

```
  trust:       reviewed · active · write · idempotent
  method:      POST /v1/refunds

  quota:       capacity 60 · available 47 · earmarked 10 · refill 1.0/s
  budget:      can_invoke_now: true · session_fuel_remaining: 80400
```

How many tokens are left, whether earmarks are eating headroom — *before* you burn a call.

**A table:**

```bash
$ capcli inspect db://orders
```

```
  columns:  12    rows:  4,281    indexes:  3    views:  2
  access:   read: all levels · write: reviewed+ · drop: denied · alter: reviewed
```

Shape, access rules, recent traffic. No `PRAGMA table_info`. No grepping schema files.

**A binding:**

```bash
$ capcli inspect bind://nightly_sync
```

```
  type:        cron              schedule:   0 3 * * *
  capability:  cap://inventory_sync@3
  status:      active            catchup:    max 1 fire on restart
```

**A doc** — progressive disclosure: you get the outline, not the blob. Need one section? `capcli doc read doc://refund-policy --section 3 --max-tokens 100`.

**A pending ask:** `capcli inspect ask://ask_7f2c` — status, options, expiry. See [approvals.md](approvals.md).

## When inspect says no

The denial isn't a wall. It's a map. Your harness reads `blocking_reasons` and decides: wait for the session to reset, ask you for a new session, pick a lighter capability, or yield and retry later. Inspect doesn't just block. It says *why* and *what's tight*. And remember: search and inspect are both optional — if your harness already knows the exact pointer and the budget is obviously fine, it skips straight to invocation. Discovery is for "I don't know what's here."

## What your harness actually does

You say: "ship order 8842 via fedex". Your harness does:

1. `capcli search "dispatch"` → finds `cap://dispatch_order@4`
2. `capcli inspect cap://dispatch_order@4` → checks `can_invoke_now`
3. Sees `true` → `capcli run dispatch_order -p order_id=ORD-8842 -p carrier=fedex -m "..."`
4. Reads the exit code. Reads the output. Reports to you.

Four words from you. Three commands from the harness. One shipped order. (Exact syntax: [reference/cli/run.md](../reference/cli/run.md).)

---

**Found data? Work it** → [query-data.md](query-data.md) · **Found a gap? Fill it** → [routines.md](routines.md)
