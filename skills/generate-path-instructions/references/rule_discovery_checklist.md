# Rule Discovery Checklist

This checklist guides you through extracting scope-specific rules from code, configuration, and documentation.

**Key principle:** Extract rules that apply ONLY to the target scope, not generic project-wide rules.

---

## Phase 1: Code Sample Analysis

### Read Representative Files
- [ ] **Select 3-5 sample files from target scope:**
  ```bash
  # Example: Testing scope
  cat tests/test_auth.py
  cat tests/test_api.py
  cat tests/integration/test_database.py
  
  # Example: Documentation scope
  cat docs/getting-started.md
  cat docs/api/authentication.md
  cat docs/tutorials/first-app.md
  ```

### Identify Structural Patterns
- [ ] **Naming conventions:**
  - File naming: test_*, *Test, *Spec, *_spec?
  - Function/method naming: test_*, should_*, it_*?
  - Class naming: Test*, *Test, *Spec?
  - Variable naming: camelCase, snake_case, PascalCase?

- [ ] **Import patterns:**
  - Common libraries imported in all files?
  - Specific testing utilities always used?
  - Framework-specific imports?
  - Example:
    ```python
    # Found in all test files:
    import pytest
    from unittest.mock import Mock, patch
    from myapp.testing import fixtures
    ```

- [ ] **Structural organization:**
  - Classes vs functions?
  - Setup/teardown patterns?
  - Fixture usage?
  - Helper function patterns?

### Identify Content Patterns
- [ ] **Assertion styles:**
  - `assert` statements?
  - `expect().toBe()`?
  - `should.equal()`?
  - Framework-specific matchers?

- [ ] **Documentation patterns:**
  - Docstrings always present?
  - Specific docstring format (Google, NumPy, reST)?
  - Comments style?
  - Type hints/annotations?

- [ ] **Error handling:**
  - `pytest.raises()`?
  - `try/except` patterns?
  - `assertRaises()`?
  - Expected error conventions?

---

## Phase 2: Configuration File Analysis

### Framework Configuration
- [ ] **Test runner configuration:**
  ```bash
  # pytest
  cat pytest.ini
  grep -A 10 "\[tool.pytest\]" pyproject.toml
  
  # Jest
  cat jest.config.js
  
  # Go
  grep -r "testing" go.mod
  ```

- [ ] **Extract relevant settings:**
  - Test discovery patterns
  - Required plugins/extensions
  - Coverage requirements
  - Markers/tags usage

### Linter/Formatter Configuration
- [ ] **Check linter rules for scope:**
  ```bash
  # Python
  cat .pylintrc
  grep -A 5 "\[tool.black\]" pyproject.toml
  
  # JavaScript
  cat .eslintrc.json
  cat .prettierrc
  
  # Go
  cat .golangci.yml
  ```

- [ ] **Extract scope-specific rules:**
  - Are there specific rules for test files?
  - Documentation linting rules?
  - Import order requirements?
  - Line length limits?

---

## Phase 3: Documentation Review

### Contributing Guidelines
- [ ] **Search CONTRIBUTING.md for scope-specific sections:**
  ```bash
  grep -A 10 -i "testing" CONTRIBUTING.md
  grep -A 10 -i "documentation" CONTRIBUTING.md
  grep -A 10 -i "components" CONTRIBUTING.md
  ```

- [ ] **Extract explicit rules:**
  - "All tests must use pytest fixtures"
  - "API docs must include code examples"
  - "Components must include TypeScript interfaces"

### Style Guides
- [ ] **Check for style guide documents:**
  ```bash
  cat docs/STYLE_GUIDE.md
  cat docs/development/testing-guide.md
  cat docs/development/documentation-guide.md
  ```

- [ ] **Extract scope-specific conventions:**
  - Testing best practices
  - Documentation formatting
  - Code organization patterns

### README Sections
- [ ] **Check README for framework mentions:**
  ```bash
  grep -A 5 "Testing" README.md
  grep -A 5 "Development" README.md
  ```

---

## Phase 4: Framework Best Practices

### Apply Framework-Specific Conventions

Based on detected framework, include standard best practices:

#### Testing Frameworks

**pytest (Python):**
- Use fixtures instead of setup/teardown
- Use `pytest.mark` for test categorization
- Follow naming: `test_*.py` or `*_test.py`
- Use `pytest.raises()` for exception testing
- Parametrize with `@pytest.mark.parametrize`

**Jest/Vitest (JavaScript/TypeScript):**
- Use `describe` blocks for grouping
- Use `test` or `it` for test cases
- Use `beforeEach`/`afterEach` for setup
- Mock with `jest.mock()` or `vi.mock()`
- Follow naming: `*.test.ts` or `*.spec.ts`

**Go testing:**
- Follow naming: `*_test.go`
- Use table-driven tests
- Use `t.Helper()` for helper functions
- Use `testing.TB` interface
- Name tests: `TestXxx` or `BenchmarkXxx`

