# Command: `capcli ping`

Governs asynchronous human interaction, sensory alerts, and structured suspension inquiries.

```bash
capcli ping <verb> [args] [--flags]
```

---

## Subcommands

| Verb | Syntax | Description |
|---|---|---|
| **`notify`** | `capcli ping notify <principal> "<msg>" --channel <c> -m "<why>"` | Sends an informational alert to configured channels. |
| **`ask`** | `capcli ping ask <principal> "<q>" --options "<opts>" [--timeout <t>] -m "<why>"` | Files a structured human inquiry and pauses caller turn. |
| **`list`** | `capcli ping list [--pending]` | Lists active and suspended human inquiries. |
| **`resolve`**| `capcli ping resolve <ask-id> --choice <opt> [-m "<why>"]` | Resolves an inquiry, unfreezing the suspended routine. |
| **`expire`** | `capcli ping expire <ask-id>` | Manually expires an inquiry, triggering fail-closed denial. |

---

## Invariants & Rules

* **Anti-Injection Enum Mandate:** `ping ask` requires `--options` (max 5 discrete choices). Free-text answers are physically banned.
* **Token Ceilings:** Questions capped at 100 tokens. Notification messages capped at 300 tokens. Max 3 notification channels.
* **Fail-Closed Deadlines:** Default timeout is 60 minutes (max allowable: 480 min). Expired inquiries exit with **`exit 2` (Denied)**.
* **Quiet Hours:** 22:00 to 07:00 host time. `ping notify` is suppressed. `ping ask` bypasses quiet hours only if blocking a live routine.

---

## Live example: the structured question

```bash
$ capcli ping ask user:ops-lead "Wipe demo data in dev environment?" \
    --options "approve,reject" \
    --timeout 30 \
    -m "confirm staging reset before testing"
```

```text
[dev:tier_1]  ⏳  suspended (ask_99d1a)

  ask_id:     ask://ask_99d1a
  to:         user:ops-lead
  question:   "Wipe demo data in dev environment?"
  options:    [approve, reject]
  timeout_at: 14:32:10 (30m remaining)
  status:     pending
```

Enumerated options only — an open-ended "what do you think?" to a 3am on-call human is how you get "sure" as an architecture decision. Expiry fails *closed*: no answer means no mutation, `exit 2`, state untouched.

---

**Narrative** → [../../use/ask-human.md](../../use/ask-human.md) · **Agent-side rules** → [../../agents/feedback.md](../../agents/feedback.md)
