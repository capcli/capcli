# capcli-routine.architecture.md *(final v3 — primitive-aware, fully integrated)*

> **Update v3.1:** Added §9.5 Harness Skill Invocation Pattern (2026-09-12)
> The procedure layer of capcli: **Python as the composition language, learned at runtime, governed like everything else.**

---

## 1. Scope & Convictions

Routines are how the agent turns repeated raw operations into reusable, callable capabilities. Five convictions:

1. **Procedures are code, not config.** The moment a representation needs sequencing, branching, retries, or composition — it's Python. We do not invent a language inside YAML.
2. **Raw SQL is exploration; routines are exploitation.** The learning loop: raw ops → repeated patterns → consolidated routine → pinned capability. Kill raw SQL and the loop never starts; kill routines and nothing is ever learned.
3. **The sandbox IS the enforcement boundary. AST validation is a lint.** Python AST checking catches common mistakes (subprocess, os, raw sqlite3) but cannot catch `exec()`, `eval()`, dynamic imports, or metaprogramming. It creates false confidence if treated as a gate. The jail (bwrap, seccomp-bpf, no network, read-only fs) is the only real protection. AST is defense-in-depth, not a gate.
   A routine can compute anything inside its jail, but every effect — SQL, HTTP, schedule, notify, claims — round-trips through the kernel gate.
4. **A routine is a governed artifact.** Versioned, hash-pinned, trust-leveled, size-capped, decayed, consolidated. It earns its place; it doesn't accumulate.
5. **Event-driven at the edges, imperative at the core.** Events start routines; routines never consume events.

---

## 2. Routine vs Op — the hierarchy

| | **Op (operation)** | **Routine** |
|---|---|---|
| What | One atomic capability call | Composed sequence of ops + logic |
| Granularity | Single effect | Multiple effects, one purpose |
| Lives as | Command / SDK call | Python file in `routines/` |
| Trust | Inherits from channel | Own ladder: draft → reviewed → pinned |
| API verbs | N/A | Imported via sync, activated via gate, same trust ladder |
| Versioned | No — it's a call | Yes — version + code_hash |
| Learned | No — fixed primitives | **Yes** — born from repeated op patterns |

```
routine: refund_and_archive          ← learned, versioned, trust-leveled
  ├── op: api.call stripe.get_charge      ← atom
  ├── op: db.query "SELECT ..."           ← atom
  ├── op: api.call stripe.refund_charge   ← atom
  └── op: db.txn(2× db.exec)              ← atoms
```

**Ops are what the kernel can do. Routines are what the agent has learned to do with it.** Once registered, both are *capabilities* — `capcli run` calls either the same way.

Naming precision (never blur these three):

| Term | Means |
|---|---|
| **Op** | the invocation through the gate |
| **Effect** | the world change it produces |
| **Event** | the audit record — exists even when the op is *denied* |

---

## 3. Anatomy of a Routine

```python
# routines/refund_and_archive.py — agent-written at runtime
from capcli import routine, Param

@routine(
    name="refund_and_archive",
    trust="draft",                    # draft → reviewed → pinned
    idempotent=False,                 # must be declared before retries allowed
    description="Refund a charge and archive its entities.",
    limits={"max_duration_seconds": 300},   # declared need; governance sets ceiling
)
def refund_and_archive(ctx, params):
    order_id: Param[str] = params["order_id"]

    # HTTP capability — kernel injects secrets + idempotency key
    order = ctx.api.call("stripe.get_charge", {"charge_id": order_id})

    # raw SQL read — authorizer + AST gated
    rows = ctx.db.query(
        "SELECT * FROM entities WHERE ref = :ref", {"ref": order_id})

    # HTTP write — pre-call policy, spend caps, audit
    refund = ctx.api.call("stripe.refund_charge",
        {"charge_id": order_id, "amount": order["amount"]},
        intent=f"refund {order_id}")

    # raw SQL write — txn-wrapped, WHERE+LIMIT enforced
    with ctx.db.txn():
        ctx.db.execute(
            "UPDATE entities SET status = 'refunded' WHERE ref = :ref LIMIT 1",
            {"ref": order_id}, intent=f"mark {order_id} refunded")

    return {"refund_id": refund["id"], "entities": len(rows)}
```

