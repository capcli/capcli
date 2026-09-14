# project-structure.architecture.md *(final v1 — the monorepo is the territory)*

> **The physical layout of capcli: one Bun monorepo, domain-sealed packages, feature-scoped files, `*.*.*` naming law, centralized types, three test tiers, zero build-tool bureaucracy. stack.md is dead — its content lives here, once, forever.**

---

## 1. Scope & Convictions

Five laws of structure:

1. **Bun IS the monorepo.** No turborepo, no nx, no pnpm workpaces, no lerna. `bunfig.toml` + workspace globs. Bun resolves, links, runs, tests. One tool.
2. **Domain seals the package. Feature seals the file.** A package owns one domain. A file owns one feature. No file crosses domains. No package leaks internals.
3. **`*.*.*` is the naming law.** Every source file carries exactly three dot-separated segments: `domain.feature.ext`. No exceptions. No `index.ts`. No `utils.ts`. No `helpers.ts`.
4. **Types live in one place.** `@capcli/types` is the single source of shared contracts. Domains import from it. Domains never export types to each other.
5. **Tests mirror source.** Every `domain.feature.ts` has `domain.feature.unit.test.ts`, `domain.feature.integration.test.ts`, or `domain.feature.e2e.test.ts` in the corresponding test tier. No test file exists without a source file.

---

## 2. Monorepo Root

```
capcli/
├── bunfig.toml                    # workspace config, single source
├── bun.lockb                      # lockfile
├── package.json                   # workspace root — scripts only
├── .gitignore
│
├── architecture.md                # master architecture (this repo's law)
├── project-structure.architecture.md  # THIS FILE — physical layout law
├── command.architecture.md
├── capcli-routine.architecture.md
├── capcli-routine-lifecycle.architecture.md
├── db.architecture.md
├── onboarding.architecture.md
├── pwa.architecture.md
├── sdk.architecture.md
├── governance.yaml
├── policy.yaml
│
├── packages/                      # all code lives here
│   ├── types/                     # @capcli/types
│   ├── kernel/                    # @capcli/kernel
│   ├── sdk/                       # @capcli/sdk
│   ├── pwa/                       # @capcli/pwa
│   └── native/                    # @capcli/native (Rust)
│
└── workspace/                     # runtime artifact — gitignored
    ├── schema.yaml
    ├── system-schema.yaml
    ├── policy.yaml
    ├── governance.yaml
    ├── apis/
    ├── routines/
    ├── workspace.db
    ├── world.sql
    └── audit/
```

### bunfig.toml

```toml
[install]
peer = false

[test]
coverage = true
coverageReporter = ["text", "lcov"]

[workspace]
packages = ["packages/*"]
```

### Root package.json

```json
{
  "name": "capcli",
  "private": true,
  "workspaces": ["packages/*"],
  "scripts": {
    "dev": "bun run --filter @capcli/kernel dev",
    "build": "bun run --filter '*' build",
    "test": "bun run --filter '*' test",
    "test:unit": "bun run --filter '*' test:unit",
    "test:integration": "bun run --filter '*' test:integration",
    "test:e2e": "bun run --filter '*' test:e2e",
    "lint": "bun run --filter '*' lint",
    "native:build": "cd packages/native && napi build --release"
  }
}
```

---

## 3. The Naming Law — `*.*.*`

Every file in `src/` follows: **`domain.feature.ext`**

| Pattern | Meaning | Example |
|---|---|---|
| `noun.verb.ts` | Command handler (one CLI verb) | `db.query.ts` |
| `noun.service.ts` | Shared domain logic | `db.service.ts` |
| `noun.types.ts` | Domain-local types (re-export from @capcli/types) | `routine.types.ts` |
| `noun.config.ts` | Domain config loader | `policy.loader.ts` |
| `noun.gate.ts` | Enforcement layer for domain | `db.authorizer.ts` |
| `noun.test.ts` | Test file (tier in path) | `db.query.unit.test.ts` |
| `noun.store.ts` | Zustand store (PWA only) | `audit.store.ts` |
| `noun.view.tsx` | React view component (PWA only) | `world.table.view.tsx` |
| `noun.hook.ts` | React hook (PWA only) | `audit.tail.hook.ts` |

**Forbidden names:** `index.ts`, `utils.ts`, `helpers.ts`, `constants.ts`, `types.ts` (bare), `main.ts` (except entry), `App.tsx`.

