# Hard Limits & Ceilings

Hit an exit code or denial? Check the ceilings. Every number below is attested — in `cans/governance.yaml`, `cans/policy.yaml`, `cans/physics.md`, or the verified command pages — and every row is marked with the noun that owns it.

The ceilings are compiled into the kernel at boot. There is no runtime knob. There is no `--override-budget`. Exceptions are git commits — which is rather the point of having a kernel.

---

## Triggers & humans

| Ceiling | Value | Noun |
|---|---|---|
| Cron interval floor | `*/5` — sub-5-minute schedules exit 3 | `bind` |
| Webhook payload | 64 KB (65,536 bytes); oversized returns `413` | `bind` |
| Webhook arrival rate | 100 events/minute | `bind` |
| Dead letter queue | 30 days or 1,000 items, FIFO purge | `bind` |
| Partner keys | 25 per workspace | `bind` |
| Partner key TTL | 90 days — immortal keys are structurally impossible | `bind` |
| Served endpoints | 10 | `bind` |
| Active schedules | 20 (max 10 per agent) | `bind` |
| Ask options | max 5 discrete choices; free text banned | `ping` |
| Question length | 100 tokens | `ping` |
| Notification length | 300 tokens | `ping` |
| Ask timeout | default 60 min, max 480 min | `ping` |

## Routine shape

| Ceiling | Value | Noun |
|---|---|---|
| Lines of code | 150 | `routine` |
| File size | 2,000 tokens | `routine` |
| Parameters | 8 | `routine` |
| Routine imports | 3 | `routine` |
| Description | min 5 words, max 60 tokens | `routine` |
| Versions kept | 25 | `routine` |
| Rollback depth | 5 versions | `routine` |
| Composition nesting | 5 levels | `routine` |
| Registry size | 300 routines hard cap (200 soft) | `routine` |
| Routine creation rate | 10 per hour | `routine` |

## The catalog

| Ceiling | Value | Noun |
|---|---|---|
| Providers | 10 | `api` |
| Verbs per provider | 500 | `api` |
| Active verbs per provider | 50 | `api` |
| Activations | 10 per hour | `api` |
| Sync interval floor | 24 hours | `api` |
| Compiled catalog size | 10 MB | `api` |

## Worlds, rates, and the kernel

| Ceiling | Value | Noun |
|---|---|---|
| Concurrent environments | 5 | `env` |
| Prod write rate | 60 writes/minute | policy rate |
| Sim write rate | 1,000 writes/minute | policy rate |
| NTP drift boot gate | >500 ms aborts boot | `sys` |
| Universal flags | exactly 12, frozen | `cli` |

## The budget cage

| Ceiling | Value | Noun |
|---|---|---|
| Ops per run | 50 — op #51 aborts | budget |
| Session ops | 500 | budget |
| Wall clock | 300-second watchdog kill | budget |
| Result tokens | 500 per routine, `truncated: true` past it | budget |
| Rows affected | 10 draft / 100 reviewed / 500 pinned | trust |
| SELECT LIMIT | 10,000 | `sql` |
| INSERT rows | 500 per statement | `sql` |
| UPDATE/DELETE | WHERE + LIMIT mandatory · LIMIT ≤ 1000 · 100 rows max affected | `sql` |
| Session fuel | 100,000 dev / 500,000 prod | budget |
| Egress per call | 5 MB | budget |

---

## What hitting a ceiling looks like

The kernel cites the measured value against the cap, then hands you the remedy:

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

Same shape whether it's 342 LOC against the 150 cap or 0 tokens left in a 24-hour window: the number, the ceiling, the remedy. Full anatomy in [errors.md](errors.md).

The escape routes are all structural — split the routine, raise the declared limits in governance YAML (a git commit), or wait for the window to reset. What is never on the table is a flag that pretends the ceiling isn't there.

---

**Which ceiling produced which exit code?** → [exit-codes.md](exit-codes.md)

**Full denial anatomy** → [errors.md](errors.md)
