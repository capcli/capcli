---
name: capcli-bootstrap
version: 1.0.0
description: Harness gateway for autonomous capabilities
pointer: skill://capcli/bootstrap
---

# CLI Execution Contract

You interact with the workspace exclusively via `capcli`. Direct database file access or unmanaged network sockets are physically denied by OS jails.

## Universal Grammar
`capcli <noun> <verb> [target] [--flags]`

## Mandatory Invariants
1. **Mutating writes require intent:** Pass `-m "<intent>"` or write fails closed (exit 3).
2. **Single SQL Entrypoint:** Execute raw SQL via `capcli sql "<query>"`. ORMs and raw file edits are blocked.
3. **Discovery Before Invocation:** Use `capcli search <query>` to locate capabilities; inspect pre-flight via `capcli inspect <urp>`.
4. **Pagination Law:** Keyset pagination `{ items, pagination: { next_cursor } }` is enforced; raw string slicing exits 3.

## Exit Status Contract
* `0`: Success (contains structured affordances).
* `2`: Governance/Authorizer denial (state untouched).
* `3`: Compile/Syntax failure (malformed statement, unpaginated shape).
* `4`: Runtime fault (clean rollback).
* `5`: Panic or plaintext credential leak (immediate kill).
* `6`: Quota/preemption yield (frame parked to _suspended_tasks).

Full exit law: see cans/kernel.md#Exit-code-law.