**Entry points are the sole exception:** `main.ts` at package root, `app.tsx` in PWA.

---

## 4. Package: `@capcli/types` — The Shared Contract

```
packages/types/
├── package.json
├── tsconfig.json
├── src/
│   ├── main.ts                    # barrel export
│   ├── exit.codes.ts              # 0/2/3/4/5 as const enum
│   ├── kernel.contract.ts         # { exit, json, text } shape
│   ├── audit.event.ts             # full audit event type
│   ├── capability.types.ts        # routine, api verb, view, db op
│   ├── policy.types.ts            # policy.yaml compiled shape
│   ├── governance.types.ts        # governance.yaml compiled shape
│   ├── schema.types.ts            # schema.yaml + system-schema.yaml shapes
│   ├── budget.types.ts            # frame, cascade, session pool
│   ├── identity.types.ts          # principal, agent, session
│   ├── env.types.ts               # environment, worktree, overlay
│   ├── api.types.ts               # verb, catalog, sync, quota
│   ├── routine.types.ts           # manifest, fingerprint, trust
│   ├── bind.types.ts              # cron, webhook, endpoint
│   ├── ping.types.ts              # notify, ask
│   ├── sdk.contract.ts            # createKernel() return type
│   └── cli.types.ts               # command args, flags, output shapes
└── __tests__/
    └── unit/
        └── exit.codes.unit.test.ts
```

**Rules:**
- Zero runtime code. Types + const enums only.
- No imports from other `@capcli/*` packages.
- Every other package imports from here. Never the reverse.
- Versioned independently. Breaking change = major bump.

---

## 5. Package: `@capcli/kernel` — The Gate

Domain-based. Feature-scoped. NestJS-alike structure without the ceremony:

- **Handler** (`noun.verb.ts`) = receives parsed args, calls service, returns `{ exit, json, text }`
- **Service** (`noun.service.ts`) = business logic, calls gate/db/audit
- **Gate** (`noun.gate.ts`) = enforcement (authorizer, AST, policy check)

No decorators. No DI container. No modules. Direct imports.

