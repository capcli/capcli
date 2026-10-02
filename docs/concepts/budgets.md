# Budgets & Brokerage

Hand an autonomous agent an unrestricted API key and you will wake up to a $4,000 billing incident. Hand it a key to a **social media platform** (X, Threads, LinkedIn, Reddit) and it's worse: it burns a 30-day posting allowance in eight seconds, slams headfirst into an HTTP `429`, and gets your developer account banned before the incident pager even warms up.

Most tools treat rate limits as an afterthought: fire requests blindly until the API screams, panic, crash, and leave half-committed data in the database. In Capcli, **a budget is not a loose suggestion or an alert threshold.**

A budget is a multi-dimensional cage compiled into every call stack frame. It cascades downward, tracks multi-day rolling windows, ring-fences capacity before touching the wire, and yields execution cleanly instead of crashing.

---

## 1. The 7 Governed Dimensions

Every subshell command, session, or routine invocation is metered on seven physical resources simultaneously:

| Dimension | Unit | Scope | What happens on breach |
|---|---|---|---|
| **1. Ops** | Primitive executions (`db.query`, `api.call`) | Per-run + session | The next op past the run ceiling aborts |
| **2. Duration** | Wall-clock | Per-run watchdog + session | Watchdog kill |
| **3. Fuel** | Normalized compute gas | Session pool | Exhaustion denial |
| **4. Wire Egress** | Socket payload bytes | Per-call + session | Hard-trapped per call |
| **5. Rows Affected** | Rows written / mutated | Trust rung + session | Authorizer cap |
| **6. Rate** | Operations per minute | Session-wide | Throttled / denied |
| **7. Result Tokens** | Summary tokens returned to the model | Per-routine only | Auto-truncated (`truncated: true`) |

