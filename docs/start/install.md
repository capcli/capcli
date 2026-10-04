# Install

You're not going to type this yourself. Let's be honest. You're going to say "hey, install capcli" to your harness and go make coffee. Fine. That's what it's for.

But you should know what's happening so you can verify it didn't lie to you.

---

## The whole thing

```bash
curl -fsSL https://capcli.dev/install.sh | bash
```

One line. Single static Rust binary. No npm. No node_modules. No Python dependency hell. No `cargo build` unless you're compiling from source.

Your harness runs this. It drops `capcli` into `/usr/local/bin/`. Done.

---

## Verify it actually worked

Tell your harness:

> "run capcli sys doctor"

Or type it yourself. Your call.

```bash
$ capcli sys doctor
```

```
[dev:tier_1]  capcli 0.4.2

  host:       linux x86_64
  tier:       1 (hardened)
  sandbox:    bwrap 0.8.1
  engine:     bun 1.2.4
  python:     3.12.1
  git:        2.44.0
  lockfile:   capcli.lock ✓
  schema:     schema.yaml ✓
  policy:     policy.yaml ✓
  governance: governance.yaml ✓

  status:     ready
```

If you see `ready`, you're installed. If you see `exit 3`, something's missing and the doctor tells you what.

---

## What just landed on your machine

| Thing | What it is | Why you care |
|---|---|---|
| `/usr/local/bin/capcli` | Single static binary | The whole kernel. No daemons to manage yet. |
| `capcli.lock` | Compiled config hash | Boot refuses if this doesn't match. Tamper evidence. |
| `schema.yaml` | Your domain schema | You'll edit this. Your harness will edit this more. |
| `policy.yaml` | Behavioral rules | What's allowed. Default: deny. You'll barely touch it. |
| `governance.yaml` | Structural limits | LOC caps, op ceilings, registry bounds. Set once, forget. |
| `workspace.db` | SQLite database | The actual state. chmod 600. Your harness can't touch it directly. |

You don't need to understand any of these yet. They exist. They'll matter later.

---

## Tier check

Your harness is running somewhere. That somewhere has a tier.

| Tier | Where | What it means |
|---|---|---|
| **1** | Linux, VPS, Docker, WSL2 | Full sandbox. bwrap namespaces. seccomp-bpf. All trust rungs. |
| **2** | macOS, Termux, Windows | Degraded isolation. IPC broker instead of bwrap. Pinned routines denied. |

The doctor tells you which one you're on. If you're on Tier 2, you'll see:

```
[dev:tier_2]  ⚠ host.degraded_isolation
```

That's not an error. It's physics. macOS doesn't do unprivileged namespaces. Capcli adapts. You just can't run pinned routines here. Dev and sim work fine.

---

## If something's wrong

```bash
$ capcli sys doctor --json
```

Machine-readable. Your harness can parse this and fix whatever's broken. That's its job. You made coffee. Let it earn its keep.

Common failures:

| Symptom | Cause | Fix |
|---|---|---|
| `exit 3` on boot | Missing python3 or git | Install them. Doctor names which one. |
| `exit 3` on boot | bwrap missing on Tier 1 | `apt install bubblewrap` |
| `exit 3` on boot | Lockfile mismatch | You edited a YAML by hand. `git checkout` it. |
| Tier 2 warning | macOS / Windows | Expected. Not a bug. |

---

## That's it

You're installed. The binary is on disk. The doctor says ready.

Your harness is now sitting in front of a governed execution kernel. It can discover things, run things, and get denied things. All without you reading a single architecture doc.

**Next:** actually do something → [first-task.md](first-task.md)
