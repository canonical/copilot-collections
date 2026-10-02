---
name: setup-temporal-workflows-test
description: 'Set up or verify the three-layer test structure (unit, activity, workflow) for a Python Temporal workflow project: tests/unit, tests/activity, tests/workflow subdirectories, corresponding Makefile targets (test, test-unit, test-activity, test-workflow), and matching steps in .github/workflows/ci.yaml. Use when asked to set up tests, add test layers, wire up CI testing, or fix test/Makefile/CI structure for a Temporal workflow project.'
---

# Setup Temporal Workflows Test Structure

Ensures a Python Temporal workflow project has the standard three-layer test
layout (`unit`, `activity`, `workflow`), Makefile targets to run each layer
individually and all together, and a CI workflow that runs each layer as a
separate step via `make`.

This repository is a monorepo where each Temporal project lives under
`workflows/<project_name>/` with its own `Makefile`, `pyproject.toml`, and
`tests/` directory (see `workflows/template/` for the canonical layout).
Always determine the target project directory first — do not assume the
repository root. If the user did not specify a project, ask which
`workflows/<name>/` directory to operate on, or infer it from the current
working directory.

## Procedure

### 1. Ensure `tests/unit`, `tests/activity`, `tests/workflow` subdirectories exist

In the target project directory:

- Check whether `tests/unit`, `tests/activity`, and `tests/workflow` already
  exist.
- Create any that are missing with `mkdir -p`.
- If the project's existing tests use `tests/__init__.py` (check the current
  `tests/` directory), add matching empty `__init__.py` files to each new
  subdirectory for consistency.
- Do **not** move existing test files automatically — flag any tests sitting
  directly in `tests/` that look like they belong in one of the three layers,
  and ask the user before moving them, since this can break coverage/CI
  expectations if done blindly.

### 2. Ensure Makefile has `test`, `test-unit`, `test-activity`, `test-workflow` targets

Read the project's `Makefile` first. Follow its existing conventions (e.g.
`$(POETRY) run $(PYTEST)`, `--cov=$(PY_PACKAGE)` flag, `.PHONY` declarations)
instead of inventing a new style. A typical existing `test` target looks like:

```makefile
.PHONY: test
test: ## Run tests
	$(POETRY) run $(PYTEST) --cov=$(PY_PACKAGE) tests
```

Rework it into four targets, each `.PHONY`, using the same pytest invocation
style but scoped to the relevant subdirectory, with `test` depending on the
other three so `make test` still runs everything:

```makefile
.PHONY: test-unit
test-unit: ## Run unit tests
	$(POETRY) run $(PYTEST) --cov=$(PY_PACKAGE) tests/unit

.PHONY: test-activity
test-activity: ## Run activity tests
	$(POETRY) run $(PYTEST) --cov=$(PY_PACKAGE) tests/activity

.PHONY: test-workflow
test-workflow: ## Run workflow tests
	$(POETRY) run $(PYTEST) --cov=$(PY_PACKAGE) tests/workflow

.PHONY: test
test: test-unit test-activity test-workflow ## Run all tests
```

Only add targets that are missing; if `test-unit`/`test-activity`/`test-workflow`
already exist, leave them alone unless they don't point at the right
directory. Preserve any other targets (`lint`, `fmt`, `check`, etc.) and their
dependency on `test` (e.g. `check: clean install-dev lint test`) unchanged.

### 3. Ensure `.github/workflows/ci.yaml` runs each layer as a separate step via `make`

- If the target project has its own `.github/workflows/ci.yaml`, add or
  update it there.
- If the project relies on this repo's root-level `.github/workflows/ci.yaml`
  (which drives testing indirectly through the reusable
  `.github/workflows/check_make.yaml` workflow and matrix of changed
  directories), do not fork the whole pipeline. Instead:
  - Confirm `check_make.yaml`'s single `command: test` input already fans out
    correctly, since `make test` now runs all three layers in sequence
    (from step 2). This satisfies "runs all tests" automatically.
  - If the user explicitly wants the three layers visible as **separate**
    steps/jobs in CI output (not just one `make test` step), add three
    sequential steps to the relevant workflow, each invoking `make` directly,
    for example:

    ```yaml
    - name: Run unit tests
      run: |
        cd workflows/${{ matrix.dir }}
        make test-unit

    - name: Run activity tests
      run: |
        cd workflows/${{ matrix.dir }}
        make test-activity

    - name: Run workflow tests
      run: |
        cd workflows/${{ matrix.dir }}
        make test-workflow
    ```

  - Never invoke `pytest` directly — always go through the `make`
    targets so local and CI behavior stay identical.
- For a standalone (non-monorepo) Temporal project with its own
  `.github/workflows/ci.yaml`, add three steps calling `make test-unit`,
  `make test-activity`, and `make test-workflow` respectively (after any
  install/lint steps), instead of a single `make test` step.

## Verification

After making changes:

1. Run `make -n test test-unit test-activity test-workflow` in the project
   directory to confirm all targets resolve without executing them.
2. Run `make test-unit` (and the other two) if a working Python/Poetry
   environment is available, to confirm they actually collect tests (even
   zero tests is fine for empty new directories — a pytest "no tests
   collected" exit code is expected until tests are added).
3. Lint the modified `ci.yaml` with `yamllint` or a YAML parser if available,
   since indentation errors here silently break CI.
4. Report which of the three checks (directories / Makefile / CI) were
   already satisfied versus newly created, so the user knows what changed.
