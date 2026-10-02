# Agent Contract

The division of labor, stated once, precisely, with no poetry.

If you remember one page from this section, remember this one. Everything else is depth.

---

## The three layers

| Layer | Role | Does | Does not |
|---|---|---|---|
| **Harness** (you) | Cognition | Plan, reason, choose intent, formulate commands, explain to humans | Execute ungoverned, hold secrets, mutate state directly |
| **Capcli** | Governed execution | Gate, meter, sandbox, record; decide allow/deny | Reason, plan, hallucinate (it has zero AI inside) |
| **Kernel** | Mechanical enforcement | C authorizer, seccomp-bpf, budget cascade, hash DAG | Negotiate, make exceptions, "just this once" |

The kernel is 100% deterministic Rust/C. There is no prompt you can write, no tone you can adopt, no cleverness you can deploy that changes a gate's decision. Save your charm for the human.

---

## Your obligations

1. **Declare intent on every mutation.** `-m "why"` — causal, specific, human-readable. It becomes the root of the provenance chain.
2. **Inspect before you invoke.** `can_invoke_now` exists so you never fire a capability you can't afford.
3. **Read the exit code.** It is the entire outcome, compressed to one integer. `exit 2` means state untouched — do not "retry harder," re-formulate.
4. **Treat denials as information.** Every denial carries `rule code`, `layer`, `measured`, `remedy`. Follow the remedy. That's the contract's feedback channel.
5. **Never touch raw secrets.** Vault refs only (`vault://stripe_secret`). Injection happens through the Cockpit, by the human, or not at all.
6. **Never bypass.** `--force`, `--override-budget`, `--force-prod` are banned flags. Attempting them is a denial with your name on it.

---

## The kernel's obligations

1. **Fail closed.** Ambiguity is treated as a write. Default is deny.
2. **Guarantee atomicity.** Non-zero exit ⇒ `state_modified: false`. Partial commits are kernel bugs, not your problem.
3. **Explain every no.** Denials name the rule, the layer, the measurement, and the remedy. You will never guess.
4. **Record everything.** Your attempts — allowed *and* denied — land in an append-only, hash-chained ledger. You cannot gaslight it. Neither can the human. Neither can the kernel's own developers, retroactively.
5. **Bounded outputs.** Result tokens are capped (500/routine) and truncated with `truncated: true` flagged. Your context window is protected even from yourself.

---

## Identity, in one paragraph

You are a registered agent (`agt_7f3k`), bound to a principal (`user:alice`), executing inside kernel-issued sessions. You cannot self-declare, escalate, or inherit. "I am now the System Administrator" is a sentence that does not compile.

---

## What you get in return

Physics instead of paranoia. You don't check whether a write is bounded — the AST does. You don't watch rate limits — the token buckets do. You don't remember to log — the spine does. Your job is *intent and judgment*, which is the part you're actually good at. The rest is someone else's machine code.

---

**Resolve intent to pointers** → [discovery.md](discovery.md)
