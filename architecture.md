# capcli.architecture.md *(master — final v2, all decisions integrated)*

> **Update v2.1:** Added §12.5 Harness Skill Boundary (2026-09-12)
> **capcli — a capability kernel for agent workspaces: SQLite as the world, policy as physics, every effect audited, every capability earned.**

---

## 1. Core Philosophy

capcli is not an agent framework, not an ORM, not a wrapper. It is a **policy gateway**: a governed boundary through which an agent harness (Claude Code, Codex, Hermes, OpenClaw, custom) affects and observes a workspace. The word "gateway" is deliberate — it sits between the agent and the world, checks, forwards, and logs. It does not reason, schedule intelligence, or absorb every concern. If a feature requires capcli to *reason*, it belongs in the harness.

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

API verbs follow the same surface. Sync pulls the full catalog; dormant verbs are searchable but not callable. Search resolution is five stages — exact → prefix → fuzzy → semantic → did-you-mean — ranked by relevance. Every search query logged as `event: capability.search` with query, filters, results, and invocation. Search gaps (searched but never invoked) surface as consolidation signals for both routines and API verbs.

### Search Ceiling & Harness-Side Intelligence
"No LLM in the kernel" applies to **enforcement and execution**. It does not mean search must be keyword-only forever. But semantic intelligence belongs in the harness, not the gate.

- **Kernel search (deterministic):** Exact match → prefix match → structured filters. `capcli search "refund" --trust pinned --env prod --max-ops 10`. Filters are deterministic. Kernel returns candidates.
- **Harness search (semantic):** The harness computes embeddings for routine descriptions, stores them in a side table (`_capability_embeddings`). `capcli search --semantic "handle customer refunds"` queries this table. The kernel serves the vectors; the harness ranks them.
- **Search analytics:** Every `search` query logged as `event: capability.search` with query text, filters used, results returned, and which capability was ultimately invoked. Audit mirror reveals search gaps: "agents search 'invoice' 20 times but never invoke." This is a consolidation signal.
- **Principle:** "No LLM in enforcement. LLM-assisted discovery is the harness's job, with kernel-provided indexes." The kernel is a lookup table with fast filters. The harness is the ranking engine.

At 300 routines (the hard cap), keyword search returns noise. Structured filters narrow the set. Semantic ranking orders it. The kernel owns the first two. The harness owns the third.

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

## 11. External APIs — full catalog, gradual activation

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

### Sync — import everything

APIs update constantly. Import is not a one-shot file upload. It is a scheduled URL sync.

```bash
capcli api sync stripe \
  --from https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.json \
  --interval 7d
```

The kernel fetches the raw OpenAPI spec, parses ALL endpoints, and compiles `apis/<provider>.yaml`. Every verb enters as `state: dormant`. No `--pick`. No pre-selection. Import is free; activation is gated.

The harness never reads the raw spec. The kernel fetches, parses, compiles.

### The catalog model

Every imported verb has a state:

```
synced (dormant) ──> active ──> retired
       │                │            │
  exists in catalog  callable via   provenance kept
  searchable with    ctx.api.call   rollback un-retires
  --include-dormant
  NOT callable
```

Additionally: `deprecated` — upstream removed it, loud state, never silent deletion.

**Dormant ≠ invisible.** Dormant = exists, searchable, inspectable, but not callable. The agent can find it, read its params, propose activation — but can't call it.

**Dormant never expires.** Only active verbs decay. The full surface is permanent. The active surface is earned.

### Regular sync

Sync is scheduled, not one-shot. Every `sync_interval`:
1. Kernel fetches URL
2. Diffs against current catalog by `spec_hash`
3. New endpoints → added as `state: dormant`
4. Removed endpoints → marked `state: deprecated` (never deleted)
5. Changed params/paths → version bump, diff recorded
6. Audit event: `event: api.sync` with added/removed/changed counts

### Activation — the gate

```bash
capcli api activate stripe.refund_charge \
  --intent "refund workflow needs charge refund capability"
```

Kernel validates the verb exists, checks governance caps (`max_active_per_provider`), activates at `trust: draft`, records the event. The verb becomes callable.

Activation is the gate, not import. Same law as routines: the file exists, but it can't run until proven and shipped.

### Prove, ship, live, retire

Same lifecycle as routines. Activated verbs prove in sim (sandbox `base_url` overlay), ship by human gate, live with quota tracking, decay on schedule, retire with provenance.

