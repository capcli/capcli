# Living World Architecture

### A protocol architecture for autonomous software, organizations, and physical systems

---

## Abstract

Living World Architecture defines a system model in which autonomous agents, humans, services, and physical systems operate within a shared, durable world.

The world is composed of **identities, facts, events, authority, capabilities, policies, goals, and commitments**. Domain-specific **Living Services** own authoritative state and expose capabilities through a common **World Protocol**. Local databases are implementation-level projections of world state rather than the global source of truth.

Agents reason over world context and pursue goals. Agents receive no arbitrary database access. Agents act through capabilities, under explicit policy and delegated authority. Every consequential action produces auditable world events.

The architecture supports:

* autonomous and multi-agent operation
* independent domain ownership
* deterministic authorization around probabilistic reasoning
* distributed state without shared databases
* incremental schema and organization evolution
* human and machine participation in one world
* simulation and counterfactual planning
* digital and physical execution
* inter-organization interoperability through zero-trust gateways

The central model is:

> **Reality → World State → Goal → Reasoning → Capability → Policy → Action → Event**

A production system implementing this model is defined by the coherent world and the contracts through which participants act within it. UI, backend, and database are implementation choices.

---

# 1. Architecture

A Living World consists of a small common substrate and independently owned domains.

```text
                         LIVING WORLD
                              │
                    ┌─────────┴─────────┐
                    │   WORLD PROTOCOL  │
                    └─────────┬─────────┘
                              │
       ┌──────────────────────┼──────────────────────┐
       │                      │                      │
       ▼                      ▼                      ▼
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│ Order        │       │ Payment      │       │ Inventory    │
│ Service      │       │ Service      │       │ Service      │
│              │       │              │       │              │
│ Agent        │       │ Agent        │       │ Agent        │
│ Capabilities │       │ Capabilities │       │ Capabilities │
│ Policies     │       │ Policies     │       │ Policies     │
│ State        │       │ State        │       │ State        │
│ Local DB     │       │ Local DB     │       │ Local DB     │
└──────────────┘       └──────────────┘       └──────────────┘
```

The World Protocol provides interoperability inside one trust boundary.

The World Kernel provides the minimum trusted substrate:

```text
identity
authority
event history
capability registry
delegation
time
global invariants
```

Everything else remains decentralized.

Execution runs on two paths:

```text
Fast path
  deterministic rules and scripts
  routine actions
  zero model inference

Slow path
  agent reasoning
  full capability loop
  edge cases, failures, novel states
```

Routine volume stays on the fast path. Model inference is reserved for work that requires reasoning.

Path assignment is a property of the capability. Each capability declares `fast` or `slow` in its registry entry. A fast-path execution passes the same policy check and appends the same canonical event as a slow-path execution; the fast path carries no reasoning step. A fast-path execution that fails its policy check, hits an unhandled state, or exhausts its declared retry bound escalates to the slow path. Escalation is a world event.

---

# 2. Core Primitives

## 2.1 Identity

Every durable entity has a globally addressable identity inside its world.

```text
customer:cus_01928
order:ord_9182
payment:pay_771
warehouse:wh_03
agent:procurement-7
```

Local databases use arbitrary local identifiers. World references remain stable.

Identity merges are explicit and historical:

```text
CustomerMerged
  from: customer:old_819
  into: customer:cus_01928
```

**Invariant:** identity is global inside the world; representation is local.

Agent identity is cryptographic, not textual. A string identifier names an agent for reference. Authority travels in short-lived signed capability tokens, detailed in Section 8.

---

## 2.2 Facts

Facts describe the current or historical state of the world.

```text
Payment.pay_771.amount = 4200
Order.ord_9182.customer = cus_01928
Inventory.A42.available = 137
```

A fact carries:

```text
subject
predicate
value
authority
valid_time
observed_time
provenance
epistemic_status
```

Epistemic status distinguishes:

```text
observed
inferred
proposed
canonical
disputed
deprecated
```

An agent inference carries `proposed` or `inferred` status until the owning authority establishes it as `canonical`. Generation alone confers no authority.

Domains own local schemas. The kernel carries identity, authority, provenance, and epistemic status. Domain semantics travel in local form and pass through translators at domain boundaries, detailed in Section 3.

---

## 2.3 Events

Events record changes that occurred in the world.

```text
OrderCreated
PaymentAuthorized
InventoryReserved
ShipmentDispatched
CustomerMerged
CreditLimitChanged
```

Events are semantic. Events expose no database implementation.

