# Command: `capcli doc`

The 10th noun is a diet plan for your context window.

Docs in Capcli aren't files you mainline — they're pointers in the world (`doc://`), and the kernel serves them in capped token slices. Your harness reads 100 tokens of the relevant section instead of inhaling a 5MB README and forgetting why it opened the terminal.

```bash
capcli doc <verb> <ptr> [--flags]
```

---

## Subcommands

| Verb | Syntax | Description |
|---|---|---|
| **`read`** | `capcli doc read <ptr> [--max-tokens 100]` | Fetches a token-capped slice of a doc from the world. |
| **`outline`** | `capcli doc outline <ptr>` | Returns the heading skeleton — nodes, not prose. |

---

## 1. The Diet: `doc read`

```bash
$ capcli doc read cap://dispatch_order@4 --max-tokens 100
```

```text
[dev:tier_1]  cap://dispatch_order@4  ✓  100-token slice

  # dispatch_order

  Dispatch paid order to carrier and update status.

  ## Params
  - order_id: string — the paid order to dispatch
  - carrier:  string — carrier to hand off to

  ## Effect
  1. db.query    orders (read)
  2. api.call    logistics.shipments.create
  3. db.execute  orders (write)

  ## Guardrails
  Writes require intent (-m). Unbounded UPDATE/DELETE denied
  at AST before…

  truncated:  true (cap reached — raise --max-tokens, or start with doc outline)
```

The cap is the point. A capability's documentation is metered like every other resource: you get the slice you asked for, a truncation flag when there's more, and zero surprise blobs in your transcript. Reading more is a *decision*, not a default.

---

## 2. The Skeleton: `doc outline`

Before reading anything, look at its bones:

```bash
$ capcli doc outline doc://refund-policy
```

```text
[dev:tier_1]  doc://refund-policy  ✓

  type:    markdown spec
  tokens:  340
  outline:
    1. Eligibility windows
    2. Partial refund rules
    3. Stripe integration notes
    4. Edge cases
```

Four nodes instead of 340 tokens. If your harness only needs section 3, it reads section 3 — and `inspect` on a `doc://` pointer returns the same outline nodes, so the discovery loop stays uniform across every pointer type.

---

## 3. Why Slices Beat Blobs

The whole registry obeys one law: search returns pointers and summaries under 60 tokens, never raw payloads. `doc` is the reading end of that law.

1. **Discover:** `capcli search "refund"` → `doc://refund-policy "Business rules for refund eligibility"`.
2. **Skim:** `capcli doc outline` → four headings.
3. **Read:** `capcli doc read --max-tokens 100` → exactly the slice you need.

Need the whole thing on disk instead of in your face? The universal `--out <path>` flag redirects the payload to a file; stdout returns a minimal receipt. Your context window stays reserved for thinking.

---

## Invariants & Rules

* **Docs are world citizens.** `doc://` pointers cover markdown specs, playbooks, error codes, and rules — searchable like everything else in the registry.
* **Token caps are physics, not hints.** `--max-tokens` slices; oversized reads come back `truncated: true`.
* **Never a raw blob.** Outline first, leaf second. The kernel holds the whole document so your harness doesn't have to.

---

**Inspect before you read** → [../../use/inspect.md](../../use/inspect.md)

**Why small surfaces win** → [../../concepts/progressive-disclosure.md](../../concepts/progressive-disclosure.md)

**Find the doc in the first place** → [../../use/discover.md](../../use/discover.md)
