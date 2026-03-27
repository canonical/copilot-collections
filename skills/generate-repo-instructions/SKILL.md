---
name: generate-repo-instructions
description: Generates the global repository constitution file (.github/copilot-instructions.md). Works for code repositories, documentation repositories, data repositories, and mixed repos. Performs LLM-driven deep repository analysis including docs, code patterns, build systems, documentation generators, and data schemas. Generates constitutional rules following context economics (under 1000 lines). Enforces positive constraints and no hardcoded secrets.
---

# Repository Instructions Generator

## Overview

This skill generates the global `.github/copilot-instructions.md` file through comprehensive LLM-driven repository analysis. It autonomously discovers project characteristics, then populates a constitutional template with discovered values.

**Works for all repository types:**
- **Code repositories:** Tech stack, build systems, coding conventions
- **Documentation repositories:** Doc generators, writing style, content structure
- **Data repositories:** Schemas, pipelines, quality standards
- **Mixed repositories:** Adapts to whatever it finds

**Key principle:** Leverage LLM strengths for analysis and synthesis rather than rigid scripts.

---

## Workflow

### Step 1: Intent Validation

Confirm the user wants to create the **global** `.github/copilot-instructions.md` file.

**Decision tree:**

- **User wants global instructions?** → Continue to Step 2
- **User wants path-specific instructions** (e.g., "only for src/components/")?
  - → STOP. Redirect them to use `generate-path-instructions` skill instead
  - Explain: Path instructions use `applyTo` glob patterns for targeted loading
- **User wants a custom agent or skill?**
  - → STOP. Clarify asset type using Asset Decision Matrix
  - Agent = role-based, Skill = capability-based

**Proceed only if creating global instructions.**

---

### Step 2: Comprehensive Repository Analysis

Perform deep codebase discovery following the checklist in `references/analysis_checklist.md`.

**Load the analysis checklist:**
```bash
cat references/analysis_checklist.md
```

Work through all 7 phases systematically:

1. **Documentation Discovery** - README, CONTRIBUTING, ARCHITECTURE docs
2. **Tech Stack Detection** - Languages, frameworks, package managers
3. **Build System Discovery** - Build/test/lint commands
4. **Code Pattern Analysis** - Indentation, formatting, async patterns
5. **Project Structure Mapping** - Directory purposes
6. **Configuration Files** - .env, .editorconfig, git configs
7. **Security & Quality** - Secret scanning, quality tools

**Important guidelines:**

- **Read actual file contents** - Don't assume, verify
- **Sample source code** - Check 3-5 files for patterns
- **Synthesize findings** - Combine information from multiple sources
- **Handle missing data gracefully** - Use "Not specified" if values can't be determined

**Output of this step:** Mental model of:
- Elevator pitch (what the project does)
- Complete tech stack (languages + frameworks + tools)
- Coding conventions (indentation, formatters, linters)
- Build workflow (build/test/lint commands)
- Project structure (directory purposes)

---

### Step 3: Minimal User Interaction

**Only ask the user if you absolutely cannot determine from the codebase:**

- **Elevator pitch** - If README is missing or too vague
- **Formatting preferences** - If code samples are inconsistent across files
- **Critical security/compliance rules** - Not evident from code

**Goal:** Generate 90% of instructions autonomously through analysis.

**Pattern for asking:**
```markdown
I've analyzed the repository but need clarification on:

1. **Project description:** The README doesn't clearly state what this software does. 
   Can you provide a 1-2 sentence elevator pitch?

2. **Indentation:** Code samples show mixed 2-space and 4-space indentation. 
   What's the preferred style?
```

**If user doesn't respond:** Use best judgment from majority pattern or "Follow existing code style".

---

### Step 4: Apply Positive Constraints

Before populating the template, convert any negative rules to positive instructions.

**Load the conversion patterns:**
```bash
cat references/positive_constraints_patterns.md
```

**Common conversions:**

| If You Found | Convert To |
|:-------------|:-----------|
| "Don't use `var`" | "Use `const` or `let` for variable declarations" |
| "Never hardcode secrets" | "Store secrets in environment variables or key vaults" |
| "Avoid deeply nested callbacks" | "Use async/await for asynchronous flows" |
| "No trailing whitespace" | "Configure editor to trim whitespace on save" |

**Validation checklist:**
- [ ] All "don't" / "never" / "avoid" rules are rephrased positively
- [ ] Security rules are phrased as "Validate X" not "Never trust X"
- [ ] Specific tools/patterns are mentioned (not vague "write good code")

---

### Step 5: Template Population

**Load the instruction template:**
```bash
cat references/instruction_template.md
```

**Populate all `{{placeholders}}` with discovered values:**

