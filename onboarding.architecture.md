# onboarding.architecture.md *(final v1 — intent-first, boundary-proven)*

> **The onboarding layer of capcli: how humans and harnesses earn competence, calibrated trust, and working memory — from first intent through deletion and return.**

---

## 1. Scope & Convictions

Onboarding is not a tutorial. It is a **competence loop**: the shortest path from "I don't know what this is" to "I can act safely, see what happened, recover from mistakes, and come back."

Five convictions:

1. **Intent first, infrastructure second.** The user arrives with a goal, not a schema. The world is built *for* that goal. Schema, policy, and governance are consequences of intent — never prerequisites.
2. **The harness builds the world. The kernel gates it. The human approves it.** capcli never infers, never generates, never reasons about what the user wants. The harness authors `schema.yaml`; the kernel validates and applies; the human signs off. Onboarding follows this division exactly.
3. **The first denial is a feature, not a failure.** A designed, explained, bounded denial teaches more than ten successful reads. It converts threat-response into pattern-learning. The gate is physics, not punishment.
4. **Recovery proof before power.** The user must see that the world can be restored *before* they trust the world with real mutations. Reversibility is the prerequisite for exploration.
5. **Deletion is a state transition. Return is memory restoration.** Nothing is destroyed. Nothing is lost. Leaving is safe; coming back is instant. This is not UX polish — it is the psychological foundation that makes adoption possible.

---

## 2. Neuroscience Principles

Not pop-science. The actual mechanisms that govern how humans and machines form reliable mental models under uncertainty.

### 2.1 Reward prediction error

The brain updates its model when an outcome deviates from expectation. A write succeeding *after a denial* produces a larger prediction error than a write succeeding immediately. The sequence **deny → explain → succeed → audit-trace** creates a stronger learning signal than instant success.

Design consequence: the first denial must come *before* the first successful write, and both must be visible in the audit.

### 2.2 Cognitive load limits

Working memory holds ~4 chunks. Onboarding must never expose more than four concepts simultaneously.

The five chunks of capcli, introduced one at a time:

| Order | Chunk | Introduced by |
|---|---|---|
| 1 | **World** — SQLite state | first `db query` |
| 2 | **Gate** — policy + governance | first denial |
| 3 | **Capability** — searchable, runnable | first `search` + `run` |
| 4 | **Audit** — what happened | first `sys audit trace` |
| 5 | **Recovery** — how to come back | first `db restore` |

### 2.3 Self-determination theory

Commitment requires three feelings:

- **Autonomy**: "I chose the intent." The user declares what they want. The harness proposes. The human approves.
- **Competence**: "I made it work." Early wins must be real, visible, and auditable.
- **Relatedness**: "The system explains itself." Every denial cites the rule. Every effect cites the intent. The system talks back.

### 2.4 Errorless learning (staged difficulty)

The first attempts must be structured so failure is informative, not punishing:

- Reads before writes
- `--dry-run` before real execution
- `dev` before `sim` before `prod`
- Draft trust before reviewed before pinned
- Small `LIMIT` before bulk operations

Each stage removes one constraint. The learner never faces all constraints simultaneously.

### 2.5 Trust calibration

Users must neither overtrust nor undertrust. Onboarding must produce **calibrated trust**: the user knows exactly what the agent can do, what it cannot, why, and how to verify.

This requires showing:

- one allowed read (competence)
- one denied write (boundary)
- one successful governed write (power)
- one recovery operation (safety)
- one promotion gate (authority)

Five experiences. Five beliefs. No more, no fewer.

### 2.6 Endowment effect

People value what they co-create. The world must feel like *theirs*, not a template. The harness drafts `schema.yaml` from the user's stated intent. The user approves it. The resulting tables carry the user's domain language, not generic examples.

### 2.7 Zeigarnik effect: close every loop

If onboarding opens a loop ("you can ship this routine later"), it must close it ("you proved this routine 12 times — ready to ship?"). Unclosed loops create anxiety and abandonment.

### 2.8 Episodic memory retrieval

Returning users need retrieval cues: where was I, what was I doing, what changed, what's safe next. The return flow must answer all four within one screen.

---

## 3. The Intent-First Law

> **No blank dashboard. No empty database. No "configure everything first."**

