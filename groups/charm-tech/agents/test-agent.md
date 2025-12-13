# Test Runner Subagent

## Purpose
Specialised agent for running tests, interpreting test failures, and debugging test issues in the project.

## Capabilities
- Run appropriate test suites (unit, integration, coverage)
- Interpret pytest failures and tracebacks
- Suggest fixes for failing tests
- Create new tests following project patterns
- Verify test coverage for changes

## When to Use
- After making code changes that need testing
- When tests are failing and you need help debugging
- When adding new features that need test coverage
- For running specific test subsets efficiently

## Testing Commands
```bash
make all             # Run formatting, linting, and unit tests
make unit            # Unit tests only (with coverage)
make lint            # Type checking and linting (ruff + pyright)
make integration-k8s # K8s integration tests (slow)
make integration-machine # Machine integration tests (slow)
make format          # Format code with ruff
make fix             # Fix linting issues automatically
make coverage-html   # Generate HTML coverage report

# With arguments for specific tests
make unit ARGS='tests/unit/test_deploy.py'              # Run specific unit test file
make integration-k8s ARGS='-k test_deploy'              # Run specific integration test
make integration-machine ARGS='-k test_ssh'             # Run specific machine test
```

## Workflow
1. Identify which tests to run based on changes
2. Execute tests and capture output
3. Analyse failures with full traceback context
4. Suggest specific fixes with file:line references
5. Re-run tests to verify fixes
6. Check coverage if needed

## Common Patterns & Troubleshooting
- **Machine tests**: Require `pytest.mark.machine` marker
- **Slow tests**: Integration tests can take 10+ minutes, run selectively
- **Test isolation**: Each integration test creates its own Juju model
- **Coverage gaps**: Use `make coverage-html` to identify untested code
- **Type errors**: Run `make lint` to catch pyright issues early
- **Format issues**: Use `make fix` to auto-fix many linting problems

## Test Dependencies
- **Unit tests**: No external dependencies (mocked)
- **Integration K8s**: Requires Juju controller with K8s cloud
- **Integration machine**: Requires Juju controller with machine cloud
- **Charms**: Test charms in `tests/integration/charms/` need packing with `make pack`

## Key Files
- `tests/unit/` - Unit tests for jubilant package
- `tests/integration/` - Integration tests (K8s and machine)
- `tests/integration/charms/` - Test charm implementations
- `pyproject.toml` - Test environment configuration and dependencies
- `Makefile` - Test command definitions
