# capcli-db.architecture.md *(final v3 — primitive-aware, mirror views integrated)*

> The database layer of capcli: **SQLite as world-state, policy as physics, raw SQL as the language.**

---

## 1. Scope & Convictions

capcli-db governs every effect on `workspace.db`. Four convictions:

1. **SQLite is not storage behind an app — it is the persistent world-state.**
2. **Raw SQL is the language.** No ORM, no query builder, no Drizzle. Agents know SQL cold; they hallucinate ORM syntax.
3. **The agent is never trusted.** Enforcement lives in the SQLite engine and the kernel gate — never in prompts.
4. **One source of truth: `schema.yaml`.** SQL DDL is what it compiles to, never hand-edited.

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

## 3. schema.yaml — the contract

Declarative structure + the semantic layer SQL cannot express:

```yaml
version: 12                          # lock with policy.yaml or boot refused
engine: sqlite
database: workspace.db

tables:
  entities:
    description: "Core objects — users, orders, docs."
    provenance: true                 # kernel auto-fills created_by / modified_by
    columns:
      id:          { type: integer, pk: true, autoincrement: true }
      type:        { type: text, required: true, description: "user|order|doc" }
      ref:         { type: text, unique: true }
      status:      { type: text, default: "active" }
      metadata:    { type: json }
      created_at:  { type: integer, immutable: true }
      created_by:  { type: text, system: true }    # agent id — auto-filled
      modified_by: { type: text, system: true }    # agent id — auto-filled
    indexes:
      - on: [type, status]
    relations:
      edges_out: { to: edges, on: "edges.src = entities.id" }

  edges:
    description: "Typed relationships. Append-only."
    columns:
      id:   { type: integer, pk: true }
      src:  { type: integer, references: entities.id }
      rel:  { type: text }
      dst:  { type: integer, references: entities.id }
      created_by: { type: text, system: true }
    constraints: ["CHECK (src != dst)"]
    immutable_rows: true

  secrets:
    sensitive: true
    columns:
      id:    { type: integer, pk: true }
      name:  { type: text, unique: true }
      value: { type: text, mask: true }

  agents:                            # identity is world-state too
    description: "Kernel-registered agent identities."
    columns:
      id:         { type: text, pk: true }         # agt_7f3k
      name:       { type: text, unique: true }
      harness:    { type: text }
      principal:  { type: text, required: true }   # user:alice
      status:     { type: text, default: "active" }
    immutable_columns: [id, principal]

views:
  active_orders:
    description: "Orders not yet refunded."
    sql: |
      SELECT id, ref, status FROM entities
      WHERE type = 'order' AND status != 'refunded'
```

Why YAML and not raw `schema.sql`:

| Need | SQL DDL | schema.yaml |
|---|---|---|
| `mask: true` (redact in results/audit) | no concept | ✅ |
| `immutable` (policy input) | only via triggers | ✅ |
| `description` (search index, explain output) | comments, unstructured | ✅ |
| `relations` (traversal search) | FK = integrity only | ✅ |
| `provenance` / `system` columns | no concept | ✅ |
| Single source of truth | ✅ if sole artifact | ✅ kernel compiles it |

**The rule:** schema.yaml is justified because the kernel *applies* it. DDL is generated output; hand-editing the DB triggers `schema diff` alarms and `sys doctor` refusal.

---

## 4. Two-Layer Policy (DB-specific)

### Layer 1 — `sqlite3_set_authorizer` (via `node:sqlite`)

Engine-enforced at prepare-time. Bypass-proof even if TS code has bugs. Bugs fail toward denial.

Granularity: **action × table × column.**

### Layer 2 — SQL AST (node-sql-parser)

Pre-prepare semantic gate: WHERE clauses, LIMIT presence, patterns, values, **intent presence on writes**.

Granularity: **statement shape, blast radius, parameters.**