```
packages/kernel/
├── package.json
├── tsconfig.json
├── src/
│   ├── main.ts                    # CLI entry — citty router
│   ├── boot.ts                    # quad-lock, compile, refuse-or-serve
│   │
│   ├── domains/
│   │   ├── db/
│   │   │   ├── db.query.ts        # handler
│   │   │   ├── db.exec.ts
│   │   │   ├── db.lock.ts
│   │   │   ├── db.unlock.ts
│   │   │   ├── db.snapshot.ts
│   │   │   ├── db.restore.ts
│   │   │   ├── db.dump.ts
│   │   │   ├── db.schema.ts
│   │   │   ├── db.service.ts      # shared logic
│   │   │   ├── db.authorizer.ts   # Layer 1: rusqlite authorizer bridge
│   │   │   ├── db.ast.ts          # Layer 2: node-sql-parser gate
│   │   │   ├── db.prepare.ts      # Layer 1.5: prepare-time cross-check
│   │   │   └── db.types.ts        # re-exports from @capcli/types + local
│   │   │
│   │   ├── routine/
│   │   │   ├── routine.draft.ts
│   │   │   ├── routine.prove.ts
│   │   │   ├── routine.ship.ts
│   │   │   ├── routine.sweep.ts
│   │   │   ├── routine.stats.ts
│   │   │   ├── routine.rollback.ts
│   │   │   ├── routine.retire.ts
│   │   │   ├── routine.service.ts
│   │   │   ├── routine.sandbox.ts # bwrap/podman jail orchestration
│   │   │   ├── routine.manifest.ts # AST extraction of ctx.* calls
│   │   │   ├── routine.fingerprint.ts # runtime vs manifest comparison
│   │   │   └── routine.types.ts
│   │   │
│   │   ├── api/
│   │   │   ├── api.sync.ts
│   │   │   ├── api.diff.ts
│   │   │   ├── api.catalog.ts
│   │   │   ├── api.activate.ts
│   │   │   ├── api.prove.ts
│   │   │   ├── api.ship.ts
│   │   │   ├── api.stats.ts
│   │   │   ├── api.retire.ts
│   │   │   ├── api.deactivate.ts
│   │   │   ├── api.rollback.ts
│   │   │   ├── api.list.ts
│   │   │   ├── api.service.ts
│   │   │   ├── api.quota.ts       # _api_quota read/enforce
│   │   │   ├── api.egress.ts      # HTTP dispatch, secret injection
│   │   │   ├── api.sim.ts         # sim_mode resolution + fixture serving
│   │   │   └── api.types.ts
│   │   │
│   │   ├── bind/
│   │   │   ├── bind.cron.ts
│   │   │   ├── bind.webhook.ts
│   │   │   ├── bind.endpoint.ts
│   │   │   ├── bind.list.ts
│   │   │   ├── bind.inspect.ts
│   │   │   ├── bind.pause.ts
│   │   │   ├── bind.resume.ts
│   │   │   ├── bind.remove.ts
│   │   │   ├── bind.keys.ts
│   │   │   ├── bind.service.ts
│   │   │   ├── bind.daemon.ts     # Bun.serve() HTTP listener
│   │   │   └── bind.types.ts
│   │   │
│   │   ├── ping/
│   │   │   ├── ping.notify.ts
│   │   │   ├── ping.ask.ts
│   │   │   ├── ping.list.ts
│   │   │   ├── ping.resolve.ts
│   │   │   ├── ping.expire.ts
│   │   │   ├── ping.service.ts
│   │   │   └── ping.types.ts
│   │   │
│   │   ├── rule/
│   │   │   ├── rule.show.ts
│   │   │   ├── rule.diff.ts
│   │   │   ├── rule.apply.ts
│   │   │   ├── rule.validate.ts
│   │   │   ├── rule.service.ts
│   │   │   ├── rule.schema.loader.ts    # schema.yaml parse + expand
│   │   │   ├── rule.system.loader.ts    # system-schema.yaml parse (read-only)
│   │   │   ├── rule.policy.loader.ts    # policy.yaml compile
│   │   │   ├── rule.governance.loader.ts # governance.yaml compile
│   │   │   └── rule.types.ts
│   │   │
│   │   ├── env/
│   │   │   ├── env.new.ts
│   │   │   ├── env.use.ts
│   │   │   ├── env.list.ts
│   │   │   ├── env.inspect.ts
│   │   │   ├── env.doctor.ts
│   │   │   ├── env.merge.ts
│   │   │   ├── env.remove.ts
│   │   │   ├── env.service.ts
│   │   │   └── env.types.ts
│   │   │
│   │   ├── sys/
│   │   │   ├── sys.audit.tail.ts
│   │   │   ├── sys.audit.trace.ts
│   │   │   ├── sys.audit.query.ts
│   │   │   ├── sys.audit.replay.ts
│   │   │   ├── sys.agent.register.ts
│   │   │   ├── sys.agent.list.ts
│   │   │   ├── sys.agent.revoke.ts
│   │   │   ├── sys.doctor.ts
│   │   │   ├── sys.backup.ts
│   │   │   ├── sys.recover.ts
│   │   │   ├── sys.exec.ts
│   │   │   ├── sys.serve.ts       # daemon start/stop/restart/status
│   │   │   ├── sys.service.ts
│   │   │   ├── sys.audit.service.ts  # JSONL sink + mirror + hash chain
│   │   │   ├── sys.budget.service.ts # frame push/pop, cascade enforcement
│   │   │   └── sys.types.ts
│   │   │
│   │   ├── run/
│   │   │   ├── run.exec.ts        # capcli run <capability>
│   │   │   ├── run.search.ts      # capcli search
│   │   │   ├── run.inspect.ts     # capcli inspect (cost envelope)
│   │   │   ├── run.service.ts
│   │   │   ├── run.resolver.ts    # exact → prefix → fuzzy → semantic
│   │   │   └── run.types.ts
│   │   │
│   │   └── identity/
│   │       ├── identity.service.ts  # principal/agent/session resolution
│   │       ├── identity.socket.ts   # SO_PEERCRED binding
│   │       ├── identity.skill.ts    # skill_origin propagation
│   │       └── identity.types.ts
│   │
│   ├── shared/
│   │   ├── exit.codes.ts          # re-export + helpers
│   │   ├── output.formatter.ts    # pretty vs --json branching
│   │   ├── intent.validator.ts    # min words, blacklist, quality heuristic
│   │   ├── trust.ladder.ts        # draft/reviewed/pinned resolution
│   │   ├── config.validator.ts    # valibot schemas for YAML
│   │   └── git.service.ts         # commit, push, worktree, recover
│   │
│   └── config/
│       ├── citty.commands.ts      # CLI tree definition
│       └── kernel.config.ts       # workspace path, env detection
│
├── __tests__/
│   ├── unit/
│   │   ├── db.query.unit.test.ts
│   │   ├── db.ast.unit.test.ts
│   │   ├── db.authorizer.unit.test.ts
│   │   ├── routine.manifest.unit.test.ts
│   │   ├── routine.fingerprint.unit.test.ts
│   │   ├── api.quota.unit.test.ts
│   │   ├── api.sim.unit.test.ts
│   │   ├── intent.validator.unit.test.ts
│   │   ├── trust.ladder.unit.test.ts
│   │   ├── sys.budget.service.unit.test.ts
│   │   └── identity.skill.unit.test.ts
│   │
│   ├── integration/
│   │   ├── db.exec.integration.test.ts   # real SQLite, policy enforced
│   │   ├── db.authorizer.integration.test.ts  # C-level deny paths
│   │   ├── routine.prove.integration.test.ts  # sandbox + manifest
│   │   ├── api.sync.integration.test.ts       # fetch + compile + catalog
│   │   ├── rule.apply.integration.test.ts     # DDL + snapshot + audit
│   │   ├── sys.audit.service.integration.test.ts  # JSONL + mirror + hash
│   │   ├── boot.quadlock.integration.test.ts  # version mismatch → refuse
│   │   └── env.merge.integration.test.ts      # worktree + policy overlay
│   │
│   └── e2e/
│       ├── onboarding.journey.e2e.test.ts  # intent → world → deny → write → recover
│       ├── routine.lifecycle.e2e.test.ts   # draft → prove → ship → live → retire
│       ├── api.lifecycle.e2e.test.ts       # sync → activate → prove → ship
│       ├── budget.cascade.e2e.test.ts      # nested routines, exhaustion
│       ├── multi.env.e2e.test.ts           # dev → sim → prod journey
│       └── recovery.worst.case.e2e.test.ts # wipe → clone → recover
│
└── scripts/
    └── native.build.ts            # napi build orchestration
```

