# command.architecture.md *(final v3 — collapsed surface)*

> The entire CLI: **9 nouns, universal flags, frequency-based depth, exit codes as law.** Small enough to memorize, deep enough that nothing escapes the gate. Zero redundancy.

---

## 1. Design Laws

1.  **One shape forever**: `capcli <noun> <verb> [target] [--flags]`. No exceptions.
2.  **Every mutating verb accepts**: `--dry-run`, `--json`, `--intent "<why>"`, `--as <principal>`. Reads get `--json` + `--as`.
3.  **Everything resolves through the registry** — db ops, routines, api verbs, views are all *capabilities*; `run`/`search`/`inspect` work identically on all.
4.  **Output contract**: humans get pretty tables; agents pass `--json` (versioned machine contract). Every output prefixes `[env]` — prod in red.
5.  **Exit codes are law** — scripts and agents branch on them, never parse stdout:

| Code | Meaning |
| :--- | :--- |
| `0` | ok |
| `2` | policy-denied |
| `3` | validation-failed (incl. governance, missing intent) |
| `4` | runtime-error |
| `5` | audit-write-failed (= nothing ran) |

### CLI Framework

`citty` (unjs) — nested subcommands, typed args, auto `--help`.
Maps directly to the 9-noun surface:

```
main → run, db, routine, api, bind, ping, rule, env, sys
db   → query, exec, lock, unlock, snapshot, restore, dump, schema
```

Each subcommand defines required/optional args with types.
`--intent` is `required: true` on all write verbs.
`--dry-run`, `--json`, `--as` are universal flags.

---

## 2. The Surface (9 Nouns)

### `run` — Hot Path
```bash
capcli run <capability> [-p k=v]... [--dry-run] [--intent "..."] [--lock <ref>]
capcli search <query> [--trust X] [--env X]
capcli inspect <capability>
```
*Resolution:* exact match → prefix match → semantic search → "did you mean?". Works on routines, api verbs, views.

#### `inspect` output contract (`--json`)

Discovery without cost awareness is invitation to denial. `inspect` returns the full cost envelope in one JSON blob. The agent makes go/no-go from this alone — no second round-trip.

```json
{
  "capability": "refund_and_archive",
  "version": 17,
  "trust": "reviewed",
  "env": "prod",
  "manifest": [
    {"seq": 1, "primitive": "api.call", "target": "stripe.get_charge"},
    {"seq": 2, "primitive": "db.query", "target": "entities", "access": "read"},
    {"seq": 3, "primitive": "api.call", "target": "stripe.refund_charge"},
    {"seq": 4, "primitive": "db.txn", "children": [
      {"primitive": "db.exec", "target": "entities", "access": "update"}
    ]}
  ],
  "cost_envelope": {
    "tokens": {
      "file_size": 840,
      "max_result_tokens": 500,
      "params_schema_bytes": 120
    },
    "duration": { "max_seconds": 300, "p50_ms": 410, "p95_ms": 640 },
    "api": {
      "calls_per_run": 2,
      "providers": ["stripe.get_charge", "stripe.refund_charge"],
      "live_quota": {
        "stripe": {
          "limit": 100, "remaining": 42,
          "reset_at": "2026-01-15T14:30:00Z",
          "status": "ok"
        }
      },
      "static_spend": { "daily_budget_usd": 50.0, "remaining_usd": 37.6 },
      "sim_mode": {
        "stripe.get_charge": "sandbox",
        "stripe.refund_charge": "sandbox",
        "gov.file_tax_return": "prod-only",
        "hw.notify_device": "mock"
      },
      "prove_status": {
        "total_verbs": 4,
        "provable_in_sim": 3,
        "skipped": 1,
        "skipped_verbs": [
          {
            "verb": "gov.file_tax_return",
            "sim_mode": "prod-only",
            "reason": "government API has no test environment",
            "first_prod_calls_require_approval": 3
          }
        ]
      }
    },
    "db": { "writes_per_run": 2, "reads_per_run": 1, "max_rows_affected": 100 },
    "concurrency": { "max_ops_per_run": 50, "active_claims_on_target": 0 },
    "frequency": { "calls_last_hour": 3, "calls_per_minute_limit": 300 },
    "success": { "total_runs": 31, "success_rate": 0.97, "manifest_match_rate": 1.0 },
    "composition": {
      "max_nesting_depth": 3,
      "child_routines": ["archive_old_orders@3", "notify_team@1"],
      "budget_inheritance": "min",
      "effective_limits": {
        "max_ops": "min(50, session_remaining)",
        "max_duration_seconds": "min(300, session_remaining)",
        "spend_usd": "session_pool",
        "rate": "session_pool"
      }
    }
  },
  "budget_status": {
    "can_invoke_now": true,
    "blocking_reasons": [],
    "warnings": [],
    "sim_gaps": [
      "gov.file_tax_return is prod-only: cannot be proven in sim. First 3 prod calls require human approval."
    ],
    "cascade": {
      "session_ops_remaining": 488,
      "session_duration_remaining_ms": 555000,
      "session_spend_remaining_usd": 37.6,
      "session_rate_remaining": 287,
      "tightest_constraint": null
    }
  }
}
```

