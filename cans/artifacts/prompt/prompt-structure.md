# Canonical Prompt Bank, Trigger & Progressive Disclosure Specification

`cans/artifacts/prompt/prompt-structure.md`  
*(Part 1/3)*

---

## 0. The Core Law: Remedy vs. Campaign

Modern AI harnesses fake progressive disclosure: they index every skill and prompt at boot, inject massive catalogs into the context window, and label the index "disclosure." This is pre-loading with extra steps, destroying KV-cache performance and causing prompt drift.

Capcli enforces compiled physics:

1. **Zero Prompt Bloat at Boot:** No prompt bank, skill catalog, or manifest is mounted into the system prompt. Boot context contains only a **120-token Zero-Turn Seed Directive** defining the laws of physics.
2. **The Remedy vs. Campaign Boundary:**
   * **A Remedy closes a single command:** Emitted directly in CLI diagnostics on standard non-zero exits (e.g., `remedy: add LIMIT 10`, `state_modified: false`). Remedies fix syntax, add missing parameters, or cite boundary limits.
   * **A Prompt opens an architectural campaign:** Emitted as a progressive pointer when the agent must perform multi-stage cognitive work (e.g., synthesize a domain model, author `schema.yaml`, plan an online DDL migration).
3. **The 10-Noun Invariant:** There is no `prompt` CLI noun or verb. Prompts are versioned, kernel-governed documents residing under the Universal Resource Pointer (URP):  
   `doc://prompt/{bank}/{slug}@{version}`  
   Prompts are inspected via `capcli inspect` and read via `capcli doc read --section`.
4. **Single-File Markdown Architecture:** Dual-file pairings (`.json` + `.txt`) are banned. Every prompt bank artifact is a single `.md` file with structured YAML frontmatter for machine predicates and Markdown headers for progressive disclosure stages (`## section:stage_*`).
5. **The 4-Level Progressive Disclosure Ladder (L0–L3):** Prompts are served in deterministic slices. Inverting levels or leaking full bodies in a single turn is prohibited and blocked by kernel tests.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        HARNESS BOOT (Turn 0)                           │
│  120-token Seed Directive: "Interact ONLY via capcli <noun> <verb>"    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Command Execution
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     DECISION AT KERNEL INTERCEPT                       │
│                                                                        │
│   Is the issue a single command fix?                                   │
│   ├── YES ──► Emit Diagnostic REMEDY (Line 1 Action, state_modified:0) │
│   │           (e.g., AST denial, missing intent, claim lease held)     │
│   │                                                                    │
│   └── NO  ──► Emit L1 PROMPT TRAILER (Campaign needed)                 │
│               `prompt: doc://prompt/{bank}/{slug}@{v}`                 │
│               (Genesis, Schema Migration, Overview Codification)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Progressive Disclosure
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               THE PROGRESSIVE DISCLOSURE LADDER (via doc)              │
│                                                                        │
│   L1: Trailer on Trigger Screen (<=30 tokens)                          │
│   L2: `capcli inspect doc://prompt/...` (<=150 token envelope)         │
│   L3: `capcli doc read ... --section stage_N` (<=500 tokens per slice) │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Directory Tree & Pure Markdown Architecture

```
cans/artifacts/prompt/
  manifest.json
  _triggers.json
  prompt-structure.md
  banks/
    genesis/
      genesis.blank_world.empty.md
    onboarding/
      onboarding.harness.empty.md
      onboarding.human.stub.md
    authoring/
      authoring.overview.absent.md
      authoring.routine.gaps.md
    crucible/
      crucible.execution.starved.md
    evolution/
      evolution.schema.drift.md
    promotion/
      promotion.routine.passed.md
    wire/
      wire.catalog.empty.md
    forensics/
      forensics.audit.tampered.md
    hitl/
      hitl.ping_ask.suspended.md
```

### 1.1 Structural Invariants
* **Zero File Pairing:** No companion `.json` or `.txt` files exist in `banks/`. Every prompt artifact is self-contained in a single `.md` file.
* **YAML Frontmatter Mandate:** Every prompt file begins with strict YAML frontmatter (`---`) declaring IDs, triggers, variable schemas, and section token caps.
* **Depth Ceiling:** File paths relative to `banks/` must remain exactly 2 components: `{bank}/{filename}`.
* **4-Segment Token Naming:**
  ```
  {bank}.{slug}.{state}.{condition}.md
  ```
  `state` must be a valid wireframe state token (`empty`, `stub`, `drift`, `passed`, `tampered`, `gaps`, `absent`, `starved`, `suspended`).
* **Deterministic Variable Substitution:** Variables like `{{env}}` or `{{domain_tables}}` are resolved exclusively from kernel state. Missing variables trigger an `exit 3` refusal; the kernel never uses LLMs to hallucinate state facts.

---

## 2. The 4-Level Progressive Disclosure Ladder

| Level | Invocation | Payload Cap | Contains | Prohibited Content |
|---|---|---|---|---|
| **L0** | Boot / Idle / Nominal Execution | 0 prompt tokens | Nothing (or 120-token Seed Directive on harness init) | Bank entries, catalog dumps, section bodies |
| **L1** | Screen matching `_triggers.json` | $\le 30$ tokens (trailer) | Trailer line: `prompt: doc://prompt/...` + trigger reason | Body text, section details, multi-stage summaries |
| **L2** | `capcli inspect doc://prompt/...` | $\le 150$ tokens | Envelope: variables, section index, token caps, `can_render_now` | Rendered section markdown |
| **L3** | `capcli doc read <ptr> --section <id>` | $\le 500$ tokens per slice | Exactly one rendered section with kernel-substituted variables | Other sections, full body text, raw unparsed templates |

### Rules of Engagement
1. **L1 is a Trailer:** On triggering screens, stdout appends a one-line trailer (or `next_prompt` field in `--json`). Exit codes, `[{env}:{tier}]` prefixes, and `state_modified: false` guarantees remain untouched.
2. **Specificity Precedence:** If multiple triggers match, the kernel picks the most specific predicate (`screen_id` > `domain` > `exit_code`).
3. **Prompt Suppression on Simple Remedies:** If a screen's diagnostic `remedy:` field fully specifies the fix (e.g., missing vault secret or missing `LIMIT`), L1 emission is banned.
4. **Shortcut Execution:** An autonomous harness that parses the L1 trailer can jump straight to L3 (`doc read --section stage_1`), skipping L2 inspection if its execution plan is already formed.

---

## 3. Core Engine Manifests

### 3.1 `manifest.json`

