# Routines

A routine is the moment your ad-hoc hack swears an oath.

Technically: **a versioned, sandboxed, multi-step script (TypeScript or Python) that bundles queries, API calls, and logic into one governed unit with a locked manifest.** Spiritually: your script going to civil service school.

---

## The lifecycle

```
author → prove → ship → run → sweep → (rollback | retire)
```

**Author.** Your harness writes `routines/order_refund.ts` directly — or scaffolds a starter:

```bash
$ capcli routine new archive_old_orders
```

```text
[dev:tier_1]  ✓  scaffolded

  file:       routines/archive_old_orders.ts
  template:   standard (db.query → db.execute)
  trust:      draft
  next:       edit logic, then `routine prove archive_old_orders`
```

Inside, the code doesn't talk to SQLite. It talks to `ctx` — the kernel-mediated contract (`ctx.db.query`, `ctx.api.call`, `ctx.log`). No raw drivers, no `requests.post`, no `while(true)` diplomacy. The physics intercepts every primitive.

**Prove.** Rehearsal against simulation — its own page: [rehearsal.md](rehearsal.md).

**Ship.** Promotion up the trust ladder — also its own page: [promotion.md](promotion.md).

---

## Running one

```bash
$ capcli run dispatch_order -p order_id=ORD-8842 -p carrier=fedex \
    -m "fulfill paid order for customer checkout"
```

```text
[dev:tier_1]  dispatch_order@4  ✓  1.2s

  status:    dispatched
  tracking:  794644790133
  ops_used:  3/8
  audit:     op_9f2c → op_9f2d → op_9f2e
```

Under the hood the kernel did what it always does: session token checked, intent bound, budget frame pushed (the `min()` cascade), each `ctx` primitive gated and audited, and the whole run hashed into the causal DAG. If op 9 of 8 blows the frame? `exit 2` at the frame boundary. No half-executed side effects — a partial commit is classified as a *kernel bug*, not a Tuesday.

---

## The manifest is the contract

Every routine carries a locked manifest — the exact call sequence:

```text
manifest:  db.query → api.call(logistics.shipments.create) → db.execute
```

When you `inspect`, you see it. When the kernel runs, it *enforces* it — the version hash is pinned, so "routine" and "what the routine does" can't quietly drift apart. Swap the manifest without a new version and a new `prove`? Not an option. The lockfile has opinions.

---

## Maintenance isn't optional — it's automated

Routines decay. Success rates sag. Circuits demote. The registry notices before you do:

```bash
$ capcli routine sweep --since 30d
```

```text
[dev:tier_1]  1 of 12 routines flagged

  routine              runs   success   signal
  ───────────────────  ─────  ────────  ─────────────────────────
  archive_old_orders   41     68.3%     below 70% floor — demote candidate
  dispatch_order       214    99.1%     healthy
  order_refund         89     97.8%     healthy
```

`archive_old_orders` is failing a third of the time. Sustained failure auto-demotes it to `draft` and the sweep names it. Old versions stay reachable for `routine rollback`, and `routine retire` decommissions without destroying provenance — history is forever, employment is not.

---

## Where the exact syntax lives

The full verb table for `capcli routine` — `new`, `prove`, `ship`, `stats`, `rollback`, `sweep`, `retire` — is documented command-by-command here:

→ [../reference/commands/routine.md](../reference/commands/routine.md)

---

**Before it earns trust: the dress rehearsal** → [rehearsal.md](rehearsal.md)
