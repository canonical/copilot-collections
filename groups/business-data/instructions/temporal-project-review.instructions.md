---
description: 'Guidelines for reviewing Python Temporal workflow projects with focus on determinism, operability, and regression risk'
applyTo: '**'
---

# Temporal Workflow Review Instructions

## Purpose

When reviewing Temporal workflow projects, prioritise correctness, determinism, operational safety, and regression risk over style preferences.

Temporal code should be reviewed differently from ordinary Python application code because small changes can break replay, alter retry behaviour, grow event history unexpectedly, or leak sensitive data into workflow history and logs.

## Review Priorities

Review Temporal changes in this order:

1. Determinism and replay safety
2. Workflow and activity boundary correctness
3. Payload size and event history growth
4. Retry, timeout, cancellation, and heartbeat behaviour
5. Async activity safety and worker health
6. Schedule, child workflow, and ID stability
7. Secrets, sensitive data, and logging hygiene
8. Tests, documentation, and deployment alignment

## What to Look For

### Determinism and replay safety

- Flag non-deterministic calls inside workflow code.
- Check that workflow code uses Temporal primitives such as `workflow.now()` rather than non-deterministic standard-library calls.
- Check sandbox-related imports and `workflow.unsafe.imports_passed_through()` usage for safety and necessity.
- Treat workflow type renames, handler changes, branching changes, timer changes, and child-workflow orchestration changes as replay-sensitive.
- Ask for replay coverage or determinism validation when workflow definitions change in meaningful ways.

### Workflow and activity boundaries

- Check that side effects stay in activities, not workflows.
- Check that workflow inputs are small and orchestration-focused.
- Flag cases where large records, service payloads, or mutable operational state are passed through workflow history unnecessarily.
- Check whether logic that should remain in one activity has been split in a way that forces large payloads across activity boundaries.

### Payload size and event history growth

- Look for payloads that may approach Temporal limits, especially large results passed between workflows and activities.
- Check for patterns that repeatedly append large data to workflow history.
- Flag fan-out or loop structures that could create excessive event histories.
- Prefer references to external storage when payloads are large.

### Retries, timeouts, cancellation, and heartbeats

- Verify that retry and timeout policy remains consistent with repository conventions.
- Check that failure handling still reflects the desired operational behaviour in Temporal UI.
- Flag missing heartbeats in long-running activities where cancellation or progress visibility matters.
- Check whether timeout or retry changes could silently alter production behaviour.

### Async activity safety

- Review `async def` activities carefully for blocking I/O.
- Flag use of blocking libraries in asynchronous activities unless the code is explicitly moved to an executor or thread helper.
- Prefer synchronous activities when the work is blocking or not clearly async-safe.

### Child workflows, schedules, and IDs

- Check that child workflows are used for a valid reason, not just code organisation.
- Review `ParentClosePolicy`, `WorkflowIDReusePolicy`, schedule IDs, workflow IDs, and task queue usage for stability.
- Treat schedule creation, update, deletion, cadence changes, and pause/manual-trigger semantics as high-impact review areas.

### Sensitive data and logging

- Flag secrets, credentials, raw service payloads, or sensitive business data appearing in workflow history, logs, constants, tests, or examples.
- Check that logs are operationally useful without exposing protected data.

### Tests, docs, and deployment alignment

- Check whether workflow changes are covered by appropriate unit, integration, time-skipping, or replay tests.
- Check whether schedule behaviour, environment variables, workflow design, and data flow docs still match the implementation.
- Review `worker.py`, startup scripts, deployment config, and README updates together when runtime behaviour changes.

## Critical Review Behaviour

For Temporal workflow reviews, you are allowed and encouraged to comment on files outside the diff when needed to assess impact.

This includes:

- workflow definitions affected by a shared helper change;
- tests that should cover a risky behaviour change but were not updated;
- `worker.py`, deployment config, or docs that now disagree with the implementation;
- payload models, config models, or helper modules that make the reviewed change risky.

## What Not to Focus On First

Unless they create a real correctness or operability risk, do not prioritise:

- stylistic preferences;
- minor naming choices;
- harmless refactors with no replay or behaviour impact;
- abstract architecture opinions unsupported by concrete Temporal risk.

## Review Template

When reviewing a Temporal workflow PR, structure your feedback to follow **exactly** this template:

```markdown
## Temporal Workflow Review

**Scope**: workflow / activity / schedule / config / docs
**Risk Level**: low / medium / high

### Findings
- [severity] `path/to/file`: concrete issue, impact, and why it matters in Temporal

### Required Validation
- Replay coverage needed / not needed
- Integration or time-skipping test needed / not needed
- Schedule or deployment verification needed / not needed

### Recommendation
- Safe to merge
- Merge after fixes
- Do not merge yet
```

## Good Findings

### Good Review Comment

> `workflows/sync_workflow.py`: This change introduces `datetime.utcnow()` inside workflow code. That is non-deterministic and can break replay for in-flight executions. Use `workflow.now()` instead.

### Good Review Comment

> `activities/export.py`: This activity is now `async def` but still uses a blocking HTTP client. That can block the worker event loop and stall unrelated work. Keep it synchronous or switch to an async-safe client.

### Good Review Comment

> `activities/process_batch.py`: The new activity returns the full transformed dataset to the workflow, which risks hitting Temporal payload limits and inflating event history. Keep the large-data processing within the activity and return a compact summary or external reference instead.

## Weak Findings to Avoid

### Bad Review Comment

> This workflow feels too complex and should probably be refactored.

**Why bad**: This is not actionable and does not identify a concrete Temporal risk.

### Bad Review Comment

> I would rename this helper because I do not like the current name.

**Why bad**: Naming preference is low value unless it hides behaviour or correctness risk.

## Review Summary

**Remember**: your role is to find deterministic, operational, and behavioural risks early. Prioritise issues that could break replay, overload event history, block workers, change retry semantics, or create production-only failures.