---

## 6. Package: `@capcli/sdk` — The Embedder Surface

Thin wrapper. No logic. Delegates to kernel.

```
packages/sdk/
├── package.json
├── tsconfig.json
├── src/
│   ├── main.ts                    # createKernel() entry
│   ├── sdk.kernel.ts              # createKernel implementation
│   ├── sdk.run.ts                 # kernel.run()
│   ├── sdk.db.ts                  # kernel.db.query() / kernel.db.exec()
│   ├── sdk.routine.ts             # kernel.routine.prove()
│   ├── sdk.search.ts              # kernel.search()
│   ├── sdk.inspect.ts             # kernel.inspect()
│   ├── sdk.audit.ts               # kernel.audit.tail() / kernel.audit.trace()
│   ├── sdk.brand.ts               # white-label noun resolution
│   ├── sdk.types.ts               # re-exports from @capcli/types
│   └── sdk.stream.ts              # WebSocket/SSE for audit.tail({follow})
│
├── __tests__/
│   ├── unit/
│   │   ├── sdk.kernel.unit.test.ts
│   │   └── sdk.brand.unit.test.ts
│   ├── integration/
│   │   ├── sdk.db.integration.test.ts
│   │   └── sdk.audit.integration.test.ts
│   └── e2e/
│       └── sdk.pwa.contract.e2e.test.ts  # PWA consumes SDK correctly
│
└── sdk.architecture.md            # embedder-facing docs (hidden from workspace)
```

---

## 7. Package: `@capcli/pwa` — The Human Harness

**Stack: React 19 + Vite 6 + Tailwind CSS 4 + Zustand 5.**

No Next.js. No SSR. PWA via Vite plugin. Zustand for state. TanStack Query for kernel polling. React Router for layer navigation.