```json
{
  "$schema": "prompt/manifest/v2",
  "version": 2,
  "compiled_at": "2026-10-06T00:00:00Z",
  "banks": [
    "genesis",
    "onboarding",
    "authoring",
    "crucible",
    "evolution",
    "promotion",
    "wire",
    "forensics",
    "hitl"
  ],
  "pointer_type": "doc://prompt/{bank}/{slug}@{version}",
  "ceilings": {
    "zero_turn_seed": 120,
    "l1_trailer_tokens": 30,
    "search_pointer_tokens": 60,
    "l2_envelope_tokens": 150,
    "l3_slice_tokens": 500
  },
  "delimiters": {
    "start": "<<<CAPCLI_DIRECTIVE_START:{ID}>>>",
    "end": "<<<CAPCLI_DIRECTIVE_END:{ID}>>>",
    "ephemeral_start": "<!-- CAPCLI:EPHEMERAL:START -->",
    "ephemeral_end": "<!-- CAPCLI:EPHEMERAL:END -->"
  },
  "output_contract": {
    "human_trailer_prefix": "prompt:",
    "json_field": "next_prompt",
    "state_modified_on_serve": false
  }
}
```

### 3.2 `_triggers.json`

```json
{
  "$schema": "prompt/triggers/v2",
  "version": 2,
  "triggers": [
    {
      "id": "t_genesis_blank_world",
      "screen_id": "db.schema.success.empty",
      "predicate": { "domain_tables": 0 },
      "prompt": "doc://prompt/genesis/blank_world@1",
      "serve": "L1",
      "reason": "blank world: 0 domain tables"
    },
    {
      "id": "t_genesis_search_empty",
      "screen_id": "run.search.success.empty",
      "predicate": { "domain_tables": 0 },
      "prompt": "doc://prompt/genesis/blank_world@1",
      "serve": "L1",
      "reason": "no capabilities and no world to search"
    },
    {
      "id": "t_onboarding_harness",
      "screen_id": "sys.doctor.success.nominal",
      "predicate": { "caller": "harness", "domain_tables": 0 },
      "prompt": "doc://prompt/onboarding/harness@1",
      "serve": "L1",
      "reason": "harness at nominal doctor with empty domain"
    },
    {
      "id": "t_onboarding_human",
      "screen_id": "sys.help.success.stub",
      "predicate": { "caller": "human" },
      "prompt": "doc://prompt/onboarding/human@1",
      "serve": "L1",
      "reason": "human operator requested onboarding tour"
    },
    {
      "id": "t_authoring_overview",
      "screen_id": "routine.prove.success.passed",
      "predicate": { "overview_exists": false },
      "prompt": "doc://prompt/authoring/overview_absent@1",
      "serve": "L1",
      "reason": "world lacks ground zero situational overview"
    },
    {
      "id": "t_authoring_gaps",
      "screen_id": "run.search.success.gaps",
      "predicate": { "gap_count": ">=1" },
      "prompt": "doc://prompt/authoring/routine_gaps@1",
      "serve": "L1",
      "reason": "telemetry shows uncodified operational sequence"
    },
    {
      "id": "t_crucible_starved",
      "screen_id": "run.execute.denial.budget_cascade",
      "predicate": { "domain": "policy.budget" },
      "prompt": "doc://prompt/crucible/execution_starved@1",
      "serve": "L1",
      "reason": "call-tree preflight failed budget cascade bounds"
    },
    {
      "id": "t_evolution_drift",
      "screen_id": "rule.diff.success.populated",
      "predicate": {},
      "prompt": "doc://prompt/evolution/schema_drift@1",
      "serve": "L1",
      "reason": "schema drift requires forward migration plan"
    },
    {
      "id": "t_promotion_passed",
      "screen_id": "routine.prove.success.passed",
      "predicate": { "trust": "draft" },
      "prompt": "doc://prompt/promotion/routine_passed@1",
      "serve": "L1",
      "reason": "proof passed: routine eligible for promotion"
    },
    {
      "id": "t_wire_empty",
      "screen_id": "api.catalog.success.empty",
      "predicate": {},
      "prompt": "doc://prompt/wire/catalog_empty@1",
      "serve": "L1",
      "reason": "no external API catalogs configured"
    },
    {
      "id": "t_forensics_tamper",
      "screen_id": "sys.doctor.warning.tamper",
      "predicate": {},
      "prompt": "doc://prompt/forensics/audit_tampered@1",
      "serve": "L1",
      "reason": "causal DAG hash chain broken: quarantine active"
    },
    {
      "id": "t_hitl_suspended",
      "screen_id": "run.execute.suspended.ask",
      "predicate": {},
      "prompt": "doc://prompt/hitl/ping_ask_suspended@1",
      "serve": "L1",
      "reason": "frame suspended awaiting human inquiry resolution"
    }
  ]
}
```

---

## 4. Master Prompt Bank Inventory

| Bank | Stem | Trigger Screen(s) | Architectural Focus |
|---|---|---|---|
| **genesis** | `genesis.blank_world.empty` | `db.schema.success.empty`, `run.search.success.empty` | Business entity synthesis, initial `schema.yaml` authoring, compile, overview, wire lockdown. |
| **onboarding**| `onboarding.harness.empty` | `sys.doctor.success.nominal` (harness) | H0–H7 Autonomous harness discipline: contract discovery, dry-run rehearsal, proving. |
| **onboarding**| `onboarding.human.stub` | `sys.help.success.stub` (human) | S0–S10 Human pedagogical path: read $\rightarrow$ deliberate denial $\rightarrow$ write $\rightarrow$ snapshot $\rightarrow$ restore proof. |
| **authoring** | `authoring.overview.absent` | `routine.prove.success.passed` (no overview) | Scaffold mandatory `<500` token `routines/overview.py` situational primer. |
| **authoring** | `authoring.routine.gaps` | `run.search.success.gaps` | Codifying repeated raw SQL and API sequences into a governed routine. |
| **crucible** | `crucible.execution.starved` | `run.execute.denial.budget_cascade` | Resolving budget cascade starvation, syscall 42 traps, contested leases, and secret injection. |
| **evolution** | `evolution.schema.drift` | `rule.diff.success.populated` | Authoring 4-phase online DDL migrations (Expand, Backfill, Contract, Pin). |
| **promotion** | `promotion.routine.passed` | `routine.prove.success.passed` (draft) | Evaluating canary metrics, SLA gates, and enqueuing ship promotion. |
| **wire** | `wire.catalog.empty` | `api.catalog.success.empty` | Importing OpenAPI specs, capturing response contracts, and gating wire egress. |
| **forensics** | `forensics.audit.tampered` | `sys.doctor.warning.tamper` | Forensic ledger isolation, inspecting quarantine sinks, validating WORM roots. |
| **hitl** | `hitl.ping_ask.suspended` | `run.execute.suspended.ask` | Human-in-the-loop inquiry management, Cockpit card resolution, OCC state fence handling. |

---

## 5. Canonical Prompt Campaigns (Pure `.md` with Frontmatter)

### 5.1 Turn-Zero Seed Directive (Harness Baseline)
*Location:* Mounted once during session initialization.  
*Token Count:* 118

```text
[KERNEL CONTRACT]
State mutations and raw network calls via bash are physically blocked (seccomp-bpf/prepare-authorizer).
Interact with reality exclusively via: `capcli <noun> <verb>`.
- Blank world? Run `capcli sys doctor` to trigger Genesis.
- Discover actions: `capcli search "<intent>"`
- Test mutations: `capcli sql "<query>" --dry-run`
- Directives and remedies are injected in-band via CLI output.
Completion requires an audit verification hash: `capcli sys verify <audit_op>`.
```

