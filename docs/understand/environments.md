# Environments: Dev, Sim, & Prod

Most companies have a "staging environment" that is an absolute lie.

Staging has broken seed data from 2022, unconfigured API keys, and zero real traffic. Developers test in staging, declare victory, push to production, and immediately trigger an incident because staging didn't look like reality at all.

In Capcli, **environments are isolated physical worlds**. 

They enforce separate databases, distinct rate-limit partitions, independent Git worktrees, and data-masking rules that keep you from accidentally emailing 10,000 real customers during a test run.

---

## 1. The Three Worlds

Capcli organizes execution along two orthogonal axes:
* **The Trust Axis** bounds *capabilities* (`draft` ➔ `reviewed` ➔ `pinned`).
* **The Environment Axis** bounds *state and infrastructure* (`dev` ➔ `sim` ➔ `prod`).

```
┌────────────────────────────────────────────────────────────────────────┐
│  DEV WORLD (envs/dev/)                                                 │
│  The Kindergarten: Draft routines run freely. Bulk checks relaxed.     │
│  Database: Local scratch workspace.db.                                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  SIM WORLD (envs/sim/)                                                 │
│  The Flight Simulator: Rehearsals against prod-shaped masked data.     │
│  Outbound APIs route to sandbox fixtures. Prod-only verbs denied.      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  PROD WORLD (envs/prod/)                                               │
│  The Live Fire Zone: Draft writes physically denied. Tier 1 Linux only.│
│  Headless crons require Pinned trust. 2-key destruction safety.        │
└────────────────────────────────────────────────────────────────────────┘
```

You can have a maximum of **5 concurrent environments** per workspace (`dev`, `sim`, `prod`, plus 2 custom experiment branches).

---

## 2. Dev: The Toddler Playpen

In `dev`, the kernel lets down its guard just enough so you can build things without crying:
* **Draft writes permitted:** Newly created routines can mutate local tables.
* **Seeding relaxation:** Dev allows up to 100 affected rows for draft mutations (compared to 10 in prod) so you can seed tables without hitting an AST wall.
* **Waived pre-counts:** You don't have to run `capcli sql --count` before every bulk update.
* **Permissive engines:** You can run Python (1st-class), JavaScript, or TypeScript.

If your agent completely ruins `envs/dev/workspace.db`, nobody cares. You delete it, run `capcli env new dev --seed prod`, and you're back in business.

---

## 3. Sim: The Flight Simulator

Before any routine is promoted to `reviewed` or touches live production state, it must survive rehearsal in **`sim`**.

In `sim`, the kernel runs a simulation overlay:
* **Base URL Rewriting:** Outbound API calls to Stripe, Twilio, or GitHub are swapped to test endpoints via `apis/<provider>.sim.yaml`.
* **Isolated Quotas:** Sim maintains an entirely separate `_api_quota` table. Burning 500 requests in simulation never drains your production rate buckets.
* **Muted Notifications:** Slack alerts and emails routed to `ping.notify` are intercepted and dumped into `#sim-notifications`. Your CEO won't receive test pings at 02:00 AM.
* **Prod-Only Hard Walls:** If an API verb is declared `sim_mode: prod-only` (like buying a non-refundable shipping label), running it in `sim` throws **`exit 2` (`policy.authorizer.sim_denial`)**. You cannot accidentally fire a live gun in the flight simulator.

---

## 4. The Data Masking Law: Format-Preserving Anonymization (FPA)

When you seed `sim` with real data from `prod` (`capcli env new sim --seed prod`), traditional tools do one of two stupid things:
1. **They copy real PII:** Your agent is now playing with live credit card numbers, home addresses, and customer emails in staging. One typo in a script, and you just sent test spam to 50,000 real people.
2. **They replace everything with black bars:** They overwrite fields with `"REDACTED"` or `"████████"`. Then your code immediately crashes because `"████████"` is not a valid email, fails regex validation, and breaks SQLite constraints.

Capcli uses **Format-Preserving Anonymization (FPA)**:

```text
PROD ROW:
  name:     "Alice O'Connor"
  email:    "alice.oconnor@gmail.com"
  card_bin: "411111"

FORKED SIM ROW (FPA):
  name:     "Anon User 8812"
  email:    "anon_8812@sim.local"
  card_bin: "400000"
```

* Sensitive columns tagged `mask=true` or `sens: true` in `schema.yaml` are automatically scrambled during the fork.
* Data types remain valid: fake emails pass RFC validation; fake phone numbers pass E.164 formats; fake cards pass Luhn checks.
* The agent tests real validation logic without ever seeing a single byte of human PII.

---

## 5. Historical Replay: Time-Traveling Traffic

You wrote a new order-dispatch routine (`cap://dispatch_order@5`). It passed unit tests. But will it hold up against the chaos of real customer behavior?

Don't wait for production bugs. **Replay real history against it:**

```bash
$ capcli sys audit replay --from prod --since 7d --dry-run
```

```text
[sim:tier_1]  Replaying 842 historical audit events against sim...

  replayed:   842 events
  mutations:  312 db writes executed deterministically
  egress:     530 api calls trapped by mock fixtures
  denials:    0 policy violations
  diff:       0 unexpected state divergences
```

### The Replay Laws:
1. **Database writes are re-executed:** State mutates deterministically inside the isolated `sim/workspace.db`.
2. **External HTTP calls are locked:** Capcli **never** auto-replays external HTTP calls (`replay: manual`). Replaying history against local SQLite is physics; replaying 500 historical Stripe credit card charges would send you to federal prison.

---

## 6. Prod: The 2-Key Submarine Rule

In `prod`, the playground is closed:
* **Draft writes are physically banned:** Running an unproven routine in prod throws `exit 2` before bytecode even evaluates.
* **Tier 1 Host Required:** You cannot run pinned routines on macOS or Windows (Tier 2). Pinned production execution strictly requires hardware-contained Linux namespaces (`bwrap` + `seccomp-bpf`).
* **Tightened Throttles:** Writes are capped at 60 writes/minute (compared to 1,000 in sim).

### How to Delete an Environment Without Getting Fired
In sloppy CLI tools, an exhausted developer accidentally runs `tool destroy --force prod` and wipes out the company.

In Capcli, deleting an environment requires **two distinct confirmation keys inserted simultaneously**, like launching a nuclear missile from a submarine:

```bash
$ capcli env remove prod --confirm-backup --confirm-prod
```

```text
[prod:tier_1]  ✓  environment removed

  target:      envs/prod/
  backup_ref:  snap_prod_pre_destroy_99f1 (verified in object store)
  git_branch:  archived to refs/archive/prod-2026-10-01
```

* Forget `--confirm-backup`? Refused (`exit 3`). You must prove a verified backup snapshot exists offsite.
* Forget `--confirm-prod`? Refused (`exit 3`). You must explicitly acknowledge you are destroying production.
* Try to pass `-f` or `--force`? **Syntax error.** Brute-force flags are permanently banned.

---

## The One Rule

**Data belongs to environments. Capabilities belong to trust.**

You build in `dev`, rehearse against masked history in `sim`, and only when code has proven its invariants does it earn the right to touch `prod`.

---

**See how secrets are safely handled across environments:** → [identity.md](identity.md)  
**Switch environments right now:** → `capcli env use sim
