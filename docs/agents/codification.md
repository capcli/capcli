# Codification Contract

The third time you execute the same recovery dance, you're no longer solving a problem. You're performing one.

Codification is how an agent's repeated useful behavior becomes a **routine** — a governed, versioned capability instead of a habit.

---

## The signal

```bash
capcli run search gaps --since 7d
```

```text
[dev:tier_1]  2 gaps detected

  query: "inventory sync"     searches: 8    invocations: 0    signal: missing capability
  query: "customer export"    searches: 5    invocations: 0    signal: missing capability
```

Also check your own audit trail: same SQL shape, re-derived, run repeatedly? Same API call sequence with fresh params each time? That's codification begging to happen. The ledger already knows. It's just too polite to say it first.

## The path

```
1. scaffold       capcli routine new <name>            (or write routines/<name>.ts directly)
2. codify         write the logic against ctx.* only   (ctx.db, ctx.api, ctx.log — no raw drivers)
3. rehearse       capcli routine prove <name> --env sim
4. ship           capcli routine ship <name> reviewed  (with evidence, when earned)
5. bind           capcli bind cron|webhook|endpoint ...  (when it should run itself)
```

Inside the routine, every primitive goes through the kernel contract:

```text
ctx.db.query(...)     → gated read, rows bounded
ctx.db.execute(...)   → gated write, intent inherited from the run's -m
ctx.api.call(verb)    → catalog verb, quota-metered, secret-blind
ctx.log(...)          → structured, hashed into the run's outcome event
```

No `requests`, no `sqlite3` import, no filesystem freelancing. The sandbox's `connect` syscall is trapped (exit 2 at the CPU); raw DB files are behind daemon IPC. The routine that *thinks* it's above the kernel is a routine that dies at op 1 with a very educational denial.

## What codification buys

- **You stop re-deriving.** One inspect instead of ten minutes of SQL archaeology.
- **Budgets attach to the unit.** Declared ops, declared ceiling — enforced by the cascade, not by your memory.
- **Trust attaches to the unit.** The routine climbs the ladder with evidence. Your (excellent, honestly) vibes were never currency anyway.
- **Provenance attaches to the unit.** Every future run cites the routine version, not "that thing the model improvised on the 14th."

## The floors you cannot charm

- New routines enter at **draft**. Always. No exceptions, no inherited credit.
- Callee routines must be `reviewed`+ to be dependencies. Drafts can't be load-bearing.
- Promotion requires rehearsal evidence — p95 in envelope, violations at zero, success rate above floor.
- Sustained failure demotes automatically. Routines can be fired. (History is retained forever. Being fired is an event; being forgotten is not an option.)

---

**What "evidence" means in exact terms** → [proving.md](proving.md)
