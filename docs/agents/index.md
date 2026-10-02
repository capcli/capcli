# Agents

You are the harness. This is your contract.

You reason. Capcli governs execution. The kernel enforces, dispatches, and audits. Capcli doesn't trust you — that's the feature that lets you operate on live state without a chaperone.

This is the machine-facing surface: exact commands, exact envelopes, exact exit codes. Precision over pedagogy. The human tour lives in [../start/index.md](../start/index.md).

---

## The fundamental path

Every governed action moves through three calls:

```
DISCOVER   →   INSPECT   →   INVOKE
search         inspect       run
pointers       verdict       gated effect
```

Search resolves typed pointers. Inspect returns a zero-roundtrip `can_invoke_now` verdict with the full cost envelope. Run executes under gates you never see — and never need to. Skip any step when you already know the signature: direct invocation is permitted, discovery is for "what's here?", not a toll booth.

---

## The eight contracts

| Page | What it pins down |
|---|---|
| [contract.md](contract.md) | The boundary: you / Capcli / kernel. Exit codes, envelopes, intent, sessions, principals. |
| [discovery.md](discovery.md) | Finding capabilities: `run search`, filters, `search gaps`, `api catalog`. |
| [inspection.md](inspection.md) | The pre-flight envelope: `can_invoke_now`, cost, quota, composition. |
| [invocation.md](invocation.md) | Executing: `run`, `sql --dry-run`, budget frames, `ctx.api.call`, exit 6. |
| [rehearsal.md](rehearsal.md) | Establishing what will happen before it happens. |
| [feedback.md](feedback.md) | Reading denials, yields, and traces as information — never as noise. |
| [codification.md](codification.md) | Turning repeated behavior into routines, including the mandatory `overview`. |
| [proving.md](proving.md) | Earning trust rungs with receipts, not vibes. |

---

## Cold start

The harness onboarding journey maps onto this section:

```
H0  contract      sys doctor --json              →  contract.md
H1  discovery     run search                     →  discovery.md
H2  rehearsal     run --dry-run                  →  rehearsal.md
H3  dual probe    sql + api catalog              →  discovery.md
H4  hybrid        routine prove                  →  rehearsal.md
H5  feedback      sys audit trace --explain      →  feedback.md
H6  codification  author the overview routine    →  codification.md
H7  proving       routine prove --env sim        →  proving.md
```

Run them in order. By H7 you hold a proven routine and a receipt.

---

**Start at the boundary** → [contract.md](contract.md)

**Need the exact grammar instead?** → [../reference/cli.md](../reference/cli.md)
