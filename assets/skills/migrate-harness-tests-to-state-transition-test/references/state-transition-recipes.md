# State-Transition Test Recipes

The snippets below turn the Harness examples from the official migration guide into reusable patterns. Replace identifiers with your charm-specific names.

## Actions

```python
from ops import testing

def test_<action>():
    ctx = testing.Context(MyCharm)
    state_in = testing.State(relations={...}, containers={...})
    state_out = ctx.run(
        ctx.on.action("<action-name>", params={"foo": "bar"}),
        state_in,
    )
    assert ctx.action_results == {"foo": "bar"}
    assert state_out.unit_status == testing.ActiveStatus()
```

**Why:** Mirrors the "Test a minimal action" and "Test the action" sections of the Canonical guide. Add `pytest.raises(testing.ActionFailed)` to capture failure paths.

## Relation data changes

```python
from ops import testing

rel = testing.Relation(
    endpoint="database",
    remote_app_data={"endpoints": "bar.local:5678"},
)
state_in = testing.State(relations={rel})
ctx.run(ctx.on.relation_changed(rel), state_in)
```

- Build the desired post-change relation data directly into `state_in`.
- Monkeypatch charm helpers (`write_workload_config`, `get_endpoint_from_relation`) to assert side effects.

## Pebble-ready containers

```python
from ops import testing

container = testing.Container("my-container", can_connect=True)
state_in = testing.State(containers={container})
state_out = ctx.run(ctx.on.pebble_ready(container), state_in)
updated = state_out.get_container(container.name)
assert "workload" in updated.plan.services
assert state_out.unit_status == testing.ActiveStatus()
```

- Provide `service_statuses` or layers up front when `_on_collect_status` inspects them.
- Remember that the container objects in `state_out` are new instances; do not assert on `container`.

## Status reporting (collect-status)

```python
from ops import pebble, testing

layer = pebble.Layer({
    "services": {
        "workload": {
            "command": "run",
            "startup": "enabled",
        }
    }
})
container = testing.Container(
    "my-container",
    layers={"base": layer},
    service_statuses={"workload": pebble.ServiceStatus.ACTIVE},
    can_connect=True,
)
state_in = testing.State(containers={container})
state_out = ctx.run(ctx.on.update_status(), state_in)
assert state_out.unit_status == testing.ActiveStatus()
```

- Create negative variants (`can_connect=False`, `service_statuses` inactive) to cover maintenance branches.

## Failure cases

```python
import pytest
from ops import testing

with pytest.raises(testing.ActionFailed) as exc:
    ctx.run(ctx.on.action("get-value", params={"value": "please fail"}), state_in)
assert exc.value.message == "Action failed, as requested"
```

- When events raise `ops.ModelError`, wrap `ctx.run` in `pytest.raises` and assert on the exception data.

## Quick review checklist

- Does the event under test match what triggered `harness.<helper>` originally?
- Is the entire state defined before calling `ctx.run`? (No incremental Harness mutations.)
- Are collect-status side effects satisfied (containers, pebble layers, services)?
- Did you assert on `state_out` and not on mutated inputs?
