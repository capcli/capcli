# Agents

This section is the machine-facing surface of Capcli. Humans read for understanding; agents read for contracts. The pages here stay precise, terse, and free of tutorial narration.

---

## The boundary

Three roles, three jobs, no overlap:

| Role | Owns | Never owns |
|---|---|---|
| **Harness** | Reasoning, planning, tool selection | Enforcement, state, secrets |
| **Capcli CLI** | Governed execution surface for a single invocation | Long-running cognition |
| **Kernel** | Mechanical enforcement, dispatch, audit | Intent, priorities, judgement |

An agent proposes work in language. Capcli translates that proposal into a bounded, recorded act — or refuses the translation. The kernel records the outcome either way.

---

## The capability path

Every agent interaction follows one path:

```
DISCOVER → INSPECT → INVOKE → OBSERVE
```

1. **Discover.** `capcli search "<intent>"` queries the unified registry. Results arrive as typed pointers: `cap://` for routines and API verbs, `db://` for tables, `doc://` for human documents, `prompt://` for agent campaign banks, `tpl://` for blueprints.
2. **Inspect.** `capcli inspect <ptr>` returns a single pre-flight envelope: parameters, limits, trust rung, budget headroom, and a boolean `can_invoke_now` verdict. One call, zero roundtrips.
3. **Invoke.** `capcli run <capability> [-p k=v]` executes inside a budget frame. Mutating work carries a causal intent (`-m "<why>"`).
4. **Observe.** `capcli sys audit tail` and `capcli sys audit trace <op-id>` expose the recorded result, including the denial anatomy for refused work.

Agents pass `--json` on the hot path. Humans receive tables; machines receive envelopes. The data underneath is identical.

---

## Reading surfaces

The `doc` noun is the single reading surface for both document schemes:

| Scheme | Addresses | Read with |
|---|---|---|
| `doc://` | Human completeness pages (this tree) | `capcli doc read doc://<path> [--max-tokens 100]` |
| `prompt://` | Agent campaign banks, one action-sized leaf at a time | `capcli doc read prompt://<bank>/<slug>@<version>#<node>` |

`capcli doc outline <ptr>` returns the node tree for either scheme. A fragment (`#<node>`) selects exactly one outline node. Token budgets default to 100 per read and cap at 500 per leaf.

---

## Identity in one paragraph

A principal holds authority. An agent is a registered harness instance acting for a principal. A session scopes one engagement, and every leaf execution inside it lands in the causal audit DAG under a kernel-issued identity. Agents never self-declare identity; the kernel mints session tokens and binds them to the active budget frame and workspace.

---

## Pages in this section

| Page | Contract |
|---|---|
| [codification.md](codification.md) | How repeated behaviour becomes a governed routine |

Deeper human explanation of the same machinery lives under [Understand](../understand/index.md). Everyday worked examples live under [Use](../use/index.md).
