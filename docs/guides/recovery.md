# Recovery: The Morning-After Guide

Disaster recovery in most shops is a fire extinguisher behind glass that nobody has pulled since the last audit. In Capcli, recovery is a Tuesday — boring on purpose, and boring *because you rehearsed it*. Every procedure below is two commands or fewer. If you can't recover in two commands, you shouldn't be running autonomous agents at all.

---

## 1. Snapshot before the risky thing

You're about to let an agent touch pricing. Take the point-in-time copy first:

```bash
$ capcli db snapshot -m "pre-pricing safety net"
```

```
[prod:tier_1]  ✓  snapshot created

  snapshot_id:  snap_prod_pre_pricing_31ac
  size:         24.8 MB
  tables:       18
  duration:     18ms
  audit:        op_88b1
```

That's a `VACUUM INTO` — an atomic, transactionally clean copy taken mid-traffic. Readers keep reading. Writers keep writing. You get a byte-identical database to rewind to.

You also get snapshots for free at the dangerous moments: before every schema migration (`snap_migration_*`), before world merges, and on the 15-minute background cadence. Git commits ride along on every apply, promote, and merge; if the repo drifts more than 30 minutes behind, `sys doctor` raises an alarm.

---

## 2. Rewind: `db restore`

The agent halved every price instead of raising them 10%. Panic? No. Rewind:

```bash
$ capcli db restore snap_prod_pre_pricing_31ac -m "revert botched pricing update"
```

```
[prod:tier_1]  ✓  state restored

  active_db:  envs/prod/workspace.db (restored to snap_prod_pre_pricing_31ac)
  audit:      op_88b2
```

Two things happened: the database rewound atomically, and the *restore itself* was written to the ledger. You don't hide the mistake. You record the recovery. That's the whole culture in one command.

---

## 3. Offsite: `sys backup --push`

Local snapshots die with the disk. Push the boring trio — Git, object store, witness:

```bash
$ capcli sys backup --push
```

```
[prod:tier_1]  ✓  backup pushed

  snapshot:  snap_prod_2f61 (VACUUM INTO)
  git:       world.sql + audit mirrors committed
  worm:      object-store checkpoint written (S3 Object Lock)
  witness:   audit/witness.log stamped
  audit:     op_44c9
```

Git keeps the readable history — schema, `world.sql`, routines, audit mirrors — squashed every 90 days so the repo stays small. The object store keeps the heavy binaries under WORM: write-once, and not even you can overwrite them. The witness log anchors the ledger root offsite, where a git force-push can't reach.

---

## 4. The full rewind: `sys recover`

Bad day. Not "one bad update" — the whole workspace needs to go back. List your recovery points first:

```bash
$ capcli sys recover --list
```

```
[prod:tier_1]  3 recovery points

  snap_prod_pre_pricing_31ac   snapshot    18m ago   local + offsite
  snap_migration_043           snapshot    2h ago    local + offsite
  a91f37c                      git commit  1d ago    world.sql @ v15
```

Then pick one:

```bash
$ capcli sys recover snap_prod_pre_pricing_31ac
```

```
[prod:tier_1]  ✓  recovered

  source:    snap_prod_pre_pricing_31ac (verified against WORM checkpoint)
  database:  restored
  audit:     op_45d0
```

Three tiers, one verb: a local snapshot rewinds state instantly, `sys recover <commit>` rebuilds the workspace from a git revision, and the offsite archive is the disaster pull when the machine itself is gone.

---

## 5. Code went bad: `routine rollback`

State problems get snapshots. Code problems get pointer rewinds:

```bash
$ capcli routine rollback dispatch_order --to-version 4 \
    -m "v5 fails on international postal codes"
```

```
[prod:tier_1]  ✓  rolled back

  pointer:     cap://dispatch_order
  active:      version 4 (hash: sha256:88a1b...)
  superseded:  version 5 (deactivated)
  audit:       op_77c2
```

One command restores the pointer. Max rollback depth is 5 versions; 25 historical versions are kept on disk, and their hashes stay pinned in the causal DAG forever, so historical replays never rot.

---

## 6. Rehearse it, or it isn't real

The only way recovery stays boring is if you've done it before. Once a month, on dev: snapshot (`capcli db snapshot -m "drill"`), break something small on purpose, restore (`capcli db restore <id> -m "drill"`), then read `capcli sys audit tail` — the snapshot, the mutation, and the restore should be sitting there in order. It's literally onboarding for new agents — snapshot, mutate, restore, verify — and humans should rehearse it too. Rehearsal is why the real thing feels like nothing.

---

## 7. Break glass (rarely)

Locked out by a corrupted policy file or a failed promotion? The emergency shell exists:

```bash
$ CAPCLI_RECOVERY=1 capcli recover snap_prod_pre_pricing_31ac
```

```
[RECOVERY MODE]  ⚠  Emergency break-glass active.
  Policy enforcement: DISABLED
  Audit sink:         ACTIVE (audit/witness.log stamped)
  State:              Restoring snap_prod_pre_pricing_31ac...
  Result:             ✓ Success. Booting normal kernel.
```

Policy is off, but only four verbs exist in recovery mode — read-only `sql`, `db dump`, `sys audit tail`, and `sys backup`. And the instant it loads, a `recovery_mode_entered` event lands in the audit sink. You can break the glass. You cannot break it quietly.

---

## The one rule

**Snapshots are cheap. Regret is expensive.** Take one before anything with teeth — migrations, merges, big batch writes. Eighteen milliseconds is the cheapest insurance you will ever buy.

---

**The machinery behind snapshots and WORM?** → [understand/recovery.md](../understand/recovery.md)

**Migration went sideways?** → [migration.md](migration.md)

**Exact command contracts?** → [reference/commands/sys.md](../reference/commands/sys.md)
