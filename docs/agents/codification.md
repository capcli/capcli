# Codification

You've issued the same op sequence four times this week. The audit spine noticed before you did.

Codification is the move from remembered behavior to governed code: a repeatable sequence becomes a routine with a version, a manifest, and a trust ladder to climb. You stop re-deriving; you start invoking.

---

## The signal is already in the ledger

The kernel maintains deterministic SQL mirror views over the audit spine — no inference, just counting:

- `op_frequency` — atomic op calls across sessions
- `shared_subsequences` — frequent n-grams, i.e. routine proposals
- `primitive_cost` — duration p50/p95, fuel, wire bytes per leaf
- `primitive_failures` — failures isolated by version and sequence

Query them through `capcli sys audit query`. When the same subsequence keeps appearing, that's the registry asking you to name it. The background miner is a hint, not a gate — direct drafting is ungated from day zero.

---

## Search before you build

Before scaffolding, search. The capability may exist under a name you didn't expect, and the gap report may already be tracking demand for it (`run search gaps --since 7d` → [discovery.md](discovery.md)).

Duplicates don't slip through either: routine similarity above 0.85 demands a `--reason` justification at draft time, and near-duplicates across agents force a merge or fork.

---

## Scaffold

```bash
$ capcli routine new refund_report
```

```
[dev:tier_1]  refund_report  ✓  scaffolded

  file:        routines/refund_report.py
  trust:       draft (version 1)
  shape_gate:  pass
  next:        capcli routine prove refund_report --env sim
```

Decode: the filesystem is the draft SSOT. `routine new` is optional scaffolding — a hand-written `routines/<name>.py` is equally valid intake. Either way the stub passes `shape_gate` before it touches disk and registers strictly at draft trust, version 1. Templates (`--template <ptr|path>`) confer zero promotional credit; imports enter at draft no matter what they promise.

---

## The smallest correct unit

A routine is one learned composition, not a framework. The shape ceiling:

| Constraint | Ceiling |
|---|---|
| Lines of code | 150 |
| File tokens | 2,000 |
| Typed params | 8 |
| Ops per run | 50 |
| Duration | 300s |
| Txn statements | 10 |
| Result tokens | 500 — over-size returns `truncated: true` |
| Description | required — if agents can't search it, it doesn't ship |

150 is a ceiling, not a target. If your routine wants to be 400 lines, it wants to be three routines.

---

## The overview routine is mandatory

H6 of the harness onboarding journey: author a routine named `overview` — `routines/overview.py` — to ground every future agent in domain state.

```bash
$ capcli run overview --json
```

```
{
  "exit": 0,
  "json": {
    "kpi": "orders: 4281 rows",
    "pending_asks": 0,
    "inbox_queued": 0,
    "active_locks": 0,
    "budget_headroom": "80400 fuel remaining",
    "health": "nominal"
  },
  "text": "[dev:tier_1]  overview  ✓  500 token cap"
}
```

The contract: `@routine(name="overview", idempotent=true)`, a dense situational summary capped at 500 result tokens — domain KPIs, pending asks, sensory inbox counts, active locks, budget headroom, system health. It executes as a standard zero-step at session boot, so the next agent (possibly future you) starts with situational awareness instead of a blind schema crawl. It's the cheapest token savings in the whole system.

---

## Then earn the rung

Draft routines run in dev and sim only. They can't read secrets, can't touch prod, and can't serve as dependencies for other agents' routines — cross-agent callees must hold trust ≥ reviewed. The path out of the nursery is proof: [rehearsal.md](rehearsal.md), then [proving.md](proving.md).

---

**Ready to prove it?** → [proving.md](proving.md)

**The human version of this journey** → [../automate/routines.md](../automate/routines.md)
