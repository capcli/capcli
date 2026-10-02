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

## Invariants & Rules

* **Cron Interval Floor:** Minimum cron interval is 5 minutes (`*/5 * * * *`). Sub-5-minute schedules throw `exit 3`.
* **Reboot Catchup Law:** Maximum 1 catchup execution on daemon reboot. Stale missed runs are discarded.
* **Webhook Hard Limits:** Payload max 64 KB (65,536 bytes); arrival ceiling 100 events/minute. Oversized payloads return `413`.
* **Dead Letter Queue (DLQ):** Failed or throttled webhook dispatches persist in DLQ for 30 days or 1,000 items (FIFO purged).
* **Endpoint Server Floor:** Only **Pinned** routines can be served over HTTP (`trust: pinned`). Binds strictly to `127.0.0.1`.
* **Partner Key Cap:** Max 25 keys per workspace. Immortal keys are banned (90-day hard TTL).
* **Route verification:** External webhooks require a valid public `--ingress` URL or active tunnel; raw `127.0.0.1` ingress is denied.

---

## Live example: cron binding

```bash
$ capcli bind cron nightly_archive archive_old_orders "0 3 * * *" -m "archive orders older than 90 days"
```

```text
[dev:tier_1]  ✓  bound

  handle:     bind://nightly_archive
  trigger:    cron 0 3 * * *
  capability: cap://archive_old_orders@3
  catchup:    max 1 per reboot (stale runs discarded)
  next_fire:  03:00
```

## Live example: health check

```bash
$ capcli bind list
```

```text
[dev:tier_1]  2 bindings

  handle                 trigger    capability             state     health
  ─────────────────────  ─────────  ─────────────────────  ────────  ─────────
  bind://nightly_archive cron       archive_old_orders@3   active    41 fires · 68.3% ok
  bind://order_webhook   webhook    process_order@2        active    812 fires · 99.6% ok
```

68.3% is below the 70% success floor — the demotion circuit has opinions, and it files them automatically. Operation is reading this table and acting on the sad rows: [../../automate/operation.md](../../automate/operation.md).

---

**Narrative** → [../../use/inbox-and-triggers.md](../../use/inbox-and-triggers.md)
