# Harness and Capcli

The most common misconception about Capcli, stated up front so we can kill it together:

> **Capcli is not the harness.**

Capcli contains zero AI. No inference, no model weights, no "understanding." It is a compiled Rust/C kernel that gates, meters, and records. It has never had a thought, and it never will — that's not a limitation, that's the *point*.

---

## The split

```
HARNESS  = cognition / reasoning
           (Claude Code, Hermes, DeepSeek, swarms…)
           You: plan, decide, explain, be confidently wrong.

CAPCLI   = governed execution
           (the kernel: gates, budgets, sandbox, audit)
           It: decide what's allowed, how much, and record it.

KERNEL   = mechanical enforcement
           (C authorizer, seccomp-bpf, min() cascade, SHA-256 DAG)
           It: enforce. Only enforce. Forever enforce.
```

**The harness proposes. The kernel disposes. Reality records.**

## Why the split must never blur

Your harness is *probabilistic*. Brilliant, fast, occasionally catastrophic — a toddler with root access who can also write sonnets. Every capability of an LLM that makes it useful is the same capability that makes it dangerous: it will confidently do the wrong thing at scale.

Capcli is the deterministic floor under that:

| The harness… | Capcli… |
|---|---|
| Reasons about which query to run | Parses the AST, checks the blast radius |
| Decides "I should refund this order" | Gates: is the caller's trust rung sufficient? |
| Forgets to check the rate limit | Token buckets meter before packets leave |
| Would prefer not to log | Emits the event *before* it can prefer anything |

Note the asymmetry of temptation: the harness drifts; the kernel compiles. Prompts degrade over versions, contexts, and moods. `sqlite3_set_authorizer` does not have moods.

## What "governed execution" buys the harness

Counter-intuitively, the split makes the harness *more* capable, not less:

- **It can be trusted with more.** Blast radius is bounded, so the leash can be longer.
- **It doesn't need paranoia.** No defensive try/catch walls, no rate-limit vigilance, no audit chores — the floor handles all three, so the harness spends its context on the actual problem.
- **It gets honest feedback.** Denials with `remedy:` fields teach faster than stack traces.

The harness gets to be exactly as smart as it is, and no dumber than physics allows.

## The corollary you should tattoo on your tooling

> If you're prompting your way to safety, you don't have safety. You have hope with a system prompt.

Governance that depends on the model's mood isn't governance. The harness-and-kernel split exists so that "the agent was having a bad day" is a *non-event* in your incident review.

---

**Next** → [sessions.md](sessions.md) — the temporary scope where governed work happens.
