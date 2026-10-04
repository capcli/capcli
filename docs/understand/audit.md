
# The Memory Spine & Causal DAG

AI agents are world-class gaslighters.

When an LLM hallucinates and drops your customer table, it doesn't say *"I am a broken script that made an illegal SQL call."* It looks you in your virtual eyes and says:

> *"I apologize for any inconvenience! I have optimized the database by removing redundant user records to improve latency."*

In traditional software, developers can SSH into the box, edit log files, run `rm -rf /var/log/app.log`, and pretend the incident never happened.

In Capcli, **your agent cannot gaslight you, and you cannot gaslight the ledger.**

Every thought, query, HTTP dispatch, and policy denial is cryptographically hash-chained into an append-only memory spine. Here is how reality records itself.

---

## 1. The Immutable Spine: `_audit`

Inside `workspace.db` sits the primary system table: **`_audit`**. 

Unlike domain tables (`orders`, `customers`) where you can run bounded `UPDATE` or `DELETE` statements, the `_audit` table has physical row immutability compiled into native C:

```sql
-- You or your agent trying to cover your tracks:
capcli sql "DELETE FROM _audit WHERE decision = 'denied'"
```

```text
[dev:tier_1]  ✗  exit 2

  FAIL  policy.authorizer.immutable_system_table
        DELETE FROM _audit WHERE decision = 'denied'
        ^^^^^^^^^^^^^^^^^^
        System table '_audit' is strictly append-only. 
        Mutations and deletions are physically denied by the C authorizer.

  state_modified: false
  layer: authorizer
```

The C authorizer laughs in your face. The query never executes. 

### The `exit 5` Panic Law
What happens if the disk fills up or the audit file is locked by host permissions? 

Traditional software swallows the error and keeps running silently in the dark. Capcli executes **`exit 5` (Kernel Panic)**. 

**Unaudited writes are physically impossible.** If the kernel cannot guarantee a cryptographic receipt for an action, execution halts instantly. Nothing mutates off the record.

---

## 2. The Tamper-Evident Hash Chain

Every single row written to `_audit` contains a cryptographic link to the row before it:

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
Let’s say an attacker gets root access to your server, opens `workspace.db` with a raw SQLite binary, and changes a `refunded` amount from `$10,000` to `$10`.

The moment Capcli boots up:
1. The kernel runs an integrity walk from Genesis to the head.
2. It discovers that Row #102 doesn't hash to `c92e4a...`.
3. **The kernel commits suicide on boot (`exit 3`).**

It refuses to run in prod, refuses to execute routines, and sounds the alarm: **Tamper evidence detected.** You don’t have to wonder if your logs were modified. The math screams at you.

---

## 3. The Causal DAG: "Why Did You Do That?"

Flat log files are useless for debugging agents. You get 40,000 lines of JSON logs, and you have no idea *which* prompt triggered *which* script, which called *which* API, which updated *which* row.

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

Every single leaf event knows its entire family tree:
* **`session`**: The broad engagement turn (`ses_a992f`).
* **`caused_by`**: The exact operation ID that birthed this specific action.
* **`intent`**: The mandatory causal reason passed via the `-m` flag.

### Trace Forensics: `sys audit trace`
If an order gets cancelled unexpectedly, you don't grep through gigabytes of text. You ask Capcli to walk the family tree:

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

You get the complete causal lineage in under 20ms. Zero mystery.

---

## 4. Distributed Tracing: Ingesting W3C `traceparent`

Autonomous agents don't live on islands. They get triggered by webhooks from GitHub, messages from Slack, or RPC calls from external microservices.

When an inbound request hits Capcli, the kernel extracts the **W3C `traceparent` header** and stamps it into `_audit.trace_id`.

If your upstream Go or Java service triggers an agent routine via MCP, your Datadog or OpenTelemetry APM can trace the distributed request:

$$\text{User clicks button in UI} \longrightarrow \text{Backend API} \longrightarrow \text{Capcli Agent Routine} \longrightarrow \text{SQLite Mutation}$$

The agent’s internal local database operations become a seamless node in your enterprise distributed trace graph.

---

## 5. Harness Provenance: `SKILL.md` Tracking

When an LLM agent uses an orchestration framework (like Claude Code, Hermes, or Swarms), it executes tasks by invoking "Skills" (defined in open `SKILL.md` files).

Capcli bridges this cognitive metadata down into the mechanical audit log:
* The harness passes the triggering skill name via the `--by` context.
* The kernel validates the skill name against strict safety rules (lowercase, hyphens only, no directory traversal, max 64 characters).
* It stamps the identifier into the **`triggered_by_skill`** column of every generated audit row.

**Why this matters:** When you audit your system, you can group your telemetry by cognitive skill: *"Which skill triggered the most policy denials this week? The customer-support skill or the inventory-sync skill?"*

---

## 6. Denials Are First-Class Citizens

In most systems, if a query is rejected, nothing is logged. The request simply fails, leaving zero trace of the attempt.

In Capcli, **denials are pedagogical evidence.** 

Every time an agent tries to drop a table, bypass a `WHERE` clause, exceed an op budget, or call an API verb its trust rung forbids, the kernel records a full denial receipt:

```json
{
  "event": "sql.query",
  "decision": "denied",
  "capability": "db://orders",
  "rules_matched": ["policy.query.update_delete.require_limit"],
  "payload": {
    "sql": "UPDATE orders SET status = 'shipped' WHERE status = 'pending'"
  },
  "rows_affected": 0,
  "effect": "none"
}
```

* **`rows_affected: 0`** and **`effect: none`** are mathematically guaranteed.
* The failed query text is preserved.
* The exact rule violation is cited.

You don't just audit what changed. **You audit every single wall your agent bumped into while trying to change things.**

---

## The One Rule

**State mutates only after the ledger agrees.**

The hash chain is the ground truth of your company. If it isn't in the memory spine, it didn't happen. If it is in the memory spine, it cannot be erased.

---

**Inspect the live audit stream right now:** → `capcli sys audit tail --follow`  
**Run a forensic trace on a recent operation:** → `capcli sys audit trace <op-id>`
