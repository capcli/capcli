# Routines

This is where sloppy ad-hoc bash scripts go to become hardened, immortal civil servants.

A routine is a versioned, sandboxed, multi-step script (TypeScript or Python) that bundles database queries, external API calls, and business logic into an atomic unit with a cryptographically locked manifest.

| Verb | What it does |
|---|---|
| `new` | Scaffolds a compliant starter in `routines/<name>.ts` (optional) |
| `prove` | Runs synthetic replay tests against masked sim data |
| `ship` | Submits the candidate for promotion up the trust ladder |
| `stats` | p50/p95 latency, run counts, historical success rates |
| `rollback` | Rewinds the capability pointer to a prior verified version |
| `sweep` | Scans for dead, failing, or duplicate routine candidates |
| `retire` | Decommissions without destroying provenance |

(Exact syntax for every verb: [reference/cli/routine.md](../reference/cli/routine.md).)

---

## Authoring

Write the file. That's it — the filesystem is the draft SSOT, and the two notations mean two different things:

```
routines/refund_order.ts     ← on disk in development: file notation
cap://refund_order@1         ← registered in the kernel: URP, version pinned
```

Direct writes to `routines/` are ungated; `capcli routine new` just scaffolds a starter if you want one. Every routine declares `name`, `trust`, `limits`, and a description of at least 5 words — if an agent can't search for it, it doesn't ship. Unsearchable code is dead code.

---

## The shape police

Your LLM loves writing 600-line monolithic scripts full of custom utility classes. The kernel disagrees. Before a routine can be registered, proved, or shipped, its physical dimensions are measured — **150 lines, 2,000 tokens, 8 params, 3 routine imports.** Violate any one and it dies at the intake gate ([`exit 2`](../reference/exit-codes.md#exit-2)), with the measured value in the denial. The full table: [routine shape limits](../reference/limits.md#routine-shape).

---

## Prove it

You wrote `routines/refund_order.ts`. You think it works. The kernel doesn't care what you think — it demands proof in simulation:

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
```

What just happened: the script ran locked in a sandbox against [masked sim data](../concepts/environments.md), outbound HTTP routed to fixtures, and the kernel compared what the code **declared** it would do against the leaf events it **actually emitted**. Touch an undeclared table? Fail. ([Why manifests and fingerprints exist](../concepts/trust-engine.md).)

---

## Ship it

```bash
$ capcli routine ship refund_order reviewed \
    --reason "passed quarterly compliance rehearsal"
```

Code doesn't get to touch production because a developer typed "please." If you configure auto-shipping, the kernel checks cold telemetry and **every gate must pass**: invariant suite 100%, success rate ≥ 95%, manifest match 100% subset, zero policy denials, zero fingerprint drift, and p95 under 70% of the timeout ceiling. Fail even one metric and the promotion is blocked — it goes to the human approval queue instead. (Why promotion is evidence-based, not vibe-based: [the trust engine](../concepts/trust-engine.md).)

---

## The 1-hour canary window

Passed the math? Promoted to `reviewed`? You're on probation for 60 minutes. During the first hour of production traffic, the kernel watches error rates and latency. Policy denial, unexpected spike, or runtime crash — the autonomous circuit breaker fires, the promotion is instantly revoked, and the routine drops straight back to `draft`. You fix the bug, you rehearse again, reality remains intact. ([Canary veto theory](../concepts/trust-engine.md).)

---

## Invoking routines

From your terminal or your harness, anywhere, any time:

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

Three primitives fired. Under budget. Logged. If the routine mutates state, `-m` is required — the same intent law as SQL writes ([query-data.md](query-data.md)). Fat params? `-p data=@payload.json` reads the file; `@-` pulls from stdin. (Exact syntax: [reference/cli/run.md](../reference/cli/run.md).)

---

## Retire it

In traditional engineering, someone runs `git rm routines/old_script.py` and breaks three cron jobs. In Capcli you never delete code:

```bash
$ capcli routine retire legacy_billing -m "superseded by billing_v2"
```

```text
[dev:tier_1]  ✓  retired

  capability:  cap://legacy_billing@8
  status:      retired
  dependents:  0 active dependencies verified
```

Two invariants. First: if anything still calls `cap://legacy_billing@8`, the authorizer [refuses the retirement (`exit 2`)](../reference/exit-codes.md#exit-2) — detach the consumers first. Second: the retired version's hashes stay in the causal DAG forever. Historical replays always work. ([The memory spine](../concepts/memory-spine.md).)

---

## Roll it back

Did v4 ship with a subtle edge-case bug? Don't push a frantic hotfix at midnight:

```bash
$ capcli routine rollback dispatch_order --to-version 3 \
    -m "v4 fails on international postal codes"
```

```text
[prod:tier_1]  ✓  rolled back

  pointer:     cap://dispatch_order
  active:      version 3 (hash: sha256:88a1b...)
  superseded:  version 4 (deactivated)
```

One command restores the pointer. Rollback depth and version retention are governed — see [limits](../reference/limits.md).

---

## Banned operations

- **`--force` doesn't exist.** Passing it to `routine ship` is an immediate syntax error.
- **No silent edits** — touching a versioned file in `routines/` without a version bump trips the lockfile ([`exit 3`](../reference/exit-codes.md#exit-3)).
- **No self-promotion** — a running routine can't `ship` itself. Trust escalation needs a human or CI principal.
