# Command: capcli doc

Progressive disclosure over long documents — specs, playbooks, error codes, and rules addressed as `doc://` pointers. You pull what you need, not the whole blob.

```bash
capcli doc <verb> <ptr> [--flags]
```

## Subcommands

| Verb | Syntax | Caller | Description |
|---|---|---|---|
| **read** | `capcli doc read <ptr> [--max-tokens 100]` | [both] | Fetches the targeted leaf content, token-capped. |
| **outline** | `capcli doc outline <ptr>` | [both] | Returns the structural outline — sections, not prose. |

## The pattern

```bash
$ capcli inspect doc://refund-policy
```

```
[dev:tier_1]  doc://refund-policy

  type:       markdown spec
  tokens:     340
  outline:
    1. Eligibility windows
    2. Partial refund rules
    3. Stripe integration notes
    4. Edge cases
```

You see the shape first. If you need one section, you fetch it leaf-first:

```bash
$ capcli doc read doc://refund-policy --max-tokens 100
```

Reading order matters: `search` returns pointers and summaries (capped by the [description budget](../limits.md#routine-shape)), `inspect` returns the outline, `doc read` returns the targeted content. Each step costs the minimum tokens necessary — the point is keeping model context lean while the full document stays on disk.

## Invariants

* `doc://` is a first-class URP type — docs are inspectable, searchable, and referenceable like any capability ([pointer standard](index.md)).
* Reads are free; the token cap is caller-controlled and the default is deliberately small.