HTTP, raw SQL, Python logic — one callable. Every leaf effect still crosses the gate.

---

## 4. The `ctx` Contract

```python
ctx.db.query(sql, params) -> list[dict]
ctx.db.execute(sql, params, intent) -> Result
ctx.db.txn() -> context manager
ctx.db.lock(target, ttl) -> Claim              # cross-agent coordination
ctx.api.call(verb, params, intent) -> dict
ctx.api.verify(verb, key) -> dict
ctx.bind.cron(...) / ctx.bind.webhook(...) / ctx.bind.endpoint(...)   # inbound triggers
ctx.ping.notify(principal, message, channel, intent)
ctx.ping.ask(principal, question, options, timeout, intent) -> Answer
ctx.log(msg) -> None                     # structured, audited
ctx.params -> dict                       # validated against Param declarations
```

Design rules:

- **`ctx` injection, never module imports.** The kernel passes `ctx` into the sandbox. Zero import surface to police; no `import requests`, no `import os`, no raw `sqlite3`.
- **AST-validated before execution.** Subprocess, HTTP clients, filesystem escapes — rejected at `draft` time, not at call time.
- **`Param` declarations are the interface.** Typed, documented, validated at the gate; what `capcli inspect` shows and what the agent reads before reuse.
- **Large results stay in routine scope.** Only computed summaries cross to the model (capped by `max_result_tokens`). Token discipline and PII containment in one rule.

---

## 5. Event-Drivenness — edges yes, core never

### Four things can *start* a routine

```
capcli run (agent/human)  ─┐
bind cron fire             ─┼─→  routine runs  ─→  effects + audit events
bind webhook dispatch      ─┤
ping ask resume (reply)    ─┘
```

### Inside: strictly sequential, no reactivity

| Temptation | What it destroys |
|---|---|
| `ctx.on("event", handler)` inside a routine | Traceability — effects in callback order, not code order |
| Reactive streams between ops | Replay determinism — the causal DAG stops being a DAG |
| Long-lived subscriptions | Transaction semantics — when does the txn close? |
| Parallel event branches | Blast-radius accounting — `max_ops_per_run` uncountable |

**The rule:** *events trigger routines; routines never consume events.* Continuous reaction = a **bind webhook** (declared, governed). Waiting = one structured `ctx.ping.ask` suspension. **Routine = transaction-shaped story; events start stories, they don't flow through them.**

---

## 6. Primitives: Manifests & Fingerprints 🔬

A routine is a story, but maintenance reads it word by word. This mechanism closes the gap between routine-level lifecycle and primitive-level reality.

### Declared Manifest (Static)

At `draft` time, the AST pass extracts the **primitive manifest** — the exact sequence of `ctx.*` calls the routine declares it will make. Stored with the version.

```yaml
# extracted at draft, stored with version 17
manifest:
  - api.call: stripe.get_charge
  - db.query: entities (read)
  - api.call: stripe.refund_charge
  - db.txn: [db.exec:entities(update), db.exec:edges(insert)]
estimated_cost_class: [2× http, 2× write]
```

The routine now *declares what it will touch* before it ever runs.

### Runtime Fingerprint (Dynamic)

Aggregated from the audit mirror during execution. The actual sequence of leaf ops that fired.

```sql
-- view: routine_fingerprints
SELECT routine_version, seq, capability, target, count(*)
FROM _audit WHERE event IN ('db.exec','db.query','api.call')
GROUP BY routine_version, seq, capability, target
```

### Why this matters

| System | Without primitives | With manifests + fingerprints |
|---|---|---|
| **Consolidation** | code text similarity | fingerprint similarity — identical primitive sequences merge regardless of Python differences |
| **Regression** | code_hash changed | v18 adds a new leaf op → flagged automatically during promote review |
| **Cost attribution** | routine p95 only | per-leaf duration/spend → "this routine is 90% one HTTP call" |
| **Drift detection** | none | runtime fingerprint diverges from manifest → `governance.anomaly` event |
| **Testing** | "it didn't crash" | proves declaration vs execution |

