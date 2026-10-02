# Invocation Contract

One command. Five gates. One integer verdict.

---

## The call

```bash
capcli run <capability> [-p k=v]... -m "<causal intent>" [--lock <t>:<ref> --ttl <s>]
```

```text
[dev:tier_1]  dispatch_order@4  ✓  1.2s

  status:    dispatched
  tracking:  794644790133
  ops_used:  3/8
  audit:     op_9f2c → op_9f2d → op_9f2e
```

Mandatory: `-m` intent on anything that mutates. Optional but wise: `--lock` for multi-step exclusive access (lease-based, TTL'd in `_claims` — crash and it expires; no orphaned locks, no deadlocks, no ghost exiles).

## The pipeline your invocation enters

```
Stage 0 — session token verified
Stage 1 — intent bound, blast radius checked
Stage 2 — AST parsed, patterns scanned
Stage 3 — authorizer callback + EXPLAIN cross-check
Stage 4 — SQLite executes, audit event emitted
```

Any stage fails ⇒ execution stops ⇒ state untouched. You cannot see the gates. You cannot configure the gates. You can only read their verdicts.

## Reads vs writes

```bash
# Read — free, bounded, no intent needed
capcli sql "SELECT id, status FROM orders WHERE status = 'pending' LIMIT 10"

# Write — intent mandatory, one miss = exit 3
capcli sql "UPDATE orders SET status = 'processing' WHERE id = 'ord_9885' LIMIT 1" \
    -m "mark oldest pending order as processing"
```

Parameterization is mandatory — positional or named bindings, never string interpolation. Multi-statement execution is denied. `UPDATE`/`DELETE` without `WHERE` and `LIMIT` die at AST parse. You know this. The parser knows you know. The parser does not care.

---

## The exit code contract — memorize this table

| Exit | Meaning | State | Your move |
|---|---|---|---|
| `0` | Success, committed, hashed into ledger | Modified | Read the payload. Report. |
| `2` | Denial — policy/AST/authorizer/trust/budget | **Untouched** | Read `remedy:`, re-formulate. Do NOT retry blindly. |
| `3` | Refusal — missing `-m`, missing param, bad syntax, lockfile drift | Untouched | Fix the invocation. Usually `-m`. Almost always `-m`. |
| `4` | Crash — sandbox runtime exception | Rolled back | Inspect the routine; the transaction is clean. |
| `5` | Kernel panic — audit sink unreachable | Untouched | Stop. Surface to human. Nothing runs unaudited, including you. |
| `6` | Yield — provider quota dry | Untouched | Wait for refill epoch or switch task. The task is parked in `_suspended_tasks`, not lost. |

`exit 2` on the same command twice is a signal about *your formulation*, not the kernel's mood. There is no mood. There is only the contract.

## Output contract

- Every stream is prefixed `[env:tier]` — you always know which world you're in. If you see `[prod:tier_1]`, act accordingly; you were warned in ASCII.
- Pass `--json` for a pure machine envelope: `domain`, `culprit`, `remedy`, `state_modified`. Structured, stable, no filler.
- Result tokens cap at 500/routine; overruns return `truncated: true`. Design around it: filter in SQL, not in your prompt.
- `--out <path>` redirects payloads to disk; stdout shrinks to a receipt under 30 tokens. Move bulk, don't recite it.
- Shell escaping defense: every argument accepts `@<path>` (file) or `@-` (stdin) to bypass quoting hell and ARG_MAX. Multi-statement via `@-` is rejected unless batch mode is explicit.

---

**Before real stakes: rehearse** → [rehearsal.md](rehearsal.md)

**When the integer isn't 0** → [feedback.md](feedback.md)
