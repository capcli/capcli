---
id: doc://prompts/authoring/binding_setup#1
stem: authoring.binding_setup.success.empty
bank: authoring
slug: binding_setup
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
  stage_1_declare: 90
  stage_2_prove: 80
  stage_3_enable: 90
slice_max_tokens: 500
docs:
  - doc://automate/repetition
status: served
---

# ⚡ BINDING SETUP PROTOCOL
No bindings are configured in [{{env}}:{{tier}}].
Declare cron, webhook, or endpoint triggers against governed routines.

## section:stage_1_declare
Declare the binding in `routines/<name>.py` via ctx.bind:
```python
ctx.bind.cron(schedule="*/5 * * * *", routine="<name>")
ctx.bind.webhook(event="stripe.charge.succeeded", routine="<name>")
ctx.bind.endpoint(path="/hooks/orders", routine="<name>")
```

One binding per declaration. See plugins.md#Capabilities.

section:stage_2_prove

Prove the routine fires under each binding in sim:

```bash
capcli routine prove <name> --environment sim
```

Confirm zero policy denials and zero drift events.

section:stage_3_enable

Register the binding and confirm mount:

```bash
capcli bind list
capcli bind inspect <binding_id>
```

Bindings dissolve atomically with routine retirement.

