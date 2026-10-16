---
id: doc://prompts/authoring/static_refusal#1
stem: authoring.static_refusal.denial.refused
bank: authoring
slug: static_refusal
version: 1
trust: draft
sections:
  stage_1_classify: 90
  stage_2_remediate: 90
  stage_3_redispatch: 60
slice_max_tokens: 500
docs:
  - doc://reference/errors
status: served
---

# ⚡ STATIC REFUSAL REMEDIATION PROTOCOL
Pre-flight refused the dispatch before any guest ran. State is untouched.
Classify the refusal domain, fix the static fault, and re-dispatch.

## section:stage_1_classify
Read the denial domain from the envelope:
- `compile` — Python syntax error or import failure.
- `validation` — Param type mismatch or missing required arg.
- `missing_param` — required Param absent.
- `lockfile_mismatch` — capcli.lock out of sync.
- `schema_hash_mismatch` — system schema hash drift.
- `kernel.boot` — boot refusal.
Exit 3 guarantees no guest code ran.

## section:stage_2_remediate
Apply the remedy verbatim from the denial envelope:
- Param faults — pass the missing arg with `-p k=v`.
- Type faults — match the declared Param type exactly.
- Lockfile drift — rerun pre-flight sub-checks.
- Schema drift — rerun pre-flight sub-checks.
Never edit capcli.lock by hand.

## section:stage_3_redispatch
Re-dispatch the exact original command.
Confirm `exit_code == 0` and `state_modified == true` if a write was intended.
