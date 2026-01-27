# Positive Constraints Conversion Patterns

LLMs respond better to affirmative instructions than negative prohibitions. This guide shows how to convert "don't do X" rules into "do Y" instructions.

---

## Core Principle

**Negative constraints increase cognitive load** and can be ambiguous (if I can't do X, what *should* I do?).

**Positive constraints are directive** and show the preferred approach clearly.

---

## Conversion Patterns

### Pattern 1: "Don't use X" → "Use Y instead"

| ❌ Negative (Bad) | ✅ Positive (Good) |
|:------------------|:-------------------|
| "Don't use `var`" | "Use `const` or `let` for variable declarations" |
| "Avoid jQuery" | "Use native DOM APIs or React for UI manipulation" |
| "Don't use `any` type" | "Use specific types or `unknown` for TypeScript" |
| "Never use global variables" | "Scope variables to function or module level" |
| "Don't write monolithic functions" | "Keep functions under 50 lines; extract helpers for complex logic" |

---

### Pattern 2: "Never do X" → "Always do Y"

| ❌ Negative (Bad) | ✅ Positive (Good) |
|:------------------|:-------------------|
| "Never hardcode secrets" | "Store secrets in environment variables or key vaults" |
| "Never commit .env files" | "Use .env.example for templates; add .env to .gitignore" |
| "Never expose database credentials" | "Use connection pooling with env-based config" |
| "Never skip tests" | "All new features must include unit tests in `tests/`" |

---

### Pattern 3: "Avoid X" → "Prefer Y"

| ❌ Negative (Bad) | ✅ Positive (Good) |
|:------------------|:-------------------|
| "Avoid synchronous I/O" | "Use async/await for all I/O operations" |
| "Avoid deeply nested callbacks" | "Use Promise chains or async/await for asynchronous flows" |
| "Avoid magic numbers" | "Define named constants for numeric values" |
| "Avoid inline styles" | "Use CSS classes or styled-components" |

---

### Pattern 4: "Don't forget to X" → "Always X"

| ❌ Negative (Bad) | ✅ Positive (Good) |
|:------------------|:-------------------|
| "Don't forget error handling" | "Wrap API calls in try/catch blocks" |
| "Don't forget to close connections" | "Use context managers (Python) or defer (Go) for cleanup" |
| "Don't forget documentation" | "Document all public functions with JSDoc/docstrings" |
| "Don't forget to update tests" | "Update tests when modifying function signatures" |

---

### Pattern 5: "No X" → "Enforce Y"

| ❌ Negative (Bad) | ✅ Positive (Good) |
|:------------------|:-------------------|
| "No tabs for indentation" | "Use 2 spaces for indentation (enforced by Prettier)" |
| "No console.log in production" | "Use structured logging with Winston/Bunyan" |
| "No SQL injection" | "Use parameterized queries or ORM methods" |
| "No mixed quotes" | "Use single quotes for strings (ESLint enforced)" |

---

### Pattern 6: "Stop doing X" → "Migrate to Y"

| ❌ Negative (Bad) | ✅ Positive (Good) |
|:------------------|:-------------------|
| "Stop using class components" | "Write new components as functional components with hooks" |
| "Stop using callbacks" | "Refactor callbacks to async/await" |
| "Stop using deprecated APIs" | "Migrate to new API: use fetch() instead of XMLHttpRequest" |

---

## Special Cases

### Security Rules

Security rules often sound negative but can be reframed:

| ❌ Negative | ✅ Positive |
|:-----------|:------------|
| "Never trust user input" | "Sanitize and validate all user inputs before processing" |
| "Don't allow SQL injection" | "Use parameterized queries exclusively for database access" |
| "Never expose internal errors to users" | "Log errors internally; show generic messages to users" |
| "Don't store passwords in plaintext" | "Hash passwords with bcrypt before storing (min 12 rounds)" |

### Performance Rules

| ❌ Negative | ✅ Positive |
|:-----------|:------------|
| "Avoid N+1 queries" | "Use eager loading or batch queries for related data" |
| "Don't block the event loop" | "Offload CPU-intensive tasks to worker threads" |
| "Never load entire datasets into memory" | "Stream large datasets or use pagination" |

### Style Rules

| ❌ Negative | ✅ Positive |
|:-----------|:------------|
| "Don't mix camelCase and snake_case" | "Use camelCase for JavaScript, snake_case for Python" |
| "No trailing whitespace" | "Configure editor to trim whitespace on save" |
| "Don't exceed 80 characters per line" | "Keep lines under 100 characters (enforced by Prettier)" |

---

## How to Apply This

### When Writing Repository Instructions

1. **Identify negative rules** in existing docs (CONTRIBUTING.md, code reviews)
2. **Find the positive alternative** - what *should* developers do?
3. **Be specific** - give the tool/pattern/command to use
4. **Enforce if possible** - mention linters, formatters, pre-commit hooks

### Template Pattern

```markdown
**[Category]:**
- [Positive instruction 1]
- [Positive instruction 2]
- [Positive instruction 3]

**Enforced by:** [Tool name - ESLint, Black, pre-commit hooks]
```

### Example: Formatting Section

**Bad (Negative):**
```markdown
## Formatting
- Don't use tabs
- Don't mix quote styles
- Avoid lines over 100 characters
```

**Good (Positive):**
```markdown
## Formatting
- Use 2 spaces for indentation
- Use single quotes for strings
- Keep lines under 100 characters

**Enforced by:** Prettier (run `npm run format` before committing)
```

---

## Edge Cases

### When Negative is Acceptable

Sometimes negative phrasing is clearer if there's no obvious alternative:

✅ **Acceptable negative rules:**
- "No hardcoded credentials" (when there are many ways to avoid it)
- "No committing build artifacts" (gitignore is the solution)
- "No force-pushing to main" (branch protection is external)

**But still better to add the positive alternative:**
```markdown
- No hardcoded credentials → Use environment variables
- No committing build artifacts → Add dist/ to .gitignore
- No force-pushing to main → Use rebase on feature branches only
```

### When "Don't" is a Warning

For edge cases or known pitfalls:

```markdown
**Known Issues:**
- React 17 event pooling is deprecated → Use event.persist() or upgrade to React 18
- Python 2 support ended 2020 → Ensure all scripts use Python 3.8+
```

This is documentation, not instruction, so negative phrasing is fine.

---

## Common Conversions Quick Reference

| Domain | ❌ Negative | ✅ Positive |
|:-------|:-----------|:------------|
| **JavaScript** | Don't use `var` | Use `const` or `let` |
| **Python** | Don't use mutable defaults | Use `None` and initialize in function body |
| **Go** | Don't ignore errors | Check and handle all error returns |
| **Rust** | Don't use unsafe unnecessarily | Encapsulate unsafe in safe abstractions |
| **TypeScript** | Don't use `any` | Use specific types or `unknown` |
| **React** | Don't mutate state | Use `useState` or immutable updates |
| **Git** | Don't commit secrets | Use .env files with .gitignore |
| **Testing** | Don't skip tests | All features require tests in `tests/` |
| **Security** | Don't trust input | Validate and sanitize all inputs |
| **Performance** | Don't block the main thread | Use async operations or workers |

---

## Validation Checklist

When reviewing generated instructions, check:

- [ ] All "don't" / "never" / "avoid" rules are converted to "use" / "always" / "prefer"
- [ ] Negative rules have specific positive alternatives
- [ ] Tools for enforcement are mentioned (linters, formatters)
- [ ] Edge cases / warnings are marked as "Known Issues" not "Rules"
- [ ] Security rules are phrased as "Validate X" not "Never trust X"

---

## Summary

**The Golden Rule:**
> Tell the agent **what to do**, not **what to avoid**.

Good instructions are:
- **Directive** - Clear action to take
- **Specific** - Mention tools, patterns, commands
- **Enforceable** - Reference linters/formatters when applicable
- **Positive** - Frame as "use Y" not "don't use X"
