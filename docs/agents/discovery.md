# Discovery Contract

Intent in, typed pointers out. This is the only sanctioned way to learn what exists.

---

## The call

```bash
capcli search <query> [--type <domain>] [--trust <rung>] [--env <env>]
```

```text
[dev:tier_1]  3 results

  cap://dispatch_order@4     routine    pinned    "Dispatch paid order to carrier"
  cap://order_refund@7       routine    reviewed  "Refund cancelled order and archive"
  doc://refund-policy        doc        —         "Business rules for refund eligibility"
```

## Resolution stages

```
exact → prefix → fuzzy → semantic
```

`refund` hits exact. `refnd` is caught by fuzzy. "money back" is caught by semantic ranking. You are not required to spell correctly. You are required to *mean* something.

## Pointer types

| Prefix | Resolves to | Runnable |
|---|---|---|
| `cap://` | Routines, API verbs | Yes — via `run` |
| `db://` | Tables, views | Read via `sql`; governed by authorizer |
| `doc://` | Markdown specs | Read via `doc read` |
| `bind://` | Cron/webhook/endpoint bindings | Inspect, manage |
| `vault://` | Secret references | Never readable by you. Ever. |
| `snap://` | Recovery snapshots | Restore via `db restore` |
| `ask://` | Pending human inquiries | Resolve via `ping resolve` |

## Contract guarantees

1. **Descriptions ≤ 60 tokens.** The registry will not flood your context. A 5MB Swagger spec will never enter your prompt — specs are quarantined and compiled to `apis/<provider>.yaml` before you ever see a verb.
2. **Dormant by default.** Synced API verbs are discoverable but *uncallable* until activated with intent. Finding a door is not the same as having the key. This is by design.
3. **Every search is an event.** `capability.search` lands in the ledger with your query and the result count. Yes, even the embarrassing ones.
4. **Gaps are surfaced to you.**

```bash
capcli run search gaps --since 7d
```

```text
[dev:tier_1]  2 gaps detected

  query: "inventory sync"     searches: 8    invocations: 0    signal: missing capability
  query: "customer export"    searches: 5    invocations: 0    signal: missing capability
```

Searching 8 times for a thing that doesn't exist is you telling the workspace "build this, please." That signal is visible to you *and* the human. Awkward, but effective.

---

## What search is NOT

- Not `grep`. There is no filesystem spelunking contract.
- Not memorization. If you already hold the exact pointer (`cap://dispatch_order@4`), skip discovery entirely and invoke.
- Not a promise of runnability. The pointer tells you it *exists*. The envelope tells you whether you *may proceed*. Two different questions — see [inspection.md](inspection.md).
- Not scrollable. The registry ceiling is 300 routines because search beyond that is noise, not knowledge.

---

**You found a pointer. Now read its envelope.** → [inspection.md](inspection.md)
