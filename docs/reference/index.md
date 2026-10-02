# Reference

Exactness beats pedagogy here. No journeys, no metaphors — just the contract.

If a command exists, it has a page. If a page exists, the command is real. Nothing here is aspirational, nothing is invented, and everything is the kernel's actual behavior. When a human page and this section disagree, believe this section — then file a docs bug.

---

## The grammar

```text
capcli <noun> <verb> [target] [--flags]
```

Ten nouns. That's the whole surface. Details: [cli.md](cli.md).

---

## Command pages, one per noun

| Noun | Runs… |
|---|---|
| [`run`](commands/run.md) | Capabilities, SQL, search, inspection |
| [`db`](commands/db.md) | Schema, locks, snapshots |
| [`routine`](commands/routine.md) | The routine lifecycle |
| [`api`](commands/api.md) | External API catalogs & verbs |
| [`bind`](commands/bind.md) | Crons, webhooks, endpoints |
| [`ping`](commands/ping.md) | Humans: alerts & structured questions |
| [`rule`](commands/rule.md) | YAML compile, diff, apply |
| [`env`](commands/env.md) | Worlds: create, switch, merge, remove |
| [`sys`](commands/sys.md) | Doctor, audit, vault, backup, recovery, daemon |
| [`doc`](commands/doc.md) | Reading workspace docs |

## Cross-cutting contracts

| Page | The exact truth about… |
|---|---|
| [output.md](output.md) | Output formats, prefixes, `--json`, `--out` |
| [exit-codes.md](exit-codes.md) | 0, 2, 3, 4, 5, 6 — the integer law |
| [audit.md](audit.md) | The `_audit` spine and its query surfaces |
| [errors.md](errors.md) | Documented failures & denials |
| [limits.md](limits.md) | Hard limits & ceilings (the physics of "no") |

---

## Conventions used on every page

- Output prefix is always `[env:tier]` — e.g. `[dev:tier_1]`.
- `exit 2` blocks are *pre-execution* denials: `state_modified: false`, guaranteed.
- `--json` exists wherever a machine consumer needs a pure envelope.
- Banned commands are listed as **banned** — they exist in this table so you stop asking. (Yes, `capcli api call` is banned. Yes, on purpose. No, not even "just this once.")
