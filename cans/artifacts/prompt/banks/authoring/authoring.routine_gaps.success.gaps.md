---
id: prompt://authoring/routine_gaps@1
stem: authoring.routine_gaps.success.gaps
bank: authoring
slug: routine_gaps
version: 1
trust: draft
vars:
  - name: env
    type: string
    source: kernel.env
sections:
  stage_1_analyze: 70
  stage_2_scaffold: 80
  stage_3_prove: 70
slice_max_tokens: 500
docs:
  - doc://automate/repetition
status: served
---

# ⚡ ROUTINE GAP MINING PROTOCOL
Operational telemetry detected uncodified multi-step commands executed via raw SQL or ad-hoc calls.
Codify these repeated patterns into governed routines.

## section:stage_1_analyze
Inspect repeated query sequences from the causal audit log:
```bash
capcli sys audit query "SELECT command, count(*) FROM _audit GROUP BY command HAVING count(*) > 5"
```
Identify operations that must run atomically.

## section:stage_2_scaffold
Scaffold a typed routine wrapping the operational sequence:
```bash
capcli routine new <routine_name>
```
Declare typed `Param` inputs and explicit `limits={"max_ops": N, "max_duration_seconds": S}` on the scaffold.

## section:stage_3_prove
Rehearse the scaffolded routine against masked simulation data:
```bash
capcli routine prove <routine_name> --env sim
capcli routine ship <routine_name> reviewed --reason "Codify operational pattern from telemetry"
```
