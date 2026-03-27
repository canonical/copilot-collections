# Glob Pattern Reference for Path-Specific Instructions

This document provides a comprehensive reference for constructing valid glob patterns for the `applyTo` directive in path-specific instruction files.

## Glob Pattern Syntax

| Pattern | Description | Example | Matches |
| :--- | :--- | :--- | :--- |
| `*` | Matches any characters except `/` | `*.py` | `test.py`, `main.py` |
| `**` | Matches any characters including `/` (recursive) | `**/*.py` | `src/main.py`, `tests/unit/test.py` |
| `?` | Matches a single character | `test?.py` | `test1.py`, `testA.py` |
| `[abc]` | Matches any character in the set | `test[123].py` | `test1.py`, `test2.py` |
| `{a,b}` | Matches either `a` or `b` | `*.{js,ts}` | `main.js`, `app.ts` |

## Common Patterns

### File Extension Matching

```yaml
# Match all Python files recursively
applyTo:
  - "**/*.py"

# Match JavaScript and TypeScript files
applyTo:
  - "**/*.js"
  - "**/*.ts"

# Match test files (multiple naming conventions)
applyTo:
  - "**/*.test.js"
  - "**/*.spec.js"
```

### Directory-Specific Matching

```yaml
# Match all files in the src/ directory
applyTo:
  - "src/**/*"

# Match all files in tests/ subdirectories
applyTo:
  - "tests/**/*"

# Match files in a specific subdirectory
applyTo:
  - "src/components/**/*.tsx"
```

### Combination Patterns

```yaml
# Match Python test files in tests/ directory
applyTo:
  - "tests/**/*.py"
  - "test_*.py"

# Match React components (TypeScript and JavaScript)
applyTo:
  - "src/components/**/*.tsx"
  - "src/components/**/*.jsx"

# Match configuration files at the root
applyTo:
  - "*.config.js"
  - "*.config.ts"
```

## Testing Patterns

### Using the test_glob_pattern.py Script

The skill includes a dedicated testing utility located at:
```
.github/skills/generate-path-instructions-v2/tools/test_glob_pattern.py
```

**Usage:**
```bash
# Test a single pattern
python .github/skills/generate-path-instructions-v2/tools/test_glob_pattern.py "**/*.py"

# Test multiple patterns
python .github/skills/generate-path-instructions-v2/tools/test_glob_pattern.py "**/*.test.ts" "**/*.spec.ts"

# Test patterns from an instruction file
python .github/skills/generate-path-instructions-v2/tools/test_glob_pattern.py --file .github/instructions/testing.md
```

**Output includes:**
- Number of matched files
- Sample matched files (first 10)
- Pattern coverage analysis
- Overlap detection between patterns

### Manual Testing with Shell Tools

```bash
# List all files matching a pattern
find . -path "./tests/**/*.py"

# Count matching files
find . -name "*.test.ts" | wc -l

# Preview matches with tree (if available)
tree -P "*.test.ts"

# Use glob with Python
python -c "import glob; print('\n'.join(glob.glob('**/*.py', recursive=True)))"
```

## Common Mistakes

### ❌ Anti-Pattern: Overly Broad Patterns

**Problem:** Matches unintended files, causing instructions to apply everywhere
```yaml
# BAD: Matches literally every file
applyTo:
  - "**/*"

# BAD: Matches all Python files, including vendored/generated code
applyTo:
  - "**/*.py"
```

**Solution:** Be specific about directories
```yaml
# GOOD: Scoped to relevant directories
applyTo:
  - "src/**/*.py"
  - "tests/**/*.py"
```

### ❌ Anti-Pattern: Absolute Paths

**Problem:** Patterns break on different machines/environments
```yaml
# BAD: Uses absolute path
applyTo:
  - "/home/user/project/src/**/*"

# BAD: Uses environment variables
applyTo:
  - "$PROJECT_ROOT/src/**/*"
```

**Solution:** Always use repository-relative paths
```yaml
# GOOD: Relative to repo root
applyTo:
  - "src/**/*"
```

### ❌ Anti-Pattern: Incomplete Coverage

