---
name: capcli
description: Governed execution firewall — every capability runs through the capcli CLI.
triggers: [capcli, database, sql, api, routine, overview]
allowed_tools: [bash]
---

# capcli — harness directive

Interact ONLY via `capcli <noun> <verb> [target] [flags]`.

Direct sqlite3 file access, raw sockets, and unbounded SQL are blocked by the kernel. The kernel mounts zero prompt banks, catalogs, or schemas at boot — everything arrives as pointers, on demand.

Prerequisite: the `capcli` binary on PATH. If `command -v capcli` returns nothing, install it first:

```bash
curl -fsSL https://capcli.dev/install.sh | bash
```

Boot sequence:

```bash
export CAPCLI_SKILL=capcli
capcli sys doctor --json
```

Discovery over guessing: `capcli search "<query>"` returns pointers, never raw code. Read pointers through the disclosure ladder — `capcli inspect <urp>`, then `capcli doc outline <urp>`, then one leaf per turn via `capcli doc read <urp>#<node> --max-tokens 500`. Kernel-emitted `prompt://` and `doc://` pointers outrank this file; follow them.

Mutations carry causal intent: `-m "<why>"`. Preview before write: `--dry-run`.

Exit codes — 0 success; 2 governance/policy/budget denial (state untouched); 3 static/compile/shape violation; 4 runtime fault (clean rollback); 5 panic or plaintext credential leak; 6 quota/preemption yield (frame parked). Full law: see cans/physics.md#Exit-code-law.

Every target is a URP (`cap://`, `db://`, `vault://`, `prompt://`, `ws://`, …); ad-hoc paths are rejected at parse: see cans/action.md#Global-pointer-registry.