```
packages/pwa/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.ts
├── postcss.config.ts
├── index.html
├── public/
│   ├── manifest.json              # PWA manifest
│   └── sw.js                      # service worker (offline cache)
│
├── src/
│   ├── main.tsx                   # React entry
│   ├── app.tsx                    # root layout + router
│   ├── app.routes.tsx             # layer route definitions
│   │
│   ├── layers/
│   │   ├── world/
│   │   │   ├── world.layer.tsx    # layer shell
│   │   │   ├── world.table.view.tsx   # table browser
│   │   │   ├── world.row.view.tsx     # row detail + audit history
│   │   │   ├── world.schema.view.tsx  # DDL + CHECK + provenance
│   │   │   ├── world.filter.hook.ts   # filter/sort params
│   │   │   └── world.types.ts
│   │   │
│   │   ├── capability/
│   │   │   ├── capability.layer.tsx
│   │   │   ├── capability.routine.view.tsx
│   │   │   ├── capability.api.view.tsx
│   │   │   ├── capability.bind.view.tsx
│   │   │   ├── capability.search.view.tsx
│   │   │   ├── capability.trust.view.tsx  # trust ladder viz
│   │   │   ├── capability.fingerprint.view.tsx  # manifest vs actual diff
│   │   │   └── capability.types.ts
│   │   │
│   │   ├── governance/
│   │   │   ├── governance.layer.tsx
│   │   │   ├── governance.policy.view.tsx
│   │   │   ├── governance.limits.view.tsx
│   │   │   ├── governance.schema.view.tsx  # interactive ERD
│   │   │   ├── governance.quadlock.view.tsx
│   │   │   └── governance.types.ts
│   │   │
│   │   ├── audit/
│   │   │   ├── audit.layer.tsx
│   │   │   ├── audit.tail.view.tsx      # live stream
│   │   │   ├── audit.event.view.tsx     # single event card
│   │   │   ├── audit.trace.view.tsx     # causal DAG
│   │   │   ├── audit.denial.view.tsx    # forensics + fix
│   │   │   ├── audit.fingerprint.view.tsx
│   │   │   ├── audit.cost.view.tsx
│   │   │   ├── audit.stream.hook.ts     # SSE/WebSocket
│   │   │   └── audit.types.ts
│   │   │
│   │   ├── budget/
│   │   │   ├── budget.layer.tsx
│   │   │   ├── budget.frame.view.tsx    # cascade tree
│   │   │   ├── budget.session.view.tsx
│   │   │   ├── budget.gauge.view.tsx    # rate limit gauges
│   │   │   ├── budget.denial.view.tsx
│   │   │   └── budget.types.ts
│   │   │
│   │   ├── environment/
│   │   │   ├── environment.layer.tsx
│   │   │   ├── environment.switcher.view.tsx
│   │   │   ├── environment.drift.view.tsx
│   │   │   ├── environment.diff.view.tsx
│   │   │   └── environment.types.ts
│   │   │
│   │   ├── approval/
│   │   │   ├── approval.layer.tsx
│   │   │   ├── approval.queue.view.tsx
│   │   │   ├── approval.evidence.view.tsx  # evidence block renderer
│   │   │   ├── approval.ask.view.tsx       # ping.ask response
│   │   │   ├── approval.veto.view.tsx      # veto window countdown
│   │   │   ├── approval.action.hook.ts     # approve/reject/veto
│   │   │   └── approval.types.ts
│   │   │
│   │   ├── recovery/
│   │   │   ├── recovery.layer.tsx
│   │   │   ├── recovery.snapshot.view.tsx
│   │   │   ├── recovery.rollback.view.tsx
│   │   │   ├── recovery.hashchain.view.tsx
│   │   │   ├── recovery.simulate.view.tsx
│   │   │   └── recovery.types.ts
│   │   │
│   │   ├── learning/
│   │   │   ├── learning.layer.tsx
│   │   │   ├── learning.gaps.view.tsx
│   │   │   ├── learning.consolidation.view.tsx
│   │   │   ├── learning.decay.view.tsx
│   │   │   ├── learning.denials.view.tsx
│   │   │   ├── learning.trust.view.tsx    # trust receipt card
│   │   │   └── learning.types.ts
│   │   │
│   │   └── identity/
│   │       ├── identity.layer.tsx
│   │       ├── identity.principal.view.tsx
│   │       ├── identity.agent.view.tsx
│   │       ├── identity.revoke.view.tsx
│   │       └── identity.types.ts
│   │
│   ├── stores/
│   │   ├── kernel.store.ts        # SDK connection state
│   │   ├── audit.store.ts         # live tail buffer
│   │   ├── approval.store.ts      # pending queue state
│   │   ├── budget.store.ts        # frame tree state
│   │   ├── env.store.ts           # active environment
│   │   └── navigation.store.ts    # cross-layer link state
│   │
│   ├── components/
│   │   ├── ui.table.tsx           # governed table renderer
│   │   ├── ui.card.tsx            # expandable card
│   │   ├── ui.gauge.tsx           # progress/rate gauge
│   │   ├── ui.badge.tsx           # env/trust/sim_mode badges
│   │   ├── ui.dag.tsx             # causal DAG visualizer
│   │   ├── ui.diff.tsx            # side-by-side diff
│   │   ├── ui.denial.tsx          # red denial card
│   │   ├── ui.masked.tsx          # ████ locked cell
│   │   ├── ui.breadcrumb.tsx      # intent chain breadcrumbs
│   │   ├── ui.confirm.tsx         # recovery confirmation
│   │   └── ui.quadlock.tsx        # quad-lock status banner
│   │
│   ├── hooks/
│   │   ├── kernel.call.hook.ts    # SDK call wrapper + exit code handling
│   │   ├── audit.poll.hook.ts     # periodic audit refresh
│   │   ├── quota.poll.hook.ts     # _api_quota 30s poll
│   │   └── approval.poll.hook.ts  # pending queue 2m poll
│   │
│   └── lib/
│       ├── sdk.client.ts          # createKernel() instance
│       ├── exit.handler.ts        # exit code → UI state mapping
│       ├── brand.resolver.ts      # white-label noun substitution
│       └── format.helpers.ts      # duration, bytes, currency
│
├── __tests__/
│   ├── unit/
│   │   ├── exit.handler.unit.test.ts
│   │   ├── brand.resolver.unit.test.ts
│   │   ├── audit.store.unit.test.ts
│   │   └── budget.store.unit.test.ts
│   ├── integration/
│   │   ├── kernel.call.hook.integration.test.ts  # mock SDK responses
│   │   ├── approval.action.hook.integration.test.ts
│   │   └── world.table.view.integration.test.ts
│   └── e2e/
│       ├── onboarding.render.e2e.test.ts   # PWA renders all 11 stages
│       ├── approval.flow.e2e.test.ts       # evidence → approve → audit
│       ├── audit.drill.e2e.test.ts         # cross-layer DAG navigation
│       └── recovery.confirm.e2e.test.ts    # snapshot → restore → event
│
└── pwa.architecture.md            # symlink or reference to root doc
```

