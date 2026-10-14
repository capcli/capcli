# CANS Agent Instructions — capcli

You are working in a CANS project. Specs live in `cans/`.
This spec describes **capcli**: a governed agent kernel with a plugin-first architecture.

## The 15 canonical files

- overview.md — what capcli is: 5-layer taxonomy, design stance, mental model
- kernel.md — the 4 physical laws: C authorizer, AST scanner, VDBE hook, SHA-256 DAG, exit codes
- plugins.md — plugin manifest, verbs, hooks, permissions, generations, CLI projection, composition
- sandbox.md — Native Tri-Jail across Linux/macOS/Windows, IPC wire protocol, exit protocol
- egress.md — zero-knowledge vault proxy, wire scrubber, quotas, rate-limit buckets
- governor.md — fast path, yield path, outbox staging, suspension, daemon resumption
- routines.md — guest procedural code, ctx contract, decorator, shape, templates, manifests
- world.md — SQLite SSOT, dual schema, migration, claims, outbox/inbox, snapshots
- effect.md — audit spine, causal DAG, denials, provenance, replay invariants
- governance.md — trust ladder, budget frames, min() cascade, promotion, evidence
- identity.md — principal, agent, session, harness markers, concurrency scope
- lifecycle.md — environments, masking, drift, stages, learning, decay, consolidation
- marketplace.md — registry, discovery, publishing, packs (.cap), intake, trust inheritance
- interface.md — 12-noun CLI, CLI projection mount, client RPC, Cockpit PWA, onboarding
- assembly.md — monorepo, packages, tests, CICD pipelines, release matrix

Artifacts live at `artifacts/` (governance.yaml, policy.yaml, system-schema.yaml). Read them, never edit or duplicate them. Cite the artifact path instead.

## Ownership — one canonical home per concept

| Concept | Home |
|---|---|
| 5-layer taxonomy, design stance, mental model | overview.md |
| microkernel laws, authorizer, AST, VDBE, DAG, exit codes | kernel.md |
| plugin manifest, verbs, hooks, permissions | plugins.md |
| plugin CLI projection, generations, GC, composition | plugins.md |
| federation transport, plugin dependency DAG | plugins.md |
| Tri-Jail, platform tiers, IPC channels, exit protocol | sandbox.md |
| vault proxy, secret injection, wire scrubber, quotas | egress.md |
| fast path, yield path, outbox, suspension, resumption | governor.md |
| routine anatomy, ctx contract, decorator, shape, templates | routines.md |
| SQLite SSOT, dual schema, migration, snapshots | world.md |
| claims lease, outbox/inbox lifecycle, concurrency locks | world.md |
| audit spine, causal DAG, denials, provenance, replay | effect.md |
| trust ladder, budget frames, cascade, promotion, evidence | governance.md |
| identity chain, harness markers, concurrency scope | identity.md |
| environments, masking, drift, stages, learning, decay | lifecycle.md |
| registry, discovery, publishing, packs, intake laws | marketplace.md |
| CLI surface, CLI projection mount, client RPC, PWA | interface.md |
| monorepo, packages, tests, CICD, release | assembly.md |

If your file needs a concept owned elsewhere: write `- <context>: see <file>.md#<Node>` — ONE hop, never chain. Never duplicate content across files. Never duplicate content that lives in `artifacts/*.yaml` — cite the artifact path instead.

## Pointer topology

Pointers flow leaf → branch → root only. A root file never points down.

- Root anchors — overview.md, kernel.md. Point to nothing (no `see:` lines).
- Branch files — plugins.md, sandbox.md, egress.md, governor.md, world.md, effect.md, governance.md, routines.md, identity.md, lifecycle.md, marketplace.md, interface.md. Point up to root, across to siblings.
- Leaf file — assembly.md. Points to everything; nothing points to it except overview.md.

Violations to reject:
- A root file that says `see <branch>.md` — wrong direction.
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