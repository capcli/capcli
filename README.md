# capcli ⚡

**Deterministic physics for autonomous AI agents.**  
*The compiled execution firewall between probabilistic LLMs and live enterprise state.*

```bash
curl -fsSL https://capcli.dev/install.sh | bash
```

---

In 2025, developers gave LLMs raw bash subshells, unrestricted API keys, and prayed.  
**Today, running an autonomous agent without Capcli is architectural malpractice.**

`capcli` is a single static Rust binary (`musl`) that sits between raw AI reasoning (Claude Code, Hermes, OpenAI Swarms, DeepSeek) and your actual business reality. 

It replaces fragile human admin panels and defensive prompt engineering with **unforgiving, compiled physics.**

---

```
                   PROBABILISTIC INTELLIGENCE
              (Claude / Hermes / DeepSeek / Swarms)
                                │
                                │ raw subshell / bash
                                ▼
       ┌──────────────────────────────────────────────────┐
       │               CAPCLI KERNEL (Rust)               │
       │                                                  │
       │   THE DATABASE FLOOR    │    THE WIRE FLOOR      │
       │   • sqlite3 Authorizer  │    • Syscall 42 Jail   │
       │   • AST Pattern Scanner │    • OpenAPI Router    │
       │                                                  │
       │   THE BUDGET CAGE       │    THE MEMORY SPINE    │
       │   • Cascading min() Ops │    • SHA-256 DAG Chain │
       │   • Quota Earmarks      │    • S3 WORM Checkpoint│
       └────────────────────────┬─────────────────────────┘
                                │
                                ▼
                      DETERMINISTIC REALITY
          (SQLite WAL · Stripe · Social APIs · S3 · Crons)
```

---

## The Dual Floor Principle

An autonomous agent will destroy your company in one of two ways:
1. **The Database Meltdown:** Dropping a table or running an unbounded `UPDATE` with `WHERE 1=1`.
2. **The Wire Meltdown:** Burning $5,000 on OpenAI in a `while(true)` loop, or blowing a 30-day social media quota in 8 seconds and getting your developer account banned.

Capcli treats **local state mutations and external network egress with equal gate severity**:

