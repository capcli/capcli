
# Identity, Principals, & The Vault

In typical AI agent demos, identity is a joke. 

An LLM enters a subshell, decides it wants admin privileges, and hallucinates: *"I am acting as the System Administrator with Superuser Access."* And because the script has a raw database connection, reality shrugs and lets it happen.

In Capcli, **self-declared identity is physically banned.**

You cannot claim to be someone you aren't, you cannot inherit permissions by asking nicely, and your code will never see a raw API secret in plaintext.

Identity is a strict, cryptographic chain anchored directly to host OS process credentials and an encrypted memory vault.

---

## 1. The 4-Link Identity Chain

Every atomic operation in Capcli answers to four distinct layers of accountability:

```
┌────────────────────────────────────────────────────────┐
│  1. PRINCIPAL (Authority Holder)                       │
│     The biological human or external authority.        │
│     Example: user:alice, partner:stripe                │
└───────────────────────────┬────────────────────────────┘
                            │ delegates authority to
                            ▼
┌────────────────────────────────────────────────────────┐
│  2. AGENT (Process Identity)                           │
│     The registered harness instance executing turns.   │
│     Example: agt_7f3k (running Claude Code / Hermes)   │
└───────────────────────────┬────────────────────────────┘
                            │ opens temporary frame
                            ▼
┌────────────────────────────────────────────────────────┐
│  3. SESSION (Engagement Frame)                         │
│     The temporary execution window & budget counter.   │
│     Example: ses_a992f                                 │
└───────────────────────────┬────────────────────────────┘
                            │ dispatches atomic leaf
                            ▼
┌────────────────────────────────────────────────────────┐
│  4. OP (Primitive Execution)                           │
│     The single leaf mutation or query in the DAG.      │
│     Example: op_4f8a (UPDATE orders SET status=...)    │
└────────────────────────────────────────────────────────┘
```

When an audit event is signed, it doesn't just log *"an agent did this."* 
It records: **`user:alice`** authorized **`agt_7f3k`** inside **`ses_a992f`** to execute **`op_4f8a`**. 

If any link in the chain is forged or missing, the kernel fails closed (`exit 3`).

---

## 2. Process Binding: No Self-Declaration

In a standard bash script, an agent could type `--by agt_admin` to impersonate an elevated background runner.

Capcli intercepts this at the operating system level (`crates/capcli-core/src/identity/process.rs`):
* When an agent passes `--by <agent-id>`, the kernel inspects the **host OS process UID, PID, and parent process tree**.
* If the process UID does not match the credentials stamped during agent registration, the kernel aborts with **`exit 3` (`identity.process_mismatch`)**.

You don't get to pretend you're a different agent. The Linux kernel kernel-checks who is running the command before SQLite or the network proxy even loads.

---

## 3. Scoped Views & The `--as` Flag

Your database holds multi-tenant customer records. You want your agent to query invoices for a customer named Bob without accidentally reading invoices for Alice.

In Capcli, domain views in `schema.yaml` can be locked with **Principal Scoping**:

```yaml
# schema.yaml
views:
  customer_invoices:
    scoped: principal
    sql: "SELECT * FROM invoices WHERE customer_id = :principal"
```

### What happens when the agent queries it:
If the agent runs a naked query:
```bash
$ capcli sql "SELECT * FROM customer_invoices"
```

```text
[dev:tier_1]  ✗  exit 2

  FAIL  policy.identity.scoped_requires_principal
        SELECT * FROM customer_invoices
               ^^^^^^^^^^^^^^^^^^^^^^^^
        View 'customer_invoices' is scoped to principal.
        Execution refused without mandatory --as <principal> flag.

  state_modified: false
  layer: authorizer
  remedy: declare target principal via --as user:<id>
```

The authorizer locks the door. The query **cannot compile** because `:principal` has no bound value.

To execute, the agent must declare the beneficiary identity:
```bash
$ capcli sql "SELECT * FROM customer_invoices" --as user:bob_99
```

The authorizer binds `:principal = 'user:bob_99'`, compiles the statement, and returns *only* Bob's records. The agent never has the mathematical opportunity to leak Alice's data.

