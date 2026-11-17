# Spread Failure Diagnosis & Troubleshooting Guide

When a Spread run reports an error or exit failure, agents must distinguish between **Selector Syntax Errors**, **Backend Infrastructure Failures**, **Setup/Hook Failures**, **Timeouts**, and genuine **Task Execution Failures** inside `execute:`.

---

## 1. Quick Failure Classification Matrix

| Failure Category | When It Happens | Typical Error Symptoms | Primary Action |
|---|---|---|---|
| **1. Selector Error** | Pre-execution | `error: nothing matches provider filter`<br>`error: invalid filter string` | Fix selector syntax (check trailing `/` for suites, verify system names in `spread.yaml`). |
| **2. Infrastructure / Allocation** | Machine provisioning | Quota exceeded, SSH timeout, backend API error, `wait-timeout` reached. | Run `spread -gc`, check cloud credentials/proxies, or execute locally on `multipass:`/`lxd:`. |
| **3. Lifecycle Hook Error** | Machine setup/teardown | Non-zero exit code during `prepare`, `prepare-each`, or `restore`. | Fix dependency installation, snap channels, or network proxy in suite `prepare:`. |
| **4. Task Execution Failure** | Task execution | Non-zero exit code during task `execute:`. | Debug the application code or task script assertions. |
| **5. Execution Timeout** | Long-running task | Task terminated after exceeding `kill-timeout` or `warn-timeout`. | Check for deadlocks, infinite loops, or increase `kill-timeout` in `task.yaml`. |

---

## 2. Diagnosing Each Failure Type

### 1. Selector & Filter Errors

Spread aborts immediately before communicating with any backend:

- **Missing trailing slash on suite**:
  ```bash
  $ spread -list tests/spread/commands
  error: nothing matches provider filter
  ```
  *Fix*: Add trailing slash -> `spread -list tests/spread/commands/`
- **Invalid colon syntax**:
  ```bash
  $ spread -list ::tests/spread/commands/...
  error: invalid filter string: "::"
  ```
  *Fix*: Avoid consecutive colons -> `spread -list tests/spread/commands/...`

---

### 2. Backend Infrastructure & Allocation Errors

Infrastructure failures occur when Spread cannot allocate, boot, or establish SSH communication with the backend instance.

- **Symptoms**:
  - `cannot allocate server on backend <backend>: ...`
  - `timeout waiting for SSH connectivity`
  - Cloud API 401/403 (unauthorized) or quota exceeded.
- **Diagnostic Procedure**:
  1. **Verify Host Environment & Credentials**: When executing on cloud backends (e.g. OpenStack), ensure authentication credentials are exported in the host shell:
     ```bash
     env | grep -E '^(OS_|LXD_)'
     ```
  2. **Inspect full communication logs**:
     ```bash
     spread -logs=./spread-logs <selector>
     ```
  3. **Run garbage collection** to purge leaked or orphaned instances:
     ```bash
     spread -gc <backend>:
     ```
  4. **Verify on a local backend**: Test if the same task reproduces on a local virtualization backend (e.g. `multipass:` or `lxd:`).

---

### 3. Lifecycle Hook Failures (`prepare` & `restore`)

Spread executes hooks in a defined lifecycle before running the task itself:

`suite.prepare` -> `suite.prepare-each` -> `task.prepare` -> `task.execute`

- **Symptoms**:
  - Failure occurs before the `execute:` script runs.
  - Apt package installation fails, snap refresh fails, or Juju bootstrap errors out.
- **Distinguishing from Task Execution Bugs**:
  - Hook errors indicate that the execution environment was not ready or external dependencies failed to download, not that the code executed by the task is broken.
- **Diagnostic Procedure**:
  - Check `./spread-logs/` to examine the failing hook script.
  - If intermittent network flakes occur during package installation, verify proxy settings in `spread.yaml`.

---

### 4. Task Execution Failures (`execute:`)

A task execution failure occurs when the commands inside the task's `execute:` block return a non-zero exit code.

- **Symptoms**:
  - Output shows application traceback, assertion failure, or non-zero exit from the task script.
  - Spread triggers `suite.debug-each` (if defined) to collect diagnostics.
- **Diagnostic Procedure**:
  1. **Preserve the instance**: Re-run with `-abend` and `-reuse` so Spread aborts on failure without running restoration scripts and keeps the machine running:
     ```bash
     spread -abend -reuse -artifacts=./test-artifacts <selector>
     ```
  2. **Inspect artifacts**: Read output logs and reports collected in `./test-artifacts/`.
  3. **Iterative re-execution**: Use `-reuse -resend` to test code fixes against the running instance:
     ```bash
     spread -reuse -resend <selector>
     ```

---

### 5. Task Timeouts (`kill-timeout` & `warn-timeout`)

Tasks can define timeout limits in `task.yaml` (e.g., `kill-timeout: 30m`).

- **Symptoms**:
  - Spread terminates the task process with SIGKILL and marks the job as timed out.
- **Diagnostic Procedure**:
  - Run with `-perf` to view timestamps for each output line:
     ```bash
     spread -perf <selector>
     ```
  - Identify whether the task hung on a blocking prompt, network request, or infinite loop.

---

## 3. Recommended Troubleshooting Decision Flow

```text
Spread Execution Result
 ├── Exited immediately with syntax error?
 │    └── Selector Error: Verify system/suite syntax (check trailing /).
 ├── Failed during VM/container allocation or SSH connection?
 │    └── Infrastructure Error: Run spread -gc, check quota/credentials.
 ├── Failed during prepare / prepare-each hook?
 │    └── Environment/Hook Error: Check proxy, package repository, or snap channels.
 ├── Failed during execute: script?
 │    └── Task Execution Failure: Re-run with -abend -reuse -artifacts=./test-artifacts to inspect failure state.
 └── Task killed unexpectedly?
      └── Timeout: Run with -perf to locate hanging command.
```
