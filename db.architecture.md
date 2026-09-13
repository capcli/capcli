# capcli-db.architecture.md *(final v5 — token-optimized schema, CHECK-as-validation, primitive-aware)*

> The database layer of capcli: **SQLite as world-state, the agent as world-builder, policy as physics, raw SQL as the language, CHECK as validation.**

---

## 1. Scope & Convictions

capcli-db governs every effect on `workspace.db`. Six convictions:

1. **SQLite is not storage behind an app — it is the persistent world-state.**
2. **The harness builds the world. The kernel gates it.** During onboarding, the harness authors `schema.yaml` from the user's stated intent. The kernel validates, previews (`--dry-run`), and applies. Creation is the harness's job; permission is the kernel's job; approval is the human's job.
3. **Raw SQL is the language.** No ORM, no query builder, no Drizzle, no Prisma. Agents know SQL cold; they hallucinate ORM syntax.
4. **The agent is never trusted at runtime.** Enforcement lives in the SQLite engine and the kernel gate — never in prompts.
5. **One source of truth: `schema.yaml`.** SQL DDL is what it compiles to, never hand-edited. The agent writes YAML; the kernel generates DDL.
6. **CHECK is validation.** Content rules live in SQLite CHECK constraints — engine-enforced, SQL-native, one enforcement point. No `validate=` vocabulary.

---

## 2. SQLite as SSOT

```
workspace.db          # capcli-owned, chmod 600, daemon user — NOT git-tracked
world.sql             # deterministic dump — git-tracked, the recoverable artifact
audit/*.jsonl         # append-only event stream — git-tracked, tamper-evident
```

- **WAL mode** for concurrent read during routine execution
- **State reconstruction**: `state(t) = fold(events[0..t])` — the audit log is the replay source
- **File permissions are the first authorizer**: agent user has no direct path to the file; the kernel process is the only opener
- **Single-writer serialization is the multi-agent arbiter** — transactions settle conflicts; no distributed locks
- **The harness can still wipe everything native.** Where capcli can't gate, it recovers — world.sql + audit-in-git make deletion a recoverable event, not a catastrophe

Every DB effect flows: `intent → kernel → authorizer → AST → SQLite → audit event`. There is no other path.

---

## 3. schema.yaml — token-optimized, agent-authored

**The agent writes this file.** It is not a pre-defined template. The agent decides the domain model and expresses it in dense, token-efficient YAML using native filesystem access in the `dev` worktree.

The kernel's role: expand shorthand at compile time, gate application, enforce at runtime, refuse drift.

### Shorthand expansion rules

| Shorthand | Expands To | Safe Because |
|---|---|---|
| `pk` | `{type: integer, pk: true, autoincrement: true}` | Universal convention |
| `text pk` | `{type: text, pk: true}` | Text PK (e.g., agent IDs) |
| `text!` | `{type: text, unique: true}` | `!` suffix = unique |
| `text=val` | `{type: text, default: "val"}` | `=` suffix = default |
| `int~` | `{type: integer, immutable: true}` | `~` suffix = immutable |
| `int ref=table.col` | `{type: integer, references: table.col}` | FK inline |
| `prov: true` | `provenance: true` + auto `created_by`/`modified_by` | Kernel injects system cols |
| `sens: true` | `sensitive: true` | Table-level masking |
| `sys: true` | `system: true` + `readonly_grant: true` | System table |
| `imm_rows: true` | Append-only table | Authorizer denies UPDATE/DELETE |
| `imm_cols: [...]` | Specific immutable columns | Authorizer denies writes on listed cols |
| `idx: [col]` | `indexes: [{on: [col]}]` | Single-col index shorthand |
| `idx: [[a, b]]` | `indexes: [{on: [a, b]}]` | Composite index |
| `rel:` | Semantic traversal edge | Kernel search index + explain |
| `chk:` | CHECK constraint array | SQLite engine enforcement |
| `trig:` | Trigger definition | Policy-gated, explicit SQL |
| `mask=true` | Column-level redaction | Authorizer + audit redaction |
| `seed: [...]` | Initial rows applied with schema | Kernel INSERTs at rule apply; not agent runtime |

