# Hard Limits & Ceilings

Every number here is compiled into `governance.yaml` and enforced at boot. None of them are suggestions, and none of them are configurable at runtime — an agent that could raise its own ceilings would defeat the entire product in one flag.

Hit a ceiling and you don't get a warning. You get an exit code and a measured value. ("File has 342 LOC, max is 150" — the denial *cites the ruler*, not just the rule.)

---

## Registry

| Limit | Value |
|---|---|
| Routines in registry (hard / soft) | **300 / 200** (doctor nags past soft) |
| Draft routines per agent | **30** — anti-flood |
| Capability description | **60 tokens** |
| Versions kept per routine | **25** · rollback depth **5** |
| Routine size | **150 LOC · 2000 tokens · 8 params · 3 imports** |

## Execution (the budget cage)

| Limit | Value |
|---|---|
| Ops per run | **50** (op 51 aborts, no partial state) |
| Routine watchdog | **300 s** (SIGKILL) |
| Result tokens per routine | **500** (then `truncated: true`) |
| Statements per transaction | **10** (one txn = one thought) |
| Session ops ceiling | **500** · exploratory reserve **200** |
| Fuel (session) | **100k dev / 500k prod** |
| Wire egress per call | **5 MB** hard-trapped |
| Rows per write (trust rung) | **10 draft / 100 reviewed / 500 pinned** |
| Writes/min (prod) | **60** |
| Sandbox scratch | **64 MB tmpfs** |
| Nesting depth (composition) | **5** |

## Quota & suspension

| Limit | Value |
|---|---|
| Earmark TTL | **24 h** (aligned to rolling windows) |
| Max deferred yields | **5** |
| Suspended tasks (daemon queue) | **100** |
| Async poll window | **30 s** |

## APIs & triggers

| Limit | Value |
|---|---|
| Providers / verbs per provider / active per provider | **10 / 500 / 50** |
| Compiled catalog size | **10 MB** (specs >10 MB prune unreferenced paths) |
| Activations per hour | **10** · retries before human-ask fallback **3** |
| Cron interval floor | **5 minutes** (`exit 3` below) |
| Webhook payload / arrival | **64 KB / 100 events/min** (oversize = `413`) |
| DLQ retention | **30 days / 1000 items**, FIFO purge |
| Endpoints / partner keys | **10 / 25** — keys expire in **90 days**, immortality banned |
| Bindings active / per agent | **20 / 15** |

## Humans (the ping path)

| Limit | Value |
|---|---|
| Notification channels | **3** · message **300 tokens** |
| Ask question | **100 tokens · max 5 options** |
| Ask timeout | default **60 min**, max **480** — expiry is fail-closed `exit 2` |
| Quiet hours | **22:00–07:00** host time (ask may bypass only if it blocks a live routine) |
| Session consolidation | **30 min · 10 proposals** (human review stays human-sized) |

## Worlds & data

| Limit | Value |
|---|---|
| Environments | **5** |
| Agent-authored tables | **100** |
| Seed rows per table (templates) | **50** — no bulk injection via template |
| Upload per object | **10 MB** · bundle transfer **5 MB** |
| Ledger mirror lag | **5 min** SLA |
| Docs read | **100 tokens default** `--max-tokens`, **20 results** per search |

## Host & boot physics

| Limit | Value |
|---|---|
| Clock drift vs NTP | **500 ms** — boot aborts (`exit 3`) |
| Audit sink buffer before panic | **5 minutes** → `exit 5` |
| Host git commit freshness | doctor alarms at **30 min drift**, force-push at **90 days** |
| Platform floors | python ≥ **3.11**, git ≥ **2.30**, bwrap ≥ **0.8.0** on Tier 1 |

---

**Why ceilings?** Because "unbounded" is the one design decision with a guaranteed 2am post-mortem. Every number above is a fence at the exact spot where someone, someday, was going to find out the hard way. The fence was cheaper.
