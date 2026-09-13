# stack.md — implementation choices (not architecture)

> Architecture says *what* and *why*. This file says *with what*.
> Swap any line here without touching architecture docs.

## Runtime

| Layer | Choice | Replaces |
|---|---|---|
| Runtime | Bun | Node.js |
| SQLite binding | rusqlite via napi-rs → `capcli_db.node` | better-sqlite3, bun:sqlite |
| Authorizer (L1) | `conn.authorizer(Some(closure))` — native C-level | AST-only enforcement |
| AST gate (L2) | `node-sql-parser` (sqlite dialect) | hand-rolled regex |
| CLI framework | `citty` (unjs) | commander, yargs |
| YAML parse | `yaml` (eemeli) | js-yaml |
| Config validation | `valibot` | zod, ajv |

## Bun Built-ins (zero deps)

| Need | Built-in |
|---|---|
| HTTP serve/webhook | `Bun.serve()` |
| Subprocess (git, bwrap) | `Bun.spawn()` |
| Audit sink (JSONL) | `Bun.file().writer()` |
| Hashing (code_hash, result_hash) | `Bun.CryptoHasher("sha256")` |
| UUID (idempotency keys) | `crypto.randomUUID()` |
| Test runner | `bun:test` |
| Env vars | `Bun.env` |

## Native Crate: `capcli_db`

```toml
[dependencies]
napi = { version = "2", features = ["napi8"] }
napi-derive = "2"
rusqlite = { version = "0.31", features = ["bundled"] }
```

- `features = ["bundled"]` compiles SQLite from C source — no system libsqlite3 needed
- Exposes: `open`, `set_authorizer`, `query`, `execute`, `snapshot`, `restore`
- Policy.yaml compiles into the Rust authorizer closure's match arms at boot
- Bun loads via `import { CapDb } from "./capcli_db.node"`

## Two-Layer Enforcement Map

```
Agent → capcli CLI (citty)
  → TypeScript kernel
    → Layer 2: node-sql-parser AST gate (WHERE? LIMIT? allowed tables?)
      → Layer 1: rusqlite authorizer (action × table × column, ATTACH deny, PRAGMA deny)
        → SQLite engine (prepare → step → finalize)
```

Layer 2 is the ceiling (policy-aware, structural).
Layer 1 is the floor (bypass-proof, C-level, cannot be skipped from TS).

## Build

```bash
# Native crate
cd native && napi build --release    # → capcli_db.node

# Kernel
bun build src/cli.ts --outdir dist   # → dist/cli.js

# Test
bun test
```

## Dependency Count

```
npm:    4  (node-sql-parser, yaml, valibot, citty)
rust:   3  (napi, napi-derive, rusqlite)
total:  7  real dependencies
```
