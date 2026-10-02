# Reference

Reference is where exactness wins over pedagogy. The rest of the docs teach; these pages testify. If a friendlier page upstream simplified the truth, this is where you come to check it against the contract.

No journeys. No mental models. What the kernel actually does, stated precisely enough to argue with.

---

## The contracts

| Page | What it nails down |
|---|---|
| [cli.md](cli.md) | Canonical grammar — `capcli <noun> <verb> [target] [--flags]`, the ten nouns, the frozen twelve flags, aliases, banned flags |
| [output.md](output.md) | Output law — the `[env:tier]` prefix on all streams, tables vs `--json`, the return envelope, `--out` receipts |
| [exit-codes.md](exit-codes.md) | The six exit codes and the state guarantee each one carries |
| [audit.md](audit.md) | Audit structures and inspection surfaces — `_audit`, the JSONL mirror, the causal DAG |
| [errors.md](errors.md) | Every denial rule id attested in the specs, plus the anatomy of a denial |
| [limits.md](limits.md) | Hard limits & ceilings — every number the kernel will enforce on you, by noun |

## The commands

One page per noun. Ten nouns, ten pages, zero invented verbs.

| Noun | Domain |
|---|---|
| [run](commands/run.md) | The hot path: execute capabilities, `sql`, `search`, `inspect` |
| [db](commands/db.md) | Storage: unified SQL, locks, schema, snapshots |
| [routine](commands/routine.md) | Versioned, sandboxed scripts and their entire lifecycle |
| [api](commands/api.md) | Third-party API catalogs, OpenAPI sync, verb lifecycles |
| [bind](commands/bind.md) | Triggers: crons, webhooks, served endpoints, exports, partner keys |
| [ping](commands/ping.md) | Human interaction: notify, structured ask, resolve |
| [rule](commands/rule.md) | The YAML compiler: show, diff, apply, validate |
| [env](commands/env.md) | Worlds: provision, switch, merge, remove |
| [sys](commands/sys.md) | Kernel instruments: audit, vault, doctor, backup, sandbox, daemon |
| [doc](commands/doc.md) | Reading and outlining capability pointers |

---

## Conventions

Every transcript in this section is real output, verbatim. First lines carry the verdict — `[env:tier]  <subject>  ✓  <detail>` — and failures say `✗ exit <n>` with the rule id, the caret line, `state_modified: false`, and a `remedy`. If you learn the conventions once, every page here reads the same way.

---

## The authority chain

CANS (`cans/*.md`) is the factual authority; these pages restate it exactly. Where the spec is silent, the pages say so out loud instead of improvising — silence is a fact too, and this is the one section of the docs that treats it like one.

---

**Start with the grammar** → [cli.md](cli.md)

**Decode a failure** → [exit-codes.md](exit-codes.md) · [errors.md](errors.md) · [limits.md](limits.md)
