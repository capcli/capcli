---
id: doc://prompts/authoring/trust_floor#1
stem: authoring.trust_floor.denial.denied
bank: authoring
slug: trust_floor
version: 1
trust: draft
sections:
  stage_1_inspect: 80
  stage_2_raise_or_widen: 100
  stage_3_rehearse: 60
slice_max_tokens: 500
docs:
  - doc://automate/promotion
  - doc://reference/errors
status: served
---

# ⚡ TRUST FLOOR REMEDIATION PROTOCOL
The kernel refused the call because a trust floor was breached.
Two floors exist: platform tier mandate (E045) and composition floor (E046).

## section:stage_1_inspect
Inspect both sides of the call:
```bash
capcli inspect cap://<routine_name>
capcli inspect plugin://<plugin_id>
```

Read the trust rung on the caller and callee.
Read the environment and platform_tier on the active session.

section:stage_2_raise_or_widen

Choose one path:

· Callee below caller — see governance.md#Promotion-gates.
· Caller below callee — you cannot lower a callee; fork the caller.
· Prod on tier 2 — see sandbox.md#Platform-tiers.
  Skipping a rung is not lawful.

section:stage_3_rehearse

Rehearse in the target environment after the fix:

```bash
capcli routine prove <routine_name> --environment sim
```

Then re-dispatch the original call.

