---
name: generate-path-instructions
description: Generates path-specific instruction files (.github/instructions/*.md) with JIT loading via applyTo glob patterns. Performs LLM-driven repository analysis to discover file patterns and extract scope-specific rules. Use when the user requests scoped, framework-specific, or directory-specific rules for testing, components, docs, config files, or language-specific files to prevent context pollution. Works for code, documentation, configuration, and data files.
---

# Path-Specific Instructions Generator

## Overview

This skill generates scoped `.github/instructions/*.md` files that load Just-In-Time (JIT) when specific files are opened. It autonomously analyzes your repository to discover file patterns, extract scope-specific rules from existing code and documentation, and generate precise glob patterns for targeted instruction loading.

**Key advantages over global instructions:**
- **Context Economics:** Load rules only when needed (vs always-on global instructions)
- **Higher Priority:** Path instructions override global instructions
- **Precision:** Target specific frameworks, file types, or directories

**Key principle:** Leverage LLM strengths for pattern discovery and rule extraction rather than manual specification.

---

## Workflow

### Step 1: Intent Validation

Confirm the user wants **path-specific** instructions (not global).

**Decision tree:**

- **User wants scoped/directory/framework-specific rules?** → Continue to Step 2
- **User wants global repository instructions?**
  - → STOP. Redirect them to use `generate-repo-instructions` skill instead
  - Explain: Global instructions go in `.github/copilot-instructions.md`
- **User wants a custom agent or skill?**
  - → STOP. Clarify asset type using Asset Decision Matrix
  - Agent = role-based, Skill = capability-based, Instructions = rules

**Proceed only if creating path-specific instructions.**

---

### Step 2: Scope Discovery

**Goal:** Understand what files/directories to target and what patterns exist.

**Load the scope analysis checklist:**
```bash
cat references/scope_analysis_checklist.md
```

Work through the checklist to discover:
1. **Target identification** - What files does the user want to scope?
2. **Repository exploration** - What file patterns actually exist?
3. **Framework detection** - What tools/frameworks are in use?
4. **Existing conventions** - What patterns are already established?

**Output:** Clear understanding of target scope with concrete file examples.

**Critical decision: Be specific or accept ambiguity?**
- If user says "test files" but repo has `.test.js`, `.spec.js`, AND `_test.py`
- → Ask: "Target all tests or just JavaScript tests?"
- Don't assume - clarify scope boundaries

---

### Step 3: Pattern Construction

**Goal:** Build precise `applyTo` glob patterns that match intended files only.

**Load the pattern construction guide:**
```bash
cat references/pattern_construction.md
```

Follow the guide to:
1. **Construct candidate patterns** based on discovered file structure
2. **Test patterns** using the glob testing script (optional but recommended)
3. **Refine patterns** to avoid over-matching or under-matching

**Example workflow:**
```bash
# Test if pattern matches intended files
python3 scripts/test_glob_pattern.py --pattern "tests/**/*.py" --limit 10

# Review matches, refine if needed
python3 scripts/test_glob_pattern.py --pattern "tests/**/*.test.py" --limit 10
```

**Output:** Validated glob pattern(s) for `applyTo` directive.

---

### Step 4: Rule Extraction

**Goal:** Discover scope-specific rules (not generic rules that belong in global instructions).

**Load the rule discovery checklist:**
```bash
cat references/rule_discovery_checklist.md
```

Work through the checklist to extract rules from:
1. **Code samples** - Read files in target scope, identify patterns
2. **Configuration files** - Extract settings from linters, formatters, test configs
3. **Documentation** - Find relevant sections in CONTRIBUTING, style guides
4. **Framework conventions** - Apply framework best practices

**Critical: Context Economics**

Load `references/context_economics.md` to understand the Include/Exclude principle:

| ✅ Include (Scope-Specific) | ❌ Exclude (Too Generic) |
|----------------------------|--------------------------|
| "Use pytest fixtures in tests" | "Use 4 spaces for indentation" |
| "Docs must follow ADR format" | "Write clear commit messages" |
| "K8s manifests must set limits" | "Follow semantic versioning" |

**Why?** Path instructions have **higher priority** than global. Use them only for truly scope-specific rules.

**Output:** List of scope-specific rules with examples from the codebase.

---

### Step 5: Template Application

**Goal:** Populate the instruction file with discovered patterns and rules.

**Load template examples:**
```bash
cat references/template_examples.md
```

Choose the appropriate template based on scope type (testing, docs, config, code).

**Populate these fields:**
- `name`: Descriptive kebab-case name
- `description`: One-sentence scope summary
- `applyTo`: Validated glob pattern(s) from Step 3
- **Scope Introduction** - What this applies to
- **Standards & Conventions** - Framework-specific patterns
- **Content Rules** - Scope-specific requirements
- **Examples** - Good examples from actual codebase (not theoretical)

**File naming convention:**
- `.github/instructions/{{scope-type}}-{{content-type}}.md`
- Examples: `python-testing.md`, `api-documentation.md`, `kubernetes-manifests.md`
- Use kebab-case, be descriptive (not generic like `rules.md`)

---

### Step 6: Validation & Testing

**Validate the generated instruction file:**

```bash
# 1. Validate YAML frontmatter and structure
python3 .github/skills/generate-agent-skills/scripts/validate_skill.py --path .github/instructions/

# 2. Verify glob pattern matches intended files
python3 .github/skills/generate-path-instructions-v2/scripts/test_glob_pattern.py \
  --pattern "tests/**/*.py" \
  --limit 20

# 3. Check rule specificity
# - Are all rules scope-specific?
# - Do rules include examples from actual codebase?
# - Is there any overlap with global instructions?
```

**Final checklist:**
- [ ] YAML frontmatter is valid (name, description, applyTo)
- [ ] Glob patterns tested and match intended files only
- [ ] All rules are scope-specific (not generic)
- [ ] Examples are from actual codebase (not theoretical)
- [ ] Filename is descriptive and uses kebab-case
- [ ] No hardcoded secrets or sensitive data

**Output to user:**
```
✅ Created: .github/instructions/{{filename}}.md
📌 Applies to: {{glob_pattern}}
📝 Summary: {{one_sentence_description}}

🧪 Tested pattern - matches {{N}} files in repo
```

---

### Step 7: Iteration (Optional)

If the user wants to refine:

1. **Test in practice** - Open a file that should match, verify instruction loads
2. **Refine glob pattern** - Adjust if over/under-matching
3. **Add missing rules** - Include additional scope-specific conventions
4. **Improve examples** - Replace theoretical examples with real code

**Common refinements:**
- Pattern too broad → Add path prefix (e.g., `**/*.test.js` → `tests/**/*.test.js`)
- Rules too generic → Move to global instructions, keep only scope-specific
- Missing context → Add framework-specific best practices

---

## Resources

### scripts/test_glob_pattern.py
Tests glob patterns against actual repository files.
- **Input:** Glob pattern(s)
- **Output:** List of matching files
- **Purpose:** Validate patterns before finalizing instruction file

### references/scope_analysis_checklist.md
Guides LLM through repository exploration to discover target scope.

### references/pattern_construction.md
Glob syntax reference with common patterns and anti-patterns.

### references/rule_discovery_checklist.md
Guides LLM through extracting scope-specific rules from code and docs.

### references/template_examples.md
Domain-specific instruction templates (testing, docs, config, code).

### references/context_economics.md
Explains when to use path-specific vs global instructions.