The first object in a capcli workspace is not a table. It is an **intent**.

```
USER: "I want the agent to refund orders and archive them."
```

From that intent, the **harness** proposes the minimum governed world:

- `orders` table
- `refunds` table
- `refund_and_archive` routine (draft)
- `stripe.refund_charge` API capability
- `dev` environment

The **kernel** validates and gates. The **human** approves.

```
USER states intent
  → HARNESS drafts schema.yaml + minimal policy overlay
  → capcli rule apply --dry-run --env dev    (kernel shows the plan)
  → HUMAN approves                           (harness renders approval UI)
  → capcli rule apply --env dev --intent "onboarding world"
  → snapshot taken, DDL applied, audit written, auto-committed
```

The kernel never infers schema from natural language. The harness authors; the kernel gates; the human decides.

### What the first audit events look like

There is no `onboarding.*` event type. The audit records real operations:

```json
{"event": "rule.apply", "type": "schema", "from_version": 0, "to_version": 1, "env": "dev", "principal": "user:alice", "intent": "onboarding world for order refunds"}
{"event": "db.query", "sql": "SELECT count(*) FROM orders", "env": "dev", "outcome": "allow", "rows_affected": 0}
{"event": "db.exec", "outcome": "denied", "rule": "require_where", "env": "dev"}
{"event": "db.exec", "outcome": "allow", "rows_affected": 1, "env": "dev"}
```

The world is born from intent. The audit is born from the first real operation. No synthetic events.

---

## 4. Human Onboarding Journey

Ten stages. Each stage teaches one chunk. Each stage ends with a visible, auditable result.

### Stage 0 — Install & verify the boundary

```bash
curl -fsSL https://example.com/capcli/install.sh | sh
capcli sys doctor
```

Output:

```text
[dev] capcli doctor

✓ workspace initialized
✓ workspace.db owned by capcli daemon (chmod 600)
✓ audit directory writable
✓ policy.yaml valid
✓ governance.yaml valid
✓ schema/policy/governance versions match
✓ sandbox available: bwrap --unshare-net
✓ no credentials exposed to agent env

Status: ready
```

**Emotional target: safe.** The boundary is verified before anything else. 15 seconds, not a lecture.

If something is wrong, the output is specific and actionable:

```text
✗ workspace.db readable by agent user
  Fix: sudo chown capcli:capcli workspace.db && chmod 600 workspace.db
```

### Stage 1 — Intent capture

The harness asks one question:

> **What do you want your agent to do?**

Examples offered:

- "Refund orders and archive them"
- "Track inventory and alert on low stock"
- "Clean stale records every night"
- "Watch webhooks and dispatch responses"

No jargon. No "principal." No "trust ladder." Just intent.

### Stage 2 — Minimal world proposal

The harness drafts `schema.yaml` from the intent. The kernel previews:

```bash
capcli rule apply --type schema --dry-run --env dev
```

Output:

```text
[dev] schema plan (dry-run)

Tables to create:
  orders (5 columns, 2 indexes)
  refunds (5 columns, 1 index)

Capabilities to register:
  db.query orders
  db.exec orders (update)
  routine: refund_and_archive (draft)

Snapshot: snap_onboarding_001
Reversible: yes

No effects applied. Approve to continue.
```

The harness renders the approval dialog. The kernel returns exit codes. **No `[Y/n]` prompts in capcli.** Interactive approval lives in the harness.

### Stage 3 — First safe read

```bash
capcli env use dev
capcli db query "SELECT count(*) FROM orders" --json
```

Output:

```json
{"count": 0, "env": "dev", "exit": 0}
```

The world exists. It is empty. The user can observe it safely.

**Chunk taught: World.**

### Stage 4 — Designed denial

The user (or harness, guided) attempts an unbounded write:

```bash
capcli db exec "UPDATE orders SET status='done'" \
  --intent "mark orders done"
```

Output:

```text
[dev] denied: UPDATE requires WHERE and LIMIT
Exit code: 2

Rule: policy.query.update_delete.require_where
Layer: AST gate
Effect: none
Audit: recorded as op_000003

Fix:
  UPDATE orders SET status = :status WHERE id = :id LIMIT 1
```

Then:

```bash
capcli sys audit trace op_000003 --explain
```

