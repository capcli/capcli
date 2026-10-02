# Environments: Dev, Sim, & Prod

Most companies have a "staging environment" that is an absolute lie: broken seed data from 2022, unconfigured API keys, zero real traffic. Developers test there, declare victory, push to production, and immediately trigger an incident — because staging didn't look like reality at all.

In Capcli, **environments are isolated physical worlds**. They enforce separate databases, distinct rate-limit partitions, independent Git worktrees, and data-masking rules that keep you from accidentally emailing 10,000 real customers during a test run.

---

## 1. The Three Worlds

Capcli organizes execution along two orthogonal axes. The **trust axis** bounds *capabilities* (`draft` → `reviewed` → `pinned`, see [trust-engine.md](trust-engine.md)); the **environment axis** bounds *state and infrastructure*:

```
┌────────────────────────────────────────────────────────────────────────┐
│  DEV WORLD (envs/dev/)                                                 │
│  Cheap to break: draft routines run freely, bulk checks relaxed.       │
│  Database: local scratch workspace.db.                                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  SIM WORLD (envs/sim/)                                                 │
│  The Flight Simulator: rehearsals against prod-shaped masked data.     │
│  Outbound APIs route to sandbox fixtures. Prod-only verbs denied.      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  PROD WORLD (envs/prod/)                                              │
│  The Live Fire Zone: draft writes physically denied. Tier 1 Linux only.│
│  Headless crons require Pinned trust. 2-key destruction safety.        │
└────────────────────────────────────────────────────────────────────────┘
```

A workspace holds at most 5 concurrent environments: `dev`, `sim`, `prod`, plus two custom experiment branches.

---

## 2. Dev: Cheap to Break

In `dev`, the kernel relaxes just enough to let you build fast:

* **Draft writes permitted:** newly created routines can mutate local tables.
* **Seeding relaxation:** the dev overlay lifts the draft row ceiling to 100 (sim stays at 10; prod denies draft writes outright) so you can seed tables without fighting the authorizer — [figures](../reference/limits.md#database-ceilings).
* **Waived pre-counts:** no `capcli sql --count` before every bulk update (dev and sim both waive it).
* **Permissive engines:** TypeScript (Bun/Node), Python, or JavaScript.

If your agent completely ruins `envs/dev/workspace.db`, nobody cares. You delete it, run `capcli env new dev --seed prod`, and you're back in business.

---

## 3. Sim: The Flight Simulator

Before any routine is promoted to reviewed or touches live production state, it must survive rehearsal in **`sim`**. The kernel runs a simulation overlay:

* **Base URL rewriting:** outbound API calls to Stripe, Twilio, or GitHub are swapped to test endpoints via `apis/<provider>.sim.yaml`.
* **Isolated quotas:** `sim` maintains an entirely separate `_api_quota` partition. Burning 500 requests in simulation never drains a production rate bucket.
* **Muted notifications:** Slack alerts and emails routed to `ping notify` are intercepted and dumped into `#sim-notifications`. Your CEO won't receive test pings at 02:00.
* **Prod-only hard walls:** an API verb declared `sim_mode: prod-only` (like buying a non-refundable shipping label) throws [exit 2](../reference/exit-codes.md#exit-2) (`policy.authorizer.sim_denial`) in sim. You cannot accidentally fire a live gun in the flight simulator.

---

<a id="fpa"></a>

## 4. The Data Masking Law: Format-Preserving Anonymization (FPA)

When you seed `sim` from `prod` (`capcli env new sim --seed prod`), traditional tools do one of two stupid things:

1. **They copy real PII.** Your agent now plays with live credit card numbers, home addresses, and customer emails. One typo in a script and you've sent test spam to 50,000 real people.
2. **They replace everything with black bars.** Fields become `"REDACTED"` or `"████████"` — and your code immediately crashes, because `"████████"` is not a valid email, fails regex validation, and breaks SQLite constraints.

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

* Sensitive columns tagged `mask=true` or `sens: true` in `schema.yaml` are automatically scrambled during the fork — enforcement is structural, not optional.
* Data types remain valid: fake emails pass RFC validation, fake phone numbers pass E.164, fake cards pass Luhn.
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

### The Replay Laws

1. **Database writes are re-executed.** State mutates deterministically inside the isolated `sim/workspace.db`.
2. **External HTTP calls are locked.** Capcli never auto-replays external API calls (`replay: manual`). Replaying history against local SQLite is physics; replaying 500 historical Stripe charges would send you to federal prison.

---

## 6. Prod: The 2-Key Submarine Rule

In `prod`, the playground is closed:

* **Draft writes are physically banned:** running an unproven routine in prod throws [exit 2](../reference/exit-codes.md#exit-2) before bytecode even evaluates.
* **Tier 1 host required:** pinned production execution needs hardware containment — unprivileged namespaces plus syscall trapping ([sandboxing.md#tiers](sandboxing.md#tiers)).
* **Tightened throttles:** writes per minute sit at the strict prod ceiling while sim iterates at its fast-rehearsal ceiling — [figures](../reference/limits.md#rate-governance).

### How to Delete an Environment Without Getting Fired

In sloppy CLI tools, an exhausted developer runs `tool destroy --force prod` and wipes out the company. In Capcli, deleting a production environment requires **two distinct confirmation keys inserted simultaneously**, like launching a nuclear missile from a submarine ([full syntax](../reference/cli/env.md)):

```bash
$ capcli env remove prod --confirm-backup --confirm-prod
```

```text
[prod:tier_1]  ✓  environment removed

  target:      envs/prod/
  backup_ref:  snap_prod_pre_destroy_99f1 (verified in object store)
  git_branch:  archived to refs/archive/prod-2026-10-01
```

* Forget `--confirm-backup`? Refused ([exit 3](../reference/exit-codes.md#exit-3)). You must prove a verified backup snapshot exists offsite.
* Forget `--confirm-prod`? Refused (`exit 3`). You must explicitly acknowledge you are destroying production.
* Try to pass `-f` or `--force`? **Syntax error.** Brute-force flags are permanently banned from the grammar.

---

**See how secrets stay safe across environments:** → [identity.md](identity.md)
**Switch environments right now:** → `capcli env use sim` ([reference/cli/env.md](../reference/cli/env.md))
