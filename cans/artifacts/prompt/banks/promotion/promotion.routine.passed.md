---
id: prompt://promotion/routine_passed@1
stem: promotion.routine.passed
bank: promotion
slug: routine_passed
version: 1
trust: draft
vars:
  - name: env
    type: string
    source: kernel.env
sections:
  stage_1_enqueue: 60
  stage_2_canary: 70
  stage_3_pin: 100
slice_max_tokens: 500
docs:
  - doc://automate/promotion
status: served
---

# ⚡ ROUTINE TRUST PROMOTION PROTOCOL
Routine simulation proof succeeded with zero drift events and zero policy violations.
Promote code safely across the trust ladder (`draft -> reviewed -> pinned`).

## section:stage_1_enqueue
Do not promote draft routines directly to pinned production execution.
Enqueue the routine for reviewed trust:
```bash
capcli routine ship <routine_name> reviewed --queue
```

## section:stage_2_canary
Monitor the routine through its 1-hour production canary observation window:
```bash
capcli routine stats <routine_name>
```
If errors spike, the autonomous circuit breaker rolls back active pointers to the previous version.

## section:stage_3_pin
If canary metrics meet the trust gates in cans/trust.md (success_rate >= 0.95, invariant suite passed, zero policy denials, zero fingerprint drift) across the 1-hour canary window, promote to pinned:
```bash
capcli routine ship <routine_name> pinned --reason "Canary passed: trust gates met"
```
*Note: Pinned execution requires Tier 1 hardened Linux namespaces.*