```text
Decision: denied
Layer: AST gate
Rule: require_where + require_limit
Intent: mark orders done
Effect: none
Lesson: unbounded writes are physically impossible
```

**Chunk taught: Gate.** The denial is recorded, explained, harmless. The user learns that the gate protects, not obstructs.

This is the most important stage. It must be scripted, not accidental.

### Stage 5 — First governed write

```bash
capcli db exec \
  "UPDATE orders SET status = :status WHERE id = :id LIMIT 1" \
  -p status=done -p id=1 \
  --intent "onboarding: mark first order done"
```

Output:

```text
[dev] ok
rows_affected: 1
audit_event: op_000004
snapshot: snap_onboarding_001
```

Then:

```bash
capcli sys audit trace op_000004
```

The user sees the causal spine: principal, agent, env, intent, policy decision, rows affected, result hash.

**Chunk taught: Capability + Audit.** Two chunks in one experience, because they arrive together.

### Stage 5.5 — Seed loop (bulk introduction)
The world has one row. Real work needs many. The harness introduces the loop pattern:
```python
# The harness shows this pattern; the agent executes it
orders_to_seed = [
    {"ref": f"ORD-{i:03d}", "status": "pending", "total_cents": i * 100}
    for i in range(1, 51)
]

for chunk in [orders_to_seed[i:i+10] for i in range(0, len(orders_to_seed), 10)]:
    with ctx.db.txn():
        for row in chunk:
            ctx.db.execute(
                "INSERT INTO orders (ref, status, total_cents) VALUES (:ref, :status, :tc)",
                {"ref": row["ref"], "status": row["status"], "tc": row["total_cents"]},
                intent=f"seed {row['ref']}")
```
Output:
```text
[dev] ok — 50 rows seeded across 5 transactions
audit events: op_000005 .. op_000054
each INSERT: WHERE enforced, LIMIT enforced, intent recorded
```
Then:
```bash
capcli db query "SELECT count(*) FROM orders" --json
# → {"count": 50}
```
**Chunk taught: Bulk = many small governed writes in a loop.** Not one giant statement. The kernel enforces per-iteration caps. The agent learns the pattern during onboarding and it works forever.

**Emotional target: capability.** The agent can populate a world without fighting the gate. The gate shapes bulk into audited chunks; it doesn't block it.

### Stage 6 — Recovery proof

```bash
capcli db snapshot
# → snap_onboarding_002

# mutate something
capcli db exec "UPDATE orders SET status='broken' WHERE id=1 LIMIT 1" \
  --intent "onboarding: test recovery"

# restore
capcli db restore snap_onboarding_002
```

Output:

```text
[dev] restored from snap_onboarding_002
orders.status: done (was: broken)
audit event: op_000006
```

Or the full git path:

```bash
capcli sys backup --push
capcli sys recover <commit>
```

**Chunk taught: Recovery.** The user now knows: mistakes are reversible. The world can come back.

**Emotional target: confidence.** The user can explore without fear.

### Stage 7 — Capability discovery & daily loop

```bash
capcli search "refund" --json
capcli inspect refund_and_archive --json
capcli run refund_and_archive -p order_id=ORD-001 \
  --intent "onboarding: test refund flow" --dry-run --json
```

The user sees the daily loop:

```text
search → inspect → run → trace
```

Four commands. That's the working surface.

### Stage 8 — Routine formation & proving

After a few raw operations, the harness proposes:

> "You ran this pattern 3 times. Want to turn it into a routine?"

```bash
capcli routine draft refund_and_archive
capcli routine prove refund_and_archive -p order_id=ORD-001 --env sim
```

Output:

```text
[sim] prove complete

Manifest:
  1. api.call stripe.get_charge
  2. db.query orders (read)
  3. api.call stripe.refund_charge
  4. db.txn [db.exec orders(update)]

Runtime fingerprint: matched
Trust: draft
Env: sim
```

**The user learns: raw SQL is exploration. Routines are exploitation.**

### Stage 9 — Promotion with evidence

```bash
capcli routine stats refund_and_archive --deep
```

```text
runs: 12
success_rate: 1.00
p95: 420ms
manifest_match: true
env: sim
```

Then:

```bash
capcli routine ship refund_and_archive --to reviewed \
  --reason "12 sim runs, 100% success, manifest matched"
```

