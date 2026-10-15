# World

A World is the governed workspace-state domain in which work happens: one set of domain tables, one schema declaration, one audit history, one trust population. Everything an agent reads, writes, proves, or promotes lives inside exactly one World at a time.

A World is a container for work, not an explanation for everything. Readers arrive from a task, a capability, or a recovery problem as often as from a blank directory.

---

## The blank World

A fresh workspace holds zero domain tables. This empty state is a normal starting point, not an error: the kernel, the audit spine, and the system tables already exist, and the domain waits for a declaration. Genesis work — declaring entities, state transitions, and external wires in `schema.yaml` — turns the blank World into a working one. See [Start](../start/index.md) for the first-task path through that moment.

Nothing in the blank World needs invention. `capcli db schema` reports the empty domain honestly, and discovery surfaces return empty result sets rather than placeholder content.

---

## The storage trinity

Three artefacts carry a World:

| Artefact | Role |
|---|---|
| `workspace.db` | Dedicated source of truth for domain tables, claims, and local state; partitioned per environment at `envs/<name>/workspace.db`, gitignored as a binary |
| `audit.db` | Isolated, append-only SQLite database holding the `_audit` ledger, free of WAL lock contention with domain writes |
| `world.sql` | Deterministic DDL and seed dump of the World; identical Worlds produce identical bytes, committed to git as the readable schema history |

Binary VACUUM snapshots sync to object storage for disaster recovery. Agents never touch the database files directly: the workspace sits behind the daemon IPC socket, and the kernel mediates every read and write.

---

## The dual schema

Two declarations compile into one physical database:

- **`schema.yaml`** — agent-owned. Domain tables, read views, and policy-vetted triggers, authored in the dev worktree and compiled through the validation gates.
- **`system-schema.yaml`** — kernel-owned. Thirteen managed system tables (`_audit`, `claims`, `routine_stats`, `_suspended_tasks`, and kin), read-only to agents, upgraded only by release binaries, hash-verified at every boot.

Manual SQL DDL editing sits outside the model. Declaration changes travel the migration pipeline in [Migration](../guides/migration.md).

Views declared in `schema.yaml` act as the read source of truth for routines. Multi-tenant tables tagged `tenant: true` stay blocked from raw queries; access runs through `scoped: principal` views carrying a mandatory `:principal` bind, or through the structured `ctx.db.mutate` ownership assertion.

---

## Environments inside a World

Environments — dev, sim, prod — isolate the state substrate while sharing the declaration. Dev carries the draft trust baseline, sim serves as the reviewed proving ground, and prod enforces the pinned production floor. Routines cross environments through the kernel env merge pipeline, never through file copying.

An environment arrives empty from `capcli env new`, or populated from a blueprint:

```bash
capcli pack scaffold pack://world/<name> <target> [-p k=v]
```

World packs bundle schema and seed data under a signed manifest. Imported routines, views, and verbs register at draft trust with zero promotional credit, and Gate 5 rehearses a dry-run migration on a temporary snapshot before any pack content lands on disk.

---

## Packs and the registry

This page carries the pack lifecycle end to end. Authoring a blueprint, packing it, publishing it, and hydrating a workspace from it are separate acts with separate commands.

### Author and freeze a blueprint

```bash
capcli pack new <name> --type routine|world
capcli rule validate [target]
capcli pack bundle <dir> [--out bundle.cap]
```

`pack new` scaffolds the blueprint (`capcli-pack.yaml` plus starter code) under `packs/`. `rule validate [target]` lints the bundle before any workspace contact: syntax, the petgraph acyclic check, and the pack manifest. `pack bundle` freezes the blueprint into an immutable SHA-256-signed `.cap` bundle. World bundles carry a 5MB ceiling.

### Publish to the registry

The registry is a dedicated PR-driven repository. An author PR merges only on a fully green gate: `rule validate` on `capcli-pack.yaml`, the shape caps (cyclomatic complexity at most 10, at most 2,000 tokens, at most 8 parameters), a headless sandbox simulation, and a frozen bundle build with its SHA-256 computed. A merged PR triggers a release that publishes the immutable `bundle.cap` asset and appends an entry — pointer, version, SHA-256, bundle URL, minimum kernel version, policy version — to the registry `index.json`.

### Sync, import, scaffold

```bash
capcli pack sync
capcli inspect pack://registry/<kind>/<name>@<ver>
capcli pack import <urp|url|file> [--sha256 <hash>]
capcli pack scaffold pack://registry/<kind>/<name>@<ver> <target-name> [-p k=v]
```

1. **`pack sync`** refreshes the local cache of the registry `index.json`.
2. **`capcli inspect`** resolves the `pack://registry/*` pointer against the cached index and returns the pre-flight envelope: required typed inputs, declared capabilities, seed row count. The same `inspect` surface pre-flights local `pack://routine/*` and `pack://world/*` blueprints.
3. **`pack import`** fetches the `.cap` bundle into the isolated `/scratch` wire sandbox. Streams exceeding 5MB abort on arrival. The kernel verifies the stream SHA-256 against the index entry or the `--sha256` flag before any archive extraction; a mismatch refuses intake at exit 3. Direct URLs enter only in pinned form — a release asset URL carrying `#sha256=<hex>`; mutable branch pulls are denied. The bundle unpacks as declarative text and AST-analysed code only: post-install scripts and shell hooks never run. Import registers the bundle into local `_packs`.
4. **`pack scaffold`** hydrates the registered blueprint into draft files under `routines/` or into a world environment, validates `-p` values against the manifest inputs at stamping, and emits exactly one audit event: `routine.draft` for a routine, `env.init_from_pack` for a world.

Remote packs register strictly at draft trust, version 1, in dev. Prod intake is denied, and packs never bundle or alter host governance: `policy.yaml` and `governance.yaml` stay outside every bundle.

---

## How state changes

Every mutation walks the same pipeline: causal intent declaration, kernel gate intake, AST structural pre-parse, the C-level SQLite authorizer, physical commit, then asynchronous audit emission into `audit.db` and the JSONL mirror. Direct driver paths and external ORM sockets bypass none of it — they are denied outright.

The result is a World whose present state always has a recorded past. `capcli db schema` shows the declared shape, PRAGMA comparison shows the physical shape, and the audit ledger shows every step between the two.

---

**Evolving the World's shape:** → [Migration](../guides/migration.md)
**Recovering a World:** → [Recovery](recovery.md)
**Governing the World's resources:** → [Budgets & Priority Floors](budgets.md)
