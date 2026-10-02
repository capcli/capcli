# Repetition

The first time you type a query, it's curiosity.

The second time, it's a habit forming.

The third time, it's a routine begging to exist — you just haven't filed the paperwork yet.

---

## The signal was there all along

Here's the convenient part: you don't have to remember what you keep doing. Capcli already does. Every bounded query, every API call, every denial — all of it sits in `_audit`, hash-chained and bored, waiting to be asked.

Ask it what you've been touching:

```bash
$ capcli sys audit query "SELECT capability, COUNT(*) AS hits FROM _audit GROUP BY capability ORDER BY hits DESC LIMIT 5"
```

```
[dev:tier_1]  ✓  16ms

  rows: 3
  capability                   hits
  ───────────────────────────  ────
  db://orders                  47
  cap://stripe.refund_charge   12
  db://customers               9
```

Forty-seven touches on `orders`. Twelve refund calls. You aren't exploring anymore — you're in a loop with extra steps.

That loop is the raw material.

---

## The other signal: what keeps *not* existing

Repetition has a twin: the thing you keep searching for and never find.

```bash
$ capcli run search gaps --since 7d
```

```
[dev:tier_1]  2 gaps detected

  query: "refund cancelled order"    searches: 9    invocations: 0    signal: missing capability
  query: "archive refunds"           searches: 4    invocations: 0    signal: missing capability
```

Nine searches for "refund cancelled order" in seven days. Zero invocations, because nothing exists to invoke.

The registry noticed the hole before you admitted it. Zero-result queries rank first in gap detection — the loudest silence in the system.

---

## The kernel notices too

You're not alone in the pattern-spotting business. The kernel mines the audit mirror in the background, and deterministic SQL views (`op_frequency`, `shared_subsequences`) surface the sequences you repeat most. Once enough telemetry accumulates, it starts proposing routines for the frequent ones.

But that's a convenience, not a gate. Direct drafting is available from day zero — you never need the kernel's permission to codify your own repetition.

---

## Turning "I keep doing this" into intent

Before you write any code, write the sentence. One line, plain language, describing what the repetition *accomplishes*:

> Refund a cancelled order through Stripe and archive it.

That sentence isn't a warm-up. It's load-bearing:

- It becomes the routine's **description** — required, minimum five words, because unsearchable code is dead code.
- It scopes the **manifest** — the tables and API verbs the sentence names are the ones the routine may touch. Nothing else.
- It survives into the registry, where next month your harness searches "refund" and finds it in one hop.

Get the sentence wrong and everything downstream inherits the wrongness. Get it right and the routine practically writes itself.

---

## When is repetition *enough* repetition?

There's no committee. The practical rule:

- **Once** — exploration. Fine. That's what dev is for.
- **Twice** — coincidence with suspicious posture.
- **Three times** — you now have a stable sequence, parameters you've already rehearsed, and real test data sitting in the audit trail. That's a routine.

And check the shelf before you build: search first. A near-duplicate of your idea may already exist — and if your draft is similar enough to something registered, the kernel will demand you justify the fork in `--reason` anyway.

---

## The One Rule

**The third time you type it, stop typing it.**

Name the repetition. Write its sentence. Go make it a routine.

---

**Ready to give it a name, a shape, and a hash?** → [routines.md](routines.md)

**Want to interrogate your history directly?** → [use/audit.md](../use/audit.md)

**The machine-facing version of this move:** → [agents/codification.md](../agents/codification.md)