**Rules:**
- `live_quota` sourced from `_api_quota` table (kernel-updated from response headers)
- `budget_status.can_invoke_now` is the pre-flight verdict; `false` + `blocking_reasons` = don't call
- `warnings` are non-blocking (e.g., remaining below `warn_at_remaining`)
- All numbers are live at inspect-time, not cached
- Exit 0 always (inspect is a read); denial happens at `run`, not here

### `db` — World State
```bash
capcli db query <sql> [-p k=v]... [--limit N] [--count]
capcli db exec  <sql> [-p k=v]... --intent "..."        # auto-txn, WHERE+LIMIT enforced
capcli db lock <table>:<ref> --ttl 10m --reason "..."   # cross-agent coordination
capcli db unlock <target>
capcli db schema [--table]
capcli db snapshot | restore <id> | dump
```
*Note:* `db count` is dead. Use `db query --count`. Bulk pre-flights are AST-enforced or explicit queries.

### `routine` — Learned Procedures
```bash
capcli routine draft <name> [--reason]                   # create + validate + manifest extract
capcli routine prove <name> [-p k=v] [--env sim]         # test fingerprint vs manifest
capcli routine ship <name> --to reviewed|pinned [--env X] --reason "..."
capcli routine sweep [--since 30d]                       # consolidate report + propose
capcli routine stats <name> [--deep]                     # per-leaf cost attribution
capcli routine rollback <name> --to-version N
capcli routine retire <name> [--reason]
```

### `api` — External API Lifecycle

```bash
capcli api sync <provider> --from <url> [--interval 7d] [--dry-run]
capcli api diff <provider>                                   # spec drift since last sync
capcli api catalog <provider> [--state dormant|active|deprecated|retired]
capcli api activate <provider.verb> --intent "..."           # dormant → active (gate)
capcli api prove <provider.verb> [-p k=v] [--env sim]       # sandbox execution
capcli api ship <provider.verb> --to reviewed|pinned --reason "..."
capcli api stats <provider> [--deep] [--summary]            # per-verb or rollup
capcli api retire <provider.verb> [--reason]
capcli api deactivate <provider.verb> [--reason]            # active → dormant
capcli api rollback <provider.verb> --to-version N
capcli api list [--provider X] [--state X]
```

*Sync* pulls the full catalog from URL. Every verb enters as `state: dormant`. No `--pick`.
*Activate* is the gate — dormant verbs become callable at `trust: draft`.
*Prove* adapts to each verb's `sim_mode`:
- `sandbox` — executes against sandbox URL (`apis/<provider>.sim.yaml` overlay)
- `mock` — returns canned fixture from `apis/<provider>.mock.yaml`, no HTTP
- `dry-run` — validates params and policy, no HTTP, returns `simulated: true`
- `skip` — excluded from prove, routine proves without it
- `prod-only` — excluded AND authorizer denies execution in sim/dev
Prove reports partial manifest match when verbs are skipped. The gap is visible.
*Ship* is human-gated. Same trust ladder as routines.
*Stats* returns usage, reliability, cost, quota burn, provenance per verb.