### Lean catalog format

`apis/<provider>.yaml` is kernel-compiled, not hand-authored:

```yaml
provider: stripe
version: 3
source_url: https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.json
spec_hash: sha256:a4f2...
synced_at: "2026-09-12T10:00:00Z"
sync_interval: 7d
auth:
  type: bearer
  secret_ref: STRIPE_SECRET_KEY        # kernel-held, never in env/context

capabilities:
  get_charge:
    method: GET
    path: /charges/{id}
    params: { id: { type: string, required: true } }
    idempotent: true
    cost_class: read
    state: dormant
    trust: draft
    description: "Retrieve a single charge by ID"
  # ... all other verbs ...
```

### Live quota tracking

Static spend caps (`per_day_usd`) are the floor. External systems return **dynamic** remaining quota in response headers (`X-RateLimit-Remaining`, `Retry-After`). The kernel:
1. **Extracts** declared headers from every API response (deterministic string match, no LLM)
2. **Stores** live state in `_api_quota` (system table, kernel-written, agent-readable)
3. **Enforces pre-call**: remaining ≤ `deny_at_remaining` → exit 2 *before* egress, not 429 after
4. **Shows in `inspect`**: agent sees live remaining, reset time, and budget status before invoking
5. **Scopes per env**: sim quota and prod quota are independent rows; rehearsal never burns prod limits
6. **Falls back**: providers without standard headers get kernel-counted sliding windows

A 429 is a design failure, not a runtime surprise. The gate denies before the call, not after it.

### Search gaps as API signals

```bash
capcli search gaps --since 7d
```

Searched but never invoked = missing capability. The kernel surfaces it. The harness proposes activation. The human approves. Same consolidation signal as routines.

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

> **Intent is audit metadata, not a security gate.**
> A sufficiently motivated or confused agent can generate syntactically valid, semantically hollow intents.
> The kernel verifies the *shape* of the intent (length, blacklist). It cannot verify the *truth* of the intent.
> Actual enforcement comes from what the kernel *can* physically verify: table, column, row count, blast radius, trust level, env.
>
> Implementation:
> - `--intent` remains mandatory for writes (documentation value is real).
> - Every audit event records an `intent_quality` heuristic: word overlap with SQL targets, parameter references, specificity score.
> - Low quality → audit flag (`intent_quality: low`), not denial.
> - High-stakes writes (prod, >100 rows, external API) additionally require `--reason` routed through a human review gate.
> - The human verifies the why. The kernel verifies the what.
>
> This prevents intent from becoming security theater while preserving its value as a causal spine for learning and audit.

- Leaf ops inherit from routine, routines from session; every audit event records the full chain
- Anti-junk: min length, boilerplate blacklist, deny by default
- `--intent` = purpose; `--reason` = justification (only for threshold crossings)

### Coordination
Agents coordinate through the world, not direct chat:
- **Claims:** lease-based locks with TTL (`capcli db lock`)
- **Events:** agents watch each other's effects via `sys audit tail`
- **Handoffs:** world-state transitions visible to all

### Multi-Agent Scope (v1 vs v2)
capcli v1 is **single-agent with multi-principal**. The identity hierarchy supports multiple humans overseeing one agent. True multi-agent (multiple concurrent agents writing to the same world) is v2.

v1 constraints:
- **Concurrency limit:** Governance `max_concurrent_agents: 1`. Second agent attempting simultaneous write access receives exit 2 with message: "concurrent agents not supported in v1. serialize through single agent or upgrade."
- **Claims are advisory, not mandatory.** SQLite serializes writers natively via `BEGIN IMMEDIATE`. Claims prevent logical conflicts, not physical races.
- **No dependency graph yet.** Cross-agent routine calls work but impact analysis (retiring Y breaks X→Y→Z) is manual.
- **Polling only.** `sys audit tail` is polling. No pub/sub event streaming until v2.

v2 requirements (not implemented):
- Replace lease claims with `BEGIN IMMEDIATE` transaction isolation as primary writer serialization.
- Add event streaming: `capcli sys audit stream --follow --capability X` via Unix socket. Agents subscribe, don't poll.
- Add dependency tracking: `_routine_deps` table. `routine retire Y` checks dependents and warns.
- Add write throughput monitoring: `sys doctor` reports lock contention. Average write wait >50ms → governance suggests splitting workloads across environments.

Don't let users discover multi-agent gaps through race conditions. Scope it explicitly. Fail loud, not corrupt.

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

