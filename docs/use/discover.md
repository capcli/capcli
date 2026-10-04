# Discover

You don't memorize. You search.

Your harness doesn't memorize either. It searches. That's the whole philosophy. The registry exists so neither of you has to carry 300 routine signatures in your head like some kind of organic man page.

---

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

Three typed pointers. Descriptions under 60 tokens each. Trust rung visible. You didn't grep a codebase. You didn't read a README. You asked a word, got answers.

---

## What you're looking at

Every result is a **Universal Resource Pointer** (URP). Typed. Addressable. Runnable.

| Prefix | Points to | Example |
|---|---|---|
| `cap://` | Routines and API verbs | `cap://order_refund@7` |
| `db://` | Tables, views, constraints | `db://orders` |
| `doc://` | Markdown specs, playbooks | `doc://refund-policy` |
| `bind://` | Crons, webhooks, endpoints | `bind://nightly_sync` |
| `vault://` | Secret references | `vault://stripe_secret` |
| `snap://` | Recovery snapshots | `snap://snap_migration_004` |
| `ask://` | Pending human questions | `ask://ask_7f2c` |

You don't need to know all of these yet. You'll meet them as you need them.

---

## The search cascade

Under the hood, search runs four stages. You don't configure this. You don't think about it. It just works.

```
exact match → prefix match → fuzzy match → semantic ranking
```

Type `refund`, you get exact hits. Type `refnd`, fuzzy catches the typo. Type "money back", semantic finds the refund routine even though the word "money" appears nowhere in its name.

Your harness does this automatically. You type a vague English phrase. The harness translates it into search queries. You get results.

---

## When search isn't enough

You found something. Now you want to know: *can I actually run this right now?*

```bash
$ capcli inspect cap://order_refund@7
```

```
[dev:tier_1]  cap://order_refund@7

  trust:       reviewed
  runtime:     python (python3)
  params:      order_id: string, reason: string
  limits:      6 ops · 20s · 500 result tokens
  budget:      can_invoke_now: true
               session_ops_remaining: 487
               tightest_constraint: null
  manifest:    api.call(stripe.refund_charge) → db.execute → db.execute
  stats:       89 runs · 97.8% success · p50 410ms · p95 1100ms
```

One command. Zero roundtrips. You know:
- Whether you can run it *right now* (`can_invoke_now: true`)
- What it'll touch (the manifest)
- What it costs (ops, duration, tokens)
- How reliable it is (89 runs, 97.8% success)

Your harness reads this envelope and decides whether to proceed. You don't have to.

---

## You don't have to search

Here's the thing nobody tells you: search is optional.

If your harness already knows the exact pointer — `cap://dispatch_order@4` — it just runs it. No search. No inspect. Straight to invocation.

Search exists for *discovery*. For "I don't know what's here." For "what can I do with orders?" For "is there something that handles refunds?"

Once you know the signature, you skip discovery and go straight to execution.

---

## Finding gaps

Sometimes the interesting result is the one that *doesn't exist*.

```bash
$ capcli run search gaps --since 7d
```

```
[dev:tier_1]  2 gaps detected

  query: "inventory sync"     searches: 8    invocations: 0    signal: missing capability
  query: "customer export"    searches: 5    invocations: 0    signal: missing capability
```

Eight searches for "inventory sync" in seven days. Zero invocations. Nothing exists to handle it.

That's a signal. Either build it, or tell your harness to build it. The registry noticed the hole before you did.

---

## What your harness actually does

You say: "find me something that handles refunds"

Your harness does:

1. `capcli search "refund"` → gets three pointers
2. Picks the most relevant one
3. `capcli inspect cap://order_refund@7` → checks `can_invoke_now`
4. If true, proceeds to invocation
5. If false, reads `blocking_reasons` and tells you why

You didn't type any of that. You said one sentence. Your harness did the discovery dance.

---

## The ceiling

The registry holds max **300 routines**. Soft cap at 200 (doctor nags you past that).

Why? Because search degrades past a certain size. 300 routines with 60-token descriptions is still searchable. 3,000 routines is noise.

If you're hitting the ceiling, it's time to consolidate. That's a later problem. For now: search works, and it works fast.

---

## The one rule

**Search before you build.**

Before your harness scaffolds a new routine, before you write a new script, before you add another capability to the registry — search first. It might already exist. It might exist under a name you didn't expect.

```bash
$ capcli search "archive old orders"
```

Two seconds. Saves you an hour of duplicate work.

---

**Found something? Now understand it** → [inspect.md](inspect.md)

**Already know what you want? Run it** → [run.md](run.md)
