# Canonical Wireframe, State Machine & Flow Engine Specification

---

## 1. Directory Tree & Architecture

The wireframe layer serves a dual purpose: an **interactive edgeless canvas** for humans and harnesses, and a **deterministic golden-file test fixture suite** for the Rust kernel.

Flow graphs, journey definitions, and multi-branch transition metadata are codified into `flows.json`. Individual screen fixtures remain atomic, stateless, and congruent with runtime compiler and authorizer output.

```
cans/artifacts/wireframe/
  manifest.json
  flows.json
  _states.json
  wireframe.html
  screens/
    run/
      execute/
      sql/
      overview/
      search/
      inspect/
    db/
      lock/
      unlock/
      schema/
      snapshot/
      restore/
      dump/
    routine/
      new/
      prove/
      ship/
      pending/
      sweep/
      stats/
      rollback/
      retire/
    api/
      sync/
      diff/
      catalog/
      prove/
      ship/
      stats/
      retire/
      rollback/
    bind/
      cron/
      webhook/
      endpoint/
      export/
      list/
      inspect/
      pause/
      resume/
      remove/
      keys/
    ping/
      notify/
      ask/
      list/
      resolve/
      expire/
    rule/
      show/
      diff/
      apply/
      validate/
    env/
      new/
      use/
      list/
      inspect/
      doctor/
      merge/
      remove/
    sys/
      help/
      inbox/
      tail/
      trace/
      query/
      replay/
      register/
      agents/
      revoke/
      vault_set/
      vault_import/
      doctor/
      backup/
      recover/
      exec/
      serve/
    doc/
      read/
      outline/
      inspect/
```

### 1.1 Structural Invariants
* **Active Nouns:** Exactly 10 CLI nouns (`run`, `db`, `routine`, `api`, `bind`, `ping`, `rule`, `env`, `sys`, `doc`).
* **Pairing Law:** Every `.json` fixture has an identical `.txt` companion in the same folder. No orphan files. No empty directories.
* **Depth Ceiling:** File paths relative to `screens/` must remain exactly 3 path components: `{noun}/{verb}/{filename}`.
* **Sibling Invariants:** Min 3, max 16 verb directories per noun branch node.
* **Naming Law:** Strict 4-segment token syntax:
  ```
  {noun}.{verb}.{state}.{condition}.{json|txt}
  ```

---

## 2. Core Manifests & States

### 2.1 `manifest.json`

Canonical file: `manifest.json` (same directory). It owns the noun list, the state axes, and the output contract; this document points at it and does not reproduce it.

The domain registry lives only in `_states.json`. This manifest carries no copy of it; consumers read `_states.json` directly.

### 2.2 `_states.json`

Canonical file: `_states.json` (same directory). It is the single home of the state taxonomy: exit code → label, exit → legal domains, exit → required diagnostic fields. Not reproduced here by design.