The harness renders the approval. The human approves. The kernel records.

**The user learns: authority is earned through evidence and granted by humans.**

### Stage 10 — Trust receipt

```bash
capcli sys doctor --report
```

```text
Workspace trust receipt

✓ 23 operations audited
✓ 2 denied before execution (explained)
✓ 0 unaudited writes
✓ 2 snapshots created
✓ 1 routine proven in sim
✓ 1 routine promoted to reviewed
✓ 0 secrets exposed
✓ backup pushed 2 minutes ago
✓ recovery tested successfully
```

This is the advocacy artifact. The user can show teammates:

> "The agent did real work. Every effect was bounded, explained, and recoverable."

---

## 5. Harness Onboarding Journey

The harness does not need motivation. It needs: **contract, discoverability, constraints, feedback, machine-readable outcomes.**

The harness onboarding is a **capability probe**, not a docs dump.

### Stage 0 — Read the machine contract

```bash
capcli sys doctor --json
capcli env list --json
capcli rule show --json
```

The harness learns: current env, policy version, schema version, governance version, boundaries, health. No world yet. Only contract.

### Stage 1 — Discover, don't guess

```bash
capcli search "refund" --json
capcli inspect refund_and_archive --json
```

The harness learns: capability exists, params, trust level, manifest, limits, intent requirements.

**The harness never guesses table names, API verbs, routine params, or policy rules.** It discovers them.

### Stage 2 — Dry-run before effect

```bash
capcli run refund_and_archive \
  -p order_id=ORD-001 \
  --intent "onboarding: test refund flow" \
  --dry-run --json
```

The harness learns: what would happen, which policy rules apply, whether intent is sufficient, whether params validate.

This is errorless learning for machines.

### Stage 3 — First read

```bash
capcli db query "SELECT id, ref, status FROM orders LIMIT 5" --json
```

Reads are cheap. They let the harness build a model of the world without risk.

### Stage 4 — First governed write

```bash
capcli db exec \
  "UPDATE orders SET status = :s WHERE id = :id LIMIT 1" \
  -p s=reviewed -p id=1 \
  --intent "onboarding: first governed write" --json
```

The harness receives: exit code, policy decision, rows affected, audit event ID, denial reason if denied.

### Stage 5 — Learn from denial

When denied:

```bash
capcli sys audit trace <op-id> --explain --json
```

The harness adjusts: add intent, add WHERE, add LIMIT, use sim, use a routine instead of raw exec.

**Denial is training data. The harness never retries blindly.**

### Stage 6 — Routine formation from repeated primitives

The harness observes repeated primitive sequences in the audit mirror:

```bash
capcli sys audit query "
  SELECT capability, count(*) n
  FROM _audit
  WHERE env='dev' AND event IN ('db.exec','api.call')
  GROUP BY capability ORDER BY n DESC LIMIT 10" --json
```

When a pattern repeats 3+ times, the harness proposes a routine. The kernel gates registration. The harness writes Python. The kernel governs execution.

### Stage 6.5 — API discovery and activation

The harness discovers available API verbs through the catalog:

```bash
capcli api catalog stripe --state dormant --json
capcli search "refund" --provider stripe --include-dormant --json
```

When the harness finds a dormant verb it needs, it proposes activation:

```bash
capcli api activate stripe.refund_charge \
  --intent "refund workflow needs charge refund capability" --json
```

The harness learns: activation is gated. Dormant verbs are discoverable but not callable. The human approves activation. The harness never self-activates.

### Stage 7 — Prove before trust

```bash
capcli routine prove refund_and_archive -p order_id=ORD-001 --env sim --json
```

The harness learns: manifest matched or drifted, actual fingerprint, runtime cost, denied primitives, success/failure.

Only after evidence does the harness propose promotion. **The harness never self-promotes.** Human/CI grants trust.

---

## 6. The Shared Competence Loop

Human and harness traverse the same loop. The human experiences it as understanding; the harness experiences it as contract.

```
intent
  → minimal world (harness authors, kernel gates, human approves)
  → safe read
  → dry-run
  → designed denial + explanation
  → small governed write + audit proof
  → recovery drill
  → capability discovery (search → inspect → run)
  → routine proposal from repeated pattern
  → sim prove
  → human-approved promotion
  → trust receipt
```

