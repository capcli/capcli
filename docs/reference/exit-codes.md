# Exit Codes & Denial Anatomy

Denials don't crash your system; they teach the caller how to pass the gate. When an LLM hits a generic bash error it hallucinates excuses; when it hits a Capcli boundary it gets a structured, machine-parseable receipt. Six codes, one law: **non-zero means the state is untouched** — a partial commit would be a critical kernel bug, not a degraded success.

| Code | Name | State Guarantee |
|---|---|---|
| [0](#exit-0) | Success | Committed, audit event recorded |
| [2](#exit-2) | Policy Denial | Untouched (`state_modified: false`) |
| [3](#exit-3) | Refusal | Untouched |
| [4](#exit-4) | Crash | Rolled back |
| [5](#exit-5) | Kernel Panic | Untouched |
| [6](#exit-6) | Yield | Untouched — task suspended, not failed |

There is no exit 1. Generic failure is not part of the contract.

---

<a id="exit-0"></a>

## exit 0 — Success

The operation committed and its receipt is on the [memory spine](../concepts/memory-spine.md). Upstream HTTP failures are handled gracefully inside the result envelope — a provider 429 during a routine does not turn your `run` into a crash; it returns a structured envelope with the outcome inside.

**Harness behavior:** proceed. The result summary is capped by the [result-token ceiling](limits.md#execution-budget); pull deeper payloads with `--out` when you need them.

---

<a id="exit-2"></a>

## exit 2 — Policy Denial

The workhorse. A governance invariant, the C authorizer, an AST rule, a budget frame, or a trust rung said no — and the denial itself is a first-class [audit event](audit.md). Domains: `db.engine` (SQLite constraint, foreign key violation, busy timeout), `policy.authorizer` (table/column gate), `policy.budget` (frame or session ceiling), `policy.trust` (rung forbids the action — draft touching prod, pinned on [Tier 2](../concepts/sandboxing.md#tiers)).

**Harness behavior:** read the [FAIL payload](#fail-payload), apply the `remedy`, change the approach. Retrying the identical input is how you trip the [thrashing detector](limits.md#rate-governance).

<a id="fail-payload"></a>

### Anatomy of a Denial

Every exit 2 carries six guarantees:

| Guarantee | What it tells you |
|---|---|
| **`FAIL` + rule id** | The exact rule that fired, e.g. `policy.query.update_delete.require_limit` |
| **Offending snippet** | Exactly what was rejected, with a caret marker under the problem |
| **`state_modified: false`** | Nothing changed. Guaranteed, not hoped. |
| **`layer`** | Which enforcement layer caught it: [AST](../concepts/authorizer.md), [VDBE bytecode trap](../concepts/authorizer.md#vdbe), C authorizer, or [budget frame](../concepts/budgets.md#the-min-law) |
| **`measured` vs cap** | The value that crossed the line — "file has 342 LOC, max is 150" — never a vague shrug |
| **`remedy`** | What to do instead |

Five walls, five receipts:

### AST blast guard — "no LIMIT"

Your harness writes a lazy UPDATE:

```bash
$ capcli sql "UPDATE orders SET status = 'shipped' WHERE status = 'processing'" \
    -m "batch ship"
```

```
[dev:tier_1]  ✗  exit 2

  FAIL  policy.query.update_delete.require_limit
        UPDATE orders SET status = 'shipped' WHERE status = 'processing'
                                                                   ^^^^^^
        No LIMIT clause. Blast radius unbounded.

  state_modified: false
  layer: AST
  measured: matches potentially 847 rows (cap: 100)
  remedy: add LIMIT, or target specific primary key
```

The SQL never touched SQLite. The [AST parser](../concepts/authorizer.md) killed it at parse time. Zero rows changed. The denial names the rule, the offending clause, the measured blast radius against the [rows-affected cap](limits.md#database-ceilings), and the fix.

Your harness retries, bounded:

```bash
$ capcli sql "UPDATE orders SET status = 'shipped' WHERE status = 'processing' LIMIT 100" \
    -m "batch ship first 100"
```

```
[dev:tier_1]  ✓  42ms

  rows_affected: 100
```

Done. It learned. You didn't have to explain anything.

### Vault wall — trust gate on `secrets.value`

Your harness tries to read credentials directly:

```bash
$ capcli sql "SELECT value FROM secrets WHERE name = 'stripe_key'"
```

```
[dev:tier_1]  ✗  exit 2

  FAIL  policy.authorizer.trust_gate
        SELECT value FROM secrets WHERE name = 'stripe_key'
               ^^^^^
        Column 'value' denied for caller trust level: draft

  state_modified: false
  layer: authorizer
  remedy: draft trust cannot read secrets; promote the routine to reviewed
```

The C authorizer intercepted this at `sqlite3_prepare_v2`. The query never executed. No secret exposure, no workaround to try — the door is locked at the engine level, and only the [trust ladder](../concepts/trust-engine.md#reviewed) opens it. How secrets actually reach egress → [apis.md](../workflows/apis.md#vault).

### Budget cage — ops 50/50

Your harness is mid-routine, op 50 of 50. It tries one more thing:

```bash
$ capcli run archive_old_orders -p cutoff_days=90 \
    -m "nightly archive"
```

```
[dev:tier_1]  ✗  exit 2

  FAIL  policy.budget.ops_exhausted
        routine archive_old_orders@3 (frame_005)
        attempted_op: db.exec
        ops: 50/50

  state_modified: false
  layer: budget
  blocking_frame: frame_005 (archive_old_orders@3)
  session_remaining: 488 ops
  remedy: increase declared_max_ops in the routine limits, or split the work
```

The session had 488 ops left. But the routine's own frame was the tightest cage — the [`min()` cascade](../concepts/budgets.md#the-min-law) held. The denial names the exact frame, the exact dimension, and the remaining headroom at every level. The harness either splits the work, raises the declaration, or yields. Headroom for every dimension is visible before you commit: `capcli inspect <ptr>` → `can_invoke_now` ([run.md](cli/run.md)).

### Trust denial — draft in prod

Your harness tries to run a draft routine in prod:

```bash
$ capcli run experimental_cleanup -p dry=true \
    -m "test cleanup in prod" \
    --env prod
```

```
[prod:tier_1]  ✗  exit 2

  FAIL  policy.trust.draft_writes_denied
        capability: cap://experimental_cleanup@1
        trust: draft
        env: prod

  state_modified: false
  layer: trust
  remedy: promote to reviewed via routine ship, or run in dev/sim
```

Draft routines cannot touch prod. No `--force`, no override. The overlay says no, the authorizer says no, the kernel says no — three locks on the same door. How code earns the key → [trust-engine.md](../concepts/trust-engine.md); how worlds stay isolated → [environments.md](../concepts/environments.md).

### Network jail — syscall 42

Your harness tries to open a raw socket inside a routine:

```python
# inside a sandboxed routine
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("10.0.0.5", 5432))
```

```
[dev:tier_1]  ✗  exit 2

  FAIL  kernel.network.jail
        syscall 42 (connect) trapped by seccomp-bpf
        target: 10.0.0.5:5432

  state_modified: false
  layer: sandbox
  remedy: use ctx.api.call with an activated catalog verb
```

The process never saw the network. `seccomp-bpf` killed the syscall before it reached the kernel's TCP stack. No timeout, no connection refused — just: *this path does not exist.* The only door out is a catalog verb through the kernel ([api.md](cli/api.md)); the jail itself is described in [sandboxing.md](../concepts/sandboxing.md).

---

<a id="exit-3"></a>

## exit 3 — Refusal

Compile-time refusal, validation failure, or boot integrity. The caller is malformed, not the policy. Common triggers:

* Missing `-m` intent on a mutating write — the audit trail demands causality.
* Unparseable SQL — parser failure fails closed.
* Lockfile mismatch — `capcli.lock` hash diverges from the YAML on disk ([lockfile law](../concepts/compiler.md)).
* NTP drift beyond the [boot gate](limits.md#invariants).
* Sub-5-minute cron registration ([cron floor](limits.md#triggers)).
* Missing parameter, missing secret in headless mode, scoped view invoked without `--as`.

State untouched. **Harness behavior:** fix the input — add the intent, repair the syntax, sync the clock — then retry. Retrying without changing anything just spends your [rate budget](limits.md#rate-governance).

---

<a id="exit-4"></a>

## exit 4 — Crash

`routine.runtime`: an uncaught exception or type crash inside the sandbox. The transaction is cleanly rolled back — no half-written rows survive.

**Harness behavior:** don't blind-retry; forensic quarantine blocks auto-retry on unhandled runtime faults. Walk the trace (`capcli sys audit trace <op-id>` → [sys.md](cli/sys.md)), fix the code, bump the version — silent edits are banned, every change is a new version.

---

<a id="exit-5"></a>

## exit 5 — Kernel Panic

The audit sink is unreachable or a host resource failed, so execution is refused outright: **unaudited writes are physically impossible.** The sink gets a short in-memory failure buffer before the kernel pulls the cord — the exact window is a [machine invariant](limits.md#invariants).

**Harness behavior:** stop and surface to a human immediately. There is nothing to retry — the machine is telling you it cannot guarantee a receipt, so it refuses to act.

---

<a id="exit-6"></a>

## exit 6 — Yield

`api.quota`: the proactive rate broker yielded instead of denying. The frame is marked `yielded`, persisted to the daemon's suspended-task queue, and re-queued automatically when tokens refill (`resume_at`). Background tasks yield when unreserved headroom drops below the [yield threshold](limits.md#api-wire); critical tasks get a hard exit 2 instead.

**Harness behavior:** do not retry and do not spawn a replacement — the task is already scheduled. Check `capcli inspect` for when headroom returns, or watch the queue drain via [sys.md](cli/sys.md). The suspension mechanics are covered in [budgets.md](../concepts/budgets.md).

---

## Thrashing detection

Capcli doesn't just block — it notices when blocking becomes a loop. [Twenty sustained denials in five minutes](limits.md#rate-governance) fires an `agent.thrashing` warning:

```
[dev:tier_1]  ⚠  agent.thrashing

  agent: agt_7f3k
  denials_last_5m: 22
  pattern: repeated policy.query.update_delete.require_limit
  remedy: harness appears stuck; consider changing approach or escalating to human
```

The harness gets the alert. You get the alert. Something needs to change — and the pattern line usually tells you exactly what.

---

## The state guarantee

Every non-zero exit guarantees `state_modified: false`. This is the contract that makes autonomy safe: when your harness reads an exit code, it is reading a promise about the database. If it isn't 0, nothing happened — and the [audit spine](../concepts/memory-spine.md) can prove it.
