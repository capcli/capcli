# capcli.architecture.md *(master — final v2, all decisions integrated)*

> **Update v2.1:** Added §12.5 Harness Skill Boundary (2026-09-12)
> **capcli — a capability kernel for agent workspaces: SQLite as the world, policy as physics, every effect audited, every capability earned.**

---

## 1. Core Philosophy

capcli is not an agent framework, not an ORM, not a wrapper. It is a **kernel**: a governed boundary through which an agent harness (Claude Code, Codex, Hermes, OpenClaw, custom) affects and observes a workspace.

Three convictions:

1. **The agent is never trusted.** Enforcement lives in physics and in the kernel — never in prompts, never in "please don't."
2. **The harness is replaceable.** capcli exposes a governed interface; it doesn't care who is reasoning above it.
3. **Rules don't constrain. Physics does.** A policy only works if the agent has no physical path around it.
4. **Intent precedes infrastructure.** The world is built for a goal. Schema, policy, and governance are consequences of intent — never prerequisites.

---

## 2. Mental Model

Three distinct stores — never conflated:

| Store | Contains | Format |
|---|---|---|
| **State** — what exists | world data | SQLite (`workspace.db`) |
| **Procedure** — what the agent learned to do | routines, capabilities | Python + YAML config |
| **Experience** — what happened | append-only event stream | JSONL audit log |

**YAML for what is declared. Python for what is executed. JSONL for what happened.**

YAML is a config format, not a procedure format. The moment a representation needs sequencing, branching, retries, or composition — it becomes code. We do not invent a programming language inside YAML.

---

## 3. Architecture

```
AGENT HARNESS  (Claude Code / Codex / Hermes / OpenClaw / custom)
   │  intent, reasoning, learning, consolidation
   ▼
CAPCLI KERNEL ──── policy.yaml + governance.yaml ──── audit/ (append-only)
   │
   ├── db.*        → SQLite SSOT    (C-level authorizer + AST gate)
   ├── routine.*   → Python sandbox (jail: net-none, socket-only)
   ├── api.*       → HTTP egress    (kernel-owned secrets, injected at boundary)
   ├── schedule.*  → time           (daemon-owned cron)
   ├── watch.*     → inbound events (webhooks/poll → capability dispatch)
   ├── serve.*     → inbound calls  (pinned routines as governed endpoints)
   └── notify/ask  → humans         (channels, quiet hours, fail-closed waits)
```

Three effect channels going out, four hands coming in. One gate, one audit stream, one trust ladder.

The agent cannot reach SQLite or the network directly:
- `workspace.db` owned by the daemon user, `chmod 600`
- Credentials never in the agent's env — memory-decrypted, injected at egress
- All agent access flows through the kernel (socket or CLI invocation)

---

## 4. Workspace Structure

```
workspace/
├── schema.yaml              # declarative structure (version-locked)
├── policy.yaml              # behavioral permission (default: deny)
├── governance.yaml          # structural limits (sizes, counts, cadence)
├── apis/
│   └── stripe.yaml          # curated OpenAPI import → lean capabilities
├── routines/
│   ├── find_related.py      # agent-composed procedures
│   └── archive_temp.py
├── workspace.db             # SSOT — daemon-owned, 600, NOT git-tracked
├── world.sql                # deterministic dump — git-tracked, recoverable
└── audit/                   # event stream — append-only JSONL, committed via backup
    └── 2026-XX-XX.jsonl
```

---

## 5. SQLite as SSOT

SQLite is not "the database behind the app." It is the persistent world-state.

- WAL mode, periodic snapshots, audit-log replay for reconstruction
- `state(t) = fold(events[0..t])` — the audit log is the replay source
- Schema lives in `schema.yaml`, version-locked to policy
- Single-writer serialization is the multi-agent arbiter

---

## 6. Two-Layer Policy + Governance

### Layer 1: C-level `sqlite3_set_authorizer`
Engine-enforced at prepare-time. Bypass-proof even if TS code has bugs. Bugs fail toward denial. Granularity: action × table × column.

### Layer 2: SQL AST check
Evaluated before prepare. Full semantic view — WHERE clauses, LIMIT, patterns, values, intent presence. Granularity: statement shape, blast radius, parameters.

