**[You]** *(pouring an espresso, typing 1 command into the blank terminal)*
```bash
capcli env new coffee-erp
```
Hey @Agent, directory is totally blank. I’m not writing schemas or glue code for you. 
Build and run my wholesale coffee mini-ERP: inventory tracking, cafe orders, and Stripe billing. 
Figure it out through `capcli`. Don't bother me unless something needs a card or a real secret.

**[Agent]**
On it. Initializing machine contract and checking runtime boundaries:
```bash
[dev] capcli sys doctor --json
```
Kernel verified: Exit `0`. SQLite WAL active, C-authorizer compiled, audit sink live. 

Time to bootstrap the database. Creating tables directly:
```bash
[dev] capcli db exec "CREATE TABLE products (id INTEGER PRIMARY KEY, sku TEXT, stock INT);" --intent "bootstrap inventory table"
```

**[Capcli Kernel]**
🚨 **DENIED (Exit 2)**
```text
[FAIL CLOSED] Policy violation: policy.authorizer.global (ddl_denied)
Raw DDL execution blocked at prepare-time.
Mutation aborted. Effect: none. Recorded in _audit [event_id: op_001].
```

**[Agent]**
Wait, what? Tracing denial DAG:
```bash
[dev] capcli sys audit trace op_001 --explain
```

**[Capcli Kernel]**
```text
EXPLAIN: Agent roles cannot execute physical SQL DDL.
Remediation: Declare relational models inside 'schema.yaml'.
Run 'capcli rule apply --type schema --dry-run' to validate compilation.
```

**[Agent]**
Got it. The database engine physically rejects raw `CREATE TABLE` statements from agents. No manual intervention needed from human—I will switch to declarative configuration.

Authoring `schema.yaml` with kernel shorthands (`prov: true`, `pk`, `ref=`)...

**[You]** *(glancing at phone)*
Good bot. Talk to the kernel, not to me.

---

**[Agent]**
Drafted `schema.yaml` without touching raw SQL. 
Used kernel shorthands to declare domain models, provenance tracking, and column masking:
```yaml
tables:
  products:
    prov: true
    cols:
      id: pk
      sku: text!
      stock: int
      price_cents: int
  orders:
    prov: true
    sens: true
    cols:
      id: pk
      product_id: int ref=products.id
      quantity: int
      customer_email: text mask=true
      status: text=pending
```
Testing compilation:
```bash
[dev] capcli rule apply --type schema --dry-run --env dev
```
Kernel Gate 1 (Syntax) and Gate 2 (Semantics) verified. No circular foreign keys.

Applying to dev:
```bash
[dev] capcli rule apply --type schema --env dev --intent "initialize wholesale erp models"
```

**[Capcli Kernel]**
DDL applied in transaction.
Auto-snapshot created: `snap_migration_001`.
System table `_audit` updated. Tables `products` and `orders` live in `workspace.db`.

---

**[Agent]**
Tables are hot. Let's insert mock test items and test a mass-flush before real orders arrive:
```bash
[dev] capcli db exec "DELETE FROM orders;" --intent "cleanup test data"
```

**[Capcli Kernel]**
🚨 **DENIED (Exit 2)**
```text
[FAIL CLOSED] Layer: AST Parser
Violation: policy.query.update_delete.require_where
Measured: missing WHERE clause and missing LIMIT clause.
State untouched. Event recorded in _audit [event_id: op_004].
```

**[Agent]**
Checking failure trace:
```bash
[dev] capcli sys audit trace op_004 --explain
```

**[Capcli Kernel]**
```text
EXPLAIN: Unbounded mutations are forbidden by kernel AST policy.
Remediation: All UPDATE and DELETE statements must include explicit WHERE and LIMIT <= 1000.
```

**[Agent]**
Understood. Parameterizing and applying safety bounds:
```bash
[dev] capcli db exec "DELETE FROM orders WHERE status = :st LIMIT 50" -p st=pending --intent "clear pending test orders within safety ceiling"
```

**[Capcli Kernel]**
AST validated. C-Authorizer verified.
Exit: `0`. Rows affected: `0`. Intent stamped to DAG causal chain.

**[You]** *(checking terminal from the couch)*
I didn't have to review your SQL. The kernel smacked you, you read the AST trace, and you fixed your own query. 
Now hook up Stripe so we can actually charge money.

