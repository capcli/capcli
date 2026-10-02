# Audit Structures

The ledger, measured with calipers: every column, event type, hash, and interrogation verb, exactly as the specs attest. The prose pages tell the story — this one shows the schematics.

---

## The spine: `_audit`

One system table inside `workspace.db`. The primary transactional source of truth for all events: you get bounded read-only SQL, only the kernel engine writes. Every field below is attested — nothing padded, nothing paraphrased.

| Group | Field | Contract |
|---|---|---|
| Identity | `event` | Dot-notated `channel.verb` identifier (`db.exec`, `api.call`, `bind.create`) |
| Identity | `ts` | Unix epoch, milliseconds |
| Identity | `env` · `stage` | `dev`/`sim`/`prod` · `live`/`test`/`replay`/`prove` — stamped on every leaf |
| Identity | `channel` | `rest`, `mcp`, `cron`, `webhook`, or `direct` (default) |
| Identity | `trace_id` | External W3C `traceparent` or MCP parent context |
| Actor | `agent` · `session` · `principal` | Agent instance (`agt_7f3k`), session (`ses_a992f`), authority holder |
| Causality | `caused_by` | Parent event id — the DAG edge |
| Causality | `intent` | The `-m` declaration, verbatim |
| Causality | `intent_chain` | Ancestry of intents back to the root |
| Payload | `capability` | Target capability pointer or SQL table |
| Payload | `payload` | `sql` + `params`, recorded verbatim for replay (masked on secret match) |
| Policy | `decision` | `allow` or `denied` — denials are first-class rows |
| Policy | `rules_matched` | Array of policy rules evaluated |
| Outcome | `rows_affected` | Rows modified — `0` on denials |
| Outcome | `result_hash` | SHA-256 of the canonical execution result |
| Outcome | `duration_ms` · `exit_code` | Wall-clock execution time · terminal status of the operation |
| Chain | `prev_hash` | SHA-256 of the prior row — the tamper seal |

Physical storage adds an autoincrement `id`, `triggered_by_skill` for harness provenance, and indexes on `(event, ts)`, `(agent, ts)`, `(capability, decision)` — which is why `tail`, `trace`, and `query` never table-scan. And one law above all: raw `stdout`/`stderr` are discarded — the kernel hashes the canonical JSON outcome and nothing else, so a chatty process cannot pad its own receipt.

---

## Leaf event payloads

The kernel event types the spec attests, with their attested payload fields. Exactly this set — this page doesn't mint event ids any more than the kernel does; if your terminal shows one that's missing here, the authority is the ledger itself (`sys audit tail`).

| Event | Attested payload fields |
|---|---|
| `db.exec` | `sql`, `params`, `vdbe_inspect`, `rules_matched`, `rows_affected`, `result_hash` |
| `routine.run` | `routine`, `version`, `hashes`, `triggered_by`, `outcome` |
| `api.call` (sim) | `sim_mode`, `http_called`, `fixture_used` |
| `api.sync` | `provider`, `added`, `removed`, `changed`, `unchanged` |
| `api.activate` | `verb`, state transition, `trust`, `intent` |
| `api.token_refresh` | `provider`, `token_type`, `expires_in`, `refresh_outcome` |
| `api.first_prod_call` | `call_number`, `calls_remaining`, `approver` |
| `bind.create` / `bind.delete` | `target_urp`, `trigger_type`, `schedule_or_source` |
| `vault.set` | `secret_name`, `secret_hash_prefix`, `action: injected` |
| `env.switch` / `env.merge` | `source_env`, `target_env`, `git_commit`, `ddl_status` |
| `sys.agent.register` / `sys.agent.revoke` | `agent_id`, `principal`, `token_hash` |
| `capability.search` | `query`, `results_count`, `resolution_stage` |
| `budget.frame_push` / `budget.frame_pop` | `declared`, `consumed`, `remaining` |
| `serve.request` | `endpoint`, `channel` (rest\|mcp), `trace_id`, `routine@version`, `api_key_id`, `status` |

Denied operations emit the same anatomy with `decision: denied`, `rules_matched` citing the exact rule id, and `effect: none` — the failed statement preserved for the post-mortem. The rule-id roster lives in [errors.md](errors.md).

---

## The JSONL mirror

`_audit` is the SSOT; `audit/audit.YYYY-MM-DD.jsonl` is its shadow.

| Property | Contract |
|---|---|
| Role | Secondary read-only export view, streamed from `_audit` |
| Format | Daily append-only JSONL files |
| Persistence | Flushed to disk and git — offline diffing, cold recovery |
| Freshness | Mirror lag hard SLA: capped at 5 minutes |

Ground truth stays in the table; the mirror just refuses to fall more than five minutes behind it.

