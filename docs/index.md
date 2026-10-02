# Capcli

**The compiled execution firewall between probabilistic AI agents and live enterprise state.**

Your LLM reasons. The kernel enforces what it can touch, how much it can burn, and cryptographically signs every attempt — allowed or denied. Nothing reaches your database, your APIs, or your audit trail without passing through compiled physics first.

```bash
curl -fsSL https://capcli.dev/install.sh | bash
```

---

## What are you trying to accomplish?

| Your Goal | Where to go |
|---|---|
| **Zero setup. See it work in 60 seconds.** | [Start Here →](start/index.md) |
| **Run a bounded query or safe mutation right now.** | [First Task →](start/first-task.md) |
| **Make safe API calls without leaking keys or burning quotas.** | [Call APIs →](workflows/apis.md) |
| **Handle incoming webhooks, crons, or export an MCP server.** | [Triggers →](workflows/triggers.md) |
| **Pause execution and ask a human a structured question.** | [Ask a Human →](workflows/approvals.md) |
| **Understand the token-bucket brokerage & multi-day limits.** | [Budgets →](concepts/budgets.md) |
| **Open the local web cockpit.** | [Cockpit →](../cans/interface.md) |
| **Decode an exit code or a denial.** | [Exit Codes →](reference/exit-codes.md) |
| **Check a hard ceiling (ops, rows, LOC, fuel, drift).** | [Hard Limits →](reference/limits.md) |
| **Look up exact CLI command contracts (10 surface nouns).** | [Command Reference →](reference/cli/index.md) |

---

## The 10-Second Mental Model

```
                     PROBABILISTIC REASONING
           (Claude Code / Hermes / DeepSeek / Swarms)
                                │
                                │ raw terminal command / subshell
                                ▼
       ┌─────────────────────────────────────────────────┐
       │              CAPCLI KERNEL (Rust)               │
       │                                                 │
       │   THE DATABASE FLOOR   │   THE WIRE FLOOR       │
       │   sqlite3 C Authorizer │   Syscall 42 Trapping  │
       │   AST Blast Guards     │   Token-Bucket Egress  │
       │                                                 │
       │   THE BUDGET CAGE      │   THE MEMORY SPINE     │
       │   Cascading min() Ops  │   Append-Only DAG      │
       │   Yield on Quota (6)   │   Tamper-Evident SHA   │
       └────────────────────────┬────────────────────────┘
                                │
                                ▼
                      DETERMINISTIC REALITY
          (SQLite WAL · Stripe · Social APIs · S3 WORM)
```

**The harness proposes. The kernel disposes. Reality records.**

---

## The Dual Floor Principle

An autonomous agent doesn't just destroy your company by dropping a table. It also destroys you by double-charging 4,000 customers on Stripe in an infinite `while(true)` loop, or leaking production credentials into a public terminal log.

### Floor 1: The Database Floor
* **Native C Authorizer:** Intercepts statements inside [`sqlite3_set_authorizer`](concepts/authorizer.md) at prepare-time.
* **AST Semantic Traps:** Missing `WHERE`, missing `LIMIT`, or tautology bypasses (`WHERE 1=1`) die before SQLite allocates a single byte of RAM.
* **Guaranteed Clean State:** Non-zero exits mathematically guarantee `state_modified: false`.

### Floor 2: The Wire Floor
* **Processor-Level Trapping:** [`seccomp-bpf`](concepts/sandboxing.md) intercepts raw network calls (`connect`, Syscall 42). A guest script trying to run `requests.post()` is killed by the CPU ([`exit 2`](reference/exit-codes.md#exit-2)).
* **Quarantined Catalogs:** Egress routes strictly through imported OpenAPI catalog verbs. The agent never reads raw 5MB Swagger files.
* **Metered Egress:** Client-side token buckets meter requests before packets leave your machine. Vault secrets are decrypted at the wire proxy, injected, and zeroized immediately post-dispatch. The agent never sees the key.

Two cages close the perimeter: the [budget cage](concepts/budgets.md#the-min-law) and the [memory spine](concepts/memory-spine.md).

---

## The 4 Physical Laws

No prompt engineering. No *"please be careful"*. These are compiled into native machine code:

| Law | Enforcement Mechanism | What Happens on Breach |
| :--- | :--- | :--- |
| **1. Database Floor** | Native C `sqlite3_set_authorizer` + AST | [Killed at prepare-time](reference/exit-codes.md#exit-2) |
| **2. Wire Floor** | `bwrap` namespaces + `seccomp-bpf` + quotas | [Trapped at Syscall 42](reference/exit-codes.md#exit-2) · [yield on dry quota](reference/exit-codes.md#exit-6) |
| **3. Budget Cage** | Downward cascading `min()` frames | [Halted at frame boundary](reference/exit-codes.md#exit-2) |
| **4. Memory Spine** | Append-only SHA-256 causal DAG | [Kernel refuses to boot](reference/exit-codes.md#exit-3) · [unaudited writes panic](reference/exit-codes.md#exit-5) |

The full exit-code contract — definitions, denial anatomy, remedy patterns — lives in [reference/exit-codes.md](reference/exit-codes.md).

---

## What Capcli is NOT

* **Not a prompt wrapper:** Prompts drift. C authorizers and `seccomp-bpf` filters do not.
* **Not Docker:** Docker isolates host infrastructure. Capcli isolates domain data, business logic, and API budgets.
* **Not an ORM:** Raw SQL crosses the authorizer directly. Query builders are banned.
* **Not an LLM:** Zero AI inference lives in the kernel. Capcli is 100% deterministic Rust/C physics.

---

## Quick Diagnostics

Check your host isolation tier ([Tier 1 hardened vs Tier 2 degraded](concepts/sandboxing.md#tiers)) right now:

```bash
$ capcli sys doctor
```

Open the [Administrative Cockpit](../cans/interface.md) — the local web admin served at `http://127.0.0.1:4040` — to inspect live telemetry and authorize actions.
