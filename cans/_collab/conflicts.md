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
