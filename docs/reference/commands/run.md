# Command: `capcli run`

The hot path. Everything your harness does a hundred times an hour routes through this noun: invoking capabilities, gated SQL, search, and pre-flight inspection.

```bash
capcli run <verb> [target] [--flags]
```

---

## Subcommands

| Verb | Syntax | Caller | Description |
|---|---|---|---|
| **execute** | `capcli run <capability> [-p k=v]... [-m "intent"]` | `[harness]` | Invokes a routine or API verb. Mutations require `-m`. |
| **sql** | `capcli sql "<query>" [-p k=v] [-m "intent"] [--dry-run]` | `[harness]` | Unified AST-gated query & execution. `sql` is a first-class alias. |
| **search** | `capcli search "<query>" [--type <domain>] [--trust X] [--env X]` | `[harness]` | Resolves intent to typed pointers. |
| **gaps** | `capcli run search gaps --since 7d` | `[harness]` | Surfaces searched-but-missing capabilities. |
| **inspect** | `capcli inspect <ptr>` | `[harness]` | Pre-flight envelope for any URP, incl. the `can_invoke_now` verdict. |
| **overview** | `capcli run overview [--as <principal>]` | `[harness]` | Single-shot domain situational briefing. |

`capcli search` and `capcli inspect` are direct aliases — three keystrokes matter at a hundred calls an hour.

---

## The invocation

```bash
$ capcli run dispatch_order -p order_id=ORD-8842 -p carrier=fedex \
    -m "fulfill paid order for customer checkout"
```

```text
[dev:tier_1]  dispatch_order@4  ✓  1.2s

  status:    dispatched
  tracking:  794644790133
  ops_used:  3/8
  audit:     op_9f2c → op_9f2d → op_9f2e
```

Stages every invocation passes: session token → intent binding + blast radius → AST scan → authorizer + EXPLAIN cross-check → SQLite execution + audit emission. Fail at any stage: stop, untouched, exit code attached.

## SQL through the same gates

```bash
$ capcli sql "UPDATE orders SET status = 'processing' WHERE id = 'ord_9885' LIMIT 1" \
    -m "mark oldest pending order as processing"
```

```text
[dev:tier_1]  ✓  18ms

  rows_affected: 1
  ops_used:      1
  audit:         op_4f8a
```

Write without `-m`:

```text
[dev:tier_1]  ✗  exit 3

  FAIL  policy.query.writes_require_intent
        Mutating write without causal intent declaration.

  state_modified: false
  remedy: add -m "why you're doing this"
```

Rules the AST enforces on every statement: parameterization mandatory (interpolation banned), `UPDATE`/`DELETE` need `WHERE` *and* `LIMIT`, multi-statement submission denied, raw writes wrap in explicit transactions.

## Dry-run: the plan, not the explosion

```bash
$ capcli sql "UPDATE orders SET status = 'shipped' WHERE status = 'processing' LIMIT 50" \
    -m "batch ship processing orders" --dry-run
```

```text
[dev:tier_1]  dry-run  ✓

  statement:     UPDATE orders SET status = 'shipped' WHERE status = 'processing' LIMIT 50
  ast_check:     pass
  authorizer:    pass (write on orders allowed)
  intent:        declared
  estimated_rows: 34
  blast_radius:  bounded (LIMIT 50)

  state_modified: false
  note:           no execution occurred
```

## Locks

```bash
$ capcli run reconcile_inventory -p warehouse=WEST \
    -m "nightly warehouse reconciliation" \
    --lock inventory:WEST --ttl 300
```

Locks are TTL'd leases in `_claims`. Crash mid-run, and the lock expires rather than haunting the table. Multi-statement transactions cap at 10 statements — one transaction, one thought.

---

**Narrative** → [../../use/run.md](../../use/run.md) · **Exit codes** → [../exit-codes.md](../exit-codes.md)
