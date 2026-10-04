# Limits & Ceilings

Every limit below is compiled directly into the Rust kernel and native C authorizer. 

These are not suggestions. You cannot `--force` bypass them. Crossing any limit immediately terminates execution with **`exit 2` (Policy Denial)**, **`exit 3` (Refusal)**, or **`exit 6` (Yield)**.

---

## 1. Routine Shape Ceilings (`governance.yaml`)

Your code must fit these exact dimensions before the kernel writes or runs it:

| Dimension | Hard Limit | Breach Result |
|---|---|---|
| **Lines of Code (LOC)** | Max 150 lines | `exit 2` at intake / prove |
| **Token Size** | Max 2,000 tokens | `exit 2` at intake / prove |
| **Parameters** | Max 8 typed `Param`s | `exit 3` on register |
| **Module Imports** | Max 3 internal routine imports | `exit 2` (composition hygiene) |
| **Description** | Min 5 words, max 60 tokens | `exit 3` (unsearchable = refused) |
| **Max Versions Kept** | 25 versions | Oldest pruned from registry |
| **Max Rollback Depth** | 5 versions | `exit 3` if rolling back further |
| **Composition Depth** | Max 5 nested routines | `exit 2` at call stack push |

---

## 2. Execution & Budget Ceilings (`governance.yaml` + `policy.yaml`)

Enforced per invocation frame and cascaded downward via $\min()$:

| Metric | Hard Limit | Scope | Breach Result |
|---|---|---|---|
| **Primitives per Run** | 50 ops | Per routine | `exit 2` on Op #51 |
| **Session Ops Pool** | 500 ops | Entire session | `exit 2` (shared pool exhausted) |
| **Timeout Watchdog** | 300 seconds (5 min) | Per routine | `exit 2` (watchdog SIGKILL) |
| **Result Summary** | 500 tokens | Per return | Auto-truncated (`truncated: true`) |
| **Transaction Statements** | Max 10 per `ctx.db.txn` | Per transaction | `exit 2` (one txn = one thought) |
| **Scratch Space** | 64 MB tmpfs | Per sandbox | `exit 4` (OOM / disk full) |
| **Session Fuel (Dev/Sim)**| 100,000 units | Per session | `exit 2` on exhaustion |
| **Session Fuel (Prod)** | 500,000 units | Per session | `exit 2` on exhaustion |
| **Fuel Confirm Gate** | > 50,000 units | Single operation | Demands human approval |

---

## 3. Database & SQL Blast Radius (`policy.yaml`)

Enforced by AST parsing and native SQLite `sqlite3_set_authorizer`:

| Metric | Dev | Sim | Prod | Breach Result |
|---|---|---|---|---|
| **Draft Rows Affected** | 100 max | 10 max | **0 (Denied)** | `exit 2` |
| **Reviewed Rows Affected** | 100 max | 100 max | 100 max | `exit 2` |
| **Pinned Rows Affected** | 500 max | 500 max | 500 max | `exit 2` |
| **SELECT LIMIT Ceiling** | 10,000 rows | 10,000 rows | 10,000 rows | Capped by authorizer |
| **INSERT Statement Cap** | 200 rows | 500 rows | 500 rows | `exit 2` (must chunk) |
| **UPDATE / DELETE LIMIT** | Max 1,000 | Max 1,000 | Max 1,000 | `exit 2` without LIMIT |
| **Bulk Confirm Gate** | > 50,000 rows | > 50,000 rows | > 10 rows | Demands confirmation |
| **Writes per Minute** | 1,000 | 1,000 | 60 | `exit 2` (rate throttle) |

* Unbounded updates/deletes (`WHERE 1=1`, missing `WHERE`, missing `LIMIT`) die instantly at prepare-time (`exit 2`).
* `ALTER TABLE` requires minimum **Reviewed** trust.
* `DROP TABLE` is unconditionally **denied** for agents.
* `VACUUM` is unconditionally **denied in prod**; requires **Pinned** trust in dev.

---

## 4. API & Network Wire Ceilings (`governance.yaml` + `policy.yaml`)

| Metric | Hard Limit | Note |
|---|---|---|
| **Registered Providers** | Max 10 providers | E.g. Stripe, GitHub, Twilio |
| **Verbs per Provider** | Max 300 imported | Full catalog ceiling |
| **Wire Payload Egress** | 5 MB max per call | Trapped at HTTP proxy layer |
| **Default Bucket Capacity** | 60 tokens | Client-side rate bucket |
| **Refill Rate** | 1.0 token / sec | Steady-state drip |
| **In-Flight Poll (`poll_until`)**| Max 30s duration, min 2s sleep | Counts as **1 aggregate op** |
| **Priority Floor (Background)** | Yields below 15 tokens | `exit 6`, frame parked in `_suspended_tasks` |
| **Priority Floor (Standard)** | Yields below 5 tokens | `exit 6`, frame parked in `_suspended_tasks` |
| **Priority Floor (Critical)** | 0 (drains pool) | Pre-call gate `exit 2` only when bucket is empty |
| **Yield Task Queue** | Max 100 suspended tasks | In `_suspended_tasks` table |
| **Yield Deferral Limit** | Max 5 re-queue attempts | Aborts after 5 consecutive yields |
| **Token Refresh Window** | 300s before expiration | Auto-refreshes (max 3 retries) |
| **Non-Idempotent Retries** | **0 (Never)** | Non-idempotent HTTP retries banned |