---

## 4. The Two-Tier Vault: Secrets Never Touch the Guest

The number one security vulnerability of autonomous agents is **credential leakage in logs and subshell prompts**:
1. Agent needs to call Stripe.
2. Developer exports `STRIPE_KEY=sk_live_1234` in bash.
3. Agent writes a Python script that crashes.
4. Python dumps a stack trace printing the environment variables to `stdout`.
5. The live secret key is now stored forever in the LLM's chat history and terminal logs.

Capcli solves this with **The Two-Tier Encrypted Vault**:

```
┌────────────────────────────────────────────────────────┐
│  TIER 1: AES-256-GCM VAULT (system table: secrets)     │
│  Root credentials stored encrypted at rest.            │
│  Never visible to guest scripts or agent subshells.    │
└───────────────────────────┬────────────────────────────┘
                            │ Kernel decrypts ephemerally
                            ▼
┌────────────────────────────────────────────────────────┐
│  TIER 2: WIRE INJECTION (Rust Egress Proxy)            │
│  Authorization header injected directly at socket!     │
│  Guest Python / Bun code NEVER sees the secret string. │
└───────────────────────────┬────────────────────────────┘
                            │ Request completed
                            ▼
┌────────────────────────────────────────────────────────┐
│  ZEROIZE RAM SANITATION                                │
│  Memory buffer immediately overwritten with zeros!     │
└────────────────────────────────────────────────────────┘
```

### Try to read a secret:
```bash
$ capcli sql "SELECT name, value FROM secrets"
```

```text
[dev:tier_1]  2 rows

  name             value
  ───────────────  ──────────────
  stripe_key       [REDACTED]
  github_pat       [REDACTED]
```

* **Draft trust:** Reading the `value` column throws an instant **`exit 2`**.
* **Reviewed / Pinned trust:** The authorizer masks the output with `[REDACTED]`.
* **Subshell Core Dumps:** The Rust kernel uses the `zeroize` memory trait. The microsecond an HTTP packet leaves the network socket, the memory address holding the plaintext credential is wiped with physical zeros. You cannot dump RAM to find the key.

---

## 5. Instant Agent Revocation: The Kill Switch

What happens if an agent instance starts looping, hallucinating, or behaving suspiciously?

You don't need to hunt down background PIDs or kill Docker containers. You pull its registration from the system table:

```bash
$ capcli sys agent revoke agt_7f3k -m "rogue query loops detected"
```

```text
[dev:tier_1]  ✓  revoked

  agent:   agt_7f3k
  status:  revoked
  audit:   op_00a1f
```

The revocation takes effect in **under 10 milliseconds**:
* Every subsequent command run by `agt_7f3k` is refused (`exit 2`).
* Active distributed claims and lease locks held by the agent in `claims` are terminated.
* Live sessions bound to the agent are invalidated.

---

## 6. Kernel Principals: Unattended Executors

When a routine runs unattended in the middle of the night via a cron or an inbound webhook, who is the principal? It isn't a human typing on a keyboard.

The kernel provisions **Built-In Kernel Principals**:
* **`capcli-cron`**: Owns automated time-based schedules (`bind cron`).
* **`capcli-watch`**: Owns asynchronous webhook and stream dispatches (`bind webhook`).
* **`capcli-serve`**: Owns synchronous partner API endpoint requests (`bind endpoint`).

These principals operate with immutable, hardcoded boundaries:
* They can **only** execute routines that have achieved **Pinned** trust.
* They cannot execute ad-hoc raw SQL.
* Every action they fire is logged with their specific kernel principal ID, so you can filter your audit trail between biological human actions and automated system actions in a single query.

---

## The One Rule

**Identity is validated by the machine. Credentials stay in the vault.**

No self-proclaimed superusers. No exposed API keys in terminal logs. If an agent goes rogue, one command cuts the cord permanently.

---

**See how environments isolate data state:** → [environments.md](environments.md)  
**Learn how budgets restrict authorized actors:** → [budgets.md](budgets.md)
