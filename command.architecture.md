# capcli-command.architecture.md *(final v2 — primitive-aware)*

> The entire CLI: **one shape, universal flags, frequency-based depth, exit codes as law.** Small enough to memorize, deep enough that nothing needs escaping.

---

## 1. Design Laws

1. **One shape forever**: `capcli <noun> <verb> [target] [--flags]`. No exceptions. Hot verbs alias-promoted to top level.
2. **Every mutating verb accepts**: `--dry-run`, `--json`, `--intent "<why>"`, `--as <principal>`. Reads get `--json` + `--as`.
3. **Everything resolves through the registry** — db ops, routines, api verbs, views are all *capabilities*; `run`/`search`/`inspect` work identically on all.
4. **Frequency determines depth**: verbs called 1000×/day live top-level; 10×/day get one noun; 1×/week get full noun-verb.
5. **Output contract**: humans get pretty tables; agents pass `--json` (versioned machine contract). Every output prefixes `[env]` — prod in red.
6. **Exit codes are law** — scripts and agents branch on them, never parse stdout:

| Code | Meaning |
|---|---|
| `0` | ok |
| `2` | policy-denied |
| `3` | validation-failed (incl. governance, missing intent) |
| `4` | runtime-error |
| `5` | audit-write-failed (= nothing ran) |

---

## 2. Hot Path (top-level)

```bash
capcli run <capability> [-p k=v]... [--dry-run] [--intent "..."]
capcli search <query> [--trust X] [--env X]
capcli inspect <capability>
```

**Resolution rule for `run`**: exact match → prefix match → semantic search → "did you mean?" with top 3. Works on routines, api verbs, views — one verb, every capability type.

---

## 3. `db` — SQL primitives

```bash
capcli db query <sql> [-p k=v]... [--limit N]
capcli db exec  <sql> [-p k=v]... --intent "..."        # auto-txn, WHERE+LIMIT enforced
capcli db count <table> [--where <sql>]                  # bulk pre-flight
capcli db schema [--table]
capcli db snapshot
capcli db restore <snapshot-id> [--dry-run]
capcli db dump                                           # → world.sql (git-committed)
```

---

## 4. `routine` — learned procedures

```bash
capcli routine new <name> [--reason]                     # duplicate-similarity warned
capcli routine validate <name>                           # AST + policy + governance + manifest extraction
capcli routine manifest <name> [--version N]             # view declared primitive sequence
capcli routine test <name> [-p k=v] [--env sim]          # proves manifest vs fingerprint
capcli routine promote <name> --to reviewed|pinned [--env X] --reason "..."
capcli routine stats <name> [--deep]                     # --deep: per-leaf duration/spend/failure
capcli routine rollback <name> --to-version N
capcli routine retire <name> [--reason]
```

---

## 5. `consolidate` / `governance` — registry hygiene

```bash
capcli consolidate report [--since 30d]                  # now includes fingerprint clusters
capcli consolidate propose --cluster <names> --into <name> [--deprecate ...]
capcli consolidate apply <proposal>                      # human-gated
capcli consolidate status

capcli governance show                                   # effective limits
capcli governance validate
capcli governance limits <routine>
```

---

## 6. `api` — external capabilities (egress)

```bash
capcli api import <provider> --from apis/<p>.yaml [--dry-run]
capcli api list <provider>
capcli api call <provider>.<verb> [-p k=v]... --intent "..." [--idempotency-key <k>]
capcli api call <provider>.<verb> --verify-key <k>       # what actually landed?
capcli api reload <provider>                             # re-import + secret rotation
```

---

## 7. `env` — switchable worlds

```bash
capcli env new <name> [--seed prod] [--from-branch X]
capcli env use <name>                                    # atomic switch
capcli env list                                          # current marked, drift flags
capcli env inspect <name>
capcli env doctor                                        # unmerged routines, secret leaks, stale sim
capcli env merge <name> --into prod
capcli env remove <name>                                 # prod: multi-flag gated
```

---

## 8. `schedule` / `watch` / `serve` / `notify` / `ask` — the hands

```bash
# schedule — time
capcli schedule add <name> --run <cap> --cron "..." --intent "..." [-p k=v]
capcli schedule list | inspect <name> | pause | resume | remove
capcli schedule fire <name> [--dry-run]

# watch — inbound events (async)
capcli watch add <name> --provider X --event Y --match <jsonpath> \
    --run <cap> --map k=<jsonpath>... --intent "..."
capcli watch list | inspect | test <name> --payload '{...}' | pause | resume | remove
capcli watch replay <event-id> [--dry-run]
capcli watch dead-letter list | inspect | replay | purge

# serve — inbound requests (sync)
capcli serve add <routine@version> --auth api-key [--rate X] [--allow-writes]
capcli serve list | openapi [--routine X] | remove
capcli serve keys issue <name> --principal partner:X     # human-gated
capcli serve keys revoke <key-id>

# notify + ask — humans
capcli notify <principal> <message> --channel X --intent "..."
capcli ask <principal> <question> --options a,b,c [--timeout 60m] --intent "..."
capcli ask list [--pending] | resolve <ask-id> --choice X | expire <ask-id>
```