All deterministic GROUP BYs and AST extraction. The kernel counts at leaf depth so the harness and human can reason with finer evidence.

---

## 7. The Trust Ladder × Environment Axis

Two axes of one ladder:

```
draft ──> reviewed ──> pinned
  │          │            │
 dev    +  sim         + prod (merge + sign-off)
```

| Level | Meaning | Caps | Audit |
|---|---|---|---|
| `draft` | agent-learned, unproven | max_rows_affected: 10 | full |
| `reviewed` | human/CI sign-off | max_rows_affected: 100 | full |
| `pinned` | proven record | max_rows_affected: 500 | summary |

Rules:

- **Self-promotion is impossible.** Promotion is human/CI-gated; the agent supplies evidence from the audit mirror, humans supply authority
- **Prod requires merge + pin.** Draft writes denied in prod outright; reaching prod travels dev → sim → prod by git merge
- **Cross-agent calls require ≥ reviewed.** One agent's draft never becomes another's dependency
- The promotion path is recorded (`promoted_through: [dev, sim, prod]`) — the journey is provenance

Full stage mechanics: **see `capcli-routine-lifecycle.architecture.md`.**

---

## 8. Governance — what routines may *be*

Policy governs what routines may *do*; governance governs what they may *be* — `governance.yaml`:

```yaml
routine_shape:                    # defaults for every routine file
  loc: { min: 5, max: 150 }
  tokens: { min: 50, max: 2000 }  # file size in tokens (context cost)
  params: { max: 8 }
  description: { min_words: 5 }   # searchable or it doesn't ship
  max_ops_per_run: 50             # primitive DAG ceiling
  max_duration_seconds: 300
  max_result_tokens: 500
  manifest_drift: anomaly         # undeclared ops trigger governance event
```

- **Effective limit = min(declared need, governance ceiling, override).** A routine may ask for less, never more
- **Enforcement bites at five gates:** register (registry caps) → draft (shape + manifest) → runtime (ops/duration/result/drift) → monitor (dead/failing) → sweep (scheduled subtraction)
- Denial cites the exact number; exceptions are git-tracked overrides, never `--force`
- Governance is never runtime-editable — a routine cannot loosen its own cage

---

## 9. Composition & Import

Routines are Python modules in `routines/`; they import each other:

```python
# routines/weekly_cleanup.py
from routines.refund_and_archive import refund_and_archive

@routine(trust="draft")
def weekly_cleanup(ctx, params):
    stale = ctx.db.query(
        "SELECT ref FROM entities WHERE status = 'temp' LIMIT 100")
    for row in stale:
        refund_and_archive(ctx, {"order_id": row["ref"]})
```

- Higher-order composition, arbitrarily deep; the kernel gates **every leaf effect** regardless of stack depth
- Callee's trust governs its effects; intent chains propagate via `caused_by`
- Multi-agent collisions: semantic similarity check at creation → near-duplicate → **merge or fork**, human-gated. Never silent duplication

### 9.5 Harness Skill Invocation Pattern

Harness skills (SKILL.md) invoke routines through a strict three-step protocol.
This is the canonical pattern that all skill authors must follow.

```
Step 1: DISCOVER     capcli search "refund" --json
Step 2: INSPECT      capcli inspect refund_and_archive --json
Step 3: INVOKE       capcli run refund_and_archive \
                        -p order_id=ORD-8842 \
                        --intent "refund customer ORD-8842 per skill refund-workflow"
```

**Parameter mapping:** Skill frontmatter parameters map 1:1 to routine `Param` declarations.
Type mismatches fail at the gate with exit code 3. Skills must inspect before invoking.

**Result handling:** Routine return values stay in kernel scope. Only the computed summary
(capped by `max_result_tokens`) crosses back into skill context. Large datasets never
enter the LLM context window. Skills must design for summary-shaped outputs.

