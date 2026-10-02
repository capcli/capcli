# Command: capcli ping

Human IO — sensory notifications and structured, fail-closed inquiries. The approvals walkthrough lives in [approvals.md](../../workflows/approvals.md).

```bash
capcli ping <verb> [args] [--flags]
```

## Subcommands

| Verb | Syntax | Caller | Description |
|---|---|---|---|
| **notify** | `capcli ping notify <principal> "<msg>" --channel <c> -m "<why>"` | [both] | Sends an informational alert to configured channels. |
| **ask** | `capcli ping ask <principal> "<q>" --options "<opts>" [--timeout <t>] -m "<why>"` | [both] | Files a structured inquiry and suspends the caller until resolved. |
| **list** | `capcli ping list [--pending]` | [both] | Lists active and suspended inquiries. |
| **resolve** | `capcli ping resolve <ask-id> --choice <opt>` | [human] | Answers an inquiry, unfreezing the suspended routine. |
| **expire** | `capcli ping expire <ask-id>` | [both] | Manually expires an inquiry, triggering the fail-closed path. |

## The enum mandate

`ping ask` requires `--options` — discrete choices only. Free-text answers are physically banned: a hostile or hallucinated upstream can't inject instructions through a multiple-choice card. Option and token ceilings → [limits](../limits.md#human-io).

## Fail-closed deadlines

An expired or undeliverable inquiry is a denial — never an "assume yes." Default and maximum timeouts are [governed](../limits.md#human-io); on expiry the suspended routine resumes to an [exit 2](../exit-codes.md#exit-2) receipt.

## Quiet hours

Notifications are suppressed between [22:00 and 07:00](../limits.md#human-io) host time. `ping ask` bypasses quiet hours only when it is blocking a live routine — the suspension itself is the emergency.

## Invariants

* Every notify and ask is a mutating action: `-m` intent required.
* Resolutions ride the [audit spine](../audit.md) with full causal linkage back to the suspended frame.
* Ask cards render in the cockpit's resolution layer (see [cans/interface.md](../../../cans/interface.md) — Administrative cockpit PWA) and resolve through this surface.
