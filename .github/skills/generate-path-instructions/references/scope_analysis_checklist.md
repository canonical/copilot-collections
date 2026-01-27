# Scope Analysis Checklist

This checklist guides you through discovering the target scope for path-specific instructions.

---

## Phase 1: Target Identification

### Clarify User Intent
- [ ] **What does the user want to scope?**
  - Specific directory? (e.g., "tests/", "docs/", "src/components/")
  - File type? (e.g., "test files", "Markdown docs", "YAML configs")
  - Framework/tool? (e.g., "pytest tests", "React components", "Kubernetes manifests")
  - Content type? (e.g., "API documentation", "integration tests", "Terraform configs")

- [ ] **Is the scope ambiguous?**
  - If user says "test files" → Which tests? Unit? Integration? All languages?
  - If user says "documentation" → User docs? API docs? ADRs? All .md files?
  - If user says "config files" → Which format? YAML? JSON? TOML? All configs?
  - **Action:** Ask clarifying questions before proceeding

---

## Phase 2: Repository Exploration

### Directory Structure Analysis
- [ ] **List repository top-level structure:**
  ```bash
  ls -la
  ```
  
- [ ] **Identify relevant directories:**
  - Code directories: `src/`, `lib/`, `app/`, `pkg/`
  - Test directories: `tests/`, `test/`, `__tests__/`, `spec/`
  - Documentation: `docs/`, `doc/`, `documentation/`
  - Configuration: `config/`, `.github/`, `infrastructure/`
  - Scripts: `scripts/`, `bin/`, `tools/`

- [ ] **Explore target directory structure (if known):**
  ```bash
  # Example: If targeting tests
  tree tests/ -L 2
  # or
  find tests/ -type f | head -20
  ```

### File Pattern Discovery
- [ ] **Find files by extension in target area:**
  ```bash
  # Example: Python files in tests/
  find tests/ -name "*.py" | head -10
  
  # Example: Markdown in docs/
  find docs/ -name "*.md" | head -10
  
  # Example: YAML everywhere
  find . -name "*.yml" -o -name "*.yaml" | head -10
  ```

- [ ] **Analyze naming patterns:**
  - Test files: `test_*.py`, `*_test.go`, `*.test.js`, `*.spec.ts`
  - Components: `*.component.tsx`, `*View.swift`, `*Fragment.kt`
  - Configs: `*.config.js`, `*rc`, `.*.yml`
  - Note: Which patterns are used in THIS repo?

- [ ] **Count files by pattern (validate scope size):**
  ```bash
  # How many files would match?
  find tests/ -name "*.py" | wc -l
  ```

---

## Phase 3: Framework Detection

### Language & Framework Identification
- [ ] **Check for test frameworks:**
  - **Python:** pytest (test_*.py, conftest.py), unittest
  - **JavaScript/TypeScript:** Jest (*.test.js, *.spec.js), Mocha, Vitest
  - **Go:** *_test.go files
  - **Java:** JUnit (*Test.java), TestNG
  - **Ruby:** RSpec (*_spec.rb)

- [ ] **Check for documentation tools:**
  - **MkDocs:** mkdocs.yml
  - **Sphinx:** conf.py, docs/source/
  - **Docusaurus:** docusaurus.config.js
  - **Hugo:** config.toml
  - **Jekyll:** _config.yml
  - **JSDoc/TypeDoc:** jsdoc.json, typedoc.json

- [ ] **Check for config management:**
  - **Kubernetes:** *.yaml with kind/apiVersion
  - **Terraform:** *.tf files
  - **Docker:** Dockerfile, docker-compose.yml
  - **Ansible:** playbooks, roles/
  - **Helm:** Chart.yaml, values.yaml

- [ ] **Check for component frameworks:**
  - **React:** package.json with react dependency
  - **Vue:** *.vue files
  - **Angular:** angular.json
  - **Svelte:** *.svelte files

### Configuration File Analysis
- [ ] **Check for linter/formatter configs (extract conventions):**
  - `.eslintrc*`, `prettier.config.js`
  - `.pylintrc`, `pyproject.toml`, `.flake8`
  - `.golangci.yml`
  - `.rubocop.yml`

- [ ] **Check for test runner configs:**
  - `pytest.ini`, `pyproject.toml` [tool.pytest]
  - `jest.config.js`, `vitest.config.ts`
  - `phpunit.xml`

---

## Phase 4: Existing Conventions Discovery

### Sample File Analysis
- [ ] **Read 3-5 sample files from target scope:**
  ```bash
  # Example: Sample test files
  cat tests/test_auth.py
  cat tests/test_api.py
  cat tests/integration/test_database.py
  ```

- [ ] **Identify patterns in samples:**
  - Naming: test_*, *_test, *Test, *Spec?
  - Structure: Classes? Functions? Fixtures?
  - Imports: Common testing utilities?
  - Assertions: assert, expect, should?
  - Annotations: @pytest.mark, @Test, describe()?

### Documentation Review
- [ ] **Check CONTRIBUTING.md for scope-specific rules:**
  ```bash
  grep -A 5 -i "test" CONTRIBUTING.md
  grep -A 5 -i "documentation" CONTRIBUTING.md
  ```

- [ ] **Check README for conventions:**
  ```bash
  grep -A 3 -i "testing" README.md
  grep -A 3 -i "development" README.md
  ```

- [ ] **Check for style guides:**
  - `STYLE_GUIDE.md`
  - `docs/development/testing.md`
  - `docs/contributing/documentation.md`

---

## Phase 5: Scope Boundary Definition

### Define What's In Scope
- [ ] **Specific directories:**
  - Example: "tests/" but not "tests/fixtures/"
  - Example: "docs/api/" but not "docs/user-guide/"

- [ ] **Specific file patterns:**
  - Example: "*.test.ts" but not "*.spec.ts"
  - Example: "test_*.py" but not "*_test.py"

- [ ] **Specific frameworks:**
  - Example: "React components in src/components/" but not all .tsx files
  - Example: "Kubernetes manifests in k8s/" but not all YAML files

### Define What's Out of Scope
- [ ] **Exclusions:**
  - Files that match pattern but shouldn't (e.g., fixtures, mocks, generated files)
  - Directories that should use different instructions
  - Files better covered by global instructions

### Validate Scope Size
- [ ] **Is the scope too broad?**
  - Example: All .py files → Too broad, use global instructions
  - Example: All tests → Maybe too broad, consider splitting by test type

- [ ] **Is the scope too narrow?**
  - Example: Single file → Don't use path instructions, just edit the file
  - Example: 2-3 files → Might be too narrow, consider broader pattern

**Sweet spot:** 10-500 files with shared conventions

---

## What to Do with Findings

### Synthesize Scope Definition

After completing the checklist, document:

1. **Target Scope Summary**
   - "Python test files in tests/ using pytest"
   - "API documentation in docs/api/ using Markdown"
   - "Kubernetes manifests in k8s/ directory"

2. **File Patterns Found**
   - "tests/test_*.py" (37 files)
   - "tests/integration/*_test.py" (12 files)
   - Combined: ~49 test files

3. **Framework Detected**
   - pytest with fixtures
   - Uses pytest.mark decorators
   - conftest.py for shared fixtures

4. **Existing Conventions**
   - test_* naming for unit tests
   - *_test naming for integration tests
   - Classes start with Test
   - Heavy use of fixtures

5. **Scope Boundaries**
   - ✅ Include: tests/**/*.py
   - ❌ Exclude: tests/fixtures/ (not test code)
   - ❌ Exclude: tests/conftest.py (configuration, not tests)

**Next:** Use this information in Step 3 (Pattern Construction)