---

### 5.2 Genesis Campaign: Blank World (`genesis.blank_world.empty.md`)

```markdown
---
id: doc://prompt/genesis/blank_world@1
stem: genesis.blank_world.empty
bank: genesis
slug: blank_world
version: 1
trust: draft
trigger:
  screens: ["db.schema.success.empty", "run.search.success.empty"]
  predicate:
    domain_tables: 0
vars:
  - name: env
    type: string
    source: kernel.env
  - name: tier
    type: string
    source: kernel.tier
  - name: domain_tables
    type: int
    source: kernel.schema.domain_table_count
sections:
  stage_1_intent: 120
  stage_2_schema: 290
  stage_3_compile: 80
  stage_4_overview: 220
  stage_5_wire: 140
slice_max_tokens: 500
---

# ⚡ CAPCLI GENESIS DIRECTIVE (BLANK WORLD DETECTED)
Workspace contains {{domain_tables}} domain tables in environment [{{env}}:{{tier}}].
You are operating in a void. Do not write ad-hoc bash scripts.
Execute the 5-stage Genesis protocol. Slices must be executed in order.

## section:stage_1_intent
Find the core business mission from harness history (Ledger 1):
• Hermes: sqlite3 ~/.hermes/state.db "SELECT query FROM sessions ORDER BY timestamp ASC LIMIT 10;"
• OpenClaw: head -n 20 ~/.openclaw/agents/main/sessions/latest.jsonl
Identify:
1. Core Entities (e.g., Orders, Customers, Invoices)
2. State Transitions (e.g., pending -> paid -> fulfilled)
3. External Wires (e.g., Stripe, Logistics, SendGrid)
Output of this stage must be an entity list, not code.

## section:stage_2_schema
Declare the physical world in `schema.yaml` using Capcli AST shorthands. Never execute raw `CREATE TABLE`:
```yaml
version: 1
engine: sqlite
db: workspace.db

tables:
  customers:
    prov: true
    columns:
      id: pk
      email: text!
      name: text
      stripe_customer_id: text
      billing_status: text=active
      data: json mask=true

  orders:
    prov: true
    imm_rows: false
    columns:
      id: pk
      customer_id: int ref=customers.id
      total_cents: int~
      status: text=pending
      tracking_num: text
    chk:
      - "status IN ('pending', 'paid', 'shipped', 'cancelled', 'refunded')"
      - "total_cents >= 0"
    idx:
      - [customer_id]
      - [status]

views:
  orders_summary:
    exposes: [orders]
    query: "SELECT status, count(*) as count, sum(total_cents) as volume FROM orders GROUP BY status;"
```

## section:stage_3_compile
Validate syntax, semantics, and compile the physical DDL:
```bash
capcli rule validate
capcli apply -m "Genesis: Initialize business world schema"
```
If errors occur, read the remedy diagnostic, fix `schema.yaml`, and re-run.

## section:stage_4_overview
Author the Ground Zero primer (`routines/overview.py`).
Situational KPIs must remain strictly under 500 result tokens:
```python
from capcli import routine, ctx

@routine(name="overview", idempotent=True, limits={"max_ops": 5, "max_duration_seconds": 10})
def overview():
    kpis = ctx.db.query("SELECT * FROM orders_summary")
    pending = ctx.db.query("SELECT count(*) as count FROM orders WHERE status = 'pending'")
    return {
        "status": "nominal",
        "pending_orders": pending[0]["count"] if pending else 0,
        "kpis": kpis
    }
```
Prove and pin it:
```bash
capcli routine prove overview --env sim
capcli routine ship overview pinned --reason "Mount system overview baseline"
```

## section:stage_5_wire
Import and lock external wire egress before invoking external endpoints:
```bash
capcli api import stripe /v1/charges POST --spec https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.yaml
capcli api prove stripe.charges.create --env sim
capcli api ship stripe.charges.create reviewed --reason "Order billing capability"
```
```

---

### 5.3 Onboarding Campaign: Harness (`onboarding.harness.empty.md`)

```markdown
---
id: doc://prompt/onboarding/harness@1
stem: onboarding.harness.empty
bank: onboarding
slug: harness
version: 1
trust: draft
trigger:
  screens: ["sys.doctor.success.nominal"]
  predicate:
    caller: harness
    domain_tables: 0
vars:
  - name: env
    type: string
    source: kernel.env
  - name: tier
    type: string
    source: kernel.tier
sections:
  stage_1_contract: 100
  stage_2_discovery: 140
  stage_3_rehearsal: 150
  stage_4_proving: 110
slice_max_tokens: 500
---

# ⚡ AUTONOMOUS HARNESS ONBOARDING PROTOCOL (H0–H7)
Host physics verified nominal. System is uninitialized in [{{env}}:{{tier}}].
Operate strictly via structured machine contracts (`--json`).

## section:stage_1_contract
Verify machine-level JSON envelope parity:
```bash
capcli sys doctor --json
```
Assert: `exit_code == 0`, `state_modified == false`, `data.status == "nominal"`.

## section:stage_2_discovery
Enumerate registered capabilities and catalog verbs:
```bash
capcli search "" --json
```
Parse the JSON response array. If zero capabilities exist, trigger the Genesis campaign:
```bash
capcli doc read doc://prompt/genesis/blank_world@1 --section stage_1_intent
```

## section:stage_3_rehearsal
Practice non-mutating preview execution:
```bash
capcli sql "SELECT 1" --dry-run --json
```
Assert: `state_modified == false`.
Never dispatch mutating SQL (`UPDATE`, `DELETE`, `INSERT`) without a preceding `--dry-run`.

## section:stage_4_proving
Verify ability to execute simulation proving:
```bash
capcli routine prove overview --env sim --json
```
All autonomous routines must pass 100% simulation verification before production deployment.
```

---

*(Continued in Part 2/3: Campaigns for Human Onboarding, Overview Authoring, Routine Mining, Execution Crucible, Schema Evolution, Trust Promotion, Wire Lockdown, Forensics, and Human-in-the-Loop)*

# Canonical Prompt Bank, Trigger & Progressive Disclosure Specification

`cans/artifacts/prompt/prompt-structure.md`  
*(Part 2/3)*

---

### 5.4 Onboarding Campaign: Human Pedagogical Tour (`onboarding.human.stub.md`)

