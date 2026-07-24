---
name: generate-docs-spread-test
description: "Regenerate Spread tutorial test scaffolding from docs/tutorial.md. Creates spread.yaml, tests/spread/tutorial/task.yaml, and .github/workflows/spread_test.yaml. WHEN: generate spread test, create task.yaml, spread scaffolding, refresh spread test, tutorial spread task, spread tutorial test."
argument-hint: "Describe any constraints or the target tutorial file"
metadata:
  author: canonical/platform-engineering
  version: "1.0.0"
---

# Generate the tutorial Spread test

You are refreshing the Spread test scaffolding for a charm tutorial.
The tutorial lives in `docs/tutorial.md` and is the single source of truth for
the commands that must run.

## When to Use

- Generating or refreshing Spread test scaffolding from a charm tutorial
- Creating `spread.yaml`, `tests/spread/tutorial/task.yaml`, and the CI workflow
- Extracting tutorial commands into Spread lifecycle phases (prepare/execute/restore)

## Goal

Add or update exactly these three files:

1. `spread.yaml` — Spread project configuration at the repository root.
2. `tests/spread/tutorial/task.yaml` — the tutorial task, one Spread task
   covering the full deploy-to-cleanup flow.
3. `.github/workflows/spread_test.yaml` — a plain (non-agentic) GitHub Actions
   workflow that installs Spread and runs `spread -v github-ci:` on
   `workflow_dispatch`, on a weekly `schedule`, and on `pull_request` when any
   of the Spread files change.

Do **not** modify any other file. Do not touch `docs/tutorial.md`, `src/**`,
`lib/**`, or any existing workflow.

## Procedure

### Step 1 — Read the tutorial

Read `docs/tutorial.md` end-to-end. Also read `charmcraft.yaml` or
`metadata.yaml` to discover the charm name.

### Step 2 — Extract and classify commands

Extract shell commands from `docs/tutorial.md` in tutorial order. Do not
paraphrase or reorder them. Split commands across Spread lifecycle phases:

Refer to [the command classification reference](./references/command-classification.md)
for the phase assignment criteria and examples.

### Step 3 — Generate `spread.yaml`

Refer to [the spread.yaml reference](./references/spread-yaml-shape.md) for
the required structure, including the verbatim `github-ci` backend block.

### Step 4 — Generate `tests/spread/tutorial/task.yaml`

Refer to [the task.yaml reference](./references/task-yaml-shape.md) for
the required structure. Replace narrative waits with deterministic checks
using `juju wait-for` and Spread's `MATCH` helper.

### Step 5 — Generate `.github/workflows/spread_test.yaml`

Refer to [the workflow reference](./references/spread-workflow-shape.md) for
the required structure.

### Step 6 — Validate

Run each check. If any fails, fix the generated files and re-run.

1. Install `spread` if missing:
   ```
   command -v spread || sudo snap install spread || \
     (sudo snap install --classic go && /snap/bin/go install github.com/canonical/spread/cmd/spread@latest)
   ```
2. `spread -list ./` — must succeed and print at least one job matching
   `github-ci:ubuntu-24.04-64:tests/spread/tutorial…`.
3. `yamllint spread.yaml tests/spread/tutorial/task.yaml .github/workflows/spread_test.yaml`
   — must pass.

### Step 7 — Summarize

Provide the user with:

1. **Command mapping** — a Markdown table with columns `Tutorial section` |
   `Phase (prepare / execute / restore)` | `Command` covering every
   command extracted from the tutorial.
2. **Validation output** — trimmed `spread -list ./` output.
3. **Follow-ups** — anything the tutorial doesn't yet express as a
   deterministic check (e.g., manual "click Sign Up" steps that had to be
   dropped or approximated).
