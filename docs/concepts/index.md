# Concepts

The theory layer: how capcli's enforcement actually works. Each file is the single source of truth for its mechanism.

| Read | When you want to understand… |
|---|---|
| [trust-engine.md](trust-engine.md) | …why code starts untrusted and how it earns the right to run unattended (draft → reviewed → pinned). |
| [authorizer.md](authorizer.md) | …how every SQL statement is intercepted at three layers before it can touch a row. |
| [sandboxing.md](sandboxing.md) | …Tier 1 vs Tier 2 hosts, the network jail, and why pinned execution demands Linux. |
| [compiler.md](compiler.md) | …why YAML is compiled like code, and the five gates every schema must survive. |
| [memory-spine.md](memory-spine.md) | …the immutable audit ledger, the hash chain, and causal-DAG forensics. |
| [budgets.md](budgets.md) | …the min() cascade, dual-rate windows, quota earmarks, and clean yielding. |
| [environments.md](environments.md) | …dev / sim / prod isolation, data masking (FPA), and historical replay. |
| [identity.md](identity.md) | …the 4-link identity chain, scoped views, and the two-tier secrets vault. |
| [recovery.md](recovery.md) | …hot snapshots, dual storage, WORM anchoring, and break-glass mode. |

New here? Start with [trust-engine.md](trust-engine.md) and [authorizer.md](authorizer.md) — everything else enforces what those two define. For step-by-step doing, see [workflows](../workflows/index.md); for every number and exit code, see [reference](../reference/index.md).
