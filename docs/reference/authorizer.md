# The Database Authorizer

Capcli does not inspect SQL with regex middleware after the fact. 

Every query crosses a **three-stage prepare-time interception pipeline** compiled into the Rust kernel. If any stage flags an invariant violation, the query is executed with zero side effects: **`exit 2` (Policy Denial)**, and SQLite memory never mutates.

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

## 1. Layer 1: Native C Authorizer (`sqlite3_set_authorizer`)

Engineered as a native Rust closure passed to `sqlite3_set_authorizer` inside `sqlite3_prepare_v2`. Evaluates every statement at the C engine level.

### Engine Operations & Global Bans

| Operation | Policy | Trust Floor | Breach Result |
|---|---|---|---|
| **`ATTACH` / `DETACH`** | **Denied Unconditionally** | None (Impossible) | `exit 2` (`SQLITE_DENY`) |
| **`DROP TABLE / VIEW`** | **Denied for Agents** | None (Kernel only) | `exit 2` (`SQLITE_DENY`) |
| **`ALTER TABLE`** | Restricted | **Reviewed** | `exit 2` (Draft blocked) |
| **`VACUUM`** | Restricted | **Pinned** (Dev/Sim only) | `exit 2` (Denied in Prod) |
| **Agent Triggers** | **Denied** | None (Kernel only) | `exit 2` (`SQLITE_DENY`) |

---

### PRAGMA Strict Whitelist

Only **two** SQLite PRAGMAs are permitted. All others return `SQLITE_DENY`:

* `PRAGMA query_only`
* `PRAGMA foreign_keys`

*(Running `PRAGMA table_info`, `PRAGMA journal_mode`, or arbitrary config statements is killed instantly).*

---

### Function Allowlist & Denylist

SQLite scalar and aggregate functions are locked to a strict whitelist:

| Status | Functions | Note |
|---|---|---|
| **Allowed** | `count`, `sum`, `min`, `max`, `avg`, `json_extract`, `date`, `strftime` | Standard math, dates, and JSON querying |
| **Denied** | `load_extension`, `writefile`, `readfile`, `fts3_tokenizer` | Hard exploit/escape prevention |

---

## 2. Layer 1.5: VDBE Bytecode Trap (`EXPLAIN`)

Agents can construct obfuscated SQL designed to fool AST parsers into classifying mutations as safe reads.

To prevent this:
1. Every query is dry-run through `sqlite3_prepare_v2`.
2. The engine evaluates the resulting **VDBE bytecode opcodes**.
3. If an AST-classified read query emits the **`OpenWrite`** bytecode opcode:
   * **Execution terminates immediately.**
   * Throws `exit 2` (`policy.authorizer.opcode_trap`).
   * State is untouched.

---

## 3. Layer 2: AST Semantic Rules (`sqlparser`)

Evaluated before SQLite compilation begins. Enforces syntactic discipline and limits blast radius.

### Banned Query Patterns

The AST parser fails closed on queries containing these structural anti-patterns:

```sql
-- 1. Unbounded tautology bypass (Denied)
UPDATE orders SET status = 'shipped' WHERE status = 'pending' OR 1=1;

-- 2. Full-table deletion bypass (Denied)
DELETE FROM orders WHERE NOT EXISTS (SELECT 1 FROM non_existent);

-- 3. Naked tautology (Denied)
SELECT * FROM users WHERE 1=1;

-- 4. Multi-statement raw batches (Denied)
SELECT id FROM orders; DROP TABLE users;
```

---

### Update & Delete Mutation Bounds

Every `UPDATE` and `DELETE` must satisfy three AST criteria:

1. **`WHERE` clause required:** Naked mutations are refused.
2. **`LIMIT` clause required:** Must include an explicit `LIMIT` up to `1000`.
3. **Primary Key or Specific Index:** Target predicates must be bounded.

