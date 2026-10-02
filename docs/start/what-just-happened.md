# What Just Happened

You told your harness to do a thing. It did the thing. You watched.

But five distinct pieces of machinery fired under the hood. You don't need to master them yet. You just need names for what you saw.

---

## The chain, mapped

| You saw… | That was… | It lives in… |
|---|---|---|
| `capcli search "order"` | **Discovery** — the search surface | [workflows/discover.md](../workflows/discover.md) |
| `capcli sql "SELECT …"` | **Gated read** — AST + authorizer said "fine, go ahead" | [concepts/authorizer.md](../concepts/authorizer.md) |
| `exit 2` on sloppy UPDATE | **A denial** — physics said "absolutely not" | [reference/exit-codes.md](../reference/exit-codes.md) |
| `capcli sql "UPDATE … WHERE id=…"` | **Bounded write** — intent declared, limits respected | [workflows/query-data.md](../workflows/query-data.md) |
| `capcli sys audit tail` | **The memory spine** — append-only hash-chained log | [concepts/memory-spine.md](../concepts/memory-spine.md) |

That's the whole mental model. Five pieces. Everything else is depth on one of these five.

---

## Discovery: "what exists?"

```bash
$ capcli search "order"
```

Your harness didn't grep your codebase. It didn't read a schema file. It asked the **registry** — a typed pointer system that covers everything: routines, tables, API verbs, docs, snapshots, bindings.

Every result came back as a **URP** (Universal Resource Pointer):

```
db://orders                 → a table
cap://dispatch_order@4      → a routine at version 4
```

You don't memorize. You search. Your harness doesn't memorize either. It searches.

→ Deeper: [workflows/discover.md](../workflows/discover.md)

---

## Gated read: "show me data"

```bash
$ capcli sql "SELECT … LIMIT 5"
```

Two layers checked that query before SQLite ever saw it:

1. **AST check** — parsed the SQL, confirmed it's a SELECT, confirmed it has a LIMIT
2. **C authorizer** — `sqlite3_set_authorizer` callback said "read on `orders`? allowed"

Both passed. SQLite executed. Rows came back.

Your harness didn't write a try/catch. Didn't check permissions. Didn't remember to add LIMIT. The kernel enforced all of it because it *can't not*.

→ Deeper: [concepts/authorizer.md](../concepts/authorizer.md)

---

## The denial: "absolutely not"

```bash
$ capcli sql "UPDATE orders SET status='processing' WHERE status='pending'"
```

```
exit 2
FAIL  policy.query.update_delete.require_bounded
state_modified: false
```

Three things happened:

1. **AST caught the blast radius.** No primary key. No LIMIT. Could hit hundreds of rows.
2. **The denial was structural.** Not a warning. Not a suggestion. [`exit 2`](../reference/exit-codes.md#exit-2) means the SQL never reached SQLite. Zero rows touched.
3. **The denial taught.** `remedy: target specific primary key or add LIMIT`. Your harness read that, fixed the query, retried.

Denials aren't errors. They're the system saying "here's the wall, here's the door."

→ Deeper: [reference/exit-codes.md](../reference/exit-codes.md)

---

## Bounded write: "do the thing, precisely"

```bash
$ capcli sql "UPDATE orders SET status='processing' WHERE id='ord_9885' LIMIT 1" \
    -m "mark oldest pending order as processing"
```

Four gates passed:

| Gate | What it checked |
|---|---|
| Intent | `-m` flag present. Writes without intent get [`exit 3`](../reference/exit-codes.md#exit-3). |
| AST | WHERE clause targets a specific ID. LIMIT 1. Blast radius: one row. |
| Authorizer | Write on `orders` table? Allowed for this trust level. |
| Budget | Ops consumed: 1 of 50. Plenty of headroom. |

SQLite executed. One row changed. Audit event emitted.

Your harness didn't think about any of this. It just ran the command. The kernel did the thinking about *whether it should run*.

→ Deeper: [workflows/query-data.md](../workflows/query-data.md)

---

## The memory spine: "prove it"

```bash
$ capcli sys audit tail --since 2m
```

Three rows. The read. The denied write. The successful write.

Each row is **hash-chained**. Row N contains the SHA-256 of row N-1. Tamper with one row, every subsequent hash breaks. The kernel verifies this chain at boot. Broken chain = `exit 3` = kernel refuses to start.

You didn't configure logging. You didn't write middleware. You didn't remember to audit. The spine is *structural*. Unaudited writes are physically impossible ([`exit 5`](../reference/exit-codes.md#exit-5)).

→ Deeper: [concepts/memory-spine.md](../concepts/memory-spine.md)

---

## What you didn't have to think about

Here's the list of things your harness *didn't* do, because Capcli did them structurally:

- ❌ Check if the query was a read or write
- ❌ Validate the WHERE clause
- ❌ Enforce LIMIT
- ❌ Declare intent for the write
- ❌ Check budget remaining
- ❌ Write an audit log entry
- ❌ Hash-chain the audit entry
- ❌ Handle the denial and retry
- ❌ Verify the trust level

Your harness reasoned. Capcli governed. That's the split. That's always the split.

---

## The one mental model to keep

```
YOUR HARNESS          CAPCLI KERNEL           REALITY
(thinks)              (enforces)              (changes)

"I want to update     AST: bounded? ✓         orders.ord_9885
 ord_9885"            Authorizer: allowed? ✓   status = 'processing'
                      Budget: ops 1/50? ✓
                      Intent: declared? ✓
                      Audit: hash-chained? ✓

                      → execute
```

Harness proposes. Kernel disposes. Reality records.

---

## Where to go from here

You've done something. You've seen the pieces. Now pick your next direction:

| You want to… | Go to |
|---|---|
| Do more everyday work | [workflows/index.md](../workflows/index.md) |
| Understand the deeper model | [concepts/index.md](../concepts/index.md) |
| Automate something you keep doing | [workflows/routines.md](../workflows/routines.md) |
| Look up exact syntax | [reference/index.md](../reference/index.md) |
