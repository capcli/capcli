# Command: capcli bind

Registers and governs inbound triggers — time crons, webhook listeners, and local reverse API endpoints. The trigger walkthrough lives in [triggers.md](../../workflows/triggers.md).

```bash
capcli bind <verb> [args] [--flags]
```

## Subcommands

| Verb | Syntax | Caller | Description |
|---|---|---|---|
| **cron** | `capcli bind cron <name> <capability> "<cron_expr>" -m "<why>"` | [both] | Registers an automated schedule. |
| **webhook** | `capcli bind webhook <name> <provider> <event> <capability> [--ingress <url>\|--tunnel] -m "<why>"` | [both] | Binds an inbound webhook with mandatory HMAC verification. |
| **endpoint** | `capcli bind endpoint <routine@version> --auth api-key [--rate <r>] [--channel all\|rest\|mcp]` | [both] | Serves a pinned routine over local HTTP and MCP. |
| **export** | `capcli bind export <openapi\|mcp> [--out <path>]` | [both] | Generates pure OpenAPI v3 or MCP JSON manifests. |
| **keys** | `capcli bind keys issue <name> --principal partner:<id>` | [human] | Issues a partner API key with a hard expiry. |
| **list** | `capcli bind list` | [both] | Displays active, paused, and dead bindings. |
| **inspect** | `capcli bind inspect <handle>` | [both] | Binding health and arrival rates. |
| **pause** | `capcli bind pause <handle>` | [both] | Suspends trigger processing. |
| **resume** | `capcli bind resume <handle>` | [both] | Resumes a paused trigger. |
| **remove** | `capcli bind remove <handle>` | [both] | Unbinds and archives the binding record. |

## Cron law

* Sub-5-minute schedules are refused at registration ([cron floor](../limits.md#triggers)).
* **Reboot catchup law:** a daemon restart fires at most one catchup execution — the missed backlog is discarded, never machine-gunned.
* Retiring a bound routine auto-disables its schedule, loudly.
* Schedules require reviewed trust; prod schedules require pinned — drafts can't give themselves a future.

## Webhook law

* Every event is signature-verified at the door — unsigned events are rejected.
* External ingress requires a valid public `--ingress` URL or an active tunnel; a raw `127.0.0.1` listener is denied.
* Payload size and arrival rates are [hard-capped](../limits.md#triggers); failures land in the dead-letter queue and are never silently dropped.

## Endpoint law (serve)

* Only **pinned** routines may serve HTTP, and only at an explicit version — `bind endpoint order_status@12`, never a moving target.
* The daemon binds strictly to `127.0.0.1`; public exposure lives behind your proxy.
* Inbound writes are denied by default and require opt-in; responses are capped ([serve ceilings](../limits.md#triggers)).
* Partner keys are human-issued and expire — immortal keys are banned ([key rotation](../limits.md#triggers)).

## Invariants

* Watch, schedule, and serve ceilings → [limits](../limits.md#triggers).
* Binding mutations are audit events (`bind.*`) on the [spine](../audit.md).
* The daemon split (CLI commits, axum daemon serves) is described in [sys.md](sys.md).
