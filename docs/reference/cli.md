# CLI Grammar

```text
capcli <noun> <verb> [target] [--flags]
```

Ten nouns, a handful of verbs each, one grammar. The CLI is small because the surface of a governed kernel *should* be small — every command is a door, and doors need keepers.

---

## The ten nouns

```text
run      db      routine   api     bind
ping     rule    env       sys     doc
```

| Noun | Path | One-liner |
|---|---|---|
| `run` | The hot path | Execute capabilities, SQL, search, inspect |
| `db` | Storage path | Schema, locks, snapshots, restore |
| `routine` | Capability lifecycle | new → prove → ship → sweep → retire |
| `api` | The wire path | Sync catalogs, activate & promote verbs |
| `bind` | Trigger path | Crons, webhooks, endpoints, keys |
| `ping` | Human path | notify, ask, resolve |
| `rule` | Governance path | show, diff, validate, apply (YAML compile) |
| `env` | World path | new, use, list, merge, remove |
| `sys` | System path | doctor, audit, vault, backup, serve |
| `doc` | Document path | read, outline |

Ergonomic alias: `capcli apply` = `capcli rule apply schema`. That's the only one. Aliases multiply; kernels don't.

## Aliases on the hot path

```bash
capcli search "<q>"      # ≡ capcli run search "<q>"
capcli inspect <ptr>     # ≡ capcli run inspect <ptr>
capcli sql "<query>"     # ≡ capcli run sql "<query>"
```

## Universal flags

| Flag | Effect |
|---|---|
| `--json` | Pure machine envelope: domain, culprit, remedy, state_modified |
| `--as <principal>` | Execute as a scoped principal (missing principal on scoped views = `exit 3`) |
| `-m "<intent>"` / `--intent` | Causal intent declaration — mandatory on mutations |
| `-p k=v` | Bound parameters (repeatable) |
| `--dry-run` | Full gate stack, zero execution |
| `@<path>` / `@-` | File/stdin argument escaping (shell-proof, ARG_MAX-proof) |

## Output laws

- Every output line is prefixed `[env:tier]`. You always know which world you're in, including the times you'd rather not know.
- `--help` on the root is capped at 6 lines and points at `search`. Dumping full noun trees in help is banned — discoverability belongs to the registry, not to a wall of text.
- Humans get tables; machines pass `--json` and get envelopes. Never both mangled into one stream.
- Tier 2 hosts get a standing banner: `host.degraded_isolation`.

## Caller categories

Commands are labeled for who may run them:

| Label | Meaning |
|---|---|
| `[harness]` | Safe for autonomous agent execution |
| `[human]` | Requires interactive human approval |
| `[both]` | Depends on flags |

Your harness should check the category before it decides a command is "supported." The kernel checks it too, with less diplomacy.

## Banned (documented so you stop grepping for them)

```text
capcli config set              # policy mutation at runtime is forbidden — edit YAML, git commit
capcli db count|query|exec     # retired; use the unified `capcli sql`
capcli claim                   # retired; use `db lock` or `run --lock`
capcli jail                    # retired; use `sys exec --sandbox`
capcli policy explain          # retired; use `sys audit trace --explain`
capcli api call                # banned; use `run` or ctx.api.call inside guest code
capcli api import --pick       # banned; verbs sync in full
capcli budget                  # banned; use the inspect cost envelope
--verbose                      # banned; use `sys audit tail`
--force / --override-budget / --force-prod   # banned bypass flags. Always.
```

Direct DDL via `capcli sql "ALTER TABLE …"` is also banned — all DDL originates from `schema.yaml` through the 5-Gate compiler. An agent with ad-hoc `ALTER` power is a Tuesday away from a legend.

---

**Per-noun exact contracts** → [commands/](commands/)
