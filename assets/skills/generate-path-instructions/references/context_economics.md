# Context Economics for Path Instructions

## Overview

Path-specific instructions allow you to scope rules to specific parts of your repository using glob patterns, avoiding context pollution and keeping your global instructions lean and focused.

## Path-Specific vs Global Instructions

### Global Instructions (`.github/copilot-instructions.md`)
- **Purpose**: Repository-wide constitutional rules that apply everywhere
- **Scope**: Entire repository, always loaded
- **Content**: Project identity, tech stack, universal coding standards
- **Size limit**: ~1000 lines (context budget constraint)
- **Examples**: Project description, primary languages, global conventions

### Path-Specific Instructions (`.github/instructions/*.md`)
- **Purpose**: Just-in-time (JIT) loaded rules for specific file types or directories
- **Scope**: Only loaded when working with matching files (via `applyTo` glob)
- **Content**: Framework-specific patterns, testing conventions, component standards
- **Size limit**: ~200-500 lines per file (focused scope)
- **Examples**: React component rules, Python test patterns, API doc standards

## Priority System

When multiple instruction files apply to the same file:

1. **Path-specific instructions override global instructions**
2. **More specific globs take precedence over broader ones**
3. **Multiple path instructions can apply simultaneously** (all are loaded)

### Example Hierarchy
```
File: src/components/Button.test.tsx

Loaded instructions (in priority order):
1. .github/instructions/react-testing.md (applyTo: "**/*.test.tsx")
2. .github/instructions/react-components.md (applyTo: "src/components/**/*.tsx")
3. .github/copilot-instructions.md (global)

Result: Button.test.tsx gets React testing rules + component rules + global rules
```

## Include/Exclude Decision Table

| Scenario | Path-Specific | Global | Rationale |
|----------|---------------|--------|-----------|
| React component patterns | ✅ Include | ❌ Exclude | Framework-specific, only needed for `.tsx` files |
| Python pytest fixtures | ✅ Include | ❌ Exclude | Testing framework specific, only for test files |
| API endpoint documentation format | ✅ Include | ❌ Exclude | Scoped to API docs directory |
| Go test table-driven patterns | ✅ Include | ❌ Exclude | Language + testing specific |
| Kubernetes resource conventions | ✅ Include | ❌ Exclude | Only for YAML manifests in k8s dirs |
| TypeScript strict null checks | ✅ Include | ❌ Exclude | Language-specific compiler settings |
| Database migration naming | ✅ Include | ❌ Exclude | Only for migration files |
| GraphQL schema conventions | ✅ Include | ❌ Exclude | Schema files only |
| Terraform module structure | ✅ Include | ❌ Exclude | IaC-specific patterns |
| Storybook story format | ✅ Include | ❌ Exclude | Only for `*.stories.tsx` files |
| Project name/description | ❌ Exclude | ✅ Include | Universal context |
| Primary programming languages | ❌ Exclude | ✅ Include | Applies everywhere |
| Error handling philosophy | ❌ Exclude | ✅ Include | Cross-cutting concern |
| Code review standards | ❌ Exclude | ✅ Include | Universal process |
| Security practices | ❌ Exclude | ✅ Include | Applies to all code |

## Scope Sweet Spot

### Ideal Scope Size: 10-500 Files

**Too Narrow (< 10 files)**
- Overhead not worth the complexity
- Consider inline comments or global rules instead
- Exception: Complex, critical subsystems (e.g., authentication)

**Sweet Spot (10-500 files)**
- Clear pattern/framework/directory scope
- Significant rule set that would clutter global instructions
- JIT loading provides meaningful context savings
- Examples:
  - All test files in a framework
  - Component library directory
  - API documentation directory
  - Infrastructure-as-code files

**Too Broad (> 500 files)**
- Scope may be too generic
- Consider splitting or using global instructions
- Exception: Large monorepos with clear domain boundaries

### Measuring Your Scope
Use the included glob testing script:
```bash
python .github/skills/generate-path-instructions-v2/scripts/test_glob_pattern.py \
  --pattern "src/components/**/*.tsx" \
  --limit 50
```

## When to Split Path Instructions

### Split When:

1. **Different frameworks/tools** - Even if same file type
   ```
   ✅ tests/unit/*.test.ts → jest-testing.md
   ✅ tests/e2e/*.test.ts → playwright-testing.md
   ```

2. **Distinct conventions** - Different patterns in different directories
   ```
   ✅ src/api/v1/**/*.md → api-v1-docs.md
   ✅ src/api/v2/**/*.md → api-v2-docs.md
   ```

3. **File approaching 500 lines** - Breaking natural topic boundaries
   ```
   ✅ react-components.md (200 lines)
   ✅ react-testing.md (250 lines)
   ❌ react-everything.md (600 lines) → Too large
   ```

4. **Conflicting rules** - Same file type, different purposes
   ```
   ✅ src/components/**/*.tsx → react-components.md
   ✅ src/pages/**/*.tsx → nextjs-pages.md
   ```

### Keep Combined When:

1. **Tightly coupled concepts** - Rules that work together
   ```
   ✅ kubernetes-manifests.md (includes Deployment, Service, ConfigMap patterns)
   ```

2. **Shared vocabulary** - Common terminology and patterns
   ```
   ✅ graphql-schema.md (types, queries, mutations all use same conventions)
   ```

3. **Small total size** - Combined < 300 lines
   ```
   ✅ markdown-docs.md (general docs + API docs = 200 lines)
   ```

## Context Economics Formula

```
Context Budget = 1000 lines total instructions

Global Instructions:     300-500 lines (constitutional rules)
Path-Specific Average:   200-300 lines per file
Active Path Instructions: 1-3 files (loaded JIT based on current file)

Effective Context Used = Global + Σ(Active Path Instructions)
                       ≈ 400 + (2 × 250) = 900 lines
```

## Best Practices

1. **Start with global** - Begin with `.github/copilot-instructions.md`
2. **Extract patterns** - Move framework-specific rules to path instructions
3. **Test globs** - Use the test script to validate patterns
4. **Measure impact** - Track instruction file sizes
5. **Iterate** - Refine scope as repository evolves

## Anti-Patterns

❌ **Don't**: Create path instruction for 3 files  
✅ **Do**: Use inline comments or global rules

❌ **Don't**: Put project description in path instructions  
✅ **Do**: Keep identity in global instructions

❌ **Don't**: Create overlapping globs with contradictory rules  
✅ **Do**: Design clear, hierarchical glob patterns

❌ **Don't**: Exceed 500 lines in a single path instruction  
✅ **Do**: Split into focused, topic-specific files

## Examples

See `template_examples.md` for complete, production-ready examples of path-specific instruction files.
