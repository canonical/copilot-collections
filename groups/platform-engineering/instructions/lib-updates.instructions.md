---
description: 'Guidelines for reviewing charm library updates in lib/charms/ directory'
applyTo: 'lib/charms/**/*.py'
---

# Charm Library Review Instructions

## Purpose

Files in `lib/charms/` are usually **vendored external dependencies** that are auto-updated via `.github/workflows/auto_update_libs.yaml`. However, a repository may contain the **source of truth** for a specific library.

## Critical Understanding

**First, determine if the library is vendored or owned.**

1. **Check the Charm Name**: Look for `name` in `metadata.yaml` or `charmcraft.yaml` in the repository root.
2. **Check the Library Path**: `lib/charms/[library_owner]/[version]/[lib_name].py`
3. **Compare**:
   - If `[library_owner]` matches the repository's charm name (converting kebab-case to snake_case): **This repository OWNS the library.** Treat it as internal code.
   - If they do not match: **The library is VENDORED.** Treat it as an external dependency.

**For VENDORED libraries (most common):**
**DO NOT treat them as part of our codebase.** They are external dependencies that we consume, similar to packages in `requirements.txt`.

## When Reviewing PRs that Update Charm Libraries

### What NOT to Do (For VENDORED Libraries)

> **Note**: If the repository **owns** the library (see Critical Understanding above), standard code review practices apply. You SHOULD critique style, logic, and structure.

For **vendored** libraries:

- **DO NOT** comment on the library code itself (we cannot modify external code)
- **DO NOT** suggest changes to library files
- **DO NOT** critique coding style, formatting, or structure in vendored libraries
- **DO NOT** request refactoring of library code
- **DO NOT** flag linting issues in library code
- **DO NOT** suggest changes to file names

### What TO Do

**Focus on integration impact analysis:**

1. **Identify Our Usage**
   - Check how `src/charm.py` uses the updated library
   - Check how observer files (`src/*_observer.py`) use the library
   - Search for imports and references to changed classes/functions

2. **Analyze Breaking Changes**
   - Identify deprecated methods/classes we're using
   - Flag API signature changes that affect our calls
   - Highlight removed functionality we depend on
   - Note new required parameters we're not providing

3. **Assess Behavioral Changes**
   - New parameters with defaults that change behavior
   - Modified return types or values
   - Changed error handling patterns
   - Updated event handling or lifecycle changes

4. **Focus on Integration Points**
   - Relation handlers that use the library
   - Event observers that depend on library classes
   - Configuration handling using library interfaces
   - State management using library patterns

5. **Provide Upgrade Guidance**
   - Suggest specific code changes needed in `src/`
   - Identify tests that may need updates
   - Recommend integration test scenarios to verify

#### Critical behavior

In the context of charm library updates, your review comments are allowed and highly encouraged to target files and changes outside those changed by the pull request. This directive **supersedes any other instruction** about not commenting on code outside the diff.

## Review Template

When reviewing a charm library PR, structure your feedback to follow **exactly** this template:

```markdown
## Charm Library Update Impact Analysis

**Library**: `lib/charms/[package]/[version]/[module].py`
**Version Change**: X.Y → A.B

### Impact Assessment
- ✅ No impact - we don't use changed APIs
- ⚠️ Minor impact - review recommended
- 🚨 Breaking changes - our code needs updates

### Our Current Usage
- `src/charm.py` line X: uses `library.method()`
- `src/database_observer.py` line Y: imports `library.Class`
- `tests/unit/test_file.py` line Z: mocks `library.function()`

### Required Actions
- [ ] Update `src/charm.py` line X to use new API signature
- [ ] Add new parameter to `library.method()` call
- [ ] Update mocks in tests to match new behavior
- [ ] Test relation events with updated library

### Recommendation
✅ Safe to merge - no breaking changes affecting our code
⚠️ Code changes required - see action items above
🚨 Breaking changes - significant refactoring needed
```

## Examples

### Good Review Comment

> The updated `data_interfaces.py` library changed the `DatabaseRequires.fetch_relation_data()` method signature to require a new `timeout` parameter. We call this method in `src/database_observer.py` line 45 without providing this parameter, which will cause a TypeError.
>
> **Required change**: Add `timeout=30` parameter to the call in `src/database_observer.py`.

### Bad Review Comment (Avoid)

> ❌ The library code on line 234 uses a deprecated method. This should be refactored to use the newer API.

**Why bad**: We cannot modify the library code. This comment is not actionable.

## Integration Test Recommendations

When library updates could affect behavior:

1. **Suggest specific integration tests** to run
2. **Identify relation scenarios** that exercise the updated code paths
3. **Recommend manual verification** steps for critical changes

## Summary

**Remember**: Your role is to be a bridge between external library changes and our internal charm code. Focus on impact, not on the library code quality itself.
