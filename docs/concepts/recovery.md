
# Recovery, Snapshots, & Break-Glass

In traditional software, disaster recovery is an emergency fire extinguisher behind glass that nobody has tested in three years.

When a bad script corrupts a database at 03:00 AM, a frantic DevOps engineer SSHs into the production box, searches for a 14-hour-old backup file, realizes the backup script failed last Tuesday, and starts writing an apology email to customers.

In Capcli, **recovery is not an emergency fire drill. Recovery is normal everyday operation.**

Your AI agent will make mistakes. That is a statistical certainty. 

If recovering from a botched batch update takes more than five seconds, your architecture is broken. Here is how Capcli makes catastrophic state loss structurally impossible.

---

## 1. Hot Point-in-Time Snapshots: `VACUUM INTO`

When your database is taking active read and write traffic, you cannot simply run `cp workspace.db backup.db`. You will get a corrupted file with torn pages.

Capcli uses native SQLite **`VACUUM INTO`** via `capcli db snapshot` ([full syntax](../reference/cli/db.md)):

```bash
$ capcli db snapshot -m "pre-migration safety snapshot"
```

```text
[prod:tier_1]  ✓  snapshot created

  snapshot_id: snap_migration_042
  size:        24.8 MB
  tables:      18
  duration:    18ms
  audit:       op_88b1
```

### Why this matters:
* **Zero Locking:** It creates an atomic, transactionally clean, byte-identical copy of `workspace.db` without locking readers or interrupting active writers.
* **Automatic Triggers:** Capcli automatically creates a snapshot before every schema migration (`snap_migration_*`), before world merges, and on the automated background maintenance cadence ([figures](../reference/limits.md#workspace-storage)).

### The 2-Second Rollback:
If an agent messes up an update:
```bash
$ capcli db restore snap_migration_042 -m "revert botched price update"
```

```text
[prod:tier_1]  ✓  state restored

  active_db:  envs/prod/workspace.db (restored to snap_migration_042)
  audit:      op_88b2
```

State rewinds instantly. The restore action itself is logged into the audit ledger. You don't hide the mistake; you record the recovery.

---

## 2. The Dual-Storage Guarantee: Git + Object Storage

Most architectures try to use Git for everything or Object Storage for everything. Both fail:
* **Git alone fails:** Binary SQLite databases bloat Git repositories in days. Committing a 50MB `.db` file every 15 minutes will make `git clone` crash within a month.
* **Object Storage alone fails:** S3 buckets don't give you readable line-by-line diffs, branch merges, or PR code reviews for schema changes.

Capcli enforces a **Dual-Storage Guarantee**:

```
┌────────────────────────────────────────────────────────────────────────┐
│  HOT RUNTIME (Local Disk)                                              │
│  workspace.db (chmod 600) + daily audit JSONL mirrors                  │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
      Auto-commits  │                                │ Binary snapshots
      every 15 min  ▼                                ▼ every 15 min
┌───────────────────────────────┐  ┌─────────────────────────────────────┐
│  GIT WORKTREE REPOSITORY      │  │  OBJECT STORE (S3 / R2 WORM)        │
│  • schema.yaml (DDL changes)  │  │  • Binary VACUUM snapshots          │
│  • world.sql (DDL exports)    │  │  • S3 Object Lock (Immutable WORM)  │
│  • routines/ (.ts, .py code)  │  │  • checkpoint.sig (KMS Notary)      │
│  • audit/ (Daily JSONL logs)  │  │  • Retained permanently             │
│  • Squashed every 90 days     │  │                                     │
└───────────────────────────────┘  └─────────────────────────────────────┘
```

* **The Git Repo** stays small and human-readable. It tracks code, declarative schemas, and JSONL text logs. To handle automated commits (~35,000 commits/year), Git history is cleanly squashed on the retention cadence ([figures](../reference/limits.md#workspace-storage)).
* **The Object Store** (S3/Cloudflare R2) holds the heavy binary payloads: the raw `VACUUM INTO` snapshots and append-only audit archives.

---

## 3. Cryptographic Anchoring: S3 WORM & KMS Notarization

Git commits can be rewritten with `git push --force`. A rogue developer or compromised CI pipeline could rewrite Git history to erase a security incident.

Capcli prevents this with **Offsite WORM Checkpointing**:
1. At scheduled intervals, the kernel computes the root SHA-256 hash of the entire `_audit` ledger.
2. It pushes this root hash to an **S3 Object Lock (Write-Once-Read-Many)** bucket.
3. An external cloud KMS key signs the checkpoint and stamps it into `audit/witness.log`.

**Result:** Even if someone force-pushes your Git repository and deletes your local SQLite file, the offsite KMS witness signature remains immutable in cloud object storage. 

When you restore, the kernel verifies the local hash chain against the offsite WORM checkpoint. If they don't match, **the kernel refuses to boot ([exit 3](../reference/exit-codes.md#exit-3))**.

---

## 4. Break-Glass Emergency Mode: `CAPCLI_RECOVERY=1`

What happens if an invalid configuration, corrupted policy file, or failed promotion completely locks you out of the system?

If the behavioral policy engine is refusing all commands, how do you fix it?

You use the **Emergency Recovery Mode**:

```bash
$ CAPCLI_RECOVERY=1 capcli sys recover snap_migration_042
```

```text
[RECOVERY MODE]  ⚠  Emergency break-glass active.
  Policy enforcement: DISABLED
  Audit sink:         ACTIVE (audit/witness.log stamped)
  State:              Restoring snap_migration_042...
  Result:             ✓ Success. Booting normal kernel.
```

### The Break-Glass Invariants:
1. **Policy is Disabled:** The C authorizer and AST limits are bypassed so you can fix corrupted files.
2. **Restricted Verb Allowlist:** You cannot run arbitrary business routines. Only four verbs exist in recovery mode:
   * `capcli sql` (strictly read-only `SELECT`)
   * `capcli db dump`
   * `capcli sys audit tail`
   * `capcli sys backup` / `capcli sys recover`
3. **The Alarm Bell:** The instant `CAPCLI_RECOVERY=1` is loaded, the kernel stamps a **`recovery_mode_entered`** event directly into the immutable audit sink. You can break the glass, but you cannot hide that you broke it.

---

## 5. Re-Entry Context: The "Where Was I?" Routine

When an agent crashes mid-turn or a human supervisor restores a database from a snapshot, the biggest danger is **amnesia**. 

The agent wakes up, forgets what it already did, and tries to re-bill customers or re-apply schema migrations.

Capcli solves this with the **Ground Zero Briefing**:

```bash
$ capcli run overview
```

```text
[prod:tier_1]  overview@1  ✓  24ms

  environment: prod (Tier 1 Hardened)
  schema:      v14 (nominal, 0 drift)
  policy:      v5 (locked, hash: sha256:77a1...)
  last_action: 3m ago (db.execute: orders.ORD-9912 status='shipped')
  active_lock: none
  drift_alert: 0 uncommitted changes
  next_step:   ready for incoming triggers
```

Every session begins with this dense situational briefing (capped at the routine result ceiling — [figures](../reference/limits.md#execution-budget); command reference: [reference/cli/run.md](../reference/cli/run.md)):
* What environment am I in?
* What was the exact last intent successfully committed to the causal DAG?
* Are there any active lease locks in `claims`?
* Did someone restore a snapshot while I was asleep?

The agent grounds its reasoning in deterministic reality before proposing its next move.

---

**See how environments separate blast radius:** → [environments.md](environments.md)  
**Inspect available recovery snapshots:** → `capcli sys recover --list` ([reference/cli/sys.md](../reference/cli/sys.md))
