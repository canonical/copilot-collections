# Spread Logs, Artifacts & Diagnostic Output

When debugging Spread task runs, agents cannot rely on interactive shells. Instead, Spread provides built-in mechanisms to export **Artifacts**, **Execution Logs**, and **Machine-Readable JSON Results**.

---

## 1. Artifacts Collection (`-artifacts`)

Artifacts are files or directories generated on the task instance (e.g., application logs, core dumps, execution reports) that Spread pulls back to the host upon task completion or failure.

### Checking Declared Artifacts in `task.yaml`

To check if a task exports artifacts, inspect the `artifacts:` key in its `task.yaml`:

```bash
yq '.artifacts // []' tests/spread/commands/version/task.yaml
```

### Pulling Artifacts with `-artifacts`

Pass `-artifacts=<DIR>` to specify the destination directory on the host when running Spread:

```bash
spread -artifacts=./test-artifacts multipass:ubuntu-24.04-64:tests/spread/commands/version
```

### Artifact Directory Layout on Host

Spread organizes downloaded artifacts into a folder named after the full job descriptor:

```text
test-artifacts/
└── multipass.ubuntu-24.04-64.tests_spread_commands_version/
    ├── app.log
    ├── syslog
    └── crash-reports/
```

### Inspecting Artifacts

List and inspect downloaded artifact files:

```bash
# Locate all downloaded artifact files
find ./test-artifacts/ -type f
```

---

## 2. Execution & Communication Logs (`-logs`)

The `-logs` flag stores the complete raw output and backend communication transcripts for each job. This is particularly useful for debugging backend provisioning issues, SSH timeouts, and suite-level `prepare`/`restore` hook failures.

### Exporting Logs

```bash
spread -logs=./spread-logs openstack:ubuntu-24.04-64:tests/spread/commands/
```

### Log File Layout on Host

Spread generates individual log files for each job in the matrix:

```text
spread-logs/
├── openstack.ubuntu-24.04-64.tests_spread_commands_git-build-root.log
└── openstack.ubuntu-24.04-64.tests_spread_commands_version.log
```

---

## 3. Structured JSON Results (`-json`)

The `-json` flag produces machine-readable task execution summaries containing job status, execution timings, and error traces. This enables agents and CI systems to parse task outcomes programmatically.

### Exporting JSON Results

```bash
spread -json=./spread-results multipass:ubuntu-24.04-64:tests/spread/commands/...
```

### JSON Results Structure

The output directory contains a `summary.json` file detailing the executed jobs. A single job entry contains:

- `job`: Full job identifier.
- `status`: Outcome (`passed`, `failed`, `aborted`).
- `duration`: Execution duration in seconds.
- `error`: Error messages or non-zero exit codes if the task failed.

**Example output:**

```json
[
  {
    "job": "multipass:ubuntu-24.04-64:tests/spread/commands/version",
    "status": "passed",
    "duration": 42.3,
    "error": null
  }
]
```

---

## 4. Console Verbosity & Timing Flags

| Flag | Purpose | Description |
|---|---|---|
| `-v` | Verbose output | Displays detailed step-by-step progress during execution. |
| `-vv` | Debug output | Displays low-level debug messages, including backend API calls and SSH handshakes. |
| `-perf` | Timestamps | Prepends datetime timestamps to task script output to identify bottlenecks and hanging steps. |

---

## 5. Recommended Agent Diagnostic Workflow

When investigating task failures, use this combined non-interactive recipe:

```bash
# Run with failure preservation, structured JSON output, logs, and artifacts
spread -abend \
  -reuse \
  -artifacts=./test-artifacts \
  -logs=./spread-logs \
  -json=./spread-results \
  openstack:ubuntu-24.04-64:tests/spread/commands/version
```

### Diagnostic Steps:

1. **Check JSON summary**: Confirm whether failure occurred in task `execute:`, a suite hook (`prepare`), or backend allocation.
2. **Review task artifacts**: Check `./test-artifacts/` for application logs.
3. **Inspect full logs**: Read `./spread-logs/` for backend or hook execution logs.
4. **Preserved instance**: Because `-abend` was used, the machine remains alive on the backend for targeted follow-up re-runs with `-reuse`.