### `bind` — Inbound Triggers
```bash
# Time
capcli bind cron <name> --run <cap> --cron "..." --intent "..."
# Async Events
capcli bind webhook <name> --provider X --event Y --run <cap> --intent "..."
# Sync Endpoints
capcli bind endpoint <routine@version> --auth api-key [--rate X]
# Management
capcli bind list | inspect | pause | resume | remove <name>
capcli bind keys issue <name> --principal partner:X      # human-gated
```

### Serve Lifecycle Split
`bind endpoint` registers a served endpoint. It does NOT start an HTTP server. The CLI configures; a daemon serves.

- **Registration (CLI):** `capcli bind endpoint <routine@version>` writes the endpoint config to workspace.db. Returns exit 0. No listener started.
- **Serving (Daemon):** `capcli sys serve --start` starts the HTTP listener (`Bun.serve()` or companion process). Reads endpoint configs from DB. Enforces same policy gates as `run`.
- **Lifecycle:** `capcli sys serve --stop | --restart | --status`. Governed by systemd/supervisord/docker in production.
- **Health check:** `capcli bind endpoint <name> --health` returns 200 if live, 503 if not. `sys doctor` checks all endpoints.
- **Request-level audit:** Every HTTP request to a serve endpoint generates an audit event:
  ```json
  {"event": "serve.request", "endpoint": "order_status", "routine": "get_order@12", "api_key_id": "key_abc", "principal": "partner:stripe", "params": {"id": "ORD-001"}, "response_status": 200, "duration_ms": 42}
  ```
  This closes the audit gap between CLI invocations (which are audited) and HTTP requests (which were not).

The architecture separates registration (CLI, synchronous, exit codes) from serving (daemon, persistent, concurrent). The kernel governs both identically.

### `ping` — Outbound Human IO
```bash
capcli ping notify <principal> <message> --channel X --intent "..."
capcli ping ask <principal> <question> --options a,b,c [--timeout 60m] --intent "..."
capcli ping list [--pending] | resolve <ask-id> --choice X | expire <ask-id>
```

### `rule` — Static Configuration
```bash
capcli rule show [--type schema|system-schema|policy|governance]
capcli rule diff [--git] [--type schema|system-schema]   # vs HEAD or live DB
capcli rule apply [--type schema] [--dry-run]            # world schema only; agent-triggered
capcli rule validate                                     # compile all layers; quad-lock; bad = no boot
```
*Note:* Schema migrations, policy reloads, and governance checks live here. One noun for all static truth.

*Note:* `rule apply --type schema` applies `schema.yaml` (world tables). `system-schema.yaml` is applied at boot or kernel upgrade only — agent cannot trigger it. `rule show --type system-schema` is a read; agent can inspect system table definitions.

### `env` — Switchable Worlds
```bash
capcli env new <name> [--seed prod] [--from-branch X]
capcli env use <name>                                    # atomic switch
capcli env list | inspect | doctor
capcli env merge <name> --into prod
capcli env remove <name>                                 # prod: multi-flag gated
```

### `sys` — Kernel & Audit
```bash
# Audit & Forensics
capcli sys audit tail [--follow] [--capability X] [--since 1h]
capcli sys audit trace <op-id> [--explain]               # causal DAG + denial reason
capcli sys audit query <sql> [-p k=v]                    # SQL against _audit mirror
capcli sys audit replay --from <ts|event-id> [--dry-run]

# Identity & Health
capcli sys agent register | list | revoke
capcli sys doctor                                        # boundaries, perms, drift
capcli sys backup [--push] | recover <commit>
capcli sys exec <cmd> [--sandbox]                        # jailed execution
```

---

## 3. Universal Flags