### Seed data
Tables may declare initial rows that ride with the schema migration:
```yaml
orders:
  cols: ...
  seed:
    - { ref: "ORD-001", status: "pending", total_cents: 4200 }
    - { ref: "ORD-002", status: "pending", total_cents: 1800 }
```
- Applied by the kernel during `capcli rule apply --type schema`, inside the same DDL txn
- Capped at 50 rows per table (onboarding-scale, not bulk loading)
- Audited as part of the `rule.apply` event (`seed_rows: N`)
- The world is born populated. The agent does not bulk-insert at draft trust to populate it.

### Full-complexity example (every DDL feature)

```yaml
# schema.yaml v5 — full DDL coverage, token-optimized
version: 5
engine: sqlite
db: workspace.db

customers:
  desc: Customer profiles with PII
  prov: true
  sens: true
  cols:
    id: pk
    email: text!
    name: text
    phone: text~
    tier: text=standard
    metadata: json
    created_at: int~
  idx:
    - [tier, created_at]
    - email
  rel:
    orders: orders.customer_id = customers.id
    subscriptions: subscriptions.customer_id = customers.id
  chk:
    - "tier IN ('standard','premium','enterprise')"
    - "email LIKE '%@%'"

orders:
  desc: Transactional order records
  prov: true
  cols:
    id: pk
    ref: text!
    customer_id: int ref=customers.id
    status: text=pending
    total_cents: int
    discount_cents: int=0
    tax_cents: int=0
    currency: text=USD
    notes: text
    metadata: json
    created_at: int~
  idx:
    - [customer_id, status]
    - [status, created_at]
    - ref
  rel:
    customer: customers.id = orders.customer_id
    items: order_items.order_id = orders.id
    payments: payments.order_id = orders.id
  chk:
    - "total_cents >= 0"
    - "discount_cents <= total_cents"
    - "tax_cents >= 0"
  trig:
    validate_total:
      when: before insert
      sql: |
        SELECT RAISE(ABORT, 'total mismatch')
        WHERE NEW.total_cents != (
          SELECT COALESCE(SUM(unit_price_cents * quantity), 0)
          FROM order_items WHERE order_id = NEW.id
        )

order_items:
  desc: Line items per order
  prov: true
  imm_rows: true
  cols:
    id: pk
    order_id: int ref=orders.id
    sku: text ref=inventory.sku
    quantity: int
    unit_price_cents: int
    metadata: json
  idx:
    - [order_id]
    - [sku]
  chk:
    - "quantity > 0"
    - "unit_price_cents >= 0"

inventory:
  desc: SKU stock levels
  prov: true
  cols:
    id: pk
    sku: text!~
    name: text
    stock: int=0
    reorder_point: int=10
    warehouse: text=DEFAULT
    last_restocked: int
  idx:
    - [warehouse, stock]
    - sku
  chk:
    - "stock >= 0"
    - "reorder_point >= 0"

payments:
  desc: Payment transactions
  prov: true
  sens: true
  cols:
    id: pk
    order_id: int ref=orders.id
    provider: text
    provider_ref: text!
    amount_cents: int
    status: text=pending
    raw_response: json mask=true
    created_at: int~
  idx:
    - [order_id]
    - provider_ref
  chk:
    - "amount_cents > 0"
    - "status IN ('pending','completed','failed','refunded')"

subscriptions:
  desc: Recurring billing subscriptions
  prov: true
  cols:
    id: pk
    customer_id: int ref=customers.id
    plan: text
    interval: text=monthly
    amount_cents: int
    active: int=1
    next_billing: int
    created_at: int~
  idx:
    - [customer_id, active]
    - [next_billing]
  chk:
    - "interval IN ('monthly','yearly')"
    - "amount_cents > 0"

secrets:
  desc: Kernel-managed secrets
  sens: true
  cols:
    id: pk
    name: text!~
    value: text mask=true
    scope: text=global
    expires_at: int
  idx:
    - name
    - [scope, expires_at]

agents:
  desc: Registered agent identities
  cols:
    id: text pk
    name: text!
    harness: text
    principal: text!
    status: text=active
  imm_cols: [id, principal]
  idx:
    - principal
    - status

_audit:
  desc: Audit mirror (kernel-managed)
  sys: true
  cols:
    id: pk
    event: text
    ts: int
    env: text
    agent: text
    session: text
    principal: text
    capability: text
    intent: text
    outcome: text
    duration_ms: int
    payload: json mask=true
  idx:
    - [event, ts]
    - [agent, ts]
    - [capability, outcome]

_api_quota:
  desc: Live external API quota state (kernel-managed, updated from response headers)
  sys: true
  cols:
    id: pk
    provider: text!
    scope_key: text                              # api_key hash or endpoint path
    env: text!
    limit_total: int
    remaining: int
    reset_at: int                                # unix epoch
    retry_after_s: int
    last_updated: int
    last_op: text                                # op_id that updated this row
  idx:
    - [provider, env]
    - [provider, scope_key, env]
  chk:
    - "remaining >= -1"                          # -1 = unknown (no headers received yet)

_api_catalog:
  desc: Full API verb catalog — all imported verbs, all states (kernel-managed)
  sys: true
  imm_cols: [provider, verb]
  cols:
    id: pk
    provider: text!
    verb: text!
    method: text
    path: text
    params_schema: json
    idempotent: int=0
    cost_class: text=read
    state: text=dormant
    trust: text=draft
    description: text
    activated_at: int
    activated_by: text
    retired_at: int
    spec_hash: text
    synced_at: int
    version: int=1
  idx:
    - [provider, state]
    - [provider, verb]
    - [state, trust]
    - [description]
  chk:
    - "state IN ('dormant','active','deprecated','retired')"
    - "trust IN ('draft','reviewed','pinned')"
    - "cost_class IN ('read','write')"
    - "method IN ('GET','POST','PUT','DELETE','PATCH')"

views:
  pending_orders:
    desc: Orders awaiting fulfillment
    exposes: [orders, customers]
    sql: |
      SELECT o.id, o.ref, o.total_cents, c.name as customer_name
      FROM orders o
      JOIN customers c ON o.customer_id = c.id
      WHERE o.status = 'pending'
      ORDER BY o.created_at DESC

  low_stock_alerts:
    desc: Inventory below reorder point
    exposes: [inventory]
    sql: |
      SELECT sku, name, stock, reorder_point, warehouse
      FROM inventory
      WHERE stock <= reorder_point AND stock > 0

  customer_lifetime_value:
    desc: Aggregated spend per customer
    exposes: [customers, orders, payments]
    scoped: principal
    sql: |
      SELECT c.id, c.name, SUM(p.amount_cents) as total_spent
      FROM customers c
      JOIN orders o ON o.customer_id = c.id
      JOIN payments p ON p.order_id = o.id
      WHERE p.status = 'completed' AND c.id = :principal
      GROUP BY c.id
```