An event is consumable by services using completely different storage technologies.

The canonical event log records policy-cleared capability executions and their resulting state transitions. Reasoning traces, hypotheses, and simulations live in separate ephemeral storage, detailed in Section 9.

---

## 2.4 Capabilities

A capability represents an executable operation.

```text
order.submit
payment.authorize
inventory.reserve
refund.issue
shipment.dispatch
purchase.create
```

Capabilities are the only execution surface. Unrestricted application access does not exist in the model.

Every consequential action follows:

```text
Agent
  ↓
Capability
  ↓
Policy
  ↓
State Transition
  ↓
Event
```

Capabilities are invisible by default. The registry has no public enumeration endpoint. An agent receives a capability only against a signed intent ticket from an authorized orchestrator, detailed in Section 8.

---

## 2.5 Policies

Policies define the conditions under which capabilities execute.

Example:

```text
payment.authorize

ALLOW IF:

identity.valid
AND order.status = submitted
AND amount = order.total
AND idempotency_key.unused
```

Policies are deterministic and independently auditable.

**Rule:** reasoning is probabilistic; authorization is deterministic.

Policy carries two layers:

```text
Static rules
  binary conditions on the single action

Blast-radius caps
  aggregate limits across time and volume
  rate limits per actor and capability
  daily and hourly spend ceilings
  velocity and anomaly thresholds against actor baseline
```

An action that passes static rules and breaches an aggregate cap is throttled or denied. Authorization evaluates the action and the pattern.

The actor baseline is a rolling 30-day window per actor and capability: action rate, aggregate value, counterparty spread, and failure rate. Deviation beyond the capability's declared threshold triggers throttling first, denial second, human review third.

---

## 2.6 Goals

Goals define desired outcomes.

```text
Goal:
Fulfill order:ord_9182

Constraints:
delivery < 48h
cost < $120
customer_sla > 0.99
```

Goals are hierarchical. Goals conflict. Conflict resolution operates through policy, priority, and human authority.

Agents optimize within assigned authority and constraints.

---

## 2.7 Commitments

Commitments represent obligations between participants.

```text
Commitment {
  owner
  beneficiary
  obligation
  conditions
  deadline
  evidence
}
```

Example:

```text
supplier:S7
commits:
10,000 units
by 2026-10-14
at $4.10/unit
```

Cross-domain and cross-organization commitments carry escrow, detailed in Section 10. A commitment without locked value or a programmatic unwind path is a record, not an enforceable obligation.

Commitments support autonomous procurement, contracts, logistics, service levels, and inter-company coordination.

---

# 3. Living Services

A Living Service is an autonomous domain with:

```text
identity
authority
agent(s)
capabilities
policies
local state
event processing
memory
observability
```

A Living Service owns the authoritative facts for its domain.

| Domain    | Authoritative facts            |
| --------- | ------------------------------ |
| Order     | status, total, customer        |
| Payment   | authorization, charge, refund  |
| Inventory | quantity, reservation          |
| Shipping  | route, carrier, shipment state |
| Credit    | credit limit, eligibility      |

Services share no operational databases.

Services share world identities, semantic events, capabilities, and authority rules inside one trust boundary.

Each domain owns its local schema. Cross-domain traffic passes through a translator at the boundary:

```text
Domain A local event
  ↓
Boundary translator
  ↓
World Protocol envelope
  identity, authority, provenance, epistemic status
  ↓
Domain B local projection
```

Translation is schema-on-read. No global domain ontology exists. The kernel envelope is fixed and minimal; domain semantics evolve independently on each side of a translator.

---

# 4. Authority and Provenance

A world distinguishes truth from belief.

Every significant fact has an authority.

```text
Payment.status      → Payment Service
Inventory.quantity  → Inventory Service
Shipment.location   → Logistics Service
```

Derived facts retain their evidence.

```text
Claim:
customer:cus_19 is strategic

Evidence:
  contracts
  invoices
  meetings
  payment history

Derived by:
sales-agent:v7

Status:
proposed
```

A canonical fact is established only through the appropriate authority.

The traceable chain is:

```text
Evidence → Derivation → Claim → Authority → Canonical Fact
```

---

# 5. Agency and Memory

Agents are first-class world participants.

An agent has:

```text
identity
owner
version
authority
capabilities
lifecycle state
memory
```

Agent memory is separate from canonical world truth.

Four memory classes:

```text
World memory       what happened
Domain memory      what the service knows
Episodic memory    previous tasks and interactions
Procedural memory  strategies that have worked
```