**The asymmetry:** authorizer = default-deny floor (can't be bypassed). AST = expressive ceiling. Bypass requires both to fail.

### Policy vs Governance

| File | Governs | Examples |
|---|---|---|
| **policy.yaml** | What capabilities may *do* (behavior) | row caps, write denials, spend limits, trust requirements, intent mandates |
| **governance.yaml** | What capabilities may *be* (structure) | LOC/tokens per file, max routines, ops per run, maintenance cadence |

Both compiled at boot. Bad config → kernel refuses to serve. No degraded mode.

---

## 7. Capabilities — the unifying concept

Everything the agent can effect on the world is a **capability**:

```
capability
├── db op      → SQL through authorizer + AST
├── routine    → composed Python, trust-leveled
├── api verb   → OpenAPI-imported, kernel-owned secrets
└── view       → read-only lens, principal-scoped
```

One registry, one `search` surface, one trust ladder, one audit format. The agent doesn't know or care which channel an invocation uses.

Registry fronted by **progressive disclosure**: at scale the agent gets one `cap search` meta-tool, not a dump of every capability. Base context stays constant whether there are 10 or 10,000.

---

## 8. Raw SQL & Bulk Operations

Raw SQL is **allowed and is the default primitive**. The kernel exists so raw SQL is safe, not to forbid it.

Rules:
- **Parameterized only** — API enforces bound params; string interpolation rejected structurally
- **Reads: nearly free** — authorizer scope + `max_limit`
- **Writes: capped** — `require_where` + `require_limit` + explicit transaction
- **DDL: gated** — `require_trust: reviewed`
- **ATTACH / PRAGMA writes: never**

Every raw write runs inside an explicit transaction.

### Bulk operations
Agents batch for token economy. Give them fewer *agent* calls, many *kernel* operations:
- `require_limit` on UPDATE/DELETE forces chunking
- Agent writes the loop in Python; kernel enforces sane `max_limit` per chunk
- Pre-flight `db query --count` before any mass op — estimate vs. policy cap
- Each chunk = own txn, own audit event, resumable from checkpoint

Raw SQL is the **exploration layer**. Routines are the **exploitation layer**. Kill raw SQL and the learning loop never starts.

---

## 9. Routines — the procedure layer

Routines are Python. Not YAML-with-code — actual Python files executing in a jailed sandbox.

```python
@routine(name="refund_and_archive", trust="draft", idempotent=False)
def refund_and_archive(ctx, params):
    order_id: Param[str] = params["order_id"]
    order = ctx.api.call("stripe.get_charge", {"charge_id": order_id})
    with ctx.db.txn():
        ctx.db.execute("UPDATE entities SET status='refunded' WHERE ref=:r LIMIT 1",
                       {"r": order_id}, intent=f"mark {order_id} refunded")
    return {"status": "refunded"}
```

Design rules:
- **`ctx` injection, not module imports** — zero import surface to police
- **Kernel validates via AST before execution** — rejects subprocess, raw sqlite3, file writes outside workspace
- **Sandbox isolates computation, never authority** — every `ctx.db.*` / `ctx.api.*` call round-trips through the kernel gate
- **Code-hash pinned** — every routine recorded with `version` + `sha256`; hash mismatch on replay → refuse
- **Governance shape limits** — LOC, tokens, max_ops_per_run, max_duration enforced at five gates

Lifecycle: `draft → prove → ship (reviewed → pinned) → retire`, with `sweep`, `stats`, `rollback`. The harness proposes consolidation; the kernel governs registration.

**Data never transits the model:** large results stay in routine scope; only computed summaries cross back to the LLM. Kills token cost and PII leakage into context.

---

## 10. Primitives: Manifests & Fingerprints

A routine is a story, but maintenance reads it word by word.

### Declared Manifest (Static)
At `validate` time, the AST extracts the primitive manifest — the exact sequence of `ctx.db.*` and `ctx.api.*` calls the routine declares it will make. Stored with the version.

### Runtime Fingerprint (Dynamic)
Aggregated from the audit mirror. The actual sequence of leaf ops that executed.

### Why this matters
- **Consolidation:** near-duplicate detection operates on fingerprint similarity (identical primitive sequences), not just code text similarity
- **Regression:** version 17→18 adding a new leaf op is flagged automatically during promotion review
- **Cost attribution:** p95 duration and spend per leaf → optimization targets
- **Drift detection:** runtime fingerprint diverges from declared manifest → `governance.anomaly` event

Audit mirror views power this deterministically: `routine_fingerprints`, `primitive_failures`, `primitive_cost`, `shared_subsequences`. Pure GROUP BYs. No LLM in the kernel.

---

## 11. External APIs — same gate, different channel

External effects are governed identically — but HTTP is not SQL:

| Property | SQL | External API |
|---|---|---|
| Enforcement point | inside SQLite (authorizer) | egress boundary only |
| Transactions | real | none — no rollback |
| Retry | safe (idempotent) | double-spend risk |
| Replay | deterministic | re-execution ≠ same result |

Therefore:
- **Pre-call policy only** — once the request leaves, it's gone. External writes gated stricter than SQL writes
- **No auto-retry on non-idempotent calls.** Retry only with kernel-generated idempotency key persisted *before* first attempt
- **Replay records mark external effects `replay: manual`** — never auto-replayed

### Lean OpenAPI import
Raw specs are monsters. Import is curated, opt-in, default-deny. Unlisted endpoints don't exist. Kernel injects secrets at egress; agent never sees tokens.

---

## 12. The Hands

| Hand | Direction | Gives the agent |
|---|---|---|
| `db` | world-state | raw SQL through the gate |
| `api` | out | external services, kernel-held secrets |
| `schedule` | time → agent | persistence across sessions |
| `watch` | world → agent (async) | reactions to external events |
| `serve` | world → agent (sync) | governed endpoints + OpenAPI |
| `notify`/`ask` | agent → humans | voice, and the blocking question |

The kernel never infers, never reasons, never does LLM work — it matches, dispatches, delivers, and logs. Intelligence is the harness's job; mechanics is capcli's.

### 12.5 Harness Skill Boundary

capcli does **not** manage, store, validate, or govern harness skills (SKILL.md files).
Skills live in the harness layer above; routines live in capcli. The boundary is the
capability registry — clean, auditable, intentionally dumb.

```
HARNESS SKILL (SKILL.md)          CAPCLI KERNEL
   │                                  │
   │  "use capcli run refund_archive" │
   ├─────────────────────────────────►│  capcli search / inspect / run
   │                                  │  ↓ gate ↓ audit
   │  summary result (≤500 tokens)    │  routine executes in sandbox
   │◄─────────────────────────────────┤
   │                                  │
```

- Skills reference capabilities via `capcli search` and `capcli run`. Never raw SQL.
- capcli has zero visibility into skill content, markdown structure, or agent reasoning.
- Skill-origin propagation is opt-in via `identity.skill_origin` in policy.yaml.
- **Anti-decision addition (§21):** No skill storage in the kernel. No SKILL.md parsing.
  No semantic analysis of harness instructions. Skills are the mind's business;
  capcli is the nervous system.

---

## 13. Trust Ladder × Environment Axis

Two axes of one ladder:

```
draft ──> reviewed ──> pinned
  │          │            │
 dev    +  sim         + prod (merge + sign-off)
```

- **Overlays, not separate policies** — one engine, parameterized
- Draft = agent-learned, unproven: tight caps, full audit
- Reviewed = human/CI sign-off granted
- Pinned = proven track record; relaxed caps, summary audit
- **Self-promotion is impossible** — promotion is a human/CI-gated command
- Decay: unused 30 days → auto-retire; success rate <70% → auto-rollback

Environments are git worktrees. Promotion travels dev → sim → prod, and reaches prod only through merge + pin sign-off.

---

## 14. Multi-Agent Identity & Intent

### Identity hierarchy
```
principal (user:alice) → agent (agt_7f3k) → session (ses_a9) → op (op_001)
```
- IDs are kernel-issued, stored in `workspace.db`, bound to socket credentials (`SO_PEERCRED`). Never self-declared.
- Revocation is instant.
- Cross-agent routine calls require callee ≥ `reviewed`.

### Intent chain
Writes require intent; the chain inherits downward: `session goal → routine intent → op intent`.
- Leaf ops inherit from routine, routines from session; every audit event records the full chain
- Anti-junk: min length, boilerplate blacklist, deny by default
- `--intent` = purpose; `--reason` = justification (only for threshold crossings)

### Coordination
Agents coordinate through the world, not direct chat:
- **Claims:** lease-based locks with TTL (`capcli db lock`)
- **Events:** agents watch each other's effects via `sys audit tail`
- **Handoffs:** world-state transitions visible to all

---

## 15. The Learning Loop & Consolidation

```
agent runs raw ops                     (exploration)
  → kernel logs every op with intent
  → agent queries the audit mirror     (deterministic views)
  → proposes routine                   (harness writes the file)
  → draft → prove (audit-sampled real params) → ship with stats evidence
  → future work calls the routine      (exploitation)
```

Accumulation is automatic. Consolidation must be scheduled:
```
maintenance window (Sun 03:00)
  → kernel builds sweep report (fingerprint similarity, dead, failing)
  → harness drafts merges (LLM labor)
  → draft + prove candidates (gate)
  → human approves (gate)
  → apply: retire originals with provenance pointers, never delete
```

---

## 16. Recovery — where the gate can't reach

The harness has native fs/exec — capcli doesn't pretend to gate them. Instead: recovery.

- **Auto-commit:** interval + event-triggered commits of `world.sql` (deterministic DB dump), audit logs, configs → pushed to git remote
- **Audit in git:** append-only JSONL in version control = tamper-evidence for free
- **Restore:** `capcli sys recover <commit>` restores full world-state from history
- Worst case (harness wipes everything): `git clone` + `sys recover` → world restored, audit spine intact

Destruction becomes a reversible event.

---

## 17. Replay — Event Sourcing

The audit log is the replay source:

```yaml
replay_record:
  routine: archive_temp
  version: 17
  code_hash: sha256:abc123
  inputs: {...}
  operations: [db.exec, api.call, ...]
```

Three invariants:
1. **Replay re-applies *current* policy, not historical policy** — a demoted routine doesn't resurrect old permissions
2. **Code-hash verified** — edited file ≠ replayable record
3. **External effects never auto-replayed** — manual only

Idempotency keys on every write make retries safe. `result_hash` per event detects drift.

---

## 18. CLI Surface

Shape: `capcli <noun> <verb> [target] [--flags]` — no exceptions.
Universal flags on all mutating verbs: `--dry-run`, `--json`, `--intent "<why>"`, `--as <principal>`.

8 nouns. Zero redundancy.

-   **run** · search · inspect (hot path)
-   **db** · query · exec · lock · unlock · snapshot · restore · dump
-   **routine** · draft · prove · ship · sweep · stats · rollback · retire
-   **bind** · cron · webhook · endpoint · list · pause · resume · remove · keys
-   **ping** · notify · ask · list · resolve · expire
-   **rule** · show · diff · apply · validate (owns schema + policy + governance)
-   **env** · new · use · list · inspect · doctor · merge · remove
-   **sys** · audit (tail/trace/query/replay) · agent · doctor · backup · recover · exec

Exit codes are law: `0` ok · `2` policy-denied · `3` validation · `4` runtime · `5` audit-write-failed.

`sys audit trace --explain` is the single learning signal for denials.

---

## 19. Security Model

**The capcli gate is only real if there's no other door.**

### Credentials: grades of "unavailable"
Kernel injects `Authorization` at egress. Tokens never in agent env, never in context, never in audit output. Memory-decrypted at boot.

### Isolation tiers
1. **Credentials isolation + file perms** — the shippable minimum
2. **Egress allowlist** — host firewall or daemon-embedded proxy
3. **Network jail** — `bwrap --unshare-net` / `docker --network none` for agent subprocesses
4. **gVisor / Firecracker** — multi-tenant, untrusted agents

`sys doctor` refuses to serve if boundaries are broken: shared user, wrong DB perms, missing jail. Misconfiguration must be loud.

---

## 20. Fail-Closed Contract

- No valid policy → **no boot**
- Schema/policy version mismatch → **no boot**
- Write can't be audited → **it doesn't run**
- Scoped capability without principal → **refused**
- Ambiguous read/write classification → **errs toward write**
- Headless/crashed approval → **denied**

---

## 21. Anti-Decisions (what capcli refuses to be)

- **No ORM.** Drizzle/Prisma/SQLAlchemy syntax is hallucination bait for LLMs, and ORMs compile to SQL anyway — a middleman before the same authorizer check. Raw SQL is universal.
- **No custom query-builder APIs.** `bulk_update()`, `cursor()` etc. = accidental ORM. Python loops + `require_limit` policy cover bulk safely.
- **No CLI write-path for config.** Policy edited in files by humans, validated by kernel.
- **No `default: allow`.** Ever. Convenience here converts the kernel into a wrapper.
- **No interactive modes.** The kernel serves agents and scripts; approval prompts belong in the harness above.
- **No YAML procedures.** YAML declares; Python executes; JSONL records.
- **No agent-to-agent chat channels.** Agents coordinate through the world: claims, events, handoffs.
- **No LLM in the kernel.** Setup is agent intelligence, execution is kernel mechanics, authority is human.
- **No kernel-generated worlds.** The harness authors schema.yaml from user intent; the kernel gates application. capcli never infers structure from natural language.
- **No onboarding events.** The audit records real ops, effects, and denials. No synthetic `onboarding.*` event types. Intent is a field on an op, not a standalone event.
- **No deletion.** Retirement with provenance pointers; rollback un-retires; history only grows.

---

## 22. Vocabulary

| Term | Meaning |
|---|---|
| **Op** | atomic unit — one capability call |
| **Effect** | the world change an op produces |
| **Event** | the audit record — exists even when the op is denied |
| **Routine** | agent-learned composition of ops (Python, hash-pinned) |
| **Capability** | anything exposed to the agent: db op, routine, api verb, view |
| **Rule** | static configuration: schema (shape), policy (behavior), governance (limits) |
| **Bind** | inbound trigger: cron, webhook, served endpoint |
| **Ping** | outbound human IO: notify, ask |
| **Trust** | draft → reviewed → pinned |
| **Kernel** | the capcli process — the only door in the wall |

Eight words, zero overlap. If a ninth is needed, one of these was wrong.

---

## 23. The One-Liner

> **capcli — a capability kernel for agent workspaces: SQLite as the world, policy as physics, every effect audited, every capability earned. The harness is the mind; capcli is the nervous system — and if the mind goes rogue, git history puts the world back.**