### Why YAML and not raw `schema.sql`

| Need | SQL DDL | schema.yaml |
|---|---|---|
| `mask=true` (redact in results/audit) | no concept | ✅ |
| `~` / `immutable` (policy input) | only via triggers | ✅ |
| `desc` (search index, explain output) | comments, unstructured | ✅ |
| `rel` (traversal search) | FK = integrity only | ✅ |
| `prov` / `system` columns | no concept | ✅ |
| Token-optimized for agents | verbose | ✅ ~60% savings |
| Single source of truth | ✅ if sole artifact | ✅ kernel compiles it |

### What the rule layer governs per-column vs what SQLite validates

| Flag | Purpose | Enforcement Layer |
|---|---|---|
| `type` | Storage type | SQLite type affinity |
| `pk` | Primary key | SQLite engine |
| `!` (unique) | Uniqueness | SQLite UNIQUE constraint |
| `~` (immutable) | Write-once | **Authorizer denies UPDATE on column** |
| `=val` (default) | Default value | SQLite DEFAULT |
| `ref=` | Foreign key | SQLite FK constraint |
| `mask=true` | Redact on read | **Authorizer + audit redaction** |
| `system: true` | Kernel auto-fills | **Authorizer denies agent writes** |
| `chk:` | Content validation | **SQLite CHECK constraint** |

**Shape = capcli. Content = SQLite. No overlap. No dual enforcement.**

---

## 4. Schema Evolution — the explicit lifecycle

The agent builds the world. The kernel governs its growth. This is not free-form `ALTER TABLE` — it is a governed pipeline.

### Step-by-step: agent adds a column

