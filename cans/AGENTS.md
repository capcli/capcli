# CANS Agent Instructions — capcli

You are working in a CANS project. Specs live in `cans/`.
This spec describes **capcli**: a governed agent kernel where agents author, a kernel compiles, humans approve.

## The 13 canonical files

- overview.md — what capcli is: philosophy, mental model, kernel stance
- world.md — what exists: see space.md#Environment-axis
- physics.md — what is allowed: two-layer policy, fail-closed, raw SQL rules
- effect.md — what happened: audit spine, causal DAG, JSONL ground truth
- agent.md — who acts: principal → agent → session → op identity hierarchy
- action.md — what can be done: capabilities, routines, manifests, API catalog
- time.md — how things persist and change: draft → prove → ship → live → decay
- space.md — where things happen: dev → sim → prod, worktrees, drift
- trust.md — earned authority: draft → reviewed → pinned ladder and gates
- budget.md — what resources exist: frames, cascades, quotas
- recovery.md — how to undo: see world.md#SQLite-as-SSOT
- interface.md — how humans and agents touch the world: CLI, SDK, PWA, onboarding
- assembly.md — how the kernel is built: monorepo, packages, naming, tests

Artifacts live at `artifacts/` (governance.yaml, policy.yaml, repomix.config.json) — read them, never edit or duplicate them.

## Ownership — one canonical home per concept

| Concept | Home |
|---|---|
| budget cascade structure (scopes, inheritance) | governance.yaml routine_shape.composition |
| budget exhaustion behavior (deny, partial) | policy.yaml budget |
  # FIX #19: added ownership row for the split
| schema, tables, DDL, validation gates | world.md |
| authorizer, AST, policy layers, fail-closed | physics.md |
| audit, denials, forensics, provenance | effect.md |
| identity, sessions, intents, secrets | agent.md |
| capability registry, routine anatomy, ctx, manifests, API catalog | action.md |
| lifecycle stages, consolidation, learning loop, schedule | time.md |
| environments, sim mode, worktrees, drift | space.md |
| trust ladder, promotion, evidence, overrides | trust.md |
| budget frames, cascade, quotas | budget.md |
| snapshots, backup, restore, git integration | recovery.md |
| CLI surface, SDK, PWA layers, onboarding journeys | interface.md |
| monorepo, packages, naming law, tests, build | assembly.md |

If your file needs a concept owned elsewhere: write `- <context>: see <file>.md#<Node>` — ONE hop, never chain. Never duplicate content across files. Never duplicate content that lives in `artifacts/*.yaml` — cite the artifact path instead.

## Reading

Find concept → read canonical home → follow `see:` ONE hop. Never chain.
Read the parent chain for context, not just the leaf leaf-node.

## Writing

- Bullets only. Indentation is hierarchy. Dense over verbose — every bullet earns its place.
- Depth: 5–7 levels. Every branching node has ≥3 siblings.
  # FIX #27: aligned with _rules.yaml depth.min: 5
- Preserve real identifiers exactly: `sqlite3_set_authorizer`, `@capcli/kernel`, `routine prove`.
- Unknowns are TBD — mark it, move on, don't invent.
- Node text ≤ 200 chars (overflow.max_node_chars). No code fences, tables, or diagrams
  # FIX #26: clarified which config field governs the 200-char limit
- Smallest correct change. Don't restructure what isn't broken.

## Changing

Find canonical home → update there → `cans check` → verify references.
Never silently resolve conflicts — log to `_collab/conflicts.md`.

## ADRs

Decisions get an ADR in `_adr/`. ADRs record WHY. Specs are the truth.

## Tasks

Work tracking in `_tasks/`. Task states live in checkboxes. Archive with `cans done <name>`.

## Token budget

Before reading a concept: `cans budget read "<concept>" --json`. Read only the plan.
Before writing: `cans budget write "<concept>" --json`. Only edit files in canEdit.
