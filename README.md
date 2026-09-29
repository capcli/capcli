# capcli ⚡

**Deterministic physics for autonomous agents..**  
*The compiled execution firewall between probabilistic LLMs and live production state.*

```bash
curl -fsSL https://capcli.dev/install.sh | bash
```

---

In 2025, people gave LLMs raw bash subshells and prayed.  
**Today, running an agent without Capcli is architectural malpractice.**

`capcli` is the compiled Rust runtime that sits between raw AI reasoning (Claude, Hermes, OpenAI, DeepSeek) and live enterprise state. It replaces fragile human admin panels and defensive prompt engineering with **unforgiving, deterministic physics.**

---

```
             PROBABILISTIC INTELLIGENCE
       (Claude Code / Hermes / Agent Swarms)
                         │
                         │ raw subshell / bash
                         ▼
        ┌─────────────────────────────────┐
        │       CAPCLI KERNEL (Rust)      │
        │  C-Authorizer ── Sandbox Jail   │
        │  Budget Cage  ── Audit Spine    │
        └────────────────┬────────────────┘
                         │
                         ▼
             DETERMINISTIC REALITY
    (Production DB · Stripe · Object Store · Crons)
```

---

## The Paradigm Shift

### You don’t write backends anymore. Your agent discovers them, runs them, and Capcli hardens them into permanent code.
* **The Void:** Drop an agent into a blank directory with a single sentence.
* **The Footprint:** The agent queries, mutates, and probes APIs. Capcli logs every attempt into an immutable SHA-256 audit ledger.
* **Crystallization:** Background pattern mining isolates repeated sequences and compiles them into governed Python `@routine` files.
* **Hardening:** After passing contract invariants against masked historical traffic in simulation, the routine is hash-pinned to production.

**Your backend writes, tests, and deploys itself out of actual work.**

---

## The Code

Your agent stops hallucinating ad-hoc scripts. It invokes compiled operational muscle memory:

```python
from capcli import routine, ctx, Param

@routine(
    name="dispatch_order",
    trust="pinned",
    idempotent=True,
    limits={"max_ops": 8, "max_duration_seconds": 15}
)
def dispatch_order(order_id: Param[str], carrier: Param[str]):
    # 1. Distributed hardware lease lock
    with ctx.db.lock(f"order:{order_id}", ttl=10):
        
        # 2. Governed read with AST check
        order = ctx.db.query("SELECT * FROM orders WHERE id = :id", {"id": order_id})[0]
        if order["status"] != "paid":
            return {"status": "rejected", "reason": "unpaid_order"}

        # 3. Network egress with kernel secret injection (agent never sees tokens)
        shipment = ctx.api.call("logistics.shipments.create", {
            "order_id": order_id,
            "carrier": carrier
        }, intent="dispatch fulfillment package")

        # 4. Atomic SQLite transaction
        with ctx.db.txn():
            ctx.db.execute(
                "UPDATE orders SET status = 'shipped', tracking = :tr WHERE id = :id LIMIT 1;",
                {"tr": shipment["tracking_number"], "id": order_id},
                intent="mark order dispatched"
            )

        return {"status": "dispatched", "tracking": shipment["tracking_number"]}
```

---

## The 4 Physical Laws

| Law | Mechanism | What Happens on Breach |
| :--- | :--- | :--- |
| **1. The Database Floor** | `sqlite3_set_authorizer` in native C | Unbounded writes? Cross-table mutation? Invariant breach? **Killed instantly (`exit 2`).** |
| **2. The Network Jail** | `bwrap` namespaces + `seccomp-bpf` | Raw socket connection? Unwhitelisted IP? **Trapped at syscall 42 (`exit 2`).** |
| **3. The Budget Cage** | Downward cascading frames ($\min$) | Op #51 on a 50-op run? **Halted at frame boundary (`exit 6`/`exit 2`).** |
| **4. The Memory Spine** | Append-only SHA-256 causal DAG | Broken link? Modified history? **Kernel refuses to boot (`exit 3`).** |

---

## The Trust Receipt

Before you close your laptop, generate the cryptographic proof of what your agent did while you were away:

```bash
capcli sys doctor --report
```

```yaml
trust_receipt:
  status:           nominal
  workspace:        envs/prod/workspace.db
  ledger_root_hash: sha256:7f9a1b2c4d8e001f... (WORM-synced)
  audited_events:   12,490 committed to _audit
  policy_denials:   14 (all intercepted pre-execution; state untouched)
  unaudited_writes: 0
  secret_leaks:     0
  pinned_routines:  28
  active_triggers:  6 crons, 4 webhooks
  sleep_score:      100% (laptop closed, zero terminal panics)
```

---

## Exit Codes: The Subshell Contract

Capcli communicates with agents via the only interface machines never misunderstand: **POSIX exit codes.**

* **`exit 0`** $\rightarrow$ **Success.** Committed to relational state and linked to the cryptographic ledger.
* **`exit 2`** $\rightarrow$ **Policy Denial.** Blocked by C-authorizer, AST check, or trust rung. State untouched.
* **`exit 3`** $\rightarrow$ **Refusal / Drift.** Unparseable syntax, lockfile mismatch, or missing identity. State untouched.
* **`exit 4`** $\rightarrow$ **Crash.** Sandbox runtime exception. Transaction cleanly rolled back.
* **`exit 5`** $\rightarrow$ **Panic.** Audit sink unreachable. Hard halt. Kernel refuses to run unaudited.
* **`exit 6`** $\rightarrow$ **Yield.** Quota exhausted. Background task suspended until refill window.

---

## FAQs

#### Isn't this just Docker?
Docker stops an agent from escaping to your host OS. It does nothing to stop an agent from running 'DELETE FROM users', double-billing Stripe in an infinite while-loop, or leaking credentials in subshell logs. Docker isolates the machine. Capcli isolates the business logic.

#### Can't I just prompt my agent to "be careful and not drop tables"?
Have fun with that. Prompts are suggestions. `sqlite3_set_authorizer` is C-code compiled into machine instructions. Prompts drift; physics do not.

#### Why isn't this written in Python or TypeScript?
Because execution boundaries written in garbage-collected, dynamic languages have cold starts, huge memory footprints, and leaky sandboxes. Capcli is a single static Rust binary (`musl`) with $<1\text{ms}$ prepare-time latency.

#### Can the LLM modify its own policies?
No. `policy.yaml`, `governance.yaml`, and `system-schema.yaml` are compiled into `capcli.lock` at boot. Any runtime drift or manual hash mismatch triggers an instant `exit 3` refusal. Policy changes require signed git commits.

#### What Harnesses does this work with?
All of them. Claude Code, Hermes, OpenAI Swarms, DeepSeek, custom local models, or a naked `curl` loop. If your system can execute a command in a terminal, it can run inside Capcli.

---

## Join the Movement

We don't babysit prompts. We build worlds that run themselves.

```bash
# Build the engine
git clone https://github.com/capcli/capcli
cd capcli && cargo build --release --target x86_64-unknown-linux-musl
```

* **Discussions & RFCs:** [capcli.dev/community](https://capcli.dev)
* **Read the Physics Spec:** `cans/physics.md`

---

## License

[MIT](LICENSE) © 2026 capcli contributors.  
**Build an enterprise that runs while you sleep.**