An agent remembers:

> “Supplier A usually delivers early.”

The world independently verifies whether Supplier A delivered early.

A new agent enters a domain through JIT hydration:

```text
1. Scoped capability manifest
   only the capabilities issued to that agent
2. Strict input and output schemas per capability
3. Three deterministic execution examples per capability
```

The agent runs in a dry-run sandbox projection until five simulated capability executions succeed. Live event log access opens after sandbox clearance.

Reasoning over a world fact runs under an optimistic lease, detailed in Section 9.

---

# 6. Human Participation

Humans are authorized participants, not external workflow exceptions.

A human exercises:

```text
approve
reject
delegate
override
teach
correct
revoke
```

Example:

```text
Agent
  ↓
purchase.approve
  ↓
Human authority
  ↓
PurchaseApproved
```

The decision and evidence become part of world history.

Human judgment also produces policy change:

```text
Human correction
  ↓
Policy proposal
  ↓
Governance
  ↓
Policy activation
```

Negotiation escalation, taint clearance, and blast-radius overrides terminate in the human queue. The human decision is a world event with full provenance.

---

# 7. Governance

Operating authority and constitutional authority are separate.

### Operating capabilities

```text
purchase.create
payment.authorize
shipment.dispatch
```

### Governance capabilities

```text
capability.create
policy.create
authority.transfer
agent.promote
ontology.change
```

Governance operations require stronger authorization than operating operations.

An agent exercises delegated authority. Delegated authority carries no power to enlarge itself.

**Rule:** autonomy operates within the constitution; autonomy does not rewrite the constitution.

---

# 8. Security

All consequential actions carry explicit authority context.

```json
{
  "actor": "agent:procurement-7",
  "acting_for": "department:manufacturing",
  "capability": "purchase.create",
  "object": "purchase:9182",
  "limits": {
    "amount": 25000,
    "currency": "USD"
  },
  "expires_at": "2026-10-07T18:00:00Z"
}
```

Authority transport is cryptographic:

```text
Ephemeral mutual TLS between participants
Hardware-backed signing keys (TPM or HSM)
Short-lived capability tokens (macaroons)
  time-to-live under 60 seconds
  single-use nonce
  caveats bound to actor, capability, object, limits
```

Revocation is expiry. No revocation broadcast exists. A compromised token dies within its time-to-live, and every cross-domain call presents a fresh token.

Delegation narrows monotonically. A token issued down a delegation chain carries caveats equal to or narrower than its parent token: lower value limits, shorter time-to-live, equal or smaller capability set. Chain depth is a caveat. No hop widens any dimension.

The capability registry is dark:

```text
No public capability enumeration
No discovery endpoint
Capability issuance against a signed intent ticket only
No ticket, no knowledge of the capability
Orchestrators receive their issuing scope through governance,
  out of band, under governance capabilities
```

Context handling carries taint:

```text
External documents, mail, invoices, and tool output enter as tainted
Reasoning over tainted context marks the session tainted
High-risk capabilities (payout, export, authority change) block on taint
Human clearance removes the taint flag
The clearance is a world event
Taint inherits across agent-to-agent messages
  a brief, summary, or instruction derived from tainted reasoning
  carries the taint flag into the receiving session
```

Security guarantees:

* no authority from prompts
* no authority from untrusted documents
* scoped delegation
* capability expiry in seconds
* domain isolation
* immutable audit history
* explicit cross-domain authorization
* taint blocking on high-risk capabilities

Context influences reasoning.

**Context grants no authority.**

---

# 9. Time, History, and Storage

World state preserves both the time a fact was true and the time the fact became known.

```text
Shipment.location = Singapore

valid_time:
2026-10-05 14:00

observed_time:
2026-10-05 14:07
```

This supports:

* audit
* historical reconstruction
* delayed observations
* temporal policy
* forecasting
* dispute resolution

The system distinguishes:

```text
actual state
historical state
observed state
predicted state
agent belief
```

Storage is split by epistemic class:

```text
Canonical event log
  policy-cleared capability executions
  state transitions
  commitments, escrows, human decisions
  immutable, permanent

Ephemeral store
  reasoning traces
  hypotheses
  simulation branches
  agent belief
  30-day time-to-live, cheap storage
```

Only a policy-cleared execution appends to the canonical log.

Reasoning over facts runs under an optimistic lease set:

```text
Agent reads facts at state versions V1..Vn (vector clocks)
  ↓
Kernel issues lease set, 30-second bound, renewable while reasoning runs
  ↓
Any leased fact changes during reasoning
  ↓
Kernel cancels execution and interrupts inference
  ↓
Agent rehydrates at the new versions
```

A lease set spans domains. Each domain validates its own vector clock segment. One changed segment invalidates the set. Lease expiry without renewal cancels the run under the same rule.

Staleness fails fast at the lease. Tokens stop at cancellation, not at the policy checkpoint.

Observability storage follows the same split. A successful execution records:

```text
inputs
context snapshot hash
tool outputs
model identifier and endpoint version
model seed
temperature
final event hash
```

Full reasoning traces persist on failure only, under a 180-day retention in the ephemeral store. The failure record in the canonical log is permanent and carries the trace hash.

A replay record captures the complete reasoning input surface:

```text
inputs
context snapshot
tool outputs
model identifier and endpoint version
model seed
temperature
final event hash
```

Replay runs in a deterministic replay container against the pinned model endpoint and the captured tool outputs. No live tool executes during replay. The replay reproduces the recorded trace from captured inputs; a model endpoint that no longer exists renders the trace archival, and the canonical failure record states that status.

---

# 10. Negotiation and Commitments

Autonomous services interact beyond request and response.

Negotiation is a first-class protocol.

```text
Need:
10,000 units
≤ $4.00
delivery ≤ 7 days

Offer:
$4.20 / 5 days

Counter:
$4.00 / 7 days

Accepted
```

Negotiation carries hard bounds:

```text
Maximum 3 rounds
Hard time-to-live in seconds
No convergence → abort
Abort trace → human review queue
```

The negotiation terminates in a formal commitment or capability invocation.

```text
Negotiation
    ↓
Agreement
    ↓
Commitment
    ↓
Capability
    ↓
Execution
```

Cross-domain commitment execution runs through escrow:

```text
Agreement
  ↓
Funds or assets lock in a stateful escrow contract
  ↓
Counterparty executes
  ↓
Signed proof-of-execution event arrives before deadline
  ↓
Escrow releases

Deadline passes without proof
  ↓
Escrow unwinds automatically
```

Escrow custody inside one world sits in the kernel escrow service. The kernel holds locked funds; a domain holds locked physical goods as a reservation under its own authority, and the escrow contract references the reservation identity. Release consumes the reservation. Unwind releases it.

Repeated counterparties clear bilaterally: commitments net against each other inside a clearing window, and escrow locks the net position. The clearing record is a canonical event.

No cross-domain flow relies on a bare promise. Locked value and a programmatic timeout carry every multi-party execution across failure, crash, and non-cooperation.

This enables autonomous procurement, logistics, resource allocation, and inter-company commerce.

---

# 11. Simulation

The world branches into hypothetical states.

```text
                    REAL WORLD
                         │
                       branch
             ┌───────────┴───────────┐
             ▼                       ▼
       Scenario A               Scenario B
       price +5%                price +10%
             │                       │
          simulate                simulate
             │                       │
             └───────────┬───────────┘
                         ▼
                    evaluate
                         │
                         ▼
                       commit
```

Agents evaluate plans before committing actions to reality.

Simulation branches live in the ephemeral store. A simulation enters the canonical log only through an explicit commit executed as a policy-cleared capability.

Simulation is a native world operation, not an isolated analytics product.

---

# 12. Physical Execution

Physical operations are represented as capabilities.

```text
robot.pick
robot.move
machine.start
truck.dispatch
warehouse.open
machine.shutdown
```

A physical capability carries additional safety constraints:

```text
certification
location
operating envelope
interlocks
human safety
energy limits
```

The resulting event confirms physical state:

```text
RobotMoved
ItemPicked
TruckDispatched
MachineStopped
```

The architecture spans software and physical systems under one world model.

---

# 13. World Evolution

World structure becomes more formal without discarding history.

A discovered structure progresses through:

```text
Observed
   ↓
Hypothesis
   ↓
Proposed
   ↓
Experimental
   ↓
Canonical
   ↓
Deprecated
```

Examples:

```text
new entity
new relationship
new capability
new policy
new domain authority
```

Domain schema evolution is local. Translators at domain boundaries absorb schema change on read. No global ontology negotiation gates a domain release.

Local database migration is an implementation concern.

World evolution is a semantic concern.

```text
World event
    │
    ├── Service A updates schema
    ├── Service B ignores it
    └── Service C creates a projection
```

**World migration and database migration are separate operations.**

---

# 14. Consistency

Consistency follows the nature of the fact.

