# Audit

Your harness just ran thirty commands while you blinked. One of them changed something.

In a normal stack you'd grep a log file and take somebody's word for it. Here you ask the ledger. Every operation — allowed *or* denied — lands in one append-only, hash-chained table. Your only job is asking it good questions.

---

## "What happened?"

```bash
$ capcli sys audit tail --since 5m
```

```
[dev:tier_1]  audit tail  ✓  6 events

  ts          event                    decision   agent      capability
  ──────────  ───────────────────────  ─────────  ─────────  ──────────────────────
  ...         run.dispatch_order       allow      agt_7f3k   cap://dispatch_order@4
  ...         db.exec                  allow      agt_7f3k   orders (read)
  ...         api.call                 allow      agt_7f3k   logistics.shipments.create
  ...         db.exec                  allow      agt_7f3k   orders (write)
  ...         sql.query                denied     agt_7f3k   orders (delete)
  ...         sql.query                denied     agt_7f3k   orders (update)
```

Six attempts. Four allowed, two denied, zero editorializing. The `DELETE FROM orders` that never executed sits in the same list as the order it couldn't touch. What happened, what was allowed, what was denied — one table, one filter away.

Narrow it with `--capability cap://dispatch_order@4`. Watch it live with `--follow`.

---

## "Who — or what — caused this?"

The tail is flat. Causality isn't. Every event carries a `caused_by` pointer to its parent, so history is a tree — leaf op → routine → session goal — and `trace` walks it for you.

```bash
$ capcli sys audit trace op_9f2e --explain
```

```
[dev:tier_1]  audit trace  ✓  op_9f2e → ses_a992f

  ses_a992f  session.start       "fulfill urgent pending orders"
    └── op_9f2c  routine.dispatch_order@4
          ├── op_9f2d  db.query (orders)    ✓  12ms
          ├── op_9f2e  api.call (logistics.shipments.create)  ✓  340ms
          │     └── tracking: 794644790133
          └── op_9f2f  db.execute (orders)  ✓  18ms
                └── rows_affected: 1

  root intent:  "fulfill urgent pending orders"
  authority:    user:alice (via agt_7f3k)
  integrity:    valid hash link (chain verified)
```

One command, full family tree. That API call happened because a human wanted urgent orders fulfilled, executed by agent `agt_7f3k`, with the chain of custody verified on the way out. If the work arrived over HTTP, the caller's W3C `traceparent` is stamped into `trace_id` — external requests graft onto the same tree.

Every `run` prints its chain — `audit: op_9f2c → op_9f2d → op_9f2e` is your receipt. Feed any of those ids to `trace`.

---

## "What was denied?" (Yes, that's recorded too.)

Most systems log the successes and lose the rejections. Capcli records both. A denial is a first-class event — the attempt, the rule, the remedy — stamped `effect: none`.

```bash
$ capcli sys audit trace op_a31f --explain
```

```
[dev:tier_1]  audit trace  ✓  op_a31f (denied leaf)

  ses_a992f  session.start            "fulfill urgent pending orders"
    └── op_a31f  sql.query (orders)   ✗  denied pre-execution

  rule:           policy.query.update_delete.require_where
  layer:          authorizer
  culprit:        DELETE FROM orders
  effect:         none
  rows_affected:  0
  state_modified: false
  remedy:         add WHERE + LIMIT, or use chunked loop via ctx.db.execute
```

`--explain` prints the exact rule and the fix — the same teaching payload you met in [boundaries.md](boundaries.md), except this copy cannot be deleted.

Why log denials at all? Accountability: "who tried to nuke the table" is a question you will someday need answered. Diagnosis: sustained denials feed the thrashing detector. Training: denial patterns are literally what your harness learns from. And the guarantee is structural — non-zero exit means `state_modified: false` — so `effect: none` isn't a promise. It's physics.

---

## "What actually changed?"

The spine is a table: `_audit`, inside `workspace.db`. Queryable, bounded, read-only. Only the kernel writes to it.

```bash
$ capcli sys audit query "SELECT capability, count(*) AS writes, sum(rows_affected) AS rows_changed
    FROM _audit
    WHERE decision = 'allow' AND rows_affected > 0 AND agent = @agent
    GROUP BY capability
    ORDER BY rows_changed DESC" \
    -p agent=agt_7f3k
```

```
[dev:tier_1]  audit query  ✓  2 rows

  capability       writes   rows_changed
  ───────────────  ───────  ─────────────
  db://orders      41       118
  db://inventory   12       96
```

"What changed" is a number, not a vibe. And the number survives interrogation, because the kernel hashes canonical outcomes — `rows_affected`, `result_hash` — not raw stdout. A chatty process can't pad its own receipt.

---

## Why you can't argue with it

**It's append-only.** Every row carries `prev_hash` — the SHA-256 of the row before it — so editing one row breaks every hash after it. The blast radius of a single tampered row is the entire rest of the ledger. There are no ghost actions: every CLI verb, binding, and environment transition advances the chain.

**Unaudited writes are refused.** If the audit sink can't record an action, the kernel won't run it — `exit 5`, state untouched. The sink gets a five-minute in-memory buffer to catch up before that panic fires.

**It's anchored offsite.** The ledger's root hash is checkpointed to S3 Object Lock — write-once storage — under KMS signatures, and a scheduled walk re-verifies the whole chain. Rewrite your git history all you like; the witness doesn't care.

Two footnotes. A fresh world's ledger opens with four events — a `rule.apply`, a read, a denied write, an allowed write. Denials are load-bearing from genesis. And everything mirrors into daily append-only `audit/*.jsonl` files, git-tracked, with mirror lag capped at five minutes.

---

## Try it

1. Run anything from [run.md](run.md) and read the `audit:` line it prints.
2. `capcli sys audit tail` — find the op id of what you just did.
3. `capcli sys audit trace <op-id> --explain` — meet the family.
4. Found something you now need to undo? [recover.md](recover.md) is the rewind button.

---

## The one rule

**If it isn't in the ledger, it didn't happen. If it is, it can't be erased.**

You don't have to remember what your agent did. The chain does. Ask it three questions — `tail`, `trace`, `query` — and read answers that can't lie.

---

**Want the deep machinery — hash chains, WORM checkpoints, distributed tracing?** → [../understand/audit.md](../understand/audit.md)

**Need the exact table structures and fields?** → [../reference/audit.md](../reference/audit.md)

**Want the denial side of the street?** → [boundaries.md](boundaries.md)
