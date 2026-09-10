# governance.yaml *(final v2 — primitive-aware)*

> Structural governance: what capabilities may **be** — sizes, counts, cadence, budgets. (Behavior — rows, writes, spend — lives in `policy.yaml`. Zero overlap.)

```yaml
# ═══════════════════════════════════════════════════════════════
# governance.yaml — registry & capability shape governance
# Version-locked with schema.yaml + policy.yaml at boot.
# Compiled by kernel; never runtime-editable; exceptions = git commits.
# ═══════════════════════════════════════════════════════════════
version: 8
schema_version: 12                    # mismatch → kernel refuses boot
policy_version: 4                     # triple-lock across all config

# ───────────────────────────────────────────────────────────────
# 1. REGISTRY — the shelves have dimensions
# ───────────────────────────────────────────────────────────────
registry:
  max_routines: 300                   # hard cap — register refuses past it
  soft_cap: 200                       # sys doctor nags; consolidation urged
  max_per_agent_draft: 30             # anti-flood per agent identity
  creation_rate: { per_hour: 10 }     # no rapid-fire generation
  search_index:
    max_description_tokens: 60        # keep search surface lean per capability
    require_description: true         # unsearchable = unregistrable

# ───────────────────────────────────────────────────────────────
# 2. ROUTINE SHAPE — defaults every file must satisfy
# ───────────────────────────────────────────────────────────────
routine_shape:
  loc:        { min: 5,    max: 150 }    # split big routines; no stubs
  tokens:     { min: 50,   max: 2000 }   # file size in tokens (context cost)
  params:     { max: 8 }                  # interface bloat guard
  description:{ min_words: 5 }            # searchable or it doesn't ship
  imports:    { max_routine_imports: 3 }  # composition depth hygiene
  execution:
    max_ops_per_run: 50               # primitive DAG ceiling — op 51 aborts
    max_duration_seconds: 300         # sandbox watchdog kill
    max_result_tokens: 500            # summary cap crossing to the model
    max_txn_statements: 10            # one transaction stays one thought
  versions:
    max_versions_kept: 25             # provenance graph stays navigable
    max_rollback_depth: 5
  manifest_drift: anomaly             # undeclared primitives trigger governance event

# ───────────────────────────────────────────────────────────────
# 3. OVERRIDES — reviewable exceptions, never --force
# ───────────────────────────────────────────────────────────────
overrides:
  large_migration:                    # declared need approved by human commit
    execution: { max_duration_seconds: 900, max_ops_per_run: 200 }
  weekly_report:
    execution: { max_result_tokens: 1500 }   # reports may summarize longer
  order_status:                       # served endpoint gets tighter, not looser
    execution: { max_duration_seconds: 5 }   # external callers pay for latency

# ───────────────────────────────────────────────────────────────
# 4. MAINTENANCE — subtraction runs on schedule
# ───────────────────────────────────────────────────────────────
maintenance:
  consolidation:
    schedule: "0 3 * * 0"             # Sunday 03:00
    max_session_minutes: 30           # consolidation labor is budgeted too
    max_proposals_per_session: 10     # human review stays human-sized
    duplicate_similarity: 0.85        # deterministic SQL/param similarity
    fingerprint_similarity: 0.90      # identical primitive sequences = merge candidates
    merge_requires_human: true        # always
    auto_retire_dead: false           # propose, never auto-destroy
  decay:
    dead_after_days: 30               # unused → retire candidate
    fail_threshold: 0.7               # success rate below → rollback candidate
    stale_sim_after_days: 14          # sim data too old vs prod → re-seed nag
  audits:
    mirror_lag_max_minutes: 5         # JSONL → _audit mirror freshness SLA
    hash_chain_verify: "0 4 * * *"    # daily integrity check

# ───────────────────────────────────────────────────────────────
# 5. SCHEDULE — time is governed like everything else
# ───────────────────────────────────────────────────────────────
schedule:
  max_active: 20
  max_per_agent: 10
  min_interval_minutes: 5             # no sub-5-minute cron (use watch)
  max_catchup_fires: 1                # daemon restart ≠ fire the missed 40
  dead_schedule_disable: true         # bound routine retired → auto-disable loudly

# ───────────────────────────────────────────────────────────────
# 6. WATCH — ears with limits
# ───────────────────────────────────────────────────────────────
watch:
  max_active: 50
  max_per_agent: 15
  webhook:
    max_payload_bytes: 65536
    events_per_minute: 100            # DDoS guard on the mailbox
  poll:
    min_interval_minutes: 5           # no tight-loop polling
    max_poll_watches: 10              # polling costs egress budget
  dead_letter:
    max_age_days: 30
    max_items: 1000                   # FIFO purge past this, loudly

# ───────────────────────────────────────────────────────────────
# 7. SERVE — the counter window is the strictest door
# ───────────────────────────────────────────────────────────────
serve:
  max_endpoints: 10                   # exposure surface stays small
  max_keys: 25
  min_trust: pinned                   # non-negotiable floor
  require_version_pin: true           # serve order_status@12, never a moving target
  allow_writes_default: false         # inbound writes cost explicit opt-in
  bind: "127.0.0.1"                   # internal-first; public lives behind a proxy
  key_rotation_days: 90               # keys expire; re-issue is a human act
  response:
    max_body_bytes: 65536
    max_result_tokens: 500            # inherits routine result cap

# ───────────────────────────────────────────────────────────────
# 8. NOTIFY / ASK — voices don't shout
# ───────────────────────────────────────────────────────────────
notify:
  max_channels: 3
  message_max_tokens: 300             # notifications are summaries, not essays
  ask:
    question_max_tokens: 100
    max_options: 5
    default_timeout_minutes: 60
    max_timeout_minutes: 480

# ───────────────────────────────────────────────────────────────
# 9. ENVIRONMENTS — worlds stay honest
# ───────────────────────────────────────────────────────────────
env:
  max_worktrees: 5                    # prod + dev + sim + 2 experiments
  prod_removal_flags: 2               # number of confirm flags to remove prod (!)
  require_backup_push: true           # no world exists unbacked
  sim_seed_masking: enforce           # sensitive columns masked on fork, always

# ───────────────────────────────────────────────────────────────
# 10. BACKUP — recoverability is a structural property
# ───────────────────────────────────────────────────────────────
backup:
  interval_minutes: 15
  max_drift_minutes: 30               # doctor alarms if commits fall behind
  push: true
  include_audit: true
  trigger_on: [promote, migrate, import, register, restore, serve.add]

# ───────────────────────────────────────────────────────────────
# 11. DENIAL UX — limits teach, not just block
# ───────────────────────────────────────────────────────────────
denials:
  cite_measured_value: true           # "file has 342 LOC, max is 150"
  suggest_remediation: true           # "split it, or propose an override"
  log_all: true                       # every governance.deny is an audit event
  blacklist_intents: ["test", "update", "misc", "fix", "..."]
  min_intent_words: 3
```

## What changed from v1

| Section | Addition | Why |
|---|---|---|
| `routine_shape.manifest_drift` | `anomaly` | Undeclared primitives executing at runtime now trigger a governed event instead of silent acceptance |
| `maintenance.consolidation.fingerprint_similarity` | `0.90` | Consolidation now clusters by primitive sequence identity, not just code text similarity |

Everything else remains structurally identical. The enforcement map, anti-decisions, and command surface carry forward unchanged.

## Enforcement map reminder

| Section | Gate |
|---|---|
| `registry` | `routine new` / register |
| `routine_shape` | `routine validate` (static + manifest) + runtime (ops/duration/result/drift) |
| `overrides` | compile-time merge: **effective = min(need, ceiling, override)** |
| `maintenance` | schedule subsystem + consolidation session runner |
| `schedule` / `watch` / `serve` / `notify` | hand registration commands |
| `env` | `env new` / `env remove` / `env doctor` |
| `backup` | daemon committer + `sys doctor` drift alarm |
| `denials` | every `governance.deny` event format |

## The principle

> **Policy gates the *act*; governance gates the *artifact*.** One governs verbs, the other nouns — and together they keep the registry a library instead of a landfill. 📏📚