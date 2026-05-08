---
description: 'Guidelines for Python Temporal projects'
applyTo: '**'
---

# Temporal Project - Copilot Instructions

## Overview

This repository contains a Python-based Temporal application. These projects typically define one or more workflows, register activities in one or more workers, and integrate with APIs, databases, queues, storage systems, or internal services. Assume the repository is production-oriented, automation-heavy, and sensitive to operational correctness. Optimise for deterministic workflow logic, clear workflow and activity boundaries, safe payload handling, clear operational behaviour, and maintainable Python code.

---

## Typical Stack

| Layer | Tooling / Pattern |
|---|---|
| Language | Python 3.12 |
| Package management | Poetry |
| Workflow engine | Temporal Python SDK + `temporallib` |
| Configuration | `pydantic-settings` / environment variables |
| Execution entrypoint | `<package>/worker.py` |
| Local automation | `Makefile` |
| Deployment artifact | `rockcraft.yaml` + `scripts/start-worker.sh` |
| Tests | `pytest` |
| Quality tools | `black`, `isort`, `flake8`, `pylint`, `bandit`, `pydocstyle` |

---

## Repository Structure

Most Temporal workflow repositories in this ecosystem follow this layout:

```text
<root>/
├── README.md
├── pyproject.toml
├── poetry.lock
├── Makefile
├── .env.sample
├── rockcraft.yaml
├── scripts/
│   └── start-worker.sh
├── helper_scripts/ or sample_scripts/
│   └── trigger_workflow.py
├── docs/
├── tests/
│   └── unit_tests/
└── <package_name>/
    ├── worker.py
    ├── activities/
    ├── workflows/
    ├── common/
    ├── backend/
    └── clients/
```

Keep these responsibilities clear:

- `workflows/` orchestrates execution and Temporal semantics.
- `activities/` performs side effects and talks to external systems.
- `common/` holds configuration, schemas, constants, and shared helpers.
- `backend/` and `clients/` wrap service-specific logic.
- `worker.py` wires workflows, activities, connection options, and schedules.

---

## Core Design Rules

### Keep workflow code deterministic

- Put orchestration in workflow classes and side effects in activities.
- Do not perform network I/O, filesystem writes, database queries, or random value generation directly in workflow code.
- Use Temporal primitives such as `workflow.now()` and `workflow.info()` instead of non-deterministic standard-library calls.
- Pass through only deterministic, side-effect-free modules via `workflow.unsafe.imports_passed_through()`.

### Keep workflow inputs minimal

- Pass only the identifiers and control parameters the workflow needs.
- Fetch large, sensitive, or rapidly changing records inside activities rather than embedding them in workflow inputs.
- Avoid putting secrets, raw API payloads, or sensitive data into workflow history unless there is a strong reason.
- Remember that all workflow inputs and outputs pass through the Temporal data converter; prefer payloads that serialize and replay cleanly.

### Make retries explicit

- Define timeout and retry helpers in one shared place so policy is consistent and reviewable.
- Use consistent retry policies for activities by default, but allow activity-specific timeout or retry overrides when the work is materially different, for example heavier processing or longer-running operations.
- Prefer retryable failures by default so failed executions stay visible near the top of the Temporal UI until they are resolved.
- Raise `ApplicationError` explicitly only when you need to control Temporal-specific failure metadata such as error type, details, or non-retryable behaviour. Otherwise, let Temporal convert uncaught exceptions.

### Prefer stable orchestration patterns

- Prefer simpler workflow topologies when the problem size is bounded.
- Use an orchestrator or dispatcher workflow only when the workflow topology genuinely benefits from it.
- Prefer workflow IDs and schedule IDs that are stable, meaningful, and derived from domain identity.
- Batch or rate-limit fan-out when calling quota-constrained APIs.

---

## Workflow Conventions

### Workflow classes

- Decorate every workflow with `@workflow.defn(name="...")` and keep the name stable.
- Use a single `run` method as the workflow entrypoint.
- Return structured, serialisable summaries instead of raw service responses.
- Log meaningful state transitions using `workflow.logger`.
- Keep workflow handlers and internal state easy to reason about; avoid unnecessary mutable shared state within a workflow.

### Activity execution

