# Progressive Disclosure

You found the maintenance corridor. It's fine. It's clean in here.

This page is for people *writing* Capcli documentation, not people using Capcli. If you wandered in from the concepts shelf expecting another deep idea — the deep idea is this: the pages you just came from are shaped the way they are on purpose, and this page explains the shaping.

---

## The principle

**Reveal machinery only when it explains observed behavior.**

A reader who has just watched a denial doesn't need the C authorizer explained — they need the denial decoded. A reader who hasn't run anything yet doesn't need sessions, budgets, or the trust ladder. Every mechanism mentioned before its moment is a tax on a reader who hasn't been paid a reason to care.

So each page starts with the reader's problem, shows the result, and only then lifts the hood — and only as high as the observed behavior demands.

---

## The journey shape

The documentation quietly moves a reader through:

```
nothing yet → something worth doing → something becomes concrete →
see what exists → act → encounter boundaries → understand the result →
observe history → repeat useful work → rehearse → prove → delegate →
operate → recover / change / subtract → return later
```

Three rules about that shape:

1. **It's a documentation journey, not a product state machine.** No reader should ever meet it as a diagram of "Capcli lifecycle stages."
2. **It's quiet.** The reader should feel progression, not signage.
3. **Readers enter anywhere.** The shape exists so each page knows what a reader has probably already seen — start pages assume less, understand pages assume more, reference pages assume precision.

---

## The One-Sentence Test

Before publishing any page, ask:

**«Why does the reader need this page right now?»**

If the answer is unclear, the page belongs later, belongs merged into another page, or doesn't belong. This test kills more pages than it publishes — which is the point.

---

## Hard rules digest

The full authoring law lives in `docs/doc.md`. The digest:

1. **CANS is the factual authority.** The documentation architecture doesn't redefine Capcli. Specs win.
2. **Playbooks are stories.** A journey can demonstrate Capcli; it cannot invent commands, states, outputs, or error codes.
3. **Never fabricate output.** No fictional IDs, hashes, timestamps, rows, metrics, or exit codes. Every transcript is complete: command, output, decode.
4. **Start with the reader's problem.** Not the implementation. Not the architecture.
5. **World is one concept among many.** Not the explanation for everything.
6. **No concept before its reason exists.** Especially sessions, budgets, trust, environments, routines, and audit internals.
7. **Harness and Capcli stay separate.** Capcli is never described as the reasoning harness.
8. **Human and agent docs are different surfaces.** Humans get progressive explanation; agents get exact contracts. Mixing them shortchanges both.

---

## The page-level rhythm

Most explanatory pages run the same loop:

```
what are you trying to do? → show the behavior → what happened? →
why it matters → mental model → mechanism → try it →
failure / boundary / recovery → go deeper → exact reference
```

The deeper the reader goes, the more precise the language gets. Start pages may joke; reference pages may not.

---

## The wink

If you're a reader who got this far down a page that wasn't for you: notice you never needed this page to *use* Capcli. That's progressive disclosure applied to the documentation itself.

Every concept you did need arrived right after you watched it do something. That timing wasn't luck — it was the whole job.

Now back to the nice part of the building.

---

**Back to the concepts shelf** → [index.md](index.md)

**The journey, seen from the front door** → [../start/index.md](../start/index.md)

**The other surface: exact contracts for machines** → [../agents/index.md](../agents/index.md)
