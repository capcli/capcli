- conflicts

---
Task ID: 5-b (action.md dedup+deepen)
- dups-action.json idx25 (Never runtime-editable): keeper=physics.md but the line lives at trust.md:33; physics.md lacks it. Pointed action.md → physics.md#Two-layer-enforcement per keeper rule. Pending: physics owner confirms the landing spot.
- dups-action.json idx41 (Pre-call deny before egress): keeper=physics.md but the line lives at budget.md:42. Pointed action.md → physics.md#Fail-closed-stance per keeper rule. Pending: physics owner confirms.
- dups-action.json idx53 (No silent edits): keeper=trust.md but the line lives at time.md:116. Pointed action.md → trust.md#Evidence (hash-pinned lines live there). Pending: time owner confirms.
- dups-action.json idx59 (Near-duplicate check at birth): keeper=space.md but the line lives at time.md:19. Pointed action.md → space.md#Primitive-scoping per keeper rule. Pending: space/time owners reconcile.
- dups-action.json idx5 (capability.search event): keeper=effect.md; effect.md does not yet carry capability.search. Pointed action.md → effect.md#Audit-spine. Pending: effect owner adds the event line.
- NOT MINE: interface.md:425 broken ref "see Anti-decisions" (no file prefix, from 5-e af703f4) — correct form: `see action.md#Anti-decisions`. Left for 5-e.
- NOT MINE: world.md:221 self-reference (world.md → world.md, in-flight WIP by another agent).

