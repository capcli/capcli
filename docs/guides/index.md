# Guides

Something specific went wrong? You're in the right place.

The rest of this documentation is a journey. This section is a workbench. Nobody reads guides for pleasure — you arrive with a symptom, find your row, and leave with a command.

---

## Pick your row

| You're here because... | Go to |
|---|---|
| A command printed `✗ exit 2` — or 3, 5, or 6 — and you want the diagnosis, not a vibe. | [Troubleshooting →](troubleshooting.md) |
| State is wrong. A routine went sideways. You want yesterday's database back. | [Recovery →](recovery.md) |
| The schema has to change, and you'd prefer there be no fire drill. | [Migration →](migration.md) |
| You've used Capcli before, you're coming back, and you need to know where you left off. | [Returning to Capcli →](returning-to-capcli.md) |

---

## If you only have ten seconds

- Exit code in hand, need the law? → [exit-codes.md](../reference/exit-codes.md)
- Denial in hand? Read the `remedy:` line at the bottom. It is not decoration. → [boundaries.md](../use/boundaries.md)
- About to do something with teeth? Snapshot first: `capcli db snapshot -m "why"`. → [recovery.md](recovery.md)

---

## What guides are not

They're not the reference. When you need exact grammar — every flag, every field, every ceiling — that lives in [reference/](../reference/index.md).

And they're not the journey. If you're new here, or you want the mental model instead of the fix, start at [start/](../start/index.md) and walk forward.

---

## The house rule

Every failure in here is a receipt: the rule that fired, the statement that died, `state_modified: false`, and a `remedy:` line. Panic is for systems that don't tell you what they just prevented.

---

**On fire?** → [troubleshooting.md](troubleshooting.md)
