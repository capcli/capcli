# CLI Grammar

Canonical CLI grammar. Where exactness wins over pedagogy — and where the pedagogy was never that great to begin with.

```bash
capcli <noun> <verb> [target] [--flags]
```

Ten nouns. One shape. No flags that only exist on Tuesdays.

---

## The ten nouns

| Noun | Domain | What it owns |
|---|---|---|
| **`run`** | hot path | Execute a capability; reach `sql`, `search`, `overview`, `inspect` |
| **`db`** | storage | Unified SQL, table locks, schema views, snapshots and restore |
| **`routine`** | automation | Author, prove, ship, profile, roll back, sweep, retire |
| **`api`** | egress | Sync OpenAPI catalogs; verb lifecycle from dormant to retired |
| **`bind`** | triggers | Crons, webhooks, served endpoints, exports, partner keys |
| **`ping`** | humans | Notify, structured ask, resolve, expire |
| **`rule`** | governance | Show, diff, apply, validate — the compiler door |
| **`env`** | worlds | Provision, switch, inspect, merge, remove environments |
| **`sys`** | kernel | Audit spine, inbox, identities, vault, doctor, backup, sandbox, daemon |
| **`doc`** | context | Read and outline pointers without flooding your context window |

Every noun has its own page under `commands/` with the full verb table. If a verb isn't on its page, it doesn't exist.

---

## Universal flags — the frozen twelve

| Flag | Contract |
|---|---|
| `--json` | Stable machine-readable output |
| `--as <principal>` | Target execution principal for scoped access |
| `--env <name>` | Environment override; defaults to the sticky context set by `env use` |
| `-m`, `--intent "<why>"` | Causal motivation for mutating actions; short flag supported |
| `--workspace <path>` | Project root anchor; overrides `CAPCLI_WORKSPACE` |
| `--session <token>` | Cryptographic session handle binding principal and frame |
| `--in <path>` | File or stdin (`@-`) source for the primary command payload |
| `--out <path>` | Payload writes to disk; stdout returns a token-lean summary |
| `@<path>` / `@-` | At-expansion on every string argument (`-p`, `--intent`, `--reason`, queries) |
| `--dry-run` | Plan the execution; apply nothing |
| `--reason "<why>"` | Threshold-crossing justification; inline text or file |
| `--by <agent-id>` | Acting identity — verified via process credentials, never self-declared |

Twelve. Frozen. No per-noun flag growth — the surface does not sprawl while you're looking away.

Two flags are scoped rather than universal:

| Flag | Scope | Contract |
|---|---|---|
| `--lock <ref>` | `run` | Exclusive claim lease on the run |
| `--sandbox` | `sys exec` | Jail wrapper for the one-shot command |

---

## Aliases

| Alias | Expands to |
|---|---|
| `capcli sql "<query>"` | The unified AST-gated query & execution surface |
| `capcli search <query>` | `capcli run search` |
| `capcli inspect <ptr>` | `capcli run inspect` |
| `capcli apply` | `capcli rule apply schema` |

---

## The help stub law

Root `--help` is capped at six lines and points to `search`. Dumping full noun trees from help is banned — the registry is the discovery surface, not the manual. Want to know what exists? Ask the kernel:

```bash
$ capcli run search "order"
```

```
[dev:tier_1]  3 results

  cap://dispatch_order@4     routine    pinned    "Dispatch paid order to carrier"
  cap://order_refund@2       routine    reviewed  "Refund and archive cancelled order"
  db://orders                table      —         "Core order state"
```

Typed pointers, trust rungs, descriptions under 60 tokens each. That's discovery — no manual required.

---

## Banned flags

Passing any of these is an immediate syntax error. They are not escape hatches; they are typographic fiction:

| Flag | Why it doesn't exist |
|---|---|
| `--force` | There is no force. There is policy. |
| `--override-budget` | Budgets are physics, not suggestions |
| `--force-prod` | Prod is entered by promotion, never by flag |
| `--verbose` | The audit spine is the verbosity: `sys audit tail` |

---

## Banned and retired operations

| Operation | Status | Use instead |
|---|---|---|
| `config set` | banned | Edit the YAML and git commit |
| `db count` / `db query` / `db exec` | retired | Unified `capcli sql` |
| `claim` | retired | `db lock` or `run --lock` |
| `jail` | retired | `sys exec --sandbox` |
| `policy explain` | retired | `sys audit trace --explain` |
| `api call` | banned | `capcli run`, or `ctx.api.call` inside guest code |
| `api import --pick` | banned | `api sync` — verbs are synced in full |
| `budget` | banned | The `inspect` cost envelope |
| Manual schema edits | banned | Edit `schema.yaml`, then `rule apply` |
| Direct system-schema apply | banned | Kernel upgrades manage it |

---

**Exact output shapes?** → [output.md](output.md)

**What each exit code guarantees?** → [exit-codes.md](exit-codes.md)

**Full verb tables, noun by noun?** → [index.md](index.md)
