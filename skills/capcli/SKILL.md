---
name: capcli
description: Governed execution firewall — every capability runs through the capcli CLI.
triggers: [capcli, database, sql, api, routine, overview]
allowed_tools: [bash]
---

# capcli — harness directive

Interact ONLY via `capcli <noun> <verb> [target] [flags]`.

Direct sqlite3 file access, raw sockets, and unbounded SQL are blocked by the kernel. The kernel mounts zero prompt banks, catalogs, or schemas at boot — everything arrives as pointers, on demand.

Boot sequence:

```bash
export CAPCLI_SKILL=capcli
capcli sys doctor --json
```

Discovery over guessing: `capcli search "<query>"` returns pointers, never raw code. Read pointers through the disclosure ladder — `capcli inspect <urp>`, then `capcli doc outline <urp>`, then one leaf per turn via `capcli doc read <urp>#<node> --max-tokens 500`. Kernel-emitted `prompt://` and `doc://` pointers outrank this file; follow them.

Mutations carry causal intent: `-m "<why>"`. Preview before write: `--dry-run`.