```markdown
---
id: doc://prompt/onboarding/human@1
stem: onboarding.human.stub
bank: onboarding
slug: human
version: 1
trust: draft
trigger:
  screens: ["sys.help.success.stub"]
  predicate:
    caller: human
vars:
  - name: env
    type: string
    source: kernel.env
  - name: tier
    type: string
    source: kernel.tier
sections:
  stage_1_probe: 110
  stage_2_read: 120
  stage_3_denial: 160
  stage_4_write: 130
  stage_5_recovery: 150
slice_max_tokens: 500
---

# ⚡ HUMAN OPERATOR ONBOARDING TOUR (S0–S10)
Welcome to Capcli. Execution physics are enforced at compile time in [{{env}}:{{tier}}].
Follow the 5-stage pedagogical path to understand deterministic boundaries.

## section:stage_1_probe
Run host readiness diagnostics:
```bash
capcli sys doctor
```
Locate registered capabilities dynamically:
```bash
capcli search "order"
capcli inspect cap://dispatch_order@1
```

## section:stage_2_read
Execute an AST-bounded read against the database:
```bash
capcli sql "SELECT * FROM orders LIMIT 5"
```
Reads do not mutate state (`state_modified: false`).

## section:stage_3_denial
Trigger a deliberate policy denial to observe compiler physics:
```bash
capcli sql "UPDATE orders SET status = 'shipped'"
```
Observe prepare-time interception (`exit 2`). AST blocks unbounded mutations.
Zero rows are touched.

## section:stage_4_write
Remediate the write using explicit WHERE bounds, LIMIT, and causal intent:
```bash
capcli sql "UPDATE orders SET status = 'shipped' WHERE id = 1 LIMIT 1" -m "Manual order dispatch"
```
The mutation commits and appends an immutable record to `_audit`.

## section:stage_5_recovery
Practice snapshot reversal and verify integrity:
```bash
capcli db snapshot --reason "Pre-experiment baseline"
capcli db restore snap_latest
capcli sys doctor --report
```
Inspect the generated Trust Receipt.
```

---

### 5.5 Authoring Campaign: Overview Primer (`authoring.overview.absent.md`)

```markdown
---
id: doc://prompt/authoring/overview_absent@1
stem: authoring.overview.absent
bank: authoring
slug: overview_absent
version: 1
trust: draft
trigger:
  screens: ["routine.prove.success.passed"]
  predicate:
    overview_exists: false
vars:
  - name: env
    type: string
    source: kernel.env
sections:
  stage_1_scaffold: 140
  stage_2_bound: 130
  stage_3_pin: 110
slice_max_tokens: 500
---

# ⚡ GROUND ZERO OVERVIEW CODIFICATION PROTOCOL
Your workspace lacks a situational overview routine. Autonomous agents will burn tokens
blindly querying tables unless grounded by a unified briefing.

## section:stage_1_scaffold
Scaffold `routines/overview.py` aggregating core domain counts:
```python
from capcli import routine, ctx

@routine(name="overview", idempotent=True, limits={"max_ops": 5, "max_duration_seconds": 5})
def overview():
    kpis = ctx.db.query("SELECT * FROM orders_summary")
    pending = ctx.db.query("SELECT count(*) as count FROM orders WHERE status = 'pending'")
    return {
        "status": "nominal",
        "pending_orders": pending[0]["count"] if pending else 0,
        "kpis": kpis
    }
```

## section:stage_2_bound
Ensure the overview output envelope stays strictly below 500 result tokens.
Never return unbounded lists or raw JSON blobs inside overview payloads.

## section:stage_3_pin
Rehearse in simulation and promote to pinned:
```bash
capcli routine prove overview --env sim
capcli routine ship overview pinned --reason "Establish system overview baseline"
```
```

---

### 5.6 Authoring Campaign: Routine Mining (`authoring.routine.gaps.md`)

```markdown
---
id: doc://prompt/authoring/routine_gaps@1
stem: authoring.routine.gaps
bank: authoring
slug: routine_gaps
version: 1
trust: draft
trigger:
  screens: ["run.search.success.gaps"]
  predicate:
    gap_count: ">=1"
vars:
  - name: env
    type: string
    source: kernel.env
sections:
  stage_1_analyze: 130
  stage_2_scaffold: 160
  stage_3_prove: 120
slice_max_tokens: 500
---

# ⚡ ROUTINE GAP MINING PROTOCOL
Operational telemetry detected uncodified multi-step commands executed via raw SQL or ad-hoc calls.
Codify these repeated patterns into governed routines.

## section:stage_1_analyze
Inspect repeated query sequences from the causal audit log:
```bash
capcli sys audit query "SELECT command, count(*) FROM _audit GROUP BY command HAVING count(*) > 5"
```
Identify operations that must run atomically.

## section:stage_2_scaffold
Scaffold a typed routine wrapping the operational sequence:
```bash
capcli routine new <routine_name> --runtime python
```
Enforce strict boundaries:
- Maximum 150 Lines of Code (LOC)
- Maximum 8 typed `Param` variables
- Explicit `limits={"max_ops": N, "max_duration_seconds": S}`

## section:stage_3_prove
Rehearse the scaffolded routine against masked simulation data:
```bash
capcli routine prove <routine_name> --env sim
capcli routine ship <routine_name> reviewed --reason "Codify operational pattern from telemetry"
```
```

---

### 5.7 Execution Crucible Campaign: Starvation & Recovery (`crucible.execution.starved.md`)

```markdown
---
id: doc://prompt/crucible/execution_starved@1
stem: crucible.execution.starved
bank: crucible
slug: execution_starved
version: 1
trust: draft
trigger:
  screens: ["run.execute.denial.budget_cascade"]
  predicate:
    domain: "policy.budget"
vars:
  - name: env
    type: string
    source: kernel.env
sections:
  stage_1_budget: 150
  stage_2_jail: 140
  stage_3_claims: 130
  stage_4_vault: 140
slice_max_tokens: 500
---

# ⚡ EXECUTION CRUCIBLE RESOLUTION PROTOCOL
Execution was intercepted by kernel boundary defenses (budget starvation, sandbox trap, or lease collision).
Follow this 4-stage resolution pipeline:

## section:stage_1_budget
Resolve call-tree budget starvation:
1. Run pre-flight inspection to locate the tightest child constraint:
   ```bash
   capcli inspect cap://<routine_name>
   ```
2. Child routines inherit bounds via `min()`. Adjust the parent routine's `@routine` declaration:
   `limits={"max_ops": parent_ops + sum(child_ops)}`

## section:stage_2_jail
Remediate sandbox network traps (Syscall 42):
Raw socket egress (`connect`) is blocked by seccomp-bpf.
Never import `requests`, `urllib`, or raw `fetch`.
Route traffic exclusively via imported catalog verbs:
```bash
capcli api catalog
```
Dispatch inside routines via `ctx.api.call("<provider>.<verb>", payload)`.

## section:stage_3_claims
Resolve contested lease collisions (`db.claims`):
If an exclusive entity lease is held by another session:
```bash
capcli sql "SELECT * FROM claims WHERE resource = :target" -p target="orders:ORD-1"
```
Do not poll in a tight while loop. Yield control back to sensory inbox:
```bash
capcli sys inbox pop
```

## section:stage_4_vault
Resolve missing vault credentials:
Passing API tokens via prompts or CLI arguments is blocked to prevent leaks.
Inject secrets through the Cockpit interface:
```bash
open http://127.0.0.1:4040/vault
```
Or import local environment variables in development:
```bash
capcli sys vault_import
```
```

