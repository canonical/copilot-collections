# Context Economics for Repository Instructions

## The Problem
Repository instructions (.github/copilot-instructions.md) are **always loaded** into the agent's context window for every interaction. This creates a high cost:
* **Token Cost:** Large instruction files consume the context budget.
* **Attention Degradation:** Noisy or verbose instructions dilute the agent's focus.

## The Solution: The 1000-Line Rule
Keep repository instructions under **1000 lines** (approximately 2 pages).

### What to Include (High-Priority)
1. **Project Identity:** What the software does (2-3 sentences).
2. **Tech Stack:** Canonical list of languages/frameworks.
3. **Constitutional Rules:** Immutable laws that apply globally (formatting, security, testing).
4. **Build/Test Commands:** How to build and test (CLI commands only).

### What to Exclude (Use Path Instructions Instead)
* Framework-specific rules → `.github/instructions/react-components.md` with `applyTo: ["src/components/**/*.tsx"]`
* Test-specific rules → `.github/instructions/testing.md` with `applyTo: ["tests/**/*"]`
* API documentation → Move to `docs/` and reference it.

## Positive Constraints Pattern
Convert negative rules to positive instructions:

| ❌ Negative (Bad) | ✅ Positive (Good) |
| :--- | :--- |
| "Don't use `var`" | "Use `const` or `let` for variable declarations" |
| "Never hardcode secrets" | "Store secrets in environment variables or key vaults" |
| "Avoid jQuery" | "Use native DOM APIs or React for UI manipulation" |

**Why?** LLMs respond better to affirmative instructions. Negative constraints increase cognitive load.

## Template Variable Reference
When populating the instruction template, ensure all variables are replaced:

| Variable | Source | Example |
| :--- | :--- | :--- |
| `{{repo_name}}` | Auto-detected (repo directory name) | `my-project` |
| `{{elevator_pitch}}` | User input | "A CLI tool for analyzing logs" |
| `{{languages}}` | Auto-detected (from package.json, go.mod, etc.) | "Go, Python" |
| `{{frameworks}}` | Auto-detected | "React, Express" |
| `{{build_tools}}` | Auto-detected | "npm, make" |
| `{{formatting_rules}}` | User input | "Indent with 2 spaces, use Prettier" |
| `{{test_dir}}` | Auto-detected | `tests/` |
| `{{structure_map}}` | Auto-detected | Directory tree with purposes |
| `{{build_command}}` | Auto-detected | `npm run build` |
| `{{test_command}}` | Auto-detected | `npm test` |
| `{{lint_command}}` | Auto-detected | `npm run lint` |
