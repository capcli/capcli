---
id: prompt://genesis/blank_world@1
stem: genesis.blank_world.success.empty
bank: genesis
slug: blank_world
version: 1
trust: draft
vars:
  - name: env
    type: string
    source: kernel.env
  - name: tier
    type: string
    source: kernel.tier
  - name: domain_tables
    type: int
    source: kernel.schema.domain_table_count
sections:
  stage_1_intent: 120
  stage_2_schema: 220
  stage_3_compile: 70
  stage_4_overview: 190
  stage_5_wire: 100
slice_max_tokens: 500
docs:
  - doc://start
  - doc://understand/world
status: served
---

# ⚡ CAPCLI GENESIS DIRECTIVE (BLANK WORLD DETECTED)
Workspace contains {{domain_tables}} domain tables in environment [{{env}}:{{tier}}].
You are operating in a void. Do not write ad-hoc bash scripts.
Execute the 5-stage Genesis protocol. Slices must be executed in order.

## section:stage_1_intent
Establish what exists and what the mission is, from governed surfaces only:
```bash
capcli sys doctor
capcli db schema
capcli search "<mission intent>"
```
No raw filesystem or foreign harness stores. Output of this stage must be an entity list, not code:
1. Core Entities (e.g., Orders, Customers, Invoices)
2. State Transitions (e.g., pending -> paid -> fulfilled)
3. External Wires (e.g., Stripe, Logistics, SendGrid)

## section:stage_2_schema
Declare the physical world in `schema.yaml` using Capcli AST shorthands. Never execute raw `CREATE TABLE`:
```yaml
version: 1
engine: sqlite
db: workspace.db

tables:
  customers:
    prov: true
    columns:
      id: pk
      email: text!
      name: text
      stripe_customer_id: text
      billing_status: text=active
      data: json mask=true

  orders:
    prov: true
    imm_rows: false
    columns:
      id: pk
      customer_id: int ref=customers.id
      total_cents: int~
      status: text=pending
      tracking_num: text
    chk:
      - "status IN ('pending', 'paid', 'shipped', 'cancelled', 'refunded')"
      - "total_cents >= 0"
    idx:
      - [customer_id]
      - [status]

views:
  orders_summary:
    exposes: [orders]
    query: "SELECT status, count(*) as count, sum(total_cents) as volume FROM orders GROUP BY status;"
```

## section:stage_3_compile
Validate syntax, semantics, and compile the physical DDL:
```bash
capcli rule validate
capcli apply -m "Genesis: Initialize business world schema"
```
If errors occur, read the remedy diagnostic, fix `schema.yaml`, and re-run.

## section:stage_4_overview
Author the Ground Zero primer (`routines/overview.py`).
Situational KPIs must remain strictly under 500 result tokens:
```python
from capcli import routine, ctx

@routine(name="overview", idempotent=True, limits={"max_ops": 5, "max_duration_seconds": 10})
def overview():
    kpis = ctx.db.query("SELECT * FROM orders_summary")
    pending = ctx.db.query("SELECT count(*) as count FROM orders WHERE status = 'pending'")
    return {
        "status": "nominal",
        "pending_orders": pending[0]["count"] if pending else 0,
        "kpis": kpis
    }
```
Prove and pin it:
```bash
capcli routine prove overview --env sim
capcli routine ship overview pinned --reason "Mount system overview baseline"
```

## section:stage_5_wire
Import and lock external wire egress before invoking external endpoints:
```bash
capcli api import stripe /v1/charges POST --spec https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.yaml
capcli api prove stripe.charges.create --env sim
capcli api ship stripe.charges.create reviewed --reason "Order billing capability"
```
