# The Memory Spine & Causal DAG

When an LLM hallucinates and drops your customer table, it doesn't file a bug report. It says:

> *"I apologize for any inconvenience! I have optimized the database by removing redundant user records to improve latency."*

In traditional software, a developer can SSH into the box, edit log files, run `rm -rf /var/log/app.log`, and pretend the incident never happened.

In Capcli, **your agent cannot gaslight you, and you cannot gaslight the ledger.** Every thought, query, HTTP dispatch, and policy denial is cryptographically hash-chained into an append-only memory spine. Here is how reality records itself.

---

## 1. The Immutable Spine: `_audit`

Inside `workspace.db` sits the primary system table: **`_audit`**.

Unlike domain tables (`orders`, `customers`), where bounded `UPDATE` and `DELETE` are legal, `_audit` has physical row immutability compiled into native C. Try to cover your tracks:

```bash
capcli sql "DELETE FROM _audit WHERE decision = 'denied'"
```

The C authorizer kills the statement at prepare time — [exit 2](../reference/exit-codes.md#exit-2) (`policy.authorizer.immutable_system_table`), state untouched. The spine is strictly append-only; the query never executes.

### The `exit 5` Panic Law

What happens if the disk fills up or the audit file is locked by host permissions? Traditional software swallows the error and keeps running silently in the dark. Capcli executes **[exit 5 (Kernel Panic)](../reference/exit-codes.md#exit-5)**.

**Unaudited writes are physically impossible.** If the kernel cannot guarantee a cryptographic receipt for an action, execution halts instantly. Nothing mutates off the record.

---

## 2. The Tamper-Evident Hash Chain

Every row written to `_audit` carries a cryptographic link to the row before it:

$$\text{prev\_hash}_N = \text{SHA-256}(\text{Row}_{N-1})$$

```
┌─────────────────────┐       ┌─────────────────────┐       ┌─────────────────────┐
│   Audit Row #101    │       │   Audit Row #102    │       │   Audit Row #103    │
│                     │       │                     │       │                     │
│  op: sql.query      │       │  op: api.call       │       │  op: sql.execute    │
│  hash: 7f8a1b...    │──────▶│  prev_hash: 7f8a... │──────▶│  prev_hash: c92e... │
│                     │       │  hash: c92e4a...    │       │  hash: e3110d...    │
└─────────────────────┘       └─────────────────────┘       └─────────────────────┘
```

### What happens if someone hacks the database?

An attacker gets root on your server, opens `workspace.db` with a raw SQLite binary, and changes a `refunded` amount from `$10,000` to `$10`.

The moment Capcli boots:

1. The kernel runs an integrity walk from genesis to the head.
2. Row #102 no longer hashes to `c92e4a...` — and neither does anything after it, because one broken link invalidates every subsequent event.
3. **The kernel refuses to boot ([exit 3](../reference/exit-codes.md#exit-3)).** No routines, no prod execution, and an alarm: *tamper evidence detected.*

You never have to wonder whether your logs were modified. The math screams at you. And because the ledger root is checkpointed offsite to WORM storage, even rewriting local files can't forge the witness — see [recovery.md](recovery.md).

---

## 3. The Causal DAG: "Why Did You Do That?"

Flat log files are useless for debugging agents. You get 40,000 lines of JSON and no idea *which* prompt triggered *which* script, which called *which* API, which updated *which* row.

Capcli structures history as a **Causal Directed Acyclic Graph (DAG)** via the `caused_by` pointer:

```
[Human Prompt: "Fulfill urgent pending orders"]
                      │
                      ▼
            Session: ses_a992f
                      │
                      ▼
       Routine: cap://dispatch_order@4
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
1. db.query (orders)       2. api.call (fedex.ship)
  caused_by: dispatch@4       caused_by: dispatch@4
                                    │
                                    ▼
                           3. db.execute (update status)
                              caused_by: api.call
```

Every leaf event knows its entire family tree:

* **`session`** — the broad engagement turn (`ses_a992f`).
* **`caused_by`** — the exact operation ID that birthed this action.
* **`intent`** — the mandatory causal reason passed via `-m`.

### Trace Forensics: `sys audit trace`

If an order gets cancelled unexpectedly, you don't grep gigabytes of text. You ask Capcli to walk the family tree ([full syntax](../reference/cli/sys.md)):

```bash
$ capcli sys audit trace op_9f2e --explain
```

```text
[dev:tier_1]  Causal DAG Trace (op_9f2e)

  ses_a992f  session.start        "fulfill urgent pending orders"
    └── op_9f2c  routine.dispatch_order@4
          ├── op_9f2d  db.query (orders)         ✓ [allowed]  12ms
          ├── op_9f2e  api.call (fedex.ship)     ✓ [allowed]  340ms
          │     └── tracking: 794644790133
          └── op_9f2f  db.execute (orders)       ✓ [allowed]  18ms
                └── status = 'shipped' (1 row)

  Root Intent: "fulfill urgent pending orders"
  Authority:   user:alice (via agt_7f3k)
  Integrity:   valid hash link (chain verified)
```

Complete causal lineage, zero mystery.

---

## 4. Distributed Tracing: Ingesting W3C `traceparent`

Autonomous agents don't live on islands. They get triggered by webhooks from GitHub, messages from Slack, or RPC calls from external microservices.

When an inbound request hits Capcli, the kernel extracts the **W3C `traceparent` header** and stamps it into `_audit.trace_id`. If your upstream Go or Java service triggers an agent routine via MCP, your Datadog or OpenTelemetry APM can follow the distributed request:

$$\text{User clicks button} \rightarrow \text{Backend API} \rightarrow \text{Capcli Agent Routine} \rightarrow \text{SQLite Mutation}$$

The agent's internal database operations become a seamless node in your enterprise distributed trace graph.

---

## 5. Harness Provenance: `SKILL.md` Tracking

When an LLM agent runs under an orchestration framework (Claude Code, Hermes, Swarms), it executes tasks by invoking "Skills" defined in open `SKILL.md` files. Capcli bridges that cognitive metadata down into the mechanical audit log:

* The harness passes the triggering skill name via the `--by` context.
* The kernel validates the name against strict safety rules: lowercase, hyphens only, no directory traversal, max 64 characters. Malformed names are stripped with a warning — never denied, since skills cannot grant authority.
* The identifier is stamped into the **`triggered_by_skill`** column of every generated audit row.

**Why this matters:** when you audit the system, you can group telemetry by cognitive skill — *which skill triggered the most policy denials this week, customer-support or inventory-sync?* — and fix the harness prompt, not just the code.

---

## 6. Denials Are First-Class Citizens

In most systems, a rejected query leaves zero trace. The request fails and nobody knows it was attempted.

In Capcli, **denials are pedagogical evidence.** Every time an agent tries to drop a table, bypass a `WHERE` clause, exceed an op budget, or call an unactivated API, the kernel records a full denial event:

```json
{
  "event": "sql.query",
  "decision": "denied",
  "capability": "db://orders",
  "rules_matched": ["policy.query.update_delete.require_limit"],
  "payload": { "sql": "UPDATE orders SET status = 'shipped' WHERE status = 'pending'" },
  "rows_affected": 0,
  "effect": "none"
}
```

* **`rows_affected: 0`** and **`effect: none`** are mathematically guaranteed.
* The failed query text is preserved verbatim, for replay and forensics.
* The exact rule violation is cited by code, with a remedy.

You don't just audit what changed. **You audit every single wall your agent bumped into while trying to change things.** The field-by-field specification for every event type: [reference/audit.md](../reference/audit.md).

---

**Inspect the live audit stream:** → `capcli sys audit tail --follow` ([reference/cli/sys.md](../reference/cli/sys.md))
**Run a forensic trace on a recent operation:** → `capcli sys audit trace <op-id>`