**Problem:** Misses files due to naming variations
```yaml
# BAD: Only catches one test convention
applyTo:
  - "**/*.test.js"
# Misses: *.spec.js, test_*.js, *_test.js
```

**Solution:** Include all relevant conventions
```yaml
# GOOD: Covers multiple conventions
applyTo:
  - "**/*.test.js"
  - "**/*.spec.js"
  - "**/test_*.js"
  - "**/*_test.js"
```

### ❌ Anti-Pattern: Case Sensitivity Issues

**Problem:** Patterns fail on case-insensitive filesystems
```yaml
# BAD: Won't match .PY or .Py on some systems
applyTo:
  - "**/*.py"
```

**Solution:** Test on target filesystem; consider multiple patterns
```yaml
# GOOD: Explicit about expected extensions
applyTo:
  - "**/*.py"
  # Add *.PY if needed based on team conventions
```

### ❌ Anti-Pattern: Trailing/Leading Slashes

**Problem:** May cause pattern to fail or behave unexpectedly
```yaml
# BAD: Leading slash treats as absolute
applyTo:
  - "/src/**/*.py"

# BAD: Trailing slash may be too restrictive
applyTo:
  - "src/**/*.py/"
```

**Solution:** Use clean, relative paths
```yaml
# GOOD: Clean pattern
applyTo:
  - "src/**/*.py"
```

### ❌ Anti-Pattern: Overlapping Patterns

**Problem:** Multiple instruction files match the same files
```yaml
# File 1: .github/instructions/python.md
applyTo:
  - "**/*.py"

# File 2: .github/instructions/testing.md
applyTo:
  - "tests/**/*.py"
# Results in duplicate/conflicting instructions for test files
```

**Solution:** Use mutually exclusive patterns or intentional layering
```yaml
# File 1: .github/instructions/python.md
applyTo:
  - "src/**/*.py"  # Only source code

# File 2: .github/instructions/testing.md
applyTo:
  - "tests/**/*.py"  # Only tests
```

## Pattern Refinement Workflow

### Step 1: Define Scope

Clearly identify what files need the instructions:
- Which directories? (`src/`, `tests/`, `docs/`)
- Which file types? (`.py`, `.ts`, `.go`)
- Which naming patterns? (`test_*`, `*.test.*`, `*_test.*`)

### Step 2: Draft Initial Pattern

Start broad, then narrow:
```yaml
# Initial: Too broad
applyTo:
  - "**/*.py"

# Refined: Scoped to directory
applyTo:
  - "src/**/*.py"

# Final: Exclude specific subdirectories if needed
applyTo:
  - "src/**/*.py"
  - "!src/vendor/**/*.py"  # If negation is supported
```

### Step 3: Test Pattern Coverage

Use the test script to validate:
```bash
# Check what files match
python .github/skills/generate-path-instructions-v2/tools/test_glob_pattern.py "src/**/*.py"

# Verify sample output
# Expected: src/main.py, src/utils/helper.py
# Unexpected: vendor/lib.py, tests/test.py
```

### Step 4: Verify in Repository

Manually inspect matched files:
```bash
# List matches
find . -path "./src/**/*.py" -type f

# Count matches
find . -path "./src/**/*.py" -type f | wc -l

# Sample files
find . -path "./src/**/*.py" -type f | head -10
```

### Step 5: Check for Gaps

Identify missed files:
```bash
# Find Python files NOT in src/ or tests/
comm -23 \
  <(find . -name "*.py" | sort) \
  <(find . -path "./src/**/*.py" -o -path "./tests/**/*.py" | sort)
```

### Step 6: Iterate and Refine

Adjust patterns based on findings:
```yaml
# Add missed patterns
applyTo:
  - "src/**/*.py"
  - "lib/**/*.py"  # Discovered during gap analysis

# Remove over-matches by being more specific
applyTo:
  - "src/app/**/*.py"  # Narrowed from src/**/*.py
```

### Step 7: Document and Review

Add comments explaining intent:
```yaml
# Python source files in application code (excludes tools, scripts, vendor)
applyTo:
  - "src/app/**/*.py"
  - "src/lib/**/*.py"
```