**Intent chain:** Skills must pass meaningful `--intent` strings. The intent propagates
downward: `skill intent → routine intent → op intent`. Boilerplate intents ("test", "fix")
are denied by policy. Skill name is recorded via `triggered_by_skill` audit field when
`identity.skill_origin.allow_propagation` is enabled.

**Anti-patterns (skills must NEVER instruct agents to):**
- Write raw SQL directly (`capcli db exec` is `[human]`-tagged)
- Call `capcli routine ship` / `capcli routine draft` (consolidation is human-gated)
- Read secrets or masked columns (policy denies at authorizer level)
- Bypass `capcli run` by constructing HTTP calls or filesystem access
- Cache routine results across sessions (state lives in workspace.db, not skill memory)
- Propose routines without evidence (routines are drafted only after ≥3 identical primitive sequences appear in the audit mirror)
- Self-promote during onboarding (draft → prove in sim → ship requires human/CI gate, always)

**Skill author checklist:**
1. ✅ Uses only `[harness]`-tagged commands from command.architecture.md §4
2. ✅ Inspects before invoking (params validated at gate, not guessed)
3. ✅ Passes specific, non-boilerplate `--intent`
4. ✅ Designs for summary-shaped outputs (≤500 tokens default)
5. ✅ Never references file paths, credentials, or raw SQL in skill body
6. ✅ References capabilities by name, not by implementation detail

---

## 10. The Learning Loop — log-driven, primitive-deep

```
agent runs raw ops                     (exploration)
  → kernel logs every op with intent
  → agent queries the audit mirror     (deterministic views: op_frequency, shared_subsequences)
  → proposes routine                   (harness writes the file)
  → draft (emits manifest) → prove (proves fingerprint) → ship with stats evidence
  → future work calls the routine      (exploitation)
```

- The audit mirror is the training data: repeated intent patterns + frequent op bigrams → candidates
- **Search-first enforced:** `routine draft` shows near-duplicates; reuse or justify with `--reason`
- Failures are teaching data: `policy.deny` patterns = what the agent doesn't yet know how to do right
- Consolidation uses `shared_subsequences` view: common primitive n-grams across routines → kernel proposes extracting a common sub-routine, deterministically

---

## 11. Consolidation — the counter-force

Accumulation is automatic; consolidation must be scheduled:

```
maintenance window (Sun 03:00)
  → kernel builds consolidation report   (fingerprint similarity, dead, failing, overlap)
  → harness drafts merges                (LLM labor)
  → validate + test candidates           (gate)
  → human approves                       (gate)
  → apply: retire originals with provenance pointers, never delete
```

- Merges are links: `consolidated_from: [a@12, b@7]`; rollback of a bad merge = un-retire
- Sessions are budgeted (`max_session_minutes`, `max_proposals_per_session`) — human review stays human-sized
- **The registry stays a library because subtraction runs on schedule.**

---

## 12. Execution — The Sandbox

Routines execute in a jailed subprocess:

- **Network: none** — all HTTP goes through `ctx.api` → kernel egress
- **Filesystem: read-only workspace + tmpfs scratch**
- **No subprocess, no os, no raw sqlite3** — AST flags at draft (lint), jail blocks at runtime (enforcement)
- **Socket to the kernel is the only capability** — computation free, authority zero
- Tiers: `bwrap --unshare-net` (Linux) · Podman `--network none` (portable) · gVisor/Firecracker (multi-tenant)
- **Syscall filter: seccomp-bpf** inside the jail. Even if Python escapes AST detection via `exec()`/`eval()`/dynamic import, the process cannot open sockets, fork, or write outside allowed paths. The jail's syscall permissions ARE the source of truth; the AST deny-list is derived from them, not maintained separately.
- Runtime budgets enforced: op #51 aborts (`limit_exceeded` event), watchdog kills past duration, results truncated with `truncated: true`
- **v2 path: WASM routines.** WASM has no `exec`, no `eval`, no dynamic imports, no filesystem without explicit grants. Capability model is structural. Python routines become the power-user escape hatch; WASM becomes the default.

---

## 13. Audit & Provenance