```
1. AGENT EDITS schema.yaml (native fs, dev worktree)
   → adds: discount_cents: int=0
   → bumps: version: 4 → 5

2. AGENT PREVIEW
   capcli rule apply --type schema --dry-run --env dev
   → output: exact DDL, snapshot id, reversibility confirmation
   → exit 0 (plan valid)

3. KERNEL GATES
   capcli rule apply --type schema --env dev
   → policy check: alter.require_trust = reviewed
   → agent trust: draft
   → exit 2: "schema changes require reviewed trust"

4. HUMAN/CI REVIEWS
   → reads the diff (version 4 → 5)
   → sees: ALTER TABLE orders ADD COLUMN discount_cents INTEGER DEFAULT 0
   → approves

5. HUMAN SHIPS
   capcli routine ship schema_v5 --to reviewed --reason "add discount column"

6. AGENT APPLIES
   capcli rule apply --type schema --env dev --intent "add discount_cents to orders"
   → snapshot taken
   → DDL executed in one txn
   → schema_version bumped
   → auto-committed to git
   → audit event written

7. PROD (same pattern, stricter gate)
   → human merges dev branch into prod
   → capcli env use prod
   → capcli rule apply --type schema --intent "add discount_cents to orders"
   → applied with prod-level confirmations
```

### What the agent CANNOT do

| Temptation | Result |
|---|---|
| `db.exec("ALTER TABLE orders ADD COLUMN hack TEXT")` | **exit 2** — `alter.require_trust: reviewed` |
| `db.exec("DROP TABLE orders")` | **exit 2** — `drop: deny` (authorizer, unconditional) |
| Edit `workspace.db` directly | **exit 4** — file perms (chmod 600, daemon-owned) |
| Skip `schema.yaml`, hand-write DDL | **exit 3** — `rule diff` alarm, `sys doctor` refuses boot |
| Apply schema to `prod` without merge | **exit 2** — env overlay denies cross-world DDL |
| Delete a column without snapshot | **exit 2** — migration is snapshot-first, always |

### Migration rules

- **Forward-only.** No down-migrations. Snapshots are the rollback.
- **Snapshot-first.** Every migration takes a WAL-consistent snapshot before DDL.
- **Explicit-SQL-shown.** `--dry-run` prints the exact DDL. No surprises.
- **One transaction.** Failure → auto-restore from snapshot.
- **Auto-commit.** Every successful migration is a git commit.
- **Version-locked.** `schema_version` must match `policy.yaml` + `governance.yaml` or boot is refused.
- **Onboarding is migration.** The first `rule apply` from intent is version 0→1. It follows the exact same snapshot-first, explicit-SQL-shown, one-transaction pipeline as every subsequent migration. No special fast-path for genesis.

---

## 5. Validation — five gates, zero trust

Validation isn't a single step — it's a layered defense that runs at every boundary.

### Gate 1: YAML Syntax (parse-time)
- Valid YAML structure, no duplicate keys
- Shorthand expansion succeeds
- All required fields present (`version`, `engine`, `db`)
- **Fail → exit 3, cites line + column**

### Gate 2: Semantic Validation (compile-time)
- All `ref=` targets exist and types match
- All `rel:` targets exist and columns match types
- All `idx:` columns exist in parent table
- All `chk:` expressions parse as valid SQL WHERE clauses
- All `trig:` SQL bodies parse without error
- All `views.sql` parse and only reference tables in `exposes:`
- `scoped: principal` views contain `:principal` bind param
- `mask=true` only on `text`/`json` columns
- `imm_cols` entries exist in table
- No circular `ref=` chains
- **Fail → exit 3, cites exact rule + location**

### Gate 3: Policy Lock (boot-time)
- `schema.version` == `policy.schema_version` == `governance.schema_version`
- Mismatch → **refuse boot, exit 5**

### Gate 4: Live Drift Detection (runtime)
- `capcli sys doctor` compares compiled YAML vs live DB via PRAGMAs
- Any divergence → **refuse to serve, exit 4, cites exact drift**

### Gate 5: Migration Safety (apply-time)
- Snapshot taken before DDL
- DDL executes in test txn against snapshot
- Rollback verified, idempotency checked
- **Fail → auto-restore snapshot, exit 4**

### What validation catches