---

## 8. Package: `@capcli/native` — The Rust Crate

```
packages/native/
├── Cargo.toml
├── build.rs
├── src/
│   ├── lib.rs                     # napi entry
│   ├── db.open.rs                 # open SQLite with WAL
│   ├── db.authorizer.rs           # set_authorizer closure from policy
│   ├── db.query.rs                # prepared statement → rows
│   ├── db.execute.rs              # execute with changes count
│   ├── db.snapshot.rs             # VACUUM INTO
│   ├── db.restore.rs              # restore from snapshot
│   └── db.types.rs                # napi type bridges
│
├── __tests__/
│   ├── unit/
│   │   └── db.authorizer.unit.test.ts  # via napi from TS
│   └── integration/
│       └── db.authorizer.integration.test.ts  # real deny paths
│
└── native.architecture.md         # crate docs
```

### Cargo.toml

```toml
[package]
name = "capcli_db"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
napi = { version = "2", features = ["napi8"] }
napi-derive = "2"
rusqlite = { version = "0.31", features = ["bundled"] }
```

Build: `napi build --release` → `capcli_db.node`

---

## 9. Implementation Stack (absorbed from dead stack.md)

| Layer | Choice | Replaces |
|---|---|---|
| Runtime | Bun | Node.js |
| SQLite binding | rusqlite via napi-rs → `capcli_db.node` | better-sqlite3 |
| Authorizer (L1) | `conn.authorizer(Some(closure))` — C-level | AST-only |
| AST gate (L2) | `node-sql-parser` (sqlite dialect) | regex |
| Prepare cross-check (L1.5) | `sqlite3_prepare_v2` dry-run + `EXPLAIN` | none |
| CLI framework | `citty` (unjs) | commander, yargs |
| YAML parse | `yaml` (eemeli) | js-yaml |
| Config validation | `valibot` | zod, ajv |
| PWA framework | React 19 | Svelte, Solid |
| PWA build | Vite 6 | webpack, Next |
| PWA styling | Tailwind CSS 4 | CSS modules, styled-components |
| PWA state | Zustand 5 | Redux, Jotai, Recoil |
| PWA data | TanStack Query 5 | SWR, RTK Query |
| PWA routing | React Router 7 | TanStack Router |
| PWA real-time | native EventSource / WebSocket | Socket.io |
| HTTP serve | `Bun.serve()` | Express, Hono |
| Subprocess | `Bun.spawn()` | child_process |
| Audit sink | `Bun.file().writer()` | fs.appendFile |
| Hashing | `Bun.CryptoHasher("sha256")` | crypto module |
| UUID | `crypto.randomUUID()` | uuid package |
| Test runner | `bun:test` | vitest, jest |
| E2E (PWA) | Playwright | Cypress |
| E2E (kernel) | `bun:test` + temp workspaces | — |

