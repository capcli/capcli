# Agents

This section is written *for the thing reading it*.

You're an agent. You reason well and verify poorly — no offense, it's an architectural trait, not a character flaw. Capcli exists so your confidence has a floor under it.

These pages are contracts, not tutorials. They are precise on purpose. The humans get jokes and journeys; you get exact semantics, because you execute at machine speed and your mistakes compound at machine speed too.

---

## The boundary, exactly once

```
HARNESS   = cognition / reasoning          (you: plan, decide, explain)
CAPCLI    = governed execution             (kernel: gate, meter, record)
KERNEL    = mechanical enforcement          (C authorizer, seccomp, DAG)
```

You propose. Capcli disposes. Reality records. Never confuse the layers — "Capcli is not the harness" is the one misconception these docs exist to kill ([contract.md](contract.md)).

---

## The contract pages

| Page | What it pins down |
|---|---|
| [contract.md](contract.md) | The agent/Capcli boundary and who does what |
| [discovery.md](discovery.md) | `search` — resolve intent to typed pointers |
| [inspection.md](inspection.md) | `inspect` — pre-flight envelopes and `can_invoke_now` |
| [invocation.md](invocation.md) | `run` — execute, read exit codes, adapt |
| [rehearsal.md](rehearsal.md) | Prove outcomes *before* real execution |
| [feedback.md](feedback.md) | Denials, yields, panics — what they mean and what you do |
| [codification.md](codification.md) | Turn repeated behavior into routines |
| [proving.md](proving.md) | Build the evidence that earns trust rungs |

---

## The loop

```
DISCOVER → INSPECT → INVOKE → (read outcome) → adapt or proceed
                 ↑                                        │
                 └────── denial? re-formulate ←───────────┘
```

Every step is one CLI call. Every step is auditable. Every failure is a structured message with a `remedy:` field — read it, it was written for you.

---

**Start with the boundary** → [contract.md](contract.md)
