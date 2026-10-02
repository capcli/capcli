# Command: capcli run

The hot path — execute capabilities, query data, discover what exists. Every loop a harness runs lives here.

```bash
capcli run <capability> [-p k=v] [-m "<why>"]
capcli sql "<query>" [-p k=v] [-m "<intent>"] [--dry-run]
capcli search <query> [--type <domain>] [--trust <rung>] [--env <env>]
capcli inspect <ptr>
```

`sql`, `search`, and `inspect` are canonical top-level commands — the run noun's hot path promoted for ergonomics. The only `run search` form is the gap-analysis subcommand below.

## Subcommands

| Verb | Syntax | Caller | Description |
|---|---|---|---|
| **execute** | `capcli run <capability> [-p k=v] [-m "<why>"]` | [both] | Runs a registered routine or activated API verb. |
| **sql** | `capcli sql "<query>" [-p k=v] [-m "<intent>"] [--dry-run]` | [both] | Unified AST-gated query and execution — reads and writes in one surface ([db.md](db.md)). |
| **overview** | `capcli run overview [--as <principal>]` | [both] | Single-shot domain situational briefing for session priming. |
| **search** | `capcli search <query> [--type <domain>] [--trust <rung>] [--env <env>]` | [both] | Cascading discovery: exact → prefix → fuzzy → semantic. |
| **inspect** | `capcli inspect <ptr>` | [both] | Pre-flight envelope across all URP types. |
| **gaps** | `capcli search gaps --since 7d` | [harness] | Surfaces capabilities searched repeatedly but never invoked (noun path: `capcli run search gaps`). |

## Execute

```bash
$ capcli run dispatch_order -p order_id=ORD-8842 -p carrier=fedex \
    -m "fulfill paid order for customer checkout"
```

```
[dev:tier_1]  dispatch_order@4  ✓  1.2s

  status:    dispatched
  tracking:  794644790133
  ops_used:  3/8
  audit:     op_9f2c → op_9f2d → op_9f2e
```

The harness didn't write a try/catch, didn't check rate limits, didn't remember to audit. The kernel did all of it because it *can't not* — every primitive crosses the [enforcement pipeline](../../concepts/authorizer.md) and lands on the [spine](../audit.md).

Multi-step operations that must not be interrupted take a lease: `--lock <ref>` (exclusive claim with TTL — [db.md](db.md)).

## SQL: reads free, writes declared

Reads don't need intent. They're free — bounded, but free:

```bash
$ capcli sql "SELECT id, total, status FROM orders WHERE status = 'pending' LIMIT 10"
```

Writes need `-m`. Always. No exceptions, no "I forgot":

```bash
$ capcli sql "UPDATE orders SET status = 'processing' WHERE id = 'ord_9885' LIMIT 1" \
    -m "mark oldest pending order as processing"
```

Forgot the `-m`? [exit 3](../exit-codes.md#exit-3), with the remedy printed. Want to see the plan before mutating? `--dry-run` prints the AST verdict, the authorizer verdict, and the estimated blast radius — state untouched.

## Inspect: the pre-flight envelope

One command, zero roundtrips, full go/no-go verdict:

| Section | Answers |
|---|---|
| **manifest** | What will it actually touch? |
| **budget_status** | Can I run it *right now*? (`can_invoke_now`) |
| **stats** | How reliable is it historically? |

```bash
$ capcli inspect cap://dispatch_order@4
```

```
[dev:tier_1]  cap://dispatch_order@4

  trust:       pinned
  params:      order_id: string, carrier: string

  budget_status:
    can_invoke_now:          true
    session_ops_remaining:   488
    tightest_constraint:     null
```

`can_invoke_now: false` comes with `blocking_reasons` naming the tightest constraint — the [min() cascade](../../concepts/budgets.md#the-min-law) showing you exactly which dimension blocks. Inspect an API verb and you also see the live token bucket; inspect a table and you see access rules and recent traffic.

## The harness loop

You say: "ship order 8842 via fedex". The harness does:

1. `capcli search "dispatch"` → finds `cap://dispatch_order@4`
2. `capcli inspect cap://dispatch_order@4` → checks `can_invoke_now`
3. Sees `true` → `capcli run dispatch_order -p … -m "…"`
4. Reads the exit code. Reads the output. Reports.

Skip inspect when the signature and budget are obviously fine — direct invocation is always permitted. In unfamiliar territory, two seconds of inspect saves a denial.

## Invariants

* Writes require intent; reads stay free — the whole contract in one line ([exit 3](../exit-codes.md#exit-3) on a missing `-m`).
* Read and write bounds are governed by the [blast-radius caps](../limits.md#database-ceilings); result sizes by the [execution ceilings](../limits.md#execution-budget).
* Search returns pointers and summaries, never raw blobs — discovery payloads are capped by the [description budget](../limits.md#routine-shape).
* All string arguments accept `@<path>` and `@-` (stdin): `-p data=@payload.json` bypasses shell escaping and ARG_MAX.
* The walkthroughs live in [workflows](../../workflows/): [discover.md](../../workflows/discover.md) and [query-data.md](../../workflows/query-data.md).
