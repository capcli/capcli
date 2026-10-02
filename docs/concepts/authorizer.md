# The Database Authorizer

Capcli does not inspect SQL with regex middleware after the fact.

Every query crosses a **three-stage prepare-time interception pipeline** compiled into the Rust kernel. If any stage flags an invariant violation, the query dies with zero side effects — [exit 2 (Policy Denial)](../reference/exit-codes.md#exit-2) — and SQLite memory never mutates.

```
Incoming SQL
     │
     ▼
┌──────────────────────────────────────────────┐
│  Layer 2: AST Semantic Analysis (sqlparser)  │ → Blast radius, tautologies, WHERE/LIMIT
└──────────────────────┬───────────────────────┘
                       │ pass
                       ▼
┌──────────────────────────────────────────────┐
│  Layer 1.5: VDBE Bytecode Trap (EXPLAIN)     │ → Opcode check: OpenWrite on read = KILL
└──────────────────────┬───────────────────────┘
                       │ pass
                       ▼
┌──────────────────────────────────────────────┐
│  Layer 1: Native C Authorizer (sqlite3)      │ → Action × Table × Column permission gate
└──────────────────────┬───────────────────────┘
                       │ SQLITE_OK
                       ▼
             Physical SQLite Commit
```

---

<a id="layer-1"></a>

## 1. Layer 1: Native C Authorizer (`sqlite3_set_authorizer`)

A native Rust closure passed to `sqlite3_set_authorizer` inside `sqlite3_prepare_v2`. Every statement is evaluated at the C engine level, as a 3D **action × table × column** tuple.

### Engine Operations & Global Bans

| Operation | Policy | Trust Floor | Breach Result |
|---|---|---|---|
| **`ATTACH` / `DETACH`** | **Denied unconditionally** | None (impossible) | `exit 2` (`SQLITE_DENY`) |
| **`DROP TABLE / VIEW`** | **Denied for agents** | None (kernel only) | `exit 2` (`SQLITE_DENY`) |
| **`ALTER TABLE`** | Restricted | **Reviewed** | `exit 2` (Draft blocked) |
| **`VACUUM`** | Restricted | **Pinned** (denied in prod) | `exit 2` (Denied in Prod) |
| **Agent Triggers** | **Denied** | None (kernel only) | `exit 2` (`SQLITE_DENY`) |

### PRAGMA Strict Whitelist

Only **two** SQLite PRAGMAs are permitted. All others return `SQLITE_DENY`:

* `PRAGMA query_only`
* `PRAGMA foreign_keys`

(`PRAGMA table_info`, `PRAGMA journal_mode`, and arbitrary config statements are killed on sight.)

### Function Allowlist & Denylist

| Status | Functions | Note |
|---|---|---|
| **Allowed** | `count`, `sum`, `min`, `max`, `avg`, `json_extract`, `date`, `strftime` | Standard math, dates, and JSON querying |
| **Denied** | `load_extension`, `writefile`, `readfile`, `fts3_tokenizer` | Hard exploit/escape prevention |

---

<a id="vdbe"></a>

## 2. Layer 1.5: VDBE Bytecode Trap (`EXPLAIN`)

Agents can construct obfuscated SQL designed to fool an AST parser into classifying a mutation as a safe read. So the kernel cross-checks the engine itself:

1. Every query is dry-run through `sqlite3_prepare_v2`.
2. The engine evaluates the resulting **VDBE bytecode opcodes**.
3. If an AST-classified read query emits the **`OpenWrite`** opcode, execution terminates instantly — `exit 2` (`policy.authorizer.opcode_trap`), state untouched.

The parser says *read*; the bytecode says *write*; the bytecode wins.

---

<a id="layer-2"></a>

## 3. Layer 2: AST Semantic Rules (`sqlparser`)

Evaluated before SQLite compilation begins. Enforces syntactic discipline and bounds blast radius.

### Banned Query Patterns

The AST parser fails closed on structural anti-patterns:

```sql
-- 1. Unbounded tautology bypass (denied)
UPDATE orders SET status = 'shipped' WHERE status = 'pending' OR 1=1;

-- 2. Full-table deletion bypass (denied)
DELETE FROM orders WHERE NOT EXISTS (SELECT 1 FROM non_existent);

-- 3. Naked tautology (denied)
SELECT * FROM users WHERE 1=1;

-- 4. Multi-statement raw batches (denied)
SELECT id FROM orders; DROP TABLE users;
```

### Update & Delete Mutation Bounds

Every `UPDATE` and `DELETE` must satisfy three AST criteria:

1. **`WHERE` clause required.** Naked mutations are refused.
2. **`LIMIT` clause required**, within the update/delete ceiling ([figures](../reference/limits.md#database-ceilings)).
3. **Primary key or specific index.** Target predicates must be bounded.

```bash
# Passes: bounded predicate, explicit LIMIT, declared intent
capcli sql "UPDATE orders SET status = 'shipped' WHERE status = 'processing' LIMIT 50" -m "ship"
```

Drop the `LIMIT` and the AST layer kills the statement before SQLite ever sees it — the receipt it prints is dissected in [Anatomy of a denial](#anatomy-of-a-denial) below.

### Mandatory Causal Intent (`-m`)

* **Reads (`SELECT`):** intent is optional.
* **Writes (`INSERT`, `UPDATE`, `DELETE`, `ALTER`):** intent is mandatory. Missing `-m` throws [exit 3](../reference/exit-codes.md#exit-3) (`policy.query.writes_require_intent`).
* **Scope binding:** the AST verifies that touched tables and columns match the declared intent. Touching undeclared tables throws `exit 2`.

### Ceilings

Reads cap at 10,000 rows per query, INSERTs at 500 rows per statement, and UPDATE/DELETE at `LIMIT` 1,000 — the full table of per-statement ceilings lives in [reference/limits.md#database-ceilings](../reference/limits.md#database-ceilings).

---

## 4. Trust Level Overlays

The C authorizer parameterizes permissions by the caller's trust rung:

| Rule | Draft | Reviewed | Pinned |
|---|---|---|---|
| **Can read secrets** | **No** (`exit 2`) | Masked | Masked |
| **Can execute `ALTER TABLE`** | **No** (`exit 2`) | Yes | Yes |
| **Can run in production** | **No** (`exit 2`) | Yes (supervised) | Yes (unattended) |
| **Audit detail** | Full payload | Full payload | Summary |

Row ceilings scale the same way — draft mutations cap at 10 rows (100 in dev for seeding, denied outright in prod), reviewed at 100, pinned at 500. Exact per-rung figures: [reference/limits.md#database-ceilings](../reference/limits.md#database-ceilings). How rungs are earned: [trust-engine.md](trust-engine.md).

---

## 5. System Tables Protection Matrix

The 13 kernel-managed system tables live inside `workspace.db` alongside domain data. The C authorizer applies hard-coded access rules:

| System Table | Purpose | Agent Access |
|---|---|---|
| `_audit` | Cryptographic event ledger | **Read-Only** (UPDATE/DELETE = `exit 2`) |
| `_api_quota` | Live rate-bucket balances | **Read-Only** |
| `_api_catalog` | OpenAPI imported verbs | **Read-Only** |
| `_budget_frames` | Cascading call-stack frames | **Read-Only** |
| `_budget_earmarks` | Ring-fenced token allocations | **Read-Only** |
| `secrets` | AES-256-GCM encrypted credentials | **Read-Only** (`value` masked; Draft denied) |
| `agents` | Process identity registry | **Read-Only** |
| `claims` | Distributed lease locks | **Read, Insert, Delete** (for locking) |
| `_pending_asks` | Suspended human inquiries | **Read-Only** |
| `_watch_cursors` | Webhook / polling stream offsets | **Read-Only** |
| `_capability_embeddings` | Semantic search vectors | **Read-Only** |
| `routine_stats` | Historical latency/reliability | **Read-Only** |
| `_system_schema` | Compiled DDL checksums | **Read-Only** |

---

<a id="anatomy-of-a-denial"></a>

## 6. Anatomy of a Denial

When any layer kills a query, the kernel returns a machine-parseable `[FAIL]` receipt: the exact rule code, the rejected statement, the measured value against the cap, an actionable `remedy`, and a hard guarantee that `state_modified: false`. The receipt also names the `layer` — AST, VDBE bytecode, or C authorizer — so denials are debuggable, not mysterious.

The full six-guarantee payload anatomy, with worked denial walkthroughs, lives in [reference/exit-codes.md#fail-payload](../reference/exit-codes.md#fail-payload).

**Every ceiling in one table:** → [reference/limits.md](../reference/limits.md)
