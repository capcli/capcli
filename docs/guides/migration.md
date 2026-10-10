# Migration

Migration evolves the physical schema of a World — columns, tables, constraints — while live state, pinned routines, and the audit chain stay intact. Schema change rides one pipeline: detect drift, rehearse on a snapshot, cut over through shadow tables, pin the new lockfile hash. Raw DDL plays no part at any stage.

---

## When migration applies

- `capcli rule diff schema` reports drift between `schema.yaml` and live SQLite PRAGMAs.
- A codified routine needs a column, table, index, or constraint the current declaration lacks.
- A provider contract change reshapes the stored shape of catalog data.

Direct `ALTER TABLE` and `DROP TABLE` statements are denied unconditionally, and hand-written table-rebuild scripts fail at the AST gate. Migration is the only road from declaration to physical schema.

---

## The five validation gates

Every schema change crosses the same gates; the pipeline halts at the first failure:

| Gate | Timing | Core checks |
|---|---|---|
| **1. Syntax** | File load | YAML validity, duplicate keys, shorthand expansion, required roots |
| **2. Semantics** | Compile | Reference targets exist with matching types, index targets exist, check expressions parse, acyclic table graph via topological sort, scoped views bind `:principal` |
| **3. Manifest lock** | Boot | Live hash matches `capcli.lock`; dev and sim recompile automatically after Gates 1–2 pass, prod refuses a mismatch |
| **4. Live drift** | `sys doctor` | PRAGMA scan finds no undeclared columns or tables in the physical schema |
| **5. Migration safety** | Apply | Rehearsal on a masked sim snapshot, foreign-key integrity, backfill termination inside fuel bounds, every pinned routine rehearsed against the migrated schema |

Gate 5 carries the sharpest edge: a rehearsal breaking any pinned routine contract aborts the migration before cutover begins.

---

## The four-phase cutover

1. **Expand.** Additive, non-breaking DDL: nullable columns, new tables. The phase targets a sub-10ms execution window.
2. **Backfill.** A user-space pinned routine at `migrations/NNNN/backfill.py` fills new structure in bounded chunks of at most 500 rows per transaction, yielding cleanly when quota or fuel runs dry and resuming from recorded progress.
3. **Contract.** Kernel migration code rebuilds obsolete structure through a trigger-replicated online shadow table; background backfill continues in chunks while the shadow table tracks live deltas.
4. **Pin.** Live PRAGMA comparison against `schema.yaml` verifies parity, and the root hash in `capcli.lock` updates to the new declaration.

The kernel holds the exclusive write lock only for the final trigger detach and table rename — an atomic swap inside a 20ms window. A cold VACUUM snapshot lands before the Expand phase as a disaster-only recovery point.

---

## Operating procedure

```bash
capcli rule diff schema --git
capcli rule plan --name <slug>
capcli db snapshot -m "pre-migration safety point"
capcli rule prove <id> --env sim
capcli rule apply schema -m "Execute atomic table swap"
```

- **Plan** generates the `migrations/NNNN_<slug>/` bundle: plan file plus a backfill stub.
- **Prove** rehearses expand, backfill, and contract timing against sim, including lock duration and backfill fuel.
- **Apply** executes the phased cutover under the declared intent.

Structural rebuilds run in kernel space; backfills run in user space. The separation never blurs.

---

## Rollback means forward

Down-migrations do not exist. Reverting a landed migration means authoring a forward-roll revert bundle: a new migration whose declaration restores the earlier shape, crossing the same five gates and the same rehearsal. History stays append-only, and the audit record shows both crossings.

Cross-world DDL without a git merge is denied, and `system-schema.yaml` — the kernel-owned half of the dual schema — sits outside agent reach entirely. Migration governs `schema.yaml`, the agent-owned declaration, and nothing else.

---

**The World this migration reshapes:** → [World](../understand/world.md)
**Recovery when a migration still goes wrong:** → [Recovery](../understand/recovery.md)
