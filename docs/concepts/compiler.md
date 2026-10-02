# The 5-Gate Compiler & Lockfile Integrity

In typical developer tools, YAML is parsed dynamically on the fly. Make a typo in `config.yaml` and the server boots anyway, runs happily for three days, then crashes on a Tuesday afternoon because line 84 was missing an indent.

Worse: an autonomous agent with shell access can simply run:

```bash
sed -i 's/max_rows_affected: 10/max_rows_affected: 1000000/' policy.yaml
```

And boom — your agent just edited its own leash, granted itself god-mode permissions, and dropped your production database.

In Capcli, **YAML is a compiled, version-locked programming language.** The configuration files are not parsed at runtime. They pass through a **5-Gate static analysis pipeline** and compile into an immutable cryptographic artifact: **`capcli.lock`**.

If a single byte on disk mismatches the lockfile, the kernel refuses to boot ([exit 3](../reference/exit-codes.md#exit-3)).

---

## 1. The Compilation Target: `capcli.lock`

Your workspace contains four declarative blueprints:

* **`schema.yaml`** — domain tables, columns, indexes, and views.
* **`system-schema.yaml`** — the 13 kernel-managed system tables (`_audit`, `secrets`, etc.).
* **`policy.yaml`** — behavioral rules (what capabilities may *do*).
* **`governance.yaml`** — structural rules (what capabilities may *be*).

At boot, the kernel compiles all four into a single root SHA-256 checksum:

```
  schema.yaml ──┐
  system-schema ┼──▶ [ RUST KERNEL COMPILER ] ──▶ SHA-256 ──▶ capcli.lock
  policy.yaml   │          (5-Gate Pipeline)
  governance    ┘
```

### The Lockfile Law

If an agent edits `policy.yaml` through a subshell script, the on-disk hash immediately diverges from `capcli.lock`:

```bash
$ capcli sql "SELECT * FROM orders"
```

```text
[prod:tier_1]  ✗  exit 3

  FATAL  kernel.boot.lockfile_mismatch
         Compiled capcli.lock root hash does not match working tree.
         expected: sha256:88a1f2c9...
         computed: sha256:00b9911e... (tainted: policy.yaml)

  state_modified: false
  layer: compiler
  remedy: discard uncommitted YAML changes via git checkout, or run 'capcli rule apply'
```

**The binary refuses to run.** You cannot sneak a policy change past the kernel. Configuration changes require running the compiler, generating a forward migration, and committing the resulting `capcli.lock` to Git.

---

## 2. The 5-Gate Compilation Pipeline

When you run `capcli rule apply` — or its canonical alias, `capcli apply` ([full syntax](../reference/cli/rule.md)) — your blueprints pass through five sequential validation gates. Any gate failure aborts compilation with `exit 3`:

```
┌────────────────────────────────────────────────────────┐
│  GATE 1: SYNTAX (Parse-Time)                           │
│  • Valid YAML indentation, no duplicate keys           │
│  • Micro-DDL shorthand syntax expands cleanly          │
└───────────────────────────┬────────────────────────────┘
                            │ pass
                            ▼
┌────────────────────────────────────────────────────────┐
│  GATE 2: SEMANTICS (Petgraph Acyclic Validator)        │
│  • Cycle detection: circular foreign keys rejected     │
│  • Topological sort establishes table compile order    │
│  • Scoped views verified for mandatory :principal      │
└───────────────────────────┬────────────────────────────┘
                            │ pass
                            ▼
┌────────────────────────────────────────────────────────┐
│  GATE 3: MANIFEST LOCK (Integrity Gate)                │
│  • Root SHA-256 of schema+system+policy+governance     │
│  • Must match capcli.lock exactly — prod/sim refuse    │
│    to boot; dev is marked as uncompiled draft          │
└───────────────────────────┬────────────────────────────┘
                            │ pass
                            ▼
┌────────────────────────────────────────────────────────┐
│  GATE 4: LIVE DRIFT (PRAGMA Scan)                      │
│  • Live SQLite table PRAGMAs compared against YAML     │
│  • Undeclared columns or phantom tables trigger denial │
└───────────────────────────┬────────────────────────────┘
                            │ pass
                            ▼
┌────────────────────────────────────────────────────────┐
│  GATE 5: MIGRATION SAFETY (Snapshot Dry-Run)           │
│  • DDL executes in an isolated transaction on a        │
│    snapshot; rollback verified before touching state   │
│  • Failure auto-restores the snapshot                  │
└────────────────────────────────────────────────────────┘
```

### Why Gate 2 (Acyclic Graph) Matters

LLMs love creating circular foreign keys: Table A references Table B, and Table B references Table A. Neither table can then be inserted into or dropped without disabling foreign key checks — a temporal paradox with a schema diagram.

Gate 2 builds a directed graph of your schema using Rust's `petgraph` crate. If `is_cyclic_directed(&graph)` returns `true`, compilation fails instantly. Circular schema bugs are caught before a single line of SQL is generated.

---

## 3. Micro-DDL Shorthand Expansions

Raw SQL DDL inside YAML is ugly and error-prone. Capcli provides a dense micro-DDL shorthand that expands into native SQLite constraints and C authorizer rules. A taste:

| Shorthand | Expands To | Layer |
|---|---|---|
| **`pk`** | `INTEGER PRIMARY KEY AUTOINCREMENT` | SQLite |
| **`int~`** | `INTEGER` + authorizer write lock — write-once immutable; set on `INSERT`, denied on `UPDATE` forever | Kernel authorizer |
| **`mask=true`** | Redaction hook — applies Format-Preserving Anonymization in `sim` data layers ([environments.md#fpa](environments.md#fpa)) | Kernel serializer |

### Example in `schema.yaml`

```yaml
tables:
  orders:
    description: "Core order state"
    columns:
      id: pk
      customer_id: text ref=customers.id
      total_cents: int!
      tracking_no: text~          # Immutable: once set, cannot be edited
      status: text='pending'
    idx:
      - [customer_id]
      - [[status, total_cents]]   # Composite index
    chk:
      - "total_cents >= 0"        # Native SQLite check constraint
```

Compiled, this generates deterministic, byte-reproducible SQL DDL, mounts authorizer interception hooks, and builds the schema in one atomic transaction. The complete shorthand table (`text!`, `ref=`, `imm_rows`, `imm_cols`, `sens`, `prov`, …) lives in [reference/schemas.md](../reference/schemas.md).

---

## 4. The NTP Clock Drift Law

In distributed systems and autonomous agent loops, time is an enforcement mechanism, not an aesthetic preference:

* Distributed locks in `claims` rely on TTL epochs.
* Quota windows in `_api_quota` rely on reset timestamps.
* Human inquiry expirations in `_pending_asks` rely on wall-clock deadlines.

Freeze the clock in a VM, or wind it back four hours to dodge an API rate-limit window, and every one of those guarantees silently rots. So at startup, `capcli-core` probes the host clock against an authoritative NTP delta. Skew past the boot ceiling and the kernel refuses to start — no corrupted locks, no manipulated token windows. The exact threshold and its invariant row: [reference/limits.md#invariants](../reference/limits.md#invariants). Physics requires monotonic time.

---

**See where compiled schemas land in daily work:** → [workflows/query-data.md](../workflows/query-data.md)
**Run an offline compilation check in CI:** → `capcli rule validate` ([reference/cli/rule.md](../reference/cli/rule.md))
