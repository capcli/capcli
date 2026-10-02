# Exit Codes

Six integers. Total. Your harness builds its entire control flow on these, so the kernel keeps the list short and the semantics brutal.

---

## The law

| Exit | Name | Meaning | State guarantee |
|---|---|---|---|
| `0` | **Success** | Committed, hashed into the causal ledger. Upstream HTTP failures are handled gracefully inside the envelope — a vendor 500 is *data*, not a kernel crisis. | Modified |
| `2` | **Policy denial** | Blocked by authorizer, AST, trust rung, or budget. `state_modified: false` is a mathematical guarantee, not a promise. | Untouched |
| `3` | **Refusal** | Compile/validate-time no: missing intent, missing param, lockfile mismatch, clock drift > 500ms, unparseable input. | Untouched |
| `4` | **Crash** | Uncaught sandbox runtime exception. Transaction cleanly rolled back. | Rolled back |
| `5` | **Kernel panic** | Audit sink unreachable or host resource failure. Nothing runs unaudited — including the rest of your session. | Untouched |
| `6` | **Yield** | Provider quota dry. Task parked in `_suspended_tasks` until the refill epoch. | Untouched |

## The state rollback law

> **Any non-zero exit guarantees `state_modified: false`.** A partial commit is classified as a critical kernel bug, not as "Tuesday."

There is no exit code for "mostly worked." If rows 1–34 committed and row 35 exploded, that's `exit 4` *with a full rollback* — the 34 never happened. Atomicity is a floor here, not a feature flag.

## Which `exit 2` domain fired

`exit 2` is a family; the envelope's `domain` field names the parent:

```text
db.engine          SQLite check constraints, FK violations, busy timeout
policy.authorizer  C-level table/column denial
policy.budget      frame or session op/fuel ceiling hit
policy.trust       action forbidden at caller's rung
```

The remedy differs per family: `db.engine` means fix your data; `policy.budget` means split the work; `policy.trust` means earn a rung or change env; `policy.authorizer` means that door has no key at your level, period.

## Exit 6 vs exit 2 on quota

Quota exhaustion yields differently by criticality:

- **Background task** hit the bucket → `exit 6`, parked, auto-resumes at refill. Do nothing.
- **Critical (interactive) call** hit the bucket → `exit 2`, denied. Because a foreground caller waiting 6 hours isn't patience, it's a zombie.

## Exit 3's favorite causes

In order of observed frequency (yours, not ours — the ledger sees everything):

1. Missing `-m` on a write. (Writes. Need. Intent.)
2. Missing `-p` parameter the envelope told you about at inspect time.
3. Lockfile mismatch — someone hand-edited YAML; `git checkout` it.
4. Clock drift > 500ms vs NTP. Claims need causality; causality needs a clock.

## For harness authors

Map integers to behavior, not to strings. Never parse the prose — the prose is for humans and post-mortems. `2` → read `remedy`, reformulate. `3` → fix invocation. `4` → report op-id. `5` → halt and escalate. `6` → switch tasks. Retrying `2` unchanged is a loop with extra steps, and the kernel will win the staring contest. It always has. It's compiled that way.
