Here are the 5 core **Move 3** command reference files for `docs/reference/commands/` that enshrine the missing network, trigger, compilation, and system mechanics.

---

### File 1: `docs/reference/commands/api.md`
```markdown
# Command: `capcli api`

Manages external third-party API catalogs, OpenAPI synchronization, and verb lifecycles.

```bash
capcli api <verb> [args] [--flags]
```

---

## Subcommands

| Verb | Syntax | Description |
|---|---|---|
| **`sync`** | `capcli api sync <provider> <url> [--interval 7d] [--dry-run]` | Imports and compiles OpenAPI specs into `apis/<provider>.yaml`. |
| **`diff`** | `capcli api diff <provider>` | Diffs compiled spec against upstream spec hash (`spec_hash`). |
| **`catalog`**| `capcli api catalog <provider> [--trust <trust>]` | Lists verbs filtered by trust rung (`draft`, `reviewed`, `pinned`). |
| **`prove`** | `capcli api prove <provider.verb> [-p k=v] [--env sim]` | Dry-runs against simulated mocks or schema fixtures. |
| **`ship`** | `capcli api ship <provider.verb> <reviewed\|pinned> [--reason "<why>"]` | Promotes an API verb up the trust ladder. |
| **`stats`** | `capcli api stats <provider> [--deep] [--summary]` | Displays provider token-bucket quotas and latency metrics. |
| **`retire`** | `capcli api retire <provider.verb> [--reason "<why>"]` | Permanently disables verb while preserving provenance. |
| **`rollback`**| `capcli api rollback <provider.verb> [version]` | Restores prior verb configuration schema. |

---

## Invariants & Rules

* **Spec Quarantine:** The harness is banned from reading raw OpenAPI files. Specs >10MB auto-prune unreferenced paths during compilation.
* **Verb Lifecycle:** Verbs sync at `draft` trust and climb the ladder via `ship` (`draft` ➔ `reviewed` ➔ `pinned`); retiring preserves provenance. There is no dormant state and no activation verb.
* **Simulation Modes:**
  * `sandbox`: Routes to provider sandbox URL via `apis/<provider>.sim.yaml`.
  * `mock`: Returns canned fixture from `apis/<provider>.mock.yaml`.
  * `dry-run`: Validates payload schema and returns `{ "simulated": true }`.
  * `prod-only`: Throws `exit 2` if called in `dev` or `sim`.
* **Ceilings:** Max 10 providers; max 300 verbs/provider.

---

## Banned Verbs
* `capcli api call` ➔ **Banned.** Use `capcli run` or `ctx.api.call` inside guest code.
* `capcli api import --pick` ➔ **Banned.** Verbs are synced in full to preserve schema integrity.
```

---

### File 2: `docs/reference/commands/bind.md`
```markdown
# Command: `capcli bind`

Registers and governs inbound triggers: time crons, webhook listeners, and local reverse API endpoints.

```bash
capcli bind <verb> [args] [--flags]
```

---

## Subcommands

| Verb | Syntax | Description |
|---|---|---|
| **`cron`** | `capcli bind cron <name> <capability> "<cron_expr>" -m "<why>"` | Registers automated cron schedule. |
| **`webhook`** | `capcli bind webhook <name> <provider> <event> <capability> [--ingress <url>] -m "<why>"` | Binds inbound webhook with mandatory HMAC verification. |
| **`endpoint`**| `capcli bind endpoint <routine@version> --auth api-key [--rate <r>] [--channel all\|rest\|mcp]` | Serves a pinned routine over local HTTP and MCP. |
| **`export`** | `capcli bind export <openapi\|mcp> [--out <path>]` | Generates pure OpenAPI v3 or MCP JSON manifests. |
| **`keys`** | `capcli bind keys issue <name> --principal partner:<id>` | Issues partner API keys with mandatory 90-day expiry. |
| **`list`** | `capcli bind list` | Displays active, paused, and dead bindings. |
| **`inspect`** | `capcli bind inspect <handle>` | Inspects binding trigger health and arrival rates. |
| **`pause`** | `capcli bind pause <handle>` | Temporarily suspends trigger processing. |
| **`resume`** | `capcli bind resume <handle>` | Resumes paused trigger processing. |
| **`remove`** | `capcli bind remove <handle>` | Unbinds trigger and archives binding record. |

---

## Invariants & Rules

* **Cron Interval Floor:** Minimum cron interval is 5 minutes (`*/5 * * * *`). Sub-5-minute schedules throw `exit 3`.
* **Reboot Catchup Law:** Maximum 1 catchup execution on daemon reboot. Stale missed runs are discarded.
* **Webhook Hard Limits:** Payload max 64 KB (65,536 bytes); arrival ceiling 100 events/minute. Oversized payloads return `413`.
* **Dead Letter Queue (DLQ):** Failed or throttled webhook dispatches persist in DLQ for 30 days or 1,000 items (FIFO purged).
* **Endpoint Server Floor:** Only **Pinned** routines can be served over HTTP (`trust: pinned`). Binds strictly to `127.0.0.1`.
* **Partner Key Cap:** Max 25 keys per workspace. Immortal keys are banned (90-day hard TTL).
```

