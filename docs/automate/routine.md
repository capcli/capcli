# Command: `capcli routine`

This is where sloppy ad-hoc bash scripts go to become hardened, immortal civil servants.

A routine is a versioned, sandboxed, multi-step script (Python 1st-class, JavaScript, or TypeScript). It bundles database queries, external API calls, and business logic into an atomic unit with cryptographically locked manifests.

```bash
capcli routine <verb> [args] [--flags]
```

---

## Subcommands

| Verb | Syntax | Description |
|---|---|---|
| **`prove`** | `capcli routine prove <name> [-p k=v] [--env sim]` | Runs synthetic replay tests against masked simulation data. |
| **`ship`** | `capcli routine ship <name> <reviewed\|pinned> [--env X] [--reason "..."] [--queue]` | Submits candidate for promotion up the trust ladder. |
| **`sweep`** | `capcli routine sweep [--since 30d]` | Maintenance pass over the routine registry. |
| **`stats`** | `capcli routine stats <name> [--deep]` | Displays p50/p95 latency, run counts, and historical success rates. |
| **`rollback`**| `capcli routine rollback <name> [--to-version <v>]` | Rewinds capability pointer to a prior verified version hash. |
| **`retire`** | `capcli routine retire <name> [--reason "..."]` | Decommissions a routine without destroying historical provenance. |

---

## Authoring a routine

A routine enters the registry by one of two routes:

- **Direct write.** Author the file straight into `routines/<name>.py`. The intake shape gate measures it before registration.
- **Blueprint scaffold.** Pre-flight the blueprint with `capcli inspect tpl://routine/<name>`, then stamp a draft routine with `capcli template scaffold tpl://routine/<name> <target> [-p k=v]`.

Either route registers the result at draft trust, version 1, with zero promotional credit. The full template lifecycle, including registry-sourced blueprints, lives in [World](../understand/world.md#templates-and-the-registry).

## The Shape Police (Governance Bounds)

Your LLM loves writing 600-line monolithic scripts full of custom utility classes. 

**Capcli hates that.** 

Before a routine can be registered, proved, or shipped, the Rust kernel measures its physical dimensions. If it violates any of these, intake refuses it (`exit 3`):

* **Max 2,000 Tokens:** Keeps file sizes small so inspecting them doesn't bankrupt your LLM context window. Lines of code are unrestricted — whitespace and comments don't count.
* **Max 8 Parameters (`Param`):** If a routine needs 14 arguments, your design is bad and you should feel bad. Use an object or break up the task.
* **Max 3 Routine Imports:** Routines can import other routines, but composition depth is capped. No 12-layer lasagna code.
* **Mandatory Description (Min 5 words, max 60 tokens):** If an agent can’t search for it, it doesn’t ship. Unsearchable code is dead code.

---

## 1. Proving It: `routine prove`

You wrote `routines/refund_order.py`. You think it works. 

The kernel doesn't care what you think. It demands proof in simulation:

```bash
$ capcli routine prove refund_order -p order_id=ORD-9912 -p amount=50 \
    --env sim
```

```text
[sim:tier_1]  refund_order@1  ✓  prove passed (412ms)

  manifest_declared: db.query → api.call(stripe.refund) → db.execute
  manifest_executed: db.query → api.call(stripe.refund) → db.execute
  match:             100% subset
  policy_denials:    0
  drift_events:      0
  audit:             op_992a → op_992b → op_992c
```

### What just happened:
1. The script was locked inside a `bwrap` container (tmpfs scratch space, no host network).
2. It executed against masked data in `sim` (sensitive emails were scrambled to `anon_*@sim.local`).
3. Outbound HTTP calls routed to simulation sandbox fixtures (`apis/stripe.sim.yaml`).
4. The kernel compared what the code **declared** it would do against the **actual leaf events** emitted to the audit trail. If it touched an undeclared table, it fails.

---

## 2. Climbing the Ladder: `routine ship`

Code doesn't get to touch production just because a developer typed `"please"`. 

To elevate a routine from `draft` to `reviewed` or `pinned`, you run `ship`:

```bash
$ capcli routine ship refund_order reviewed \
    --reason "passed quarterly compliance rehearsal"
```

### The 5-Point Autonomous Auto-Promotion Math
If you configure automated shipping, the kernel checks cold, hard telemetry in `routine_stats`. **Every single metric must pass:**

| Metric | Threshold | What happens if you get 94.9%? |
|---|---|---|
| **Invariant Suite** | 100% pass | Denied. Goes to human review queue. |
| **Historical Success Rate** | $\ge 95.0\%$ | Denied. |
| **Manifest Match** | 100% subset | Denied (ran an undeclared primitive). |
| **Policy Denials** | **Exactly 0** | Denied (hit an AST or authorizer wall). |
| **Fingerprint Drift** | **Exactly 0** | Denied (diverged from manifest). |
| **Latency Ceiling** | $\text{p95} \le 70\%$ of timeout | Denied (too slow in simulation). |

Fail even one metric? The promotion is blocked, and the routine is thrown into the human approval queue (`capcli routine pending`).

---

## 3. Deleting Without Deleting: `routine retire`

In traditional engineering, someone runs `git rm routines/old_script.py`, commits it, and breaks three cron jobs and two API endpoints.

In Capcli, **you never delete code.** 

```bash
$ capcli routine retire legacy_billing -m "superseded by billing_v2"
```

```text
[dev:tier_1]  ✓  retired

  capability:  cap://legacy_billing@8
  status:      retired
  dependents:  0 active dependencies verified
  audit:       op_11d4
```

### Retirement Invariants:
1. **Dependency Protection:** If another routine or cron schedule still calls `cap://legacy_billing@8`, the authorizer **refuses to retire it (`exit 2`)**. You must detach the consumers first.
2. **Permanent Provenance:** The script is marked `retired` in the registry and becomes uncallable. But its historical version hashes (`code_hash`, `manifest_hash`) remain in the causal DAG forever. Historical replays will always work.

---

## 4. The Time Machine: `routine rollback`

Did an updated routine ship with a subtle edge-case bug? Don't push a frantic hotfix commit at midnight:

```bash
$ capcli routine rollback dispatch_order --to-version 3 \
    -m "v4 fails on international postal codes"
```

```text
[prod:tier_1]  ✓  rolled back

  pointer:     cap://dispatch_order
  active:      version 3 (hash: sha256:88a1b...)
  superseded:  version 4 (deactivated)
  audit:       op_77c2
```

* One command restores the pointer.
* **Max Rollback Depth:** 5 versions.
* **Max Versions Kept:** 25 historical versions (older versions are pruned from disk while audit hashes stay pinned).

---

## Banned Operations

* **There is no `routine new` verb, and no `template list`, `template inspect`, `template validate`, or `template apply` verb.** The parser rejects each at intake. Authoring runs through direct write or `capcli template scaffold`; blueprint pre-flight runs through `capcli inspect tpl://`; bundle lint runs through `capcli rule validate [target]`.
* **`--force` is banned:** Passing `--force` to `routine ship` is an immediate syntax error.
* **Direct filesystem tampering:** Editing a versioned file directly in `routines/` without bumping the version or running through intake triggers an instant lockfile mismatch (`exit 3`).
* **Self-Promotion:** A running routine cannot invoke `routine ship` on itself. Trust escalation requires human or CI principal authority.
