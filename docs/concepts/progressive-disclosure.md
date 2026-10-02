# Progressive Disclosure

*(Internal authoring guidance — why these docs reveal things as late as they do. Not a user-facing concept, kept in-tree because doc authors are users too.)*

---

## The rule

Reveal a mechanism **only after the reader has felt it push back.**

A reader who has been denied by the AST does not need to be *told* the AST matters — they have the `exit 2` receipt. A reader who has not yet been denied will experience any explanation of the AST as a lecture with no referent. Same information, opposite effect, and the only variable is *sequence*.

This is why the docs' journey shape is:

```
see it → do it → hit a wall → understand the wall → act again → deepen
```

...and not: "Chapter 1: The Authorizer."

## The four authoring moves

1. **Problem first.** Every page opens with the reader's situation, never with the machinery. The machinery is the *answer*, and answers go after questions.
2. **Mechanism at the moment of observed behavior.** We explain `sqlite3_prepare_v2` exactly when the reader wonders "how did the SQL never reach SQLite?" — not one page earlier.
3. **Precision increases with depth.** Start pages speak in metaphors (bank teller, toddler, raccoon). Reference pages speak in exit codes and field names. Both are honest; they're pitched at different altitudes of the same mountain.
4. **The One-Sentence Test before publishing:** *why does the reader need this page right now?* If the answer is "to appreciate the architecture," the page is a lecture in disguise and gets merged, moved later, or deleted.

## Concepts with a *reason gate*

Never introduce before the need exists:

| Concept | Its reason (must be experienced first) |
|---|---|
| Sessions | You felt budget/accountability edges |
| Budgets | You felt a yield or an ops denial |
| Trust rungs | You got denied for being `draft` |
| Environments | You needed to not-email-real-customers |
| Audit internals | You asked "what actually happened?" |

A concept introduced before its reason is trivia. The same concept introduced after its reason is *relief*.

## What this looks like in practice

Compare the same fact at two altitudes:

> **Start:** "Capcli said no. Not 'are you sure?' *No.*"

> **Understand:** "The C authorizer killed it at `sqlite3_prepare_v2`. State untouched."

> **Reference:** "`exit 2` · `policy.query.update_delete.require_where` · `state_modified: false` · `remedy: add WHERE + LIMIT`"

Three true statements, three altitudes, one reader journey. Pick the altitude for the page you're writing; never blend them into a single page and call it "completeness."

---

**The master plan** → [../doc.md](../doc.md) · **Section doorways** → [../index.md](../index.md)
