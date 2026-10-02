# APIs

Your agent wants to talk to Stripe, Twilio, or GitHub.

Left to its own devices, an LLM will ask you to paste your live production secret into a chat prompt, write a broken `curl`, burn your context window with 4,000 lines of Swagger JSON, and wake you at 3:00 AM with a rate-limit meltdown.

In Capcli, external APIs are governed with the exact same ruthless physics as the database. Here's how your agent talks to the outside world without setting the company on fire.

---

## Discovery: the dormant catalog

You do not paste giant OpenAPI specs into your prompt — that gives the model amnesia and burns context for zero reason. Sync the vendor spec once and let the kernel be the only thing that reads it:

```bash
$ capcli api sync stripe https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.yaml
```

The kernel compiles the endpoints into `apis/stripe.yaml`. Every endpoint enters the registry **dormant**:

```bash
$ capcli search "refund"
```

```text
[dev:tier_1]  2 results

  cap://stripe.refund_charge    api-verb   dormant   "Issue partial or full Stripe refund"
  cap://order_refund@4          routine    reviewed  "Process cancelled order and archive"
```

Notice the pointer: **`cap://`**, not `api://`. To the kernel, anything runnable is a capability — local TypeScript routine or external Stripe endpoint, the interface is identical: search it, inspect it, run it.

Dormant means: zero token cost to your context window, fully discoverable via search, and **physically uncallable** until deliberately activated.

---

## Activation & training wheels
<a id="training-wheels"></a>

Your agent can't fire off random endpoints. It activates the verb and declares its causal motivation (`-m`, like every mutation):

```bash
$ capcli api activate stripe.refund_charge -m "allow support agent refunds"
```

```text
[dev:tier_1]  ✓  activated

  verb:            cap://stripe.refund_charge
  trust:           draft
  training_wheels: 3 calls remaining
  sim_mode:        sandbox
```

The first three calls don't get to blast the live wire: the kernel forces them through synthetic contract replays against historical audit logs in simulation. No payload schema violations, no rate trips — and call 4 auto-graduates into standard governance. You don't let an autonomous agent wake up a live payment endpoint and immediately start moving money.

---

## The missing-key trap: Cockpit-only injection
<a id="vault"></a>

Never paste live API keys into a chat terminal. They end up in LLM training logs, bash histories, and subshell environments.

Watch what happens when the agent runs a verb before credentials exist:

```bash
$ capcli run stripe.refund_charge -p charge_id=ch_3M9x -p amount=2500 \
    -m "refund defective item"
```

```text
[dev:tier_1]  ✗  exit 3

  FAIL  policy.secrets.missing
        capability: cap://stripe.refund_charge
        secret_ref: vault://stripe_secret

        Credential 'stripe_secret' not found in vault.
        Direct CLI parameter injection is banned to prevent prompt leakage.

  state_modified: false
  layer: vault
  remedy: prompt human supervisor to inject credential via Cockpit (http://127.0.0.1:4040/vault)
```

[Exit 3](../reference/exit-codes.md#exit-3): refused, state untouched. The kernel won't prompt the agent to read the key, and it won't let the agent accept the key string either.

So your agent reads the `remedy` and talks to you:

> *"I need credentials for Stripe. I'm not allowed to see or handle your secret key. Please open the Cockpit at http://127.0.0.1:4040/vault and inject `stripe_secret`."*

You open the local [Administrative Cockpit](../../cans/interface.md) in your browser, authorize via biometric, and paste the key straight into the encrypted AES-256-GCM vault. Now the agent retries:

```bash
$ capcli run stripe.refund_charge -p charge_id=ch_3M9x -p amount=2500 \
    -m "refund defective item"
```

```text
[dev:tier_1]  stripe.refund_charge  ✓  312ms

  status:     succeeded
  refund_id:  re_98Fka92
  quota_used: 1 token (47 remaining)
  audit:      op_7b2f
```

The egress proxy injected `Authorization: Bearer sk_live_...` into the HTTP header at the wire boundary, and the moment the response returned, the memory buffer holding the plaintext secret was overwritten with zeros. The agent got its refund ID. It never touched the key.

---

## Kill the `while(true)` loop: `poll_until`

Agents love infinite sleep loops while waiting for async jobs:

```python
# THE WRONG WAY: burns 40 ops and dies of budget exhaustion
while True:
    res = ctx.api.call("video.status", {"id": job_id})
    if res.ready: break
    time.sleep(2)  # killed by the watchdog → exit 2
```

Busy-waiting in guest code is a quick way to get your routine killed by the watchdog. Use the kernel primitive instead:

```python
# THE CAPCLI WAY: slept in the Rust runtime, counts as ONE op
res = ctx.api.poll_until(
    verb="video.status",
    params={"id": job_id},
    condition="res.status == 'completed'",
    timeout_s=30,
    interval_s=2
)
```

The guest interpreter suspends cleanly; the compiled Rust kernel manages the polling and the sleep. A 30-second polling cycle making 15 HTTP checks counts as **exactly 1 op** against your budget — 30s ceiling, 2s interval floor ([limits](../reference/limits.md#api-wire)).

---

## Proactive rate limits & dynamic header scraping

Most HTTP libraries blast requests blindly until they slam face-first into a `429`. Capcli stops the blast before it leaves your machine:

1. **Client-side token bucket** — outbound cadence is regulated locally: 60 burst capacity, 1.0 token/second steady refill ([limits](../reference/limits.md#api-wire)).
2. **Dynamic header scraping** — every response recalibrates the local bucket: standard `X-RateLimit-Remaining` headers, or nested JSON headers like Meta's `X-Business-Use-Case-Usage` via JSONPath.
3. **Forced drain** — if Stripe reports you have 2 requests left, the local bucket drains down to 2. Immediately.

When the quota runs dry, behavior splits by priority class: **critical/interactive tasks** are blocked before touching the wire with [`exit 2`](../reference/exit-codes.md#exit-2); **background tasks** are parked safely with [`exit 6`](../reference/exit-codes.md#exit-6) and resume automatically at the reset epoch. Session fuel and per-call egress ceilings work the same way — every call metered, every byte counted. (How earmarks, priority classes, and preemption work: [budgets](../concepts/budgets.md).)

---

**Next:** incoming webhooks and triggers → [triggers.md](triggers.md)

**Need a human decision?** → [approvals.md](approvals.md)
