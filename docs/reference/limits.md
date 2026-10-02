# Limits & Ceilings

Single source of truth for every cap, ceiling, and floor. Every number below is compiled into the kernel at boot from [`governance.yaml`](../../cans/artifacts/governance.yaml) and [`policy.yaml`](../../cans/artifacts/policy.yaml) and enforced by the native C authorizer — you cannot argue with it, and the bypass flags do not exist. Narrative docs link here; they never restate numbers. Exit semantics live in [exit-codes.md](exit-codes.md): crossing a limit terminates execution with [exit 2](exit-codes.md#exit-2) (policy denial), [exit 3](exit-codes.md#exit-3) (refusal), or [exit 6](exit-codes.md#exit-6) (yield) — and the state is never modified.

Two formulas live in the concepts layer rather than here: the downward [`min()` cascade](../concepts/budgets.md#the-min-law), which makes every child frame inherit the tightest constraint, and the [platform tier taxonomy](../concepts/sandboxing.md#tiers), which decides which hosts may execute which trust rungs.

---

<a id="routine-shape"></a>

## 1. Routine Shape Ceilings (`governance.yaml`)

Your code must fit these dimensions before the kernel will register or run it:

| Dimension | Hard Limit | Breach Result |
|---|---|---|
| **Lines of Code** | Max 150 | [exit 2](exit-codes.md#exit-2) at intake / prove |
| **Token Size** | Max 2,000 tokens | exit 2 at intake / prove |
| **Parameters** | Max 8 typed `Param`s | [exit 3](exit-codes.md#exit-3) on register |
| **Module Imports** | Max 3 internal routine imports | exit 2 (composition hygiene) |
| **Description** | Min 5 words, max 60 tokens | exit 3 — unsearchable = refused |
| **Composition Depth** | Max 5 nested routines | exit 2 at call-stack push |
| **Versions Kept** | 25 per routine | Oldest pruned from the registry |
| **Rollback Depth** | 5 versions | exit 3 past the floor |

The registry shelves have dimensions too:

| Registry Cap | Hard Limit | Breach Result |
|---|---|---|
| **Registered Routines** | 300 hard cap / 200 soft cap | Registration refuses past 300; `sys doctor` nags past 200 |
| **Drafts per Agent** | 30 concurrent | exit 2 on creation |
| **Creation Velocity** | 10 per hour | exit 2 (anti-flooding) |

And nothing is immortal:

| Decay & Maintenance Rule | Threshold | Action |
|---|---|---|
| **Dead routine** | Unused 30 days | Retire candidate surfaced by `routine sweep` |
| **Failing routine** | Success rate below 0.70 over 20 runs | Demoted to draft (rollback candidate) |
| **Stale sim data** | Prod fork older than 14 days | `env doctor` re-seed nag |
| **Consolidation window** | Sunday 03:00 | Weekly duplicate scan — max 30 minutes of labor, max 10 proposals |

---

<a id="execution-budget"></a>

## 2. Execution & Budget Ceilings (`governance.yaml` + `policy.yaml`)

Enforced per invocation frame and cascaded downward via [`min()`](../concepts/budgets.md#the-min-law) — the cage tightens, never widens. Splitting a routine into children does not escape the session pool.

| Metric | Hard Limit | Scope | Breach Result |
|---|---|---|---|
| **Primitives per Run** | 50 ops | Per routine | [exit 2](exit-codes.md#exit-2) on op 51 |
| **Session Ops Pool** | 500 ops | Entire session | exit 2 — shared pool exhausted |
| **Timeout Watchdog** | 300 seconds | Per routine | exit 2 — watchdog kill |
| **Result Summary** | 500 tokens | Per return | Truncated (`truncated: true`) |
| **Transaction Statements** | 10 per `ctx.db.txn` | Per transaction | exit 2 — one txn = one thought |
| **Scratch Space** | 64 MB tmpfs | Per sandbox | [exit 4](exit-codes.md#exit-4) — OOM / disk full |
| **Session Fuel (Dev / Sim)** | 100,000 units | Per session | exit 2 on exhaustion |
| **Session Fuel (Prod)** | 500,000 units | Per session | exit 2 on exhaustion |
| **Fuel Confirm Gate** | > 50,000 units | Single operation | Demands human approval |

Exhaustion is never silent and never partial: a budget denial is an exit 2 that cites the frame, the dimension, and the remaining headroom at every level. No half-executed side effects, ever.

---

<a id="database-ceilings"></a>

## 3. Database & SQL Blast Radius (`policy.yaml`)

Enforced by AST parsing and the native [`sqlite3_set_authorizer`](../concepts/authorizer.md) callback at prepare time:

| Metric | Dev | Sim | Prod | Breach Result |
|---|---|---|---|---|
| **Rows Affected — draft trust** | 100 max | 10 max | 0 (writes denied) | [exit 2](exit-codes.md#exit-2) |
| **Rows Affected — reviewed trust** | 100 max | 100 max | 100 max | exit 2 |
| **Rows Affected — pinned trust** | 500 max | 500 max | 500 max | exit 2 |
| **INSERT Rows per Statement** | 500 (dev draft: 200) | 500 | 500 | exit 2 — must chunk |
| **SELECT LIMIT Ceiling** | 10,000 rows | 10,000 rows | 10,000 rows | Capped by authorizer |
| **UPDATE / DELETE LIMIT** | ≤ 1,000 | ≤ 1,000 | ≤ 1,000 | exit 2 without `LIMIT` |
| **Writes per Minute** | 60 | 1,000 | 60 | exit 2 — rate throttle |
| **Bulk Confirm Gate** | > 1,000 rows | > 50,000 rows | > 10 rows | Demands confirmation |

* Unbounded mutations — missing `WHERE`, missing `LIMIT`, `WHERE 1=1` tautologies — die at parse time.
* Bulk operations demand a pre-count in prod; dev and sim waive it.
* `ALTER TABLE` requires reviewed trust. `DROP`, `ATTACH`, and `DETACH` are denied outright. `VACUUM` requires pinned trust and is denied in prod.
* SQL functions run on an allowlist (`count`, `sum`, `min`, `max`, `avg`, `json_extract`, `date`, `strftime`); `load_extension`, `writefile`, `readfile`, and `fts3_tokenizer` are physically denied.
* PRAGMAs run on a whitelist, never a blacklist: `query_only` and `foreign_keys` only.
* System tables are agent-read-only — the full protection matrix lives in [schemas.md](schemas.md).

---

<a id="api-wire"></a>

## 4. API & Network Wire Ceilings (`governance.yaml` + `policy.yaml`)

| Metric | Hard Limit | Note |
|---|---|---|
| **Registered Providers** | Max 10 | E.g. Stripe, GitHub, Twilio |
| **Verbs per Provider** | Max 500 imported | The full catalog fits |
| **Active Verbs per Provider** | Max 50 active | The active surface stays small |
| **API Search Results** | Max 20 | Semantic matches below 0.6 relevance rejected |
| **Spec Size** | > 10 MB auto-prunes | Unreferenced paths pruned at compile |
| **Compiled Catalog Size** | Max 10 MB | Compiled catalogs stay lean |
| **Sync Minimum Interval** | 24 hours | No hourly hammering of provider URLs |
| **Verb Activations** | Max 10 / hour | Anti-flooding |
| **Training-Wheels Window** | 24 hours per unapproved call | Un-simulated verbs graduate on call 4 |
| **Wire Payload Egress** | 5 MB max per call | Trapped at the HTTP proxy layer |
| **Default Bucket Capacity** | 60 tokens | The client-side bucket is the primary authority |
| **Refill Rate** | 1.0 token / sec | Steady-state drip |
| **In-Flight Poll (`poll_until`)** | Max 30s duration, min 2s interval | Counts as 1 aggregate op |
| **Active Quota Earmarks** | Max 50 registry / 10 per session | Ring-fenced API capacity |
| **Max Earmark Share** | 80% of the token bucket | Anti-hoarding lock |
| **Earmark TTL** | Max 24 hours | Auto-dissolves to the global pool |
| **Background Yield Threshold** | < 15 unreserved tokens | Background task suspends via [exit 6](exit-codes.md#exit-6) |
| **Yield Task Queue** | Max 100 suspended tasks | `_suspended_tasks` |
| **Yield Deferral Limit** | Max 5 re-queue attempts | Aborts after 5 consecutive yields |
| **Token Refresh Window** | 300s before expiry | Auto-refresh, max 3 retries |
| **Idempotent Retries** | Max 3, exponential backoff | — |
| **Non-Idempotent Retries** | 0 — never | Double-spend prevention is physics |

The harness never reads raw OpenAPI specs — the kernel alone parses them. Catalog and verb mechanics → [api.md](cli/api.md).

---

<a id="triggers"></a>

## 5. Triggers, Webhooks & Crons (`governance.yaml`)

| Trigger | Dimension | Hard Limit | Action on Breach |
|---|---|---|---|
| **Cron** | Minimum interval | 5 minutes | [exit 3](exit-codes.md#exit-3) on registration |
| **Cron** | Active per agent | Max 10 | exit 2 (anti-spam) |
| **Cron** | Total active registry | Max 20 | exit 2 |
| **Cron** | Catchup fires on reboot | Exactly 1 | The rest of the backlog is discarded |
| **Watch** | Active watches | Max 50 registry / 15 per agent | exit 2 |
| **Webhook** | Max payload size | 64 KB (65,536 bytes) | 413 Payload Too Large |
| **Webhook** | Arrival rate ceiling | 100 events / minute | Throttled / 429 |
| **Webhook** | Dead letter queue | 30 days or 1,000 items | FIFO auto-purged with alarms |
| **Polling** | Poll interval | Min 5 minutes | Sub-5-minute polling rejected |
| **Polling** | Active poll watches | Max 10 | Caps background network drain |
| **Serve** | Exposed endpoints | Max 10 | 127.0.0.1 binding only |
| **Serve** | Partner API keys | Max 25 | Keys expire after 90 days — re-issue is a human act |
| **Serve** | Response body | 65,536 bytes / 500 result tokens | Capped |
| **Serve** | Minimum trust floor | Pinned | Draft/reviewed cannot serve HTTP |

---

<a id="human-io"></a>

## 6. Human IO & Quiet Hours (`governance.yaml` + `policy.yaml`)

| Channel | Dimension | Hard Limit | Behavior |
|---|---|---|---|
| **Quiet Hours** | Wall-clock window | 22:00 – 07:00 | Non-urgent notifications suppressed |
| **Quiet Hours Bypass** | Urgent inquiry | `ping ask` only | Suspended routines may still ask |
| **Notifications** | Message length | Max 300 tokens | Summaries, not essays |
| **Notifications** | Channels per setup | Max 3 | E.g. Slack, email, terminal |
| **Inquiries (`ask`)** | Question length | Max 100 tokens | Concise problem framing |
| **Inquiries (`ask`)** | Allowed options | Max 5 discrete choices | No free-form text inputs |
| **Inquiries (`ask`)** | Default timeout | 60 minutes | Fail-closed ([exit 2](exit-codes.md#exit-2)) on expiry |
| **Inquiries (`ask`)** | Maximum timeout | 480 minutes (8 hrs) | Max suspension lifespan |

---

<a id="workspace-storage"></a>

## 7. Workspace, Schema & Storage Ceilings (`governance.yaml`)

| Surface | Metric | Hard Limit |
|---|---|---|
| **Domain Tables** | Max per workspace | 100 tables |
| **Columns per Table** | Max | 30 columns |
| **Indexes per Table** | Max | 10 indexes |
| **Read Views** | Max per workspace | 50 views |
| **Active Environments** | Max isolated worktrees | 5 (`dev`, `sim`, `prod` + 2 custom) |
| **Audit Retention** | Events kept | 90 days — [audit.md](audit.md) |
| **Blob Upload Size** | Max per object | 10 MB (10,485,760 bytes) |
| **Blob MIME Allowlist** | Allowed formats | `application/pdf`, `image/*`, `text/*`, `application/json` |
| **Template Bundle Size** | Max package | 5 MB |
| **Template Seed Rows** | Max per table | 50 rows (anti bulk-injection) |

---

<a id="rate-governance"></a>

## 8. Anti-Spam & Rate Governance (`policy.yaml` + `governance.yaml`)

Runaway agent loops burn resources. These meters stop them:

| Rate Meter | Hard Limit | Enforcement Action |
|---|---|---|
| **Capability Invocations** | Max 300 calls / minute | [exit 2](exit-codes.md#exit-2) |
| **Routine Drafts per Agent** | Max 30 concurrent | exit 2 on creation |
| **Routine Creation Velocity** | Max 10 / hour | exit 2 |
| **API Verb Activations** | Max 10 / hour | exit 2 |
| **Template Promotions** | Max 5 / day | exit 2 |
| **Exploratory Ops Budget** | 200 ops / session | Reserved for raw ad-hoc exploration |
| **Agent Thrashing Threshold** | 20 sustained denials in 5 min | Fires the `agent.thrashing` alarm |
| **Backup Auto-Commit** | Every 15 minutes | Auto-commits state to Git |
| **Backup Drift Alarm** | Drift > 30 minutes | `sys doctor` warning |
| **Git History Squash** | Commits older than 90 days | Repo stays small; full history lives in object storage |

---

<a id="invariants"></a>

## 9. Machine Invariants & Non-Negotiable Bans

These are not ceilings you can negotiate — they are boot-time facts about the machine:

| Rule | Parameter | What Happens on Breach |
|---|---|---|
| **NTP Clock Drift** | Delta > 500ms vs NTP | Kernel refuses to boot (exit 3) |
| **Lockfile Integrity** | `capcli.lock` hash mismatch | Kernel refuses to boot (exit 3) |
| **Unaudited Writes** | Audit sink failure | 5-minute in-memory buffer, then execution halts ([exit 5](exit-codes.md#exit-5)) — nothing runs off the record |
| **Audit Mirror Lag** | JSONL lag > 5 minutes | `sys doctor` alerts an SLA breach |
| **Hash Chain Verification** | Daily integrity walk at 04:00 | A broken link is tamper evidence → boot refusal |
| **Universal CLI Flags** | Exactly 12 | No per-noun flag growth — [cli/index.md](cli/index.md) |
| **Headless Prompts** | Unattended confirm gate | Fails closed instantly (exit 2) |
| **Tier 2 Host Platform** | macOS, Windows, Termux | Pinned routines refused (exit 2) — [tiers](../concepts/sandboxing.md#tiers) |
| **Prod Environment Removal** | Missing confirmation | Requires both `--confirm-backup` AND `--confirm-prod` |
| **Banned Flags** | `--force`, `--force-prod`, `--override-budget`, `--verbose` | Abort immediately with a syntax error |