---

### 5.8 Schema Evolution Campaign: 4-Phase Migration (`evolution.schema.drift.md`)

```markdown
---
id: doc://prompt/evolution/schema_drift@1
stem: evolution.schema.drift
bank: evolution
slug: schema_drift
version: 1
trust: draft
trigger:
  screens: ["rule.diff.success.populated"]
  predicate: {}
vars:
  - name: env
    type: string
    source: kernel.env
sections:
  stage_1_diff: 110
  stage_2_plan: 160
  stage_3_rehearse: 140
  stage_4_cutover: 120
slice_max_tokens: 500
---

# ⚡ ONLINE SCHEMA EVOLUTION PROTOCOL (4-PHASE MIGRATION)
`rule diff` detected structural drift between `schema.yaml` and live SQLite PRAGMAs.
Direct `ALTER TABLE` execution is denied. Structural mutations must follow the online migration pipeline:

## section:stage_1_diff
Inspect structural deltas:
```bash
capcli rule diff
```
Ensure changes avoid circular foreign key references (Gate 2 checks).

## section:stage_2_plan
Generate the deterministic 4-phase migration plan bundle:
```bash
capcli rule plan --name "<migration_slug>" -m "Migration rationale"
```
The kernel scaffolds:
1. **Expand:** Creates shadow tables and forward non-breaking columns.
2. **Backfill:** Generates bounded data copy routines.
3. **Contract:** Removes obsolete shadow structures.

## section:stage_3_rehearse
Rehearse migration phases against masked simulation snapshots:
```bash
capcli rule prove <migration_id> --env sim
```
Assert that table lock acquisition takes less than 20ms under simulation load.

## section:stage_4_cutover
Execute the atomic schema cutover:
```bash
capcli rule apply <migration_id> -m "Execute atomic table swap"
```
Shadow tables are atomically renamed within a single transaction.
```

---

### 5.9 Trust Promotion Campaign: Canary Ladder (`promotion.routine.passed.md`)

```markdown
---
id: doc://prompt/promotion/routine_passed@1
stem: promotion.routine.passed
bank: promotion
slug: routine_passed
version: 1
trust: draft
trigger:
  screens: ["routine.prove.success.passed"]
  predicate:
    trust: draft
vars:
  - name: env
    type: string
    source: kernel.env
sections:
  stage_1_enqueue: 120
  stage_2_canary: 150
  stage_3_pin: 130
slice_max_tokens: 500
---

# ⚡ ROUTINE TRUST PROMOTION PROTOCOL
Routine simulation proof succeeded with zero drift events and zero policy violations.
Promote code safely across the trust ladder (`draft -> reviewed -> pinned`).

## section:stage_1_enqueue
Do not promote draft routines directly to pinned production execution.
Enqueue the routine for reviewed trust:
```bash
capcli routine ship <routine_name> reviewed --queue
```

## section:stage_2_canary
Monitor the routine through its 1-hour production canary observation window:
```bash
capcli routine stats <routine_name>
```
If errors spike, the autonomous circuit breaker rolls back active pointers to the previous version.

## section:stage_3_pin
If canary metrics meet production thresholds (success rate > 99.5%), promote to pinned:
```bash
capcli routine ship <routine_name> pinned --reason "Canary passed: 200 runs with 0 errors"
```
*Note: Pinned execution requires Tier 1 hardened Linux namespaces.*
```

---

### 5.10 Wire Campaign: Catalog Ingestion & Egress Lockdown (`wire.catalog.empty.md`)

```markdown
---
id: doc://prompt/wire/catalog_empty@1
stem: wire.catalog.empty
bank: wire
slug: catalog_empty
version: 1
trust: draft
trigger:
  screens: ["api.catalog.success.empty"]
  predicate: {}
vars:
  - name: env
    type: string
    source: kernel.env
sections:
  stage_1_import: 140
  stage_2_record: 150
  stage_3_prove: 130
  stage_4_ship: 110
slice_max_tokens: 500
---

# ⚡ EXTERNAL WIRE CATALOG LOCKDOWN PROTOCOL
No external API catalogs are configured. Outbound HTTP requests from routines are blocked
at the socket layer until imported, proven, and registered.

## section:stage_1_import
Import an external OpenAPI endpoint into the local catalog:
```bash
capcli api import <provider> <path> <method> --spec <spec_url_or_file>
```
Example:
```bash
capcli api import stripe /v1/refunds POST --spec https://api.stripe.com/openapi.yaml
```

## section:stage_2_record
Record an idempotent live request to capture response schemas and create simulation cassettes:
```bash
capcli api record stripe.refunds.create -p charge_id="ch_test_123"
```
This writes fixtures into `apis/<provider>.cassette.jsonl`.

## section:stage_3_prove
Prove the API verb inside the simulation environment:
```bash
capcli api prove stripe.refunds.create --env sim
```
Verify that payload scrubbing and token bucket limits match provider contracts.

## section:stage_4_ship
Promote the API capability to reviewed trust:
```bash
capcli api ship stripe.refunds.create reviewed --reason "Enable refund automation"
```
```

---

### 5.11 Forensics Campaign: Audit Tamper Isolation (`forensics.audit.tampered.md`)

```markdown
---
id: doc://prompt/forensics/audit_tampered@1
stem: forensics.audit.tampered
bank: forensics
slug: audit_tampered
version: 1
trust: draft
trigger:
  screens: ["sys.doctor.warning.tamper"]
  predicate: {}
vars:
  - name: env
    type: string
    source: kernel.env
sections:
  stage_1_quarantine: 140
  stage_2_isolate: 150
  stage_3_attest: 130
slice_max_tokens: 500
---

# ⚡ TAMPER FORENSICS & QUARANTINE PROTOCOL
A broken SHA-256 hash link was detected in `_audit`.
The causal DAG detected ledger corruption. Corrupted blocks are quarantined to preserve operational uptime.

## section:stage_1_quarantine
Inspect the quarantined audit entries:
```bash
capcli sys doctor --quarantine
```
Locate the exact operation ID where `parent_hash != prev_hash`.

## section:stage_2_isolate
Verify that corrupted blocks have been isolated to `audit.quarantine.jsonl`.
Live database tables remain online; uncorrupted audit history remains queryable:
```bash
capcli sys audit query "SELECT * FROM _audit ORDER BY timestamp DESC LIMIT 10"
```

## section:stage_3_attest
Verify current state against the offsite S3 WORM ledger root:
```bash
capcli sys doctor --report
```
Reconcile root ledger hashes to ensure offsite backups reflect verified operations.
```

---

### 5.12 Human-in-the-Loop Campaign: Ping Ask Suspension (`hitl.ping_ask.suspended.md`)

