# Command: `capcli api`

Manages external API catalogs, OpenAPI synchronization, and verb lifecycles.

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

## Live example: activation

```bash
$ capcli api activate stripe.refund_charge -m "allow support agent refunds"
```

```text
[dev:tier_1]  ✓  activated

  verb:            cap://stripe.refund_charge
  trust:           draft
  training_wheels: 3 calls remaining
  sim_mode:        sandbox
```

Calls 1–3 replay the recorded contract in simulation; call 4 runs under standard governance. The vendor's sandbox takes the risk, not your customers.

## Missing secret → cockpit, not chat

```bash
$ capcli run stripe.refund_charge -p charge_id=ch_3M9x -p amount=2500 \
    -m "refund defective item"
```

```text
[dev:tier_1]  ✗  exit 3

  FAIL  policy.secrets.missing
        capability: cap://stripe.refund_charge
        secret_ref: vault://stripe_secret

        Credential 'stripe_secret' not found in vault.
        Direct CLI parameter injection is banned to prevent prompt leakage.

  state_modified: false
  layer: vault
  remedy: prompt human supervisor to inject credential via Cockpit (http://127.0.0.1:4040/vault)
```

The kernel refuses *and* tells your agent exactly which human sentence to say next. Remedies are scripts, not suggestions.

## Banned Verbs
* `capcli api call` ➔ **Banned.** Use `capcli run` or `ctx.api.call` inside guest code.
* `capcli api import --pick` ➔ **Banned.** Verbs are synced in full to preserve schema integrity.

---

**Narrative** → [../../use/call-apis.md](../../use/call-apis.md) · **Quota physics** → [../../understand/budgets.md](../../understand/budgets.md)
