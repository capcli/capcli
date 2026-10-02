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

## In Practice

```bash
$ capcli ping ask human:ops "Refund ORD-9912 at 50 USD?" \
    --options "yes|no|escalate" \
    --timeout 60 \
    -m "customer complaint"
```

```text
[dev:tier_1]  ✓  filed (ask_31e8d)

  ask_id:     ask://ask_31e8d
  to:         human:ops
  question:   "Refund ORD-9912 at 50 USD?"
  options:    [yes, no, escalate]
  timeout_at: 16:41:09 (60m remaining)
  status:     pending — caller turn suspended, fail-closed on expiry
```

Three options — well under the 5-option ceiling. Question comfortably under the 100-token cap. Timeout at the 60-minute default. The caller's turn suspends on the spot, and if nobody answers, silence means *no* — never "probably yes."

---

## Invariants & Rules

* **Anti-Injection Enum Mandate:** `ping ask` requires `--options` (max 5 discrete choices). Free-text answers are physically banned.
* **Token Ceilings:** Questions capped at 100 tokens. Notification messages capped at 300 tokens. Max 3 notification channels.
* **Fail-Closed Deadlines:** Default timeout is 60 minutes (max allowable: 480 min). Expired inquiries exit with **`exit 2` (Denied)**.
* **Quiet Hours:** 22:00 to 07:00 host time. `ping notify` is suppressed. `ping ask` bypasses quiet hours only if blocking a live routine.
