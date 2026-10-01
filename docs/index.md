# Capcli

**The governed execution layer between your AI agent and live production state.**

Your harness reasons. Capcli enforces what it's allowed to touch, how much, and records every attempt — allowed or denied.

---

## What can I do with this?

Run an agent against real databases, real APIs, real cron jobs — without praying it doesn't `DELETE FROM users` or double-bill Stripe in a loop.

Capcli is the physics. Not a suggestion. Not a prompt. A compiled Rust kernel that denies structurally.

---

## Start here

| You are… | Go to |
|---|---|
| Brand new, nothing installed | [Start →](start/index.md) |
| Installed, need to get something done | [Use →](use/index.md) |
| Building an agent integration | [Agents →](agents/index.md) |
| Need exact syntax or exit codes | [Reference →](reference/index.md) |
| Something broke | [Guides →](guides/index.md) |

---

## The 10-second version

```
YOUR AGENT (Claude, Hermes, whatever)
        │
        │  capcli run dispatch_order -p order_id=ORD-42
        ▼
┌─────────────────────────────┐
│      CAPCLI KERNEL          │
│  authorizer · budget · jail │
└─────────────┬───────────────┘
              ▼
     STATE CHANGED (or denied)
     AUDIT RECORDED (always)
```

Allowed or denied. Never silent. Never half-executed.

---

## The four laws

| Law | Breach result |
|---|---|
| Database floor (C authorizer) | `exit 2` — write killed |
| Network jail (bwrap + seccomp) | `exit 2` — socket trapped |
| Budget cage (min cascade) | `exit 6` or `exit 2` — halted |
| Audit spine (SHA-256 chain) | `exit 3` — boot refused |

---

## Not Capcli

- Not a prompt wrapper
- Not Docker (Docker isolates the machine; Capcli isolates business logic)
- Not the reasoning harness (your LLM reasons; Capcli governs execution)
- Not an ORM

---

**Install:** `curl -fsSL https://capcli.dev/install.sh | bash`

**First task:** [start/first-task.md](start/first-task.md)
