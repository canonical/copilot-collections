# Harness → State-Transition Migration Checklist

Source of truth: [How to migrate unit tests from Harness](https://documentation.ubuntu.com/ops/latest/howto/legacy/migrate-unit-tests-from-harness/).

## 1. Inventory harness usage

- Run `python3 .github/skills/migrate-harness-tests-to-state-transition-test/scripts/find_harness_tests.py` from the charm root to list every file that still instantiates `testing.Harness`.
- Sort the output by suite so you can migrate one charm surface area (actions, relations, pebble, status) at a time.
- Capture the current assertions before refactoring; you will re-use them after the state-transition rewrite.

## 2. Pick the event and define states

Each migrated test must answer three questions before you touch any code:

1. **Event to simulate** – Map Harness helpers to the equivalent event trigger.
2. **Input state** – Everything Juju already knows *before* the event fires (containers, relations, config, stored state).
3. **Expected output state** – Assertions to run against `ctx.run(...)` return values.

| Harness helper | State-transition replacement | Notes |
| --- | --- | --- |
| `harness.begin*`, `add_relation`, `add_storage`, `set_leader` | `testing.State(...)` | Build the entire state upfront instead of mutating Harness step-by-step. |
| `harness.charm.on.<event>.emit` | `ctx.run(ctx.on.<event>(...), state_in)` | Use the dedicated `ctx.on.*` factory for each Juju event. |
| `harness.run_action` | `ctx.on.action("name", params=...)` | Inspect `ctx.action_results` or capture exceptions such as `testing.ActionFailed`. |
| `harness.evaluate_status` | Automatic after each `ctx.run(...)` | Provide containers/services inside `State`; collect-status fires for free. |

## 3. Model supporting objects explicitly

- Build mock containers with `testing.Container` (set `can_connect`, `plan`, `service_statuses`).
- Build relations with `testing.Relation(endpoint=..., remote_app_data=...)`; remember that `State` should already contain "new" data.
- Use monkeypatching for workload side effects (files, network clients) exactly like Harness tests did.

## 4. Recreate assertions per scenario

Follow the pattern from the official guide:

1. Instantiate `ctx = testing.Context(Charm)` once per test.
2. Create `state_in = testing.State(...)` with only the data needed for the chosen event.
3. Call `state_out = ctx.run(ctx.on.<event>(...), state_in)`.
4. Assert against:
   - `state_out` (relations, containers, unit/app status)
   - `ctx.action_results` / `ctx.logs`
   - Workload fakes that were monkeypatched into the Charm.

## 5. Cover collect-status explicitly

State-transition tests always execute `collect_unit_status`/`collect_app_status`. Make sure the input state can satisfy `_on_collect_status` hooks:

- Provide mock containers or pebble layers for workloads that access Pebble.
- Add negative variants (container down, relation missing) so `_on_collect_status` branches stay tested.

## 6. Validate and retire Harness

- Run the migrated tests (`tox -e unit` or `pytest tests/unit`) to prove behavioral parity.
- Delete the original Harness fixtures and helpers once a suite has been migrated.
- Keep the `find_harness_tests.py` report clean in CI to ensure the repository stays on the state-transition style.
