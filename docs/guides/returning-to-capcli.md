# Returning to Capcli

You used this before. Then a quarter happened. Now you're back, and the question isn't *"what is Capcli?"* — you know. It's:

> **"Where do I pick up?"**

---

## The 30-second orientation

```bash
$ capcli sys doctor --report
```

```yaml
trust_receipt:
  status:            nominal
  workspace:         envs/dev/workspace.db
  ledger_root_hash:  sha256:7f9a1b...
  audited_events:    847
  policy_denials:    2 (pre-execution; state untouched)
  unaudited_writes:  0
  secret_leaks:      0
  pinned_routines:   3
  sleep_score:       100%
```

One command tells you the world still boots, the chain still verifies, and what's pinned. If this passes, your quarter away cost you nothing. The kernel kept the receipts; that's its whole personality.

## Where you left off, in order of usefulness

| Question | Command |
|---|---|
| Which world am I in? | `capcli env current` |
| What routines exist now? | `capcli search ""` → or `capcli routine sweep --since 30d` for the health view |
| What ran while I was gone? | `capcli sys audit tail --since 720h` |
| What's scheduled? | `capcli bind list` |
| Did anything drift? | `capcli rule diff schema --git` · `capcli sys doctor` |

## Reading the tree again

You don't re-read the manual. You re-read the *index* and jump:

- Daily surface → [../use/index.md](../use/index.md)
- Exact syntax → [../reference/index.md](../reference/index.md)
- Machine contracts → [../agents/index.md](../agents/index.md)
- Something broke → [../guides/troubleshooting.md](troubleshooting.md)

## What changed while you were away (probably)

The honest answer lives in the repo's own history, but the durable trends are: more pinned surface (`pinned_routines` in the receipt), retired verbs staying retired (`db query`/`exec` → `capcli sql`, `claim` → `db lock`, `policy explain` → `sys audit trace --explain`), and the registry slowly filling toward the 300 ceiling — `routine sweep` shows the consolidation candidates.

If a command you remember now exits 3 with a deprecation-shaped denial: the `remedy:` line names the modern verb. The system onboards its own returners. Rude, but efficient.

## The one habit to re-form in the first hour

**Inspect before invoke.** Your session budget is fresh; your muscle memory isn't:

```bash
$ capcli inspect cap://dispatch_order@4
```

`can_invoke_now: true`? Go. Everything is where you left it — cryptographically guaranteed, in fact, which is more than most of us can say.

---

**Fresh start instead?** → [../start/index.md](../start/index.md)
