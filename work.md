Here are **10 concrete absurdities, non-senses, and contradictions** inside `cans/artifacts/wireframe/` when cross-checked against the **cans spec (SSOT)**:

---

### 1. The Day-0 Blind Spot: Zero Git & S3 Probes on Boot
* **The Spec (`assembly.md`, `recovery.md`):** Capcli demands host `git >= 2.30`, an active Git worktree, and an append-only S3/R2 WORM object store. All backups and audit notarizations (`checkpoint.sig`, `witness.log`) stream directly to S3.
* **The Wireframe Reality:** 
  * `sys.doctor.success.nominal` checks Python and `bwrap`, but **completely ignores Git and S3**. 
  * No screen tests: "Is `.git` initialized?", "Are Git user/email set?", "Is the S3 bucket reachable?", or "Are AWS/R2 credentials configured?".
  * In `sys.doctor.success.report.json`, it reports `ledger_root_hash: ... (WORM-checkpointed)` right after initial install, before S3 is even set up. Pure fiction.

---

### 2. Dual Confirmation Flags vs "Banned Flags" Paradox
* **The Spec (`recovery.md`, `space.md`, `interface.md`):** Destructive production actions strictly require an **out-of-band cryptographic signature** (Passkey/GPG). The spec explicitly says: *"terminal flag overrides are prohibited"*.
* **The Wireframe Absurdity:** Table 4.8 defines:
  * `env.remove.denial.prod_flags` $\rightarrow$ *"Prod removal requires dual confirmation flags"*.
  * Why does a screen requiring CLI confirmation flags exist when the SSOT bans terminal flag bypasses and mandates crypto signatures?

---

### 3. The 12-Flag Ceiling vs Phantom Replay Flag
* **The Spec (`interface.md`):** *"Flag ceiling — universal flags frozen at exactly twelve; no per-noun growth"*. All 12 are explicitly named (`--json`, `--as`, `--env`, `-m`, `--workspace`, `--session`, `--in`, `--out`, `--dry-run`, `--reason`, `--by`, `--lock`). Furthermore, HTTP calls during audit replay are *"strictly forbidden unless manually flagged"*.
* **The Wireframe Absurdity:** Table 4.9 has `sys.replay.denial.external`: *"HTTP calls require manual flag"*.
* **The Catch:** Which flag? There is no `--manual` or `--allow-external` in the frozen 12 flags. The wireframe invents a requirement that violates its own flag ceiling.

---

### 4. Tamper Forensics: Exit 0 Success for a Broken Hash Chain?!
* **The Spec (`physics.md`, `README.md`):** Exit 5 is `kernel.panic` (unrecoverable media corruption/tamper). A broken SHA-256 chain is an existential security failure.
* **The Wireframe Absurdity:** Table 4.9 and `_flows.json` define:
  * `sys.doctor.success.tamper` $\rightarrow$ **State: `success`, Exit: `0`**.
  * `journey_tamper_forensics`: transitions from `success.tamper` (Exit 0) to `success.quarantine` (Exit 0).
* An attacker breaks the causal hash chain, and Capcli exits with **`0` (SUCCESS)**?! That breaks the entire fail-closed philosophy.

---

### 5. Missing Critical Quota Denial Screen (Exit 2 Quota Void)
* **The Spec (`budget.md`):** Priority classes govern rate exhaustion:
  * Background/Standard tasks yield cleanly via **Exit 6**.
  * Critical tasks drain the pool to 0, then throw **Exit 2** (Hard Denial).
* **The Wireframe Absurdity:** Table 4.1 (`run/`) only has `run.execute.yield.quota` (Exit 6). 
* The **Exit 2 denial for exhausted Critical tasks does not exist** anywhere in the `run/` screens. Half of the priority scheduling engine has zero test fixtures.

---

### 6. Contract Invariant Broken: Pagination in Doc Screens
* **The Spec (`action.md`, `manifest.json`):** Any output exceeding the token cap **must** adhere to the keyset envelope schema:
  `required_envelope_keys: ["items", "next_cursor", "has_more"]`.