| Flag | Applies to | Meaning |
| :--- | :--- | :--- |
| `--dry-run` | all mutating verbs | full pipeline, zero effects — policy evaluated, plan returned |
| `--json` | everything | machine contract (versioned); agents always use it |
| `--intent "<why>"` | writes | mandatory; anti-junk validated; inherited chains accepted |
| `--reason "<why>"` | threshold crossings | justification for exceptions (bulk, overrides, promotions) |
| `--as <principal>` | everything | who this is ultimately for; scoped views require it |
| `--by <agent-id>` | mutating | acting identity; socket-verified |
| `--env <name>` | cross-world ops | explicit world targeting (default: current) |
| `--lock <ref>` | `run` | lease-based exclusivity with TTL |
| `--sandbox` | `sys exec` | bwrap/podman: net-none, ro binds |

---

## 4. The Agent's Daily Surface

A working agent lives in ~8 commands:

```bash
capcli search "..."                 # [harness] discover capabilities
capcli inspect <cap>                # [harness] understand params/manifest
capcli run <cap> -p ... --intent    # [harness] primary skill→routine bridge
capcli db query "..."               # [harness] read the world (always first)
capcli db exec "..." --intent       # [human] ⚠ skills must NEVER instruct direct db exec
capcli <any-mutating> --dry-run     # [harness] mandatory before first real effect
capcli sys audit trace <id> --explain # [harness] learn from denial
capcli routine stats <name> --deep  # [harness] per-leaf cost attribution
capcli rule show --type policy      # [harness] understand constraints
capcli api catalog stripe --state dormant  # [harness] discover available verbs
capcli api activate stripe.X --intent "..." # [harness] propose activation (human gates)
capcli api stats stripe.X --deep           # [harness] per-verb cost attribution
capcli search gaps --since 7d              # [harness] find unresolved searches
```

**Caller tag legend:**
-   `[harness]` — safe for skill-authored agent invocation
-   `[human]` — requires human/CI approval
-   `[both]` — context-dependent; skills may use read-only variants

---

## 5. What the Surface Refuses to Grow

-   **No `config set`** — config is files + git + review; no CLI write-path
-   **No `db count`** — `db query --count` or AST-enforced pre-flight
-   **No `claim` noun** — `db lock` or `run --lock`
-   **No `jail` noun** — `sys exec --sandbox`
-   **No `policy explain`** — `sys audit trace --explain` is the single source of truth
-   **No separate config nouns** — `rule` owns schema, policy, governance
-   **No separate trigger nouns** — `bind` owns cron, webhook, endpoint
-   **No `--verbose`** — `sys audit tail` is the verbosity knob
-   **No interactive modes** — approvals live in the harness
-   **No onboarding wizards** — the CLI returns exit codes and JSON; the harness renders approval dialogs, intent capture, and progression UI
-   **No `--force`** — exceptions are overrides in governance.yaml
-   **No `api import --pick`** — sync pulls everything; activation gates what's callable
-   **No `api create`** — verbs come from OpenAPI sync, never hand-authored
-   **No `api call`** — invocation is `ctx.api.call` inside routines or `run`; no direct CLI egress
-   **No `budget` noun** — budget info lives in `inspect` cost_envelope and denial messages; no separate budget command
-   **No `--override-budget`** — budget exceptions are governance overrides, never flags
-   **No `rule apply --type system-schema`** — system schema is kernel-upgraded, never agent-triggered
-   **No `schema edit`** — agent edits schema.yaml via native fs; no CLI write-path for config
-   **No `api simulate`** — sim behavior is declared per-verb via `sim_mode`; no separate simulation command
-   **No `--force-prod`** — `prod-only` verbs are physically denied in sim/dev by the authorizer; no flag overrides this
-   **One event per verb** — if a command can't be one audit event, it's two commands

---

## The One-Liner

> **9 nouns, universal flags, exit codes as law, and a registry that flattens everything into `run` — the command surface is small enough to memorize, deep enough that nothing escapes the gate, and honest enough that every verb is an audit event.**