---

## The causal DAG

Flat logs answer *what*. The DAG answers *why*.

- `caused_by` — every event points at its parent operation id. Hierarchy: leaf op → routine → session goal.
- `intent_chain` — the full ancestry of `-m` declarations, back to the root intent someone actually wanted.
- Context stamping — `env` and `stage` ride on every leaf, so a `replay` leaf can never masquerade as a `live` one.
- External grafts — inbound W3C `traceparent` lands in `trace_id`; HTTP arrivals bind via `serve.request`; budget frames bind via `parent_frame`. Sequential routine interiors keep the DAG acyclic.
- **Zero ghost actions:** 100% of CLI verbs, bindings, and environment transitions advance the hash chain. There is no code path that changes reality without leaving a row.

---

## Tamper physics

| Law | Consequence |
|---|---|
| Per-row SHA-256 chain | Each row's `prev_hash` seals the row before it, verified against the root ledger hash |
| Blast radius | One broken link invalidates *all* subsequent events |
| External attestation | Ledger root hash checkpointed to S3 Object Lock (WORM) under KMS signatures |
| Scheduled walk | Full chain re-verification runs daily at 04:00 — the math audits itself while you sleep |
| Write priority | Unaudited writes denied outright — `exit 5`, the kernel refuses to run |
| Failure buffer | A stuttering sink queues writes in memory for 5m before the panic fires |
| Genesis sequence | A fresh world opens with four events: `rule.apply`, a read, a denied write, an allowed write |
| No synthetic types | `onboarding.*` and fake lifecycle events are denied at the door |

Root-edit one row and every hash after it screams; boot onto a broken chain and the kernel refuses to run — `exit 3`, state untouched. See [exit-codes.md](exit-codes.md).

---

## Inspection surfaces

Four verbs, all read-only, all index-backed:

| Surface | Syntax | Returns |
|---|---|---|
| Tail | `capcli sys audit tail [--follow] [--capability <urp>] [--since 1h]` | Live event stream, filterable |
| Trace | `capcli sys audit trace <op-id> [--explain]` | Causal DAG walk to root intent |
| Query | `capcli sys audit query "<sql>" [-p k=v]` | Bounded read-only SELECT against `_audit` |
| Replay | `capcli sys audit replay --from <point> [--dry-run]` | Historical events against isolated forked state |

Replay invariants worth tattooing: replay executes under **current** policy, not the historical one; external API calls are flagged `replay: manual` — auto-replay is strictly forbidden; idempotency is environment-scoped, so a replay cannot double-execute.

---

## In practice

The tail, filtered to one capability:

```bash
$ capcli sys audit tail --capability db://orders --since 1h
```

```
[dev:tier_1]  audit tail  ✓  3 events

  ts          event                    decision   agent      capability
  ──────────  ───────────────────────  ─────────  ─────────  ──────────────────
  ...         db.exec                  allow      agt_7f3k   orders (read)
  ...         db.exec                  allow      agt_7f3k   orders (write)
  ...         sql.query                denied     agt_7f3k   orders (delete)
```

The trace, walking a prove run back to its root intent — every `└──` is a `caused_by` edge:

```bash
$ capcli sys audit trace op_992c --explain
```

```
[sim:tier_1]  audit trace  ✓  op_992c → ses_44e1

  ses_44e1  session.start       "prove refund path before quarterly rehearsal"
    └── op_992a  routine.refund_order@1
          ├── op_992b  db.query (orders)          ✓  12ms
          ├── op_992c  api.call (stripe.refund)   ✓  340ms
          │     └── sim_mode: sandbox · fixture_used: true
          └── op_992d  db.execute (orders)        ✓  18ms
                └── rows_affected: 1

  root intent:  "prove refund path before quarterly rehearsal"
  authority:    user:alice (via agt_7f3k)
  integrity:    valid hash link (chain verified)
```

The query, with bound parameters — no string interpolation, ever:

```bash
$ capcli sys audit query "SELECT capability, count(*) AS denials
    FROM _audit
    WHERE decision = 'denied' AND env = @env
    GROUP BY capability
    ORDER BY denials DESC" \
    -p env=dev
```

```
[dev:tier_1]  audit query  ✓  2 rows

  capability       denials
  ───────────────  ───────
  db://orders      2
  db://inventory   1
```

---

**The narrative tour — three questions, three commands** → [../use/audit.md](../use/audit.md)

**The deep machinery — hash chains, WORM checkpoints, distributed tracing** → [../understand/audit.md](../understand/audit.md)

**Effects, provenance, and the sys noun that hosts these verbs** → [../understand/effects.md](../understand/effects.md) · [../concepts/provenance.md](../concepts/provenance.md) · [commands/sys.md](commands/sys.md)