---

### File 3: `docs/reference/commands/ping.md`
```markdown
# Command: `capcli ping`

Governs asynchronous human interaction, sensory alerts, and structured suspension inquiries.

```bash
capcli ping <verb> [args] [--flags]
```

---

## Subcommands

| Verb | Syntax | Description |
|---|---|---|
| **`notify`** | `capcli ping notify <principal> "<msg>" --channel <c> -m "<why>"` | Sends an informational alert to configured channels. |
| **`ask`** | `capcli ping ask <principal> "<q>" --options "<opts>" [--timeout <t>] -m "<why>"` | Files a structured human inquiry and pauses caller turn. |
| **`list`** | `capcli ping list [--pending]` | Lists active and suspended human inquiries. |
| **`resolve`**| `capcli ping resolve <ask-id> --choice <opt> [-m "<why>"]` | Resolves an inquiry, unfreezing the suspended routine. |
| **`expire`** | `capcli ping expire <ask-id>` | Manually expires an inquiry, triggering fail-closed denial. |

---

## Invariants & Rules

* **Anti-Injection Enum Mandate:** `ping ask` requires `--options` (max 5 discrete choices). Free-text answers are physically banned.
* **Token Ceilings:** Questions capped at 100 tokens. Notification messages capped at 300 tokens. Max 3 notification channels.
* **Fail-Closed Deadlines:** Default timeout is 60 minutes (max allowable: 480 min). Expired inquiries exit with **`exit 2` (Denied)**.
* **Quiet Hours:** 22:00 to 07:00 host time. `ping notify` is suppressed. `ping ask` bypasses quiet hours only if blocking a live routine.
```

---

### File 4: `docs/reference/commands/rule.md`
```markdown
# Command: `capcli rule`

Compiles, validates, diffs, and applies declarative YAML schemas and governance bounds.

```bash
capcli rule <verb> [target] [--flags]
```

---

## Subcommands

| Verb | Syntax | Description |
|---|---|---|
| **`show`** | `capcli rule show [target=schema\|policy\|governance]` | Dumps compiled AST rules for the active workspace. |
| **`diff`** | `capcli rule diff [target=schema] [--git]` | Compares working directory YAML against Git HEAD or live DB PRAGMAs. |
| **`apply`** | `capcli rule apply [target=schema] [--dry-run] -m "<why>"` | Runs the 5-Gate Compiler and executes forward DDL migrations. |
| **`validate`**| `capcli rule validate` | Offline CI gate verifying syntax and acyclic relations. |

*(Ergonomic alias: `capcli apply` directly aliases `capcli rule apply schema`)*.

---

## The 5-Gate Compiler Pipeline

1. **Gate 1: Syntax:** Validates YAML structure and expands shorthand DDL keywords. Throws `exit 3` on failure.
2. **Gate 2: Semantics:** Constructs relational graph via `petgraph`. Cycle detection rejects circular foreign keys (`exit 3`).
3. **Gate 3: Manifest Lock:** Checks live SHA-256 hash against `capcli.lock`. Mismatch halts boot in prod/sim (`exit 3`).
4. **Gate 4: Live Drift:** Compares live SQLite table PRAGMAs against declarations. Undeclared columns throw `exit 3`.
5. **Gate 5: Migration Safety:** Dry-runs DDL on an isolated snapshot. Rollback failure aborts migration (`exit 3`).

---

## Shorthand DDL Expansions

| Shorthand | Expands To | Description |
|---|---|---|
| `pk` | `INTEGER PRIMARY KEY AUTOINCREMENT` | Auto-incrementing integer key. |
| `text pk` | `TEXT PRIMARY KEY` | String primary key. |
| `text!` | `TEXT NOT NULL UNIQUE` | Unique non-nullable string. |
| `int~` | `INTEGER` + Authorizer Write Lock | Write-once immutable column. |
| `text=val` | `TEXT DEFAULT 'val'` | Default text value. |
| `int ref=t.c` | `INTEGER REFERENCES t(c)` | Foreign key constraint. |
| `blob ref=storage` | `TEXT` (JSON object metadata) | Managed object store pointer. |
| `mask=true` | Authorizer redaction hook | Format-Preserving Anonymization in sim. |
| `imm_rows: true`| C Authorizer intercept | Disallows `UPDATE` and `DELETE` on table. |
| `imm_cols: [...]`| C Authorizer intercept | Disallows `UPDATE` on listed columns. |

---

## Banned Operations
* `capcli config set` ➔ **Banned.** Dynamic policy mutation is forbidden. Edit YAML and Git commit.
* Manual DDL (`capcli sql "ALTER TABLE..."`) ➔ **Banned.** All DDL must originate from `schema.yaml`.
```