```
SQL text
  → intent check (writes without intent → deny)
  → AST parse (reject multi-statement, unparseable)
  → AST rules (require_where, require_limit, max_rows, patterns)
  → sqlite3_set_authorizer (table/column/action, ATTACH, PRAGMA, functions)
  → execute
  → audit event (agent, session, principal, caused_by, intent chain)
```

**The asymmetry:** authorizer = default-deny floor that can't be bypassed. AST = expressive ceiling. Bypass requires both to fail.

### DB-relevant policy excerpt

```yaml
authorizer:
  tables:
    entities: { allow: [read, insert, update, delete], deny_columns_write: [id, created_at, created_by, modified_by] }
    edges:    { allow: [read, insert] }               # immutable rows
    secrets:  { allow: [read], mask_columns: [value] }
    agents:   { allow: [read] }                       # identity managed by kernel commands only
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

---

## 5. Raw SQL Rules

Raw SQL is **allowed by default** — it's the exploration layer that feeds the learning loop. Guardrails, not prohibitions:

| Rule | Enforcement |
|---|---|
| Parameterized only — no string interpolation | API rejects structurally |
| Reads run free | authorizer scope + `max_limit` |
| `UPDATE`/`DELETE` need `WHERE` | AST |
| `UPDATE`/`DELETE` need `LIMIT` | AST |
| Writes need an **intent** (inherited chain accepted) | AST, deny by default |
| Writes run in explicit transactions | kernel wraps `db exec`; SDK requires `ctx.db.txn()` |
| DDL gated | `require_trust: reviewed` |
| `ATTACH` / write-PRAGMAs | authorizer, unconditional deny |

```python
# ✅
ctx.db.execute(
    "UPDATE entities SET status = :s WHERE id = :id LIMIT 1",
    {"s": "refunded", "id": 7},
    intent="mark ORD-8842 refunded")

# ❌ rejected: interpolation
ctx.db.execute(f"UPDATE entities SET status = '{s}' WHERE id = {id}")

# ❌ rejected: no WHERE, no LIMIT
ctx.db.execute("UPDATE entities SET archived = 1")
```

**Raw SQL is exploration. Routines are exploitation.** Kill raw SQL and the learning loop never starts.

---

## 6. Bulk Strategy

Agents batch for token economy. Answer: fewer *agent* calls, many *kernel* operations. No `bulk_update()` APIs (that's accidental ORM) — Python loops + `require_limit`:

```python
while True:
    res = ctx.db.execute(
        "UPDATE entities SET archived = 1 WHERE type = :t AND archived = 0 LIMIT 500",
        {"t": "temp"},
        intent="archive stale temp entities")
    if res.changes < 500:
        break
