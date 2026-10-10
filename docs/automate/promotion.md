# Promotion

Promotion moves a routine or API verb up the trust ladder — draft, reviewed, pinned — on recorded evidence. Confidence, seniority, and urgency play no part. The ladder climbs one rung at a time, and every crossing leaves an audit event.

Trust concepts for human readers live in [The Trust Engine](../understand/trust-engine.md). This page is the operational mechanics.

---

## The rungs in brief

| Rung | Meaning | Headline bounds |
|---|---|---|
| **draft** | Unproven exploratory state | No secret reads, sandboxed egress only, full payload audit |
| **reviewed** | Proven in simulation, signed off | Bulk operations unlocked, promoted-by identity recorded |
| **pinned** | Hardened production baseline | Tier 1 host required, unattended schedules permitted, summary audit |

Imported routines and world templates enter at draft with zero promotional credit. Blueprints confer nothing; evidence confers everything.

---

## Draft → reviewed: the auto-promotion conjunction

Auto-promotion evaluates `routine_stats` and the audit mirror against six criteria. Every criterion passes, or the candidate routes to the human queue — a single failure blocks the conjunction.

| Criterion | Threshold |
|---|---|
| Invariant suite | Passed in full (boundary and idempotency assertions) |
| Reliability | `success_rate >= 0.95` |
| Declaration match | Executed leaves a strict subset of the declared manifest; zero undeclared leaves |
| Policy compliance | Policy denials: exactly 0 |
| Runtime stability | Fingerprint drift events: exactly 0 |
| Latency | `p95_duration <= 0.70` of the declared maximum duration |

```bash
capcli routine ship <name> reviewed --queue
capcli routine pending
```

Queue age carries an SLA. A breached queue age surfaces as a `promotion.sla_breached` alarm from `sys doctor`. A human veto returns a candidate to draft at any point via rollback to draft trust.

Simulation proof precedes this gate: a 100% replay invariant pass with fuzzing in sim, plus a simulation success rate of at least 0.90 at the ship gate itself. Synthetic fixtures never substitute for sampled historical parameters in ship evidence.

---

## Reviewed → pinned: canary and contract proof

Pinning adds two evidence layers on top of the conjunction:

1. **The canary window.** Promotion opens a 1-hour automated telemetry window. Anomaly spikes or policy denials inside the window trigger an autonomous circuit-breaker rollback to draft; a clean window completes the pin.
2. **Live contract proof for API verbs.** External verbs validate responses against the upstream OpenAPI JSON Schema, with safe idempotent routes verified through read-only shadow canarying. Call-count graduation plays no part: unvalidated verbs stay at draft regardless of volume.

Pinned execution carries host physics. Tier 2 hosts — macOS, Windows, Termux — cap at reviewed, and invoking a pinned routine on Tier 2 is refused. Unattended pinned schedules run under a dedicated server daemon, never from a local workstation.

---

## Demotion: the fast direction

Movement down the ladder meets no gate resistance:

- **Spec drift.** An upstream provider `spec_hash` change or a breaking contract change demotes pinned capabilities to draft immediately.
- **Circuit demotion.** A sustained routine failure rate demotes to draft automatically.
- **Manual veto.** A human rollback to draft executes without the promotion conjunction.

Demotion preserves provenance. Version hashes, manifest hashes, and the causal chain behind every crossing remain inspectable after any demotion.

---

## Composition floors during promotion

Promotion evaluates the routine as a graph, not a file. Cross-agent callees hold trust at or above reviewed. A pinned caller composes pinned callees only; a reviewed caller composes reviewed or pinned. Draft routines never appear as dependencies, and a candidate with a draft callee waits until the callee promotes first.

---

## Promotion checklist

```
prove in sim ──► ship --queue ──► conjunction metrics ──► human queue or auto-promote
                                                          │
                              pinned: + 1-hour canary + contract proof (API verbs)
                                                          │
                                          demotion watches: spec drift, failure circuit
```

---

**Where routines come from:** → [Repetition](repetition.md) · [Codification](../agents/codification.md)
**Trust explained for humans:** → [The Trust Engine](../understand/trust-engine.md)