- Centralise `RetryPolicy` and timeout creation instead of rebuilding them inline, and use existing helper wrappers such as `ActivityRunner` when the repository already provides them.
- Prefer Pythonic `snake_case` activity names that clearly describe the side effect or unit of work, for example verb-led names like `fetch_records`, `sync_account`, `upload_file`, or `cleanup_resources`.
- Default activities to synchronous implementations unless you are sure the activity body is async-safe and does not block the event loop.
- If an activity is asynchronous, use async-safe libraries for I/O. If it must call blocking code, move that work to a synchronous activity or run it through an executor or thread helper.

### Child workflows and fan-out

- Do not introduce child workflows just for code organisation; prefer a single workflow plus activities when the problem size is bounded.
- Use child workflows when they model a separate long-lived workflow concern, partition a large workload into smaller event histories, represent ownership of a single resource, or encapsulate periodic logic. Prefer activities when in doubt; child workflows add workflow-level overhead and state-management complexity.
- Set `ParentClosePolicy` deliberately.
- Remember that parent and child workflows do not share local state and communicate only through workflow mechanisms such as signals and results.
- Use explicit `WorkflowIDReusePolicy` when reruns are expected, and be mindful of event history growth in both parent and child workflows.

### Schedules

- Create schedules in `worker.py`.
- Use stable schedule IDs so updates are idempotent.
- If a schedule may already exist, update or recreate it explicitly rather than relying on implicit behaviour.
- Document whether a schedule is automatic, paused by default, or intended for manual triggering.

---

## Activity Conventions

### Side-effect boundaries

- Put side effects in activities: external API calls, database work, filesystem operations, storage access, message publishing, notifications, cleanup, or any other interaction with the outside world.
- Keep each activity responsible for one coherent unit of side-effecting work.
- If an operation mixes expensive I/O with aggregation logic, consider splitting it into multiple activities unless atomicity is essential.
- Use heartbeats for long-running activities when cancellation responsiveness or progress reporting matters.

### Error handling

- Catch service-specific exceptions close to the integration boundary.
- Re-raise errors with enough context to explain which record, batch, or external system failed and why.
- Default to retryable failures; use non-retryable failures only when continued retries would be actively harmful or would hide a more important operator action.
- Keep failure semantics explicit and predictable so retries, alerts, and operator action are easy to understand.

### Logging

- Log identifiers and counts, not secrets or sensitive payloads.
- Include enough context to debug failed executions, for example workflow ID, record identifier, source system, or target environment.
- Prefer structured, stable log messages over ad hoc debug text.

---

## Configuration Conventions

### Environment-driven config

- Use typed configuration models where the repository benefits from them.
- Group settings by domain, for example Temporal, workflow tuning, API clients, storage, email, or business-system credentials.
- Use prefixes consistently, such as `APP_`, `TEMPORAL_`, `WORKFLOW_`, `WF_`, or service-specific prefixes.
- Keep defaults conservative and production-safe.

### Secrets

- Never hardcode credentials, encryption keys, tokens, or service-account material.
- Assume local development uses `.env` and deployed environments use Juju config and secrets.
- Reference documented secret names and environment variables instead of inventing new ones casually.
- Treat encryption keys and OIDC credentials as deployment secrets, not code or sample data.

### Validation

- Validate configuration shape close to the config model.
- Prefer descriptive validation errors over silent coercion.
- Keep naming consistent between config classes, `.env.sample`, documentation, and deployment files.

---

## Data Modeling

- Use Pydantic models or dataclasses for workflow inputs, activity inputs, and structured results.
- Keep payloads JSON-serialisable by Temporal, and handle `Decimal`, `datetime`, enums, and large nested payloads deliberately.
- Customise the data converter only when the application genuinely needs custom serialization, codecs, encryption, compression, or payload offloading.
- Prefer small result objects with explicit fields over unstructured dictionaries when the contract is stable.

If the data is privacy-sensitive or high-volume:

- pass lightweight identifiers through workflow history;
- fetch the full record inside the activity;
- return only the fields needed for orchestration or reporting.

If payload size is a concern:

- observe Temporal payload and event-history size limits, including the 2 MB payload limit;
- do not pass large payloads between workflows and activities or across activity boundaries;
- prefer keeping large-data logic within the same activity when the data can stay in-process;
- prefer references to external storage over very large workflow payloads;
- keep payload contracts versionable and easy to replay.

---

## Local Development

Temporal repositories usually benefit from a simple local loop such as:

```bash
make install-dev
make run-worker
make run-client
```

If the repository provides local Temporal helpers, prefer those over ad hoc commands. Common patterns include:

- `make start-local-temporal`
- `make run-worker`
- `make run-client`
- repo-specific scripts for worker startup, local test servers, or workflow triggering

When adding new instructions, examples, or code:

- preserve the repository's existing `Makefile` targets;
- keep local and deployed modes clearly separated;
- honour flags such as `APP_USE_LOCAL_TEMPORAL` or equivalent local-run switches.

---

## Testing Expectations

- Prefer `pytest` unless the repository already standardises on something else.
- Add or update tests for workflow branching logic, config validation, payload models, and activity helper logic.
- Test activities in isolation with Temporal's activity testing utilities when activity context, cancellation, or heartbeats matter.
- Prefer integration-style workflow tests with Temporal test environments for most workflow behaviour.
- Use time-skipping test environments for timer-heavy or retry-heavy workflows.
- Mock activities in workflow tests when you need to isolate orchestration logic.
- Cover schedule-related behaviour when the workflow creates, updates, or deletes schedules.
- Add replay tests or workflow-history replay checks for workflow changes that could affect determinism.

Use the repository's standard commands where present:

```bash
make fmt
make lint
make test
make check
```

---

## Documentation Expectations

- Document the workflow topology and overall design clearly in `README.md`: entry workflow, child workflows, activities, schedules, integrations, data flow, process orchestration, and key decisions or handoffs.
- Keep environment variables and secrets documented in either `.env.sample`, `docs/vars_table.md`, `deployment.yaml`, or equivalent deployment docs.
- When a schedule is created automatically by the worker, state its ID, cadence, and whether it should be paused or manually triggered.
- When external systems impose quotas or permissions, document the operational constraint explicitly.
- Document any determinism-sensitive assumptions, sandbox customisations, data-converter customisations, or replay expectations that future maintainers must preserve.

---

## Deployment Conventions

- Keep worker startup commands, packaging metadata, and module names aligned.
- Ensure the deployed worker entrypoint starts the intended worker module or process consistently.
- If versioned deployment artifacts are used, update versions intentionally and follow semantic versioning.
- Keep task queue, namespace, and host configuration externalised.
- Separate deployment-specific guidance from workflow logic when possible so the core Temporal design remains portable.

---

## Preferred Patterns

### Good pattern: small workflow input, full lookup in activity

```python
class WorkItem(BaseModel):
    resource_id: str
    requested_by: str | None = None


@workflow.defn(name="ResourceSyncWorkflow")
class ResourceSyncWorkflow:
    @workflow.run
    async def run(self, work_item: WorkItem) -> dict[str, str]:
        await workflow.execute_activity(
            sync_resource,
            work_item,
            start_to_close_timeout=get_timeout(),
            retry_policy=get_retry_policy(),
        )
```

Why this is good:

- the workflow history stays small;
- sensitive fields are fetched inside the activity;
- retry and timeout policy is standardised.

### Good pattern: schedule creation with stable identifiers

```python
await client.create_schedule(
    SCHEDULE_ID,
    Schedule(
        action=ScheduleActionStartWorkflow(
            MyWorkflow.run,
            id=SCHEDULE_ID,
            task_queue=os.getenv("TEMPORAL_QUEUE"),
        ),
        spec=ScheduleSpec(intervals=[ScheduleIntervalSpec(every=timedelta(hours=2))]),
    ),
)
```

### Avoid

- fetching live external data directly inside workflow code;
- passing entire source-system records into workflow input without need;
- embedding secrets or credential material in constants or tests;
- duplicating retry / timeout literals across many workflows;
- using async activities for blocking I/O without async-safe libraries or executor handoff;
- disabling the workflow sandbox casually;
- overusing child workflows when activities or simpler workflow structure would do;
- hiding schedule semantics in undocumented magic strings;
- making workflow behaviour depend on undocumented environment variables.

---

## Review Checklist

When reviewing or generating code for Temporal workflow projects, check that:

- workflow code is deterministic and orchestration-focused;
- activities own the side effects;
- configuration is environment-driven and validated;
- workflow sandbox and passthrough-module choices are deliberate;
- activity sync versus async choices are appropriate for the I/O being performed;
- payload size and serialization choices are appropriate for Temporal history;
- retries and timeouts are explicit and reusable;
- workflow and schedule IDs are stable and meaningful;
- logs avoid secrets and large sensitive payloads;
- tests cover branching logic, failure handling, and determinism-sensitive changes;
- README and deployment docs reflect the real runtime behaviour.
