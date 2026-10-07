---
id: prompt://hitl/ping_ask_suspended@1
stem: hitl.ping_ask.suspended
bank: hitl
slug: ping_ask_suspended
version: 1
trust: draft
vars:
  - name: env
    type: string
    source: kernel.env
sections:
  stage_1_inspect: 50
  stage_2_resolve: 60
  stage_3_occ: 80
slice_max_tokens: 500
docs:
  - doc://use
status: served
---

# ⚡ HUMAN-IN-THE-LOOP (PING ASK) RESOLUTION PROTOCOL
A routine executed `ctx.ping.ask`. Execution is parked awaiting human input.
State is protected by an Optimistic Concurrency Control (OCC) fence.

## section:stage_1_inspect
Enumerate pending inquiry cards:
```bash
capcli ping list --pending
```
Review the structured question, available options ($\le 5$), and timeout deadline.

## section:stage_2_resolve
Resolve the inquiry via CLI or provide the Cockpit URL to the human operator:
```bash
capcli ping resolve <ask_id> --choice approve
```
Cockpit Web UI: `http://127.0.0.1:4040/inquiries`

## section:stage_3_occ
Handle OCC state drift on resumption:
If underlying records were modified while awaiting human response, resumption trips an OCC conflict (`exit 2`).
Transaction rolls back cleanly. Re-invoke the routine from turn zero with fresh state:
```bash
capcli run <routine_name>
```
