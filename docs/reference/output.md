# Output Contracts

Every stream Capcli emits obeys the same three laws: it tells you where you are, it tells you what happened, and it never lies about state. The exactness is load-bearing — your harness parses this — so the whimsy stays in the prose and never in the payload.

---

## The prefix law

Every output stream — success, denial, warning — is prepended with the execution context:

```
[<env>:<tier>]
```

| Prefix | Meaning |
|---|---|
| `[dev:tier_1]` | dev, hardened host (Linux bare-metal, VPS, Docker, WSL2) |
| `[sim:tier_1]` | simulation, hardened host |
| `[prod:tier_1]` | production, hardened host |
| `[dev:tier_2]` | dev on a degraded-isolation host (macOS, Termux, Windows native) |

You never have to wonder which world a result came from. The first characters of the line tell you.

---

## The first line

The first line of any result carries the verdict, with two-space separators:

```
[env:tier]  <subject>  ✓  <detail>      success
[env:tier]  <subject>  ✗  exit <n>      failure
```

Success, from the hot path:

```bash
$ capcli run dispatch_order -p order_id=ORD-8842 -p carrier=fedex \
    -m "fulfill paid order for customer checkout"
```

```
[dev:tier_1]  dispatch_order@4  ✓  1.2s

  status:    dispatched
  tracking:  794644790133
  ops_used:  3/8
  audit:     op_9f2c → op_9f2d → op_9f2e
```

Failure — same shape, opposite verdict:

```bash
$ capcli sql "DELETE FROM orders"
```

```
[dev:tier_1]  ✗  exit 2

  FAIL  policy.query.update_delete.require_where
        DELETE FROM orders
        ^^^^^^^^^^^^^^^^^^
        Missing WHERE clause. Unbounded delete denied.

  state_modified: false
  remedy: add WHERE + LIMIT, or use chunked loop via ctx.db.execute
```

Fields are indented two spaces and aligned `key:  value`. Denials add `FAIL <rule.id>`, a caret line under the offending syntax, `state_modified: false`, and a `remedy` line. The full denial anatomy lives in [errors.md](errors.md).

---

## Tables for humans, envelopes for machines

Humans receive tables. Agents pass `--json` and get the same facts as a pure envelope — no prose, no filler, no decorative characters to strip:

```bash
$ capcli sql "DELETE FROM orders" --json
```

```json
{
  "exit": 2,
  "json": {
    "domain": "policy.query.update_delete.require_where",
    "culprit": "DELETE FROM orders",
    "remedy": "add WHERE + LIMIT, or use chunked loop via ctx.db.execute",
    "state_modified": false
  },
  "text": "[dev:tier_1]  ✗  exit 2"
}
```

The return envelope is always `{ exit: number, json: object, text: string }`, and the machine diagnostic inside it carries four guaranteed keys: `domain`, `culprit`, `remedy`, `state_modified`. Whether your consumer is a shell script, a harness, or the cockpit PWA, that is the shape of truth.

Human-facing text is rustc-style diagnostics rendered via `miette` and `codespan` — no filler. Rebranding (white-label names, aliases) applies to human text only; JSON is never rebranded.

---

## `--out`: payload to disk, receipt to stdout

When `--out <path>` is set, the payload writes to the file and stdout emits a minimal receipt under 30 tokens. Big artifacts never flood your context window:

```bash
$ capcli bind export mcp --out /tmp/capcli-mcp.json
```

```
[dev:tier_1]  ✓  exported

  tools:    14 pinned routines
  format:   Model Context Protocol (v2024-11-05)
  written:  /tmp/capcli-mcp.json
```

The mirror image is `@`-expansion: every string argument (`-p`, `--intent`, `--reason`, queries) accepts `@<path>` or `@-` (stdin until EOF) — the shell-escaping defense against injection and `ARG_MAX`. Multi-statement input via `@-` is rejected unless batch mode is explicit.

---

## The Tier 2 banner

On degraded-isolation hosts, boot emits:

```
[dev:tier_2]  ⚠ host.degraded_isolation
```

Not an error — physics. Tier 2 mediates through an IPC broker and the C authorizer instead of bwrap namespaces; pinned execution is denied, while draft and reviewed run fine in dev and sim. Check your tier with `capcli sys doctor`.

---

## What never appears in the output

Guest `stdout`/`stderr` are never logged — the effect engine hashes the canonical JSON outcome and nothing else. Masked columns stay masked in egress, and auth headers are always redacted. And there is no such thing as unaudited output, for the same reason there is no such thing as unaudited anything: the kernel refuses to run that way (`exit 5`).

---

**What the exit codes mean?** → [exit-codes.md](exit-codes.md)

**Every attested denial rule?** → [errors.md](errors.md)
