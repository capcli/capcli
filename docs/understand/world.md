# The World

Most "workspaces" are a folder where state goes to hide — a `.env` here, a stray SQLite file there, three scripts writing the same table with three different assumptions.

In Capcli, **a World is the governed workspace and state domain in which work happens.** One database. One door. One ledger watching the door.

---

## 1. What a World Is (and Isn't)

A World is where state lives and where effects land. It is not the explanation for everything else. You may have arrived here chasing a capability, a task, an agent, or a recovery problem — the World is where their consequences end up, not the reason they're governed.

Ask where you are:

```bash
$ capcli env current
```

```text
[dev:tier_1]  env: dev

  workspace:  envs/dev/workspace.db
  schema:     14 tables, 3 views
  trust:      draft baseline
```

One line of output, three facts: which environment you're in, which database holds the state, and what the default trust posture is here.

---

## 2. The Storage Trinity

A World keeps its state in three places, and each place earns its keep:

```
┌──────────────────────────────────────────────────────────────────┐
│  workspace.db        The SSOT. Domain tables AND the _audit       │
│  envs/dev/           ledger, in one chmod-600 SQLite file.       │
│                      WAL mode: concurrent reads, serialized      │
│                      writes. Kernel-managed. You don't open it.  │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│  world.sql           The deterministic DDL + seed dump. Committed │
│                      to git. Identical world → identical bytes,  │
│                      so schema history is readable diffs.        │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│  object snapshots    Binary VACUUM INTO backups in the object    │
│                      store. The "rewind reality" tier.           │
└──────────────────────────────────────────────────────────────────┘
```

The database is the source of truth for the state *and* for the story of the state. The SQL dump is what humans diff. The snapshots are what you restore when everything else fails.

---

## 3. Two Files Own One DDL

Every World runs on a **dual schema**:

* **`schema.yaml`** — yours. Authored in the dev worktree. Declares domain tables, read views, and triggers in YAML, not in hand-written SQL.
* **`system-schema.yaml`** — the kernel's. Written and upgraded only by kernel releases, hash-verified at boot. It defines the 13 kernel tables: `_audit`, `secrets`, `_api_quota`, `routine_stats`, `_sessions`, and friends.

Both compile into a single unified DDL inside `workspace.db`. That's why manual SQL DDL editing is prohibited — there is no second front door through which tables can appear. How loose declarations become this compiled structure is the next page's story: [structure.md](structure.md).

---

## 4. When You Start From Nothing

Maybe you just installed Capcli. No tables. No routines. Nothing established yet.

That's a legal condition, not a failure. The kernel doesn't need content to boot — it needs intent. And no, there is no formal "Void state" to invoke or manage. The world is simply empty, the way a new notebook is empty. "Void" is just the word we use while explaining it; you won't find it in any command output.

The very first events in a fresh World are always the same short class:

```bash
$ capcli sys audit tail
```

```text
[dev:tier_1]  4 events

  ts    event          decision   principal    capability
  ────  ─────────────  ─────────  ───────────  ──────────────────
  ...   rule.apply     allow      user:alice   schema v1
  ...   sql.query      allow      user:alice   orders (read)
  ...   sql.query      denied     user:alice   orders (write)
  ...   sql.query      allow      user:alice   orders (write)
```

Read it like a syllabus: a declaration (the schema compiled), curiosity (a read), a lesson (a sloppy write, denied), then a bounded write that landed. Every World starts with the kernel teaching the same four-line class.

From there, worlds grow one of three ways: a **guided mission** (you direct worker agents to author domain modules), **emergent discovery** (bounded exploration accumulates until the patterns get codified), or **predefined structure** (a human commits `schema.yaml` and execution happens inside its bounds from day one).

---

## 5. One Door

The World's perimeter is not a convention; it's file permissions and sockets:

* `workspace.db` is isolated behind the kernel daemon's IPC socket. Raw subshell access — your agent opening the file with `sqlite3` or a Python driver — is denied. Direct database sockets don't exist.
* Every mutation runs the same pipeline: intent declared → kernel gate intake → AST structural analysis → C-level authorizer interception → physical SQLite commit → audit mirror emission. No path skips a stage.
* State is partitioned per environment: `envs/<name>/workspace.db`, gitignored, with `world.sql` and the declarative files tracked in an isolated git worktree per environment. You can hold up to 5 concurrent environments — the full story is [environments.md](environments.md).

---

## The One Rule

**State has one home and one door.**

`workspace.db` is the home. The kernel is the door. Everything else — `schema.yaml`, `world.sql`, object snapshots — is a projection of that state you can read, diff, and restore.

---

**How loose exploration becomes declared structure** → [structure.md](structure.md)

**How snapshots rewind this whole thing** → [recovery.md](recovery.md)

**Why there are several worlds, not one** → [environments.md](environments.md)