---

## 9. `policy` / `schema` — governance contracts

```bash
capcli policy validate                                   # compile both layers; bad = no boot
capcli policy explain <sql|capability>                   # the WHY — the learning signal
capcli policy diff                                       # vs git HEAD

capcli schema show [--table]
capcli schema diff                                       # YAML vs live (PRAGMAs, no parser)
capcli schema migrate [--dry-run]                        # snapshot-first, forward-only
capcli schema import <db>                                # bootstrap: live DB → schema.yaml
```

---

## 10. `audit` — the event stream

```bash
capcli audit tail [--follow] [--capability X] [--principal X] [--agent X] [--since 1h] [--denied]
capcli audit show <event-id>
capcli audit query <sql> [-p k=v]                        # SQL against _audit mirror + primitive views
capcli audit sample --capability X [--limit N]           # real-param extraction for tests
capcli audit verify [--git]                              # hash chain + git tamper check
capcli audit replay --from <ts|event-id|prod> [--dry-run] [--skip-external]
capcli audit trace <op-id>                               # causal DAG walk
```

Mirror views queryable via `audit query`: `routine_fingerprints`, `primitive_failures`, `primitive_cost`, `shared_subsequences`.

---

## 11. `agent` / `claim` — identity & coordination

```bash
capcli agent register <name> --harness X --as <principal>
capcli agent list [--active]
capcli agent revoke <agent-id>

capcli claim <table>:<ref> --ttl 10m --reason "..."
capcli claim release <target>
capcli claim list
```

`--by <agent-id>` is universal on mutating verbs — validated against socket identity, never trusted from args.

---

## 12. `sys` / `jail` — kernel health & physics

```bash
capcli sys doctor                                        # boundaries, perms, config compile, drift
capcli sys status                                        # version, schema_version, registry size, env

capcli sys snapshot                                      # dump db + stage world
capcli sys commit [--push]                               # manual backup commit
capcli sys recover <commit> [--dry-run]                  # restore world-state from history
capcli sys backup-status                                 # last commit, last push, drift

capcli jail exec <cmd>                                   # bwrap/podman: net-none, ro binds
capcli jail doctor                                       # is the physics actually in place?
```

---

## 13. Universal Flags

| Flag | Applies to | Meaning |
|---|---|---|
| `--dry-run` | all mutating verbs | full pipeline, zero effects — policy evaluated, plan returned |
| `--json` | everything | machine contract (versioned); agents always use it |
| `--intent "<why>"` | writes | mandatory; anti-junk validated; inherited chains accepted |
| `--reason "<why>"` | threshold crossings | justification for exceptions (bulk, overrides, promotions) |
| `--as <principal>` | everything | who this is ultimately for; scoped views require it |
| `--by <agent-id>` | mutating | acting identity; socket-verified |
| `--env <name>` | cross-world ops | explicit world targeting (default: current) |

---

## 14. Verb Census

| Depth | Count | Examples |
|---|---|---|
| Top-level | 3 | `run`, `search`, `inspect` |
| Nouns | 17 | db, routine, consolidate, governance, api, env, schedule, watch, serve, notify, ask, policy, schema, audit, agent, claim, sys, jail |
| Total verbs | ~100 | one audit event type each |

---

## 15. What the Surface Refuses to Grow

- **No `config set`** — config is files + git + review; no CLI write-path (agent self-grant hole)
- **No `db delete`/`db update` specials** — `db exec` + policy is the gate; special verbs invite special bypasses
- **No `--verbose`** — `audit tail` is the verbosity knob
- **No interactive modes** — the kernel serves agents and scripts; approvals live in the harness
- **No `--force`** — exceptions are overrides in governance.yaml, committed and reviewed
- **One event per verb** — if a command can't be one audit event, it's two commands

---

## 16. The Agent's Daily Surface

Everything above exists, but a working agent lives in ~10 commands:

```bash
capcli search "..."                 # discover
capcli inspect <cap>                # understand
capcli run <cap> -p ... --intent    # act
capcli db query "..."               # read the world
capcli db exec "..." --intent       # change the world
capcli policy explain "..."         # learn from denial
capcli audit trace <op-id>          # understand consequences
capcli routine manifest <name>      # see declared primitives
capcli routine stats <name> --deep  # per-leaf cost attribution
capcli routine new/validate/test    # consolidate what it learned
```

The other ~90 verbs are governance, lifecycle, and recovery — touched occasionally, available always.

---

## The One-Liner

> **One shape, universal flags, exit codes as law, and a registry that flattens everything into `run` — the command surface is small enough to memorize, deep enough that nothing escapes the gate, and honest enough that every verb is an audit event.**