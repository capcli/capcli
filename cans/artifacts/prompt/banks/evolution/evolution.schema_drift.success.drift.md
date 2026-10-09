---
id: prompt://evolution/schema_drift@1
stem: evolution.schema_drift.success.drift
bank: evolution
slug: schema_drift
version: 1
trust: draft
vars:
  - name: env
    type: string
    source: kernel.env
sections:
  stage_1_diff: 50
  stage_2_dry_run: 120
  stage_3_snapshot: 60
  stage_4_cutover: 60
slice_max_tokens: 500
docs:
  - doc://guides/migration
status: served
---

# ⚡ ONLINE SCHEMA EVOLUTION PROTOCOL (4-PHASE MIGRATION)
`rule diff` detected structural drift between `schema.yaml` and live SQLite PRAGMAs.
Direct `ALTER TABLE` execution is denied. Structural mutations ride the dry-run, snapshot, apply pipeline:

## section:stage_1_diff
Inspect structural deltas:
```bash
capcli rule diff schema --git
```
Ensure changes avoid circular foreign key references (Gate 2 checks).

## section:stage_2_dry_run
Rehearse the migration against the live schema in dry-run mode:
```bash
capcli rule apply schema --dry-run
```
The rehearsal validates the full mutation set without committing: shadow-table expansion,
forward non-breaking columns, bounded backfill, obsolete-structure contraction, and live
PRAGMA parity against `schema.yaml`.

## section:stage_3_snapshot
Take a pre-migration safety snapshot:
```bash
capcli db snapshot -m "pre-migration safety point"
```

## section:stage_4_cutover
Execute the atomic schema cutover:
```bash
capcli rule apply schema -m "Execute atomic table swap"
```
Shadow tables are atomically renamed within a single transaction.
