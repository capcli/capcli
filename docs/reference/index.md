# Reference

Hard contracts. Zero prose.

| File | Contract |
|---|---|
| [limits.md](limits.md) | Every cap, ceiling, and floor — the single source of truth for numbers. |
| [exit-codes.md](exit-codes.md) | The six-code exit contract and the anatomy of a denial. |
| [audit.md](audit.md) | The `_audit` event schema, redaction rules, and query surfaces. |
| [schemas.md](schemas.md) | Micro-DDL shorthand and the system-table protection matrix. |
| [cli/](cli/index.md) | The command surface — ten nouns, universal flags, caller categories. |

## URP pointer standard

Everything addressable gets a typed pointer. On disk in development: file notation (`routines/refund.ts`). Registered in the kernel: always the URP form.

| Scheme | Points to | Example |
|---|---|---|
| `cap://` | Routines and API verbs | `cap://order_refund@2` |
| `db://` | Tables and views | `db://orders` |
| `bind://` | Triggers — crons, webhooks, endpoints | `bind://nightly_sync` |
| `vault://` | Credential references | `vault://stripe_secret` |
| `ask://` | Pending human prompts | `ask://ask_7f2c` |

Full taxonomy (including `doc://`, `audit://`, `snap://`, `quota://`, `policy://`, `tpl://`) → [cans/action.md](../../cans/action.md) — Global pointer registry.
