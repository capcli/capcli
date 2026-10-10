# Codification

Codification turns behaviour an agent already repeats into a governed routine: named, typed, bounded, rehearsed, and promoted on evidence. Raw SQL exploration becomes routine exploitation. Ad-hoc sequences stay ad-hoc until telemetry proves they recur.

---

## What counts as a codification candidate

A pattern qualifies when the audit record shows all three properties:

- **Recurrence.** The same leaf sequence appears across separate turns or sessions.
- **Atomicity.** The steps succeed or fail as one unit; a half-finished sequence leaves misleading state.
- **Stable shape.** Inputs vary, structure stays constant. Varying values become typed parameters; varying structure stays manual.

One-off investigations, exploratory reads, and sequences still changing shape remain uncodified by design.

---

## The pipeline

### 1. Mine the record

Routine fingerprints aggregate executed leaf sequences from the audit ledger. Frequent shared subsequences surface as routine proposals, ranked by repetition rather than by guesswork.

```bash
capcli run search gaps --since 7d
capcli sys audit query "SELECT command, count(*) FROM _audit GROUP BY command HAVING count(*) > 5"
```

Gap detection works from the same ledger: repeated multi-step command chains with no covering routine appear as codification gaps.

### 2. Scaffold the routine

```bash
capcli routine new <routine_name>
capcli template apply tpl://routine/<name> <target> [-p k=v]
```

Direct authoring writes `routines/<name>.py`; blueprint instantiation stamps a draft routine from a `tpl://routine/*` micro-pattern. Either route registers the result at draft trust, version 1, with zero promotional credit.

### 3. Fit the shape envelope

The intake gate measures the scaffold before registration:

- Token envelope: maximum 2,000 tokens per routine file. Lines of code carry no ceiling; whitespace, comments, and docstrings count for nothing.
- Complexity: cyclomatic complexity at most 10 branch paths, evaluated at AST prepare-time.
- Parameters: at most 8 typed `Param` declarations, each with an explicit type.
- Description: a searchable description is mandatory. Unsearchable code never ships.
- Limits: explicit `limits={"max_ops": N, "max_duration_seconds": S}` on the `@routine` decorator.

Composition between routines runs through `ctx.call(routine, params)`. Direct cross-routine module imports play no part in the model, and a callee holds trust equal to or higher than its caller.

### 4. Prove in simulation

```bash
capcli routine prove <routine_name> --env sim
```

Proving replays the routine against masked simulation data and compares the dynamic execution fingerprint against the declared manifest. Executed leaves form a subset of declared leaves, policy denials stay at zero, and drift events stay at zero. Passing prove makes the routine a promotion candidate; prove alone grants no trust.

### 5. Promote on evidence

```bash
capcli routine ship <routine_name> reviewed --queue --reason "<why codified>"
```

Promotion reads `routine_stats` and the audit mirror directly. The full gate list, canary window, and demotion paths live in [Promotion](../automate/promotion.md).

### 6. Maintain or retire

Codified routines decay. Sustained failure demotes a routine to draft, and retirement removes callability while preserving the full provenance graph — version hashes, manifest hashes, and the audit chain stay readable forever. Nothing codified becomes immortal; everything codified stays inspectable.

---

## The overview routine

A workspace with no situational routine forces every agent to burn context on raw table queries. The canonical first codification is `routines/overview.py`, registered under the name `overview`: an idempotent routine aggregating core domain counts inside a strict result envelope of under 500 result tokens. Agents prove it in sim and enqueue it for reviewed trust, giving every later session a one-call briefing instead of a schema crawl.

---

## What codification never does

- Codification never bypasses intake. A routine written straight to disk still passes the shape gate before registration.
- Codification never inherits trust from a template, a sibling routine, or prior ad-hoc success.
- Codification never deletes history. Retirement and rollback move pointers; the record stays.

---

**Recognising repetition as a human operator:** → [Repetition](../automate/repetition.md)
**The trust mechanics after codification:** → [Promotion](../automate/promotion.md)