| Error | Gate | Message |
|---|---|---|
| `ref=nonexistent_table.id` | 2 | `orders.customer_id references missing table` |
| `idx: [missing_col]` | 2 | `index on orders.missing_col: column does not exist` |
| `mask=true` on `int` column | 2 | `payments.amount_cents: mask only valid on text/json` |
| View references unlisted table | 2 | `pending_orders.sql touches 'inventory' not in exposes` |
| Schema v5 + Policy v4 | 3 | `version mismatch: refusing boot` |
| Live DB has extra column | 4 | `drift: orders.hack_column exists in DB but not schema.yaml` |
| FK type mismatch | 2 | `orders.customer_id (int) refs customers.id (text)` |
| Circular ref | 2 | `circular reference: a→b→c→a` |
| Trigger SQL syntax error | 2 | `orders.validate_total: syntax error` |

---

## 6. Two-Layer Policy (DB-specific)

### Layer 1 — `sqlite3_set_authorizer`

Engine-enforced at prepare-time. Bypass-proof. Granularity: **action × table × column.**

### Layer 2 — SQL AST

Pre-prepare semantic gate. Granularity: **statement shape, blast radius, parameters, intent.**

```
SQL text
  → intent check (writes without intent → deny)
  → AST parse (reject multi-statement, unparseable)
  → AST rules (require_where, require_limit, max_rows, patterns)
  → sqlite3_set_authorizer (table/column/action, ATTACH, PRAGMA, functions)
  → execute
  → audit event
```

**Layer boundaries and completeness:**
The two layers cover different, non-overlapping surfaces. The authorizer checks action × table × column. The AST checks WHERE, LIMIT, blast radius, patterns. A parser bug in node-sql-parser does NOT get caught by the authorizer because the authorizer doesn't check what the parser checks.

Therefore, a third verification exists between them:

### Layer 1.5: Prepare-time cross-check
After AST passes but before execution, run `sqlite3_prepare_v2` in a dry-run transaction. SQLite's own C parser is the ground truth.
- If prepare fails → deny.
- If statement type from prepare contradicts AST classification (e.g., AST says SELECT but prepare sees UPDATE opcodes) → deny.
- node-sql-parser version is pinned and fuzz-tested against SQLite's test corpus. Parse failure = deny, never pass-through.
- Every parse logged as `ast_parse: {ok, node_count, statement_type}` in the audit event.
- For write statements: cross-check AST classification against SQLite `EXPLAIN` output. If AST says read-only but `EXPLAIN` shows `OpenWrite` → deny.

**Asymmetry:** authorizer = default-deny floor (bypass-proof). AST = expressive ceiling (semantic). Prepare-time = ground-truth cross-check. Bypass requires all three to fail simultaneously.

### DB-relevant policy excerpt

```yaml
authorizer:
  tables:
    orders:     { allow: [read, insert, update, delete], deny_columns_write: [id, created_at, created_by, modified_by] }
    customers:  { allow: [read, insert, update, delete], deny_columns_write: [id, created_by, modified_by] }
    inventory:  { allow: [read, insert, update], deny_columns_write: [id, sku, created_by, modified_by] }
    secrets:    { allow: [read], mask_columns: [value] }
    agents:     { allow: [read] }
  global:
    attach: deny
    pragma: [query_only, foreign_keys]
    functions: { deny: [load_extension, writefile, readfile] }
    drop: deny
    alter: { require_trust: reviewed }

query:
  multi_statement: deny
  writes_require_intent: true
  update_delete: { require_where: true, require_limit: true, max_limit: 1000 }
  select:        { max_limit: 10000 }
  bulk:          { require_pre_count: true, require_trust_for_bulk: reviewed }
```

## Implementation Binding

The two enforcement layers map to two runtimes:

| Layer | Runtime | Binding | Bypass-proof? |
|---|---|---|---|
| L1: Authorizer floor | Rust (rusqlite via napi-rs) | `conn.authorizer(Some(closure))` | Yes — C-level, runs inside `sqlite3_prepare_v2` |
| L2: AST ceiling | TypeScript | `node-sql-parser` (sqlite dialect) | No — but runs before L1; rejected SQL never reaches prepare |

policy.yaml's `authorizer` section compiles into Rust match arms at boot:

```rust
conn.authorizer(Some(move |action: AuthAction| {
    match action {
        AuthAction::Attach { .. } => AuthResult::Deny,
        AuthAction::DropTable { .. } => AuthResult::Deny,
        AuthAction::Update { table_name, column_name, .. } => {
            // compiled from policy.yaml authorizer.tables
            if deny_columns_write.contains(&column_name) { AuthResult::Deny }
            else { AuthResult::Ok }
        }
        _ => AuthResult::Ok,
    }
}));
```