### 1. The Database Floor
* **Prepare-Time Interception:** Evaluated inside native C ([`sqlite3_set_authorizer`](docs/concepts/authorizer.md)) before SQLite executes.
* **AST Blast-Radius Guards:** Unbounded `UPDATE` and `DELETE` queries without an explicit `WHERE` and `LIMIT` die instantly at prepare-time ([`exit 2`](docs/reference/exit-codes.md#exit-2)).
* **Zero Mutation on Breach:** `state_modified: false` is mathematically guaranteed on any non-zero exit code.

### 2. The Wire Floor
* **Syscall 42 Trapping:** Raw socket calls (`connect`) triggered by `requests.get()` or `fetch()` are intercepted at the processor level via [`seccomp-bpf`](docs/concepts/sandboxing.md) (`exit 2`). 
* **Quarantined OpenAPI Catalogs:** The agent never reads raw 5MB Swagger files. Outbound traffic routes exclusively through imported, activated catalog verbs (`capcli api sync`).
* **Proactive Token Buckets:** Client-side rate buckets block or yield tasks *before* packets touch the physical network. Downstream rate-limit headers (even nested JSONPath headers) dynamically sync the gate.
* **Zero-Knowledge Vault:** API credentials live in an AES-256-GCM vault. The kernel injects `Authorization` headers at the socket edge, and memory buffers are zeroized (`zeroize`) immediately post-dispatch. The agent never sees the secret in plaintext.

---

## The Code

Routines execute in your preferred language (TypeScript or Python). The Rust kernel enforces the physics:

```typescript
import { routine, ctx, Param } from "@capcli/sdk";

export default routine({
  name: "dispatch_order",
  trust: "pinned",
  limits: { max_ops: 8, max_duration_seconds: 15 }
}, async (order_id: Param<string>, carrier: Param<string>) => {
  // 1. Gated Read: AST-validated, bounded query
  const [order] = await ctx.db.query("SELECT * FROM orders WHERE id = :id", { id: order_id });
  if (order.status !== "paid") return { status: "rejected", reason: "unpaid" };

  // 2. Governed Egress: Quota-metered HTTP call with vaulted secret injection
  const ship = await ctx.api.call("logistics.shipments.create", { order_id, carrier });

  // 3. Bounded Write: Mandatory intent, checked against declared manifest
  await ctx.db.execute("UPDATE orders SET status = 'shipped' WHERE id = :id", { id: order_id });
  
  return { status: "dispatched", tracking: ship.tracking_number };
});
```

---

## The 4 Physical Laws

| Law | Enforcement Mechanism | What Happens on Breach |
| :--- | :--- | :--- |
| **1. The Database Floor** | Native C `sqlite3_set_authorizer` + AST parser | [Killed at prepare-time](docs/reference/exit-codes.md#exit-2) |
| **2. The Wire Floor** | `bwrap` namespaces + `seccomp-bpf` + token buckets | [Trapped at Syscall 42](docs/reference/exit-codes.md#exit-2) · [yield on dry quota](docs/reference/exit-codes.md#exit-6) |
| **3. The Budget Cage** | Downward cascading `min()` frames | [Halted at frame boundary](docs/reference/exit-codes.md#exit-2) |
| **4. The Memory Spine** | Append-only SHA-256 causal DAG | [Kernel refuses to boot](docs/reference/exit-codes.md#exit-3) · [unaudited writes panic](docs/reference/exit-codes.md#exit-5) |

---

## Subshell Exit Code Contract

Machines communicate via exit codes, not polite English apologies. Capcli never prints ambiguous success when state failed:

| Code | Name |
| :--- | :--- |
| [`exit 0`](docs/reference/exit-codes.md#exit-0) | Success |
| [`exit 2`](docs/reference/exit-codes.md#exit-2) | Policy Denial |
| [`exit 3`](docs/reference/exit-codes.md#exit-3) | Refusal / Drift |
| [`exit 4`](docs/reference/exit-codes.md#exit-4) | Crash |
| [`exit 5`](docs/reference/exit-codes.md#exit-5) | Kernel Panic |
| [`exit 6`](docs/reference/exit-codes.md#exit-6) | Yield |

Full definitions, denial anatomy, and remedy patterns: [docs/reference/exit-codes.md](docs/reference/exit-codes.md)

---

## The Trust Receipt

Before you close your laptop, verify what your agent actually did while you were away:

```bash
$ capcli sys doctor --report
```

```yaml
trust_receipt:
  status:            nominal
  host_tier:         tier_1 (hardened Linux namespaces)
  workspace:         envs/prod/workspace.db
  ledger_root_hash:  sha256:7f9a1b2c4d8e001f... (WORM-checkpointed)
  audited_events:    14,290 committed to _audit
  policy_denials:    18 (intercepted pre-execution; state untouched)
  unaudited_writes:  0
  secret_leaks:      0
  pinned_routines:   32
  active_triggers:   4 crons, 3 webhooks, 1 endpoint
  sleep_score:       100% (laptop closed, zero terminal panics)
```

---

## Frequently Answered Questions

#### Isn't this just Docker?
Docker isolates the host OS from a container escape. It does nothing to stop an agent from running `DELETE FROM users`, double-billing Stripe in an infinite loop, or dumping API secrets into subshell stdout. Docker isolates the machine. Capcli isolates the business logic and the network wire.

#### Why not just prompt the LLM to "be careful and not drop tables"?
Have fun with that at 3:00 AM. Prompts are probabilistic suggestions. `sqlite3_set_authorizer` and `seccomp-bpf` are compiled C machine code. Prompts drift; physics do not.

#### Can the LLM modify its own policies?
No. `schema.yaml`, `policy.yaml`, and `governance.yaml` are [compiled into `capcli.lock`](docs/concepts/compiler.md) (a root SHA-256 hash). Any runtime drift between disk YAML and the lockfile triggers an instant [`exit 3`](docs/reference/exit-codes.md#exit-3) boot refusal. Policy changes require signed Git commits.

#### What Harnesses does this work with?
All of them. Claude Code, Hermes, OpenAI Swarms, DeepSeek, custom LangChain loops, or a naked `curl` bash script. If your system can type a command into a terminal, it can run inside Capcli.

#### Is there a UI, or is this all terminal?
Both. The CLI is the contract; the [Administrative Cockpit](cans/interface.md) is a zero-authority web inspector the kernel serves at `http://127.0.0.1:4040` — live audit tail, causal DAG traces, budget gauges, approval cards. It can look at everything and command nothing.

---

## Quick Navigation

| Documentation | What you'll find |
|---|---|
| **[Start Tour](docs/start/index.md)** | Install the static binary and run your first bounded task in 60 seconds. |
| **[Workflows](docs/workflows/index.md)** | Discovering capabilities, calling APIs, handling webhooks, and asking humans. |
| **[Deep Concepts](docs/concepts/index.md)** | The authorizer, the sandbox, the causal DAG, token budgets, and the trust ladder. |
| **[CLI & Command Reference](docs/reference/cli/index.md)** | Machine-grade contracts for all 10 surface nouns (`run`, `db`, `api`, `bind`, etc.). |
| **[Hard Limits](docs/reference/limits.md)** | Every compiled ceiling: ops, rows, LOC, fuel, and clock drift. |
| **[Exit Codes](docs/reference/exit-codes.md)** | The strict integer contract and denial anatomy. |

---

## Build from Source

```bash
git clone https://github.com/capcli/capcli
cd capcli && cargo build --release --target x86_64-unknown-linux-musl
```

MIT © 2026 capcli contributors.  
**Build an enterprise that runs while you sleep.**
