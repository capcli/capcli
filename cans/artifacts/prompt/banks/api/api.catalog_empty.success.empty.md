---
id: prompt://api/catalog_empty@1
stem: api.catalog_empty.success.empty
bank: api
slug: catalog_empty
version: 1
trust: draft
vars:
  - name: env
    type: string
    source: kernel.env
sections:
  stage_1_sync: 70
  stage_2_catalog: 70
  stage_3_prove: 60
  stage_4_ship: 50
slice_max_tokens: 500
docs:
  - doc://use
status: served
---

# ⚡ EXTERNAL API CATALOG LOCKDOWN PROTOCOL
No external API catalogs are configured. Outbound HTTP requests from routines are blocked
at the socket layer until synced, proven, and registered.

## section:stage_1_sync
Sync the provider's OpenAPI spec into the local catalog:
```bash
capcli api sync <provider> <spec_url>
```
Example:
```bash
capcli api sync stripe https://api.stripe.com/openapi.json --interval 7d
```

## section:stage_2_catalog
Confirm the synced verbs landed in the catalog:
```bash
capcli api catalog <provider>
```
Example:
```bash
capcli api catalog stripe --state active
```

## section:stage_3_prove
Prove the API verb inside the simulation environment:
```bash
capcli api prove stripe.refunds.create --env sim
```
Verify that payload scrubbing and token bucket limits match provider contracts.

## section:stage_4_ship
Promote the API capability to reviewed trust:
```bash
capcli api ship stripe.refunds.create reviewed --reason "Enable refund automation"
```
