Capcli Documentation Structure

1. Documentation Tree

The documentation is organized around the reader's journey, not around the internal CANS file structure.

docs/
├── index.md
│
├── start/
│   ├── index.md
│   ├── what-is-capcli.md
│   ├── see-it.md
│   ├── install.md
│   ├── first-task.md
│   └── what-just-happened.md
│
├── use/
│   ├── index.md
│   ├── discover.md
│   ├── inspect.md
│   ├── run.md
│   ├── work-with-your-data.md
│   ├── boundaries.md
│   ├── audit.md
│   └── recover.md
│
├── understand/
│   ├── index.md
│   ├── world.md
│   ├── structure.md
│   ├── capabilities.md
│   ├── effects.md
│   ├── environments.md
│   ├── identity.md
│   ├── budgets.md
│   ├── trust.md
│   └── recovery.md
│
├── automate/
│   ├── index.md
│   ├── repetition.md
│   ├── routines.md
│   ├── rehearsal.md
│   ├── proving.md
│   ├── promotion.md
│   └── operation.md
│
├── agents/
│   ├── index.md
│   ├── contract.md
│   ├── discovery.md
│   ├── inspection.md
│   ├── invocation.md
│   ├── rehearsal.md
│   ├── feedback.md
│   ├── codification.md
│   └── proving.md
│
├── reference/
│   ├── index.md
│   ├── cli.md
│   ├── commands/
│   │   ├── run.md
│   │   ├── db.md
│   │   ├── routine.md
│   │   ├── api.md
│   │   ├── bind.md
│   │   ├── ping.md
│   │   ├── rule.md
│   │   ├── env.md
│   │   └── sys.md
│   ├── output.md
│   ├── exit-codes.md
│   ├── audit.md
│   └── errors.md
│
├── guides/
│   ├── index.md
│   ├── troubleshooting.md
│   ├── recovery.md
│   ├── migration.md
│   └── returning-to-capcli.md
│
└── concepts/
    ├── index.md
    ├── harness-and-capcli.md
    ├── sessions.md
    ├── provenance.md
    └── progressive-disclosure.md

This tree is the documentation architecture.

It is deliberately not a mirror of the CANS specification.

---

2. Why This Tree

The top-level areas answer different reader needs:

START       → "What is this, and can I use it?"
USE         → "I need to get something done."
UNDERSTAND  → "I want to understand what I'm working with."
AUTOMATE    → "I keep doing this."
AGENTS      → "I need an agent to operate it."
REFERENCE   → "I need the exact contract."
GUIDES      → "Something specific went wrong / I need to do something unusual."
CONCEPTS    → "I need to understand a deeper idea."

The reader should not have to understand the entire system before becoming productive.

---

3. "index.md"

The home page is the doorway.

It should answer:

«What can I do with this?»

It should not become an architecture lecture.

Suggested flow:

What you're trying to accomplish
        ↓
See Capcli doing something
        ↓
Install
        ↓
First useful task
        ↓
Understand what happened

Returning users should also have direct paths to:

Use
Reference
Agents
Guides

---

4. "start/"

"start/index.md"

The first-time entry point.

It should accommodate different starting situations:

Nothing established yet
        ↓
Something already exists
        ↓
Something needs to be understood
        ↓
Something needs to be done

Do not assume that every reader starts with an existing World.

---

"start/what-is-capcli.md"

Explain Capcli in human terms.

The minimum useful distinction:

«The harness reasons. Capcli provides the governed execution layer.»

Do not begin with SQLite, authorizers, budgets, or audit internals.

Those belong later.

---

"start/see-it.md"

The show-don't-tell page.

Let the reader see a useful Capcli interaction before explaining the machinery.

Every output shown here must be real and verified.

No invented IDs, hashes, timestamps, rows, URLs, or command output.

---

"start/install.md"

Installation should be treated as a bridge to usefulness.

The reader should not have to understand Capcli architecture before installing it.

Progressively reveal only what is necessary.

---

"start/first-task.md"

Get the reader to the first meaningful result.

The goal is:

«“I actually did something.”»

Not:

«“I completed the tutorial.”»

---

"start/what-just-happened.md"

Only now explain the pieces the reader just encountered.

This page is where the first deeper mental model can begin.

---