```markdown
---
id: doc://prompt/hitl/ping_ask_suspended@1
stem: hitl.ping_ask.suspended
bank: hitl
slug: ping_ask_suspended
version: 1
trust: draft
trigger:
  screens: ["run.execute.suspended.ask"]
  predicate: {}
vars:
  - name: env
    type: string
    source: kernel.env
sections:
  stage_1_inspect: 130
  stage_2_resolve: 140
  stage_3_occ: 150
slice_max_tokens: 500
---

# ⚡ HUMAN-IN-THE-LOOP (PING ASK) RESOLUTION PROTOCOL
A routine executed `ctx.ping.ask`. Execution is parked awaiting human input.
State is protected by an Optimistic Concurrency Control (OCC) fence.

## section:stage_1_inspect
Enumerate pending inquiry cards:
```bash
capcli ping list --pending
```
Review the structured question, available options ($\le 5$), and timeout deadline.

## section:stage_2_resolve
Resolve the inquiry via CLI or provide the Cockpit URL to the human operator:
```bash
capcli ping resolve <ask_id> --choice approve
```
Cockpit Web UI: `http://127.0.0.1:4040/inquiries`

## section:stage_3_occ
Handle OCC state drift on resumption:
If underlying records were modified while awaiting human response, resumption trips an OCC conflict (`exit 2`).
Transaction rolls back cleanly. Re-invoke the routine from turn zero with fresh state:
```bash
capcli run <routine_name>
```
```

---

*(Continued in Part 3/3: The Complete 35+ Diagnostic Remedy Matrix across all 10 CLI nouns and the Rust Kernel Engine Implementation & Verification Suite)*


# Canonical Prompt Bank, Trigger & Progressive Disclosure Specification

`cans/artifacts/prompt/prompt-structure.md`  
*(Part 3/3)*

---

## 6. The Definitive Anatomy: Remedy vs. Campaign

Confusing a **Diagnostic Remedy** with a **Prompt Campaign** breaks autonomous harnesses:
* Giving a prompt campaign to an agent that missed a SQL `LIMIT` clause bloats context and causes over-engineering.
* Giving a one-line remedy to an agent facing an uninitialized blank world leaves it stranded without architectural direction.

### The Contrast Matrix

| Dimension | Diagnostic Remedy | Prompt Campaign (`doc://prompt/...`) |
|---|---|---|
| **Objective** | Fix and close a failed command | Open and guide a multi-turn architectural campaign |
| **Trigger Mechanism** | Direct non-zero exits (2, 3, 4, 5, 6) | State machine screen triggers in `_triggers.json` |
| **Token Budget** | $\le 40$ tokens (inlined in error diagnostic) | Sliced across turns ($\le 500$ tokens per section) |
| **Delivery Medium** | In-band via terminal `stdout`/`stderr` | Sliced via `capcli doc read <ptr> --section <id>` |
| **Lifecycle** | **Ephemeral:** Pruned after command succeeds | **Durable:** Governed markdown artifact in `banks/` |
| **Action Placement** | Top-loaded on **Line 1** (`ACTION: ...`) | Sequenced in progressive stages (`## section:stage_*`) |
| **State Authority** | Modifies no state (`state_modified: false`) | Drives state changes via ordinary CLI commands |

---

## 7. The Exhaustive 48-Condition Diagnostic Remedy Matrix

Every single refusal, denial, yield, and crash condition across all 10 CLI nouns possesses an exact, top-loaded Line 1 remedy:

```
[dev:tier_1]  ✗  exit {code} | ACTION: {command}
  FAIL  {domain}.{condition}
        {statement_or_culprit}
        ^^^^^^^^^^^^^^^^^^^^^^
        {diagnostic_explanation}

  audit_op: {op_id}
  state_modified: false
  layer: {layer}
  remedy: {remedy_text}
```

### 7.1 `run` Remedies (11 Conditions)

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R01 | `run.sql.denial.ast` | 2 | `policy.ast` | `unbounded` | `ACTION: capcli sql "<q> LIMIT 10" --dry-run` | `remedy: add LIMIT, or target specific primary key` |
| R02 | `run.sql.denial.authorizer` | 2 | `policy.authorizer` | `schema_mod` | `ACTION: capcli rule diff` | `remedy: direct DDL prohibited; modify schema.yaml` |
| R03 | `run.sql.denial.engine_busy` | 2 | `db.engine` | `timeout` | `ACTION: capcli sql "<q>" --retry-busy 3` | `remedy: transaction queue wait exceeded 5000ms; retry query` |
| R04 | `run.sql.refusal.missing_intent` | 3 | `compile` | `no_intent` | `ACTION: capcli sql "<q>" -m "<rationale>"` | `remedy: mutating operations require causal -m rationale` |
| R05 | `run.execute.denial.budget` | 2 | `policy.budget` | `exhausted` | `ACTION: capcli inspect cap://<name>` | `remedy: frame ceiling exceeded; increase max_ops in @routine` |
| R06 | `run.execute.denial.budget_cascade` | 2 | `policy.budget` | `starved` | `ACTION: capcli inspect cap://<name>` | `remedy: parent budget cannot fund worst-case child branch` |
| R07 | `run.execute.denial.network_jail` | 2 | `kernel.sandbox` | `syscall_42` | `ACTION: capcli search "<provider>"` | `remedy: raw socket connect trapped; use ctx.api.call` |
| R08 | `run.execute.refusal.missing_secret` | 3 | `policy.secrets` | `missing_key` | `ACTION: open http://127.0.0.1:4040/vault` | `remedy: credential not in vault; inject via Cockpit UI` |
| R09 | `run.execute.crash.poll_timeout` | 4 | `routine.runtime` | `timeout` | `ACTION: capcli inspect cap://<name>` | `remedy: poll_until ceiling exceeded 30s; bind webhook instead` |
| R10 | `run.execute.panic.secret_leak` | 5 | `kernel.panic` | `leak` | `ACTION: capcli sys doctor --boot-check` | `remedy: plaintext secret detected in stdout; zeroized buffers` |
| R11 | `run.execute.yield.quota` | 6 | `api.quota` | `rate_limit` | `ACTION: capcli sys inbox pop` | `remedy: task yielded; daemon will auto-resume at reset_at` |

---

### 7.2 `db` Remedies (5 Conditions)

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R12 | `db.lock.denial.claim_held` | 2 | `db.claims` | `held` | `ACTION: capcli sql "SELECT * FROM claims"` | `remedy: lease held by another session; yield or await TTL` |
| R13 | `db.lock.refusal.missing_reason` | 3 | `validation` | `missing_arg` | `ACTION: capcli db lock <ref> --reason "<why>"` | `remedy: exclusive lock leases mandate --reason flag` |
| R14 | `db.unlock.refusal.not_holder` | 3 | `policy.authorizer` | `unauthorized` | `ACTION: capcli sql "SELECT holder FROM claims"` | `remedy: acting agent ID does not own target lease` |
| R15 | `db.snapshot.denial.prod_draft` | 2 | `policy.trust` | `forbidden` | `ACTION: capcli env use sim` | `remedy: draft trust cannot snapshot prod; switch to sim` |
| R16 | `db.restore.denial.active_locks` | 2 | `db.claims` | `active_locks` | `ACTION: capcli sql "SELECT * FROM claims"` | `remedy: active business claims prevent state reversal` |

