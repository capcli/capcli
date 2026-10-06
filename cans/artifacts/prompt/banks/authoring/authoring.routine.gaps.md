---
id: doc://prompt/authoring/routine_gaps@1
stem: authoring.routine.gaps
bank: authoring
slug: routine_gaps
version: 1
trust: draft
trigger:
  screens: ["run.search.success.gaps"]
  predicate:
    gap_count: ">=1"
vars:
  - name: env
    type: string
    source: kernel.env
sections:
  stage_1_analyze: 70
  stage_2_scaffold: 80
  stage_3_prove: 70
slice_max_tokens: 500
docs: "docs/automate/repetition.md"
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
Enforce strict boundaries:
- Maximum 150 Lines of Code (LOC)
- Maximum 8 typed `Param` variables
- Explicit `limits={"max_ops": N, "max_duration_seconds": S}`

## section:stage_3_prove
Rehearse the scaffolded routine against masked simulation data:
```bash
capcli routine prove <routine_name> --env sim
capcli routine ship <routine_name> reviewed --reason "Codify operational pattern from telemetry"
```