---

## 5. Triggers, Webhooks & Crons (`governance.yaml`)

| Trigger | Dimension | Hard Limit | Action on Breach |
|---|---|---|---|
| **Cron** | Minimum Interval | 5 minutes | `exit 3` on registration |
| **Cron** | Active per Agent | Max 10 active | `exit 2` (anti-spam) |
| **Cron** | Total Active Registry | Max 20 active | `exit 2` |
| **Cron** | Catchup Fires on Boot | **Exactly 1 fire** | Discards rest of backlog |
| **Webhook**| Max Payload Size | 64 KB (65,536 bytes) | `413 Payload Too Large` |
| **Webhook**| Arrival Rate Ceiling | 100 events / minute | Throttled / 429 response |
| **Webhook**| Dead Letter Queue | 30 days or 1,000 items | FIFO auto-purged with alarms |
| **Polling**| Polling Interval | Min 5 minutes | Sub-5-min polling rejected |
| **Polling**| Max Active Watches | Max 10 watches | Caps network background drain |
| **Serve** | Exposed Endpoints | Max 10 endpoints | `127.0.0.1` binding only |
| **Serve** | Partner API Keys | Max 25 keys | Key expires after 90 days |
| **Serve** | Minimum Trust Floor | **Pinned** | Draft/Reviewed cannot serve HTTP |

---

## 6. Human IO & Quiet Hours (`governance.yaml` + `policy.yaml`)

| Channel | Dimension | Hard Limit | Behavior |
|---|---|---|---|
| **Quiet Hours** | Wall-clock Window | **22:00 to 07:00** | Non-urgent notifications denied |
| **Quiet Hours Bypass** | Urgent Inquiry | `ping.ask` only | Suspended routines can ping |
| **Notifications** | Message Length | Max 300 tokens | Summaries only; no essays |
| **Notification Channels**| Max per Setup | 3 channels | E.g. Slack, Email, Terminal |
| **Inquiries (`ask`)** | Question Length | Max 100 tokens | Concise problem framing |
| **Inquiries (`ask`)** | Allowed Options | Max 5 choices | No free-form text inputs |
| **Inquiries (`ask`)** | Default Timeout | 60 minutes | Fail-closed (`exit 2`) on timeout |
| **Inquiries (`ask`)** | Maximum Timeout | 480 minutes (8 hrs) | Max suspension lifespan |

---

## 7. Workspace, Schema & Storage Ceilings (`governance.yaml`)

| Surface | Metric | Hard Limit |
|---|---|---|
| **Domain Tables** | Max per Workspace | 100 tables |
| **Columns per Table** | Max per Table | 30 columns |
| **Indexes per Table** | Max per Table | 10 indexes |
| **Read Views** | Max per Workspace | 50 views |
| **Active Environments** | Max isolated worktrees | 5 (`dev`, `sim`, `prod` + 2 custom) |
| **Blob Upload Size** | Max per file | 10 MB (10,485,760 bytes) |
| **Blob MIME Allowlist** | Allowed formats | `application/pdf`, `image/*`, `text/*`, `application/json` |
| **Template Bundle Size**| Max package size | 5 MB |
| **Template Seed Rows** | Max per table | 50 rows (anti-bulk data injection) |

---

## 8. Anti-Spam & Rate Governance (`policy.yaml` + `governance.yaml`)

To stop runaway agent loops from burning resources:

| Rate Meter | Hard Limit | Enforcement Action |
|---|---|---|
| **Capability Invocations**| Max 300 calls / minute | `exit 2` |
| **Routine Drafts per Agent**| Max 30 concurrent drafts | `exit 2` on creation |
| **Routine Creation Velocity**| Max 10 created / hour | `exit 2` (anti-flooding) |
| **Template Promotions** | Max 5 promotions / day | `exit 2` |
| **Agent Thrashing Threshold**| 20 sustained denials in 5 min| Fires `agent.thrashing` alarm |
| **Backup Auto-Commit** | Every 15 minutes | Auto-commits state to Git |
| **Backup Drift Alarm** | Drift > 30 minutes | `sys doctor` emits warning |

---

## 9. Machine Invariants & Non-Negotiable Bans

| Rule | Parameter | What happens on breach |
|---|---|---|
| **NTP Clock Drift** | Delta > 500ms vs NTP | Kernel refuses to boot (`exit 3`) |
| **Audit Mirror Lag** | JSONL lag > 5 minutes | `sys doctor` alerts SLA breach |
| **Universal CLI Flags** | Exactly 12 flags | No custom per-noun flag bloat |
| **Headless Prompts** | Unattended confirm gate | Fails closed instantly (`exit 2`) |
| **Tier 2 Host Platform** | macOS, Win, Termux | Pinned routines refused (`exit 2`) |
| **Prod Environment Removal**| Missing confirmation | Requires `--confirm-backup` AND `--confirm-prod` |
| **Banned Flags** | `--force`, `--verbose`, `--override-budget` | Aborts immediately with syntax error |