```

- Each chunk = own txn, own audit event, resumable by natural WHERE drift
- `capcli db count <table> --where` = mandatory pre-flight for mass ops
- `INSERT ... SELECT` (unchunkable inside SQLite): estimate-before-execute via `count`
- Bulk writes require trust ≥ `reviewed`; exceeding caps requires `--reason` justification

---

## 7. Command Surface — `capcli db`

```bash
capcli db query <sql> [-p k=v]... [--limit N] [--json]
capcli db exec  <sql> [-p k=v]... --intent "..." [--dry-run]
capcli db count <table> [--where <sql>]
capcli db schema [--table]
capcli db snapshot
capcli db restore <snapshot-id> [--dry-run]
capcli db dump                          # → world.sql (deterministic, git-committed)
capcli claim <table>:<ref> --ttl 10m --reason "..."   # coordination lease
```

Universal flags apply: `--dry-run`, `--json`, `--intent`, `--as`, `--by <agent-id>`. Exit codes: `0` ok · `2` policy-denied · `3` validation · `4` runtime · `5` audit-failed.

---

## 8. The `ctx.db` SDK (routine-side surface)

```python
ctx.db.query(sql, params) -> list[dict]        # reads; max_limit enforced
ctx.db.execute(sql, params, intent) -> Result  # writes; WHERE+LIMIT+intent enforced
ctx.db.txn() -> context manager                # required wrapper for writes
ctx.db.count(table, where) -> int              # pre-flight
ctx.claim(target, ttl) -> Claim                # cross-agent coordination
```

Constraints inside the SDK:

- No raw connection object exposed — routines can never reach `sqlite3` directly
- No `executescript`, no multi-statement
- Results are plain dicts; `mask` columns arrive redacted
- `system: true` columns are auto-filled by the kernel (provenance) — routines cannot set or spoof them
- Large results stay in routine scope — only summaries cross to the model

---

## 9. Identity & Provenance (multi-agent)

Every DB effect carries the full spine:

```
principal → agent → session → op, with caused_by linking the causal DAG
```

- **Agent IDs are kernel-issued** (`capcli agent register`), stored in the `agents` table, bound to socket credentials — never self-declared
- **Row-level provenance**: `provenance: true` tables get `created_by` / `modified_by` auto-filled with the acting agent id. Six months later the data itself answers "who did this"
- **Claims**: lease-based exclusivity with TTL so dead agents can't deadlock the world; conflicting claims return the holder's id
- **Cross-agent routine calls** require the callee to be ≥ `reviewed` — one agent's draft never becomes another's dependency

---

## 10. Intent Chain

Writes require intent; the chain inherits downward:

```
session goal → routine intent → op intent
```

- Leaf ops inherit from routine, routines from session; every audit event records the full chain
- Anti-junk: min length, boilerplate blacklist, deny by default
- `--intent` = purpose (why this action); `--reason` = justification (only for threshold crossings)

---

## 11. Audit Mirror & Primitive Views 🔬

The JSONL stream is canonical (append-only, git-backed, tamper-evident), but the kernel maintains a **read-only mirror inside workspace.db** so the agent mines its own history with SQL:

```yaml
tables:
  _audit:
    system: true
    description: "Mirror of the audit stream. Read-only."
    readonly_grant: true
```

Beyond raw events, the mirror hosts **primitive-aware views** powering lifecycle, consolidation, and forensics:

```sql
-- view: routine_fingerprints
-- actual primitive sequence executed per routine version
SELECT routine_version, seq, capability, target, count(*) n
FROM _audit WHERE event IN ('db.exec','db.query','api.call')
GROUP BY routine_version, seq, capability, target;

-- view: primitive_failures
-- which LEAF fails, not just which routine
SELECT routine, capability, target, error, count(*) failures
FROM _audit WHERE outcome != 'success' AND event != 'routine.run'
GROUP BY routine, capability, target, error;

-- view: primitive_cost
-- duration and spend attribution per leaf
SELECT routine, capability, target,
       avg(duration_ms) p50, max(duration_ms) p95
FROM _audit GROUP BY routine, capability, target;

-- view: shared_subsequences
-- common primitive n-grams across routines → merge candidates
SELECT seq_pattern, count(DISTINCT routine_version) routines_seen
FROM routine_fingerprints GROUP BY seq_pattern HAVING routines_seen > 1;
```

All deterministic GROUP BYs. The kernel counts at leaf depth; the harness reasons over it. These views power `consolidate report`, `routine stats --deep`, and `audit trace`.

---

## 12. Durability & Recovery

Three tiers, layered:

| Tier | Artifact | Mechanism |
|---|---|---|
| Point-in-time | `db snapshot` | WAL-consistent copy + hash + schema_version |
| Committed history | `db dump` → **world.sql** | deterministic text dump, git-tracked; data history becomes human-readable diffs |
| Offsite truth | `sys commit --push` | interval + event-triggered (promote, migrate, restore) |

- `db restore` = snapshot-first recovery; `--dry-run` shows the plan
- `sys recover <commit>` = restore full world-state (db + routines + policy + audit) from git history
- `audit replay` reconstructs state: events re-applied through the same gate, **current** policy enforced
- Every event carries `result_hash` — drift detection when replaying onto a diverged world
- **Worst case** (harness wipes everything): `git clone` + `capcli sys recover` → world restored, audit spine intact

---

## 13. Migrations — deliberately dumb

No auto-magic. Forward-only, snapshot-first, explicit-SQL-shown:

```
capcli schema migrate [--dry-run]
  1. snapshot workspace.db
  2. diff schema.yaml version N → N+1
  3. print the exact DDL statements
  4. --apply runs them in one txn; failure → auto-restore
  5. auto-commit the transition
