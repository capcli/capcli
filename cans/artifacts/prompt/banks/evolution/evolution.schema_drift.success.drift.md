---
id: doc://prompts/evolution/schema_drift#2
stem: evolution.schema_drift.success.drift
bank: evolution
slug: schema_drift
version: 2
trust: draft
vars:
  - name: env
    type: string
    source: kernel.env
sections:
  stage_1_expand: 50
  stage_2_align: 110
  stage_3_contract: 80
  stage_4_pin: 50
slice_max_tokens: 500
status: served
---

# ⚡ ONLINE SCHEMA MIGRATION PROTOCOL (4-PHASE MIGRATION)
`rule diff` detected structural drift between `schema.yaml` and live SQLite PRAGMAs.
Raw DDL (ALTER/DROP/CREATE TABLE) is denied for draft and reviewed principals — exit 2.
Structural changes ride the four-phase migration pipeline — see world.md#Schema-migration.

## section:stage_1_expand
Inspect structural deltas, then author the migration bundle:
```bash
capcli rule diff schema --git
capcli rule plan --name <slug>
```
Expand phase is additive non-breaking DDL only (nullable columns, new tables); execution SLA < 10ms.

## section:stage_2_align
Align phase runs in user space via `migrations/NNNN_<slug>/align.py`: bounded chunks (max 500 rows/txn), yields cleanly on quota or fuel exhaustion (exit 6).
Rehearse in sim before prod:
```bash
capcli rule rehearse <id> --env sim
```
`rule rehearse` in sim is mandatory before `env merge <name> prod` — all pinned routines rehearse, any break exits 2.

## section:stage_3_contract
Contract phase runs in kernel space (`migrate.rs`): creates `_shadow_<table>`, attaches AFTER INSERT/UPDATE/DELETE delta triggers replicating in-flight mutations, copies base rows in 500-row chunks.
Zero-lag swap: BEGIN IMMEDIATE at zero replication lag, drops triggers, renames shadow to live, drops the old table; exclusive write lock held < 20ms.

## section:stage_4_pin
Pin phase verifies live PRAGMA matches `schema.yaml` and updates the root hash in `capcli.lock`.
```bash
capcli rule apply <id> -m "<intent>"
```
A cold VACUUM snapshot pairs each migration for disaster-only recovery.
