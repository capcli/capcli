# Budgets & Brokerage

If you give an autonomous agent an unrestricted API key, you will wake up to a $4,000 billing incident. 

If you give it an API key to a **social media platform** (X, Meta/Threads, LinkedIn, Reddit), it’s even worse: it will burn your entire 30-day posting allowance in 8 seconds, slam headfirst into an HTTP `429`, and get your developer account banned before your morning coffee.

Most developer tools treat rate limits like an afterthought: they fire requests blindly until an API screams, panic, crash, and leave half-committed data in your database.

In Capcli, **a budget is not a loose suggestion or an alert threshold.** 

A budget is a multi-dimensional financial cage compiled into every call stack frame. It cascades downward, tracks multi-day rolling windows, ring-fences capacity before touching the wire, and yields execution cleanly instead of crashing.

---

## 1. The 7 Governed Dimensions

Every time an agent executes a subshell command, spins up a session, or calls a routine, the kernel meters seven distinct physical resources simultaneously:

| Dimension | Unit | Scope | What happens on breach |
|---|---|---|---|
| **1. Ops** | Primitive executions (`db.query`, `api.call`) | Routine + Session | `exit 2` on Op #51 (Routine) or #501 (Session) |
| **2. Duration** | Wall-clock milliseconds | Routine watchdog | SIGKILL at 300 seconds (5 min) |
| **3. Fuel** | Normalized compute gas | Session-wide pool | `exit 2` on exhaustion (100k dev / 500k prod) |
| **4. Wire Egress** | Physical socket payload bytes | Per-call + Session | Hard-trapped at 5 MB per call |
| **5. Rows Affected** | Rows written / mutated | Trust rung + Session | Capped by authorizer (10 draft, 100 reviewed, 500 pinned) |
| **6. Rate** | Operations per minute | Session-wide | Throttled / denied above 60 writes/min (prod) |
| **7. Result Tokens** | Summary tokens returned to model | Per-routine only | Auto-truncated at 500 tokens (`truncated: true`) |

Notice that these aren't just "CPU and RAM." Capcli governs the dimensions that **cost you real money, corrupt your state, or flood your LLM's brain**.

---

## 2. The Social Media Problem: Dual-Rate Windows & The 24-Hour Trap

Standard rate limiters only track simple token buckets (e.g. *60 requests per minute*).

Social media APIs don't work like that. They operate like digital breadlines with brutal multi-tier penalties:
* **Short-term burst:** 10 requests per minute.
* **Long-term ceiling:** 50 posts per **24-hour rolling window**.
* **Harsh penalty:** Trip the ceiling once, and your IP gets throttled for 6 hours.

Capcli handles this through **Dual-Rate Partitions** in `_api_quota`:

```yaml
# apis/threads.yaml (compiled quota partition)
quota:
  provider: threads
  quota_type: sliding_window
  bucket_capacity: 10          # Short burst ceiling
  refill_rate_per_s: 0.16      # 10 reqs / min
  window_seconds: 86400        # 24-hour rolling window
  window_max_calls: 50         # Hard daily post limit
```

### Dynamic JSONPath Header Scraping
Some platforms (like Meta) don't even return clean integer headers. They send back nested JSON payloads inside HTTP headers like `X-Business-Use-Case-Usage`.

Capcli doesn't care how ugly their response is. The egress proxy compiles dynamic JSONPaths directly into the parser:
```yaml
utilization_jsonpath: "$.*.call_count"
wait_seconds_jsonpath: "$.*.estimated_time_to_regain_access"
```

The moment Meta responds, Capcli parses the nested JSON, extracts the exact minute when your allowance resets, and locks the local gate. 

Your agent can beg, loop, or argue all day—the kernel refuses to dispatch another HTTP packet until that `wait_seconds` timer clears.

---

## 3. The Downward $\min()$ Law

The single most important law of Capcli composition:

$$\text{Effective Limit} = \min(\text{Declared Need}, \text{Governance Cap}, \text{Parent Remaining}, \text{Session Remaining})$$

The budget cage **tightens downward. It never widens.**

```
┌────────────────────────────────────────────────────────┐
│  SESSION POOL: 500 Ops Remaining                      │
│                                                        │
│   ┌────────────────────────────────────────────────┐   │
│   │  Parent Routine (Declared: 50 ops)             │   │
│   │  Burned: 35 ops → 15 ops remaining             │   │
│   │                                                │   │
│   │   ┌────────────────────────────────────────┐   │   │
│   │   │  Child Routine (Declared: 20 ops)      │   │   │
│   │   │                                        │   │   │
│   │   │  Effective limit = min(20, 15) = 15!   │   │   │
│   │   │  (Child gets 15 ops, NOT 20)           │   │   │
│   │   └────────────────────────────────────────┘   │   │
│   └────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘
```