5. "use/"

This is the everyday working surface.

"use/discover.md"

How to find what is available.

Discovery comes before unnecessary memorization.

---

"use/inspect.md"

How to understand something before invoking it.

---

"use/run.md"

How to invoke an available capability.

Keep the human explanation simple; exact syntax belongs in Reference.

---

"use/work-with-your-data.md"

Introduce the reader's actual workspace/data progressively.

This is where the World concept can become useful.

The explanation should begin with:

«“What exists here?”»

and only then reveal the implementation underneath.

---

"use/boundaries.md"

Show what happens when Capcli does not allow an operation.

The reader should experience:

attempt
  ↓
decision
  ↓
explanation
  ↓
next action

A denial is not merely an error.

It is part of how the system communicates its boundary.

---

"use/audit.md"

Answer:

«“What actually happened?”»

Introduce audit through real questions:

- What happened?
- Who/what caused it?
- What was allowed?
- What was denied?
- What changed?

---

"use/recover.md"

Recovery belongs in normal use, not hidden as an emergency appendix.

Show that governed work includes the ability to understand and recover from changes.

---

6. "understand/"

This section exists for readers who want the mental model behind what they already experienced.

"understand/world.md"

Explain World without making World the explanation for everything.

Cover the useful idea:

«the governed workspace/state domain in which work happens.»

If the reader begins from nothing, this page should also explain that nothing may be established yet.

Do not invent a formal “Void state”.

“Void” may be used as explanatory language only.

---

"understand/structure.md"

Explain how something initially loose or exploratory can become explicit, structured, and inspectable.

This is where the documentation can gradually introduce schema and other concrete mechanisms.

Do not open with SQL.

---

"understand/capabilities.md"

Explain the common capability surface and why discovery/inspection/invocation exist.

---

"understand/effects.md"

Explain the difference between:

- an operation
- an effect
- an event
- recorded provenance

Use examples from verified Capcli behavior.

---

"understand/environments.md"

Explain dev, sim, and prod when the reader has a reason to separate exploration, rehearsal, and real operation.

---

"understand/identity.md"

Explain identity only when scope and accountability become useful.

---

"understand/budgets.md"

Explain resource governance after the reader understands why uncontrolled execution is a problem.

---

"understand/trust.md"

Explain draft, reviewed, and pinned only after the reader has experienced the need for evidence and progression.

---

"understand/recovery.md"

Deeper explanation of recovery mechanics.

---

7. "automate/"

Automation should emerge from repetition.

The reader should first think:

«“I keep doing this.”»

Then:

«“Can this become a routine?”»

"automate/repetition.md"

Recognize repeated useful work.

---

"automate/routines.md"

Introduce routines as the mechanism for repeatable procedures.

---

"automate/rehearsal.md"

Show how to rehearse work before relying on it.

---

"automate/proving.md"

Explain evidence required to establish confidence.

---

"automate/promotion.md"

Explain progression from exploratory work toward more trusted operation.

---

"automate/operation.md"

Explain ongoing operation, monitoring, change, recovery, and eventual subtraction.

---

8. "agents/"

This is the machine-facing surface.

It should be precise rather than conversational.

"agents/contract.md"

Define the actual agent/Capcli boundary.

Explicitly preserve:

Harness
  = cognition / reasoning

Capcli
  = governed execution

Kernel
  = mechanical enforcement / dispatch / audit

Do not collapse these into one thing.

---

"agents/discovery.md"

The machine discovery contract.

---

"agents/inspection.md"

The machine inspection contract.

---

"agents/invocation.md"

The machine invocation contract.

The fundamental capability path is:

DISCOVER
   ↓
INSPECT
   ↓
INVOKE

---

"agents/rehearsal.md"

How an agent can establish what will happen before real execution where the contract supports it.

---

"agents/feedback.md"

How the agent should respond to outcomes, denials, and evidence.

---

"agents/codification.md"

How repeated useful behavior becomes codified where the specification supports it.

---

"agents/proving.md"

How an agent establishes evidence for trusted operation.

---

9. "reference/"

Reference is where exactness wins over pedagogy.

"reference/cli.md"

Canonical CLI grammar.

capcli <noun> <verb> [target] [--flags]

Only document commands supported by the actual specification/implementation.

---

