# Recover

Your harness will eventually break something. That's not pessimism — it's arithmetic.

Most systems treat recovery as a fire extinguisher bolted behind glass: documented never, needed at 3 AM. Capcli treats it as a Tuesday verb. You snapshot before risk, you rewind when wrong, and both the mistake *and* the fix land in the audit ledger. Understand first ([audit.md](audit.md)), then undo. No panic required.

---

## Snapshot before you do something brave

You're about to let the harness reprice inventory. Bold. Take the picture first.

```bash
$ capcli db snapshot -m "before repricing experiment"
```

```
[dev:tier_1]  snapshot  ✓  snap_b31d2e

  size:    14.2 MB
  tables:  14
  method:  VACUUM INTO (transactionally clean, during traffic)
  audit:   op_44c1
```

That's a `VACUUM INTO` — an atomic, transactionally clean copy taken *while writes are running*. No table locks. No "stop the database while I back it up." You met this button in [work-with-your-data.md](work-with-your-data.md); it works exactly as advertised.

Often you won't even take the snapshot yourself. The kernel does: before every schema migration (`snap_migration_*`), on schedule (`snap_auto_*`), at onboarding (`snap_onboarding_*`). Show up brave — the net is already strung.

---

## The harness broke it. Fine.

The repricing ran. Prices are now half of what they should be — the classic. You don't open a ticket. You rewind.

```bash
$ capcli db restore snap_b31d2e -m "revert botched repricing"
```

```
[dev:tier_1]  restore  ✓  state rewound

  snapshot:  snap_b31d2e
  tables:    14 restored
  audit:     op_44c9
```

One command, atomic. And note the `audit:` line — the restore itself is an event. You didn't hide the mistake, you *recorded the recovery*. Anyone asking "why did prices flicker?" gets the full story from the ledger: what ran, what it broke, what you did about it.

---

## The code was the problem

Sometimes the data is fine and the routine is wrong. `dispatch_order@4` just shipped with an edge-case bug — it mangles international postal codes. You don't hotfix at midnight. You point back at the version that worked.

```bash
$ capcli routine rollback dispatch_order --to-version 3 \
    -m "v4 fails on international postal codes"
```

```
[prod:tier_1]  routine rollback  ✓  cap://dispatch_order → version 3

  active:      version 3 (hash: sha256:88a1b...)
  superseded:  version 4 (deactivated)
  audit:       op_77c2
```

This rewinds a pointer. It deletes nothing. Version 4 stays in the provenance graph — hash-pinned, immutable, still replayable — because history is evidence, not clutter. In-place edits are banned anyway: code changes force version bumps, which is exactly why rollback exists as a first-class verb.

You can reach back five versions; twenty-five are kept for provenance. Deep enough for any bug you'd actually admit to.

---

## Get it off the machine

A snapshot on the same disk as the database is a hope, not a backup. Push:

```bash
$ capcli sys backup --push
```

```
[prod:tier_1]  backup  ✓  pushed

  git:        committed — world.sql, audit/*.jsonl, schema.yaml
  snapshots:  snap_migration_042 → object store (WORM)
  ledger:     root hash checkpointed (sha256:5c9e2a...)
  witness:    stamped to audit/witness.log
  audit:      op_6d10
```

Two destinations, on purpose. Git takes the readable artifacts — schema, routines, daily audit mirrors — and auto-commits every 15 minutes anyway; `--push` also ships the binary `VACUUM INTO` snapshots to append-only object storage.

The line that matters is `witness`. The ledger's root hash is checkpointed offsite under KMS signatures. Someone can force-push your git history into oblivion; the offsite witness is write-once. The math survives the sysadmin. Git stays small anyway — history squashes on a 90-day rhythm, with the full immutable archive retained in object storage.

---

## Pick a recovery point

Everything you might return to, in one list:

```bash
$ capcli sys recover --list
```

```
[prod:tier_1]  recover --list  ✓  4 recovery points

  point                kind      note
  ───────────────────  ─────────  ─────────────────────────
  snap_migration_042   snapshot   auto: before schema v14
  snap_b31d2e          snapshot   manual: before repricing
  snap_auto_0630       snapshot   scheduled
  6f2a91c              commit     kernel commit (pre-v14)
```

Three tiers of "go back": a local snapshot (instant `db restore`), a git revision (full workspace reconstruction), or the offsite archive (the disaster tier, pulled from object storage when the machine itself is gone). Rebuild the whole workspace from a commit:

```bash
$ capcli sys recover 6f2a91c
```

```
[prod:tier_1]  recover  ✓  workspace reconstructed

  point:    git 6f2a91c
  state:    schema v13 · policy v4
  chain:    verified against offsite WORM checkpoint
  next:     capcli run overview
```

That `chain:` line is the part worth loving. On the way back in, the local hash chain is verified against the offsite checkpoint. If your history doesn't match the witness, the kernel refuses to boot (`exit 3`). A restored world that lies about itself doesn't get to run.

Back inside, don't trust memory — run `capcli run overview` and get the ground-zero briefing: environment, schema, last successful action, next step. Nobody re-bills customers from a stale imagination.

---

## When you're truly locked out

Corrupted policy, failed promotion, boot refusal — if the kernel won't cooperate, there's a break-glass: `CAPCLI_RECOVERY=1`. It boots with policy disabled and exactly four verbs available (read-only `sql`, `db dump`, `sys audit tail`, `sys backup`). The moment it activates, a `recovery_mode_entered` event is stamped into the ledger. You can break the glass. You cannot break it quietly.

---

## The one rule

**Undo is a daily verb, not an emergency.**

Snapshots are cheap. Restores are atomic and audited. Rollbacks preserve history instead of scrubbing it. That's the whole reason you can let an agent work while you sleep: every change has a receipt, and every receipt has a rewind path.

---

**Need a step-by-step drill for a specific disaster?** → [../guides/recovery.md](../guides/recovery.md)

**Want the machinery — VACUUM INTO, WORM checkpoints, break-glass?** → [../understand/recovery.md](../understand/recovery.md)

**Making recovery part of everyday operations?** → [../automate/operation.md](../automate/operation.md)