* **The Wireframe Absurdity:** Look at fixture 5.11 (`doc.read.success.sliced`):
  * It returns `outline_node`, `tokens`, and `has_more`.
  * It completely omits `items` and `next_cursor`. The wireframe author violated the kernel's own mandatory pagination schema.

---

### 7. OCC State Drift Wrongly Blamed on `db.engine`
* **The Spec (`assembly.md`, `action.md`):** When human inquiries resume, `occ_fence_gate.rs` inspects entity state hashes. If records drifted while the human was deciding, it aborts.
* **The Wireframe Absurdity:** Table 4.6 has:
  * `ping.resolve.denial.occ_conflict` $\rightarrow$ **Domain: `db.engine`**, Condition: `stale_state`.
* SQLite’s engine didn't fail. SQLite has no concept of OCC application fences; the **Kernel Policy Gate** caught the drift. Routing this to `db.engine` masks kernel logic as an internal database crash.

---

### 8. Complete Mismatch on S0–S10 & H0–H7 Onboarding
* **The Spec (`interface.md`):** Human onboarding is explicitly a 10-step ladder: S1 (Intent) $\rightarrow$ S2 (Proposal) $\rightarrow$ ... $\rightarrow$ S7 (Discovery) $\rightarrow$ S8 (Scaffold routine) $\rightarrow$ S9 (Sim prove & promotion) $\rightarrow$ S10 (Receipt).
* **The Wireframe Reality (`_flows.json`):** 
  * Discovery (S7) is shoved to the front.
  * Routine scaffolding (S8) and Trust Promotion (S9) are **completely deleted**.
  * For harnesses (H0–H7), H6 demands *authoring* `overview.py`, but the flow tries to run `capcli run overview` before the harness ever writes the code.

---
### 9. The Phantom DB "Corruption" Step
* **In `_flows.json` (`journey_human_onboarding`):**
  * Description promises: *"snapshot creation -> state corruption -> restore proof"*.
* **In Transitions:**
  * `t_human_commit_to_snapshot`: executes `capcli db snapshot`.
  * `t_human_snapshot_to_corrupt`: immediately executes `capcli db restore snap_onboarding_01`.
* Nothing ever corrupts or mutates state in between. The "corruption" step is an imaginary transition; the restore proof tests absolutely nothing.

Here is the breakdown for **#10 through #15**, zeroing in on the **Sensory Inbox**, the **Notification system (`ping`)**, and the **Session Overview**:

---

### 10. The Overview Chicken-and-Egg Paradox (`_flows.json`)
* **The Spec (`trust.md`, `interface.md`):** Autonomous routines must follow strict lifecycle physics: Author (H6) $\rightarrow$ Prove in sim (H7) $\rightarrow$ Ship $\rightarrow$ Run. Unproven draft routines cannot be executed in live workflows.
* **The Wireframe Absurdity:** Look at the machine onboarding transitions in `_flows.json`:
  1. `t_harness_trace_to_overview`: executes `capcli run overview` (`run.overview.success.populated`).
  2. `t_harness_overview_to_final_prove`: executes `capcli routine prove overview --env sim`.
* **The Non-Sense:** 
  * The flow literally **runs the overview routine before proving it**.
  * Even worse: where did the code come from? H6 in `interface.md` mandates *"author mandatory overview routine"*, but `_flows.json` skips drafting/scaffolding entirely and runs a non-existent routine right out of thin air.

---

### 11. The Ghost Inbox: `sys inbox pop` Has No Database Table
* **The Spec (`action.md`, `world.md`):** Agents are grounded via physical stimulus; telepathic hallucinations are banned. Agents must fetch inbound sensory tasks using `sys inbox pop`.
* **The Database SSOT (`world.md`, `system-schema.yaml`):** The spec explicitly enumerates all **13 kernel-managed tables**:
  `_audit`, `_api_quota`, `_api_catalog`, `_budget_frames`, `secrets`, `agents`, `claims`, `_pending_asks`, `_watch_cursors`, `_outbox_events`, `routine_stats`, `_suspended_tasks`, `_templates`.
