---
id: prompt://onboarding/human@1
stem: onboarding.human.success.stub
bank: onboarding
slug: human
version: 1
trust: draft
vars:
  - name: env
    type: string
    source: kernel.env
  - name: tier
    type: string
    source: kernel.tier
sections:
  stage_1_probe: 60
  stage_2_read: 50
  stage_3_denial: 70
  stage_4_write: 70
  stage_5_recovery: 60
slice_max_tokens: 500
docs:
  - doc://start
status: served
---

# ⚡ HUMAN OPERATOR ONBOARDING TOUR (S0–S10)
Welcome to Capcli. Execution physics are enforced at compile time in [{{env}}:{{tier}}].
Follow the 5-stage pedagogical path to understand deterministic boundaries.

## section:stage_1_probe
Run host readiness diagnostics:
```bash
capcli sys doctor
```
Locate registered capabilities dynamically:
```bash
capcli search "order"
capcli inspect cap://dispatch_order@1
```

## section:stage_2_read
Execute an AST-bounded read against the database:
```bash
capcli sql "SELECT * FROM orders LIMIT 5"
```
Reads do not mutate state (`state_modified: false`).

## section:stage_3_denial
Trigger a deliberate policy denial to observe compiler physics:
```bash
capcli sql "UPDATE orders SET status = 'shipped'"
```
Observe prepare-time interception (`exit 2`). AST blocks unbounded mutations.
Zero rows are touched.

## section:stage_4_write
Remediate the write using explicit WHERE bounds, LIMIT, and causal intent:
```bash
capcli sql "UPDATE orders SET status = 'shipped' WHERE id = 1 LIMIT 1" -m "Manual order dispatch"
```
Verify the commit in `_audit`.

## section:stage_5_recovery
Practice snapshot reversal and verify integrity:
```bash
capcli db snapshot
capcli db restore <snapshot_id>
capcli sys doctor --report
```
Inspect the generated Trust Receipt.
