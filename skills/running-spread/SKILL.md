---
name: running-spread
description: >-
  Discovers, selects, executes, and debugs Spread integration test tasks
  in repositories with spread.yaml configurations. Use when running spread
  tests, inspecting spread.yaml matrix dimensions (backends, systems, suites,
  tasks, variants), troubleshooting spread failures, or managing spread
  server lifecycle.
compatibility: spread yq
allowed-tools: spread yq find grep env ls cat
---

# Using Spread

## Scope

This skill covers discovering, executing, and debugging Spread tasks.
It does NOT cover writing new `task.yaml` files, modifying `spread.yaml` configuration, writing Spread backend plugins, configuring cloud credentials, or setting up local virtualization providers (Multipass/LXD/QEMU).

---

## How to Use This Skill

This skill acts as a router. When you need to perform a task, read the corresponding reference guide:

1. **Discover the test matrix** → Read [test-matrix-and-selectors.md](references/test-matrix-and-selectors.md) to inspect backends, systems, suites, tasks, variants, and constraints using `yq` and `find`.
2. **Execute and iterate** → Read [command-reference.md](references/command-reference.md) for CLI flags (e.g., `-reuse`, `-resend`, `-abend`, `-workers`, `-repeat`).
3. **Diagnose failures** → Read [failure-diagnosis-and-troubleshooting.md](references/failure-diagnosis-and-troubleshooting.md) for the error classification matrix (infrastructure vs hooks vs timeouts).
4. **Manage servers** → Read [server-management-and-cleanup.md](references/server-management-and-cleanup.md) for lifecycle control (`-reuse -discard`, `-gc`, recovering PIDs).
5. **Collect diagnostic output** → Read [logs-and-artifacts.md](references/logs-and-artifacts.md) for parsing `-json` results, inspecting `-logs`, and collecting `-artifacts`.

---

## Critical Invariant Rules

> [!IMPORTANT]
> **Always run `spread -list` before executing tasks.**
> Before triggering any execution, you MUST run `spread -list <selector...>` to inspect the complete set of resolved task runs on `stdout`. This ensures you only provision instances and execute the exact intended set of tasks, backends, and systems, avoiding unintended blanket matrix runs.

> [!IMPORTANT]
> **Trailing Slash on Suites**: A suite name **must always end with a trailing slash (`/`)** both in `spread.yaml` and in selector expressions. Omitting the trailing slash causes Spread to treat the string as a task path instead of a suite.

> [!WARNING]
> If `spread` exits with a non-zero exit code, classify the failure before retrying.
> Read [failure-diagnosis-and-troubleshooting.md](references/failure-diagnosis-and-troubleshooting.md) and follow the Quick Failure Classification Matrix.

> [!CAUTION]
> **Interactive Flags**: Do NOT use `-debug`, `-shell`, `-shell-before`, or `-shell-after`. These spawn interactive TTY sessions that hang agent execution indefinitely. They are for human developers only.