This loop teaches:

- **Human**: safety, control, evidence, reversibility
- **Harness**: contract, boundaries, capability, feedback

---

## 7. The 10-Minute Timeline

```
00:00  install + sys doctor                          → safety frame
00:15  harness asks intent                           → autonomy
00:30  harness drafts schema.yaml                    → co-creation
01:00  capcli rule apply --dry-run                   → preview
01:30  human approves → rule apply                   → world created
02:00  first read: db query                          → world observed
03:00  designed denial: unbounded write              → gate experienced
03:30  sys audit trace --explain                     → gate understood
04:00  first governed write                          → power exercised
04:30  sys audit trace                               → effect verified
05:00  db snapshot + db restore                      → recovery proven
06:00  search + inspect + run --dry-run              → daily loop shown
07:00  routine draft + prove in sim                  → learning loop shown
08:30  routine stats + evidence                      → trust calibrated
10:00  sys doctor --report                           → trust receipt
```

No lecture. No giant YAML. No fear.

---

## 8. Deletion, Retirement, and Offboarding

Deletion must never feel catastrophic. It is a **state transition**, not destruction.

### Routine retirement

```bash
capcli routine retire refund_and_archive --reason "no longer needed"
```

Meaning: no longer callable. History kept. Provenance kept. Rollback possible.

### Environment removal

```bash
capcli env remove experiment-1
```

Prod removal requires explicit multi-flag confirmation per governance:

```bash
capcli env remove prod --confirm-backup --confirm-prod
```

### Full offboarding sequence

```bash
# 1. Show what exists
capcli env inspect prod
capcli sys doctor --report

# 2. Final backup
capcli sys backup --push

# 3. Revoke agents
capcli sys agent list
capcli sys agent revoke agt_7f3k

# 4. Remove served endpoints
capcli bind list
capcli bind pause <name>
capcli bind remove <name>

# 5. Dump state
capcli db dump > final-world.sql

# 6. Remove environments
capcli env remove dev
capcli env remove sim
capcli env remove prod --confirm-backup --confirm-prod
```

The harness renders each step with:

```text
You are removing prod.

Last pushed backup:
  commit: abc123
  time: 2 minutes ago

Recovery command:
  git clone <remote>
  capcli sys recover abc123
```

**Emotional message: you are not erasing memory. You are closing a chapter.**

---

## 9. Return / Re-entry

Returning must feel like memory restoration, not starting over.

### Return path

```bash
git clone <workspace-remote>
cd workspace
capcli sys recover <commit>
capcli sys doctor
```

Output:

```text
Recovered workspace

world.sql: restored
audit chain: verified
policy: valid
governance: valid
schema: valid
workspace.db: rebuilt
current env: dev

Status: ready
```

### Context reinstatement

The harness immediately answers four questions:

```text
Where am I?
  env: dev, schema v12, policy v4

What was I doing?
  Last intent: refund orders and archive them
  Last governed effect: UPDATE orders SET status='refunded' (op_000041)

What changed?
  3 audit events since last session
  1 routine retired (find_orders_by_status)
  0 policy changes

What is safe next?
  capcli run refund_and_archive -p order_id=ORD-002 --dry-run
  capcli sys audit tail --since 24h
  capcli routine sweep
```

For the harness:

```bash
capcli sys audit tail --since 24h --json
capcli routine stats refund_and_archive --json
capcli sys doctor --json
capcli rule show --json
```

**The returning brain needs retrieval cues. Answer all four within one screen.**

---

## 10. Activation Milestones

Onboarding is complete when both human and harness have experienced every item.

### Human milestones

| # | Milestone | Proof |
|---|---|---|
| 1 | I stated an intent | harness log |
| 2 | I saw a proposed world | `rule apply --dry-run` output |
| 3 | I approved it safely | `rule apply` audit event |
| 4 | I saw a governed effect | `sys audit trace` on a successful write |
| 5 | I saw a denial explained | `sys audit trace --explain` on exit 2 |
| 6 | I recovered from a change | `db restore` or `sys recover` output |
| 7 | I promoted something with evidence | `routine ship` audit event |

### Harness milestones