| World property        | Consistency          |
| --------------------- | -------------------- |
| Money                 | Strong               |
| Ownership             | Strong               |
| Identity              | Strong               |
| Authorization         | Strong               |
| Inventory reservation | Strong               |
| Domain state          | Domain-authoritative |
| Search                | Eventual             |
| Analytics             | Eventual             |
| Forecast              | Probabilistic        |
| Agent hypothesis      | Epistemic            |

No single global consistency model exists in the architecture.

Eventual projections create ghost-read risk. The optimistic lease in Section 9 closes that risk at reasoning time: decisions run against a leased state version, and a version change cancels the run.

---

# 15. Production Failure Model

Distributed autonomy retains distributed failure.

Production systems carry:

```text
idempotency
timeouts
retries
deduplication
ordering
leases
compensation
sagas
dead-letter handling
backpressure
rate limits
circuit breakers
```

Example:

```text
PaymentAuthorized
       ↓
InventoryReservationFailed
       ↓
compensation policy
       │
       ├── retry
       ├── wait
       ├── alternative warehouse
       └── refund
```

Cross-domain sagas terminate in escrow unwind on deadline, per Section 10. No saga holds locked value indefinitely.

Agents choose among valid recovery strategies.

The infrastructure guarantees deterministic execution semantics.

---

# 16. Transport and Wire Format

Agent traffic runs on persistent bidirectional multiplexed streams:

```text
QUIC or WebTransport transport
Actor-style messaging, no request-response polling
Cap'n Proto frames with schema-hash headers
Self-describing frames: a frame carries its schema hash;
  an unknown schema resolves through the boundary translator
Capability query, negotiation, and execution in one round-trip
No statically compiled client stubs
```

Agents reason in tokens. The wire carries binary.

Domain capabilities, standard facts, and epistemic tags map to fixed bytecode identifiers:

```text
payment.authorize = 0x0F4A
```

Translation between bytecode and model-readable schema happens at the edge, at parameter generation. Network payload carries identifiers and values, not verbose semantic envelopes.

The kernel bytecode registry allocates identifier ranges per domain under governance authority. A domain assigns identifiers inside its own range. Gateways translate between organizations' identifier maps at the boundary; no cross-organization identifier space exists.

---

# 17. Reference Use Cases

## Autonomous Procurement

```text
Inventory detects shortage
        ↓
Procurement Agent
        ↓
supplier.search
quote.request
        ↓
Negotiation (3 rounds, hard time-to-live)
        ↓
purchase.create
        ↓
Policy (static rules + blast-radius caps)
        ↓
Commitment under escrow
```

No fixed supplier-specific workflow exists.

---

## Autonomous Finance

```text
Bank transaction
        ↓
Finance Agent
        ↓
invoice.match
contract.verify
tax.evaluate
        ↓
reconciliation.apply
        ↓
Policy
        ↓
Reconciled / ReviewRequired
```

Tainted source documents block payout capabilities until human clearance. The service accumulates organizational knowledge without turning agent memory into accounting truth.

---

## Autonomous Operations

```text
IncidentDetected
        ↓
Operations Agent
        ↓
inspect
diagnose
simulate
        ↓
deployment.rollback
        ↓
Policy
        ↓
Rollback
        ↓
Verification
        ↓
IncidentResolved
```

The resulting history becomes operational knowledge.

---

## Autonomous Manufacturing

```text
Demand Forecast
        ↓
Planning Agent
        ↓
inventory.reserve
machine.schedule
supplier.negotiate
robot.execute
        ↓
Production events
        ↓
continuous replanning
```

Software, suppliers, machines, and humans participate in one operational world.

---

## Company From Zero

A new company begins with:

```text
email
documents
payments
spreadsheets
messages
human decisions
```

Agents identify recurring entities, relationships, capabilities, and policies.

The organization formalizes its operating model incrementally, domain by domain, through local schemas and boundary translators. No complete enterprise schema gates day one.

---

# 18. World-Level Observability

Production observability follows the causal chain:

```text
Goal
 ↓
Observation
 ↓
Reasoning
 ↓
Capability
 ↓
Policy
 ↓
Action
 ↓
Event
 ↓
Result
```

A world trace answers:

```text
What was the objective?

What did the agent know?

Which evidence did it use?

What did it decide?

Which capability did it invoke?

Which policy authorized it?

What changed?

What other participants reacted?
```

