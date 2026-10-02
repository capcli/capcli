# Command: capcli routine

The capability lifecycle — scaffold, prove, ship, watch, and eventually subtract. The workflow walkthrough lives in [routines.md](../../workflows/routines.md); this page is the verb surface.

```bash
capcli routine <verb> <name> [args] [--flags]
```

## Subcommands

| Verb | Syntax | Caller | Description |
|---|---|---|---|
| **new** | `capcli routine new <name> [--template <ptr\|path>]` | [both] | Optional scaffold. Direct writes to `routines/<name>.py` are the draft SSOT — creation itself is ungated. |
| **prove** | `capcli routine prove <name> [-p k=v] [--env sim]` | [both] | Static validation + simulated execution against real historical inputs. |
| **ship** | `capcli routine ship <name> <reviewed\|pinned> [--env X] [--reason "..."]` | [human] | Trust rung elevation; `--queue` batches candidates for human approval. |
| **sweep** | `capcli routine sweep [--since 30d]` | [harness] | Surfaces dead, failing, and duplicate routines for consolidation. |
| **stats** | `capcli routine stats <name> [--deep]` | [both] | Telemetry profile from `routine_stats`. |
| **rollback** | `capcli routine rollback <name> [version]` | [both] | Reinstates a prior version pointer — un-retires if needed. |
| **retire** | `capcli routine retire <name> [--reason]` | [both] | Makes the routine uncallable while preserving provenance. |

## Authoring

Routines are TypeScript or Python files in `routines/` — decorated with `@routine(name, trust, idempotent, description, limits)` and executed through the injected `ctx` contract. The kernel holds an authoring mutex per file: concurrent edits exit 2. Near-duplicates demand a `--reason` justification at draft time; the consolidation scan runs weekly on schedule ([limits](../limits.md#routine-shape)).

## Proving

`prove` runs at draft trust regardless of what the decorator declares. It checks shape, jail rules, parameter typing, policy reachability, and compares the runtime fingerprint against the declared manifest — skipped verbs report a fractional match. Shape violations (LOC, tokens, params, imports) are [governed caps](../limits.md#routine-shape).

## Shipping

The ship gate reads `routine_stats` and the audit mirror directly — it verifies the six-metric conjunction (invariant suite, success rate, manifest subset match, zero policy denials, zero fingerprint drift, latency p95 ≤ 70% of declared max) described in [trust-engine.md](../../concepts/trust-engine.md). Qualifying candidates auto-promote with a one-hour canary veto window; everything else routes to the human queue (`capcli routine ship <name> reviewed --queue`, inspected via `capcli routine pending`). Production promotion additionally requires a merged branch and sim proof.

## Subtraction

Nothing is deleted — retirement keeps the provenance graph navigable. Decay is scheduled: unused routines become retire candidates, failing routines get demoted, and rollback depth is capped ([limits](../limits.md#routine-shape)). Retiring a routine auto-disables its bound schedules, loudly.

## Invariants

* Draft → reviewed → pinned is a monotonic climb; elevation skips are denied ([trust ladder](../../concepts/trust-engine.md)).
* Code edits force a version bump — silent edits are banned; versions and rollback depth are [capped](../limits.md#routine-shape).
* Pinned execution requires a [Tier 1](../../concepts/sandboxing.md#tiers) host.
* Execution ceilings (ops, duration, result tokens) are declared per routine and always stay under the [governance ceilings](../limits.md#execution-budget).