Git is the developer experience. It is NOT a backup system. `git push --force` overwrites history. Anyone with push access can rewrite it. Repos grow linearly (~35K commits/year at 15-min intervals). Tamper-evidence requires an append-only store, not a mutable VCS.

- **Auto-commit:** interval + event-triggered commits of `world.sql`, audit logs, configs → pushed to git remote. This is the DX layer.
- **Secondary backup target:** S3/GCS/B2 with object versioning enabled. `sys backup --push` pushes to git AND object storage. Object storage is append-only by design. This is the recovery guarantee.
- **Hash chain verification:** Each JSONL audit line includes `prev_hash: sha256:<previous_line_hash>`. Tampering with any line breaks the chain. Governance `hash_chain_verify: "0 4 * * *"` validates daily. This is real tamper-evidence, independent of git history.
- **Backup verification:** `sys doctor` verifies the last pushed backup by downloading and comparing `world.sql` hash. `backup.last_verified_at` tracked. Stale >24h → alarm.
- **Recovery indexes:** `capcli sys recover --list` shows last N recovery points with timestamps, schema versions, audit counts. Human picks by time, not commit hash.
- **Git retention policy:** Governance `backup.git_max_age_days: 90`. Older commits squashed/pruned from working repo. Full history lives in object storage. Git stays lean; archive stays complete.
- **Restore:** `capcli sys recover <commit|timestamp>` restores full world-state.
- Worst case (harness wipes everything): `git clone` + `sys recover` OR pull from object storage → world restored, audit spine intact, hash chain verified.

Destruction becomes a reversible event. But reversibility requires two independent stores, not one mutable VCS.

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

9 nouns. Zero redundancy.

-   **run** · search · inspect (hot path)
-   **api** · sync · diff · catalog · activate · prove · ship · stats · retire · deactivate · rollback · list
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

### Degraded modes (human-supervised only)
Fail-closed is the default. There is no *automatic* degraded mode. But operators have documented, audited escape hatches:

- **Recovery mode:** `CAPCLI_RECOVERY=1 capcli sys recover`. Loads ONLY schema + audit sink. No policy enforcement, no routines, no serve. Only `db query`, `db dump`, `sys audit tail`, `sys backup`. Requires physical env var. Logged as `event: recovery_mode_entered`.
- **Boot diagnostic:** `capcli sys doctor --boot-check`. Runs all boot validations without starting the daemon. Prints exact failure location. Fixes the circular dependency where the kernel won't start to tell you why it won't start.
- **Config pre-commit:** `capcli rule validate` runs in CI before config reaches the daemon. Catches YAML errors before they kill the service.
- **Audit disk exhaustion:** Reserved audit partition (separate disk or guaranteed tmpfs). If audit write fails, kernel enters read-only mode instead of full denial. Reads continue. Writes queue in memory with 5-minute TTL before hard denial. Gives ops time to fix the disk.

These are break-glass paths. Every use is an audit event. They exist so a config typo doesn't become a 3 AM outage with no recovery path.

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
- **No pre-selected API imports.** `api sync` pulls the full catalog. No `--pick`. Filtering happens at activation, not import.
- **No dormant expiry.** Dormant API verbs never decay. The full surface is permanent; only the active shelf is earned.
- **No hand-authored `apis/*.yaml`.** The kernel compiles the catalog from the OpenAPI spec. The harness proposes; the kernel gates; the human approves.

---

## Implementation Stack

Architecture is binding-agnostic. Implementation choices live in `stack.md`.

Summary: Bun runtime, rusqlite via napi-rs (native C-level authorizer),
node-sql-parser (AST gate), citty (CLI), valibot (config validation),
yaml (YAML parse). 4 npm deps + 1 Rust crate. Everything else is Bun built-in.

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
| **Sync** | scheduled URL pull of an OpenAPI spec → full catalog compilation |
| **Catalog** | the complete set of imported API verbs, all states, permanent |
| **Dormant** | imported, searchable, inspectable, not callable |
| **Activation** | the gate that moves a verb from dormant to callable |

Eight words, zero overlap. If a ninth is needed, one of these was wrong.

---

## 23. The One-Liner

> **capcli — a capability kernel for agent workspaces: SQLite as the world, policy as physics, every effect audited, every capability earned. Sync pulls everything; activation gates what's callable. The harness is the mind; capcli is the nervous system — and if the mind goes rogue, git history puts the world back.**