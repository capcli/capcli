- conflicts

---
Task ID: 5-b (action.md dedup+deepen)
- dups-action.json idx25 (Never runtime-editable): keeper=physics.md but the line lives at trust.md:33; physics.md lacks it. Pointed action.md → physics.md#Two-layer-enforcement per keeper rule. Physics owner should confirm landing spot.
- dups-action.json idx41 (Pre-call deny before egress): keeper=physics.md but the line lives at budget.md:42. Pointed action.md → physics.md#Fail-closed-stance per keeper rule. Physics owner should confirm.
- dups-action.json idx53 (No silent edits): keeper=trust.md but the line lives at time.md:116. Pointed action.md → trust.md#Evidence (hash-pinned lines live there). Time owner should confirm.
- dups-action.json idx59 (Near-duplicate check at birth): keeper=space.md but the line lives at time.md:19. Pointed action.md → space.md#Primitive-scoping per keeper rule. Space/time owners should reconcile.
- dups-action.json idx5 (capability.search event): keeper=effect.md; effect.md does not yet carry capability.search. Pointed action.md → effect.md#Audit-spine. Effect owner should add the event line.
- NOT MINE: interface.md:425 broken ref "see Anti-decisions" (no file prefix, from 5-e af703f4) — should be `see action.md#Anti-decisions`. Left for 5-e.
- NOT MINE: world.md:221 self-reference (world.md → world.md, in-flight WIP by another agent).

---
Task ID: 5-e (interface.md dedup+deepen)
- dups-interface.json (PWA session token / --as mapping): keeper=agent.md, but agent.md:79 itself reads "see interface.md#SDK-contract". Per keeper rule I replaced interface.md auth line with "Auth: session token maps to `--as`: see agent.md#Sessions-and-sockets". Result is a mutual pointer pair (agent.md ↔ interface.md). Agent.md owner should drop their "see interface.md#SDK-contract" tail or move the canonical sentence into agent.md.
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
- dups-action idx43 ("The human verifies the why; the kernel verifies the what"): keeper=overview.md but the line lives at agent.md:42 and trust.md:21. Kept in trust.md for now; overview owner should land the canonical copy, then agent/trust can see:.
- dups-action idx25 ("cannot loosen its own cage"): keeper=physics.md (physics.md:106 has it; action.md:138 already sees physics.md#Two-layer-enforcement). Converted trust.md's copy to "see physics.md#Two-layer-enforcement" per keeper rule.
- dups-action idx22 vs dups-time-space-trust rec62 (min() precedence line): conflicting keepers (budget.md vs trust.md). Kept in trust.md#Overrides→Precedence per 6-b task content list ("min() precedence" is trust content); budget.md:46 pointer targets trust.md#Overrides, budget.md#Cascade still owns cascade mechanics.
- Promotion queue mechanics (48h SLA, promotion.sla_breached, CI --by, veto countdown) are canonical in time.md#Stage-details (5-c); trust.md#Promotion-queue keeps the authority angle + one see: — no dup re-added.
