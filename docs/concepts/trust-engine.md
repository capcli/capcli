# The Trust Engine

Agents hallucinate safety. Capcli ignores claims and enforces an integer trust ladder:

```
[PINNED]    → Unattended production. Tier 1 Linux only.
   ▲
[REVIEWED]  → Supervised prod & live APIs. Survived sim replay.
   ▲
[DRAFT]     → Default entry. Sandboxed, no secrets, dev/sim only.
```

Trust is earned through deterministic simulation metrics — not prompts, human vibes, or `--force` flags. (Passing `--force` in Capcli is a syntax error. Don't embarrass yourself.)

Every routine, query, and API verb sits on exactly one rung, and the kernel — not the model — decides which one.

---

## The Three Rungs

### 1. Draft: Unproven

Every newly written routine, imported template, or freshly activated API verb starts here. Zero exceptions, zero inherited credit — a template that claims to be production-ready enters at draft anyway.

* **Rows affected:** capped at the draft ceiling — 10 rows, relaxed to 100 in dev for seeding, denied outright in prod ([figures](../reference/limits.md#database-ceilings)).
* **Secrets:** invisible. `SELECT value FROM secrets` throws [exit 2](../reference/exit-codes.md#exit-2) before a row returns.
* **Production:** physically banned. Running a draft routine in prod throws `exit 2` before bytecode even evaluates.
* **Network:** sandboxed socket jail ([sandboxing.md](sandboxing.md)).

Draft is a sandbox within the sandbox. The harness can make typos, hallucinate arguments, and fail all day. Reality won't notice.

---

<a id="reviewed"></a>

### 2. Reviewed: Proven in Sim

Code that passed rehearsal in the `sim` environment against masked, production-shaped data — real historical inputs, zero policy denials. It knows the rules and hasn't broken anything lately.

* **Rows affected:** the reviewed ceiling — 100 rows ([figures](../reference/limits.md#database-ceilings)).
* **Bulk queries:** unlocked. Mass updates work — `WHERE` and `LIMIT` stay mandatory.
* **Secrets:** masked credentials visible for outbound API egress.
* **Production:** allowed, but requires an active human supervisor. No headless crons yet.

---

### 3. Pinned: Unattended

Hardened, battle-tested code. Source and execution manifest are cryptographically hashed and version-locked (`cap://dispatch_order@4` — the `@4` is permanent; silent edits force a new version).

* **Rows affected:** the pinned ceiling — 500 rows ([figures](../reference/limits.md#database-ceilings)).
* **Unattended schedules:** `may_run_unattended: true` — crons and webhooks can fire at 03:00 with nobody watching.
* **Public endpoints:** only pinned routines can be served over HTTP to partners.
* **Audit level:** high-level summary — it runs so fast and so often that full payload dumps would drown the disk.

---

## How Code Earns Its Rung: The Auto-Promotion Math

You don't promote code by asking. To move a routine from draft to reviewed, the kernel runs a zero-tolerance conjunction against simulation history. Every metric must pass — fail one by 0.01% and auto-promotion aborts, routing the candidate to the human queue (`capcli routine pending` → [reference/cli/routine.md](../reference/cli/routine.md)). No negotiation.

| Metric | Threshold | Fail Result |
|---|---|---|
| **Invariant suite** | 100% pass | Rehearsal failure → human queue |
| **Success rate** | ≥ 95.0% | 94.9%? Blocked. No rounding up. |
| **Manifest match** | 100% subset | Executed a single undeclared query? Denied. |
| **Policy denials** | Exactly 0 | Hit one authorizer wall? Back to the drawing board. |
| **Fingerprint drift** | Exactly 0 | Runtime leaf divergence → denied. |
| **Latency ceiling** | p95 ≤ 70% of declared max duration | Too slow in sim? Denied. |

---

## The 1-Hour Parole Window (Canary Veto)

Congratulations — the conjunction passed and the routine was promoted. It's live.

**Now it's on parole.**

The moment a routine is promoted, the kernel starts a silent **60-minute canary timer**:

```
Promotion Approved
        │
        ▼
┌───────────────────────────────┐
│   1-Hour Canary Telemetry     │
│   (Watches error rates & ops) │
└───────────────┬───────────────┘
                │
     ┌──────────┴──────────┐
     ▼                     ▼
Any anomaly spike?     Clean 60 mins?
     │                     │
AUTONOMOUS DEMOTION   PERMANENT RUNG
(Back to Draft)       (Survives parole)
```

If the routine triggers a policy denial, latency spike, or runtime panic during those first 60 minutes, the kernel doesn't page you. It fires an **autonomous circuit breaker**, cancels the promotion, and drops the routine straight back to `draft`.

You fix the bug. You try again.

---

## Tier 2: The Pinned Ceiling

Pinned execution requires hardware-level containment: unprivileged Linux namespaces and syscall trapping via `seccomp-bpf`. Hosts without those primitives — macOS, Windows native, Termux — are classified [Tier 2 (degraded isolation)](sandboxing.md#tiers): draft and reviewed run fine in dev and sim, but invoking a pinned routine there throws [exit 2](../reference/exit-codes.md#exit-2) (`E045_TIER2_PINNED_DENIED`). The machine invariant row: [reference/limits.md#invariants](../reference/limits.md#invariants).

It isn't elitism; it's physics. Write code on your Mac, rehearse it in sim on your Mac — but when it's time to run unattended against live production state, it runs on Linux.

---

<a id="training-wheels"></a>

## Training Wheels for APIs

When your agent activates a brand-new external API verb (e.g. `stripe.refund_charge`) that has no simulation mock fixture, it gets tagged with **training wheels**:

* The first calls must pass synthetic contract replay proofs against historical audit logs.
* On **call 4**, the verb automatically graduates to standard governance.

The system assumes every new external effect is a potential disaster until proven routine. The step-by-step workflow — including the vault that feeds it — lives in [workflows/apis.md#training-wheels](../workflows/apis.md#training-wheels).

---

**See the rung on any capability:** → `capcli inspect cap://dispatch_order@4`
**Watch a routine climb the ladder end-to-end:** → [workflows/routines.md](../workflows/routines.md)