"reference/commands/"

One file per actual CLI noun:

run
db
routine
api
bind
ping
rule
env
sys

No invented commands.

No commands copied from an illustrative playbook unless independently verified.

---

"reference/output.md"

Exact output contracts.

Where human output and machine-readable output differ, document the real behavior.

---

"reference/exit-codes.md"

Exact documented exit codes and their meanings.

---

"reference/audit.md"

Exact audit structures and inspection surfaces.

---

"reference/errors.md"

Exact documented errors/denials.

Do not manufacture error codes to make examples look complete.

---

10. "guides/"

Guides solve specific problems without forcing readers through the main journey.

"guides/troubleshooting.md"

Problem → diagnosis → evidence → remediation.

---

"guides/recovery.md"

Practical recovery procedures.

---

"guides/migration.md"

Practical schema/world evolution procedures supported by the implementation.

---

"guides/returning-to-capcli.md"

For people who used Capcli before and are coming back.

The first question is not:

«“What is Capcli?”»

It is:

«“Where do I pick up?”»

---

11. "concepts/"

Deep concepts that are useful across multiple journeys.

"concepts/harness-and-capcli.md"

The boundary between cognition and governed execution.

This page should explicitly prevent the common misconception:

«Capcli is not the harness.»

---

"concepts/sessions.md"

Introduce sessions only when the reader needs execution scope.

Human-facing explanation:

«A session is Capcli's temporary scope for a piece of governed work.»

Agent-facing material can provide the exact kernel-issued semantics defined by the specification.

Do not make sessions part of the first-time experience.

---

"concepts/provenance.md"

Explain how actions can be connected to their origin and history.

---

"concepts/progressive-disclosure.md"

Internal documentation-authoring guidance.

This page does not need to be exposed as a major user-facing concept.

---

12. Page-Level Teaching Pattern

Most explanatory pages should follow:

1. What are you trying to do?
           ↓
2. Show the result / behavior
           ↓
3. What happened?
           ↓
4. Why does it matter?
           ↓
5. Simple mental model
           ↓
6. Relevant mechanism
           ↓
7. Try it
           ↓
8. Failure / boundary / recovery
           ↓
9. Go deeper
           ↓
10. Exact reference

The deeper the reader goes, the more precise the language becomes.

---

13. Journey Shape

The overall experience should quietly move through:

nothing yet
    ↓
something worth doing
    ↓
something becomes concrete
    ↓
see what exists
    ↓
act
    ↓
encounter boundaries
    ↓
understand the result
    ↓
observe history
    ↓
repeat useful work
    ↓
rehearse
    ↓
prove
    ↓
delegate
    ↓
operate
    ↓
recover / change / subtract
    ↓
return later

This is a documentation journey, not a new Capcli lifecycle.

Do not expose it to the reader as a formal product state machine.

---

14. Hard Authoring Rules

Rule 1 — CANS remains the factual authority

The documentation architecture does not redefine Capcli.

Rule 2 — Playbooks are stories

A playbook can demonstrate a journey.

It cannot silently define new Capcli commands, states, APIs, outputs, error codes, or terminology.

Rule 3 — Never fabricate output

No fictional:

- IDs
- timestamps
- hashes
- versions
- URLs
- rows
- metrics
- token counts
- audit records
- error codes
- command output

Rule 4 — Don't start with implementation

Start with the reader's problem.

Reveal implementation when it explains observed behavior.

Rule 5 — Don't make World everything

World is important, but it is one concept among many.

The reader may start with nothing, an existing workspace, a capability, a task, an agent, or a recovery problem.

Rule 6 — Don't introduce concepts before their reason exists

Especially:

- sessions
- budgets
- trust
- environments
- routines
- audit internals

Rule 7 — Keep harness and Capcli separate

Never describe Capcli as the reasoning harness.

Rule 8 — Human and agent documentation are different surfaces

Humans need progressive explanation.

Agents need exact contracts.

Do not sacrifice either one by mixing them into a single page.

---

15. The One-Sentence Test

Before publishing any page, ask:

«Why does the reader need this page right now?»

If the answer is unclear, the page probably belongs later, should be merged, or should not exist.

The documentation should always move the reader from:

«“I don't know what this is.”»

toward:

«“I know what I can do next.”»