These aren't "CPU and RAM." Capcli governs the dimensions that **cost real money, corrupt state, or flood the model's brain**. Every exact figure lives in [reference/limits.md](../reference/limits.md): [execution-budget](../reference/limits.md#execution-budget), [api-wire](../reference/limits.md#api-wire), [rate-governance](../reference/limits.md#rate-governance).

---

## 2. Dual-Rate Windows & The 24-Hour Trap

Standard limiters track a single token bucket. Social media APIs don't work like that. They run multi-tier penalties:

* **Short-term burst:** a per-minute bucket.
* **Long-term ceiling:** a hard cap on a 24-hour rolling window.
* **Harsh penalty:** trip the ceiling once and your account gets throttled for hours.

Capcli models this with **dual-rate partitions** in `_api_quota` — burst bucket plus rolling window, tracked and reconciled per environment, so rehearsal in sim never drains a production bucket. The client-side bucket is the primary authority: before every dispatch, the gate fails closed if a token isn't available.

### Dynamic JSONPath Header Calibration

Some platforms (Meta) don't return clean integer headers at all. They embed nested JSON payloads inside HTTP headers like `X-Business-Use-Case-Usage`. The egress proxy compiles dynamic JSONPaths directly into the parser:

```yaml
utilization_jsonpath: "$.*.call_count"
wait_seconds_jsonpath: "$.*.estimated_time_to_regain_access"
```

The moment Meta responds, the kernel parses the nested JSON, extracts the exact minute the allowance resets, and locks the local gate. Your agent can beg, loop, or argue all day — no packet leaves until the `wait_seconds` timer clears. Default bucket arithmetic: [reference/limits.md#rate-governance](../reference/limits.md#rate-governance).

---

<a id="the-min-law"></a>

## 3. The min() Law

The single most important law of Capcli composition, stated once, precisely:

> **A child frame's effective budget is `min(declared, parent_remaining)` — enforced per dimension at every frame push.** It applies to the cascading dimensions (ops, duration). A declaration is itself bounded by the governance ceiling; you cannot declare your way past a cap. **The cage tightens downward. It never widens.**

| Dimension family | Scope | Cascade behavior |
|---|---|---|
| **Ops, duration** | Routine-scoped | Cascades: child consumes from the parent's pool |
| **Fuel, egress bytes, writes/min, capability calls/min, rows** | Session-scoped pool | Shared per session — no per-frame slice to inherit |
| **Result tokens** | Per-routine | Independent — each routine caps its own output |

### Worked Example

```
Session opens with a 500-op ceiling.
Parent routine declares 50 — the per-run ceiling — and burns 35.
The parent frame has 15 left.

Child routine declares 20.
Child effective = min(20, 15) = 15.
The child hits its wall at op 15, not 20.
```

Run the same child early, while the parent frame is fresh, and it gets its full 20. Run it against a nearly drained session pool, and it gets whatever the pool still holds — the session ceiling caps every frame below it. The declaration is a request; the tightest wall is the answer.

### Splitting Is Not Escaping

When an agent hits an op ceiling, it gets clever: split the task into ten smaller routines of five ops each. **This does not work.** Child routines inherit the parent's frame pool and consume from the same session counters — a 100-op job split into 10×10 still hits the session ceiling at the same absolute count. Splitting buys modularity. It never buys a single extra op or API call.

---

## 4. Proactive Brokerage: Quota Earmarks

Scenario: a scheduler publishes three promotional posts a day, and a customer-support agent replies to mentions on the same platform. Without brokerage, the support agent answers a spam storm at noon, burns the entire 24-hour account quota, and the scheduled campaign crashes at 18:00 with an unhandled exception.

Capcli ring-fences capacity up front via **Quota Earmarks** (`_budget_earmarks`):

```typescript
// The daily scheduler runs at 08:00 and ring-fences 3 posts for the day:
const earmark = await ctx.quota.earmark({
  provider: "twitter",
  verb: "create_post",
  tokens: 3,
  ttl_hours: 24,
  intent: "reserve quota for scheduled daily broadcasts"
});

// Later that evening, the scheduled post consumes from the reserve:
await ctx.api.call("twitter.create_post", { text: "Hello world" }, { earmark_id: earmark.id });
```

* **Ring-fenced headroom:** even if the support agent goes crazy answering mentions, it is physically blocked from touching those 3 reserved slots.
* **The 80% anti-hoarding ceiling:** no single reservation can lock more than 80% of a provider's active capacity, and sessions are capped at 10 active earmarks.
* **Decaying leases:** if the campaign is cancelled or fails to use its slots, the earmark TTL auto-dissolves the reservation back into the public pool.

---

## 5. Priority Preemption: Yielding Instead of Crashing

Tasks run in three priority classes: **Critical** (a human is waiting on a refund or password reset), **Standard** (day-to-day operations), and **Background** (batch scrapers, marketing campaigns, analytics).

When quota runs dry on a platform with 6-hour cooldowns, crashing is the stupid move — the agent loses its place, forgets what it was doing, and leaves half-written drafts in the database. Capcli parks instead:

* **The clean park:** a background routine that finds the rolling ceiling exhausted gets [exit 6 (Yield)](../reference/exit-codes.md#exit-6) — not an error.
* **The suspended frame:** the routine's call stack, parameters, and leaf progress are serialized into `_suspended_tasks` alongside the exact `resume_at` epoch when the API window reopens.
* **Zero babysitting:** the daemon watches the reset timestamps, unfreezes the frame, and re-executes when the window clears.
* **Critical bypass:** critical tasks may borrow unburned earmarks in an emergency; a hard-empty pool still denies ([exit 2](../reference/exit-codes.md#exit-2)) rather than yield a user-facing failure into oblivion.

```text
[prod:tier_1]  ✗  exit 6

  YIELD  policy.api.quota_exhausted
         routine broadcast_newsletter@2 (frame_018)
         provider: threads · verb: threads.create_media_post

  state_modified:  false
  tokens_left:     0 (24h window)
  reset_at:        18:00:00 UTC
  suspended_frame: task_99a8b1
  remedy:          task safely yielded; daemon auto-resumes at reset_at
```

`state_modified: false` — no ghost posts, no half-finished transactions. The task is alive and waiting, not dead in a ditch.

Budget-denial receipts (the `exit 2` form, when a frame simply cannot proceed) follow the standard denial anatomy in [reference/exit-codes.md](../reference/exit-codes.md).

---

**See how audit logs link budget frames:** → [memory-spine.md](memory-spine.md)
**Inspect live quotas and unreserved headroom:** → `capcli inspect cap://threads.create_media_post`
