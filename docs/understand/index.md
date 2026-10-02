# Understand

You've run things. You've hit walls. You've probably restored a snapshot at least once. The daily loop works.

Now you want the model underneath the moves. This section is where the pieces you've already touched get names, edges, and a little physics.

---

## Pick your mental model

| You're wondering… | Start here |
|---|---|
| Where does my state actually live? | [world.md](world.md) |
| How does loose exploration become structure? | [structure.md](structure.md) |
| What counts as a capability — and why only one surface? | [capabilities.md](capabilities.md) |
| Op, effect, event, provenance — which is which? | [effects.md](effects.md) |
| Why do dev, sim, and prod exist? | [environments.md](environments.md) |
| Who is accountable for what? | [identity.md](identity.md) |
| Why did execution park instead of crash? | [budgets.md](budgets.md) |
| Why can't this routine touch prod yet? | [trust.md](trust.md) |
| How do snapshots, restores, and break-glass work? | [recovery.md](recovery.md) |
| How does the ledger stay honest? | [audit.md](audit.md) |

---

## Two axes, if you only keep two ideas

**Trust bounds capabilities** (`draft` → `reviewed` → `pinned`). **Environments bound state** (`dev` → `sim` → `prod`). Most of what Capcli allows or denies is one of those two axes doing its job.

Building the model from scratch? Read in order: world → structure → capabilities → effects. Then jump anywhere. Every other page is depth, not prerequisite.

---

## The one rule for this section

**Nothing here is required to use Capcli. It's required to predict it.**

You can run the daily loop — discover, inspect, run, observe — for months without knowing what a causal DAG is. But the night something behaves strangely at 03:00, this is the section you'll wish you'd read.

---

**Start at the ground floor** → [world.md](world.md)

**Skip straight to the machinery** → [capabilities.md](capabilities.md)
