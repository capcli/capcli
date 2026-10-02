# Audit Event Anatomy

Every operation — allowed or denied — lands in `_audit` as one row on a tamper-evident hash chain. This page is the field contract. The theory (hash chaining, the causal DAG, tamper forensics) lives in [memory-spine.md](../concepts/memory-spine.md).

## The event schema (`policy.yaml` → `audit.log`)

| Field | Type | Meaning |
|---|---|---|
| `event` | text | `channel.verb` identifier (e.g. `db.exec`, `api.call`, `routine.run`) |
| `env` | text | `dev`, `sim`, or `prod` |
| `stage` | text | `live`, `test`, `replay`, or `prove` |
| `agent` | text | Acting agent instance id (e.g. `agt_7f3k`) |
| `session` | text | Engagement session id (e.g. `ses_a9`) |
| `principal` | text | Authority holder (`user:alice`, `partner:stripe`) |
| `caused_by` | text | Parent event id in the causal DAG |
| `intent` | text | Causal intent declared via `-m` |
| `intent_chain` | json | Full chain: session goal → routine intent → op intent |
| `capability` | text | Target capability or SQL table |
| `version` | int | Routine / API config version |
| `policy_decision` | text | `allow` or `denied` |
| `rules_matched` | json | Policy rules evaluated for the decision |
| `rows_affected` | int | Rows modified (always 0 on denials) |
| `result_hash` | text | sha256 of the execution result |
| `duration_ms` | int | Wall-clock execution time |
| `idempotency_key` | text | Kernel-minted; persisted before egress |
| `sim_mode` | text | `sandbox`, `mock`, `dry-run`, `skip`, `prod-only`, or `real` |
| `fixture_used` | bool | True if a mock fixture served the call |
| `http_called` | bool | False for `dry-run` and `mock` |
| `triggered_by_skill` | text | Harness skill provenance (`SKILL.md` name) |

Physical envelope — columns on `_audit` in [`system-schema.yaml`](../../cans/artifacts/system-schema.yaml): `id`, `ts` (unix ms), `trace_id` (W3C `traceparent`), `channel` (`rest`, `mcp`, `cron`, `webhook`, `direct`), `payload` (verbatim params and SQL, redacted), and `prev_hash` (the sha256 chain link). Cross-check note: `intent_chain`, `version`, `idempotency_key`, `sim_mode`, `fixture_used`, and `http_called` ride in the event payload and the JSONL mirror rather than as dedicated `_audit` columns. Raw stdout/stderr is discarded — only the canonical JSON outcome is hashed.

## Annotated example

One leaf event from a dispatch routine:

```json
{
  "event": "api.call",
  "env": "dev",
  "stage": "live",
  "agent": "agt_7f3k",
  "session": "ses_a992f",
  "principal": "user:alice",
  "caused_by": "op_9f2d",
  "intent": "fulfill urgent pending orders",
  "intent_chain": ["fulfill urgent pending orders", "dispatch paid order ORD-8842", "create shipment via fedex"],
  "capability": "cap://dispatch_order@4",
  "version": 4,
  "policy_decision": "allow",
  "rules_matched": ["policy.api.egress.allowlist"],
  "rows_affected": 0,
  "result_hash": "sha256:c92e4a…",
  "duration_ms": 340,
  "idempotency_key": "idem_9f2e_a4b8",
  "sim_mode": "sandbox",
  "fixture_used": false,
  "http_called": true,
  "triggered_by_skill": "order-fulfillment"
}
```

* `caused_by: op_9f2d` — this call was birthed by the routine's dispatch op; walk the pointer upward and you reach the session's root intent.
* `policy_decision` + `rules_matched` — the verdict and the exact rules evaluated to reach it. Denials carry the same fields with `effect: none`.
* `idempotency_key` — minted and persisted *before* egress, so a crash between dispatch and receipt can never double-spend.
* `sim_mode: sandbox` / `http_called: true` — the call routed to the provider sandbox over real HTTP; `mock` and `dry-run` events would read `false`.
* `triggered_by_skill` — provenance from the harness skill that started the chain; metadata only, it grants zero authority.

## Redaction rules

Secrets never enter the spine in the clear:

* `secrets.value` — redacted, always.
* Params matching `*token*`, `*password*`, `*secret*` — redacted before the row is written.
* Authorization headers — redacted `always`, no exceptions.

## Retention & integrity

* Events are retained for [90 days](limits.md#workspace-storage).
* The JSONL export mirror trails `_audit` by at most the [mirror-lag SLA](limits.md#invariants).
* Nothing runs unaudited: a failed sink halts execution outright ([exit 5](exit-codes.md#exit-5)).
* The chain is walked daily; a broken link is tamper evidence and a boot refusal.

## Query surfaces

| Surface | Command | Returns |
|---|---|---|
| tail | `capcli sys audit tail [--follow]` | Live event stream |
| trace | `capcli sys audit trace <op-id> [--explain]` | Causal DAG walk to the root intent |
| query | `capcli sys audit query "<sql>" [-p k=v]` | Bounded read-only SQL over `_audit` |
| replay | `capcli sys audit replay --from <point> [--dry-run]` | Historical re-execution against forked state |

Full command reference → [sys.md](cli/sys.md). Denial receipts (the other half of the record) → [exit-codes.md](exit-codes.md#fail-payload).
