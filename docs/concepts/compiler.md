
# The 5-Gate Compiler & Lockfile Integrity

In typical developer tools, YAML files are a joke. 

They are parsed dynamically on the fly. If you make a typo in `config.yaml`, the server boots up anyway, runs happily for three days, and then crashes on a Tuesday afternoon because line 84 was missing an indent.

Worse: an autonomous agent with shell access can simply run:
```bash
sed -i 's/max_rows_affected: 10/max_rows_affected: 1000000/' policy.yaml
```
And boom—your agent just edited its own leash, gave itself god-mode permissions, and dropped your production database.

In Capcli, **YAML is a compiled, version-locked programming language.**

The configuration files are not parsed dynamically at runtime. They are compiled through a **5-Gate static analysis pipeline** into an immutable cryptographic artifact: **`capcli.lock`**.

If a single byte on disk mismatches the lockfile, the kernel refuses to boot (`exit 3`). Here is how the compiler enforces reality.

---

## 1. The Compilation Target: `capcli.lock`

Your workspace contains four declarative blueprints:
* **`schema.yaml`**: Domain tables, columns, indexes, and views.
* **`system-schema.yaml`**: The 13 kernel-managed system tables (`_audit`, `secrets`, etc.).
* **`policy.yaml`**: Behavioral rules (what capabilities may do).
* **`governance.yaml`**: Structural rules (what artifacts may be).

At boot, the kernel compiles all four files into a single root SHA-256 checksum:

```
  schema.yaml ──┐
  system-schema ┼──▶ [ RUST KERNEL COMPILER ] ──▶ SHA-256 ──▶ capcli.lock
  policy.yaml   │          (5-Gate Pipeline)
  governance    ┘
```

### The Lockfile Law
If an agent edits `policy.yaml` using a subshell script, the on-disk hash immediately diverges from `capcli.lock`.

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

**The binary refuses to run.** 

You cannot sneak a policy change past the kernel. Configuration changes require running the compiler, generating a forward migration, and committing the resulting `capcli.lock` to Git.

---

## 2. The 5-Gate Compilation Pipeline

When you run `capcli rule apply` (or `capcli apply`), your blueprints pass through five sequential validation gates. If any gate flags an invariant violation, compilation aborts with **`exit 3`**:

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
│  • Compiles unified root SHA-256 hash                  │
│  • Verifies active runtime version compatibility       │
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
│  • DDL executes in isolated transaction on a snapshot  │
│  • Rollback cleanly verified before touching live state│
└────────────────────────────────────────────────────────┘
```

### Why Gate 2 (Acyclic Graph) Matters:
LLMs love creating circular foreign keys: Table A references Table B, and Table B references Table A. 

This creates a temporal paradox where neither table can be inserted into or dropped without disabling foreign key checks.

Gate 2 builds a directed graph of your schema using Rust's `petgraph` crate. If `is_cyclic_directed(&graph)` returns `true`, compilation fails instantly. Circular schema bugs are caught before a single line of SQL is generated.

---

## 3. Micro-DDL Shorthand Expansions

Writing raw SQL DDL inside YAML files is ugly and error-prone. Capcli provides a dense, expressive micro-DDL shorthand syntax that expands into native SQLite constraints and C authorizer rules:

| Shorthand | Expands To | Engine Layer | Behavior |
|---|---|---|---|
| **`pk`** | `INTEGER PRIMARY KEY AUTOINCREMENT` | SQLite | Standard auto-incrementing ID. |
| **`text pk`** | `TEXT PRIMARY KEY` | SQLite | String primary key. |
| **`text!`** | `TEXT NOT NULL UNIQUE` | SQLite | Mandatory unique text. |
| **`int~`** | `INTEGER` + Authorizer Write Lock | Kernel Authorizer | **Write-once immutable.** Can be set on `INSERT`, but `UPDATE` is denied forever. |
| **`text=val`** | `TEXT DEFAULT 'val'` | SQLite | Default fallback value. |
| **`int ref=users.id`** | `INTEGER REFERENCES users(id)` | SQLite | Foreign key relation. |
| **`blob ref=storage`** | `TEXT` (JSON Object Metadata) | Kernel Subsystem | Automatically links column to managed S3/R2 object storage. |
| **`mask=true`** | Redaction Hook | Kernel Serializer | Applies Format-Preserving Anonymization in `sim` data layers. |
| **`imm_rows: true`** | Table Mutation Lock | C Authorizer | Table allows `INSERT`, but `UPDATE` and `DELETE` are killed at prepare-time. |
| **`imm_cols: [a, b]`** | Column Mutation Lock | C Authorizer | Listed columns cannot be modified after initial insert. |

### Example in `schema.yaml`:
```yaml
tables:
  orders:
    description: "Core order state"
    columns:
      id: pk
      customer_id: text ref=customers.id
      total_cents: int!
      tracking_no: text~          # Immutable: once set, cannot be edited!
      status: text='pending'
    idx:
      - [customer_id]
      - [[status, total_cents]]   # Composite index
    chk:
      - "total_cents >= 0"        # Native SQLite check constraint
```

When compiled, this generates deterministic, byte-reproducible SQL DDL, mounts authorizer interception hooks, and builds the database schema in one atomic transaction.

---

## 4. The 500ms NTP Clock Drift Warning

In distributed systems and autonomous agent loops, time is not an aesthetic preference.

Time is an enforcement mechanism:
* Distributed locks in `claims` rely on TTL epochs.
* Quota windows in `_api_quota` rely on reset timestamps.
* Human inquiry expirations in `_pending_asks` rely on wall-clock deadlines.

Wall-clock drift degrades none of these mechanisms. The internal causal DAG and lease claims bind to `CLOCK_MONOTONIC` and SQLite sequence IDs, so causal ordering survives a skewed host clock.

When the host clock delta against NTP exceeds **500 milliseconds**, `sys doctor` emits a diagnostic warning and execution continues. The drift degrades audit wall-clock timestamps only; the recorded remedy is clock synchronization via `chronyd` or `ntpdate` at the operator's convenience.

Physics requires monotonic time — and monotonic time is exactly what the kernel binds to.

---

## The One Rule

**Configuration is code. Blueprints are compiled, not interpreted.**

You cannot hack your own leash with a shell script. If the YAML syntax is ambiguous or the graph is circular, Capcli fails closed before a single process can spawn. A drifting clock earns a warning and a remedy, never a boot refusal.

---

**See where compiled schemas land:** → [work-with-your-data.md](../use/work-with-your-data.md)  
**Run an offline schema compilation check in CI:** → `capcli rule validate`
