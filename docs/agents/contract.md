# Contract

You are the harness. Capcli doesn't trust you. That's a feature — this page is the boundary between your cognition and governed execution, and everything else in this section assumes you've read it.

---

## Three roles. Do not collapse them.

| Layer | Owns | Never does |
|---|---|---|
| **Harness** (you) | Cognition: planning, ranking, deciding when to retry | Touch state directly |
| **Capcli** | Governed execution: CLI surface, registry, trust ladder | Reason about your goals |
| **Kernel** | Mechanical enforcement, dispatch, audit | LLM inference — zero, ever |

You propose. The kernel disposes. The ledger records. There is no mode where the kernel "understands what you meant" — only what you declared, what policy allows, and what the audit spine can prove. The kernel treats every caller uniformly — PID, principal, agent ID, session. You are not special; that's why you're safe to let loose.

---

## The execution model

You invoke a stateless CLI from a bash subshell:

```
capcli <noun> <verb> [target] [--flags]
```

Ten nouns: `run`, `db`, `routine`, `api`, `bind`, `ping`, `rule`, `env`, `sys`, `doc`. The subshell reaches the kernel daemon over an IPC socket; direct `workspace.db` file access is blocked. External tools consume the same surface over the HTTP/WS daemon (JSON-RPC 2.0) — same gates, same audit.

Universal flags are frozen at twelve — no per-noun growth, no `--force`, no `--verbose`, no `--override-budget`. Root `--help` is capped at 6 lines and points to search. Every command is tagged for its caller: `[harness]` (autonomous execution — yours), `[human]` (interactive approval — escalate via ping), or `[both]`. A `[human]` gate means a human, not a cleverer flag combination. Grammar and tags: [../reference/cli.md](../reference/cli.md).

---

## Exit codes are the machine language

You don't parse prose. You read integers.

| Exit | Meaning | State |
|---|---|---|
| `0` | Success; audit event recorded | Modified |
| `2` | Invariant or governance denial | Untouched |
| `3` | Refusal: validation failure, missing intent or param, drift | Untouched |
| `4` | Sandbox runtime crash | Rolled back |
| `5` | Kernel panic; audit sink unreachable | Refused |
| `6` | Quota yield; parked until refill | Untouched |

Non-zero exits guarantee `state_modified: false`. A partial commit would be a kernel bug, not your problem. Full table: [../reference/exit-codes.md](../reference/exit-codes.md).

---

## The return envelope

With `--json`, every command returns one shape: `{ exit, json, text }`.

```bash
$ capcli run dispatch_order -p order_id=ORD-8842 -p carrier=fedex \
    -m "fulfill paid order for customer checkout" --json
```

```
{
  "exit": 0,
  "json": {
    "capability": "cap://dispatch_order@4",
    "status": "dispatched",
    "ops_used": "3/8",
    "audit_chain": ["op_9f2c", "op_9f2d", "op_9f2e"]
  },
  "text": "[dev:tier_1]  dispatch_order@4  ✓  1.2s"
}
```

Branch on `exit`. Consume `json`. Ignore `text` unless a human is reading over your shoulder. One envelope — no scraping, no regex over banners.

Denials return the canonical error keys — `domain`, `culprit`, `remedy`, `state_modified`:

```
{
  "exit": 2,
  "json": {
    "domain": "policy.query",
    "culprit": "policy.query.update_delete.require_where",
    "remedy": "add WHERE + LIMIT, or use chunked loop via ctx.db.execute",
    "state_modified": false
  },
  "text": "[dev:tier_1]  ✗ exit 2"
}
```

---

## Mutations carry intent

Every mutating operation takes `-m` / `--intent`; missing intent on a write throws exit 3 before anything executes. Intent propagates down the chain — session goal → routine intent → op intent — and lands on every leaf event.

The kernel doesn't judge your reason. It demands you have one, and that it matches your blast radius: an intent target that diverges from the AST's write tables is denied with exit 2. High-impact writes additionally demand `--reason`. `--intent` accepts inline text or `@<path>` / `@-` (stdin) for long or hostile strings.

---

## Sessions and principals

A session is the kernel's temporary scope for a piece of governed work, held as a kernel-minted HMAC token passed as `--session <token>`. It binds principal and frame; `CAPCLI_SESSION` or the workspace's active context preserves it across turns. Session counters — fuel, wire bytes, rate, rows — ride every budget frame, audit event, and claim. Tokens are kernel-issued; self-declaration is denied. Detail: [../concepts/sessions.md](../concepts/sessions.md).

Identity around the session is a four-link chain — principal → agent → session → op — recorded on every leaf event:

- `--as <principal>` declares the *beneficiary* of execution. Scoped views refuse to compile without it; the kernel binds `:principal`, and the query returns exactly that principal's rows.
- `--by <agent-id>` declares the *acting* identity, verified against process credentials. Mismatch aborts with exit 3 — you cannot claim a link you were never issued. Detail: [../understand/identity.md](../understand/identity.md).

---

## H0: read the machine boundaries first

```bash
$ capcli sys doctor --json
```

```
{
  "exit": 0,
  "json": { "tier": "tier_1", "sandbox": "bwrap", "status": "nominal" },
  "text": "[dev:tier_1]  doctor  ✓  nominal"
}
```

Tier matters: pinned execution is denied outright on tier 2 hosts. Know your floor before you plan against the ceiling.

---

**Found nothing yet? Find something** → [discovery.md](discovery.md)

**The cognition/execution boundary, deeper** → [../concepts/harness-and-capcli.md](../concepts/harness-and-capcli.md)
