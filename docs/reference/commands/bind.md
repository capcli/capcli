# Command: `capcli bind`

Registers and governs inbound triggers: time crons, webhook listeners, and local reverse API endpoints.

```bash
capcli bind <verb> [args] [--flags]
```

---

## Subcommands

| Verb | Syntax | Description |
|---|---|---|
| **`cron`** | `capcli bind cron <name> <capability> "<cron_expr>" -m "<why>"` | Registers automated cron schedule. |
| **`webhook`** | `capcli bind webhook <name> <provider> <event> <capability> [--ingress <url>] -m "<why>"` | Binds inbound webhook with mandatory HMAC verification. |
| **`endpoint`**| `capcli bind endpoint <routine@version> --auth api-key [--rate <r>] [--channel all\|rest\|mcp]` | Serves a pinned routine over local HTTP and MCP. |
| **`export`** | `capcli bind export <openapi\|mcp> [--out <path>]` | Generates pure OpenAPI v3 or MCP JSON manifests. |
| **`keys`** | `capcli bind keys issue <name> --principal partner:<id>` | Issues partner API keys with mandatory 90-day expiry. |
| **`list`** | `capcli bind list` | Displays active, paused, and dead bindings. |
| **`inspect`** | `capcli bind inspect <handle>` | Inspects binding trigger health and arrival rates. |
| **`pause`** | `capcli bind pause <handle>` | Temporarily suspends trigger processing. |
| **`resume`** | `capcli bind resume <handle>` | Resumes paused trigger processing. |
| **`remove`** | `capcli bind remove <handle>` | Unbinds trigger and archives binding record. |

---

## In Practice

A nightly cleanup, bound with intent — and the registry view that proves it took:

```bash
$ capcli bind cron nightly-cleanup cap://cleanup_stale@2 "0 3 * * *" \
    -m "purge stale claims nightly"
```

```text
[dev:tier_1]  ✓  bound

  handle:     bind://nightly-cleanup
  schedule:   0 3 * * * (daily at 03:00)
  target:     cap://cleanup_stale@2
  next_fire:  tomorrow 03:00
  audit:      op_b41a
```

```bash
$ capcli bind list
```

```text
[dev:tier_1]  2 bindings

  handle                  type     target                           state
  ──────────────────────  ───────  ───────────────────────────────  ──────
  bind://nightly-cleanup  cron     cap://cleanup_stale@2            active
  bind://stripe_disputes  webhook  cap://freeze_disputed_account@2  active
```

The binding is itself an audit event (`bind.create` with `target_urp`, `trigger_type`, `schedule_or_source`) — the hash chain advances the moment the schedule exists. There are no ghost triggers.

---

## Invariants & Rules

* **Cron Interval Floor:** Minimum cron interval is 5 minutes (`*/5 * * * *`). Sub-5-minute schedules throw `exit 3`.
* **Reboot Catchup Law:** Maximum 1 catchup execution on daemon reboot. Stale missed runs are discarded.
* **Webhook Hard Limits:** Payload max 64 KB (65,536 bytes); arrival ceiling 100 events/minute. Oversized payloads return `413`.
* **Dead Letter Queue (DLQ):** Failed or throttled webhook dispatches persist in DLQ for 30 days or 1,000 items (FIFO purged).
* **Endpoint Server Floor:** Only **Pinned** routines can be served over HTTP (`trust: pinned`). Binds strictly to `127.0.0.1`.
* **Partner Key Cap:** Max 25 keys per workspace. Immortal keys are banned (90-day hard TTL).
