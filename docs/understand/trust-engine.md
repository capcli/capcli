# The Trust Engine

Your AI agent will look you dead in your virtual eyes and say, *"I have thoroughly tested this script, it is completely safe to run in production."*

Then it drops your production customer table because it got confused by a subquery.

In Capcli, **trust is not a feeling, a prompt, or an apology.** Trust is an integer ladder backed by cold, unblinking math. You don't grant trust because an LLM sounds confident; the kernel grants trust when code survives simulation without breaking a single physical law.

---

## The Three Rungs

Think of trust as security clearances for code. Every routine, query, and API verb sits on one of three rungs:

```
[ PINNED ]    → Battle-hardened machine. Runs unattended at 3 AM.
     ▲
[ REVIEWED ]  → Proven intern. Survived simulation; allowed to touch real APIs.
     ▲
[ DRAFT ]     → Toddler with plastic scissors. Can't touch prod, can't see secrets.
```

---

### 1. Draft: Toddler Mode
Every newly written routine, imported template, or freshly synced API verb starts here. Zero exceptions.

* **Max rows affected:** 10 (Dev allows 100 so you can seed test data without crying).
* **Secrets:** Completely invisible. Try to `SELECT value FROM secrets` and the C authorizer laughs in your face (`exit 2`).
* **Production:** Physically banned. Running a draft routine in `prod` throws `exit 2` before the code even compiles.
* **Network:** Sandboxed socket jail.

Draft is your sandbox within a sandbox. The harness can make typos, hallucinate arguments, and fail all day. Reality won't notice.

---

### 2. Reviewed: The Proven Intern
Code that passed rehearsal in the `sim` environment. It knows the rules and hasn't broken anything lately.

* **Max rows affected:** 100 rows.
* **Bulk queries:** Unlocked. Mass updates work (with mandatory `WHERE` and `LIMIT`).
* **Secrets:** Can access masked credentials for outbound API egress.
* **Production:** Can run in prod, but **requires an active human supervisor** (no headless cron jobs yet).

---

### 3. Pinned: The Autopilot
Hardened, battle-tested code. The routine's source code and its execution manifest are cryptographically hashed and version-locked (`dispatch_order@4`).

* **Max rows affected:** 500 rows.
* **Unattended schedules:** Can be wired to automated crons and webhooks (`may_run_unattended: true`).
* **Public endpoints:** Only pinned routines can be served over HTTP to partners.
* **Audit level:** High-level summary (it runs so fast and so often that full payload dumping would drown the disk).

---

## How Code Earns Its Wings: The 5-Point Math

You don't promote code by typing `--force`. (Fun fact: passing `--force` in Capcli is an immediate syntax error. Don't embarrass yourself).

To auto-promote a routine from `draft` to `reviewed`, the kernel runs a zero-tolerance conjunction algorithm against simulation history. **Every single metric must pass:**

| Metric | Threshold | Fail Result |
|---|---|---|
| **1. Invariant Suite** | `100% pass` | Rehearsal failure $\rightarrow$ human queue |
| **2. Success Rate** | $\ge 95.0\%$ | 94.9%? Blocked. No rounding up. |
| **3. Manifest Match** | `100% subset` | Executed a single undeclared query? Denied. |
| **4. Policy Denials** | **Exactly 0** | Hit one AST wall? Back to the drawing board. |
| **5. Fingerprint Drift** | **Exactly 0** | Runtime leaf divergence $\rightarrow$ Denied. |
| **6. Latency Ceiling** | $\text{p95} \le 70\%$ of max timeout | Too slow in sim? Denied. |

Fail even one check by 0.01%? Auto-promotion aborts, and the candidate gets tossed into the human approval queue (`capcli routine pending`). No negotiation.

---

## The Tier 2 Permanent Nerf (Mac & Windows Tears)

Here is a cold, hard pill to swallow:

If you are developing on a **MacBook Pro, Windows machine, or Android Termux**, your machine is classified as **Tier 2 (Degraded Isolation)**.

```bash
$ capcli run dispatch_order@4 --env prod
```
```text
[prod:tier_2]  ✗  exit 2

  FAIL  E045_TIER2_PINNED_DENIED
        Pinned execution refused on Tier 2 host.
        macOS does not support unprivileged user namespaces (bwrap).
```

### Why?
It’s not elitism; it’s physics. 

Running a `pinned` production routine unattended requires hardware-level containment: unprivileged Linux namespaces (`bwrap`) and system-call trapping via `seccomp-bpf` (trapping raw socket calls at syscall 42). 

macOS and Windows simply do not have unprivileged kernel namespaces. An agent running locally on Darwin can bypass network proxies if it tries hard enough.

### The Rule
* **Tier 1 (Linux bare-metal, VPS, Docker with userns, WSL2):** Can run everything (`draft`, `reviewed`, `pinned`).
* **Tier 2 (macOS, Windows native, Termux):** Hard-capped at **Reviewed** in `dev` and `sim`.

You write code on your Mac. You test it in simulation on your Mac. But when it's time to pin it to live production state, it runs on Linux. Physics wins every time.

---

## Un-simulated APIs

When your agent calls a brand new external API verb (e.g. `stripe.refund_charge`) that has no simulation fixture:

* There is no activation gate and no human sign-off — the verb is governed by its declared **`sim_mode`** from day one.
* If `apis/<provider>.sim.yaml` exists, calls route to the provider sandbox; without one, the verb falls back to schema-validating **`dry-run`** responses (`{ "simulated": true }`).
* Verbs marked **`prod-only`** are physically denied in `dev` and `sim` by the authorizer — they can only ever touch the live wire in `prod`.

The system assumes every new external effect is a potential disaster until its simulation mode says otherwise.

---

## The One Rule

**Prompts ask for trust. Physics enforces it.**

Never rely on an agent promising to be careful. Check its rung, inspect its manifest, and let the kernel handle the leash.

---

**Want to see what happens when trust is breached?** → [boundaries.md](../use/boundaries.md)  
**Inspect an envelope before running it?** → [inspect.md](../use/inspect.md)
