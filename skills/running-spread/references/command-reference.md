# Spread CLI Command Reference

This reference covers the command-line flags, runtime options, debugging helpers, and practical workflows for executing tasks with [Spread](https://github.com/canonical/spread).

> [!TIP]
> For a detailed explanation of the matrix hierarchy (Backends, Systems, Suites, Tasks, Variants), programmatic matrix discovery with `yq`/`find`, and full selector grammar, refer to [test-matrix-and-selectors.md](test-matrix-and-selectors.md).

---

## 1. Command-Line Flags

> [!NOTE]
> For flags taking arguments, Spread accepts both space-separated (`-flag <val>`) and equal-separated (`-flag=<val>`) syntax.

| Flag | Description | Typical Use Case |
|---|---|---|
| `-list` | List all matched jobs on stdout without executing them | Previewing task selection before execution |
| `-json=<DIR>` | Save structured machine-readable task results (JSON) | Automated result parsing by agents or CI |
| `-logs=<DIR>` | Save generated execution and communication logs to a directory | Archiving full task logs for diagnosis |
| `-reuse` | Keep allocated instances alive for subsequent runs | Accelerating local iterative execution |
| `-discard` | Discard/destroy any running reusable instances | Cleaning up environment after execution |
| `-resend` | Resend project content to reused servers | Syncing updated source files to reused instance |
| `-repeat <N>` | Repeat each selected task `N` times | Flake hunting and stability verification |
| `-order` | Execute tasks in exact declared order without shuffling | Preventing task randomization |
| `-seed <N>` | Seed for random task permutation | Reproducing order-dependent failures |
| `-abend` | Stop immediately on first error without restoring/cleaning up | Preserving failure state on the backend instance |
| `-artifacts=<DIR>` | Directory to save collected artifacts | Fetching logs, crash dumps, and outputs |
| `-perf` | Show timestamps and task execution durations | Performance benchmarking and timing analysis |
| `-v` / `-vv` | Verbose / debug logging output from Spread | Troubleshooting Spread allocation/setup |
| `-workers <N>` | Number of concurrent workers per system | Tuning task parallelism |
| `-restore` | Run only the restore scripts | Cleaning up partially executed suites |
| `-gc` | Discard allocated servers no longer in use | Purging orphaned backend instances |
| `-reuse-pid <PID>` | Select servers reused by a specific Spread process | Recovering from a crashed Spread run |

---

## 2. Practical Workflow Recipes

### 1. Previewing Task Selection (`-list`)

For detailed selector syntax examples across backends, systems, suites, tasks, and variants, see [test-matrix-and-selectors.md](test-matrix-and-selectors.md):

```bash
# List all jobs in the project matrix
spread -list

# List all tasks in a specific suite (suite must end with '/')
spread -list tests/spread/commands/

# List matching tasks on OpenStack for Ubuntu 24.04
spread -list openstack:ubuntu-24.04-64:
```

### 2. Fast Local Iteration & Server Management (`-reuse`, `-resend`, `-discard`)

When developing or modifying a task, avoid re-provisioning instances each run. For complete server lifecycle and garbage-collection guides, see [server-management-and-cleanup.md](server-management-and-cleanup.md):

```bash
# First run: provisions the backend instance and keeps it alive
spread -reuse multipass:ubuntu-24.04-64:tests/spread/commands/version

# Subsequent runs: syncs modified files and reuses the running machine
spread -reuse -resend multipass:ubuntu-24.04-64:tests/spread/commands/version

# When finished testing, discard the reused instance
spread -reuse -discard
```

### 3. Preserving Failure State (`-abend`)

Stop execution on the first error and prevent restoration scripts from altering the machine state. For error classification and troubleshooting steps, see [failure-diagnosis-and-troubleshooting.md](failure-diagnosis-and-troubleshooting.md):

```bash
# Halt on first failure and preserve remote machine state for inspection
spread -abend openstack:ubuntu-24.04-64:tests/spread/commands/version
```

### 4. Hunting Flaky Tasks (`-repeat`, `-seed`, `-order`)

By default, Spread shuffles task order within a suite to uncover hidden order dependencies:

```bash
# Repeat the task 10 consecutive times to verify determinism
spread -repeat 10 multipass:ubuntu-24.04-64:tests/spread/commands/version

# Execute tasks in sequential/declared order without shuffling
spread -order tests/spread/commands/

# Reproduce a specific randomized execution order using its seed
spread -seed 42 tests/spread/commands/
```

### 5. Controlling Concurrency on Local Host (`-workers`)

When running on local backends (Multipass, LXD, QEMU), limit worker parallelism to avoid CPU contention or memory exhaustion:

```bash
# Run with a single worker to avoid host overloading
spread -workers 1 multipass:ubuntu-24.04-64:tests/spread/commands/
```

### 6. Collecting Artifacts (`-artifacts`)

Download logs and output files declared under `artifacts:` in `task.yaml`. For layout details and inspection procedures, see [logs-and-artifacts.md](logs-and-artifacts.md):

```bash
spread -artifacts=./test-artifacts multipass:ubuntu-24.04-64:tests/spread/commands/version
```

### 7. Exporting Machine-Readable Results (`-json` & `-logs`)

Save structured task execution results and logs for automated parsing. For schema details and diagnostic workflows, see [logs-and-artifacts.md](logs-and-artifacts.md):

```bash
# Run tasks and export structured JSON summary and log files
spread -json=./spread-results -logs=./spread-logs multipass:ubuntu-24.04-64:tests/spread/commands/version
```

---

## 3. Interactive Flags (Human Operators Only)

These flags (`-debug`, `-shell`, `-shell-before`, `-shell-after`) are strictly for human debugging and spawn interactive PTY shells. As noted in the main skill router, agents must never invoke them.
