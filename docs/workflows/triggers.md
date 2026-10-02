# Triggers

An unsupervised AI agent left in an infinite loop is a menace.

Without sensory boundaries, it will invent imaginary work, poll an empty database 5,000 times a minute, or process the same Stripe webhook 40 times because it forgot where it left off.

In Capcli, **agents do not run loose loops.** They are event-driven machines. They sleep until a real physical stimulus arrives — a clock tick, a verified webhook, an explicit request. Here's how you wire your world to wake them up safely. (Exact syntax for every verb: [reference/cli/bind.md](../reference/cli/bind.md).)

---

## Sensory grounding: `sys inbox pop`

In naive agent frameworks, agents "decide" what to do next based on vibe prompts: *"Check if anything needs fixing."* Inevitably the model starts hallucinating phantom tasks, refactoring working code, or querying orders that don't exist.

Capcli enforces **sensory grounding**: if there is no stimulus queued in the sensory inbox, there is zero work to do.

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

If the queue is empty, the subshell exits clean — `inbox empty (0 events)`. Zero tokens burned. No hallucinated maintenance tasks.

---

## Timed automation: `bind cron`

You want an agent routine to run every morning at 03:00 to reconcile payments:

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

The anti-DDoS cron laws (bindings are mutations — every `bind` verb takes `-m`, same law as SQL writes):

1. **The 5-minute floor.** The minimum allowed interval is 5 minutes. Binding `* * * * *` (every minute) fails instantly with [`exit 3`](../reference/exit-codes.md#exit-3). Need sub-minute triggers? Use webhooks. ([All trigger ceilings](../reference/limits.md#triggers).)
2. **The "laptop closed" catchup rule.** Shut your laptop on Friday, open it Monday: a standard Unix crontab tries to fire all 72 missed weekend runs in the same second, incinerating your CPU. Capcli's rule: **max exactly 1 catchup run on wake.** The rest of the backlog is discarded.
3. **Orphan protection.** Retire `cap://reconcile_orders@3` and the daemon loudly disables the bound schedule. No zombie crons executing dead code.

---

## Webhooks: the HMAC bouncer

Most developers let webhooks hit their guest code directly. A botnet sprays your URL with garbage payloads, triggers 10,000 subshells, and drains your budget before lunch.

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

When a payload arrives:

- **HMAC verification wall.** The kernel checks the cryptographic signature using the secret in your vault *before* spawning any guest process. Tampered signature? **Dropped instantly.** Zero Python or TypeScript processes spawned.
- **64 KB payload cap.** Webhooks are notifications, not file transfers. Anything over 65,536 bytes gets `413 Payload Too Large`.
- **The 100/min DDoS ceiling.** If Stripe goes crazy and sends 400 events in a minute, traffic above the ceiling is queued to the Dead Letter Queue.
- **The dead letter purge.** Failed or throttled payloads live in the DLQ for 30 days, max 1,000 items, then FIFO auto-purge with loud alerts. ([Numbers](../reference/limits.md#triggers).)

---

## Turning routines into servers: `bind endpoint`

You built a hardened routine (`cap://order_status@12`). Now let external partners or client apps query it over HTTP or MCP:

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

The hard server laws:

- **The pinned-only floor.** Draft routines cannot serve traffic. Reviewed routines cannot serve traffic. Only code that has survived simulation and earned an immutable version hash is allowed to listen on a port — [why the ladder ends at pinned](../concepts/trust-engine.md).
- **Localhost binding.** Capcli binds strictly to `127.0.0.1` and refuses `0.0.0.0`. Want public traffic? Put Cloudflare, Caddy, or Nginx in front of it like an adult.
- **Keys expire in 90 days.** Issue keys via `capcli bind keys issue partner_acme` — every key carries a mandatory 90-day expiration. Generating an immortal API key is structurally impossible. ([Key governance](../reference/limits.md).)

---

## Instant MCP export

Using Claude Desktop, Cursor, or external agent swarms? No custom MCP bridge scripts needed:

```bash
$ capcli bind export mcp --out /tmp/capcli-mcp.json
```

```text
[dev:tier_1]  ✓  exported

  tools:    14 pinned routines
  format:   Model Context Protocol (v2024-11-05)
  written:  /tmp/capcli-mcp.json
```

Point your external AI harness at the generated JSON. It automatically inherits all input schemas, types, and descriptions — while every single call crossing the bridge remains shackled to the budget cage and the authorizer.

---

**Next:** need a human to approve an edge case? → [approvals.md](approvals.md)

**Inspect active bindings:** `capcli inspect bind://nightly_reconcile`