---

### 7.3 `routine` Remedies (6 Conditions)

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R17 | `routine.new.refusal.shape_violation` | 3 | `validation` | `bad_shape` | `ACTION: head -n 150 routines/<name>.py` | `remedy: routine exceeds limits: 150 LOC, 2000 tokens, 8 params` |
| R18 | `routine.prove.denial.policy` | 2 | `policy.authorizer` | `illegal_leaf` | `ACTION: capcli inspect cap://<name>` | `remedy: forbidden leaf: external API calls banned in db.txn` |
| R19 | `routine.ship.denial.trust` | 2 | `policy.trust` | `tier2_refusal` | `ACTION: capcli run <cap> --env sim` | `remedy: E045 pinned trust forbidden on Tier 2 macOS/Win` |
| R20 | `routine.ship.rollback.canary` | 0 | `policy.authorizer` | `rolled_back` | `ACTION: capcli routine prove <name> --env sim` | `remedy: canary telemetry spike triggered auto-rollback` |
| R21 | `routine.rollback.denial.depth` | 2 | `policy.authorizer` | `depth_limit` | `ACTION: capcli routine stats <name>` | `remedy: target version exceeds max rollback depth of 5` |
| R22 | `routine.retire.denial.active_deps` | 2 | `policy.authorizer` | `deps_exist` | `ACTION: capcli inspect cap://<name>` | `remedy: active routines or crons depend on this capability` |

---

### 7.4 `api` Remedies (4 Conditions)

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R23 | `api.sync.denial.rate` | 2 | `api.quota` | `rate_limit` | `ACTION: capcli api diff <provider>` | `remedy: spec sync within 24h cooldown; inspect local diff` |
| R24 | `api.sync.refusal.missing_url` | 3 | `missing_param` | `missing_arg` | `ACTION: capcli api import <p> <path> <m> --spec <u>` | `remedy: upstream OpenAPI spec URL or file path required` |
| R25 | `api.prove.denial.sim_gap` | 2 | `policy.authorizer` | `sim_gap` | `ACTION: capcli api record <verb> -p k=v` | `remedy: missing mock fixture in sim; record live cassette` |
| R26 | `api.prove.crash.runtime` | 4 | `routine.runtime` | `exception` | `ACTION: capcli api diff <provider>` | `remedy: upstream API payload violates catalog schema types` |

---

### 7.5 `bind` Remedies (5 Conditions)

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R27 | `bind.cron.denial.interval` | 2 | `policy.authorizer` | `interval_low` | `ACTION: capcli bind cron <n> <c> "*/5 * * * *"` | `remedy: cron schedules cannot run faster than 5-minute cap` |
| R28 | `bind.webhook.denial.unsigned` | 2 | `policy.authorizer` | `unsigned` | `ACTION: capcli bind webhook <n> <p> <e> <c> --driver <s>` | `remedy: unsigned webhooks rejected; configure driver HMAC` |
| R29 | `bind.webhook.denial.payload_size` | 2 | `policy.authorizer` | `too_large` | `ACTION: capcli inspect bind://<name>` | `remedy: hook payload exceeds 64KB memory buffer ceiling` |
| R30 | `bind.webhook.refusal.missing_ingress` | 3 | `compile` | `no_ingress` | `ACTION: capcli bind webhook <n> <p> <e> <c> --tunnel` | `remedy: missing public ingress URL; supply --tunnel for dev` |
| R31 | `bind.endpoint.denial.trust` | 2 | `policy.trust` | `unpinned` | `ACTION: capcli routine ship <r> pinned --reason "<w>"` | `remedy: public HTTP/MCP endpoints require pinned trust` |

---

### 7.6 `ping` Remedies (4 Conditions)

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R32 | `ping.notify.denial.quiet_hours` | 2 | `policy.authorizer` | `quiet_hours` | `ACTION: capcli sys inbox pop` | `remedy: notification blocked between 22:00 and 07:00` |
| R33 | `ping.ask.denial.options_cap` | 2 | `policy.authorizer` | `cap_exceeded` | `ACTION: capcli ping ask <p> "<q>" --options "a,b"` | `remedy: ctx.ping.ask exceeds maximum of 5 structured choices` |
| R34 | `ping.resolve.denial.occ_conflict` | 2 | `db.engine` | `stale_state` | `ACTION: capcli run <routine_name>` | `remedy: OCC fence violated during suspension; re-run from turn 0` |
| R35 | `ping.resolve.denial.expired` | 2 | `policy.notify` | `expired` | `ACTION: capcli ping expire <ask_id>` | `remedy: inquiry timeout elapsed; fail-closed without mutation` |

---

### 7.7 `rule` Remedies (3 Conditions)

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R36 | `rule.validate.refusal.syntax` | 3 | `compile` | `bad_syntax` | `ACTION: capcli rule validate` | `remedy: Gate 1 YAML syntax failure; check schema indentation` |
| R37 | `rule.validate.refusal.semantics` | 3 | `compile` | `circular_ref` | `ACTION: capcli rule validate` | `remedy: Gate 2 circular dependency detected in table FK graph` |
| R38 | `rule.apply.refusal.lockfile` | 3 | `lockfile_mismatch`| `drift` | `ACTION: capcli rule validate` | `remedy: lockfile root hash mismatch; recompile in dev` |

---

### 7.8 `env` Remedies (4 Conditions)

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R39 | `env.new.denial.cap` | 2 | `policy.authorizer` | `cap_exceeded` | `ACTION: capcli env list` | `remedy: maximum 5 environments reached; remove stale worktrees` |
| R40 | `env.new.refusal.bundle_too_large` | 3 | `policy.template` | `size_overflow`| `ACTION: capcli env list` | `remedy: template bundle exceeds 5MB ceiling; remove seed dumps` |
| R41 | `env.remove.denial.crypto_sig` | 2 | `policy.authorizer` | `confirmation` | `ACTION: open http://127.0.0.1:4040/admin` | `remedy: production teardown requires hardware challenge signature` |
| R42 | `env.merge.refusal.plan_conflict` | 3 | `compile` | `conflict` | `ACTION: git pull origin main` | `remedy: target schema migration plan conflict; rebase worktree` |

---

### 7.9 `sys` Remedies (5 Conditions)

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R43 | `sys.doctor.refusal.boot` | 3 | `compile` | `missing_dep` | `ACTION: capcli sys doctor` | `remedy: host missing python3.11 or sandbox provider (bwrap)` |
| R44 | `sys.register.denial.cap` | 2 | `policy.authorizer` | `cap_exceeded` | `ACTION: capcli sys agents` | `remedy: maximum registered agents reached; revoke idle tokens` |
| R45 | `sys.doctor.warning.clock_drift` | 0 | `host.ntp` | `clock_skew` | `ACTION: sudo chronyd -q || sudo ntpdate pool.ntp.org`| `remedy: host clock skewed >500ms; monotonic fallback active` |
| R46 | `sys.doctor.alarm.thrashing` | 2 | `agent.thrashing` | `looping` | `ACTION: capcli sys audit trace latest --explain` | `remedy: 20 sustained denials in 5m; harness throttled` |
| R47 | `sys.exec.crash.runtime` | 5 | `kernel.panic` | `crash` | `ACTION: export CAPCLI_RECOVERY=1 && capcli sys doctor` | `remedy: unrecoverable media failure; boot emergency recovery` |