The agent never touches SQLite directly. `workspace.db` is `chmod 600`,
owned by the daemon user. All access flows through the kernel, through
both layers, in order. See `stack.md` for full binding details.

---

## 7. Raw SQL Rules

Raw SQL is **allowed by default** — it's the exploration layer that feeds the learning loop.

| Rule | Enforcement |
|---|---|
| Parameterized only — no string interpolation | API rejects structurally |
| Reads run free | authorizer scope + `max_limit` |
| `UPDATE`/`DELETE` need `WHERE` | AST |
| `UPDATE`/`DELETE` need `LIMIT` | AST |
| Writes need an **intent** | AST, deny by default |
| Writes run in explicit transactions | kernel wraps; SDK requires `ctx.db.txn()` |
| DDL gated | `require_trust: reviewed` |
| `ATTACH` / write-PRAGMAs | authorizer, unconditional deny |

```python
# ✅
ctx.db.execute(
    "UPDATE orders SET status = :s WHERE id = :id LIMIT 1",
    {"s": "fulfilled", "id": 7},
    intent="mark ORD-8842 fulfilled")

# ❌ rejected: interpolation
ctx.db.execute(f"UPDATE orders SET status = '{s}' WHERE id = {id}")

# ❌ rejected: no WHERE, no LIMIT
ctx.db.execute("UPDATE orders SET archived = 1")
```

**Raw SQL is exploration. Routines are exploitation.** Kill raw SQL and the learning loop never starts.

---

## 8. Bulk Strategy

Fewer *agent* calls, many *kernel* operations. Python loops + `require_limit`:

```python
while True:
    res = ctx.db.execute(
        "UPDATE orders SET archived = 1 WHERE status = 'completed' AND archived = 0 LIMIT 500",
        {},
        intent="archive completed orders")
    if res.changes < 500:
        break
```

- Each chunk = own txn, own audit event, resumable
- `capcli db query --count` = mandatory pre-flight for mass ops
- Bulk writes require trust ≥ `reviewed`

---

## 9. Command Surface — `capcli db`

```bash
capcli db query <sql> [-p k=v]... [--limit N] [--count] [--json]
capcli db exec  <sql> [-p k=v]... --intent "..." [--dry-run]
capcli db lock <table>:<ref> --ttl 10m --reason "..."
capcli db unlock <target>
capcli db schema [--table]
capcli db snapshot | restore <id> | dump
```

Exit codes: `0` ok · `2` policy-denied · `3` validation · `4` runtime · `5` audit-failed.
`db count` is dead. Use `db query --count` or rely on AST-enforced bulk pre-flights.

---

## 10. The `ctx.db` SDK

```python
ctx.db.query(sql, params) -> list[dict]        # reads; max_limit enforced
ctx.db.execute(sql, params, intent) -> Result  # writes; WHERE+LIMIT+intent enforced
ctx.db.txn() -> context manager                # required wrapper for writes
ctx.db.lock(target, ttl) -> Claim              # cross-agent coordination (replaces ctx.claim)
```

- No raw connection object exposed
- No `executescript`, no multi-statement
- Results are plain dicts; `mask` columns arrive redacted
- `system: true` columns auto-filled by kernel
- Large results stay in routine scope

---

## 11. Identity & Provenance

```
principal → agent → session → op, with caused_by linking the causal DAG
```

- Agent IDs kernel-issued, socket-bound, never self-declared
- `prov: true` tables get `created_by`/`modified_by` auto-filled
- Claims: lease-based exclusivity with TTL
- Cross-agent routine calls require callee ≥ `reviewed`

---

## 12. Intent Chain

```
session goal → routine intent → op intent
```

- Leaf ops inherit from routine, routines from session
- Anti-junk: min length, boilerplate blacklist, deny by default
- `--intent` = purpose; `--reason` = justification for threshold crossings

---

## 13. Audit Mirror & Primitive Views

Read-only `_audit` mirror inside workspace.db. Deterministic views:

```sql
-- routine_fingerprints: actual primitive sequence per version
-- primitive_failures: which LEAF fails
-- primitive_cost: duration/spend attribution per leaf
-- shared_subsequences: common primitive n-grams → merge candidates
```

All GROUP BYs. Kernel counts at leaf depth; harness reasons over it.

---

## 14. Durability & Recovery

