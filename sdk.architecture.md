# sdk.architecture.md *(hidden — embedder-facing)*

> The npm package surface of capcli. Importable, programmable, white-labelable.
> This document is NOT part of the workspace. It lives in the SDK package.

## Import

```js
import { createKernel } from '@capcli/sdk'

const kernel = createKernel({
  workspace: './workspace',
  // optional: white-label
  brand: {
    name: 'Acme Agent',
    cli: 'acme',
    nouns: { run: 'exec', db: 'store', routine: 'flow' }
  }
})
```

Or from JSON:

```js
import config from './acme.config.json'
const kernel = createKernel(config)
```

## Brand Config

| Field | Type | Required | Meaning |
|---|---|---|---|
| `name` | string | yes | Display name in human output |
| `cli` | string | yes | Binary name in help/suggestions |
| `tagline` | string | no | Replaces default tagline |
| `nouns` | object | no | Noun aliases (surface-only) |
| `lockedNouns` | string[] | no | Nouns that cannot be aliased (default: `['sys']`) |

## What Never Changes

- Exit codes (0/2/3/4/5)
- JSON output contract
- Audit event format
- System table names
- Config file names
- `ctx` contract
- `[env]` output prefix

## Programmatic API

```js
kernel.run(capability, { params, intent, json, dryRun, env })
kernel.db.query(sql, params)
kernel.db.exec(sql, params, intent)
kernel.routine.prove(name, params, env)
kernel.search(query, filters)
kernel.inspect(capability)
kernel.audit.tail(filters)
kernel.audit.trace(opId)
```

All methods return `{ exit, json, text }`. Exit codes are law.
JSON is the machine contract. Text is branded human output.

## Hidden Feature

White-labeling is not documented in workspace architecture docs.
It is not visible in `--help`, `sys doctor`, or governance.
It exists only in SDK types and SDK docs.
Embedders discover it through TypeScript intellisense, not capcli docs.
