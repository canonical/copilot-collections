# Spread Server Management & Resource Cleanup Guide

When running tasks across virtualization (LXD, Multipass, QEMU) and cloud backends (OpenStack, Google Cloud), Spread allocates virtual machines and containers. This guide explains how to manage active server instances, reuse them for fast iteration, and cleanly discard or garbage-collect resources.

---

## 1. The Spread Server Lifecycle

By default, Spread provisions a fresh instance for a task run and automatically destroys it upon task completion. However, provisioning instances repeatedly introduces significant latency. Spread provides controls to keep servers alive across runs and clean them up when done.

| Action | Command / Flag | Purpose |
|---|---|---|
| **Keep server alive** | `-reuse` | Leaves backend instances running for subsequent task runs. |
| **Resend source files** | `-resend` | Synchronizes modified local files into the running reused instance. |
| **Discard reused servers** | `-discard` | Shuts down and deletes active reused servers. |
| **Garbage collection** | `-gc` | Reclaims orphaned or leaked backend resources (VMs, volumes, containers). |
| **Recover from crash** | `-reuse-pid <PID>` | Reconnects to servers left behind by a crashed Spread process. |
| **Run restore scripts** | `-restore` | Runs only the suite and task `restore` scripts on the instance. |

---

## 2. Iterative Development with `-reuse` and `-resend`

### Step 1: Provision and Keep Alive

Run the task with `-reuse`. Spread allocates the machine, runs the task, and keeps the server running:

```bash
spread -reuse multipass:ubuntu-24.04-64:tests/spread/commands/version
```

### Step 2: Re-run with Updated Code

After editing task files or source code in the repository, use `-reuse -resend` to push the updated files to the existing server without re-provisioning:

```bash
spread -reuse -resend multipass:ubuntu-24.04-64:tests/spread/commands/version
```

---

## 3. Discarding Reused Servers (`-reuse -discard`)

When execution is complete, always release backend resources by discarding the reused servers. Combining `-reuse` and `-discard` explicitly instructs Spread to target the active reused server pool and tear it down:

```bash
spread -reuse -discard
```

> [!TIP]
> You can also discard reused servers for a specific backend or selector:
>
> ```bash
> spread -reuse -discard multipass:
> spread -reuse -discard openstack:ubuntu-24.04-64:
> ```

---

## 4. Backend Garbage Collection (`-gc`)

If tasks are abruptly terminated or cloud resources leak, Spread can inspect the backend provider and remove orphaned VMs, dangling storage volumes, and unused security groups:

```bash
spread -gc
```

To run garbage collection for a specific backend:

```bash
spread -gc openstack:
spread -gc multipass:
```

---

## 5. Recovering from Crashed Processes (`-reuse-pid`)

When Spread runs with `-reuse`, it tags the provisioned server with its process ID (PID). If the Spread process crashes or is killed (`SIGKILL`, terminal disconnect):

1. Identify the PID of the previous Spread process from logs or history.
2. Reconnect to and discard the orphaned instances:

```bash
# Clean up servers left by process 12345
spread -reuse-pid 12345 -discard
```

---

## 6. Recommended Agent Cleanup Checklist

To avoid leaking instances or exhausting cloud quotas, agents should follow this cleanup procedure:

1. **Active Iteration**: Use `spread -reuse ...` and `spread -reuse -resend ...` while modifying and re-running code.
2. **Post-Execution Cleanup**: Always execute `spread -reuse -discard` once task execution concludes.
3. **Quota/Allocation Errors**: If Spread reports backend allocation errors or resource exhaustion, run `spread -gc` to purge orphaned resources before retrying.
