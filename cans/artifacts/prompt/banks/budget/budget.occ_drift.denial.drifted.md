---
id: doc://prompts/budget/occ_drift#1
stem: budget.occ_drift.denial.drifted
bank: budget
slug: occ_drift
version: 1
trust: draft
sections:
  stage_1_fence: 80
  stage_2_reconcile: 100
  stage_3_abort_or_retry: 80
slice_max_tokens: 500
docs:
  - doc://reference/errors
status: served
---

# ⚡ OCC DRIFT REMEDIATION PROTOCOL
A suspended frame resumed and found its read set changed.
The kernel denied the write with E061_OCC_DRIFT.

## section:stage_1_fence
Inspect the suspended frame's state_fence:
```bash
capcli sys audit trace <op-id> --explain
```

state_fence lists rows read during Phase 1.
The denial cites the drifted row.

section:stage_2_reconcile

Compare the drifted row against fresh state:

```bash
capcli inspect db://<table>/<id>
```

Confirm the new value is what you want to write against.
If the drift changes the intent, abort the frame.

section:stage_3_abort_or_retry

Abort the drifted frame before re-running:

```bash
capcli run abort <frame_id>
```

Then re-dispatch fresh. The new run reads the reconciled state.
See governor.md#Suspension-registry.

