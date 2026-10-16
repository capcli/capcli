---
id: doc://prompts/federation/outbound#1
stem: federation.outbound.success.empty
bank: federation
slug: outbound
version: 1
trust: draft
sections:
  stage_1_allowlist: 90
  stage_2_probe: 80
  stage_3_dial: 90
slice_max_tokens: 500
docs:
  - doc://reference/errors
status: served
---

# ⚡ FEDERATED OUTBOUND ONBOARDING PROTOCOL
No active federated peers are registered. Outbound ws:// calls are refused.
Register a peer, probe its socket, and confirm the allowlist.

## section:stage_1_allowlist
List current peers and their status:
```bash
capcli sys agent list
```

Confirm the peer's ws:<name> row exists and status=active.

section:stage_2_probe

Probe the peer socket before dialing:

```bash
capcli ws status <peer_name>
```

Confirm the transport adapter is reachable.
See plugins.md#Federation-transport.

section:stage_3_dial

Dial the peer with a reviewed-trust routine:

```bash
capcli run ws://<workspace>/<routine>@<version> -p k=v
```

Version is mandatory. Unversioned exits 3.