One parent event + one event per leaf op, linked by `caused_by`:

```json
{
  "event": "routine.run",
  "routine": "refund_and_archive",
  "version": 17,
  "code_hash": "sha256:9d2e...",
  "manifest_hash": "sha256:a1b2...",
  "env": "prod",
  "stage": "live",
  "agent": "agt_7f3k",
  "principal": "user:alice",
  "triggered_by": "run",
  "intent": "refund ORD-8842",
  "intent_chain": ["process refund queue", "refund_and_archive", "..."],
  "params": { "order_id": "ORD-8842" },
  "outcome": "success",
  "ops": 4,
  "duration_ms": 640
}
```

`capcli sys audit trace <op-id>` walks any leaf effect up through routine → session goal. Every corrupted row answers: which routine, which version, which world, which agent, why.

---

## 14. Git Integration — Review for Free

Routines are git-tracked Python:

- **Agent-written code gets native code review** — a PR is a routine diff; promotion to prod = merge
- **Environments are worktrees** — born in dev, proven in sim, merged to prod
- `env doctor` flags unmerged routines running in prod — drift made loud
- Governance overrides are commits too — exceptions reviewed like code

---

## 15. Commands

```bash
capcli routine draft <name> [--reason]
capcli routine prove <name> [-p k=v] [--env sim]
capcli routine ship <name> --to reviewed|pinned [--env X] --reason "..."
capcli routine sweep [--since 30d]
capcli routine stats <name> [--deep]
capcli routine rollback <name> --to-version N
capcli routine retire <name> [--reason]
capcli rule show --type governance                  # effective limits
capcli rule validate                                # compile all layers
capcli sys audit sample --capability X
capcli sys audit trace <op-id>
```

---

## 16. Anti-Decisions

- **No YAML procedures.** YAML declares; Python executes. Control flow inside YAML is the smell we rejected
- **No module imports for authority.** `ctx` injection only — the jail's sole door is the socket
- **No self-promotion.** Trust ascends through human/CI gates; evidence is agent work, authority is human work
- **No event-driven cores.** No subscriptions, no callbacks, no reactive streams inside routines — events trigger, they don't flow through
- **No silent edits.** Hash-pinned versions; change = new version
- **No immortal routines.** Decay + consolidation are mandatory rhythms
- **No `bulk_update()`-style conveniences.** Composition over raw primitives; convenience APIs become an accidental ORM
- **No ungoverned shape.** LOC/tokens/params/ops caps enforced at five gates; exceptions as reviewable commits
- **No routine-level-only analysis.** Maintenance operates at primitive depth via manifests and fingerprints
- **No deletion.** Retirement with provenance pointers; the history graph only grows
- **No synthetic learning.** Routines are born from audited primitive repetition, not generated from user intent. The harness observes the audit mirror; the kernel gates registration.
- **No pre-selected API imports.** Sync pulls the full catalog. Activation gates what's callable. The library is permanent; the active shelf is earned.

---

## 17. Invariants

1. Every routine is validated (AST + policy + governance shape) before it can execute, and sandboxed while it does
2. Every effect inside a routine crosses the kernel gate — no exceptions, no depth discount
3. Every routine version is hash-pinned; replay verifies the hash; promotion paths are recorded
4. Validate extracts the primitive manifest; runtime fingerprint proves or contradicts it
5. Trust moves up through human/CI gates only; decay and consolidation move it down on schedule
6. Routines are event-driven at the edges and imperative at the core — stories, not listeners
7. Every run carries the causal spine: env, stage, agent, principal, intent chain, caused_by
8. The registry consolidates, never duplicates; subtracts on schedule, never deletes
9. What routines may *do* is policy; what they may *be* is governance — two files, zero overlap
10. Manifest drift at runtime is a governed anomaly, never silently accepted

---

## The One-Liner

> **capcli-routine: the agent's procedural memory — atoms composed into molecules, born from raw ops, shaped by governance, proven in sim by their own primitives, promoted by evidence and human authority, consolidated on schedule, and governed at every leaf like anything else that touches the world.**