**JUnit (Java):**
- Use `@Test` annotations
- Use `@BeforeEach`/`@AfterEach` for setup
- Follow naming: `*Test.java`
- Use descriptive test method names
- Use AssertJ or Hamcrest matchers

#### Documentation Frameworks

**MkDocs:**
- Use ATX headers (# ## ###)
- Include code fences with language tags
- Use admonitions (!!! note, !!! warning)
- Follow nav structure from mkdocs.yml

**Sphinx:**
- Use reStructuredText
- Include :param: and :returns: in docstrings
- Use directives (.. code-block::)
- Cross-reference with :ref:

**JSDoc/TypeDoc:**
- Use @param, @returns, @example tags
- Include type annotations
- Document all public APIs
- Use @deprecated for deprecated items

#### Component Frameworks

**React:**
- Use functional components with hooks
- PropTypes or TypeScript interfaces
- Destructure props
- Use PascalCase for component names
- One component per file

**Vue:**
- Use Composition API or Options API (consistent)
- Define props with types
- Use kebab-case for component files
- Include scoped styles

---

## Phase 5: Scope-Specific vs Global Rules

### Apply Context Economics Filter

For each rule discovered, ask: **Is this scope-specific or global?**

| ✅ Scope-Specific (Include) | ❌ Global (Exclude) |
|-----------------------------|---------------------|
| "Use pytest fixtures not setUp/tearDown" | "Use 4 spaces for indentation" |
| "Tests must include docstrings with Given/When/Then" | "Keep functions under 50 lines" |
| "Docs must follow ADR template" | "Use meaningful variable names" |
| "API docs must include request/response examples" | "Write descriptive commit messages" |
| "K8s manifests must set resource limits" | "Follow semantic versioning" |
| "React components must export TypeScript interfaces" | "Keep dependencies up to date" |
| "Integration tests must use transaction rollback" | "Avoid commented code" |

**Test:**
- Would this rule apply to files OUTSIDE the scope? → Global
- Is this rule only relevant to THIS scope? → Scope-specific

---

## Phase 6: Example Extraction

### Find Real Examples from Codebase

- [ ] **Good examples:**
  ```bash
  # Find well-structured files to use as examples
  # Look for recent, well-maintained files
  git log --name-only --pretty=format: tests/ | sort | uniq -c | sort -rn | head -5
  ```

- [ ] **Extract specific patterns:**
  - Good: File from codebase that exemplifies rules
  - Bad: Theoretical example that doesn't exist in repo
  
- [ ] **Keep examples concise:**
  - 10-20 lines maximum
  - Focus on demonstrating 1-2 rules clearly
  - Use actual code from repo (with sensitive data removed)

---

## What to Do with Findings

### Synthesize Scope-Specific Rules

After completing the checklist, organize rules into categories:

#### 1. Naming Conventions
Example:
- **Files:** `test_*.py` for unit tests, `integration_test_*.py` for integration tests
- **Functions:** `test_*` with descriptive names (e.g., `test_user_login_with_valid_credentials`)
- **Classes:** `Test*` for test classes

#### 2. Structure Requirements
Example:
- Use pytest fixtures defined in `tests/conftest.py`
- Group related tests in classes
- Include module-level docstring explaining test scope

#### 3. Content Standards
Example:
- All tests must include docstring with Given/When/Then format
- Use `@pytest.mark.integration` for integration tests
- Mock external dependencies with `@patch` decorator

#### 4. Framework-Specific Patterns
Example:
- Use `pytest.fixture(scope="function")` for test-specific fixtures
- Use `pytest.mark.parametrize` for data-driven tests
- Use `pytest.raises()` for exception testing

#### 5. Quality Requirements
Example:
- Tests must be isolated (no shared state)
- Integration tests must clean up resources in teardown
- Minimum 80% coverage for new code

### Create Examples Section

For each major rule, include:

**Rule:** Use pytest fixtures instead of setUp/tearDown

**Good Example (from tests/test_auth.py):**
```python
@pytest.fixture
def authenticated_client(client, user):
    """Fixture providing an authenticated API client."""
    client.login(user)
    return client

def test_protected_endpoint(authenticated_client):
    """Verify protected endpoint requires authentication."""
    response = authenticated_client.get('/api/protected')
    assert response.status_code == 200
```

**Why:** Fixtures are reusable, composable, and provide better dependency injection than setUp methods.

---

## Common Pitfalls

### ❌ DON'T:
- Include rules that apply to entire codebase ("use meaningful names")
- Use theoretical examples that don't exist in the repo
- Copy rules from other projects without validating they apply
- Include outdated patterns that aren't used anymore
- Mix framework-specific rules from different frameworks

### ✅ DO:
- Focus on rules specific to the target scope
- Use real examples from the actual codebase
- Validate rules by checking if they're followed in recent files
- Include "why" explanations for non-obvious rules
- Reference framework documentation for standard patterns

---

## Output

**Deliverable:** List of scope-specific rules organized by category with real examples from the codebase.

**Next:** Use these rules in Step 5 (Template Application)
