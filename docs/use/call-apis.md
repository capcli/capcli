# Call APIs

Your agent wants to talk to Stripe, Twilio, or GitHub. 

Left to its own devices, an LLM will ask you to paste your live production secret into a chat prompt, write a broken `curl` command, burn your token context with 4,000 lines of Swagger JSON, and wake you up at 3:00 AM with a rate-limit meltdown.

In Capcli, external APIs are governed with the exact same ruthless physics as the database. 

Here is how your agent talks to the outside world without setting the company on fire.

---

## 1. Discovery: The Dormant Catalog

You do not paste giant OpenAPI JSON specs into your LLM prompt. That gives the model amnesia and burns your context window for zero reason.

Instead, sync the vendor spec once:

```bash
$ capcli api sync stripe https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.yaml
```

The kernel compiles the endpoints into `apis/stripe.yaml`. Every endpoint enters the registry as **dormant**:

```bash
$ capcli search "refund"
```

```text
[dev:tier_1]  2 results

  cap://stripe.refund_charge    api-verb   dormant   "Issue partial or full Stripe refund"
  cap://order_refund@4          routine    reviewed  "Process cancelled order and archive"
```

Notice the pointer: **`cap://`**, not `api://`. 

To the kernel, anything runnable is a capability. Whether it’s a local TypeScript routine or an external Stripe endpoint, the interface is identical: you search it, you inspect it, you run it.

**Dormant means:**
* Zero token cost to your agent’s context window.
* Fully discoverable via search.
* **Physically uncallable** until deliberately activated.

---

## 2. Wake It Up: Activation & Training Wheels

Your agent cannot fire off random endpoints. It must activate the verb and declare its causal motivation:

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

### The 3-Call Training Wheels Rule
You don't let an autonomous agent wake up a live payment endpoint and immediately start blasting money.

* **Calls 1, 2, and 3:** The kernel forces the verb through synthetic contract replays against historical audit logs in simulation. 
* **Call 4:** If it didn't violate payload schemas or trigger rate limits, it auto-graduates to standard governance.

---

## 3. The Missing Key Trap: Cockpit-Only Injection

Never paste your live API keys into a chat terminal unless you want your credentials leaked into LLM training logs, bash histories, and subshell environments. 

Watch what happens when the agent tries to run an endpoint before credentials exist:

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

The kernel refuses to execute (`exit 3`). It does not prompt the agent to read the key, and it does not allow the agent to accept the key string.

### What the harness does next:
Your agent reads the `remedy` and talks directly to you:

> *"I need credentials for Stripe to execute this refund. I am not allowed to see or handle your secret key. Please open the Cockpit at http://127.0.0.1:4040/vault and inject `stripe_secret`."*

You open the local Administrative Cockpit in your browser, authorize via your browser or mobile FaceID, and paste the key directly into the encrypted AES-256-GCM vault. 

Now, the agent retries:

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

The Rust egress proxy injected `Authorization: Bearer sk_live_...` into the HTTP header at the wire boundary. The moment the response returned, the memory buffer holding the plaintext secret was **overwritten with zeros (`zeroize`)**. 

The agent got its refund ID. It never touched the key.

---

## 4. Kill the `while(True)` Loop: `poll_until`

Agents love writing infinite sleep loops while waiting for asynchronous jobs (like a webhook, container build, or video render):

```python
# THE WRONG WAY: Agent burns 40 ops and dies of budget exhaustion
while True:
    res = ctx.api.call("video.status", {"id": job_id})
    if res.ready: break
    time.sleep(2) # KILLED: exit 2 (policy.budget.ops_exhausted)
```

In Capcli, writing busy-waiting sleep loops in guest code is a quick way to get your routine killed by the watchdog.

Use the kernel primitive inside your routines:

```python
# THE CAPCLI WAY: Slept in the Rust runtime, counts as ONE operation
res = ctx.api.poll_until(
    verb="video.status",
    params={"id": job_id},
    condition="res.status == 'completed'",
    timeout_s=30,
    interval_s=2
)
```

The guest interpreter suspends cleanly. The compiled Rust kernel manages the network polling and sleep intervals. 

A 30-second polling cycle that makes 15 HTTP checks counts as **exactly 1 aggregate primitive op** against your op budget.

---

## 5. Proactive Rate Limits & Dynamic Header Scraping

Most HTTP libraries blast requests blindly until they slam face-first into an HTTP `429 Too Many Requests`.

Capcli stops the blast before the request leaves your machine:

1. **Client-Side Token Bucket:** Capcli regulates outbound cadences locally (default: 60 burst capacity, 1.0 token/second steady refill).
2. **Dynamic Header Scraping:** When remote APIs respond, Capcli scrapes standard rate headers (`X-RateLimit-Remaining`) or nested JSON headers (like Meta's `X-Business-Use-Case-Usage` via JSONPath).
3. If Stripe reports you only have 2 requests left, Capcli forcefully drains the local token bucket down to 2.

### What happens when the quota runs dry?
* **Critical / Interactive Tasks:** Blocked before touching the wire with **`exit 2` (Denied)**.
* **Background Tasks:** Suspended safely with **`exit 6` (Yield)**. The frame is parked in `_suspended_tasks` until the reset epoch, then resumed automatically by the daemon.

---

## The One Rule

**Your agent requests the effect. The human provides the key via Cockpit. The kernel meters the wire.**

No leaked tokens in terminal logs. No runaway polling loops. No unmetered requests.

---

**Next:** Handle incoming webhooks and async queues → [inbox-and-triggers.md](inbox-and-triggers.md)  
**Need a human decision on something else?** → [ask-human.md](ask-human.md)
