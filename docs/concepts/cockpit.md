# The Administrative Cockpit

Your browser's one job in this architecture: `http://127.0.0.1:4040`.

The CLI is the machine surface. The Cockpit is the *human* surface — a local-only web cockpit for live telemetry, approvals, and the one place a secret is ever allowed to be pasted. It binds strictly to loopback; it is never exposed, and partner traffic never touches it (partners get `bind endpoint` + 90-day keys instead).

---

## Starting it

```bash
$ capcli sys serve --start
```

```text
[dev:tier_1]  ✓  daemon running

  cockpit:    http://127.0.0.1:4040
  daemon:     axum · pid 4117
  channels:   rest · mcp
```

`--status`, `--restart`, `--stop` manage the daemon that owns the Cockpit *and* the IPC surface your `capcli sql` calls ride on. If the daemon is down, your terminal politely refuses to run unaudited work — which is the theme of this entire product.

## What's in it

| Surface | What you do there |
|---|---|
| **Live telemetry** | Session ops, budget frames, rate buckets, binding health — the `bind list` table with charts |
| **Trust receipts** | The `sys doctor --report` view: `ledger_root_hash`, `policy_denials`, `sleep_score` |
| **Audit stream** | `sys audit tail --follow` rendered as a scroll, filterable by capability |
| **Pending asks** | The `ask://` queue — approve/reject with enumerated options, no free-text roulette |
| **Vault** | The *only* sanctioned place to inject secrets |
| **Approvals** | Queued promotions (`ship --queue`), first-prod-call watchpoints |

## The vault rule, exactly once

Secrets enter via the Cockpit or they don't enter. When a capability needs a credential your agent doesn't have:

```text
[dev:tier_1]  ✗  exit 3

  FAIL  policy.secrets.missing
        capability: cap://stripe.refund_charge
        secret_ref: vault://stripe_secret
        ...
  remedy: prompt human supervisor to inject credential via Cockpit (http://127.0.0.1:4040/vault)
```

The denial *tells your agent what to say to you*. You open the Cockpit, authorize (browser or mobile FaceID), paste the key into the AES-256-GCM vault. From then on: the kernel decrypts at the wire proxy, injects at dispatch, and zeroes the plaintext buffer immediately after. Your agent never sees the key — not in a prompt, not in a log, not in a `print()` statement it "needed for debugging."

The alternative workflow — paste prod secrets into a terminal chat — is how credentials end up in LLM training logs, bash histories, and a security team's group chat. The Cockpit exists so that sentence stays hypothetical.

## Why a web UI at all?

Because some jobs are *inherently* human-shaped: squinting at a diff, approving a promotion queue, pasting a secret, watching a 03:00 fire resolve. The terminal is for verbs; the Cockpit is for *judgment calls* — the ones where a table with a confirm button genuinely beats a `-y` flag.

And it's local-only, auth-gated, and behind the same audit spine as everything else — even your clicks leave receipts here. Especially your clicks.

---

**Next** → [progressive-disclosure.md](progressive-disclosure.md)
