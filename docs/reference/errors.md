# Errors & Denials

A denial is not an error message. It is the boundary of the system, stated out loud, with a remedy attached. Denials teach; this page is their anatomy textbook.

---

## The anatomy

Every denial follows the same skeleton. Here is the classic — the unbounded DELETE:

```bash
$ capcli sql "DELETE FROM orders"
```

```
[dev:tier_1]  ✗  exit 2

  FAIL  policy.query.update_delete.require_where
        DELETE FROM orders
        ^^^^^^^^^^^^^^^^^^
        Missing WHERE clause. Unbounded delete denied.

  state_modified: false
  remedy: add WHERE + LIMIT, or use chunked loop via ctx.db.execute
```

| Part | Contract |
|---|---|
| `[env:tier]` prefix | Where the refusal happened |
| `✗ exit <n>` | The code and its state guarantee — see [exit-codes.md](exit-codes.md) |
| `FAIL <rule.id>` | The exact rule you hit |
| Statement + caret line | What you tried, offending bytes underlined |
| `state_modified: false` | Nothing changed. Strictly boolean, strictly false on non-zero exits |
| `measured` | The observed value vs the ceiling (e.g. "342 LOC vs 150 cap") |
| `remedy` | The door out — actionable, never apologetic |

The `layer` field names the floor that caught you: AST, authorizer, budget, trust, sandbox, compiler, vault, or quota.

Under `--json`, the canonical error payload carries four guaranteed keys: `domain`, `culprit`, `remedy`, `state_modified`. Machines parse those; humans read the carets. Same verdict, two renderings.

### The YIELD variant

Exit 6 swaps `FAIL` for `YIELD`: no culprit to fix, no state to roll back — a parked frame, a `reset_at` timestamp, and a daemon that will wake it. Details in [exit-codes.md](exit-codes.md).

---

## Every rule id attested in the specs

This table is complete in one specific sense: these are exactly the rule ids attested across `cans/` and the verified docs. Nothing invented, nothing padded.

| Rule id | Exit | Layer | What it means |
|---|---|---|---|
| `policy.query.update_delete.require_where` | 2 | AST | UPDATE/DELETE with no WHERE — unbounded blast radius |
| `policy.query.update_delete.require_limit` | 2 | AST | WHERE present, LIMIT missing |
| `policy.query.update_delete.deny_patterns` | 2 | AST | Tautology bypass (`WHERE 1=1`, `... OR 1=1`) |
| `policy.query.writes_require_intent` | 3 | AST | Mutating write without `-m` intent |
| `policy.authorizer.trust_gate` | 2 | authorizer | Column denied for the caller's trust level (e.g. draft reading `secrets.value`) |
| `policy.authorizer.sim_denial` | 2 | authorizer | `prod-only` verb invoked in `dev`/`sim` |
| `policy.authorizer.immutable_system_table` | 2 | authorizer | Write to an append-only system table (`_audit`) |
| `policy.trust.draft_writes_denied` | 2 | trust | Draft routine attempting prod writes |
| `policy.budget.ops_exhausted` | 2 | budget | Frame hit its declared ops ceiling |
| `kernel.network.jail` | 2 | sandbox | Raw socket (`connect`, syscall 42) trapped by seccomp-bpf |
| `kernel.boot.lockfile_mismatch` | 3 | compiler | `capcli.lock` root hash diverges from the working tree — prints `FATAL`, refuses to boot |
| `policy.secrets.missing` | 3 | vault | Credential absent; direct CLI injection is banned |
| `identity.process_mismatch` | 3 | identity | `--by` doesn't match the OS process credentials |
| `policy.api.quota_exhausted` | 6 | quota | Provider quota dry — yield, park, resume |

---

## The warning that isn't a denial

Twenty sustained denials trip the thrashing detector. The kernel notices your harness is stuck in a loop and says so:

```
[dev:tier_1]  ⚠  agent.thrashing

  agent: agt_7f3k
  denials_last_5m: 22
  pattern: repeated policy.query.update_delete.require_limit
  remedy: harness appears stuck; consider changing approach or escalating to human
```

That's a `⚠`, not a `✗` — an observation about behavior, not a block on an operation.

---

## What this page deliberately does not contain

The specs publish no exhaustive numbered error registry, so this page won't manufacture one to look finished. Rule ids are minted from compiled `policy.yaml` and `governance.yaml`; the table above is the set attested in the documentation. If your terminal shows a rule id that isn't listed here, the authority is not this table — it's the explanation the kernel itself hands you: `capcli sys audit trace <op-id> --explain`.

---

**What each exit code guarantees** → [exit-codes.md](exit-codes.md)

**Was it a ceiling, not a rule?** → [limits.md](limits.md)
