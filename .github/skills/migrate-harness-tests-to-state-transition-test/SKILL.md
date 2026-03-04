---
name: migrate-harness-tests-to-state-transition-test
description: Migrates legacy ops.testing Harness suites to state-transition tests by enumerating Harness usages, defining explicit State objects, and recreating assertions per Juju event so charms stay compatible with modern ops releases.
---

# Migrate Harness Tests To State Transition Test

## Overview

Guide charm maintainers through replacing deprecated Harness-based unit tests with deterministic state-transition tests that mirror how Juju actually fires events. Use this skill whenever a test still instantiates `testing.Harness` or chains multiple events inside one fixture.

## When To Use
- `ops.testing.Harness` (or Scenario Harness helpers) still appear in tests or fixtures.
- Migration requires modeling relations, containers, secrets, or actions with `testing.State`.
- CI must stay green while Harness-only helpers (`add_relation`, `evaluate_status`, etc.) are removed.

## Preflight Checks
- Inspect `pyproject.toml` (or requirements files) before touching code; ensure `ops[testing]` is present in **every** dependency group that executes Scenario/state-transition tests. Remove legacy `ops-scenario` if it lingers.
- Match the repo’s package manager: use `uv add --group unit ops[testing]` (and mirror across groups) when `[tool.uv]` or `uv.lock` exists; otherwise edit the appropriate `requirements.txt`, Poetry group, etc.
- After dependency edits, re-sync the exact groups you touched (`uv sync --group unit --group lint`, `poetry install`, etc.) so the virtualenv contains Scenario Context.
- Re-run the project’s bootstrap entrypoint (`uv sync`, `pip install -r requirements.txt`, `make setup`, …) to align local + CI execution before rewriting tests.

## Mandatory Plan & Ledger
Create a written task list **before** editing files and keep it updated:
1. Record the migration goal (e.g., "Drop Harness from tests/unit/test_charm.py") plus all files involved.
2. Add explicit tasks for every preflight requirement: dependency inspection, disposable venv creation, environment sync commands, bootstrap targets.
3. Inventory Harness usage with the detector script, note each file’s assertions, and migrate files one by one in ledger order.
4. Pair every code-change task with an immediate verification task (targeted pytest/tox command). Log the command, exit code, and timestamp when marking done.
5. If a command fails, append remediation + re-run tasks; do not advance to the next file until the paired verification succeeds.

## Repository Tooling Notes
- Prefer tox over ad-hoc venvs when `tox.toml` wires environments to `uv` runners; it keeps CI parity.
- Keep dependency groups consistent (fmt, lint, unit, integration, …). When `ops[testing]` is added to one group, mirror it across any environment that imports Scenario helpers.
- Check helper targets in `Makefile`/`tox.toml` before running bespoke setup commands—they often wrap the correct bootstrap flow.

## End-to-End Workflow

### 0. Pick the migration style
- Reuse existing fixtures/builders (for example `PenpotStateBuilder`, `create_state`) and port their internals to Scenario primitives when available.
- Inline tiny `State` objects only when Harness usage was minimal; large charms benefit from shared factories so relations/secrets stay consistent.

### 1. Inventory Harness usage
- Run `scripts/find_harness_tests.py` against `tests/` and categorize hits by surface area (actions, relations, Pebble, status).
- Copy the current assertions/story so you can verify behavioral parity after rewriting.

### 2. Define the event boundary and states
- For each Harness test, map the single Juju event being exercised and document the expected input/output state using the [migration checklist](references/migration-checklist.md).
- Pre-populate `testing.State` with relations, containers, config, leadership, secrets, and network data—Scenario never replays incremental Harness mutations.
- Ensure collect-status side effects have the necessary mock containers/layers/service statuses.

### 3. Rewrite the test
- Follow [state-transition-recipes.md](references/state-transition-recipes.md) to express one event per test.
- Invoke `ctx.run(ctx.on.<event>(...), state_in)` and assert on `state_out`, `ctx.action_results`, emitted statuses, and monkeypatched workload helpers.
- Duplicate Harness failure coverage with `pytest.raises(testing.ActionFailed)` or other exception checks; add separate tests for each branch instead of branching inside one function.

### 4. Validate and retire Harness
- Run the narrowest possible selection (e.g., `tox -e unit -- tests/unit/test_charm.py`) right after editing each file; log the result in the ledger.
- Delete Harness fixtures/imports once a file is fully migrated, then rerun the detector to confirm it no longer reports hits.
- Finish with the repo’s canonical unit-test target (`tox -e unit`, `pytest tests/unit`) and only mark the migration complete when it returns 0 with zero Harness matches.

## Reusable Resources
- `scripts/find_harness_tests.py`: Recursively scans the provided paths for `testing.Harness`/`Scenario` references. Usage:
	- `python3 .github/skills/migrate-harness-tests-to-state-transition-test/scripts/find_harness_tests.py tests/unit tests/integration`
- `references/migration-checklist.md`: Step-by-step plan that maps every Harness helper to its state-transition counterpart and reminds you to satisfy collect-status requirements.
- `references/state-transition-recipes.md`: Ready-to-paste snippets for actions, relation-changed, Pebble-ready, update-status, and failure cases.
- Canonical guide: [How to migrate unit tests from Harness](https://documentation.ubuntu.com/ops/latest/howto/legacy/migrate-unit-tests-from-harness/) (authoritative reference for nuanced behaviors).

## Event Playbooks (quick cues)
- **Actions**: `ctx.on.action("name", params=...)`; assert on `ctx.action_results` and expected failures (`testing.ActionFailed`). Provide container data when `_on_collect_status` inspects Pebble.
- **Relation changes**: Reuse the same `testing.Relation` instance in both `State` and `ctx.on.relation_changed(...)`; populate remote/local databags with the "new" data that triggered the event.
- **Pebble / containers**: Supply `testing.Container` objects with realistic `layers`, `service_statuses`, and `can_connect` flags. Inspect the **output** container via `state_out.get_container(name)`.
- **Status reporting**: Prefer `ctx.on.update_status()` to cover `_on_collect_status`; create success and failure variants (inactive service, disconnected container, missing plan).

## Example Prompts
- "List the files that still use `testing.Harness` so I can migrate them to state-transition tests."
- "Rewrite `tests/unit/test_charm.py::test_relation_changed` using the relation recipe and show the new `testing.State`."
- "Explain what additional state I need to provide so `_on_collect_status` stops failing inside the new tests."

## Quality Bar
- Every migrated file passes `scripts/find_harness_tests.py` with zero hits.
- Each test focuses on a single Juju event with clearly documented input and output state.
- Collect-status logic has both success and failure coverage.
- The final diff removes Harness imports and helpers in addition to adding state-transition tests.
- Repository ledger shows paired code/verification tasks with recorded command outputs and remediation notes for any failures.
- Final `tox -e unit` (or repo equivalent) succeeds after dependency sync and Harness removal.
