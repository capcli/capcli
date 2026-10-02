# Rehearsal

A prove pass means nothing if the world it ran in doesn't resemble yours.

Most staging environments are a flattering portrait painted by someone who left the company. Capcli's `sim` world is not that. It's a physical fork of reality with the teeth removed: separate database, separate quotas, masked data, and API calls that route to fixtures instead of vendors.

You build in `dev`. You rehearse in `sim`. Only proven code earns `prod`. Same code, three worlds, zero free lunches.

---

## Forking reality, safely

Seed the simulator from production:

```bash
$ capcli env new sim --seed prod
```

```
[sim:tier_1]  ✓  environment ready

  env:      sim
  seeded:   prod (format-preserving masks applied)
```

Wait — seeded from prod? With real customer data in it? No. And not black bars either.

---

## The masking law: FPA

Naive tools anonymize by destruction — `████████` everywhere, and then your validation logic crashes because that's not a valid email. Capcli uses **Format-Preserving Anonymization (FPA)** instead:

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

The mask keeps the *shape* of the truth. Fake emails pass RFC validation. Fake cards pass Luhn. Fake phone numbers pass E.164. Columns tagged `mask: true` or `sens: true` in `schema.yaml` scramble automatically on fork — enforced, always, no opt-out.

Your routine tests its real validation logic against prod-shaped data, having seen zero bytes of human PII.

---

## The wire never leaves the building

Outbound API calls in `sim` don't go to Stripe, Twilio, or GitHub. They route to sandbox fixtures declared in `apis/<provider>.sim.yaml` — same verbs, same shapes, none of the consequences:

- **Base URLs rewritten** to test endpoints.
- **Quotas isolated** — `sim` keeps its own `_api_quota` bucket. Burning five hundred simulated requests never drains a production rate limit.
- **Notifications muted** — `ping.notify` traffic dumps into the simulation sink. Nobody's CEO gets a 02:00 test ping.

And a verb declared `sim_mode: prod-only` — buying a non-refundable shipping label, say — is denied outright in `sim`, `exit 2` (`policy.authorizer.sim_denial`), before bytecode evaluates. You cannot fire a live gun in the flight simulator.

---

## Time-travel: replay real history

Unit tests use inputs you imagined. Replays use inputs your customers actually generated.

```bash
$ capcli sys audit replay --from prod --since 7d --dry-run
```

```
[sim:tier_1]  Replaying 842 historical audit events against sim...

  replayed:   842 events
  mutations:  312 db writes executed deterministically
  egress:     530 api calls trapped by mock fixtures
  denials:    0 policy violations
  diff:       0 unexpected state divergences
```

A week of real traffic — every weird order, every retry, every edge case your imagination didn't budget for — run against your new code in a world that can't hurt anyone.

### The replay laws

1. **Database writes are re-executed.** State mutates deterministically inside the isolated `sim` workspace.
2. **External HTTP is never auto-replayed.** Local SQLite is physics; re-charging five hundred historical credit cards is a felony. Egress replays only by explicit, manual decision.

---

## Keep the simulator honest

`sim` drifts stale as `prod` moves on. Let it sit too long — past about two weeks without a re-seed — and the kernel starts nagging that your rehearsal data no longer resembles reality.

A rehearsal against stale data is just a more elaborate way of lying to yourself. `capcli env use sim`, re-seed, re-prove. Cheap. Boring. Correct.

---

## The One Rule

**Rehearse against a world that can't hurt anybody.**

If the rehearsal world lies, every proof it produces lies with it.

---

**The prove numbers, decoded — and the promotion math they feed:** → [proving.md](proving.md)

**The three-world model in full:** → [understand/environments.md](../understand/environments.md)

**Replay, tail, and trace contracts:** → [reference/commands/sys.md](../reference/commands/sys.md)
