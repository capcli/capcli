# Command: `capcli api`

Manages external third-party API catalogs, OpenAPI synchronization, and verb lifecycles.

```bash
capcli api <verb> [args] [--flags]
```

---

## Subcommands

| Verb | Syntax | Description |
|---|---|---|
| **`sync`** | `capcli api sync <provider> <url> [--interval 7d] [--dry-run]` | Imports and compiles OpenAPI specs into `apis/<provider>.yaml`. |
| **`diff`** | `capcli api diff <provider>` | Diffs compiled spec against upstream spec hash (`spec_hash`). |
| **`catalog`**| `capcli api catalog <provider> [--state <state>]` | Lists verbs filtered by state (`dormant`, `active`, `deprecated`, `retired`). |
| **`activate`**| `capcli api activate <provider.verb> -m "<why>"` | Moves verb from `dormant` to `active` at `draft` trust. |
| **`prove`** | `capcli api prove <provider.verb> [-p k=v] [--env sim]` | Dry-runs against simulated mocks or schema fixtures. |
| **`ship`** | `capcli api ship <provider.verb> <reviewed\|pinned> [--reason "<why>"]` | Promotes an API verb up the trust ladder. |
| **`stats`** | `capcli api stats <provider> [--deep] [--summary]` | Displays provider token-bucket quotas and latency metrics. |
| **`deactivate`**| `capcli api deactivate <provider.verb> [--reason "<why>"]` | Reverts an active verb back to dormant. |
| **`retire`** | `capcli api retire <provider.verb> [--reason "<why>"]` | Permanently disables verb while preserving provenance. |
| **`rollback`**| `capcli api rollback <provider.verb> [version]` | Restores prior verb configuration schema. |

---

## In Practice

The catalog, unfiltered — state and trust rung in one glance:

```bash
$ capcli api catalog stripe
```

```text
[dev:tier_1]  stripe  2 verbs

  cap://stripe.refund_charge           active    reviewed   "Issue partial or full Stripe refund"
  cap://stripe.payment_intents.create  dormant   —          "Creates PaymentIntent for card/invoice capture"
```

One active, one dormant. Dormant verbs cost your context window nothing and are physically uncallable — wake one with `api activate <provider.verb> -m "<why>"` and it lands at `draft` trust with training wheels attached. Add `--state active` (or `dormant`, `deprecated`, `retired`) to filter to a single lifecycle state.

---

## Invariants & Rules

* **Spec Quarantine:** The harness is banned from reading raw OpenAPI files. Specs >10MB auto-prune unreferenced paths during compilation.
* **Verb Lifecycle:** `dormant` ➔ `active` ➔ `deprecated` ➔ `retired`. Dormant verbs never decay or expire.
* **Training Wheels:** Newly activated unmocked verbs enforce 3 contract replay passes. Auto-graduates on Call 4.
* **Simulation Modes:**
  * `sandbox`: Routes to provider sandbox URL via `apis/<provider>.sim.yaml`.
  * `mock`: Returns canned fixture from `apis/<provider>.mock.yaml`.
  * `dry-run`: Validates payload schema and returns `{ "simulated": true }`.
  * `prod-only`: Throws `exit 2` if called in `dev` or `sim`.
* **Ceilings:** Max 10 providers; max 500 verbs/provider; max 50 active verbs/provider; max 10 activations/hour.

---

## Banned Verbs
* `capcli api call` ➔ **Banned.** Use `capcli run` or `ctx.api.call` inside guest code.
* `capcli api import --pick` ➔ **Banned.** Verbs are synced in full to preserve schema integrity.
