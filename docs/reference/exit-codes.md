# Boundaries

Your harness is going to hit walls. That's the point.

The walls teach. They say *no*, they say *why*, and they say *what to do instead*. Your harness reads the denial, fixes its approach, and retries. You watch it learn.

---

## The shape of a denial

Every denial looks like this:

```
attempt → decision → explanation → next action
```

Not a crash. Not a mystery. Not a stack trace. A structured teaching moment with an exit code.

---

## AST denial: "you're too greedy"

Your harness writes a lazy UPDATE.

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

The SQL never touched SQLite. The AST parser killed it at parse time. Zero rows changed. The denial tells the harness exactly what's wrong and how to fix it.

Your harness retries:

```bash
$ capcli sql "UPDATE orders SET status = 'shipped' WHERE status = 'processing' LIMIT 100" \
    -m "batch ship first 100"
```

```
[dev:tier_1]  ✓  42ms

  rows_affected: 100
```

Done. It learned. You didn't have to explain anything.

---

## Authorizer denial: "you don't have the key"

Your harness tries to read secrets.

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
  remedy: draft trust cannot read secrets; promote routine to reviewed
```

The C authorizer intercepted this at `sqlite3_prepare_v2`. The query never executed. The harness doesn't get to see the secret. Doesn't get to try a workaround. The door is locked at the engine level.

---

## Budget denial: "you're out of gas"

Your harness is mid-routine, op 20 of 20. It tries one more thing.

```bash
$ capcli run archive_old_orders -p cutoff_days=90 \
    -m "nightly archive"
```

```
[dev:tier_1]  ✗  exit 2

  FAIL  policy.budget.ops_exhausted
        routine archive_old_orders@3 (frame_005)
        attempted_op: db.exec
        ops: 20/20

  state_modified: false
  layer: budget
  blocking_frame: frame_005 (archive_old_orders@3)
  session_remaining: 488 ops
  remedy: increase declared_max_ops in routine limits, or split work
```

The session had 488 ops left. But the routine's own frame was the tightest cage. The `min()` cascade held. The denial names the exact frame, the exact dimension, and the remaining headroom at every level.

Your harness reads this. It either splits the work, increases the declaration, or yields.

---

## Trust denial: "you're not ready for this room"

Your harness tries to run a draft routine in prod.

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

Draft routines cannot touch prod. Period. No `--force`. No override. The overlay says no, the authorizer says no, the kernel says no. Three locks on the same door.

---

## Network jail: "there is no door"

Your harness tries to open a raw socket inside a routine.

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

The process never saw the network. `seccomp-bpf` killed the syscall before it reached the kernel's TCP stack. The routine got an exit code. No timeout. No connection refused. Just: *this path does not exist.*

---

## What happens if your harness keeps hitting the wall

Twenty sustained denials triggers a thrashing alert.

```
[dev:tier_1]  ⚠  agent.thrashing

  agent: agt_7f3k
  denials_last_5m: 22
  pattern: repeated policy.query.update_delete.require_limit
  remedy: harness appears stuck; consider changing approach or escalating to human
```

Capcli doesn't just block. It notices when blocking becomes a loop. Your harness gets the alert. You get the alert. Something needs to change.

---

## The denial contract

Every denial gives you:

| Field | What it tells you |
|---|---|
| `FAIL` + rule code | Which specific rule you hit |
| Rejected statement | Exactly what you tried, with the offending part highlighted |
| `state_modified: false` | Nothing changed. You're safe. |
| `layer` | Which enforcement layer caught you (AST, authorizer, budget, trust, sandbox) |
| `measured` | The actual value that crossed the line |
| `remedy` | What to do instead |

This isn't an error message. It's a teaching payload. Your harness parses it. Fixes the approach. Retries. You don't intervene unless you want to.

---

## The one rule

**A denial is not a failure. It's the system talking.**

When you see `exit 2`, don't panic. Don't retry blindly. Read the `remedy`. Your harness reads it too. The wall just told you where the door is.

---

**Want to see what actually happened?** → [audit.md](audit.md)

**Need to undo something?** → [recover.md](recover.md)