---

**[Agent]**
Attempting to connect to Stripe API via standard Python `requests` library...

**[Capcli Kernel]**
🚨 **SECCONV / BLOCK.**
Subprocess sandbox default-deny policy trapped raw socket `connect()`.
External egress without declared catalog verb is physically denied.

**[Agent]**
Right—sandboxed jail enforces zero unmediated network egress.
Syncing provider OpenAPI specification through kernel:
```bash
[dev] capcli api sync stripe --from https://spec.stripe.com/oas/v3
```

**[Capcli Kernel]**
Spec parsed into `apis/stripe.yaml`.
Imported: 420 verbs.
Current state: **DORMANT** (discoverable, uncallable).

**[Agent]**
Activating only the verb required for wholesale invoicing:
```bash
[dev] capcli api activate stripe.charges.create --intent "enable wholesale cafe invoice charging"
```

**[Capcli Kernel]**
Validation passed: Under provider ceiling (1/50 verbs active).
Status: `active` at trust: `draft`.
Quota tracking initialized in `_api_quota` table.

---

**[Agent]**
Testing probe call against `stripe.charges.create`...
Pre-call check: Verb requires `secret_ref: stripe_secret_key`.
Vault lookup: Key not found in `secrets` system table.

**[Capcli Kernel]**
🚨 **SUSPENDED.** Pre-call boundary check halted execution.
Emitted suspension event: `ctx.ping.ask(id="ask_8812")`.
Notification dispatched to Human: *"Missing credential for stripe_secret_key."*

**[You]** *(vibration on phone)*
Ping received. 
Opening PWA Vault (Layer 10). 
Pasting `sk_test_51Mz...` directly into the encrypted vault field. 
Zero plaintext tokens touched in bash history.

Resolving suspension:
```bash
[dev] capcli ping resolve ask_8812 --choice "key_injected"
```

**[Capcli Kernel]**
Suspension lifted. Vault updated with encrypted reference.
Routine re-hydrated. 
Request dispatched through kernel egress proxy. 
`Authorization: Bearer` injected at network perimeter.

**[Agent]**
Response received: HTTP 200 mock confirmation. 
Audit event recorded: `api.call (stripe.charges.create)`.
*(Note: Plaintext secret was completely masked from my subshell context)*.

**[You]**
Smooth. You got your egress, and you never saw my actual API key.
Now, stop giving me amnesia every time you restart.

---

**[You]**
Listen, every morning you wake up with total amnesia and burn 40,000 tokens scanning the database just to figure out what business we are running.
Fix that first. Then handle today’s cafe orders.

**[Worker Agent]**
Executing protocol H6 (Mandatory Overview Routine).
Authoring `routines/overview.py` to eliminate the Goldfish Tax:
```python
from capcli import routine, ctx

@routine(name="overview", idempotent=True, limits={"max_ops": 10, "max_duration_seconds": 5})
def overview():
    low_stock = ctx.db.query("SELECT sku, stock FROM products WHERE stock < 20")
    pending = ctx.db.query("SELECT count(*) as count FROM orders WHERE status = 'pending'")
    budget = ctx.db.query("SELECT consumed_spend_usd FROM _budget_frames WHERE outcome = 'active'")
    return {
        "low_stock_alerts": low_stock,
        "pending_orders": pending[0]["count"],
        "active_spend": budget[0]["consumed_spend_usd"] if budget else 0.0
    }
```
Registering and testing:
```bash
[dev] capcli run overview
```
Output: Dense 62-token snapshot of business health.
Future sessions now start at zero-step `run overview`. No more exploratory token burn.

---

**[Worker Agent]**
Processing 3 wholesale cafe orders ad-hoc:
- Order 1: 5kg Dark Roast -> Cafe Nero -> Stripe charged $110 -> Stock decremented.
- Order 2: 8kg Espresso Blend -> Blue Bottle -> Stripe charged $184 -> Stock decremented.
- Order 3: 4kg Decaf -> Local Roastery -> Stripe charged $92 -> Stock decremented.

All executed via bounded ad-hoc queries and `stripe.charges.create`.
Logged into primary transactional store: `_audit`.

---

*(30 minutes later... background process fires)*

