# Invocation

The verdict came back true. Now spend it — through one verb with two doors: `run` for capabilities, `sql` for raw gated queries. Both pass the same five-stage gate pipeline — session token, intent binding, AST scan, authorizer cross-check, execution — and both return the same envelope.

---

## Run a capability

```bash
$ capcli run dispatch_order -p order_id=ORD-8842 -p carrier=fedex \
    -m "fulfill paid order for customer checkout" --json
```

```
{
  "exit": 0,
  "json": {
    "capability": "cap://dispatch_order@4",
    "status": "dispatched",
    "tracking": "794644790133",
    "ops_used": 3,
    "ops_limit": 8,
    "audit_chain": ["op_9f2c", "op_9f2d", "op_9f2e"]
  },
  "text": "[dev:tier_1]  dispatch_order@4  ✓  1.2s"
}
```

Decode: `-p k=v` passes typed params, validated against the Param schema before anything runs — a signature mismatch exits 3, not a runtime surprise halfway through your effect. `-m` carries intent; mutating runs without it exit 3. `audit_chain` is the causal DAG for this run — keep the last op id, it's your handle for tracing.

---

## Raw SQL, gated

`sql` is the unified read/write door — the retired `db count` / `db query` / `db exec` verbs are banned, and you should not mourn them. Reads are bounded and parameterized: SELECT caps at 10,000 rows. Writes require `WHERE` + `LIMIT`, bound parameters (interpolation denied), and `-m` intent.

Dry-run any mutation before you commit it — `simulated: true`, every gate checked, zero rows touched:

```bash
$ capcli sql "UPDATE orders SET status = 'shipped' WHERE status = 'processing' LIMIT 50" \
    -m "batch ship processing orders" --dry-run --json
```

```
{
  "exit": 0,
  "json": {
    "simulated": true,
    "statement": "UPDATE orders SET status = 'shipped' WHERE status = 'processing' LIMIT 50",
    "ast_check": "pass",
    "authorizer": "pass",
    "intent": "declared",
    "estimated_rows": 34,
    "state_modified": false
  },
  "text": "[dev:tier_1]  dry-run  ✓"
}
```

---

## Budget counting is not optional knowledge

Every invocation pushes a budget frame; the kernel counts ops, duration, fuel, egress bytes, rows, and api calls — per frame and per session. The min() law: child effective limit = min(declared, governance ceiling, parent remaining, session ceiling). The cage tightens downward, never widens. Splitting is not escaping: a 100-op routine chopped into 10×10 children still hits the session ops ceiling.

Exhaustion is a denial (exit 2), never silent truncation — and the denial cites the exact frame, dimension, and ancestor headroom. Deeper: [../understand/budgets.md](../understand/budgets.md).

---

## Inside routines: ctx, not sockets

Inside a routine you don't shell out. You use the ctx contract:

- `ctx.db.query` / `ctx.db.execute` / `ctx.db.txn` / `ctx.db.lock` — gated database access
- `ctx.api.call(verb, params, intent)` — governed egress, secrets injected at the kernel boundary, idempotency key minted before dispatch
- `ctx.quota.inspect` / `earmark` / `release` — ring-fence provider tokens before you need them

Three laws, no exceptions: `ctx.api.call` is forbidden inside `ctx.db.txn` blocks; waiting is `ctx.api.poll_until` (kernel-managed, one aggregate op) — raw `time.sleep` loops are banned; and raw sockets do not exist:

```
# inside a sandboxed routine
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("10.0.0.5", 5432))
```

```
[dev:tier_1]  ✗ exit 2

  FAIL  kernel.network.jail
        syscall 42 (connect) trapped by seccomp-bpf
        target: 10.0.0.5:5432

  state_modified: false
  layer: sandbox
  remedy: use ctx.api.call with an activated catalog verb
```

The process never saw the network. Egress routes exclusively through activated catalog verbs — that's the wire floor. Detail: [../concepts/sandboxing.md](../concepts/sandboxing.md).

---

## Exit 6: yield, don't grind

When a provider bucket runs dry and your task is Background or Standard class, the kernel parks instead of denying:

```bash
$ capcli run inventory_sync -m "nightly inventory sync" --json
```

```
{
  "exit": 6,
  "json": {
    "domain": "api.quota",
    "culprit": "provider bucket exhausted (background class)",
    "remedy": "parked in _suspended_tasks; daemon re-queues on token refill",
    "state_modified": false
  },
  "text": "[dev:tier_1]  ✗ exit 6"
}
```

Zero partial side effects were committed before the yield. The frame is marked `yielded` and persisted; the daemon watches `resume_at` and re-queues on refill. Foreground calls: back off until the bucket's `reset_at` — visible in inspect — then retry once. Critical-class work doesn't yield at all; it gets exit 2, because a half-done critical task is worse than a denied one. Do not busy-retry exit 6 — the refill clock is not moved by enthusiasm.

---

**Not sure what it'll do? Rehearse it** → [rehearsal.md](rehearsal.md)

**Got an exit code you didn't want?** → [feedback.md](feedback.md)
