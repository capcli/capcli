# Sessions

A session is Capcli's temporary scope for one piece of governed work.

That's the human version. The exact kernel-issued semantics live with the spec ([../agents/invocation.md](../agents/invocation.md) for the envelope view); this page is the intuition, because sessions are deliberately *not* part of the first-time experience — you work for weeks without thinking about them, and that's correct.

---

## What a session actually is

When your harness starts working, the kernel issues a session: an identity-scoped, budgeted execution envelope. Everything the harness does inside it — every search, every `sql`, every `run` — shares:

- **One op budget.** Session ceiling of 500 ops, with 200 reserved for exploratory ad-hoc work. The envelope you saw at inspect time (`session_ops_remaining: 492`) is this number, live.
- **One identity context.** Agent (`agt_7f3k`) + principal (`user:alice`) + trust rung, stamped on every event the session emits.
- **One goal.** Session-level intent, to which every mutation's `-m` hangs causally. That's how `sys audit trace` walks from any leaf op back to "what were we even doing?"

## When you notice sessions at all

Almost exclusively at the edges:

| Moment | What you see |
|---|---|
| The budget edge | `session_ops_remaining: 3` in an inspect envelope; `can_invoke_now: false` with `blocking_reasons: [session_ops_exhausted]` |
| The wall-clock edge | Sessions consolidate at a 30-minute cap — labor is budgeted too, including review labor |
| The accountability edge | An audit event's `session` field naming exactly which scope of work did the thing |

A session isn't a workflow engine, isn't a login, and isn't something you "manage." It's a unit of *accountability with a budget attached* — when the work is done (or the ops run out), the scope closes, and the ledger keeps the story.

## The min() cascade, in one picture

Sessions sit at the top of the budget cascade:

```
session (500 ops)
    └── routine frame (declared, e.g. 8)
            └── transaction (10 statements max)
                    └── single op (1)
```

Every level cascades downward via `min()` — the *tightest* cage always governs. A session with 488 ops left can still deny an 8-op routine if the routine's own frame is exhausted. The denial names which frame said no, at which level, with what headroom. You never have to guess which wall you hit; the wall introduces itself.

## Sessions vs environments vs worlds

Quick disambiguation, because these three get conflated over coffee:

| Term | Scope | Lifetime |
|---|---|---|
| **World / env** | *Where* state lives (`envs/dev/`) | Long-lived |
| **Session** | *One piece of work* in a world | Minutes-to-hours |
| **Routine run** | *One invocation* inside a session | Seconds |

A world hosts many sessions. A session hosts many runs. The DAG stitches all of it into one story per session goal.

---

**Next** → [provenance.md](provenance.md) — how the story gets stitched.