The law in one paragraph: six states, one per exit — `success` 0, `denial` 2, `refusal` 3, `crash` 4, `panic` 5, `yield` 6 (cans/physics.md#Exit-code-law). The screen-ID state slot takes exactly these labels; severity and lifecycle words (`warning`, `tamper`, `suspended`, `rolled_back`) live in the condition slot. A domain determines its exit: `api.quota` alone is dual-registered (exit 2 Critical, exit 6 Background). Exit 6 covers both quota yields and `ping.ask` frame suspensions (cans/action.md suspension contract).

---

## 3. Decoupled Flow & Journey Engine (`flows.json`)

Canonical file: `flows.json` (same directory). It owns journeys and screen-to-screen routing; this document points at it and does not reproduce it.

Every screen ID referenced by a flow must exist as a fixture pair under `screens/` — the validator enforces closure. Flow prose in §5 quotes individual screens for walkthroughs; the routing itself lives only in `flows.json`.

---

## 4. Screen Inventory

The fixture pairs under `screens/` are the inventory. State and domain
legality lives in `_states.json`; routing lives in `flows.json`. No
screen table exists in this document: a hand-maintained copy of the
fixture tree is a second inventory, and the two desync.

Validator closure: every fixture pair is a legal screen (state slot,
exit, and domain agree with `_states.json`), every screen ID named in
`flows.json` exists as a fixture pair, and every fixture pair follows
the pairing and naming law in §1.1. Counts come from disk at validation
time and appear in no document.

---

## 5. Canonical Screen Fixtures

Every terminal transcript follows strict typographic rules:
1. **Header Badge:** Standardized `[{env}:{tier}]` runtime context prefix.
2. **Visual Spans:** Source SQL or parameters underlined with carets (`^^^^`) directly pinpointing violations.
3. **Indented Blocks:** Two-space hierarchical indentation; clean label columns.
4. **Dividers:** Horizontal character lines (`─`) for separation. No random vertical pipe borders.
5. **Machine/Human Duality:** Clean human presentation by default; JSON structure strictly matches `--json`.

---

### 5.1 AST Blast-Radius Denial (`screens/run/sql/run.sql.denial.ast.txt`)

```text
[dev:tier_1]  ✗  exit 2

  FAIL  policy.query.update_delete.require_limit
        UPDATE orders SET status = 'shipped' WHERE status = 'processing'
                                                                   ^^^^^^
        No LIMIT clause. Blast radius unbounded.

  audit_op: op_9f2e
  state_modified: false
  layer: AST
  measured: matches potentially 847 rows (cap: 100)
  remedy: add LIMIT, or target specific primary key
```

---

### 5.2 Causal DAG Tree Walk (`screens/sys/trace/sys.trace.success.populated.txt`)

```text
[dev:tier_1]  Causal DAG Trace (op_9f2e)

  ses_a992f  session.start        "fulfill urgent pending orders"
  └── op_9f2c  routine.dispatch_order@4
        ├── op_9f2d  db.query (orders)         ✓ [allowed]  12ms
        ├── op_9f2e  api.call (fedex.ship)     ✓ [allowed]  340ms
        │     └── tracking: 794644790133
        └── op_9f2f  db.execute (orders)       ✓ [allowed]  18ms
              └── status = 'shipped' (1 row)

  Root Intent: "fulfill urgent pending orders"
  Authority:   user:alice (via agt_7f3k)
  Integrity:   valid hash link (chain verified)
```

---

### 5.3 YAML Trust Receipt (`screens/sys/doctor/sys.doctor.success.report.txt`)

```text
[prod:tier_1]  capcli 0.4.2

trust_receipt:
  status:            nominal
  host_tier:         tier_1 (hardened Linux namespaces)
  workspace:         envs/prod/workspace.db
  ledger_root_hash:  sha256:7f9a1b2c4d8e001fa882bc19488a09b2e4f019c
  audited_events:    14290 committed to _audit
  policy_denials:    18 (intercepted pre-execution; state untouched)
  unaudited_writes:  0
  secret_leaks:      0
  pinned_routines:   32
  active_triggers:   4 crons, 3 webhooks, 1 endpoint
  deployment:        headless_daemon (systemd Linux)
```

---

### 5.4 Pre-Flight Routine Inspection Envelope (`screens/run/inspect/run.inspect.success.routine.txt`)

```text
[dev:tier_1]  capcli inspect cap://dispatch_order@4

  trust:       pinned
  runtime:     typescript (bun)
  params:      order_id: string, carrier: string
  description: "Dispatch paid order to carrier and update status"

  limits:      8 ops · 15s · 500 result tokens

  manifest:
    1. db.query    orders (read)
    2. api.call    logistics.shipments.create
    3. db.execute  orders (write)

  budget_status:
    can_invoke_now:             true
    session_ops_remaining:      488
    session_duration_remaining: 555000ms
    session_fuel_remaining:     80400
    session_egress_remaining:   4181824 bytes
    session_rate_remaining:     287
    tightest_constraint:        null

  composition:
    max_nesting_depth:   5
    budget_inheritance:  min
    child_routines:      []

  stats:
    total_runs:    214
    success_rate:  99.1%
    p50_duration:  340ms
    p95_duration:  890ms
    last_run_at:   2m ago
```

---

### 5.5 Dry-Run Schema Impact Plan (`screens/run/sql/run.sql.success.dry_run.txt`)

```text
[dev:tier_1]  dry-run  ✓

  statement:      ALTER TABLE orders ADD COLUMN priority integer DEFAULT 0
  ast_check:      pass
  authorizer:     pass (alter on orders allowed in dev)
  intent:         declared ("add priority flag for rush shipping")
  schema_impact:  +1 column (priority)
  estimated_rows: 4281
  blast_radius:   schema-only (non-destructive)

  state_modified: false
  note:           no execution occurred
```

---

### 5.6 Agent Thrashing Denial (`screens/sys/doctor/sys.doctor.denial.thrashing.txt`)

```text
[dev:tier_1]  ⚠  agent.thrashing

  agent:           agt_7f3k
  denials_last_5m: 22
  rule_hit:        policy.query.update_delete.require_limit
  target:          db://orders
  harness_status:  stuck in repetitive denial loop

  state_modified:  false
  layer:           governance
  remedy:          harness execution throttled; escalate to human or inspect remedy payload
```

---

### 5.7 Missing Vault Secret with Cockpit URL (`screens/run/execute/run.execute.refusal.missing_secret.txt`)

```text
[dev:tier_1]  ✗  exit 3

  FAIL  policy.secrets.missing
        capability: cap://stripe.refund_charge
        secret_ref: vault://stripe_secret

        Credential 'stripe_secret' not found in vault.
        Direct CLI parameter injection is banned to prevent prompt leakage.

  state_modified: false
  layer: vault
  remedy: prompt human supervisor to inject credential via Cockpit (http://127.0.0.1:4040/vault)
```

---

### 5.8 Network Jail Syscall 42 Trapping (`screens/run/execute/run.execute.denial.network_jail.txt`)

```text
[dev:tier_1]  ✗  exit 2

  FAIL  kernel.network.jail
        syscall 42 (connect) trapped by seccomp-bpf
        target: 10.0.0.5:5432
        caller: routines/sneaky_exfil.py

        Raw network egress prohibited from guest sandboxes.

  state_modified: false
  layer: sandbox
  remedy: use ctx.api.call with an activated catalog verb
```

---

### 5.9 Quota Yield Frame Suspension (`screens/run/execute/run.execute.yield.quota.txt`)

```text
[prod:tier_1]  ✗  exit 6

  YIELD  policy.api.quota_exhausted
         routine broadcast_newsletter@2 (frame_018)
         provider: threads
         verb:     threads.create_media_post

  state_modified:  false
  layer:           quota
  tokens_left:     0 / 50 (24h window)
  reset_at:        18:00:00 UTC (in 4h 12m)
  suspended_frame: task_99a8b1
  remedy:          task safely yielded; daemon will auto-resume at reset_at
```

---

### 5.11 NTP Clock Drift Diagnostic Warning (`screens/sys/doctor/sys.doctor.success.clock_drift.txt`)

The rule (cans/physics.md): clock delta vs NTP > 500ms emits a diagnostic warning on an exit-0 screen — causal ordering and lease claims bind to CLOCK_MONOTONIC and SQLite sequence IDs, so drift degrades audit timestamps only and never refuses execution.

```text
[dev:tier_1]  ✓  exit 0

  ⚠  clock drift warning: host delta vs NTP is 840ms (warning threshold: 500ms)
         causal ordering unaffected: CLOCK_MONOTONIC + SQLite sequence IDs
         lease claims and causal DAG bind to monotonic time; wall-clock drift degrades audit timestamps only

  host:            ws-07 (chronyd reachable, not yet synced)
  state_modified: false
  remedy:          synchronize host system clock via 'chronyd' or 'ntpdate' when convenient; execution is not blocked
```

---

### 5.12 Progressive Disclosure Doc Reading (`screens/doc/read/doc.read.success.sliced.txt`)

```text
[dev:tier_1]  doc://refund-policy (section 3)

  outline_node: 3. Stripe integration notes
  tokens:       84 (cap: 100)
  has_more:     false

  ────────────────────────────────────────────────────────────────────────────
  Outbound refunds must include `charge_id` and idempotent client request UUID.
  Never refund a charge older than 120 days via automated routines; delegate
  to human supervisor via `ctx.ping.ask`.
```

---

### 5.13 Minimalist Root Help Stub (`screens/sys/help/sys.help.success.stub.txt`)

```text
capcli 0.4.2 — compiled execution firewall for AI agents

Usage: capcli <noun> <verb> [target] [flags]

Capabilities are discovered dynamically, not listed in static help.
  Find actions:    capcli search <query>
  Pre-flight:      capcli inspect <urp>
  System status:   capcli sys doctor
```

---

## 6. Fixture Schema & Rust Test Runner Contract

### 6.1 Screen Fixture Schema (`screens/run/sql/run.sql.denial.ast.json`)

```json
{
  "$schema": "wireframe/v2",
  "screen_id": "run.sql.denial.ast",
  "noun": "run",
  "verb": "sql",
  "target": "db://orders",
  "command": "capcli sql \"UPDATE orders SET status = 'shipped' WHERE status = 'processing'\" -m \"batch ship\"",
  "state": {
    "exit_code": 2,
    "domain": "policy.ast",
    "trust": "draft",
    "env": "dev",
    "tier": "tier_1",
    "state_modified": false,
    "data_shape": null
  },
  "diagnostic": {
    "domain": "policy.ast",
    "culprit": "No LIMIT clause. Blast radius unbounded.",
    "remedy": "add LIMIT, or target specific primary key",
    "layer": "AST",
    "measured": "matches potentially 847 rows (cap: 100)"
  },
  "txt_pair": "screens/run/sql/run.sql.denial.ast.txt",
  "txt_sha256": null,
  "test_assertions": {
    "exit_code": 2,
    "state_modified": false,
    "stdout_contains": [
      "[dev:tier_1]  ✗  exit 2",
      "FAIL  policy.query.update_delete.require_limit",
      "No LIMIT clause. Blast radius unbounded.",
      "state_modified: false",
      "layer: AST",
      "remedy: add LIMIT, or target specific primary key"
    ],
    "stdout_not_contains": [
      "--force",
      "SyntaxError",
      "panic"
    ],
    "stderr_empty": true,
    "json_keys_required": ["domain", "culprit", "remedy", "state_modified", "layer"],
    "json_field_values": {
      "state_modified": false,
      "domain": "policy.ast"
    }
  }
}
```

### 6.1.1 Trailer Slot

`output_contract.trailer` in `manifest.json` is the output contract's
only producer-facing slot. A producer hands the wireframe finished
content; the wireframe renders it and carries no producer facts — no
campaign, bank, trigger, predicate, pointer scheme, token budget, or
serving rule appears in a wireframe file, fixture, or runner check.

- Human output: one optional final line, `trailer: <string>`.
- JSON output: one optional additive envelope key, `next_action`, whose
  value is an object.
- The wireframe validates type (string / object) and position. It never
  parses, resolves, or interprets the content. Human and machine parity
  of the content is a producer obligation; each rendering is verbatim.
- Absent is the default. A screen with no trailer renders exactly as it
  renders without the slot. The slot never reorders, rewrites, or
  suppresses host-screen output, and it leaves exit code and
  `state_modified` unchanged.

One optional top-level block on a screen fixture pair carries a trailer:

```json
"trailer": {
  "human": "<producer-supplied string>",
  "json": { }
}
```

The `.txt` pair renders `trailer: <human>` as its final line, and
`test_assertions.stdout_contains` includes that exact line. Producer
keys live inside the opaque `json` object and are invisible to the
runner. A fixture gains a `trailer` block only when a producer hands
the runner one; the wireframe never originates trailer content, and no
producer inventory exists in this directory.

### 6.2 Rust Integration Test Runner

```rust
// crates/capcli-cli/tests/e2e/test_wireframe_fixtures.rs

use std::fs;
use std::path::Path;
use glob::glob;
use serde::Deserialize;

#[derive(Deserialize)]
struct TestAssertions {
    exit_code: i32,
    state_modified: bool,
    stdout_contains: Vec<String>,
    #[serde(default)]
    stdout_not_contains: Vec<String>,
    stderr_empty: bool,
}

#[derive(Deserialize)]
struct WireframeFixture {
    screen_id: String,
    command: String,
    test_assertions: TestAssertions,
    txt_pair: String,
}

#[test]
fn execute_wireframe_golden_tests() {
    let root = Path::new("cans/artifacts/wireframe/screens");
    
    for entry in glob(&format!("{}/**/*.json", root.display())).unwrap() {
        let json_path = entry.unwrap();
        let content = fs::read_to_string(&json_path).unwrap();
        let fixture: WireframeFixture = serde_json::from_str(&content).unwrap();

        // 1. Assert companion .txt file exists
        let txt_path = json_path.with_extension("txt");
        assert!(txt_path.exists(), "Missing TXT pairing for {}", json_path.display());

        // 2. Assert TXT has zero raw table pipe characters
        let txt_content = fs::read_to_string(&txt_path).unwrap();
        assert!(!txt_content.contains('|'), "Pipe character | forbidden in {}", txt_path.display());

        // 3. Dispatch CLI harness command
        let output = capcli_test_exec(&fixture.command);

        // 4. Assert exit code and strict rollback invariant
        assert_eq!(output.exit_code, fixture.test_assertions.exit_code, "Exit mismatch at {}", fixture.screen_id);
        assert_eq!(output.state_modified, fixture.test_assertions.state_modified, "State modified invariant failed at {}", fixture.screen_id);

        // 5. Assert atomic output needles
        for needle in &fixture.test_assertions.stdout_contains {
            assert!(output.stdout.contains(needle), "{}: Missing expected output needle '{}'", fixture.screen_id, needle);
        }
        for banned in &fixture.test_assertions.stdout_not_contains {
            assert!(!output.stdout.contains(banned), "{}: Output contains banned token '{}'", fixture.screen_id, banned);
        }

        // Global negative: the parser-banned flags (cans/interface.md#Refusals)
        // appear in no screen's output. Asserted once here, for every fixture;
        // fixtures carry only screen-specific negatives.
        for banned in ["--force", "--override-budget", "--force-prod", "--verbose"] {
            assert!(!output.stdout.contains(banned), "{}: Output contains banned token '{}'", fixture.screen_id, banned);
        }

        if fixture.test_assertions.stderr_empty {
            assert!(output.stderr.is_empty(), "{}: Expected empty stderr, received: {}", fixture.screen_id, output.stderr);
        }
    }
}
```

Trailer checks, applied by the runner in §6.2 to every fixture:

a. **Type.** A `trailer` block carries exactly `human` (string) and
   `json` (object). Any other top-level key fails.
b. **Position.** The human trailer is the final line of the `.txt`
   pair; the machine trailer is an additive envelope key. Every other
   key, value, exit code, and `state_modified` matches the
   trailer-free rendering.
c. **State neutrality.** For every trailer-carrying fixture, a twin
   assertion runs the same command with no trailer supplied: output is
   identical except the trailer line/key is absent.
d. **Opacity.** The runner performs no lookup against trailer content:
   no registry resolution, no substring scan against producer files, no
   length budget. Content correctness is tested in the producer's own
   suite, at the producer's home.
e. **Negative space.** Every fixture without a `trailer` block asserts
   `stdout_not_contains: ["trailer:", "next_action"]`.

---

## 7. Edgeless Playable Canvas Implementation (`wireframe.html`)

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>capcli State Machine & Wireframe Engine</title>
<style>
  :root {
    --bg: #0d1117; --panel: #161b22; --border: #30363d;
    --text: #c9d1d9; --green: #3fb950; --red: #f85149;
    --yellow: #d29922; --purple: #a371f7; --blue: #58a6ff;
  }
  body { margin: 0; padding: 0; background: var(--bg); color: var(--text); font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; overflow: hidden; display: flex; height: 100vh; }
  #canvas-container { flex: 1; height: 100%; position: relative; cursor: grab; }
  #canvas-container:active { cursor: grabbing; }
  svg { width: 100%; height: 100%; }
  #hud { position: absolute; top: 16px; left: 16px; display: flex; gap: 8px; z-index: 10; flex-wrap: wrap; max-width: 60%; }
  .hud-btn { background: var(--panel); border: 1px solid var(--border); color: var(--text); padding: 8px 12px; cursor: pointer; border-radius: 4px; font-family: monospace; font-size: 11px; }
  .hud-btn:hover { border-color: var(--blue); color: #fff; }
  #terminal-panel { width: 620px; height: 100%; background: var(--panel); border-left: 1px solid var(--border); display: flex; flex-direction: column; }
  #terminal-header { padding: 12px 16px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
  #terminal-body { padding: 16px; flex: 1; overflow-y: auto; white-space: pre-wrap; font-size: 12px; line-height: 1.5; color: #c9d1d9; }
  #terminal-actions { padding: 12px 16px; border-top: 1px solid var(--border); display: flex; gap: 8px; flex-wrap: wrap; }
  .action-btn { background: #21262d; border: 1px solid var(--border); color: #fff; padding: 6px 10px; cursor: pointer; border-radius: 4px; font-size: 11px; font-family: monospace; }
  .action-btn:hover { border-color: var(--green); }
  .node rect { stroke-width: 2px; rx: 6px; cursor: pointer; }
  .node text { font-size: 11px; fill: var(--text); pointer-events: none; font-family: monospace; }
  .edge { stroke: var(--border); stroke-width: 2px; marker-end: url(#arrow); fill: none; }
  .edge.denial { stroke: var(--red); stroke-dasharray: 4; }
  .edge.yield { stroke: var(--yellow); stroke-dasharray: 6; }
</style>
</head>
<body>

<div id="canvas-container">
  <div id="hud">
    <button class="hud-btn" onclick="focusJourney('journey_human_onboarding')">1. Human Onboarding (S0-S10)</button>
    <button class="hud-btn" onclick="focusJourney('journey_harness_onboarding')">2. Harness Onboarding (H0-H7)</button>
    <button class="hud-btn" onclick="focusJourney('journey_execution_crucible')">3. Execution Crucible</button>
    <button class="hud-btn" onclick="focusJourney('journey_trust_promotion')">4. Trust Ladder</button>
    <button class="hud-btn" onclick="focusJourney('journey_quota_preemption')">5. Quota Yield/Resume</button>
    <button class="hud-btn" onclick="focusJourney('journey_schema_evolution')">6. DDL Evolution</button>
    <button class="hud-btn" onclick="focusJourney('journey_tamper_forensics')">7. Forensics & Panic</button>
    <button class="hud-btn" onclick="focusJourney('journey_human_in_the_loop')">8. Ask & Resolution</button>
  </div>
  <svg id="viewport">
    <defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#30363d" />
      </marker>
    </defs>
    <g id="scene"></g>
  </svg>
</div>

<div id="terminal-panel">
  <div id="terminal-header">
    <span id="screen-id-display" style="font-weight: 600;">select a state node</span>
    <span id="exit-badge"></span>
  </div>
  <div id="terminal-body">Click any node on the canvas to inspect real CLI diagnostic output...</div>
  <div id="terminal-actions"></div>
</div>

<script>
let transform = { x: 0, y: 0, k: 1 };
const scene = document.getElementById('scene');
const viewport = document.getElementById('viewport');
let isPanning = false, startPoint = { x: 0, y: 0 };
let flowsData = null;

viewport.addEventListener('mousedown', (e) => {
  isPanning = true;
  startPoint = { x: e.clientX - transform.x, y: e.clientY - transform.y };
});
window.addEventListener('mousemove', (e) => {
  if (!isPanning) return;
  transform.x = e.clientX - startPoint.x;
  transform.y = e.clientY - startPoint.y;
  updateTransform();
});
window.addEventListener('mouseup', () => isPanning = false);
viewport.addEventListener('wheel', (e) => {
  e.preventDefault();
  const factor = e.deltaY < 0 ? 1.1 : 0.9;
  transform.k *= factor;
  updateTransform();
});

function updateTransform() {
  scene.setAttribute('transform', `matrix(${transform.k} 0 0 ${transform.k} ${transform.x} ${transform.y})`);
}

fetch('flows.json')
  .then(r => r.json())
  .then(data => { flowsData = data; });

function loadScreen(screenId, txtPath, exitCode) {
  document.getElementById('screen-id-display').textContent = screenId;
  const badge = document.getElementById('exit-badge');
  badge.textContent = `Exit ${exitCode}`;
  badge.style.color = exitCode === 0 ? 'var(--green)' : (exitCode === 6 ? 'var(--yellow)' : 'var(--red)');
  
  fetch(txtPath)
    .then(r => r.text())
    .then(text => {
      document.getElementById('terminal-body').textContent = text;
      renderOutActions(screenId);
    })
    .catch(() => {
      document.getElementById('terminal-body').textContent = "Failed to load fixture transcript.";
    });
}

function renderOutActions(screenId) {
  const container = document.getElementById('terminal-actions');
  container.innerHTML = '';
  if (!flowsData) return;

  const transitions = flowsData.transitions.filter(t => t.from.includes(screenId));
  transitions.forEach(t => {
    t.to.forEach(targetId => {
      const btn = document.createElement('button');
      btn.className = 'action-btn';
      btn.textContent = t.ui?.button_text || `Transition -> ${targetId}`;
      btn.onclick = () => {
        const parts = targetId.split('.');
        const txtPath = `screens/${parts[0]}/${parts[1]}/${targetId}.txt`;
        loadScreen(targetId, txtPath, 0);
      };
      container.appendChild(btn);
    });
  });
}

function focusJourney(journeyId) {
  if (!flowsData) return;
  const journey = flowsData.journeys[journeyId];
  if (journey) {
    document.getElementById('screen-id-display').textContent = `Journey: ${journey.name}`;
    document.getElementById('terminal-body').textContent = journey.description;
    const parts = journey.entry.split('.');
    const txtPath = `screens/${parts[0]}/${parts[1]}/${journey.entry}.txt`;
    loadScreen(journey.entry, txtPath, 0);
  }
}
</script>
</body>
</html>
```