---
applyTo: "**/*"
---

# Agent instructions for Charm Tech Python library development

## Project Overview
Charm Tech develops libraries and tools for building charms in the Juju ecosystem.

The primary library is `ops`, a Python framework for writing Kubernetes and machine charms; the canonical/operator repository also includes `ops-scenario` (a state-transition testing framework) and `ops-tracing` (observability integration).

In addition to Ops, the team maintains Pebble, a lightweight container management system primarily used by charms to manage workloads inside containers. Pebble is a Go application - there is a Python client library included in the `ops` package.

The team also maintains Jubilant (a Pythonic wrapper of the Juju CLI, primarily used in charm integration tests), Concierge (a Go tool that configures dev and test environments for charming), a collection of charm libraries, and various other small projects.

These are a mature, production libraries and tools used by thousands of charms. Changes require careful consideration of backward compatibility and testing.

## Important Notes

### Backward Compatibility
- **Always** preserve backward compatibility in public APIs
- **Document** all breaking changes in commit messages
- **Always** preserve existing behavior unless fixing a bug

## When Making Changes

### Code Modifications
1. **Read existing code** before proposing changes
2. **Check tests** - examine tests for similar test patterns
3. **Verify changes** - execute `tox`, `just`, or `make` (depending on the project) after changes to ensure linting and unit tests pass

## Development Standards

### Language & Type Checking
- Follow conventions in [STYLE.md](https://github.com/canonical/operator/blob/main/STYLE.md) - all Charm Tech projects use these standards, not just the ones in the operator repo
- Use Ruff for formatting (`tox -e format`, `just format`, `make format`)
- Python 3.10+ with **full type hints** required (check with lint)
- Use modern `x: int | None` annotations, not old-style `x: Optional[int]`
- Always provide a return type, other than for `__init__` and in test code

### Import Style
```python
# DO: Import modules, not objects (except typing)
import ops
import subprocess
from typing import Generator  # typing is an exception

class MyCharm(ops.CharmBase):
    def handler(self, event: ops.PebbleReadyEvent):
        subprocess.run(['echo', 'hello'])

# DON'T: Import objects directly
from ops import CharmBase, PebbleReadyEvent  # Avoid this
```

## Documentation Guidelines

Follow the Diátaxis framework for documentation structure:
- **Tutorials** (`docs/tutorial/`) - Learning-oriented
- **How-to guides** (`docs/howto/`) - Task-oriented
- **Reference** - Generated from docstrings
- **Explanation** (`docs/explanation/`) - Understanding-oriented

Comments are always full sentences that end with punctuation. Avoid using comments to explain *what* the code is *doing*, use them (sparingly, as required) to explain *why* the code is doing what it is doing.

### Docstring Style

Use Google-style docstrings for all public APIs, with proper formatting. The text is used to generate reference documentation with Sphinx so must be appropriate ReST.

```python
def my_function(param: str, count: int = 1) -> list[str]:
    """Brief one-line summary.

    Longer description providing more context. Focus on what the function
    does for users, not implementation details.

    Args:
        param: Description of the parameter.
        count: Number of times to repeat. Defaults to 1.

    Returns:
        A list of processed strings.

    Raises:
        ValueError: If count is negative.

    Example:
        >>> my_function("hello", 2)
        ['hello', 'hello']
    """
```

**Documentation writing tips:**
- Use **active voice**: "Create a check" not "A check is created"
- Be **objective**: Avoid "simply", "easily", "just"
- Be **concise**: No long introductions, get to the point
- Use short sentences and simple phrasing
- Be consistent with choice of words
- Avoid words or phrases specific to US or UK English where possible, and use British English otherwise
- State conditions **positively**: What should happen, not what shouldn't
- Spell out abbreviations and avoid Latin: "for example" not "e.g."
- Use **sentence case** for headings

### Version Dependencies

Only document Juju version dependencies in docstrings:

```python
def new_feature():
    """Do something new.

    .. jujuadded:: 3.5
        Further functionality was added in Juju 3.6.
    """
```

Don't document Ops version changes in docstrings - that's in the changelog.

## Commit and Pull Request Guidelines

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for more details.

Use informative, detailed, conventional-commit styled commit messages as you work through a change. Each commit should be self-contained, building up to the overall PR story.

Follow conventional commit style in PR titles:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test additions or updates
- `chore:` - Maintenance tasks
- `ci:` - CI/CD changes

Examples:
- `feat: add support for Pebble notices`
- `fix: correct type hints for ConfigData`
- `docs: clarify usage of Container.push`

The project does not use conventional commit "scopes".

### Before Submitting
1. Add tests for any new functionality
2. Update docstrings for any API changes
3. Ensure backward compatibility
4. Use the configured tooling to format code
5. Use the configured tooling to check linting and types
6. Use the configured tooling to verify unit tests pass - avoid drops in coverage
7. Run `make html` in the `docs` folder to ensure that the documentation can be generated
8. Search the explanation, how-to, and tutorial documentation in the `docs` folder for topics related to the changes, then suggest places that might need expanding/altering
