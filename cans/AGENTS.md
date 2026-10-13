# CANS Agent Instructions — capcli (day-1, plugin-first)

You are working in a CANS project. Specs live in `cans/`.
This spec describes **capcli**: a deterministic microkernel where out-of-process
plugins provide capabilities, sandboxed routines carry business logic, and every
crossing is mediated, metered, and logged.

## The 8 files

- kernel.md — layer 0: the microkernel. Physical laws, tri-jail, execution
  governor, IPC, composition mediation, URP grammar, secret perimeter, schema
  migration mechanism, trust ladder, fuel and budget, audit spine, exit-code
  contract, the 3-primitive CLI, environments and safety.
- plugin.md — layer 1: the plugin contract. Manifest, verbs, hooks, permissions,
  lifecycle, generations and GC, marketplace, the 7 extension slots.
- routine.md — layer 2: guest procedural code. The ctx contract,
  Gather→Compute→Commit, sandboxing, the trust lifecycle, token envelopes.
- template.md — layer 3: scaffolding blueprints. Intake, ceilings, draft floor,
  dissolve-on-hydrate.
- pack.md — layer 4: atomic multi-layer cartridges. All-or-nothing intake,
  the 3 iron laws, bundle composition.
- triggers.md — directive emission. The sole trigger registry, the 15 triggers,
  prompt addressing, slice caps.
- conformance.md — build and distribution legality. Deterministic builds,
  distribution contract, lockfile integrity, test-plan binding, checker tools,
  supply chain.
- _rules.yaml — shape, style, redundancy, and token rules. Law, not advice.

## The three layers (spec organization)

- cans/ is the SSOT for legality. Resolve ambiguity here first; never invent law.
- docs/ is the user-facing complete reference, derived from cans. Frozen until
  the user lifts it. docs/ holds version-controlled markdown specifications and
  playbooks.
- prompts/ is agent-facing progressive disclosure: lean, state-gated action
  that points to docs/, never a complete reference and never restated legality.

## Ownership — one canonical home per concept

- kernel.md (layer 0)
  - physical laws, authorizer, AST/VDBE hooks, fail-closed, tri-jail, tiers, sandbox floor
  - execution governor, exit-code contract (0, 2, 3, 4, 5, 6), state_modified, trust ladder, E045/E046/E047
  - fuel, frames, min() cascade, quotas, budget exhaustion, secret perimeter, vault proxy, scrub, leak panic
  - audit spine, causal DAG, sink law, URP grammar, addressing, cursors, aliases
  - 3-primitive CLI, sys verb grammar, screens, trailer slot, schema migration, composition, backup/restore, env safety, tier waivers
- plugin.md (layer 1)
  - manifest, verbs, hooks, permissions
  - lifecycle, generations, GC leases, marketplace, lockfile
  - the 7 extension slots, bind flags (driver + reachability)
- routine.md (layer 2): ctx contract, Gather→Compute→Commit, trust lifecycle, rollback, retire, envelopes
- template.md (layer 3): intake, ceilings, draft floor, scaffold
- pack.md (layer 4): atomicity, iron laws, bundle composition
- triggers.md: trigger registry, the 15 triggers, prompt addressing, slice caps
- conformance.md: deterministic builds, distribution, lockfile/test-plan/checker/supply-chain

If your file needs a concept owned elsewhere: write `- <context>: see: <file>.md`
or `- <context>: see: <file>.md#<Node>` — ONE hop, never chain. Never duplicate
content across files. Never duplicate content owned by artifacts/*.yaml — cite
the artifact path instead.

## Reading

Find concept → read canonical home → follow `see:` ONE hop. Never chain.
Read the parent chain for context, not just the leaf node.

## Writing

- Bullets only. Indentation is hierarchy. Dense over verbose — every bullet earns its place.
- Present tense, final wording. No archaeology: never evicted, formerly,
  migrated-as-history, Herdr, monolith, "used to", "was renamed", "previously",
  "legacy". No should/should-not — state law directly.
- Depth 5–18 (tree-wide target; honest-shallow chapters carry an explicit
  `<!-- exception: shallow -->` marker instead of padded depth).
  Sibling minimum 4–10 binds structural levels (d1 + d2); honest d3+ clusters
  of 2–3 children are acceptable unmarked, and small chapters (<50 lines) may
  carry honest 2–3-child d2 groupings unmarked. Proven-binary concepts carry an
  explicit `- exception: binary — <proof>` marker. Never pad to hit a number.
- Node subtrees run 5–95 lines. No empty nodes. Single children collapse upward.
- Node text ≤ 200 chars of bullet content (after the `- ` marker; leading
  indentation is structural, not content). No code fences, tables, or diagrams.
- Preserve real identifiers exactly: `sqlite3_set_authorizer`, `vault://`,
  `doc://prompts/{bank}/{slug}#{version}`, exit codes, E-codes.
- Vocabulary is frozen: terms come from the law ledger. A new term is a ruling,
  not a synonym — flag it, never coin it.
- Unknowns are TBD (max 3 per file) — mark it, move on, don't invent.

## Changing

Find canonical home → update there → `cans check` → verify references.
Never silently resolve conflicts — log to `_collab/conflicts.md`.

## Naming

- A leading underscore marks internal engine configuration and graph state
  (_triggers.json, _states.json, _flows.json); a clean manifest.json marks an
  externally consumable compiler artifact.

## Tasks

Work tracking in `_tasks/`. Task states live in checkboxes. Archive with `cans done <name>`.

## Token budget

Before reading a concept: `cans budget read "<concept>" --json`. Read only the plan.
Before writing: `cans budget write "<concept>" --json`. Only edit files in canEdit.
