---
id: prompt://wire/catalog_empty@1
stem: wire.catalog.empty
bank: wire
slug: catalog_empty
version: 1
trust: draft
vars:
  - name: env
    type: string
    source: kernel.env
sections:
  stage_1_import: 70
  stage_2_record: 70
  stage_3_prove: 60
  stage_4_ship: 50
slice_max_tokens: 500
docs:
  - doc://use
status: served
---

# ⚡ EXTERNAL WIRE CATALOG LOCKDOWN PROTOCOL
No external API catalogs are configured. Outbound HTTP requests from routines are blocked
at the socket layer until imported, proven, and registered.

## section:stage_1_import
Import an external OpenAPI endpoint into the local catalog:
```bash
capcli api import <provider> <path> <method> --spec <spec_url_or_file>
```
Example:
```bash
capcli api import stripe /v1/refunds POST --spec https://api.stripe.com/openapi.yaml
```

## section:stage_2_record
Record an idempotent live request to capture response schemas and create simulation cassettes:
```bash
capcli api record stripe.refunds.create -p charge_id="ch_test_123"
```
This writes fixtures into `apis/<provider>.cassette.jsonl`.

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
