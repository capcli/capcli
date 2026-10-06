# Capcli

**The compiled execution firewall between probabilistic AI agents and live enterprise state.**

Your LLM reasons. Capcli enforces what it can touch, how much it can burn, and cryptographically signs every attempt—allowed or denied.

```bash
curl -fsSL https://capcli.dev/install.sh | bash
```

---

## What are you trying to accomplish?

| Your Goal | Where to go |
|---|---|
| **Zero setup. See it work in 60 seconds.** | [Start Here →](start/index.md) |
| **Run a bounded query or safe mutation right now.** | [First Task →](start/first-task.md) |
| **Make safe API calls without leaking keys or burning quotas.** | [Call APIs →](use/call-apis.md) |
| **Handle incoming webhooks, crons, or export an MCP server.** | [Inbox & Triggers →](use/inbox-and-triggers.md) |
| **Pause execution and ask a human a structured question.** | [Ask Human →](use/ask-human.md) |
| **Understand the token-bucket floors & multi-day limits.** | [Budgets & Priority Floors →](understand/budgets.md) |
| **Open the local web cockpit.** | [Administrative Cockpit →](concepts/cockpit.md) |
| **Hit an exit code or denial? Check the ceilings.** | [Hard Limits & Ceilings →](reference/limits.md) |
| **Look up exact CLI command contracts (10 surface nouns).** | [Command Reference →](reference/index.md) |

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

An autonomous agent doesn't just destroy your company by dropping a table. It also destroys you by double-charging 4,000 customers on Stripe in an infinite `while(true)` loop, or leaking your production credentials into a public terminal log.

Capcli enforces **The Dual Floor**:

### Floor 1: The Database Floor
* **Native C Authorizer:** Intercepts statements inside `sqlite3_set_authorizer` at prepare-time.
* **AST Semantic Traps:** Queries with missing `WHERE`, missing `LIMIT`, or tautology bypasses (`WHERE 1=1`) die before SQLite allocates a single byte of RAM.
* **Guaranteed Clean State:** Non-zero exits mathematically guarantee `state_modified: false`.

### Floor 2: The Wire Floor
* **Processor-Level Syscall Trapping:** `seccomp-bpf` intercepts raw network calls (`connect`, Syscall 42). A guest script trying to run `requests.post()` is killed by the CPU (`exit 2`).
* **Quarantined Catalogs:** Egress routes strictly through imported OpenAPI catalog verbs. The agent never reads raw 5MB Swagger files.
* **Proactive Token-Bucket Quotas:** Client-side rate buckets meter requests before packets leave your machine. Complex rolling windows (like Meta's nested JSON headers) dynamically throttle the gate.
* **Zeroize Memory Sanitation:** Secrets decrypted from the AES-256-GCM vault are injected at the wire proxy. Plaintext buffers are overwritten with physical zeros immediately post-dispatch. The agent never sees the key.

---

## The 4 Physical Laws

No prompt engineering. No *"please be careful"*. These are compiled into native machine code:

| Law | Enforcement Mechanism | What Happens on Breach |
| :--- | :--- | :--- |
| **1. Database Floor** | Native C `sqlite3_set_authorizer` + AST | Unbounded writes or missing `LIMIT` are **killed at prepare-time (`exit 2`)**. Zero rows touched. |
| **2. Wire Floor** | `bwrap` namespaces + `seccomp-bpf` + Quota | Raw sockets trapped at **Syscall 42 (`exit 2`)**. Quota exhausted? Tasks **yield cleanly (`exit 6`)**. |
| **3. Budget Cage** | Downward cascading frames ($\min$) | Op #51 on a 50-op run? **Halted at frame boundary (`exit 2`)**. No half-executed side effects. |
| **4. Memory Spine** | Append-only SHA-256 Causal DAG | Tampered audit log or broken link? **Corrupted block isolated to quarantine (`exit 0`)**, valid history stays operable. Chain unrecoverable with both sinks dead? **Panic (`exit 5`)**, boot refused. |

---

## Subshell Exit Code Contract

Machines communicate via exit codes, not conversational apologies:

* **`exit 0`** $\rightarrow$ **Success.** Committed to relational state, hashed into the causal ledger.
* **`exit 2`** $\rightarrow$ **Policy Denial.** Blocked by C authorizer, AST, trust rung, or budget. **State untouched.**
* **`exit 3`** $\rightarrow$ **Refusal / Drift.** Missing intent (`-m`) or lockfile mismatch. **State untouched.** (Host clock drift >500ms is not a refusal: the doctor screen warns on exit 0 and execution continues on monotonic time.)
* **`exit 4`** $\rightarrow$ **Crash.** Sandbox runtime exception. Transaction cleanly rolled back.
* **`exit 5`** $\rightarrow$ **Kernel Panic.** Audit sink unreachable. Hard halt. Kernel refuses to run unaudited.
* **`exit 6`** $\rightarrow$ **Yield.** Provider quota dry. Task safely parked in `_suspended_tasks` until token refill epoch.

---

## What Capcli is NOT

* **Not a prompt wrapper:** Prompts drift. C authorizers and `seccomp-bpf` filters do not.
* **Not Docker:** Docker isolates host infrastructure. Capcli isolates domain data, business logic, and API budgets.
* **Not an ORM:** Raw SQL crosses the authorizer directly. Query builders are banned.
* **Not an LLM:** Zero AI inference lives in the kernel. Capcli is 100% deterministic Rust/C physics.

---

## Quick Diagnostics

Check your local host isolation tier (Tier 1 Hardened vs Tier 2 Degraded) right now:

```bash
$ capcli sys doctor
```

Open the local Administrative Cockpit to inspect live telemetry and authorize actions:
```text
http://127.0.0.1:4040
```