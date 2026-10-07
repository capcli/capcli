---
id: prompt://authoring/overview_absent@1
stem: authoring.overview.absent
bank: authoring
slug: overview_absent
version: 1
trust: draft
vars:
  - name: env
    type: string
    source: kernel.env
sections:
  stage_1_scaffold: 140
  stage_2_bound: 50
  stage_3_pin: 60
slice_max_tokens: 500
docs:
  - doc://agents/codification
status: served
---

# ⚡ GROUND ZERO OVERVIEW CODIFICATION PROTOCOL
Your workspace lacks a situational overview routine. Autonomous agents will burn tokens
blindly querying tables unless grounded by a unified briefing.

## section:stage_1_scaffold
Scaffold `routines/overview.py` aggregating core domain counts:
```python
from capcli import routine, ctx

@routine(name="overview", idempotent=True, limits={"max_ops": 5, "max_duration_seconds": 5})
def overview():
    kpis = ctx.db.query("SELECT * FROM orders_summary")
    pending = ctx.db.query("SELECT count(*) as count FROM orders WHERE status = 'pending'")
    return {
        "status": "nominal",
        "pending_orders": pending[0]["count"] if pending else 0,
        "kpis": kpis
    }
```

## section:stage_2_bound
Ensure the overview output envelope stays strictly below 500 result tokens.
Never return unbounded lists or raw JSON blobs inside overview payloads.

## section:stage_3_pin
Rehearse in simulation and promote to pinned:
```bash
capcli routine prove overview --env sim
capcli routine ship overview pinned --reason "Establish system overview baseline"
```