Successful executions record inputs, model seed, temperature, and final event hash. Full traces persist on failure. Deterministic replay reproduces a trace on demand inside a replay container, from the captured context snapshot and tool outputs, against the pinned model endpoint. Engineers debug from replay, not from petabyte-scale stored graphs.

This is the minimum surface for debugging autonomous systems responsibly.

---

# 19. World Portability and Inter-Organization Exchange

World identity, facts, events, authority, and capabilities are separate from local databases. A domain replaces its implementation without replacing its identity.

Inside one trust boundary, world history ports across service migration, vendor replacement, and organizational change. Local projections rebuild from the canonical log.

Between organizations, no shared world exists.

```text
Organization A world          Organization B world
        │                              │
        └────── zero-trust gateway ────┘
                 signed requests
                 mutual validation
                 non-repudiation receipts
                 zero shared state
```

Each organization runs its own kernel, its own clock, its own governance. A gateway validates every inbound claim against local policy and issues signed receipts for every exchange. Inter-organization coordination is adversarial by design.

Cross-organization value moves under paired local escrows. Each side locks value in its own kernel escrow service, under its own governance. The gateway exchanges signed lock proofs and release proofs between the two escrows. Execution proof releases both sides; deadline expiry unwinds both sides. No escrow, ledger, or state sits between the organizations.

---

# 20. Implementation Model

A production implementation begins with a minimal kernel:

```text
1. Identity service
2. Append-only canonical event log
3. Authority registry
4. Dark capability registry
5. Policy engine with blast-radius caps
6. Delegation model with short-lived signed tokens
7. Local service databases
8. World tracing with deterministic replay
9. Ephemeral store for reasoning, hypotheses, and simulation
10. Boundary translators per domain pair
11. Escrow service for cross-domain commitments
```

Then:

```text
agent runtime with fast-path and slow-path split
JIT agent hydration and sandbox clearance
optimistic lease manager
memory
goal management
commitment protocol
negotiation with round and time bounds
simulation
human governance
zero-trust gateways for external organizations
```

The implementation requires no single database technology, no single model provider, and no single agent framework.

The interoperability boundary inside a trust domain is the World Protocol. The interoperability boundary between organizations is the zero-trust gateway.

---

# 21. Design Invariants

A conforming Living World preserves these invariants:

**Identity is stable.**

**Authority is explicit.**

**Facts have provenance.**

**Canonical events are immutable.**

**Capabilities are scoped, invisible by default, and issued against signed intent.**

**Policies are deterministic.**

**Authorization evaluates the single action and the aggregate pattern.**

**Agents manufacture no authority.**

**Authority tokens expire in seconds.**

**Tainted context blocks high-risk capabilities until human clearance.**

**Reasoning runs against a leased state version.**

**Local state differs; world semantics remain interoperable.**

**Historical truth is never silently rewritten.**

**Human decisions are first-class world events.**

**Simulation mutates no production state without explicit commit.**

**Governance authority is stronger than operating authority.**

**Cross-domain value moves only under escrow with a hard deadline.**

**External organizations share no state and no kernel.**

---

# 22. The Model

Living World Architecture reduces to one loop:

```text
                 ┌──────────────┐
                 │    WORLD     │
                 └──────┬───────┘
                        │
                     observe
                        │
                        ▼
                 ┌──────────────┐
                 │    AGENT     │
                 └──────┬───────┘
                        │
                      goal
                        │
                     reason
                        │
                        ▼
                 ┌──────────────┐
                 │  CAPABILITY  │
                 └──────┬───────┘
                        │
                      policy
                        │
                        ▼
                 ┌──────────────┐
                 │    ACTION    │
                 └──────┬───────┘
                        │
                      event
                        │
                        ▼
                 ┌──────────────┐
                 │    WORLD     │
                 └──────────────┘
                        ↺
```

Routine turns of the loop run on the fast path without model inference. Reasoning turns run under optimistic lease, taint tracking, and blast-radius caps.

This loop is the fundamental unit of operation.

---

# Conclusion

Living World Architecture provides a common foundation for systems in which software reasons, acts, negotiates, learns, and evolves under deterministic control over reality.

Its essential abstractions are:

```text
Identity
Fact
Event
Authority
Capability
Policy
Goal
Commitment
Agent
Living Service
World Protocol
World Kernel
```

The database is a local projection.

The backend is an execution and trust boundary.

The agent is a participant.

The service is an autonomous domain.

The organization is an executable world.

The world itself is the durable architectural abstraction.

> **Build the world. Give participants capabilities. Make authority explicit. Let intelligence operate within the boundary.**
