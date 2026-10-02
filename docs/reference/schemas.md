# Schemas: Shorthand DDL & System Tables

Two files, two owners, one database. `schema.yaml` is yours — agent-authored in the dev worktree. `system-schema.yaml` is the kernel's — read-only for you, modified only by kernel releases. Both compile into `workspace.db` through the [5-gate compiler](../concepts/compiler.md). Agents never write DDL by hand: every table, column, index, view, and trigger originates in `schema.yaml` and lands via [`capcli apply`](cli/rule.md).

## Shorthand DDL

Raw SQL DDL inside YAML is ugly and error-prone, so the compiler accepts a dense micro-DDL that expands into native SQLite constraints and C authorizer rules:

| Shorthand | Expands To | Engine Layer | Behavior |
|---|---|---|---|
| `pk` | `INTEGER PRIMARY KEY AUTOINCREMENT` | SQLite | Auto-incrementing integer key. |
| `text pk` | `TEXT PRIMARY KEY` | SQLite | String primary key. |
| `text!` | `TEXT NOT NULL UNIQUE` | SQLite | Mandatory unique text. |
| `int~` | `INTEGER` + authorizer write lock | [C authorizer](../concepts/authorizer.md) | Write-once immutable — set on `INSERT`, `UPDATE` denied forever. |
| `text=val` | `TEXT DEFAULT 'val'` | SQLite | Default fallback value. |
| `int ref=t.c` | `INTEGER REFERENCES t(c)` | SQLite | Inline foreign key constraint. |
| `blob ref=storage` | `TEXT` (JSON object metadata) | Kernel subsystem | Links the column to managed object storage. |
| `mask=true` | Redaction hook | Kernel serializer | Format-Preserving Anonymization in sim data layers ([FPA](../concepts/environments.md#fpa)). |
| `imm_rows: true` | Table mutation lock | C authorizer | `INSERT` allowed; `UPDATE` and `DELETE` killed at prepare-time. |
| `imm_cols: [a, b]` | Column mutation lock | C authorizer | Listed columns cannot be modified after insert. |

Table-level declarations round out the vocabulary:

| Declaration | Effect |
|---|---|
| `prov: true` | Adds `created_by` / `modified_by`, populated by the kernel. |
| `sens: true` | Sensitive table — masked on sim fork. |
| `sys: true` | Read-only grant for agents (kernel-managed surface). |
| `idx:` | Single-column `[col]` or composite `[[a, b]]` indexes. |
| `rel:` | Semantic traversal edges for the search index. |
| `chk:` | Physical SQLite CHECK constraints. |
| `trig:` | Kernel-compiled, policy-exempt trigger bodies. |
| `seed:` | Initial rows executed inside the DDL transaction. |

A worked example of these declarations in a real `schema.yaml` → [compiler.md](../concepts/compiler.md).

## System tables

[`system-schema.yaml`](../../cans/artifacts/system-schema.yaml) defines **13 kernel-managed tables**. Agent access below is compiled from the authorizer section of [`policy.yaml`](../../cans/artifacts/policy.yaml):

| Table | Agent Access | Purpose |
|---|---|---|
| `_audit` | read-only; rows immutable (`imm_rows`) | Append-only audit mirror — the primary query surface for what happened ([audit.md](audit.md)). |
| `_api_quota` | read-only | Live provider rate buckets parsed deterministically from response headers. |
| `_api_catalog` | read-only; `provider`/`verb` immutable | Imported OpenAPI verb catalog: lifecycle, trust, sim mode. |
| `_budget_frames` | read-only | Per-invocation budget frames enforcing the downward [min() cascade](../concepts/budgets.md#the-min-law). |
| `_budget_earmarks` | read-only | Ring-fenced API quota reservations with TTL. |
| `_suspended_tasks` | read-only (daemon-managed) | Background tasks paused via [exit 6](exit-codes.md#exit-6), awaiting quota refill. |
| `secrets` | read; `value` masked; draft trust denied entirely | Egress credentials, AES-256-GCM at rest — never visible to agents. |
| `agents` | read-only; `id`/`principal` immutable | Registered harness identities proven via OS process credentials. |
| `claims` | read, insert, delete | Lease-based concurrency locks with TTL — the only system table agents write. |
| `_pending_asks` | read-only | Suspended human inquiries awaiting structured resolution. |
| `_watch_cursors` | read-only | Stream pagination offsets for webhook and polling listeners. |
| `_capability_embeddings` | read-only | Semantic vectors powering progressive discovery. |
| `routine_stats` | read-only | Aggregated telemetry driving the promotion gates. |

Reconciliation note, for anyone counting: `policy.yaml`'s `deny_write` roster also names **`_system_schema`** — the kernel's schema-metadata surface, hash-verified at boot but not defined in the `system-schema.yaml` tables block — and its authorizer header still says "11 kernel-managed surfaces," which is stale. The artifact on disk defines 13, including `_suspended_tasks` and `_budget_earmarks`; `_suspended_tasks` is daemon-written and never agent-writable, which is why it doesn't need a policy row. The tables above are the truth.

## The domain schema law

* **No hand-written DDL.** `capcli sql "ALTER TABLE …"` is denied — schema changes are edits to `schema.yaml`, compiled and applied via [`capcli apply`](cli/rule.md).
* **No system-schema edits.** The file is read-only for agents by filesystem permission; only kernel releases modify it, and boot verifies its hash.
* **No runtime policy mutation.** `config set` is banned — edit the YAML, recompile, git commit.
* Shape ceilings (tables, columns, indexes, views, seed rows per table) are caps, not suggestions → [limits.md](limits.md#workspace-storage).

How a schema edit travels from YAML to prod (dry-run → trust gate → apply → merge) → [environments.md](../concepts/environments.md) and [compiler.md](../concepts/compiler.md).