---

### 7.10 `doc` Remedy (1 Condition)

| ID | Screen ID | Exit | Domain | Condition | Line 1 ACTION | Diagnostic Needle / Remedy Text |
|---|---|---|---|---|---|---|
| R48 | `doc.read.success.sliced` | 0 | `doc.slice` | `sliced` | `ACTION: capcli doc read <ptr> --section <next>` | `remedy: document rendered in bounded 100-token slice; advance section` |

---

## 8. Rust Engine Implementation

The kernel loads `.md` prompt artifacts directly, parses their YAML frontmatter with `serde_yaml`, and extracts individual section slices deterministically.

```rust
// crates/capcli-cli/src/prompt_engine.rs

use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Serialize)]
pub struct PromptFrontmatter {
    pub id: String,
    pub stem: String,
    pub bank: String,
    pub slug: String,
    pub version: u32,
    pub trust: String,
    pub trigger: PromptTrigger,
    pub vars: Vec<PromptVar>,
    pub sections: HashMap<String, usize>,
    pub slice_max_tokens: usize,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct PromptTrigger {
    pub screens: Vec<String>,
    pub predicate: HashMap<String, serde_json::Value>,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct PromptVar {
    pub name: String,
    pub r#type: String,
    pub source: String,
}

pub struct PromptEngine {
    banks_root: PathBuf,
}

impl PromptEngine {
    pub fn new(banks_root: PathBuf) -> Self {
        Self { banks_root }
    }

    /// Read and parse frontmatter and body from a single .md bank file
    pub fn load_prompt(&self, bank: &str, slug: &str, condition: &str) -> (PromptFrontmatter, String) {
        let file_name = format!("{}.{}.empty.md", bank, slug);
        let path = self.banks_root.join(bank).join(file_name);
        let raw = fs::read_to_string(&path)
            .unwrap_or_else(|_| panic!("Failed to read prompt file: {}", path.display()));

        let parts: Vec<&str> = raw.splitn(3, "---").collect();
        assert!(parts.len() >= 3, "Invalid YAML frontmatter in {}", path.display());

        let frontmatter: PromptFrontmatter = serde_yaml::from_str(parts[1])
            .unwrap_or_else(|e| panic!("Frontmatter parse failure in {}: {}", path.display(), e));
        let body = parts[2].to_string();

        (frontmatter, body)
    }

    /// Extract an isolated section slice, performing kernel variable substitution
    pub fn read_section(
        &self,
        bank: &str,
        slug: &str,
        condition: &str,
        section_id: &str,
        state_vars: &HashMap<String, String>,
    ) -> Result<String, i32> {
        let (frontmatter, body) = self.load_prompt(bank, slug, condition);
        let section_header = format!("## section:{}", section_id);

        let section_block = body
            .split("## section:")
            .find(|chunk| chunk.starts_with(section_id))
            .ok_or(3)?; // Exit 3: section missing

        // Strip the section ID line
        let content = section_block.strip_prefix(section_id).unwrap_or(section_block).trim();

        // Perform deterministic variable substitution
        let mut rendered = content.to_string();
        for var_def in &frontmatter.vars {
            let token = format!("{{{{{}}}}}", var_def.name);
            if let Some(val) = state_vars.get(&var_def.name) {
                rendered = rendered.replace(&token, val);
            } else {
                return Err(3); // Exit 3: unresolvable kernel variable
            }
        }

        // Enforce token budget ceiling
        let token_estimate = rendered.len() / 4;
        let limit = *frontmatter.sections.get(section_id).unwrap_or(&500);
        assert!(token_estimate <= limit, "Section {} breached token ceiling", section_id);

        Ok(rendered)
    }
}
```

---

## 9. Verification & Golden-File Test Runner

The Rust test runner asserts every constraint across all prompt bank `.md` files:

```rust
// crates/capcli-cli/tests/test_prompt_fixtures.rs

use std::fs;
use glob::glob;

#[test]
fn assert_prompt_bank_invariants() {
    let prompt_files = glob("cans/artifacts/prompt/banks/**/*.md").unwrap();
    let mut file_count = 0;

    let banned_phrases = [
        "As an AI",
        "Please note that",
        "It is recommended to",
        "Feel free to",
        "Let me know if you need",
        "You could consider",
    ];

    for entry in prompt_files {
        let path = entry.unwrap();
        let raw = fs::read_to_string(&path).unwrap();

        // 1. Mandatory Structured YAML Frontmatter
        assert!(raw.starts_with("---\n"), "File {} must begin with YAML frontmatter", path.display());
        let parts: Vec<&str> = raw.splitn(3, "---").collect();
        assert_eq!(parts.len(), 3, "File {} missing terminating frontmatter marker", path.display());

        let frontmatter: serde_yaml::Value = serde_yaml::from_str(parts[1])
            .unwrap_or_else(|e| panic!("Frontmatter parse failure in {}: {}", path.display(), e));

        // 2. Frontmatter ID Invariants
        let id = frontmatter["id"].as_str().expect("id must be string");
        assert!(id.starts_with("doc://prompt/"), "ID {} must use doc://prompt/ URP scheme", id);

        // 3. Section Token Budget Enforcement (<=500 tokens)
        let body = parts[2];
        for section in body.split("## section:") {
            if section.trim().is_empty() { continue; }
            let est_tokens = section.len() / 4;
            assert!(
                est_tokens <= 500,
                "Section in {} exceeds 500 token ceiling (estimated: {})",
                path.display(),
                est_tokens
            );
        }

        // 4. Conversational Boilerplate Screening
        for banned in &banned_phrases {
            assert!(
                !raw.contains(banned),
                "Prompt {} contains forbidden conversational filler: '{}'",
                path.display(),
                banned
            );
        }

        file_count += 1;
    }

    assert!(file_count >= 8, "All 8 canonical prompt campaigns must be present");
}
```

---

## 10. Audit Lineage & Proof of Work

Serving prompts and remedies never alters state, but it is always auditable:

```sql
SELECT op_id, timestamp, level, prompt_ptr, tokens, state_modified
FROM _audit
WHERE domain = 'prompt'
ORDER BY timestamp DESC;
```

* **`state_modified: false`** is guaranteed for all L1 trailers, L2 inspect envelopes, and L3 slices.
* **`tokens`** tracks the exact slice spend against the session fuel budget.
* **Audit Op Hash Link:** When an agent resolves a prompt campaign, it must seal its mission by verifying its work against the ledger:
  ```bash
  capcli sys verify <audit_op>
  ```
  Unverified natural-language claims of task completion are discarded by autonomous harnesses. Deterministic execution requires cryptographic proof.