```

Down-migrations, reorder-safe alters, dialect abstraction: **not built.** SQLite + snapshots makes the simple version nearly bulletproof.

---

## 14. Introspection — no DDL parser, ever

- **YAML → DB**: one-way generation. Generating SQL is trivial; parsing is the hard part we skip
- **DB → diff**: `PRAGMA table_info`, `PRAGMA foreign_key_list`, `PRAGMA index_list` — structured vs structured
- **DB → YAML**: `capcli schema import <db>` bootstraps from a live DB via PRAGMAs — the zero-to-value adoption path

---

## 15. Audit Event Format (DB ops)

```json
{
  "event": "db.exec",
  "ts": "2026-09-08T14:03:11Z",
  "env": "prod",
  "stage": "live",
  "agent": "agt_7f3k",
  "session": "ses_a9",
  "principal": "user:alice",
  "caused_by": "op_000119",
  "intent": "mark ORD-8842 refunded",
  "intent_chain": ["process today's refund queue", "refund_and_archive", "mark ORD-8842 refunded"],
  "capability": "db.exec",
  "sql": "UPDATE entities SET status = :s WHERE id = :id LIMIT 1",
  "params": { "s": "refunded", "id": 7 },
  "policy": { "decision": "allow", "rules": ["require_where", "require_limit", "intent_present"] },
  "rows_affected": 1,
  "result_hash": "sha256:...",
  "duration_ms": 4,
  "idempotency_key": "..."
}
```

One command = one event. Three questions answered on every effect: **who, what, why.** Missing any → it doesn't run.

---

## 16. Environment Integration

Each `capcli env` is a worktree with its own `workspace.db`:

- `env new sim --seed prod` → snapshot prod → restore into sim → **auto-mask `sensitive` tables/columns**
- Sim replays prod audit against forked state: real traffic, zero prod secrets
- Prod's DB is never reachable from sim — different files, different worktrees, different sockets

---

## 17. Anti-Decisions

- **No ORM.** No SQLAlchemy/Drizzle/Prisma. ORM syntax is hallucination bait; ORMs compile to SQL anyway — a middleman before the same authorizer check
- **No query-builder APIs.** `bulk_update()`, `cursor()`, `find()` = accidental ORM. Raw SQL + policy covers it
- **No hand-edited DDL.** schema.yaml is the sole source; `sys doctor` refuses drift
- **No DDL parser.** PRAGMAs + one-way generation
- **No down-migrations.** Snapshots are the rollback
- **No direct connection exposure.** Routines get `ctx.db`, never `sqlite3`
- **No self-declared identity.** Agent ids are kernel-issued and socket-proven
- **No raw audit file reads.** Harness could `cat audit/*.jsonl`, but the mirror is the governed path — redaction guaranteed, token cost capped

---

## 18. Invariants

1. Every DB effect passes authorizer + AST. No exceptions, no bypass path exists
2. Every write is transactional, audited, and carries an intent chain; unauditable write = no write
3. Every `UPDATE`/`DELETE` has `WHERE` and `LIMIT` — physics, not policy
4. Schema and policy are version-locked; mismatch = no boot
5. Secrets-table reads are masked in every surface — results, audit, explain
6. The DB file is daemon-owned; Unix permissions are the outer wall
7. Every row on provenance tables answers *who changed it*; every event answers *who, what, why*
8. Where capcli can't gate, it recovers: world.sql + audit-in-git make destruction a reversible event
9. The audit mirror is read-only; analysis operates at primitive depth via deterministic views

---

## The One-Liner

> **capcli-db: raw SQL through an unbreakable gate — the agent explores freely above the kernel, touches nothing below it, every effect carries its author and its reason, and the whole world is recoverable from history.**