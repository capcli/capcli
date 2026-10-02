# Inbox & Triggers

An unsupervised AI agent left in an infinite loop is a menace. 

Without sensory boundaries, it will invent imaginary work, poll an empty database 5,000 times a minute like a caffeinated toddler checking the fridge, or process the same Stripe webhook 40 times because it forgot where it left off.

In Capcli, **agents do not run loose loops.** They are event-driven machines. 

They sleep until a real physical stimulus arrives—a clock tick, a verified webhook, or an explicit request. Here is how you wire your world to wake them up safely.

---

## 1. Sensory Grounding: `sys inbox pop`

In naive agent frameworks, agents "decide" what to do next based on vibe prompts: *"Check if anything needs fixing."* 

Inevitably, the model starts hallucinating phantom tasks, refactoring working code, or querying orders that don't exist.

Capcli enforces **Sensory Grounding**. If there is no stimulus queued in the sensory inbox, there is zero work to do.

```bash
$ capcli sys inbox pop
```

```text
[dev:tier_1]  1 event popped

  id:         evt_99f2c
  source:     webhook://stripe/charge.dispute.created
  capability: cap://freeze_disputed_account@2
  payload:    {"dispute_id": "dp_18s9", "amount": 4500}
  enqueued:   12s ago
```

If the queue is empty:

```bash
$ capcli sys inbox pop
```

```text
[dev:tier_1]  inbox empty (0 events)
```

The subshell exits clean. Zero tokens burned. No hallucinated maintenance tasks.

---

## 2. Timed Automation: `bind cron`

You want an agent routine to run every morning at 03:00 to reconcile payments.

```bash
$ capcli bind cron nightly_reconcile cap://reconcile_orders@3 "0 3 * * *" \
    -m "nightly accounting sync"
```

```text
[dev:tier_1]  ✓  bound

  handle:     bind://nightly_reconcile
  schedule:   0 3 * * * (daily at 03:00)
  target:     cap://reconcile_orders@3
  trust:      reviewed
```

### The Anti-DDoS Cron Laws:
1. **The 5-Minute Floor:** The minimum allowed interval is **5 minutes**. Trying to bind `* * * * *` (every minute) fails instantly (`exit 3`). If you need sub-second triggers, use webhooks.
2. **The "Laptop Closed" Catchup Rule:** Imagine you shut your laptop on Friday and open it on Monday. A standard Unix crontab tries to fire all 72 missed weekend runs at the exact same second, incinerating your CPU. Capcli's rule: **Max exactly 1 catchup run on wake.** The rest of the missed backlog is discarded.
3. **Orphan Protection:** If you retire `cap://reconcile_orders@3`, the daemon loudly disables the bound schedule. No zombie crons executing dead code.

---

## 3. Webhooks: The HMAC Bouncer (`bind webhook`)

Most developers let webhooks hit their guest code directly. A botnet sprays your URL with garbage payloads, triggers 10,000 subshells, and drains your OpenAI budget before lunch.

Capcli intercepts webhooks **at the kernel door**:

```bash
$ capcli bind webhook stripe_disputes stripe "charge.dispute.created" \
    cap://freeze_disputed_account@2 \
    --ingress "https://api.mycompany.com/events" \
    -m "handle chargeback events"
```

```text
[dev:tier_1]  ✓  bound

  handle:      bind://stripe_disputes
  provider:    stripe
  event:       charge.dispute.created
  target:      cap://freeze_disputed_account@2
  auth:        HMAC-SHA256 (via vault://stripe_webhook_secret)
  rate_limit:  100 events/min
```

### What happens when a payload arrives:
* **HMAC Verification Wall:** The kernel checks the cryptographic signature using the secret in your vault *before* spawning any guest process. Tampered signature? **Dropped instantly.** Zero Python or TypeScript processes spawned.
* **64 KB Payload Cap:** Webhooks are notifications, not file transfers. Any payload exceeding 65,536 bytes returns `413 Payload Too Large`.
* **The 100/min DDoS Ceiling:** If Stripe goes crazy and sends 400 events/minute, traffic above 100/min gets queued to the Dead Letter Queue (DLQ).
* **The Dead Letter Purge:** Failed or throttled webhook payloads live in the DLQ for 30 days (max 1,000 items). Past that, they are FIFO auto-purged with loud alerts.

---

## 4. Turning Routines into Servers: `bind endpoint`

You built a hardened routine (`cap://order_status@12`). Now you want to let external partners or client apps query it over HTTP or MCP (Model Context Protocol).

```bash
$ capcli bind endpoint cap://order_status@12 \
    --auth api-key \
    --rate 60 \
    --channel all
```

```text
[prod:tier_1]  ✓  served

  endpoint:   http://127.0.0.1:4040/endpoints/order_status
  channels:   REST, MCP
  trust:      pinned
  auth:       partner-api-key
```

### The Hard Server Laws:
* **The Pinned-Only Rule:** You cannot expose an endpoint to the outside world unless it is **Pinned** (`trust: pinned`). Draft routines cannot serve traffic. Reviewed routines cannot serve traffic. Only code that has survived simulation and earned an immutable version hash is allowed to listen on a port.
* **Localhost Binding:** Capcli binds strictly to `127.0.0.1`. It refuses to bind to `0.0.0.0`. If you want public traffic, put Cloudflare, Caddy, or Nginx in front of it like an adult.
* **Partner Keys Expire in 90 Days:** Issue keys via `capcli bind keys issue partner_acme`. Every key carries a mandatory 90-day expiration. Generating an immortal API key is structurally impossible.

---

## 5. Instant MCP Server Export

If you are using Claude Desktop, Cursor, or external agent swarms, you don't need to write custom MCP bridge scripts:

```bash
$ capcli bind export mcp --out /tmp/capcli-mcp.json
```

```text
[dev:tier_1]  ✓  exported

  tools:    14 pinned routines
  format:   Model Context Protocol (v2024-11-05)
  written:  /tmp/capcli-mcp.json
```

Point your external AI harness at the generated JSON. It automatically inherits all input schemas (`Param`), types, and descriptions—while every single call crossing the bridge remains shackled to the Capcli budget cage and authorizer.

---

## The One Rule

**Events wake routines. Routines never run unprompted.**

No infinite while-loops. No unauthenticated webhook endpoints. No immortal API keys.

---

**Next:** Need a human to approve an edge-case? → [ask-human.md](ask-human.md)  
**Inspect active bindings:** → `capcli inspect bind://nightly_reconcile`
