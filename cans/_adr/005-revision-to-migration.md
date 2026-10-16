# ADR 005 — Schema-change term: revision → migration

- Status: accepted
- Date: 2026-10-13
- Decided by: user ruling (side chat, branch cans-dedup-workorders)
- Supersedes: the 2026-10-11 migration→revision purge (vendor-purge patch: migrations/→revisions/, migrate.rs→revision.rs) and the WORKORDER-8 ripple that rewrote "Migration-class campaigns" → "Revision-class campaigns" and "judged migration/promotion" → "judged revision/promotion" in prompt-structure.md. Both are reversed by this ruling.

- Context
  - The spec called db/schema changes "revisions": revisions/ bundles, revision.rs, the Four-phase state revision pipeline, Revision safety, diagnostic domain policy.revision, snap_revision_* snapshots.
  - The user ruled the term must be "migration": the workspace root belongs to user artifacts, and the schema-change mechanism reads as migrations, matching the concept's original vocabulary.

- Decision
  - The canonical term for db/schema change is migration. revisions/ → migrations/, revision.rs → migrate.rs, the Four-phase state migration pipeline, Migration safety, Migration invariants, Migration lifecycle commands, diagnostic domain policy.migration, snap_migration_* snapshots, E060_MIGRATION_REJECTED.
  - world.md node renames: Schema-evolution → Schema-migration, with all pointers rehomed.
  - Test-plan domain renamed schema_evolution → schema_migration; case IDs se_* → sm_*.
  - CLI verbs unchanged: rule plan / rule prove / rule apply keep their names; only the concept term and paths change.
  - Deliberately untouched: "git revision" (git terminology), rev_hash/prev_hash (audit hash chain, "previous hash"), _collab/conflicts.md (historical log), docs/ (frozen).

- Alternatives considered
  - Keep revision — rejected by user ruling.
  - Rename CLI verbs too (rule migrate) — rejected: smallest correct change; the verb surface is stable, the concept term is what changed.