---
Task ID: 5-e (interface.md dedup+deepen)
- dups-interface.json (PWA session token / --as mapping): keeper=agent.md, but agent.md:79 itself reads "see interface.md#SDK-contract". Per keeper rule I replaced interface.md auth line with "Auth: session token maps to `--as`: see agent.md#Sessions-and-sockets". Result is a mutual pointer pair (agent.md ↔ interface.md). Open for the agent.md owner: drop the "see interface.md#SDK-contract" tail or move the canonical sentence into agent.md.
- interface.md:425 broken ref from af703f4 (my own) — FIXED in 5dae233 (same-file Anti-decisions list cannot be a see: target; reworded).
---
Task ID: 6-a (physics.md dedup+deepen)
- dups-action.json idx25 (Never runtime-editable, keeper=physics.md): keeper line landed in physics.md Two-layer enforcement > Policy vs governance > governance.yaml as "never runtime-editable — a routine cannot loosen its own cage" (0e66e41). trust.md:33 keeps its fuller variant; action.md pointer to physics.md#Two-layer-enforcement now resolves. Confirmed.
- dups-action.json idx41 (Pre-call deny before egress, keeper=physics.md): keeper line landed in physics.md Fail-closed stance > Runtime denials: "Pre-call enforcement: remaining ≤ deny_at_remaining → exit 2 before egress, not 429 after" (0e66e41). budget.md:42 keeps its variant. Confirmed.
- dups-world-physics.json idx4 (Exit codes are law, keeper=physics.md): physics.md retains the exit-code law line and deepened it with per-code children; interface.md:10 trim is the interface owner's action per the record note (already flagged there).
- dups-world-physics.json idx13 (Intelligence is the harness's job → overview.md#Core-philosophy): physics.md Kernel neutrality now ends in that see: leaf; overview.md#Core-philosophy anchor verified to exist.

---
Task ID: 6-b (trust.md dedup+deepen)
- dups-time-space-trust rec3 (hash-pinned line, keeper=time.md) vs dups-action idx53 (keeper=trust.md): conflicting keepers across passes. Kept a reworded "No silent edits: every change is a new hash-pinned version; replay verifies the hash" at trust.md#Evidence because action.md:159 + action.md:169 point there. time.md#Versioning-&-provenance stays canonical for the version walk. Action owner: consider retargeting action.md:169 to time.md if they prefer strict single-home.
- dups-action idx43 ("The human verifies the why; the kernel verifies the what"): keeper=overview.md but the line lives at agent.md:42 and trust.md:21. Kept in trust.md for now. Pending: overview owner lands the canonical copy; agent/trust then point via see:.
- dups-action idx25 ("cannot loosen its own cage"): keeper=physics.md (physics.md:106 has it; action.md:138 already sees physics.md#Two-layer-enforcement). Converted trust.md's copy to "see physics.md#Two-layer-enforcement" per keeper rule.
- dups-action idx22 vs dups-time-space-trust rec62 (min() precedence line): conflicting keepers (budget.md vs trust.md). Kept in trust.md#Overrides→Precedence per 6-b task content list ("min() precedence" is trust content); budget.md:46 pointer targets trust.md#Overrides, budget.md#Cascade still owns cascade mechanics.
- Promotion queue mechanics (48h SLA, promotion.sla_breached, CI --by, veto countdown) are canonical in time.md#Stage-details (5-c); trust.md#Promotion-queue keeps the authority angle + one see: — no dup re-added.

---
## Resolved (this audit pass)
- capability.search event: ADDED to effect.md#Kernel-event-payloads (was missing)
- Mutual pointer agent.md ↔ interface.md: agent.md now owns canonical PWA session token sentence
- hash-pinned line keeper: trust.md#Evidence confirmed as canonical; time.md#Versioning owns version walk
- "The human verifies the why": canonical home pinned to overview.md#Human-authority; trust.md and agent.md cite it
- min() precedence: budget.md#Cascade owns mechanics; trust.md#Overrides owns authority angle
- world.md self-reference: resolved to physics.md#Fail-closed-stance lockfile check

---
Task ID: audit-2026-10-07 (errors.md row verification, docs/reference/errors.md R01–R48)
Logged, not resolved — each needs its cans owner's ruling:
- C-1 `api sync` verb: interface.md (CLI owner) defines no `api sync`; action.md bans full sync, yet action.md cadence pointer, effect.md `api.sync` event, governance `api.sync.min_interval_hours: 24`, and `api.sync.*` fixtures assume it. Blocks errors.md R23/R24. RESOLVED 2026-10-09 by owner ruling: `api sync` legalized (interface.md API path entry; action.md Full sync bullet under cadence limits).
- C-2 webhook flags: interface.md bind webhook `[--ingress|--tunnel] [-m]` vs action.md `[--driver ...] [-m]` (no ingress). Fixture uses `--ingress`.
- C-3 rollback syntax: interface.md `routine rollback <name> [version]` vs time.md `routine rollback <name> --to-version N`; fixture is positional.
- C-4 `sys agent` flattening: interface.md/agent.md `sys agent register, list, revoke` vs wireframe `sys.register`/`sys.revoke` fixture commands.
- C-5 `env merge` syntax: interface.md/space.md `env merge <name> [target=prod]` vs fixture `capcli env merge stg --into dev` (`--into` undefined by the CLI owner).
- C-6 exit-5 scope: physics.md/effect.md reserve exit 5 (`kernel.panic`) for unrecoverable media loss; `run.execute.panic.secret_leak` fixture assigns exit 5 to a secret leak (physics mandates `kill_and_alert`, no exit). errors.md R10 follows the fixture pending ruling.
- C-7 cassette vs mock: action.md bans static cassette replays from promotion gating; space.md replays `apis/<provider>.cassette.jsonl`; policy.yaml and the R25 fixture use `apis/<provider>.mock.yaml`. Three artefact names, one seam.
- C-8 Tier 1 sandbox floor: physics.md absent bwrap → fallback container/microvm, abort only if all providers fail; `sys.doctor.refusal.boot` fixture calls bwrap "mandatory on Tier 1", floor 0.8.0. errors.md R43 follows the fixture.
- C-9 doc slicing: `doc.read.success.sliced` fixture renders outline-node output from `doc read --max-tokens 100`; interface.md defines no leaf addressing (known open ruling; `--section` illegal in v1 regardless).
- C-10 agent registry cap: "8 registered agents" cap exists only in the `sys.register.denial.cap` fixture; no owner (agent.md/governance.yaml/policy.yaml) states it.

## Still open
Task audit-2026-10-07 items C-1..C-10 above. All earlier cross-file keepers and duplicate ownership claims reconciled.

---
Task ID: PM15-D (wireframe post-mortem round 2, item 2 — env.remove dual confirmation)
- recovery.md#Offboarding-sequence Stage 3 says "remove environments with dual confirmation flags: see space.md#Safety-controls", but space.md#Safety-controls itself mandates "out-of-band cryptographic signature via Cockpit challenge or local key", recovery.md#Teardown-invariants says "terminal flag overrides are prohibited", and space.md#Environment-drift says "CLI flag bypasses are rejected". The SSOT is internally tense on the word "flags". Resolution taken in the wireframe (fixture layer only): `env.remove.denial.prod_flags` (which told users to re-run with `--confirm-backup --confirm-prod`) is rewritten as `env.remove.denial.backup_unverified` — the second, distinct teardown confirmation (verified final backup push, recovery.md#Teardown-invariants "backup verification — push dry-run required before deletion"); the signature gate stays `env.remove.denial.crypto_sig`. Pending cans owner ruling: reword recovery.md Stage 3 to "dual confirmation" without "flags", or bless the flags. Note: artifacts/test-plan se_06/se_13 still gate `env merge` on `--confirm-backup/--confirm-prod` — outside wireframe scope, flagged for the test-plan owner.

---
Task ID: PM15-D (wireframe post-mortem round 2, item 6 — doc.read envelope)
- C-9 follow-up: `doc.read.success.sliced` now carries the full keyset envelope (pagination.items/next_cursor/has_more per manifest.json output_contract.pagination and action.md output-envelope law) with `next_cursor: "doc://refund-policy#3"` — a fragment-style doc-pointer cursor. C-9 already rules leaf addressing open ("interface.md defines no leaf addressing"); the `#<section>` fragment syntax is therefore PROVISIONAL wireframe shape, not a blessed CLI/surface grammar. No `--section` flag is introduced. Pending interface.md owner ruling on the canonical cursor/resume form for doc reads.

---
Task ID: PM15-A (sys/ wireframe post-mortem round 2, items 1/3/4/11)
Date: 2026-10-08

Logged, not resolved — cans/ is SSOT and was left untouched; fixes live in the wireframe layer only.

- C-11 phantom inbox backing (work item 11): interface.md#CLI-surface specs the command ("Sensory inbox — sys inbox pop [--channel <name>]") and action.md grounds it twice ("inbox poll — capcli sys inbox pop fetches sensory queued tasks"; Session-Overview-Primer "sensory inbox — queries queued inbound events without pulling payloads"), but world.md#managed-surfaces enumerates exactly 13 kernel tables (_audit, _api_quota, _api_catalog, _budget_frames, secrets, agents, claims, _pending_asks, _watch_cursors, _outbox_events, routine_stats, _suspended_tasks, _templates — mirrored in artifacts/system-schema.yaml) with no inbound queue table: _watch_cursors holds only stream offsets and _outbox_events is an outbound transactional outbox. Where popped rows live before delivery, and how exactly-once consumption is marked, is unspecified. Fixtures now render cron/webhook-sourced intake (bind:// sources) with "durable queue backing TBD" instead of implying a phantom `_inbox` table; there is no `sys inbox push` anywhere in the spec. Pending world.md owner ruling: add a 14th managed surface or ground the queue on an existing one.
- C-12 (mechanical, prompt/test-plan owners): sys.doctor.success.tamper was reclassified and renamed to sys.doctor.panic.quarantine (exit 5, kernel.panic) per recovery.md#Hash-chains "kernel halts on chain divergence" and test-plan kp_06/ad_09 (both pin exit 5 + kernel.panic on chain tamper). Two read-only-for-wireframe artifacts still carry the old id and need the mechanical rename: artifacts/prompt/_triggers.json trigger `t_forensics_tamper` (screen_id "sys.doctor.success.tamper"; the fixture's forensics trailer is kept pointing at prompt://forensics/audit_tampered@1 pending this), and cans/_adr/003-wireframe-state-taxonomy.md line 14 (round-1 ruling "exit 0; quarantine-operable per cans/effect.md" — superseded by this round-2 reclassification; distinct from panic.tamper total-media-loss, per effect.md#Event-integrity).
  - C-12 resolution (2026-10-08, orchestrator, branch wireframe/post-mortem-15): mechanical rename executed — _triggers.json t_forensics_tamper.screen_id now "sys.doctor.panic.quarantine"; ADR-003 rename-map entry annotated SUPERSEDED IN PART with pointer here. No other stale references repo-wide (grep-verified for all four round-2 renames).

---
Task ID: PM20-B (wireframe post-mortem round 3, items 19/20 — routine retire/rollback)
Date: 2026-10-09

Logged, not resolved — cans/ is SSOT and was left untouched; fixes live in the wireframe layer only. (C-13 deliberately left free for PM20-A's expected promotion-queue sign-off gap per the round-3 setup note.)

- C-14 retire --reason threshold (work item 20): interface.md#CLI-surface line 48 declares `routine retire <name> [--reason]` — syntactically optional — while agent.md#Blast-radius-validation line 49 mandates "threshold justifications — high-impact writes demand --reason", and test-plan bt_07 always retires with a reason. Where exactly the retire --reason demand fires is under-specified: no owner file defines the high-impact threshold for retirement. Wireframe resolution (fixture layer only): `routine.retire.refusal.missing_reason` (exit 3, missing_param) draws the line at "retiring an operational routine in prod" (active, pinned, ingress-bound), mirroring routine.ship.refusal.missing_reason's classification. Pending cans owner ruling: pin the threshold in agent.md or interface.md (e.g. "retire of an ingress-bound or prod-active routine requires --reason").
- C-14b endpoint-binding teardown on retire (work item 20): bt_07 pins only the cron side (governance.yaml#schedule dead_schedule_disable: true; daemon pauses/dissolves the bound schedule on its next tick, audit event bind.delete). The teardown mechanism for bind endpoint routes targeting a retired routine is unpinned: action.md#State-machine line 327 "retired — uncallable, preserved for provenance" implies the route cannot outlive the routine, but no test-plan case or owner file states whether the endpoint binding is revoked atomically with the retire commit or dissolved on a later daemon tick. Wireframe resolution (fixture layer only): `routine.retire.success.completed` renders the endpoint binding (bnd_8d3p) "revoked with retirement — retired = uncallable" while the cron binding (bnd_3k2f) follows the bt_07 daemon-tick pause→dissolve path. Pending test-plan/cans owner ruling.

---
Task ID: PM20-A (wireframe post-mortem round 3, items 16-18 — routine new/prove/ship/pending)
Date: 2026-10-09

Logged, not resolved — cans/ is SSOT and was left untouched; fixes live in the wireframe layer only.

- C-13 promotion-queue sign-off verb (work item 18): trust.md#Promotion-queue (lines 83-90) specs the queue mechanics ("capcli routine ship <name> reviewed --queue"), inspection ("capcli routine pending surfaces batch candidates"), SLA monitoring and the 1-hour veto window; time.md#Stage-details adds "batch approval — human approves queue batch via single audit event" — but names no command. interface.md#Routine-path (line 44) lists "Promotion — routine ship <name> <reviewed|pinned> [--env X] [--reason "..."]" — the --queue flag trust.md/time.md spec is absent from the CLI owner's signature, and no approve/sign-off verb exists anywhere. The genuinely under-specified part is the human batch approval surface. Wireframe resolution (fixture layer only): `routine.ship.success.queued` (exit 0, state_modified true — the queue row IS committed; render states "enqueued for human review; no code shipped, no changes committed to the routine", batch metadata, position, enqueued_at, 48h SLA, supervisor hint "capcli routine pending"); the batch sign-off is rendered with existing spec'd surface only — the human supervisor resolves the queued candidate by running the spec'd `capcli routine ship <name> <rung> --reason "..."` (journey edge routine.pending.success.populated -> routine.ship.success.shipped, consistent with journey_trust_promotion's t_promotion_queue_to_ship), no new verb invented. Pending interface.md/trust.md owner ruling: bless `--queue` in the routine-path signature and name the canonical batch sign-off command (or add the verb).
- C-15 (mechanical, prompt owner): routine.ship.success.queued carries a trailer (prompt://promotion/routine_passed@1, serve L1 — the promotion bank's only prompt covers exactly the enqueue -> canary -> pin protocol) per the round-3 brief treating a queued screen as a legitimate trailer candidate; the prompt id exists in artifacts/prompt/manifest.json. However _triggers.json (read-only for the wireframe round) names no trigger for screen routine.ship.success.queued, and wireframe-structure.md §6.1 field law says "trailer appears only on screens named in _triggers.json". Mechanical follow-up for the prompt owner: add a trigger (suggested id t_promotion_queued, screen_id "routine.ship.success.queued", predicate {"queued": true}, prompt "prompt://promotion/routine_passed@1", serve "L1", reason "candidate enqueued: human review pending").
  - C-15 resolution (2026-10-08, orchestrator, branch wireframe/post-mortem-20): trigger t_promotion_queued added to artifacts/prompt/_triggers.json (screen routine.ship.success.queued -> prompt://promotion/routine_passed@1, serve L1); journey_trust_promotion rewired to visit the queued screen (enqueue -> inspect -> sign-off ship), bypass tag removed from t_promotion_prove_to_queue.