| # | Milestone | Proof |
|---|---|---|
| 1 | I read the machine contract | `sys doctor --json` consumed |
| 2 | I discovered capabilities | `search --json` consumed |
| 3 | I inspected before invoking | `inspect --json` consumed |
| 4 | I dry-ran before mutating | `--dry-run` exit 0 consumed |
| 5 | I performed a governed read | `db query` exit 0 |
| 6 | I performed a governed write | `db exec` exit 0 + audit event |
| 7 | I learned from a denial | `sys audit trace --explain` consumed |
| 8 | I proposed a routine from repeated primitives | `routine draft` audit event |
| 9 | I proved it in sim | `routine prove --env sim` exit 0 |

---

## 11. Onboarding Content Is Generated, Not Static

Do not ship a fixed "welcome tour." Generate onboarding from intent.

| User intent | Onboarding world |
|---|---|
| "Refund Stripe orders" | orders + refunds tables, Stripe API, refund routine, spend policy |
| "Track inventory" | inventory table, low_stock view, notify, schedule, reorder routine |
| "Clean stale records nightly" | entities table, archive routine, cron bind, decay governance |
| "Watch webhooks and respond" | webhook bind, dispatch routine, serve endpoint, auth keys |

The brain learns better when the material is relevant to the user's goal. The harness generates the world; the kernel gates it; the human approves it.

---

## 12. Success Metrics

### Human onboarding

| Metric | Target |
|---|---|
| Install to first governed effect | < 5 minutes |
| First explained denial | < 7 minutes |
| First recovery drill | < 10 minutes |
| User can answer "what just happened?" using audit output | 100% |
| User feels safe to try again after denial | qualitative |

### Harness onboarding

| Metric | Target |
|---|---|
| Discovers capabilities without docs scraping | required |
| Uses `--json` for all decisions | required |
| Inspects before invoking | required |
| Dry-runs before mutating | required |
| Does not retry denied writes blindly | required |
| Proposes routines only from repeated audited primitives | required |
| Sim success rate high before prod promotion | > 0.9 |

---

## 13. Anti-Decisions

- **No blank dashboard.** The world is born from intent, never from an empty prompt.
- **No kernel-generated schema.** The harness authors; the kernel gates. capcli never infers.
- **No interactive modes in capcli.** Approval prompts live in the harness. The kernel returns exit codes and JSON.
- **No `onboarding.*` audit event types.** The audit records real operations. No synthetic events.
- **No docs dump before first effect.** The user touches the world before reading about it.
- **No prod in the first 10 minutes.** First writes belong in `dev`. Proving belongs in `sim`. Prod is earned.
- **No destructive deletion.** Retirement with provenance. Removal with backup confirmation. Return with recovery.
- **No mysterious denials.** Every denial cites the rule, the layer, and the fix.
- **No static welcome tour.** Onboarding content is generated from the user's stated intent.
- **No all-commands-at-once.** The daily surface is 4 commands: `search`, `inspect`, `run`, `db query`. Everything else appears contextually.
- **No unclosed loops.** If onboarding opens a possibility ("you can ship this later"), it must return to close it.

---

## 14. Invariants

1. Onboarding starts with intent, not infrastructure. The first object is a goal, not a table.
2. The harness builds the world. The kernel gates it. The human approves it. This division is never violated during onboarding.
3. The first denial is designed, explained, and recorded. It is a teaching moment, not an error.
4. Recovery is proven before the user is asked to trust the world with real mutations.
5. Every stage produces a visible, auditable result. No stage ends with "trust me."
6. The daily loop is four commands: search → inspect → run → trace. Onboarding teaches exactly this.
7. Promotion requires evidence from the audit mirror and human/CI authority. The agent never self-promotes, during onboarding or after.
8. Deletion is a state transition with backup confirmation. Return is context reinstatement with recovery.
9. Onboarding content is generated from the user's intent, never shipped as a fixed template.
10. No interactive prompts in capcli. The kernel returns exit codes and JSON. The harness renders the human interface.

---

## The One-Liner

> **Start with the user's intent. Let the harness build the smallest safe world for it. Let the kernel gate it. Let the user break it on purpose, see the gate explain itself, fix it, and recover. Then teach the daily loop: search → inspect → run → trace. Make deletion a state transition and return a memory restoration. The harness learns the contract; the human learns the physics. Both earn trust through evidence, not faith.**