### The "Cutting the Pizza" Fallacy
Agents frequently try to be clever: when an agent hits an op ceiling, it attempts to split the task into 10 smaller routines with 5 ops each.

**This does not work.** 

Trying to bypass budget limits by splitting routines into child routines is like cutting a pizza into 12 slices so you have fewer calories. Child routines inherit the parent's frame pool and consume from the same global session counter. 

Splitting code gives you better modularity, but **it will never buy you a single extra op or API call.**

---

## 4. Proactive Brokerage: Quota Earmarks

Imagine you run an agent that publishes 3 scheduled promotional posts a day on X (Twitter), but you also run an interactive customer-support agent that replies to mentions.

Without brokerage: A disgruntled customer spams your brand on Twitter. The support agent fires 50 replies in 20 minutes, burns your entire 24-hour account quota, and your scheduled promotional campaign crashes at 18:00 with an unhandled exception.

Capcli solves this with **Quota Earmarks** (`_budget_earmarks`):

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

* **Ring-Fenced Headroom:** Even if the customer support agent goes crazy answering mentions, it is **physically blocked from touching those 3 reserved slots**.
* **The 80% Anti-Hoarding Ceiling:** No single task can reserve more than 80% of a provider's active capacity.
* **Decaying Leases:** If the scheduled campaign gets cancelled or fails to use the 3 slots, the earmark TTL auto-dissolves the reservation back into the public pool.

---

## 5. Priority Preemption: Yielding Instead of Crashing (`exit 6`)

When you hit a tight API quota on a platform with 6-hour cooldowns, crashing the process is stupid. The agent loses its place, forgets what it was doing, and leaves half-written drafts in the database.

Capcli splits tasks into three priority classes:
1. **Critical:** Live user-facing actions (e.g. human waiting for a refund or password reset).
2. **Standard:** Normal day-to-day operations.
3. **Background:** Batch scrapers, marketing campaigns, and routine analytics.

### What happens when social media quota runs dry:

```
                  Provider Token Headroom < 15
                                │
            ┌───────────────────┴───────────────────┐
            ▼                                       ▼
      Critical Task                           Background Task
            │                                       │
  Can borrow unburned earmarks?               EXIT 6 (YIELD)
            │                                       │
         SUCCESS                           Frame parked into
            │                              _suspended_tasks
  (Or exit 2 if dead empty)                         │
                                           Daemon watches reset_at
                                                    │
                                           Auto-resumes when
                                           rolling window clears!
```

* **The Clean Park:** When a background marketing routine tries to post but finds the rolling daily ceiling exhausted, the kernel doesn't throw a runtime error. It emits **`exit 6` (Yield)**.
* **The Suspended Frame:** The routine’s call stack, parameters, and current leaf progress are serialized into `_suspended_tasks` alongside the exact epoch timestamp (`resume_at: 1714521600`) when the API window reopens.
* **Zero Babysitting:** The daemon sleeps. When the clock strikes the reset epoch, the daemon unfreezes the task and executes the post. 

Zero human intervention. Zero crashed jobs. Zero rate-limit bans.

---

## 6. Denial Anatomy: Exact Blame

When an op ceiling, rate bucket, or fuel gauge blocks execution, Capcli doesn't print a mystery stack trace. 

It tells you the exact frame, the exact provider, and the exact reset time:

```text
[prod:tier_1]  ✗  exit 6

  YIELD  policy.api.quota_exhausted
         routine broadcast_newsletter@2 (frame_018)
         provider: threads
         verb:     threads.create_media_post

  state_modified:  false
  layer:           quota
  tokens_left:     0 / 50 (24h window)
  reset_at:        18:00:00 UTC (in 4h 12m)
  suspended_frame: task_99a8b1
  remedy:          task safely yielded; daemon will auto-resume at reset_at
```

Look at the receipt:
* **`state_modified: false`**: State is clean. No ghost posts. No half-finished transactions.
* **`tokens_left: 0 / 50`**: You know exactly which ceiling you hit.
* **`reset_at`**: Downstream timestamp parsed directly from the provider's HTTP headers.
* **`suspended_frame`**: The task is alive and waiting; not dead in a ditch.

---

## The One Rule

**Budgets are structural physics, not runtime suggestions.**

You cannot `--force` your way past a Twitter rate limit. You cannot bypass a daily ceiling by writing nested subroutines. You declare what you need, Capcli ring-fences the slots, and when the quota runs dry, reality parks cleanly until the doors open again.

---

**See how audit logs link budget frames:** → [audit.md](audit.md)  
**Inspect live API quotas and unreserved headroom:** → `capcli inspect cap://threads.create_media_post`
