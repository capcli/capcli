# Errors & Denials

Every failure below is real, documented, and structurally guaranteed to leave `state_modified: false`.

What is *not* here: invented error codes to make the table look complete. If a code isn't in the spec, it isn't in this table, and any tooling claiming otherwise is telling you a bedtime story.

---

## Denial shape (identical every time)

```text
FAIL  <rule code>            ← the exact policy key
<statement>                  ← what you submitted
<caret at the culprit>       ← where it went wrong
<explanation>                ← one honest sentence

state_modified: false
layer: <AST | authorizer | trust | budget | vault>
remedy: <sanctioned next action>
```

## The documented catalog

| Rule code | Layer | Fires when | Remedy |
|---|---|---|---|
| `policy.query.update_delete.require_where` | AST | `UPDATE`/`DELETE` without `WHERE` | Add `WHERE` + `LIMIT`, or chunk via `ctx.db.execute` |
| `policy.query.update_delete.require_limit` | AST | Mutation without `LIMIT` (unbounded blast) | Add `LIMIT`, or target a primary key |
| `policy.query.update_delete.deny_patterns` | AST | Tautology predicates (`WHERE 1=1`) | Bounded predicate |
| `policy.query.writes_require_intent` | Intent | Mutating write without `-m` | Add `-m "why"` — always, every time |
| `policy.authorizer.trust_gate` | authorizer | Column denied at caller's rung (e.g. draft reading `secrets.value`) | Promote the routine, or accept the mask |
| `policy.authorizer.immutable_system_table` | authorizer | Mutation of `_audit` or other system tables | There is no remedy. That's the point. |
| `policy.budget.ops_exhausted` | budget | Frame or session op ceiling hit (op #51 of 50) | Split work, raise declared limits, or yield |
| `policy.secrets.missing` | vault | Capability requires a vault ref that isn't set | Human injects via Cockpit (`http://127.0.0.1:4040/vault`) — never via chat |
| `policy.quota.*` (yield) | budget | Provider bucket empty (background) | None needed — task parked until refill |
| `E045_TIER2_PINNED_DENIED` | trust | Pinned routine invoked on a Tier 2 host | Run on a Tier 1 host. macOS doesn't get prod keys. |

## Boot refusals (`exit 3`, before anything runs)

| Cause | Fix |
|---|---|
| `python < 3.11` or `git < 2.30` | Install them; doctor names the missing one |
| bwrap missing on Linux (Tier 1) | `apt install bubblewrap` |
| Lockfile hash mismatch (prod/sim) | You hand-edited YAML. `git checkout` it. |
| `system_schema` hash mismatch | Kernel-managed; don't touch it |
| Clock drift > 500ms vs NTP | Sync the clock. Causality needs chronology. |
| Remote HTTP database without C authorizer | Refused outright; use local SQLite / libsql replica |
| Missing session / forged / expired token | Start a real session; forging is also an *event* now |

## Kernel panic (`exit 5`)

Audit sink unreachable or host resource failure. The 5-minute in-memory buffer has passed, and the kernel halts rather than run unaudited. This is the "circuit breaker of last resort," and it fires *instead of* silent data loss. You're welcome.

## What does NOT exist

- No `E_ERR_SOMETHING_WEIRD_0001` grab-bag. Every code is a policy key or a documented boot refusal.
- No "partial success" exit. Partial = rolled back = exit `4`.
- No error that means "maybe." The deterministic kernel doesn't maybe.

---

**The integers** → [exit-codes.md](exit-codes.md) · **The ceilings** → [limits.md](limits.md)
