# Exit Codes

Machines communicate via exit codes, not conversational apologies. Capcli emits exactly six, and each is a contract about state — not a mood, not a suggestion.

---

## The law

| Code | Name | Meaning | State guarantee |
|---|---|---|---|
| `0` | success | Committed to relational state, hashed into the causal ledger | audit event recorded |
| `2` | policy denial | Blocked by C authorizer, AST, trust rung, or budget | state untouched |
| `3` | refusal / drift | Missing `-m` intent, lockfile mismatch, NTP drift >500ms, failed gate | state untouched |
| `4` | crash | Uncaught sandbox exception or type crash in `routine.runtime` | transaction cleanly rolled back |
| `5` | kernel panic | Audit sink unreachable or host resource failure | kernel refuses to run unaudited |
| `6` | yield | Provider quota dry — task parked, not killed | frame parked in `_suspended_tasks` until refill epoch |

**The state rollback law:** every non-zero exit guarantees `state_modified: false`. A partial commit on a non-zero exit is not an edge case — it is a critical kernel bug. Upstream HTTP failures inside an otherwise successful run are handled gracefully in the envelope; they don't get smuggled into the exit code.

Six codes. That's the whole set, and each one arrives with its state guarantee attached.

---

## `0` — committed and hashed

```bash
$ capcli sql "UPDATE orders SET status = 'processing' WHERE id = 'ord_9885' LIMIT 1" \
    -m "mark oldest pending order as processing"
```

```
[dev:tier_1]  ✓  18ms

  rows_affected: 1
  ops_used:      1
  audit:         op_4f8a
```

One row changed, one op burned, one audit leaf. Exit 0 means the ledger agrees with reality.

---

## `2` — the wall

```bash
$ capcli sql "DELETE FROM orders"
```

```
[dev:tier_1]  ✗  exit 2

  FAIL  policy.query.update_delete.require_where
        DELETE FROM orders
        ^^^^^^^^^^^^^^^^^^
        Missing WHERE clause. Unbounded delete denied.

  state_modified: false
  remedy: add WHERE + LIMIT, or use chunked loop via ctx.db.execute
```

The SQL never reached SQLite — it died at `sqlite3_prepare_v2`. Exit 2 covers four domains:

| Domain | What lives there |
|---|---|
| `db.engine` | SQLite check constraints, foreign key violations, busy timeout |
| `policy.authorizer` | C-level table/column write denials |
| `policy.budget` | Frame limits, session op/fuel ceilings |
| `policy.trust` | Action forbidden by the caller's trust rung |

The full table of attested rule ids lives in [errors.md](errors.md).

---

## `3` — refusal / drift

```bash
$ capcli sql "UPDATE orders SET status = 'processing' WHERE id = 'ord_9885' LIMIT 1"
```

```
[dev:tier_1]  ✗  exit 3

  FAIL  policy.query.writes_require_intent
        Mutating write without causal intent declaration.

  state_modified: false
  remedy: add -m "why you're doing this"
```

The same statement as the exit 0 example, minus the `-m`. No intent, no write. Exit 3 is the kernel refusing *before* reality gets involved:

| Cause | What tripped it |
|---|---|
| Missing intent | Mutating write without `-m` |
| Lockfile mismatch | `capcli.lock` root hash diverges from the working tree |
| Clock drift | Host clock >500ms off NTP at boot |
| Session errors | Missing, forged, or expired session token |
| Compiler gates | Syntax, cycle, drift, or migration-safety failure in `rule apply` |
| Cron floor | Sub-5-minute schedule at `bind cron` |
| Standalone bypass | Routine invoked outside the kernel runner |

---

## `4` — crash

Domain: `routine.runtime`. An uncaught exception inside the sandbox — a guest type crash the routine didn't handle. The transaction is cleanly rolled back, and `state_modified: false` holds like every other non-zero exit.

No verified transcript of an exit 4 exists anywhere in the docs, and this page won't manufacture one to feel complete. The contract is the contract.

---

## `5` — kernel panic

Domain: `kernel.panic`. The audit sink is unreachable or the host has failed. The kernel does not log a warning and carry on — it halts, because an action without a cryptographic receipt never happened, so it is not allowed to happen.

If the sink stutters mid-flight, writes queue in memory for five minutes before the kernel fails. The diagnostic door is `capcli sys doctor`; the spine itself is covered in [audit.md](audit.md).

---

## `6` — yield

Provider quota ran dry and the task is Background or Standard class. Instead of crashing, the frame is serialized into `_suspended_tasks` with a `resume_at` epoch, and the daemon re-queues it when the window reopens:

```
[prod:tier_1]  ✗  exit 6

  YIELD  policy.api.quota_exhausted
         routine broadcast_newsletter@2 (frame_018)
         provider: threads
         verb:     threads.create_media_post

  state_modified:  false
  layer:           quota
  tokens_left:     0 / 50 (24h window)
  reset_at:        18:00:00 UTC (in 4h 12m)
  suspended_frame: task_99a8b1
  remedy:          task safely yielded; daemon will auto-resume at reset_at
```

A Critical task on a dry pool doesn't yield — it gets exit 2, because a human may be waiting on it. Yield is the courtesy the kernel extends to work that can afford to wait.

---

**Which rule just denied you?** → [errors.md](errors.md)

**Was it a ceiling?** → [limits.md](limits.md)
