---
id: prompt://onboarding/harness@1
stem: onboarding.harness.success.empty
bank: onboarding
slug: harness
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
  stage_1_contract: 50
  stage_2_discovery: 90
  stage_3_rehearsal: 70
  stage_4_proving: 60
slice_max_tokens: 500
docs:
  - doc://agents
status: served
---

# ⚡ AUTONOMOUS HARNESS ONBOARDING PROTOCOL (H0–H7)
Host physics verified nominal. System is uninitialized in [{{env}}:{{tier}}].
Operate strictly via structured machine contracts (`--json`).

## section:stage_1_contract
Verify machine-level JSON envelope parity:
```bash
capcli sys doctor --json
```
Assert: `exit_code == 0`, `state_modified == false`, `data.status == "nominal"`.

## section:stage_2_discovery
Enumerate registered capabilities and catalog verbs:
```bash
capcli search "" --json
```
Parse the JSON response array. If zero capabilities exist, trigger the Genesis campaign:
```bash
capcli doc outline prompt://genesis/blank_world@1  # then doc read the stage_1 leaf, --max-tokens 500
```

## section:stage_3_rehearsal
Practice non-mutating preview execution:
```bash
capcli sql "SELECT 1" --dry-run --json
```
Assert: `state_modified == false`.
Never dispatch mutating SQL (`UPDATE`, `DELETE`, `INSERT`) without a preceding `--dry-run`.

## section:stage_4_proving
Verify ability to execute simulation proving:
```bash
capcli routine prove overview --env sim --json
```
All autonomous routines must pass 100% simulation verification before production deployment.