### Bun Built-ins (zero deps)

| Need | Built-in |
|---|---|
| HTTP serve/webhook | `Bun.serve()` |
| Subprocess | `Bun.spawn()` |
| File streaming | `Bun.file().writer()` |
| Hashing | `Bun.CryptoHasher("sha256")` |
| UUID | `crypto.randomUUID()` |
| Test runner | `bun:test` |
| Env vars | `Bun.env` |
| Workspace resolution | `bunfig.toml` |
| Package linking | native workspace protocol |

### Dependency Count

```
npm:    6  (node-sql-parser, yaml, valibot, citty, react, zustand)
        + PWA: react-dom, react-router, @tanstack/react-query, tailwindcss, vite, playwright
rust:   3  (napi, napi-derive, rusqlite)
total:  9 kernel deps + PWA dev deps
```

---

## 10. Test Architecture

### Three Tiers, One Law

| Tier | Scope | Speed | Isolation | Runner |
|---|---|---|---|---|
| **unit** | One function, one decision | <50ms | Pure mocks, no I/O | `bun:test` |
| **integration** | One domain, real I/O | <5s | Real SQLite, temp fs, no network | `bun:test` |
| **e2e** | Full journey, all layers | <60s | Real workspace, git, sandbox | `bun:test` + Playwright (PWA) |

### Naming Law for Tests

```
source:  db.query.ts
unit:    __tests__/unit/db.query.unit.test.ts
integ:   __tests__/integration/db.query.integration.test.ts
e2e:     __tests__/e2e/db.query.e2e.test.ts
```

Every test file mirrors its source file's domain and feature. No orphan tests.

### Test Scripts (per package)

```json
{
  "scripts": {
    "test": "bun test",
    "test:unit": "bun test __tests__/unit/",
    "test:integration": "bun test __tests__/integration/",
    "test:e2e": "bun test __tests__/e2e/",
    "test:pwa:e2e": "playwright test"
  }
}
```

### What Each Tier Proves

| Tier | Proves | Example |
|---|---|---|
| unit | Logic correctness in isolation | AST rejects `UPDATE` without `WHERE` |
| integration | Domain enforcement with real substrate | Authorizer denies `ATTACH` on real SQLite |
| e2e | Full journey through all gates | Intent → world → deny → write → recover |

### E2E Workspace Strategy

Each e2e test gets a fresh temp workspace:
```ts
const ws = await createTempWorkspace()  // git init, schema.yaml, policy.yaml
// ... test ...
await ws.cleanup()
```

PWA e2e uses Playwright with a real kernel process:
```ts
// playwright.config.ts
webServer: { command: 'bun run packages/kernel/src/main.ts --env test' }
```

---

## 11. Build & Run

```bash
# Native crate (once, or on Rust change)
cd packages/native && napi build --release

# Dev (kernel)
bun run --filter @capcli/kernel dev

# Dev (PWA)
bun run --filter @capcli/pwa dev

# Build all
bun run build

# Test all
bun run test

# Test one tier
bun run test:unit
bun run test:integration
bun run test:e2e

# SDK publish
cd packages/sdk && bun build src/main.ts --outdir dist --target node
```

### Build Outputs

