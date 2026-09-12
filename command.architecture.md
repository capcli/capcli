# command.architecture.md *(final v3 — collapsed surface)*

> The entire CLI: **8 nouns, universal flags, frequency-based depth, exit codes as law.** Small enough to memorize, deep enough that nothing escapes the gate. Zero redundancy.

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

---

## 2. The Surface (8 Nouns)

### `run` — Hot Path
```bash
capcli run <capability> [-p k=v]... [--dry-run] [--intent "..."] [--lock <ref>]
capcli search <query> [--trust X] [--env X]
capcli inspect <capability>
```
*Resolution:* exact match → prefix match → semantic search → "did you mean?". Works on routines, api verbs, views.

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

### `ping` — Outbound Human IO
```bash
capcli ping notify <principal> <message> --channel X --intent "..."
capcli ping ask <principal> <question> --options a,b,c [--timeout 60m] --intent "..."
capcli ping list [--pending] | resolve <ask-id> --choice X | expire <ask-id>
```

### `rule` — Static Configuration
```bash
capcli rule show [--type schema|policy|governance]
capcli rule diff [--git]                                 # vs HEAD or live DB
capcli rule apply [--type schema] [--dry-run]            # migrate / reload
capcli rule validate                                     # compile all layers; bad = no boot
```
*Note:* Schema migrations, policy reloads, and governance checks live here. One noun for all static truth.

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
-   **One event per verb** — if a command can't be one audit event, it's two commands

---

## The One-Liner

> **8 nouns, universal flags, exit codes as law, and a registry that flattens everything into `run` — the command surface is small enough to memorize, deep enough that nothing escapes the gate, and honest enough that every verb is an audit event.**