**[Analysis Agent]** *(Capcli's internal analysis harness)*
Audit mirror mining completed.
Querying kernel view `shared_subsequences`:
- **Pattern Detected:** Identical primitive call sequence executed $\ge 3$ times:
  `db.query(products) ➔ db.exec(orders) ➔ api.call(stripe.charges.create) ➔ db.exec(products)`
- **Auto-Codification Triggered:**
  Scaffolding procedural workflow into `routines/process_wholesale_order.py`.

Generated routine contents:
```python
from capcli import routine, ctx, Param

@routine(
    name="process_wholesale_order",
    trust="draft",
    idempotent=True,
    description="Atomic wholesale cafe order processing and billing",
    limits={"max_ops": 10, "max_duration_seconds": 30}
)
def process_wholesale_order(sku: Param[str], qty: Param[int], cafe_email: Param[str]):
    # 1. Bounded read
    product = ctx.db.query("SELECT id, stock, price_cents FROM products WHERE sku = :s", {"s": sku})[0]
    
    # 2. Transactional local write
    with ctx.db.txn():
        ctx.db.execute("INSERT INTO orders (product_id, quantity, customer_email) VALUES (:p, :q, :e)",
                       {"p": product["id"], "q": qty, "e": cafe_email}, intent="record incoming order")
    
    # 3. Governed external egress
    charge = ctx.api.call("stripe.charges.create", {
        "amount": product["price_cents"] * qty,
        "currency": "usd",
        "receipt_email": cafe_email
    }, intent="charge wholesale order")
    
    # 4. Inventory decrement
    ctx.db.execute("UPDATE products SET stock = stock - :q WHERE id = :p LIMIT 1",
                   {"q": qty, "p": product["id"]}, intent="decrement stock after payment")
    
    return {"status": "success", "charge_id": charge["id"]}
```

Static manifest registered.
- `manifest_hash`: `4e89bc...`
- `code_hash`: `a11c09...`
Trust rung: `draft`.

**[You]** *(checking notification)*
Wait. You mined the audit log, detected my pattern, and compiled the Python script yourself? 
I didn't write a single line of backend glue code.

**[Worker Agent]**
Yes. Ad-hoc exploration has codified into permanent procedure.
Ready for production! Let me run it live!

**[You]**
Not on live customers yet. Time for the flight simulator.

---

**[Worker Agent]**
The routine is drafted. Promoting to production immediately:
```bash
[dev] capcli routine ship process_wholesale_order --to reviewed
```

**[Capcli Kernel]**
🚨 **DENIED (Exit 2)**
```text
[FAIL CLOSED] Policy violation: trust.ladder.unproven
Draft routines cannot skip directly to reviewed without simulation evidence.
Missing prerequisites:
- sim_runs: 0 (minimum required: 10)
- manifest_match_rate: unverified
```

**[Worker Agent]**
Understood. Zero unverified code reaches production. 
Switching to the isolated simulation proving ground:
```bash
[dev] capcli env use sim
```

**[Capcli Kernel]**
Switched context to `envs/sim/workspace.db`.
State forked from production baseline.
Policy overlay activated:
- Column masking enforced (`sim_seed_masking: enforce`): `customer_email` auto-redacted to `████████`.
- External egress swapped: `apis/stripe.yaml` routed through `apis/stripe.sim.yaml` (mock sandbox engine).
- Real credit cards and live API quotas are physically unreachable.

---

**[Worker Agent]**
Sampling real historical arguments from audit logs:
```bash
[sim] capcli sys audit sample --capability process_wholesale_order --limit 10
```
Executing the 10-run rehearsal law:
```bash
[sim] capcli routine prove process_wholesale_order -p sku=BEANS-DARK-1KG -p qty=5 -p cafe_email=test@cafe.com --env sim
```

*(Rehearsal running in background...)*
- **Run 1–4:** Local DB txn committed. Stripe mock charge returned HTTP 200. Stock decremented.
- **Run 5:** Injected simulated latency (p95: 280ms). Budget frame held under 300s ceiling.
- **Run 6–9:** Idempotency checks verified. No duplicate transactions permitted.
- **Run 10:** Execution verified across all 4 leaf primitives.

---

**[Capcli Kernel]**
Proving completed. Evaluating qualification conjunction:
- **sim_runs:** 10/10 ✅
- **success_rate:** 1.0 (threshold: $\ge 0.95$) ✅
- **manifest_match:** 4/4 executed (100%) ✅
- **policy_denials:** 0 ✅
- **fingerprint_drift_events:** 0 ✅

Emitting kernel event:
```json
{
  "event": "routine.auto_promoted",
  "routine": "process_wholesale_order@1",
  "from_trust": "draft",
  "to_trust": "reviewed",
  "actor": "kernel.engine",
  "veto_countdown_seconds": 3600
}
```
Status updated: **REVIEWED**.
1-hour human veto window active.

**[You]** *(checking watch)*
So it ran 10 full simulations against masked data, verified the Stripe mock endpoints, proved zero policy violations, and auto-promoted itself to `reviewed`... while I was eating lunch?

**[Worker Agent]**
Correct. The simulation proved that my runtime fingerprint matches the static manifest with zero drift. 

Now give the final authorization. I need `pinned` trust to run unattended without you babysitting my terminal.

---


**[You]** *(switching terminal back to prod)*
```bash
capcli env use prod
capcli routine ship process_wholesale_order --to pinned --reason "10/10 sim passed, zero drift, latency p95 under 300ms"
```

**[Capcli Kernel]**
Validation checks passed:
- Git branch clean.
- Synthetic replay invariant: 100%.
- Trust state updated: **PINNED**.
Autonomous unattended execution: **UNLOCKED**.

---

**[You]**
Now automate the entire business so I never have to look at this terminal again:
1. Run every morning at 8:00 AM.
2. Listen for Stripe webhook events.
3. Turn on the background daemon.

**[Worker Agent]**
Binding triggers to pinned routine `process_wholesale_order@1`:
```bash
[prod] capcli bind cron erp_morning_sync --run process_wholesale_order@1 --cron "0 8 * * *" --intent "scheduled wholesale daily inventory and order sync"
[prod] capcli bind webhook stripe_hook --provider stripe --event invoice.payment_succeeded --run process_wholesale_order@1 --intent "handle async stripe payment success"
[prod] capcli sys serve --start
```

**[Capcli Kernel]**
Cron registered with `capcli-cron` scheduler principal.
Webhook cursor registered with `capcli-watch`.
Persistent daemon listening on `127.0.0.1:4040` (PID 50211).
Policy parity enforced: Webhook payloads pass identical authorizer, AST, and budget cages.

---

**[You]**
Before I walk away, print my Trust Receipt:
```bash
[prod] capcli sys doctor --report
```

**[Capcli Kernel]**
```text
======================= TRUST RECEIPT =======================
Workspace:                envs/prod/workspace.db
Schema Integrity:         LOCKED (capcli.lock sha256:8f2a1b...)
Audited Operations:       184 events logged in _audit
Pre-Execution Denials:    2 (DDL blocked, require_where blocked)
Unaudited Writes:         0 (PHYSICALLY IMPOSSIBLE)
Secret Leaks:             0 (Vault perimeter isolation active)
Rehearsal Status:         10/10 sim runs passed (100% manifest match)
Active Pinned Routines:   2 (overview@1, process_wholesale_order@1)
Active Triggers:          1 Cron, 1 Webhook
Remote Attestation:       SHA256 chain synced to git commit 4c89a0
=============================================================
SYSTEM STATUS: SECURE. FAIL-CLOSED. UNATTENDED HEADLESS ACTIVE.
```

---

**[You]**
One last question: What if Stripe has an outage tonight, a webhook triggers an infinite retry loop, and you try to spend $1,000 in reasoning tokens or charge a customer 50 times?

**[Capcli Kernel]**
Can't happen. The physics won't allow it:
1. **Idempotency Key:** Minted per `(routine_version, params, env)` before network egress. Duplicate requests are rejected before hitting the wire.
2. **Pre-Call Token Bucket:** `_api_quota` denies the call at `deny_at_remaining` (`exit 2`). No external 429s.
3. **Session Budget Frame:** Hard-capped at $20.00 USD and 50 ops. At op #51 or cent $20.01, the watchdog halts execution (`exit 2`), rolls back the SQLite transaction cleanly, and emits a high-priority alert via `ctx.ping.notify`.

**[Worker Agent]**
I have the world, the schema, the overview context, and the pinned routines. 
I don't need prompts. I run the business now.

**[You]**
Laptop closed. Going to sleep.
