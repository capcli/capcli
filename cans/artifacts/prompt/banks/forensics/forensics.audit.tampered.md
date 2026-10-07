---
id: doc://prompt/forensics/audit_tampered@1
stem: forensics.audit.tampered
bank: forensics
slug: audit_tampered
version: 1
trust: draft
trigger:
  screens: ["sys.doctor.success.tamper"]
  predicate: {}
vars:
  - name: env
    type: string
    source: kernel.env
sections:
  stage_1_quarantine: 50
  stage_2_isolate: 70
  stage_3_attest: 60
slice_max_tokens: 500
docs: "docs/understand/ (audit page: docs debt)"
status: served
---

# ⚡ TAMPER FORENSICS & QUARANTINE PROTOCOL
A broken SHA-256 hash link was detected in `_audit`.
The causal DAG detected ledger corruption. Corrupted blocks are quarantined to preserve operational uptime.

## section:stage_1_quarantine
Inspect the quarantined audit entries:
```bash
capcli sys doctor
```
Locate the exact operation ID where `parent_hash != prev_hash`.

## section:stage_2_isolate
Verify that corrupted blocks have been isolated to `audit.quarantine.jsonl`.
Live database tables remain online; uncorrupted audit history remains queryable:
```bash
capcli sys audit query "SELECT * FROM _audit ORDER BY timestamp DESC LIMIT 10"
```

## section:stage_3_attest
Verify current state against the offsite S3 WORM ledger root:
```bash
capcli sys doctor --report
```
Reconcile root ledger hashes to ensure offsite backups reflect verified operations.
