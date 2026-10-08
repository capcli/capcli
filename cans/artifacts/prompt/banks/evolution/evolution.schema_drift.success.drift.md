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
  stage_2_plan: 120
  stage_3_rehearse: 60
  stage_4_cutover: 60
slice_max_tokens: 500
docs:
  - doc://guides/migration
status: served
---

# ⚡ ONLINE SCHEMA EVOLUTION PROTOCOL (4-PHASE MIGRATION)
`rule diff` detected structural drift between `schema.yaml` and live SQLite PRAGMAs.
Direct `ALTER TABLE` execution is denied. Structural mutations must follow the online migration pipeline:

## section:stage_1_diff
Inspect structural deltas:
```bash
capcli rule diff
```
Ensure changes avoid circular foreign key references (Gate 2 checks).

## section:stage_2_plan
Generate the deterministic 4-phase migration plan bundle:
```bash
capcli rule plan --name "<migration_slug>" -m "Migration rationale"
```
The kernel scaffolds:
1. **Expand:** Creates shadow tables and forward non-breaking columns.
2. **Backfill:** Generates bounded data copy routines.
3. **Contract:** Removes obsolete shadow structures.
4. **Pin:** Verifies live PRAGMA matches schema.yaml; updates root hash in capcli.lock.

## section:stage_3_rehearse
Rehearse migration phases against masked simulation snapshots:
```bash
capcli rule prove <migration_id> --env sim
```
Assert that table lock acquisition takes less than 20ms under simulation load.

## section:stage_4_cutover
Execute the atomic schema cutover:
```bash
capcli rule apply <migration_id> -m "Execute atomic table swap"
```
Shadow tables are atomically renamed within a single transaction.