```bash
# REJECTED (exit 2): Missing LIMIT
capcli sql "UPDATE orders SET status = 'shipped' WHERE status = 'processing'" -m "ship"

# ALLOWED (exit 0): Bounded predicate with LIMIT
capcli sql "UPDATE orders SET status = 'shipped' WHERE status = 'processing' LIMIT 50" -m "ship"
```

---

### Row Limits by Operation

| Statement | Hard Ceiling | Behavior on Overflow |
|---|---|---|
| **`SELECT`** | Max 10,000 rows | Capped by authorizer |
| **`INSERT`** | Max 500 rows per statement | `exit 2` (Must chunk via loop) |
| **`UPDATE / DELETE`** | Max 1,000 LIMIT ceiling | `exit 2` if `LIMIT > 1000` |

---

### Mandatory Causal Intent (`-m`)

* **Reads (`SELECT`):** Intent is optional.
* **Writes (`INSERT`, `UPDATE`, `DELETE`, `ALTER`):** Intent is **mandatory**.
* Missing the `-m` flag throws **`exit 3`** (`policy.query.writes_require_intent`).
* **Scope Binding:** The AST ensures tables and columns touched match the declared intent. Touching undeclared tables throws `exit 2`.

---

## 4. Trust Level Overlays

The C authorizer scales permissions dynamically based on the caller's trust rung:

| Rule | Draft | Reviewed | Pinned |
|---|---|---|---|
| **Max Rows Affected (Dev)** | 100 | 100 | 500 |
| **Max Rows Affected (Sim)** | 10 | 100 | 500 |
| **Max Rows Affected (Prod)** | **0 (Denied)** | 100 | 500 |
| **Can Read Secrets** | **No (`exit 2`)** | Masked | Masked |
| **Can Execute ALTER TABLE** | **No (`exit 2`)** | Yes | Yes |
| **Can Run in Production** | **No (`exit 2`)** | Yes | Yes (Unattended) |
| **Audit Detail** | Full payload | Full payload | Summary |

---

## 5. System Tables Protection Matrix

The 13 kernel-managed system tables live inside `workspace.db` alongside domain data. The C authorizer applies hard-coded access rules:

| System Table | Purpose | Agent Access |
|---|---|---|
| `_audit` | Cryptographic event ledger | **Read-Only** (UPDATE/DELETE = `exit 2`) |
| `_api_quota` | Live rate-bucket balances | **Read-Only** |
| `_api_catalog` | OpenAPI imported verbs | **Read-Only** |
| `_budget_frames` | Cascading call-stack frames | **Read-Only** |
| `_budget_earmarks`| Ring-fenced token allocations | **Read-Only** |
| `secrets` | AES-256-GCM encrypted credentials | **Read-Only** (`value` masked; Draft denied) |
| `agents` | Process identity registry | **Read-Only** |
| `claims` | Distributed lease locks | **Read, Insert, Delete** (for locking) |
| `_pending_asks` | Suspended human inquiries | **Read-Only** |
| `_watch_cursors` | Webhook / Polling stream offsets | **Read-Only** |
| `_capability_embeddings` | Semantic search vectors | **Read-Only** |
| `routine_stats` | Historical latency/reliability | **Read-Only** |
| `_system_schema`| Compiled DDL checksums | **Read-Only** |

---

## 6. Denial Feedback Anatomy

When the authorizer terminates a query, it returns machine-parseable diagnostics:

```text
[dev:tier_1]  ✗  exit 2

  FAIL  policy.query.update_delete.require_limit
        UPDATE orders SET status = 'shipped' WHERE status = 'processing'
                                                                   ^^^^^^
        No LIMIT clause. Blast radius unbounded.

  state_modified: false
  layer: AST
  measured: matches potentially 847 rows (cap: 100)
  remedy: add LIMIT, or target specific primary key
```

* **`state_modified: false`** is guaranteed on all non-zero exits.
* **`layer`** pinpoints whether the block occurred at AST, VDBE Bytecode, or the C Authorizer.
* **`remedy`** provides the syntax required to pass the gate on retry.
