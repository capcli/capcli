---
id: doc://prompt/crucible/execution_starved@1
stem: crucible.execution.starved
bank: crucible
slug: execution_starved
version: 1
trust: draft
trigger:
  screens: ["run.execute.denial.budget_cascade"]
  predicate:
    domain: "policy.budget"
vars:
  - name: env
    type: string
    source: kernel.env
sections:
  stage_1_budget: 90
  stage_2_jail: 90
  stage_3_claims: 90
  stage_4_vault: 80
slice_max_tokens: 500
docs: "docs/reference/limits.md"
status: served
---

# ⚡ EXECUTION CRUCIBLE RESOLUTION PROTOCOL
Execution was intercepted by kernel boundary defenses (budget starvation, sandbox trap, or lease collision).
Follow this 4-stage resolution pipeline:

## section:stage_1_budget
Resolve call-tree budget starvation:
1. Run pre-flight inspection to locate the tightest child constraint:
   ```bash
   capcli inspect cap://<routine_name>
   ```
2. Child routines inherit bounds via `min()`. Adjust the parent routine's `@routine` declaration:
   `limits={"max_ops": parent_ops + sum(child_ops)}`

## section:stage_2_jail
Remediate sandbox network traps (Syscall 42):
Raw socket egress (`connect`) is blocked by seccomp-bpf.
Never import `requests`, `urllib`, or raw `fetch`.
Route traffic exclusively via imported catalog verbs:
```bash
capcli api catalog <provider>
```
Dispatch inside routines via `ctx.api.call("<provider>.<verb>", payload)`.

## section:stage_3_claims
Resolve contested lease collisions (`db.claims`):
If an exclusive entity lease is held by another session:
```bash
capcli sql "SELECT * FROM claims WHERE resource = :target" -p target="orders:ORD-1"
```
Do not poll in a tight while loop. Yield control back to sensory inbox:
```bash
capcli sys inbox pop
```

## section:stage_4_vault
Resolve missing vault credentials:
Passing API tokens via prompts or CLI arguments is blocked to prevent leaks.
Inject secrets through the Cockpit vault screen (127.0.0.1:4040), or import local environment variables in development:
```bash
capcli sys vault import-env
```
