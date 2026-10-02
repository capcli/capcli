# The Administrative Cockpit

Capcli is a terminal animal. Every verb, every denial, every receipt is a line of text in a subshell.

But some days you want gauges. A frame tree instead of `--follow`. A causal DAG you can click through instead of a wall of JSON. A screen where the question your agent asked at 3pm is a card with buttons instead of an exit code.

That's the cockpit: a local web app the daemon serves, for looking at the kernel with human eyes.

---

## Open it

The cockpit is served by `capcli-daemon`. Ask the daemon how it's doing:

```bash
$ capcli sys serve --status
```

```text
[dev:tier_1]  capcli-daemon  ✓  serving

  addr:      127.0.0.1:4040
  cockpit:   embedded PWA bundle
  rpc:       POST /rpc · JSON-RPC 2.0
  ws:        /ws/audit · live leaf events
  vault:     sealed · AES-256-GCM
  audit:     sink ok · chain valid
```

Then open:

```
http://127.0.0.1:4040
```

(`capcli sys serve --start` brings the daemon up if status says otherwise; `--stop` and `--restart` do exactly what they claim.)

---

## What you're looking at

Eight functional layers, one screen. The cockpit is a **neutral kernel inspector** — it renders engine primitives, not domain abstractions. There is no "orders dashboard" here unless your world happens to be orders.

| Layer | What it shows |
|---|---|
| **1 · State Inspector** | Schema tables, columns, indexes — with format-preserved masked cells (`████`) anywhere secrets would otherwise bleed |
| **2 · Capability Inspector** | Routine catalog, version diffs, OpenAPI verb states, manifest-vs-fingerprint graphs |
| **3 · Policy & Governance** | Live authorizer rules, lockfile SHA-256 integrity, rate ceilings |
| **4 · Audit Spine** | Live streaming event tail, causal DAG trace explorer, machine denial decoders |
| **5 · Budget & Telemetry** | Call stack frame trees, fuel meters, wire byte counters, token-bucket drain gauges |
| **6 · Promotion & Approvals** | Staged routine promotions, DDL forward-migration previews, canary veto timers |
| **7 · Human Interaction (Ask)** | Structured question resolution cards with fail-closed timeout indicators |
| **8 · Vault & Biometrics** | Out-of-band credential injection, with mobile biometric / FaceID support |

The layers map onto things the CLI already knows how to tell you — schema, inspect envelopes, live rules, the audit tail, the budget cascade, promotions, asks, the vault. The cockpit isn't a second brain. It's the same brain, with better eyes.

---

## Zero authority, by construction

The PWA has no power. None. It ships no keys, holds nothing the kernel would miss, and never touches `workspace.db`.

Everything it shows and everything it does travels through two authenticated pipes:

```
┌──────────────────────────────────┐
│     ADMINISTRATIVE COCKPIT       │
│     PWA · zero authority         │
│     http://127.0.0.1:4040        │
└─────────┬───────────────┬────────┘
      POST /rpc        WS /ws/audit
      JSON-RPC 2.0     live leaf events &
      (ask, act)       frame transitions
          │                │
          ▼                ▼
┌──────────────────────────────────┐
│          capcli-daemon           │
│          127.0.0.1:4040          │
└────────────────┬─────────────────┘
                 │
                 ▼
       kernel · workspace.db · vault
```

- **`POST /rpc`** — every question and every action, as authenticated JSON-RPC 2.0. Responses come back in the same `{ exit, json, text }` envelope the CLI returns.
- **`/ws/audit`** — the live stuff: leaf events and frame transitions, streamed over WebSocket.

If the daemon is down, the cockpit is a very pretty blank page. And if the kernel would deny the CLI version of an action, it denies the cockpit version too — same enforcement path, same exit codes, same audit events. The browser adds pixels, not privileges.

### The four things you can actually do

- **Inspect** — drill from a causal op → routine manifest → budget frame → audit entry. One hop of the DAG per click.
- **Authorize** — sign off on a promotion candidate, or resolve a `ping ask` suspension and unfreeze the routine that asked.
- **Inject** — type a third-party secret straight into the encrypted in-memory daemon vault. The key crosses your eyeballs and the kernel's AES-256-GCM and nothing in between — never a guest script, never a terminal log.
- **Rollback** — trigger a snapshot restore. Mandatory dual confirmation; the cockpit will make you mean it.

---

## A cockpit, not an autopilot

It inspects and authorizes. It never flies.

The cockpit won't decide a promotion is probably fine. It won't pick an answer to an ask for you — it hands you the card, the options, and the fail-closed countdown, and *you* choose. And there's no big red button that fires an op into prod, because executing ops isn't one of its primitives. Every decision is yours; every decision is receipted; every risky verb carries a confirmation that makes the risk legible.

That's why it's called the Administrative Cockpit and not the Dashboard. Dashboards display. Cockpits have interlocks.

### Build your own, if you like

The RPC surface isn't private. External clients instantiate the same in-tree client module — `createClient({ endpoint, token, brand })` — over the same `/rpc` and tail transports. You can white-label it: custom name, tagline, even aliases for the surface nouns. One noun is locked: `sys` never gets aliased. The kernel keeps one name for itself.

---

## The One Rule

**The cockpit is a window, not a key.** It shows you everything and can do nothing the kernel wouldn't already allow — which is exactly why it's safe to leave open in a browser tab all day.

---

**The audit spine it renders** → [../understand/audit.md](../understand/audit.md)

**The asks it lets you resolve** → [../use/ask-human.md](../use/ask-human.md)

**The DAG explorer's favorite idea** → [provenance.md](provenance.md)