* **The Non-Sense:** **There is no `_inbox` table.** 
  * Where do inbound sensory events live? 
  * How do they get queued? There is no `sys inbox push` command.
  * Wireframe lists `sys.inbox.success.populated` and `sys.inbox.success.empty`, but the underlying SSOT schema has literally nowhere to store the rows. It’s an unbacked phantom feature.

---

### 12. Architectural Category Error: `ping` Denials Blamed on SQLite
* **The Spec (`physics.md`, `_states.json`):** 
  * `policy.authorizer` is native compiled C inside `sqlite3_set_authorizer` evaluating `(action, table, column)` tuples for SQLite SQL statements.
  * `policy.notify` is the dedicated engine domain created specifically for human notification and inquiry policies.
* **The Wireframe Absurdity:** Look at Table 4.6:
  * `ping.notify.denial.quiet_hours` $\rightarrow$ Domain: **`policy.authorizer`**.
  * `ping.ask.denial.options_cap` $\rightarrow$ Domain: **`policy.authorizer`**.
* **The Non-Sense:** Why is SQLite's C database authorizer checking whether it’s 10:00 PM (`quiet_hours`) or whether an interactive prompt has more than 5 UI buttons (`options_cap`)?! That is an absurd category error. It belongs in `policy.notify`, not the SQLite database authorizer.

---

### 13. Keyset Pagination Absurdity on `run.overview`
* **The Spec (`action.md`, `manifest.json`):**
  * Raw string truncation or slicing is **strictly illegal**.
  * Outputs exceeding 500 tokens **must** return typed keyset pagination: `{ items, next_cursor, has_more }`.
  * `action.md` explicitly forbids carrying cursors across LLM turns.
* **The Wireframe Absurdity:** Table 4.1 defines `run.overview.success.truncated`: *"Oversized overview clipped"*.
* **The Non-Sense:** 
  * An overview is a single-shot aggregate KPI briefing (domain KPIs, active locks, budget fuel remaining, system health).
  * You cannot paginate an aggregate situational KPI report with a cursor. If an overview routine blows past 500 tokens, it violates the shape contract and must fail during verification (`exit 3`), not get "clipped" into an unusable half-summary.

---

### 14. Exit Code Schizophrenia on Human Suspensions (`ping.ask`)
* **The Spec (`action.md`, `_states.json`):** 
  * Inquiries suspend execution. `ctx.ping.ask` freezes the frame, persists OCC fences to `_pending_asks`, and **must exit with code 6 (`yield`)**.
* **The Wireframe Absurdity:**
  * Routine runtime screen (`run.execute.yield.ask`): **Exit 6**.
  * CLI command screen (`ping.ask.success.suspended`): **Exit 0**.
* **The Non-Sense:** 
  * If a bash script or harness CLI calls `capcli ping ask` and gets **`exit 0`**, it assumes the operation succeeded and proceeds to the next command. 
  * In reality, the action is suspended pending human resolution! Emitting `0` instead of `6` completely breaks subshell determinism.

---

### 15. The "Infallible Wire" Delusion for Notifications
* **The Spec (`physics.md`):** Fail-closed on everything. Unchecked network assumptions are forbidden.
* **The Wireframe Absurdity:** Look at the screen inventory for `ping/notify` in Table 4.6. There are only three screens:
  1. `dispatched` (Exit 0)
  2. `quiet_hours` (Exit 2)
  3. `missing_intent` (Exit 3)
* **The Non-Sense:**
  * What happens when `--channel slack` is passed but no Slack webhook is configured in the vault?
  * What happens if the notification HTTP endpoint returns a 500, 404, or TLS handshake timeout?
  * What if `--principal user:bob` does not exist in the `agents` or permissions tables?
  * The wireframe provides **zero screens, zero exit codes, and zero diagnostic envelopes** for transport, configuration, or recipient failures. It acts as if outbound messaging can never fail.
