# ADR 004 — Runtime home at <workspace>/capcli

- Status: accepted
- Date: 2026-10-13
- Decided by: user ruling (side chat, branch cans-dedup-workorders)

- Context
  - The workspace root is the user's project directory: user artifacts, their own source tree, their own git repo. Runtime state (capcli.lock, workspace.db, audit.db, envs/, routines/, apis/, storage/, revisions/) lived at that root level, polluting it.
  - CAPCLI_WORKSPACE / --workspace anchored the runtime dir directly; there was no namespace separating user artifacts from machine-managed state.
  - The monorepo .gitignore carried **/workspace.db* — a pattern that only makes sense if runtime DBs can appear at arbitrary depths, i.e. the layout had no home.

- Decision
  - The runtime home is <workspace>/capcli. All runtime state from assembly.md#Instance-runtime-home lives under it; the workspace root holds user artifacts only.
  - CAPCLI_WORKSPACE and --workspace anchor the project root; the runtime home is derived as <root>/capcli.
  - The capcli/ directory is machine-managed and gitignored wholesale; declarative blueprints live in the repository artifacts/.
  - Sockets stay outside the home: /run/capcli/kernel.sock, /run/capcli/<ws>.sock. Registry downloads stay in tmpfs /scratch.
  - Runtime-internal paths in specs and test fixtures are relative to the runtime home (envs/dev/workspace.db needs no rewrite).

- Alternatives considered
  - Keep flat (root is the runtime dir) — rejected: user-artifact and runtime-state ownership collide in one directory.
  - Split (configs at root, live state in capcli/) — rejected: two homes for one runtime breaks the one-canonical-home test; CAPCLI_*_edited config YAMLs are runtime state too.

- Consequences
  - assembly.md substrate rewritten as Instance runtime home; .gitignore rule simplified to capcli/.
  - world.md git-status and persistence lines, effect.md storage-hierarchy locations, agent.md workspace pinning + anchor, space.md namespace boundary, interface.md --workspace all rehomed to capcli/ paths.