## Best Practices

### ✅ DO

* **Be Specific:** Use precise patterns to avoid over-matching
  ```yaml
  applyTo:
    - "tests/unit/**/*.py"  # Only unit tests
  ```

* **Use Multiple Patterns:** Cover different naming conventions
  ```yaml
  applyTo:
    - "**/*.test.ts"
    - "**/*.spec.ts"
  ```

* **Test Your Patterns:** Verify they match the intended files
  ```bash
  python .github/skills/generate-path-instructions-v2/tools/test_glob_pattern.py "**/*.test.ts"
  ```

* **Document Intent:** Add comments explaining the pattern scope
  ```yaml
  # React component files (TypeScript only)
  applyTo:
    - "src/components/**/*.tsx"
  ```

### ❌ DON'T

* **Over-Match:** Avoid patterns that are too broad
  ```yaml
  applyTo:
    - "**/*"  # Matches everything (too broad)
  ```

* **Use Absolute Paths:** Patterns are relative to the repo root
  ```yaml
  applyTo:
    - "/home/user/project/src/**/*"  # Invalid
  ```

* **Forget Edge Cases:** Consider all naming conventions
  ```yaml
  applyTo:
    - "**/*.test.js"  # Misses *.spec.js files
  ```

## Common Use Cases

### Python Projects

```yaml
# Python source files
applyTo:
  - "src/**/*.py"

# Python test files
applyTo:
  - "tests/**/*.py"
  - "test_*.py"
  - "*_test.py"

# Python notebooks
applyTo:
  - "**/*.ipynb"
```

### JavaScript/TypeScript Projects

```yaml
# React components
applyTo:
  - "src/components/**/*.tsx"
  - "src/components/**/*.jsx"

# Test files
applyTo:
  - "**/*.test.ts"
  - "**/*.test.js"
  - "**/*.spec.ts"
  - "**/*.spec.js"

# Configuration files
applyTo:
  - "*.config.{js,ts}"
  - ".*rc.js"
```

### Go Projects

```yaml
# Go source files
applyTo:
  - "**/*.go"

# Go test files
applyTo:
  - "**/*_test.go"

# Specific packages
applyTo:
  - "pkg/user/**/*.go"
```

### C/C++ Projects

```yaml
# Header files
applyTo:
  - "**/*.h"
  - "**/*.hpp"

# Source files
applyTo:
  - "**/*.c"
  - "**/*.cpp"

# Kernel-specific
applyTo:
  - "kernel/**/*.c"
```

## Advanced Patterns

### Exclude Patterns

Some glob implementations support negation (check your tooling):

```yaml
# Note: GitHub Copilot may not support negation
# This is for reference only
applyTo:
  - "src/**/*.ts"
  - "!src/**/*.test.ts"  # Exclude test files
```

### Multi-Level Matching

```yaml
# Match files two levels deep
applyTo:
  - "*/*/*.py"

# Match specific directory structure
applyTo:
  - "src/*/components/*.tsx"
```

## Troubleshooting

### Pattern Not Matching Files

1. **Check the path:** Ensure the path is relative to the repository root
2. **Verify the extension:** Check for case sensitivity (`.Py` vs `.py`)
3. **Test with the script:** Use `test_glob_pattern.py` to validate
4. **Check for typos:** Verify the pattern syntax
5. **Check hidden files:** Patterns may not match dotfiles by default

### Pattern Matching Too Many Files

1. **Add directory scoping:** Narrow the pattern to a specific directory
2. **Be more specific:** Add more constraints to the pattern
3. **Use multiple patterns:** Split broad patterns into specific ones
4. **Review with test script:** Use the testing tool to see all matches

### Pattern Not Working in GitHub Copilot

1. **Verify YAML syntax:** Ensure proper indentation and quoting
2. **Check for special characters:** Escape if necessary
3. **Test pattern locally:** Validate pattern works with standard glob tools
4. **Simplify pattern:** Complex patterns may not be fully supported

---

**Last Updated:** 2025
**Version:** 2.0