| Package | Output | Format |
|---|---|---|
| @capcli/kernel | `dist/cli.js` | Bun single-file |
| @capcli/sdk | `dist/index.js` + `dist/index.d.ts` | ESM + types |
| @capcli/pwa | `dist/` | Static Vite build |
| @capcli/native | `capcli_db.node` | NAPI binary |

---

## 12. Cross-Package Dependency Graph

```
@capcli/types ← (imported by all, imports none)
     ↑
@capcli/kernel ← imports types, native
     ↑
@capcli/sdk ← imports types, kernel
     ↑
@capcli/pwa ← imports types, sdk (runtime only)
```

**No circular deps. No kernel importing PWA. No PWA importing kernel directly.**

The PWA talks to the kernel exclusively through `@capcli/sdk`. Period.

---

## 13. File Ownership & Boundaries

| File/Dir | Owner | Agent access |
|---|---|---|
| `packages/kernel/src/domains/**` | Kernel devs | Read-only reference |
| `packages/pwa/src/**` | Frontend devs | N/A |
| `packages/native/src/**` | Rust devs | N/A |
| `workspace/schema.yaml` | Agent (governed) | Read-write via gate |
| `workspace/system-schema.yaml` | Kernel releases | Read-only for agent |
| `workspace/policy.yaml` | Human | Read-only for agent |
| `workspace/governance.yaml` | Human | Read-only for agent |
| `workspace/routines/*.py` | Agent (governed) | Read-write via gate |
| `workspace/apis/*.yaml` | Kernel (compiled) | Read-only for agent |

---

## 14. Anti-Decisions

| Temptation | Refusal |
|---|---|
| Turborepo / Nx / Lerna | Bun workspaces are sufficient. Zero orchestration overhead. |
| pnpm | Bun resolves natively. No second package manager. |
| `index.ts` barrels per folder | `*.*.*` naming makes barrels redundant. Import by filename. |
| NestJS decorators / DI | Overkill. Direct imports. Three layers max: handler → service → gate. |
| Separate `dto/` folders | Types live in `@capcli/types`. Domain-local types in `noun.types.ts`. |
| `utils.ts` / `helpers.ts` | Name the function by what it does: `intent.validator.ts`, not `utils.ts`. |
| Co-located tests in `src/` | Tests live in `__tests__/` with tier subfolders. Source stays clean. |
| Vitest / Jest | `bun:test` is built-in, fast, zero-config. No reason for another runner. |
| Next.js / Remix for PWA | Vite + React is sufficient. No SSR needed. PWA is a client. |
| Redux / MobX | Zustand. Five stores max. No boilerplate. |
| CSS-in-JS | Tailwind. Utility classes. No runtime style computation. |
| Storybook | The PWA has 10 layers. Each layer IS the story. No component gallery. |
| Monorepo-wide tsconfig | Each package has its own `tsconfig.json`. Root has `tsconfig.base.json` for shared compiler options only. |
| stack.md | Dead. Absorbed here. One source of truth for implementation choices. |

---

## 15. Invariants

1. Every source file follows `domain.feature.ext`. No exceptions except `main.ts` and `app.tsx`.
2. Types are centralized in `@capcli/types`. No package exports types that another package defines.
3. The dependency graph is acyclic and unidirectional: types ← kernel ← sdk ← pwa.
4. Tests mirror source. Every handler has at least a unit test. Every domain has at least an integration test. Every lifecycle has an e2e test.
5. The PWA never imports from `@capcli/kernel`. It imports from `@capcli/sdk`. Period.
6. The native crate exposes exactly six functions: `open`, `set_authorizer`, `query`, `execute`, `snapshot`, `restore`. No more.
7. Build outputs are deterministic. Same source + same deps = same binary. No timestamps in output.
8. `workspace/` is gitignored. It is a runtime artifact. The repo contains architecture, code, and config templates. Never live data.
9. `stack.md` does not exist. Implementation choices live in this file, section 9. One source. No drift.
10. The monorepo has zero orchestration tools. Bun resolves, builds, tests, runs. If Bun can't do it, the task is wrong.

---

## The One-Liner

> **One Bun monorepo, five packages sealed by domain, every file named `domain.feature.ext`, types centralized, tests tiered, the PWA speaks only through the SDK, the native crate exposes six functions, and the entire implementation stack lives here — once, final, no redundancy, no second file, no orchestration tool, no escape hatch.**