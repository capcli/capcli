# Discovery

You don't memorize. You don't grep. You search.

Every capability resolves through the unified registry. That's the registry law: no codebase grepping, no reading raw OpenAPI files, no `PRAGMA` spelunking. The kernel alone parses specs; you get typed pointers with action hints.

---

## The move

```bash
$ capcli run search "order" --json
```

```
{
  "exit": 0,
  "json": {
    "results": [
      { "ptr": "cap://dispatch_order@4", "kind": "routine", "trust": "pinned", "description": "Dispatch paid order to carrier" },
      { "ptr": "cap://order_refund@2", "kind": "routine", "trust": "reviewed", "description": "Refund and archive cancelled order" },
      { "ptr": "db://orders", "kind": "table", "trust": null, "description": "Core order state" }
    ],
    "count": 3
  },
  "text": "[dev:tier_1]  3 results"
}
```

Decode: every hit is a Universal Resource Pointer (URP) — typed, addressable, inspectable. Descriptions are capped at 60 tokens; search returns pointers and summaries, never raw blobs. Results cap: 20.

---

## Filters

Narrow before you rank:

| Flag | Cuts by |
|---|---|
| `--type <domain>` | Kind: routine, api-verb, table, doc |
| `--trust <rung>` | draft, reviewed, pinned |
| `--env <name>` | Environment scope |

```bash
$ capcli run search "refund" --trust reviewed --json
```

```
{
  "exit": 0,
  "json": {
    "results": [
      { "ptr": "cap://order_refund@7", "kind": "routine", "trust": "reviewed", "description": "Refund cancelled order and archive" }
    ],
    "count": 1
  },
  "text": "[dev:tier_1]  1 result"
}
```

---

## How search resolves

The cascade, in order: exact → prefix → fuzzy → semantic → did-you-mean.

The split is deterministic. The kernel handles exact, prefix, and FTS5 structured filters over `_search_index`. Semantic ranking is harness-side — your embeddings, your typo tolerance. The kernel does zero inference, and matches below 0.60 relevance are rejected outright, so garbage never reaches you.

Zero hits never return silence: did-you-mean proposes the nearest candidates. Parse that list before concluding a capability doesn't exist.

Search is optional machinery. Direct invocation is permitted whenever you already know the signature — discovery answers "what's here?", it is not a toll booth.

---

## Find the holes

The registry also reports what *doesn't* exist:

```bash
$ capcli run search gaps --since 7d
```

```
[dev:tier_1]  2 gaps detected

  query: "inventory sync"     searches: 8    invocations: 0    signal: missing capability
  query: "customer export"    searches: 5    invocations: 0    signal: missing capability
```

Eight searches, zero invocations: something wants to exist. Zero-result queries rank first; a low invoke rate on real hits flags descriptions that fail to convert. This is your build queue, surfaced by the kernel — see [codification.md](codification.md).

---

## Remote surface: api catalog

Third-party verbs live in provider catalogs. Inspect the remote surface before you plan around it:

```bash
$ capcli api catalog stripe --state active --json
```

```
{
  "exit": 0,
  "json": {
    "provider": "stripe",
    "state": "active",
    "verbs": [
      { "ptr": "cap://stripe.refund_charge", "trust": "reviewed", "description": "Issue partial or full Stripe refund" }
    ]
  },
  "text": "[dev:tier_1]  stripe  1 active verb"
}
```

Verb states: `dormant` → `active` → `deprecated` → `retired`. Freshly synced specs land entirely dormant — discoverable, inspectable, uncallable. Activation (`api activate <provider.verb> --intent "..."`) is a governed mutation with an anti-junk intent check, not a config flip. H3 of your onboarding journey is exactly this: probe local state via `sql`, probe remote verbs via `api catalog`.

Spec quarantine is absolute: the kernel parses OpenAPI and compiles `apis/<provider>.yaml`; the harness never reads the raw spec. If you're loading a swagger file into context, you have already failed the contract.

---

## The ceiling

The registry holds a hard ceiling of 300 routines; keyword search degrades past it. Hitting the cap means it's time to consolidate, not enumerate. Filter harder, rank semantically, or retire the dead weight.

---

**Got a pointer? Get the verdict** → [inspection.md](inspection.md)

**Curious what humans see here?** → [../use/discover.md](../use/discover.md)
