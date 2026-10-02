# You're Back

You used Capcli before. Maybe last week. Maybe last quarter. You don't need another "What is Capcli?" — you need the answer to exactly one question:

**Where do I pick up?**

Sixty seconds. Five commands. Type them in order.

---

## 1. Is the machine sane? `sys doctor`

```bash
$ capcli sys doctor
```

```
[dev:tier_1]  capcli 0.4.2

  host:       linux x86_64
  tier:       1 (hardened)
  sandbox:    bwrap 0.8.1
  engine:     bun 1.2.4
  python:     3.12.1
  git:        2.44.0
  lockfile:   capcli.lock ✓
  schema:     schema.yaml ✓
  policy:     policy.yaml ✓
  governance: governance.yaml ✓

  status:     ready
```

Tier, sandbox, lockfile, all four YAMLs. If anything refuses here, it's a boot problem — [troubleshooting.md](troubleshooting.md), sections 2 and 5. Want the minimal probe? `sys doctor --boot-check` verifies boot without the daemon.

---

## 2. Which world am I in? `env list`

```bash
$ capcli env list
```

```
[dev:tier_1]  3 environments

  dev     schema v15   active
  sim     schema v15   seeded 6d ago
  prod    schema v15   current
```

Environments are sticky — the last `env use` wins until you say otherwise, and `--env` overrides per command. Travelling is one command: `capcli env use sim`. If sim's seed data is getting stale, `env inspect` will nag you to re-seed once it passes 14 days.

---

## 3. What exists now? `run search`

```bash
$ capcli run search "orders"
```

```
[dev:tier_1]  3 results

  cap://dispatch_order@5     routine    pinned    "Dispatch paid order to carrier"
  cap://order_refund@7       routine    reviewed  "Refund and archive cancelled order"
  db://orders                table      —         "Core order state"
```

Capabilities you forgot you had, ones that were promoted while you were away, and the trust rung each one carries now. If a search keeps coming up empty, `capcli run search gaps --since 7d` shows the holes worth filling.

---

## 4. What happened recently? `sys audit tail`

```bash
$ capcli sys audit tail --since 1h
```

```
[dev:tier_1]  audit tail  ✓  4 events

  ts          event                    decision   agent      capability
  ──────────  ───────────────────────  ─────────  ─────────  ──────────────────
  ...         run.dispatch_order       allow      agt_7f3k   cap://dispatch_order@5
  ...         db.exec                  allow      agt_7f3k   orders (write)
  ...         sql.query                denied     agt_7f3k   orders (delete)
  ...         budget.frame_pop         allow      agt_7f3k   frame_021
```

One hour of history: what ran, what got denied, who did it. Denials in the tail are walls doing their job — someone attempted an unbounded delete and reality declined. Add `--follow` to keep watching live.

---

## 5. Did my jobs keep running? `routine stats`

```bash
$ capcli routine stats dispatch_order
```

```
[dev:tier_1]  dispatch_order@5  ✓  stats

  runs:      214 total
  success:   99.1%
  latency:   p50 340ms · p95 890ms
  last_run:  22m ago (bind://nightly_dispatch)
```

Crons fired, routines ran, and every one of them left evidence. While you were away, the kernel also kept committing — every 15 minutes and on every apply, promote, and merge — and a doctor alarm fires if the repo drifts past 30 minutes. Nothing waited for you.

If the numbers look wrong, `--deep` gets the full profile. If dead weight accumulated, `capcli routine sweep` finds the failing and duplicate routines (default window: 30 days).

---

## The cheat code: `run overview`

Five commands is the tour. One command is the briefing:

```bash
$ capcli run overview
```

```
[dev:tier_1]  overview@1  ✓  24ms

  environment: dev (Tier 1 Hardened)
  schema:      v15 (nominal, 0 drift)
  policy:      v5 (locked, hash: sha256:77a1...)
  last_action: 22m ago (db.execute: orders.ORD-9912 status='shipped')
  active_lock: none
  drift_alert: 0 uncommitted changes
  next_step:   ready for incoming triggers
```

Environment, schema, policy, last effect, locks, and a proposed next step — the same grounding briefing every fresh agent session starts with. Sub-500 tokens, zero amnesia.

---

## Welcome back

The walls are where you left them. The worlds kept their shape, the routines kept their evidence, and the ledger never stopped. The doctor still says `ready`.

**Something broke while you were gone?** → [troubleshooting.md](troubleshooting.md)

**Need yesterday's database back?** → [recovery.md](recovery.md)

**Schema drifted while you were away?** → [migration.md](migration.md)

Welcome back. The kernel never slept.
