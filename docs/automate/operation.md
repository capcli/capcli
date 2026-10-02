# Operation

The routine is pinned. A cron or webhook fires it while you're at the beach. Congratulations — now the job is *watching receipts*, not terminals.

This is the last rung of the automation ladder: the work runs itself, and your job shrinks to supervising telemetry, handling exceptions, and — eventually — turning things off.

---

## Wiring it up

Nothing runs loose. Work fires on *stimulus*, and stimulus is a binding:

```bash
$ capcli bind cron nightly_archive archive_old_orders "0 3 * * *" -m "archive orders older than 90 days"
```

```text
[dev:tier_1]  ✓  bound

  handle:     bind://nightly_archive
  trigger:    cron 0 3 * * *
  capability: cap://archive_old_orders@3
  catchup:    max 1 per reboot (stale runs discarded)
  next_fire:  03:00
```

Cron floor: 5 minutes (`exit 3` below that — sub-5-minute schedules are a denial-of-service on yourself). Webhooks need a public ingress or tunnel with mandatory HMAC — raw `127.0.0.1` ingress is refused, and "the agent will just poll in a loop" is banned by physics. Agents here are event-driven, not caffeinated.

---

## The morning check

You don't read logs. You read the *state of the bindings* and the *tail of reality*:

```bash
$ capcli bind list
```

```text
[dev:tier_1]  2 bindings

  handle                 trigger    capability             state     health
  ─────────────────────  ─────────  ─────────────────────  ────────  ─────────
  bind://nightly_archive cron       archive_old_orders@3   active    41 fires · 68.3% ok
  bind://order_webhook   webhook    process_order@2        active    812 fires · 99.6% ok
```

`nightly_archive` at 68.3% is below the 70% floor. The demotion circuit has already flagged it — this is the "monitoring" part of operation where you *do* something:

- Diagnose: `capcli sys audit trace <op-id> --explain` on a failed fire
- Fix and re-prove: `routine prove … --env sim`
- Or fold it: `bind pause`, fix, `bind resume`

Failure output is structured, denial-shaped, and comes with a `remedy:` line. Operation is mostly reading remedies and acting on them — the system narrates its own incidents.

---

## The receipt ritual

```bash
$ capcli sys doctor --report
```

```yaml
trust_receipt:
  status:            nominal
  workspace:         envs/dev/workspace.db
  ledger_root_hash:  sha256:7f9a1b...
  audited_events:    847
  policy_denials:    2 (pre-execution; state untouched)
  unaudited_writes:  0
  secret_leaks:      0
  pinned_routines:   3
  sleep_score:       100%
```

That's the whole ops dashboard for most days: zero unaudited writes, zero leaks, and denials that *protected* you. The number that matters is `sleep_score`, and it's binary in disguise.

---

## Change is normal

Operating isn't freeze-frame. Routines get new versions (old pointer rewinds via `rollback`), schemas evolve through `rule apply` migrations, rate buckets refill, and everything — *everything* — lands in the DAG. When a fire at 03:00 goes sideways:

1. **Snapshot** — `db snapshot` before surgery (it's cheap and point-in-time safe via `VACUUM INTO`)
2. **Restore** — `db restore <snap_id> -m "revert the 3am incident"` — seconds, not a restoration drama
3. **Explain** — `sys audit trace` the failed op back to the binding that fired it

Full disaster playbook → [../guides/recovery.md](../guides/recovery.md).

---

## Subtraction is a first-class operation

The last act of operation is *turning things off* — and Capcli treats it with the same ceremony as turning things on:

- `bind remove` — unbind and archive the record
- `routine retire --reason "…"` — decommission, provenance preserved forever
- `api retire` — same, for external verbs

Nothing vanishes from history. The ledger remembers what ran, what it did, and when it stopped. Turning it off is an event too — the only things that get deleted are the *chances to break prod*, and that's the point.

---

**When something specific breaks** → [../guides/troubleshooting.md](../guides/troubleshooting.md)
