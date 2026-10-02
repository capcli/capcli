# Output Contract

What comes back, in what shape, and why it never surprises your parser.

---

## The prefix law

Every output stream — human table or machine envelope — begins with the environment banner:

```text
[dev:tier_1]  dispatch_order@4  ✓  1.2s
```

```text
[prod:tier_2]  ⚠ host.degraded_isolation
```

`[env:tier]` is stamped on *everything*, on every line that matters, because "which world am I in" is the first question of every incident review, and now it's the first *answer* too.

## Two formats, zero hybrids

**Human:** tables, aligned columns, `✓` / `✗`, plain prose denials. Rendered via native terminal diagnostics (miette + codespan, rustc-style). No filler, no decorative ASCII.

```text
[dev:tier_1]  ✓  12ms

  rows: 10
  id          total    status
  ──────────  ───────  ───────
  ord_9921    142.00   pending
  ord_9918    89.50    pending
```

**Machine:** `--json`, always a pure envelope with stable keys:

```json
{
  "domain": "policy.query",
  "culprit": "UPDATE orders SET status = 'shipped' WHERE status = 'processing'",
  "remedy": "add LIMIT, or target specific primary key",
  "state_modified": false,
  "decision": "denied",
  "exit": 2
}
```

No pretty-printing surprises, no "informative warnings" interleaved into your data stream. Stdout and stderr are buffer-isolated — raw stdio is *never* logged into the audit spine; the kernel hashes a canonical JSON outcome instead. Your terminal noise does not become your audit trail.

## The denial format, exactly

Text denials follow a fixed shape:

```text
  FAIL  <rule code>
        <rejected statement>
        <caret line pointing at the culprit>
        <human explanation>

  state_modified: false
  layer: <AST | authorizer | trust | budget | vault | …>
  remedy: <the sanctioned next action>
```

JSON denials carry the same fields under the keys above. `remedy` is always present. It is always actionable. If you find yourself guessing after reading a denial, that's a bug — file it.

## Payload redirection

`--out <path>` writes the payload to disk; stdout collapses to a minimal receipt under 30 tokens:

```text
[dev:tier_1]  ✓  written → out/results.json (12 rows)
```

Move bulk through files. Recite nothing. Your context window is a budget too — [budgets.md](../understand/budgets.md) explains how literally the kernel takes this.

## Truncation

Routine results cap at 500 result tokens. Overflow is truncated and flagged:

```text
  summary: 500 tokens (truncated: true)
```

Filter in SQL, project narrow columns, paginate with `LIMIT`. Do not `SELECT *` your way into a stub. The cap protects the model's attention span, which — historically — needs the protection.

## Streaming

`capcli sys audit tail --follow` streams events as they hash. `--since 1h`, `--capability <urp>` filter it. Diagnostics carry latency SLAs, not vibes.

---

**The integers that end every command** → [exit-codes.md](exit-codes.md)
