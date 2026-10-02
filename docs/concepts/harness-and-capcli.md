# The Harness and Capcli

This page exists to kill one misconception before it costs you something.

**Capcli is not the harness.**

You watch an agent query a database through Capcli, and your brain files it under "AI tool." Understandable. Wrong. The thing doing the *thinking* in that demo was not Capcli. Capcli was the thing deciding how much of the world the thinking was allowed to touch — and writing down every attempt, allowed or denied.

There are two machines in the room, plus a ledger:

| Role | Who | Nature |
|---|---|---|
| **The harness** | Claude Code, Hermes, DeepSeek, agent swarms | Cognition. Reasoning. Probabilistic. |
| **Capcli** | The governed execution layer | Deterministic Rust/C physics. |
| **The kernel** | Capcli's core: enforcement, dispatch, audit | Mechanical. No moods. No mercy. |

The harness is brilliant and unreliable. The kernel is boring and incorruptible. That's not an insult to either machine — that's the architecture.

---

## The boundary, drawn on purpose

```
   PROBABILISTIC                      DETERMINISTIC
   reasons · guesses · drifts          compiles · enforces · records

┌────────────────────┐     bash     ┌─────────────────────────────┐
│      HARNESS       │  ─────────▶  │        CAPCLI KERNEL        │
│                    │   subshell   │                             │
│  Claude Code       │              │  C authorizer · AST traps   │
│  Hermes            │              │  seccomp-bpf wire jail      │
│  DeepSeek          │              │  budget frames · min()      │
│  your swarm        │              │  append-only audit DAG      │
└────────────────────┘              └──────────────┬──────────────┘
                                                   │
                                                   ▼
                                        SQLite · Stripe · S3
```

The harness reaches Capcli the way any process reaches any binary: an open bash subshell running `capcli <noun> <verb>`. No privileged channel. No mind-meld. The kernel treats every caller uniformly — PID, principal, agent ID, session. Your favorite LLM gets exactly the cage a shell script gets.

---

## Watch the boundary work

One command, three machines doing three jobs:

```bash
$ capcli sql "DELETE FROM orders"
```

```text
[dev:tier_1]  ✗  exit 2

  FAIL  policy.query.update_delete.require_where
        DELETE FROM orders
        ^^^^^^^^^^^^^^^^^^
        Missing WHERE clause. Unbounded delete denied.

  state_modified: false
  remedy: add WHERE + LIMIT, or use chunked loop via ctx.db.execute
```

Decode it as verbs:

- **Proposed.** The harness emitted a table nuke. Maybe it misread a prompt. Maybe it was "optimizing." Doesn't matter — the kernel doesn't grade intentions.
- **Disposed.** The C authorizer killed the statement at prepare-time, before SQLite allocated a byte. Zero rows touched. Not a warning. A wall.
- **Recorded.** The denial itself became an audit event — hash-chained, `effect: none`, `state_modified: false`.

**The harness proposes. The kernel disposes. Reality records.**

Memorize that sentence and half of Capcli's architecture arrives for free.

---

## Why the separation matters

### Prompts drift. Compiled authorizers don't.

You can ask an agent to "be careful with the orders table," and it will be careful — at a sampling rate. Prompt instructions are weather. `sqlite3_set_authorizer` is climate.

When the harness has a bad day, hallucinates a refactor, or gets talked into a clever `WHERE 1=1`, the kernel doesn't re-read your instructions. It doesn't have any. It has compiled rules, a lockfile hash, and an opinion-free refusal. The failure mode of a drifted prompt is a weird answer. The failure mode of a drifted authorizer is a recompile you'd notice in CI.

### Swap the harness, keep the governance.

Claude Code this quarter, Hermes next quarter, a DeepSeek swarm the quarter after. The kernel doesn't care — it can't tell them apart, and that's a feature. Governance doesn't move when your model does, because governance never lived in the model. It lives in the compiled layer between the model and reality.

Flip the framing: if Capcli *were* the harness, changing your agent stack would mean re-engineering your safety story every time. Since it isn't, it means the cages stay exactly where they were bolted.

---

## What the kernel is, mechanically

Strip the poetry and the kernel does three jobs:

1. **Enforcement.** The C authorizer, AST blast guards, seccomp jails, budget cages. Default posture across every capability vector: *deny*.
2. **Dispatch.** Routines, frames, budgets, claims. Work gets routed, scoped, and metered before it runs.
3. **Audit.** Every verb — allowed or denied — becomes a leaf event in the append-only causal DAG.

And one job it refuses: **there is no LLM in the kernel.** Zero AI inference lives in core. The kernel never decides what's a *good idea*; it only decides what's an *allowed operation*. Good ideas are the harness's department, which is why the harness keeps getting to propose.

---

## The One Rule

**Cognition is swappable. Governance is compiled.**

The harness is a tenant. The kernel is the building. Reality keeps the books.

---

**The machine-facing version of this boundary** → [../agents/contract.md](../agents/contract.md)

**How the kernel's rules get compiled and locked** → [compiler.md](compiler.md)

**The gentler introduction, if this was a lot** → [../start/what-is-capcli.md](../start/what-is-capcli.md)