| Tier | Artifact | Mechanism |
|---|---|---|
| Point-in-time | `db snapshot` | WAL-consistent copy + hash |
| Committed history | `world.sql` | deterministic dump, git-tracked |
| Offsite truth | `sys backup --push` | interval + event-triggered |

- `sys recover <commit>` restores full world-state from git
- `sys audit replay` re-applies events through current policy
- Worst case: `git clone` + `sys recover` → world restored

---

## 15. Introspection

- **YAML → DB**: one-way generation
- **DB → diff**: PRAGMAs, structured comparison
- **DB → YAML**: `capcli rule show --type schema` bootstraps from live DB

---

## 16. Audit Event Format

```json
{
  "event": "db.exec",
  "ts": "2026-09-08T14:03:11Z",
  "env": "prod",
  "stage": "live",
  "agent": "agt_7f3k",
  "principal": "user:alice",
  "caused_by": "op_000119",
  "intent": "mark ORD-8842 fulfilled",
  "capability": "db.exec",
  "sql": "UPDATE orders SET status = :s WHERE id = :id LIMIT 1",
  "params": { "s": "fulfilled", "id": 7 },
  "policy": { "decision": "allow", "rules": ["require_where", "require_limit"] },
  "rows_affected": 1,
  "result_hash": "sha256:...",
  "duration_ms": 4
}
```

```json
{
  "event": "api.sync",
  "ts": "2026-09-12T10:00:00Z",
  "provider": "stripe",
  "source_url": "https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.json",
  "spec_hash": "sha256:b7c1...",
  "added": 3,
  "removed": 1,
  "changed": 2,
  "unchanged": 394,
  "env": "dev",
  "agent": "agt_7f3k",
  "principal": "user:alice",
  "duration_ms": 1240
}
```

```json
{
  "event": "api.activate",
  "ts": "2026-09-12T10:05:00Z",
  "provider": "stripe",
  "verb": "refund_charge",
  "state_from": "dormant",
  "state_to": "active",
  "trust": "draft",
  "intent": "refund workflow needs charge refund capability",
  "env": "dev",
  "agent": "agt_7f3k",
  "principal": "user:alice"
}

Schema migration events include `from_version`, `to_version`, `ddl`, `snapshot`.

---

## 17. Environment Integration

- Each env = worktree with own `workspace.db`
- `env new sim --seed prod` → snapshot + auto-mask sensitive columns
- Schema migrations travel dev → sim → prod via git merge

---

## 18. Anti-Decisions

- **No ORM.** No SQLAlchemy/Drizzle/Prisma. Hallucination bait.
- **No query-builder APIs.** Accidental ORM.
- **No hand-edited DDL.** schema.yaml is SSOT.
- **No free-form schema changes.** Agent authors YAML; kernel gates application.
- **No `validate=` keywords.** CHECK constraints are validation. One enforcement point.
- **No DDL parser.** PRAGMAs + one-way generation.
- **No down-migrations.** Snapshots are rollback.
- **No direct connection exposure.** Routines get `ctx.db`, never `sqlite3`.
- **No self-declared identity.** Kernel-issued, socket-proven.
- **No pre-defined schemas.** Agent builds the world. Capcli governs its growth.

---

## 19. Invariants

1. Every DB effect passes authorizer + AST. No bypass path exists.
2. Every write is transactional, audited, carries intent chain.
3. Every `UPDATE`/`DELETE` has `WHERE` and `LIMIT` — physics.
4. Schema and policy are version-locked; mismatch = no boot.
5. Agent authors `schema.yaml`; kernel compiles, gates, applies. DDL never hand-written.
6. Content validation = CHECK constraints. Shape governance = capcli flags. No overlap.
7. Secrets masked in every surface — results, audit, explain.
8. DB file is daemon-owned; Unix permissions are the outer wall.
9. Every row on provenance tables answers *who changed it*.
10. Where capcli can't gate, it recovers: world.sql + audit-in-git.
11. Audit mirror is read-only; analysis at primitive depth via deterministic views.
12. Schema evolution is forward-only, snapshot-first, human-gated, fully audited.
13. Five validation gates; any failure = no execution. No degraded mode.

---

## The One-Liner

> **capcli-db: the agent builds the world in dense YAML, the kernel holds the leash with five validation gates and two enforcement layers, CHECK validates content while policy governs shape, raw SQL flows through an unbreakable authorizer, and the whole world is recoverable from git history.**