# CANS Agent Instructions — capcli

You are working in a CANS project. Specs live in `cans/`.
This spec describes **capcli**: a governed agent kernel with a plugin-first architecture.

## The 17 canonical files

- _rules.yaml — structural constants and canonical homes registry
- AGENTS.md — agent instructions and ownership table
- overview.md — 5-concern kernel, 5-layer taxonomy, pack distribution
- kernel.md — the 5 concerns, 4 laws, SQL physics, exit codes, fail-closed
- plugins.md — manifest, verbs, CLI noun, ctx namespace, generations, federation, packs
- sandbox.md — Tri-Jail, platform tiers, IPC wire protocol, exit protocol
- egress.md — vault proxy, wire scrubber, quotas, rate-limit buckets
- governor.md — fast path, yield path, outbox, suspension, daemon resumption
- routines.md — guest code, ctx split, decorator, shape, templates, manifests
- world.md — SQLite SSOT, dual schema, kernel and plugin tables, migration, snapshots
- effect.md — audit spine, causal DAG, denials, provenance, replay
- governance.md — trust ladder, budget frames, min() cascade, promotion
- identity.md — principal, agent, session, markers, concurrency
- lifecycle.md — environments, masking, drift, stages, learning, decay
- marketplace.md — registry, publishing, pack taxonomy, distribution channels
- interface.md — 9 kernel nouns, plugin nouns, client RPC, PWA, onboarding
- assembly.md — monorepo, packages, tests, CICD, release

Artifacts live at `artifacts/` (governance.yaml, policy.yaml, system-schema.yaml). Read them, never edit or duplicate them. Cite the artifact path instead.

## Ownership — one canonical home per concept

| Concept | Home |
|---|---|
| 5-concern kernel, 5-layer taxonomy, pack distribution | overview.md |
| 5 concerns, 4 laws, SQL physics, exit codes, fail-closed | kernel.md |
| plugin manifest, verbs, hooks, capabilities | plugins.md |
| CLI noun registration, ctx namespace registration | plugins.md |
| plugin schema extension, generations, GC, composition | plugins.md |
| federation transport, pack taxonomy | plugins.md |
| Tri-Jail, platform tiers, IPC channels, exit protocol | sandbox.md |
| vault proxy, secret injection, wire scrubber, quotas | egress.md |
| fast path, yield path, outbox, suspension, resumption | governor.md |
| routine anatomy, ctx split, decorator, shape, templates | routines.md |
| SQLite SSOT, dual schema, system schema roster | world.md |
| kernel tables vs plugin tables, migration, snapshots | world.md |
| claims lease, outbox/inbox lifecycle | world.md |
| audit spine, causal DAG, denials, provenance, replay | effect.md |
| trust ladder, budget frames, cascade, promotion, evidence | governance.md |
| identity chain, harness markers, concurrency scope | identity.md |
| environments, masking, drift, stages, learning, decay | lifecycle.md |
| registry, publishing, packs, distribution, trust inheritance | marketplace.md |
| 9 kernel nouns, plugin nouns, CLI projection, client RPC | interface.md |
| monorepo, packages, tests, CICD, release | assembly.md |

If your file needs a concept owned elsewhere: write `- <context>: see <file>.md#<Node>` — ONE hop, never chain. Never duplicate content across files. Never duplicate content that lives in `artifacts/*.yaml` — cite the artifact path instead.

## Pointer topology

Pointers flow leaf → branch → root only. Root anchors never point down.

- Root anchors — overview.md, kernel.md, AGENTS.md, _rules.yaml
- Branch files — plugins, sandbox, egress, governor, routines, world,
  effect, governance, identity, lifecycle, marketplace, interface
- Leaf file — assembly.md (points to everything, nothing points to it)

Violations to reject:
- Root file with `see <branch>.md` — wrong direction
- Any chain: `A → B → C`. Collapse to `A → C`.

## Vocabulary law

Never use bare ambiguous words. Always qualify per `_rules.yaml#vocabulary.required_qualifiers`.

Banned bare: `env`, `frame`, `session`, `trust`, `budget`, `surface`, `route`, `tier`, `plugin`, `verb`.

Correct:
- `environment` not `env` (except `process env`, `CliEnvelope`)
- `budget frame` / `call frame` / `federated frame` not `frame`
- `harness session` / `kernel session` not `session`
- `trust rung` / `trust receipt` / `trust floor` not `trust`
- `fuel budget` / `spend ceiling` / `frame budget` not `budget`
- `CLI surface` / `extension surface` not `surface`
- `network route` / `dispatch route` not `route`
- `platform tier` / `trust rung` not `tier`
- `plugin process` / `plugin manifest` / `plugin installation` not `plugin`
- `plugin verb` / `routine` / `API verb` not `verb`
- `plugin` must be qualified — plugin process, plugin manifest, plugin installation, plugin verb, plugin table, plugin id, plugin surface
- `namespace` must be qualified — ctx namespace, CLI noun

## Reading

Find concept → consult `_rules.yaml#canonical_homes` → read canonical home → follow `see:` ONE hop maximum. Never chain.
Read the parent chain for context, not just the leaf.

## Writing

- Bullets only. Indentation is hierarchy. Dense over verbose — every bullet earns its place.
- Depth: 5–18 levels. Every branching node has 4–10 siblings.
- Node text: 5–95 chars inclusive. No code fences, tables, or diagrams inline.
- Preserve real identifiers exactly: `sqlite3_set_authorizer`, `@capcli/kernel`, `routine prove`.
- Unknowns are TBD — mark it, move on, don't invent.
- Smallest correct change. Don't restructure what isn't broken.

## Changing

Find canonical home via `_rules.yaml#canonical_homes` → update there → `cans check` → verify references resolve.
Never silently resolve conflicts — log to `_collab/conflicts.md`.

## ADRs

Decisions get an ADR in `_adr/`. ADRs record WHY. Specs are the truth.

## Tasks

Work tracking in `_tasks/`. Task states live in checkboxes. Archive with `cans done <name>`.

## Token budget

Before reading a concept: `cans budget read "<concept>" --json`. Read only the plan.
Before writing: `cans budget write "<concept>" --json`. Only edit files in canEdit.