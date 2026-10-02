# Command: `capcli doc`

The document path: bounded reading of workspace docs. The smallest noun, doing the humblest, most context-saving job in the CLI.

```bash
capcli doc <verb> [ptr] [--flags]
```

---

## Subcommands

| Verb | Syntax | Caller | Description |
|---|---|---|---|
| **`read`** | `capcli doc read <doc://ptr> [--max-tokens 100]` | `[harness]` | Reads a workspace doc, token-capped by default. |
| **`outline`** | `capcli doc outline <doc://ptr>` | `[harness]` | Emits the heading skeleton — decide before you digest. |

---

## Live examples

```bash
$ capcli doc read doc://refund-policy --max-tokens 100
```

```text
[dev:tier_1]  doc://refund-policy  100 tokens

  # Refund Policy
  Full refunds within 30 days. Partial after 30, requires
  supervisor approval for amounts > $500. Socks are final
  sale. (Yes, even the good ones.)

  tokens: 100 (truncated: true — full doc: 340 tokens)
```

```bash
$ capcli doc outline doc://refund-policy
```

```text
[dev:tier_1]  doc://refund-policy

  # Refund Policy
  ## Eligibility windows
  ## Approval thresholds
  ## Exceptions (socks)
```

---

## The contract, briefly

- **Default cap 100 tokens; 20 results per search.** Docs feed your context, so the noun treats your attention as a budget, not a buffet.
- **Pointers are `doc://`.** They surface in `capcli search` alongside capabilities and tables — same discovery, same registry.
- **Outline first, read second.** The heading skeleton costs ~nothing; the full doc costs its tokens. Choosing wisely is the whole game.
- **Truncation is flagged, never silent** — `truncated: true` tells you exactly how much reality you haven't read yet.

Why does this noun exist at all? Because "paste the entire 340-token policy into the prompt, then paste it again for a different question" is how context windows die. `doc read` is retrieval, not recitation — read the section you need, cite the pointer, move on.

---

**Where docs sit in the pointer family** → [../cli.md](../cli.md) · **Discovery** → [../../agents/discovery.md](../../agents/discovery.md)
