---
id: prompt://federation/remediation@1
stem: federation.remediation.denial.denied
bank: federation
slug: remediation
version: 1
trust: draft
sections:
  stage_1_allowlist: 90
  stage_2_cycle: 90
  stage_3_transport: 90
slice_max_tokens: 500
docs:
  - doc://reference/errors
status: served
---

# FEDERATED CALL REMEDIATION PROTOCOL
A cross-workspace call was refused by kernel federation defenses. Follow the stage matching the denial code:

## section:stage_1_allowlist
E042_FEDERATION_DENIED — caller not an active federated peer:
1. Confirm the peer registration:
   ```bash
   capcli sys agent list
   ```
2. Register a revoked or missing peer, then retry. Only `status=active` rows pass the allowlist.

## section:stage_2_cycle
E041_FEDERATION_CYCLE — workspace already in call_chain:
1. Inspect the chain on the denial receipt; find the repeated workspace.
2. Break the cycle: inline the call or route through a non-cyclic workspace. Never retry the same chain.

## section:stage_3_transport
E055_FEDERATION_UNREACHABLE — peer socket absent after 1500ms:
1. Start the peer daemon, or confirm the socket path.
2. In sim/CI, rely on cassette replay from federation/cassettes/ instead of a live peer.