---

### File 5: `docs/reference/commands/sys.md`
```markdown
# Command: `capcli sys`

Kernel diagnostics, cryptographic audit inspection, identity registries, encrypted vault, and disaster recovery.

```bash
capcli sys <verb> [args] [--flags]
```

---

## Subcommands

| Verb | Syntax | Description |
|---|---|---|
| **`doctor`** | `capcli sys doctor [--boot-check] [--report] [--json]` | Probes host OS, sandbox tier (Tier 1 vs 2), runtime engines, and emits trust receipts. |
| **`inbox`** | `capcli sys inbox pop [--channel <name>]` | Consumes sensory queued events from webhooks, crons, or partners. |
| **`audit tail`**| `capcli sys audit tail [--follow] [--capability <urp>] [--since 1h]` | Streams immutable event log with causal hashes. |
| **`audit trace`**| `capcli sys audit trace <op-id> [--explain]` | Walks causal DAG upstream to root intent; explains denials. |
| **`audit query`**| `capcli sys audit query "<sql>" [-p k=v]` | Runs bounded read-only queries against `_audit` table. |
| **`audit replay`**| `capcli sys audit replay --from <point> [--dry-run]` | Replays historical events against isolated forked state. |
| **`agent`** | `capcli sys agent <register\|list\|revoke> [args]` | Manages OS-bound agent identities and capability tokens. |
| **`vault`** | `capcli sys vault <set\|import-env> [args]` | Encrypts root credentials into AES-256-GCM storage. |
| **`backup`** | `capcli sys backup [--push]` | Creates VACUUM snapshots and syncs Git + WORM storage. |
| **`recover`** | `capcli sys recover <commit\|snap_id>` | Restores database and workspace state from a recovery point. |
| **`exec`** | `capcli sys exec "<cmd>" --sandbox` | Executes a one-shot command inside the `bwrap` network jail. |
| **`serve`** | `capcli sys serve <--start\|--stop\|--restart\|--status>` | Controls the persistent axum daemon on `127.0.0.1:4040`. |

---

## Invariants & Break-Glass Flags

* **Clock Drift Warning:** Host clock delta > 500ms vs NTP emits a diagnostic warning. The causal DAG and lease claims bind to `CLOCK_MONOTONIC` and SQLite sequence IDs; boot and execution continue.
* **Audit Write Priority:** If the audit sink (`_audit` or JSONL mirror) fails to flush, execution halts immediately with **`exit 5` (Kernel Panic)**. Nothing runs unaudited.
* **Emergency Recovery Mode (`CAPCLI_RECOVERY=1`):**
  * Disables behavioral policy enforcement (`policy.yaml`).
  * Loads *only* `schema.yaml` and the audit sink.
  * Verbs restricted to: `sql` (read-only), `db dump`, `sys audit tail`, and `sys backup`.
* **Zeroize Memory Sanitation:** Plane-text secrets decrypted from vault are scrubbed from RAM with zeros immediately post-egress.
```
