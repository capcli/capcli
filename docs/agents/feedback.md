# Feedback

Denial is information. Blind retry is noise.

Every outcome Capcli hands you is machine-readable: an exit code, an envelope, and — for anything that touched the DAG — a trace. Your loop is: read it, change something, re-issue. Never: read it, re-issue.

---

## The decision table

| Exit | What happened | What you do |
|---|---|---|
| `0` | Effect committed, audited | Parse the envelope, continue |
| `2` | Policy denial — AST, authorizer, budget, trust | Read the rule id + `remedy`, change the call |
| `3` | You malformed the request — missing intent, param mismatch, drift | Fix your inputs |
| `4` | Runtime crash; transaction rolled back | Don't auto-retry — trace the failing leaf, fix, re-prove in sim |
| `5` | Kernel panic; audit sink unreachable | Stop. Escalate to a human |
| `6` | Quota yield | Park. Retry after refill — below |

The one law: **never blind-retry a policy denial.** Denials are deterministic. The same call hits the same wall. The wall does not get tired.

---

## Read the denial, then trace it

```bash
$ capcli sql "UPDATE orders SET status = 'shipped' WHERE status = 'processing'" \
    -m "batch ship"
```

```
[dev:tier_1]  ✗ exit 2

  FAIL  policy.query.update_delete.require_limit
        UPDATE orders SET status = 'shipped' WHERE status = 'processing'
                                                                   ^^^^^^
        No LIMIT clause. Blast radius unbounded.

  state_modified: false
  layer: AST
  measured: matches potentially 847 rows (cap: 100)
  remedy: add LIMIT, or target specific primary key
  audit:  op_5c21
```

Anatomy: `FAIL` rule id, rejected statement with the offending span, `layer`, `measured` (observed vs ceiling), `state_modified: false`, `remedy`. Denied operations still emit audit events — with `effect: none` — so the denial itself is traceable:

```bash
$ capcli sys audit trace op_5c21 --explain
```

```
[dev:tier_1]  op_5c21  trace

  op_5c21    sql.query    denied    effect: none
    rule:            policy.query.update_delete.require_limit
    layer:           AST
    state_modified:  false
    remedy:          add LIMIT, or target specific primary key
  caused_by:  ses_a992f (session root)
  agent:      agt_7f3k
  principal:  user:alice
```

`trace` walks the causal DAG to the root intent. `--explain` prints the exact policy rules and remediation. Between the two, no denial is ever a mystery — it's a named rule with a named fix. This is H5 of the harness onboarding journey.

Apply the remedy — which means changing the call:

```bash
$ capcli sql "UPDATE orders SET status = 'shipped' WHERE status = 'processing' LIMIT 100" \
    -m "batch ship first 100"
```

```
[dev:tier_1]  ✓  42ms

  rows_affected: 100
```

Changed call, different outcome. That's the whole loop.

---

## Exit 6: park, then retry after refill

A yield is not a denial. The bucket was dry; the kernel parked the frame in `_suspended_tasks` with zero partial side effects; the daemon re-queues on token refill. For foreground work: read the provider's `reset_at` from inspect, wait past it, retry once.

Retrying into a dry bucket converts a clean yield into thrashing. Don't.

---

## Exit 4 and 5: when to stop being autonomous

Exit 4 means your code crashed in the sandbox and the transaction rolled back cleanly. Trace the failing leaf, fix the routine, re-prove in sim. Forensic quarantine exists precisely to prevent auto-retry on unhandled runtime faults.

Exit 5 means the audit spine itself is unhealthy. There is no clever move here. Halt and escalate — the kernel already refused to run anything unaudited on your behalf.

---

## Thrashing is a signal about *you*

Twenty sustained denials triggers an agent thrashing alert:

```
[dev:tier_1]  ⚠  agent.thrashing

  agent: agt_7f3k
  denials_last_5m: 22
  pattern: repeated policy.query.update_delete.require_limit
  remedy: harness appears stuck; consider changing approach or escalating to human
```

If you see your own agent id in a thrashing alert, the problem is your approach, not Capcli's policy. Change course or escalate via ping. And upstream 429/503 responses are already retried with backoff and jitter by the kernel proxy — don't stack your own retry loop on top.

---

## Codify the lesson

The same remedy applied twice is a habit. The same habit applied every week is a routine waiting to exist. Denial patterns are training data: fold the fix into governed code instead of remembered behavior → [codification.md](codification.md).

---

**Same wall, every week?** → [codification.md](codification.md)

**Human-facing denial tour** → [../use/boundaries.md](../use/boundaries.md)
