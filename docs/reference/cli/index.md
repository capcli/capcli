# Command Reference

Ten nouns, one shape: `capcli <noun> <verb> [target] [--flags]`. Root `--help` is capped at six lines and points you at `capcli search` — dumping full noun trees is banned. Every output stream carries the `[env:tier]` prefix (e.g. `[dev:tier_2]`, `[prod:tier_1]`); humans get tables, machines pass `--json`.

## The ten nouns

| Noun | File | Owns |
|---|---|---|
| `run` | [run.md](run.md) | The hot path: execute, unified `sql`, `search`, `inspect`, gap detection. |
| `db` | [db.md](db.md) | Storage: SQL, lease locks, schema introspection, snapshots. |
| `routine` | [routine.md](routine.md) | Capability lifecycle: scaffold → prove → ship → sweep → retire. |
| `api` | [api.md](api.md) | External provider catalogs and verb lifecycles. |
| `bind` | [bind.md](bind.md) | Inbound triggers: crons, webhooks, served endpoints. |
| `ping` | [ping.md](ping.md) | Human IO: notifications and structured asks. |
| `rule` | [rule.md](rule.md) | Compile, diff, apply the declarative YAML blueprints. |
| `env` | [env.md](env.md) | Worlds: provision, switch, merge, deprovision dev/sim/prod. |
| `sys` | [sys.md](sys.md) | Kernel: diagnostics, audit spine, vault, identity, recovery, daemon. |
| `doc` | [doc.md](doc.md) | Progressive disclosure over `doc://` documents. |

## Caller categories

Every verb in this reference is tagged:

| Tag | Meaning |
|---|---|
| `[harness]` | Safe for autonomous agent execution. |
| `[human]` | Requires interactive human approval. |
| `[both]` | Dual execution permitted depending on flags. |

## Universal flags

Frozen at exactly twelve — no noun ever grows its own, and the bypass flags (`--force`, `--force-prod`, `--override-budget`, `--verbose`) do not exist ([invariants](../limits.md#invariants)).

**Global — work on every noun:**

| Flag | Meaning |
|---|---|
| `--json` | Stable machine-readable output envelope. |
| `--as <principal>` | Target execution principal for scoped access. |
| `--env <name>` | Environment override (defaults to the sticky context set by `env use`). |
| `-m`, `--intent "<why>"` | Causal motivation for mutating actions. |
| `--workspace <path>` | Project root anchor (overrides `CAPCLI_WORKSPACE`). |
| `--session <token>` | Cryptographic session handle binding principal and frame. |
| `--in <path>` | File or stdin source for the primary command payload. |
| `--out <path>` | Writes the payload to disk; stdout gets a token-lean receipt. |

**Mutating:**

| Flag | Meaning |
|---|---|
| `--dry-run` | Plan the execution without applying state changes. |
| `--reason "<why>"` | Threshold-crossing justification (bulk gates, near-duplicate drafts). |
| `--by <agent-id>` | Acting identity, verified via process credentials. |
| `--lock <ref>` | Exclusive claim lease on a run. |

**Scoped modifier:** `--sandbox` — the jail wrapper, valid on `sys exec` only.

**The `@` law:** every string argument (`-p`, `--intent`, `--reason`, queries) accepts `@<path>` to load from file or `@-` for stdin — `-m @intent.txt`, `-p data=@payload.json`. This bypasses ARG_MAX and shell escaping entirely.

**The `-m` law:** intent is required on every mutation — SQL writes, `api activate`/`ship`, `routine ship`, `bind cron`/`webhook`/`endpoint`, `env merge`/`remove`, `ping ask`/`notify`. Missing intent is an [exit 3](../exit-codes.md#exit-3).

## URP pointer standard

Everything addressable gets a typed pointer. On disk in development you use file notation (`routines/refund.ts`); the moment it is registered in the kernel, it is always the URP form:

| Scheme | Points to | Example |
|---|---|---|
| `cap://` | Routines and API verbs | `cap://order_refund@2` |
| `db://` | Tables and views | `db://orders` |
| `bind://` | Triggers — crons, webhooks, endpoints | `bind://nightly_sync` |
| `vault://` | Credential references | `vault://stripe_secret` |
| `ask://` | Pending human prompts | `ask://ask_7f2c` |

The full taxonomy (including `doc://`, `audit://`, `snap://`, `quota://`, `policy://`, `tpl://`) is enumerated in [cans/action.md](../../../cans/action.md) — Global pointer registry.

## Retired verbs

`db count`, `db query`, `db exec` (use `sql`); `claim` (use `db lock`); `jail` (use `sys exec --sandbox`); `policy explain` (use `sys audit trace --explain`); `--verbose` (use `sys audit tail`); `api call` (use `run`); `budget` (use `inspect`); `api import --pick`; `config set`. The per-noun files mark each with the replacement.
