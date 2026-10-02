# Feedback Contract

Every failure is a structured message. Read it, act on it, move on.

Denials are not insults. They are the system *teaching you its own boundaries* — at machine speed, in a stable format, with a `remedy` field that exists specifically so you don't have to guess.

---

## The denial anatomy

```text
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

Parse it in this order:

| Field | Meaning | Your action |
|---|---|---|
| `exit` | The class of failure | `2` = re-formulate; `3` = fix invocation; `6` = wait |
| `FAIL <rule code>` | The exact policy rule that fired | Look for prior successes on this rule — learn the pattern |
| `layer` | Which floor said no (AST / authorizer / trust / budget) | Tells you what *kind* of change helps |
| `measured` | The measurement that triggered it | The system counted; the count is the argument |
| `remedy` | The sanctioned next move | **Do this.** It is not a hint. It is the contract's answer key. |

## Decision by exit code

```
exit 2  →  re-formulate the statement (add WHERE/LIMIT, split work, promote trust via the human)
exit 3  →  your invocation is malformed (missing -m, missing -p, bad pointer) — fix and resubmit
exit 4  →  the routine crashed inside the sandbox; transaction rolled back cleanly. Report the op-id.
exit 5  →  kernel panic (audit sink unreachable). Halt. Escalate to human. Do not loop.
exit 6  →  yield. Quota dry. Task parked in _suspended_tasks until the refill epoch. Switch context.
```

**Never** respond to `exit 2` with an identical retry. The gates are deterministic; the same input earns the same no, forever, with the patience of a mountain. Change the input.

## Yields are gentle

```text
[dev:tier_1]  ✗  exit 6

  FAIL  api.quota
        provider: threads
        remaining: 0 (window: 50/50 calls in 24h)
        yield_until: 2026-10-03T09:12:00Z
        task: parked → _suspended_tasks (task_a41f)

  state_modified: false
  remedy: no action required; task resumes at refill
```

A yield is not an error. It is the kernel *deferring* your work until the bucket refills — while guaranteeing `state_modified: false` in the meantime. Polling the endpoint to "check if it's better now" burns the very quota you're waiting for. Go do something else. The task wakes itself.

## Escalating to a human

When the boundary requires human judgment (a $14,000 refund "request," an ambiguous cleanup), do not decide. File a structured inquiry:

```bash
capcli ping ask user:ops-lead "Wipe demo data in dev environment?" \
    --options "approve,reject" --timeout 30 -m "confirm staging reset before testing"
```

Enumerated options only (max 5), bounded question, hard deadline, fail-closed on expiry. You are not asking a human because you're polite — you're asking because self-deciding at the edge of policy is how 2am incidents are born.

Full surface: [../use/ask-human.md](../use/ask-human.md).

---

**Turn your repeated recoveries into routines** → [codification.md](codification.md)
