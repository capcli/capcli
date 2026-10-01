# What is Capcli?

Your AI agent is smart. It's also a toddler with root access.

You *want* it to query your orders table, call Stripe, update inventory. You *don't* want it to `DELETE FROM users` because it misread a prompt, or double-charge 4,000 customers in a `while(true)` loop because it got confused about idempotency.

Capcli is the physics that makes the bad stuff structurally impossible. Not "please don't." Not "try to be careful." Physically cannot.

---

## The one sentence

**The harness reasons. Capcli governs execution.**

That's it. That's the whole mental model.

Your LLM (Claude, Hermes, whatever) does the thinking. Capcli is the compiled Rust kernel that decides what that thinking is *allowed to touch*, *how much*, and *records every attempt* — allowed or denied.

---

## The analogy that actually works

Think of a bank teller.

The teller (your agent) knows what the customer wants. Maybe they're brilliant. Maybe they're having a bad day. Doesn't matter.

The vault has a lock. The withdrawal has a limit. Every transaction hits the ledger. The teller doesn't get to say "I'll skip the ledger today, I'm feeling creative."

Capcli is the vault, the limit, and the ledger. Compiled into machine code. Not a suggestion. Not a prompt. Physics.

---

## What Capcli is NOT

| It's not… | Because… |
|---|---|
| A prompt wrapper | Prompts drift. `sqlite3_set_authorizer` is C code. |
| Docker | Docker isolates the machine. Capcli isolates business logic. |
| An ORM | Raw SQL crosses the authorizer directly. No query builders. |
| The reasoning engine | Your LLM reasons. Capcli enforces. Never the reverse. |
| A suggestion box | Denials are structural. `exit 2` means the write never happened. |

---

## The four laws (the short version)

1. **Database floor** — unbounded writes die at the C authorizer. `exit 2`.
2. **Network jail** — raw sockets get trapped at the syscall level. `exit 2`.
3. **Budget cage** — op #51 on a 50-op run halts. No partial execution.
4. **Audit spine** — broken hash chain? Kernel refuses to boot. `exit 3`.

You'll meet these properly later. For now: they exist, they're non-negotiable, and they're why you can close your laptop while your agent works.

---

## Why not just prompt it to be careful?

You can. People do. Then they write a post-mortem at 2am titled "Regarding the Stripe Incident."

Prompts are probabilistic. Physics are not.

---

## Where to go from here

- **Show me it working** → [see-it.md](see-it.md)
- **I want to install it** → [install.md](install.md)
- **I want to understand the pieces** → [what-just-happened.md](what-just-happened.md) (after your first task)