| Placeholder | Source | Example |
|:------------|:-------|:--------|
| `{{repo_name}}` | Auto-detect from directory name or git config | `my-awesome-project` |
| `{{elevator_pitch}}` | README or user input | "A CLI tool for analyzing log files" |
| `{{languages}}` | Detected from package.json, go.mod, etc. | "Go, TypeScript" |
| `{{frameworks}}` | Detected from dependencies | "React, Express" |
| `{{build_tools}}` | Detected from Makefile, package.json scripts | "npm, make" |
| `{{formatting_rules}}` | Detected from code samples + .editorconfig | "2 spaces, Prettier enforced" |
| `{{test_dir}}` | Detected from project structure | `tests/` or `__tests__/` |
| `{{structure_map}}` | Detected directory tree with purposes | See analysis checklist |
| `{{build_command}}` | Detected from Makefile, package.json, CI | `npm run build` |
| `{{test_command}}` | Detected from package.json, Makefile | `npm test` |
| `{{lint_command}}` | Detected from package.json, Makefile | `npm run lint` |

**If a value cannot be determined:**
- Use "Not specified" for optional fields
- Use "Follow existing code patterns" for style rules
- Omit entire sections if not applicable (e.g., no build command = no build section)

---

### Step 6: Context Economics Validation

**Before writing the file**, verify compliance with context economics principles.

**Load the economics guide:**
```bash
cat references/context_economics.md
```

**Validation checklist:**

- [ ] **Line count under 1000 lines** (preferably under 500)
  - If over: Move framework-specific rules to path instructions
  - If over: Move detailed API docs to `docs/` and reference them
  
- [ ] **No hardcoded secrets or credentials**
  - Scan for: API keys, passwords, tokens, database URLs
  - If found: Remove and note in security section to use env vars
  
- [ ] **Positive constraints only**
  - All rules are phrased as "do X" not "don't do Y"
  
- [ ] **High-priority information only**
  - Project identity (what it does)
  - Tech stack (canonical list)
  - Constitutional rules (immutable laws)
  - Build/test commands (CLI only)

**If validation fails:** Trim content before writing.

---

### Step 7: File Generation

Write the populated and validated content to `.github/copilot-instructions.md`.

**Steps:**

1. Create directory if needed: `mkdir -p .github/`
2. Write file: `.github/copilot-instructions.md`
3. Verify file exists and is readable

**Do not ask for permission** - the user already requested this in Step 1.

---

### Step 8: Confirmation Report

Provide a summary report to the user:

```markdown
✅ **Repository instructions generated successfully!**

📄 **File:** `.github/copilot-instructions.md`  
📊 **Line count:** 287 lines  
🔧 **Tech stack detected:** TypeScript, React, Node.js  
⚙️  **Build system:** npm (build, test, lint commands documented)  
🎯 **Analysis sources:** README.md, package.json, 5 source files sampled

⚠️  **Reminder:** This file is always loaded into context. Review and trim if needed.

**Next steps:**
1. Review `.github/copilot-instructions.md` for accuracy
2. Test with Copilot to verify context loading
3. Create path-specific instructions for framework rules if needed
```

---

## Resources

This skill uses LLM-driven analysis - no scripts required!

### references/

**analysis_checklist.md**  
Comprehensive checklist for repository discovery. Use this to systematically analyze:
- Documentation files (README, CONTRIBUTING)
- Tech stack files (package.json, go.mod, requirements.txt)
- Build systems (Makefile, CI/CD configs)
- Code patterns (indentation, async style)

**instruction_template.md**  
The output template with `{{placeholders}}` for discovered values.

**context_economics.md**  
Guidelines for keeping instructions under 1000 lines. Explains:
- What to include (high-priority)
- What to exclude (use path instructions)
- Positive constraints pattern
- Template variable reference

**positive_constraints_patterns.md**  
Conversion patterns for rephrasing negative rules as positive instructions. Includes:
- Common conversions (don't → use)
- Security rules
- Performance rules
- Validation checklist

---

## Best Practices

### ✅ DO:
- Read actual file contents (don't assume based on filename)
- Sample multiple source files for pattern detection
- Synthesize information from multiple sources
- Use positive phrasing for all rules
- Keep instructions under 1000 lines
- Verify no secrets in generated output

### ❌ DON'T:
- Rely on scripts for analysis (LLM excels at this)
- Ask user for information already in codebase
- Use negative constraints ("don't do X")
- Generate overly verbose instructions
- Include framework-specific rules (use path instructions)
- Hardcode values that change (versions, URLs)

---

## Example Usage

**User:** "Generate repository instructions for this project"

**Agent workflow:**
1. Validates intent (global instructions ✓)
2. Loads `analysis_checklist.md`
3. Reads README.md → Extract elevator pitch
4. Reads package.json → Detect: TypeScript, React, npm
5. Reads package.json scripts → Build: `npm run build`, Test: `npm test`
6. Samples 5 .tsx files → Detect: 2-space indentation, async/await pattern
7. Maps structure → `src/` (source), `tests/` (tests), `docs/` (docs)
8. Loads `positive_constraints_patterns.md`
9. Converts "Don't use `any`" → "Use specific types or `unknown`"
10. Loads `instruction_template.md`
11. Populates all placeholders
12. Validates: 324 lines ✓, no secrets ✓, positive phrasing ✓
13. Writes `.github/copilot-instructions.md`
14. Reports success with summary
