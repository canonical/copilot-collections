---
name: generate-prompt
description: Generates reusable Prompt Template files (.github/prompts/*.prompt.md) with variable substitution for ad-hoc, high-frequency tasks. Use when the user needs quick, repeatable prompts for common operations (explain code, fix bug, add tests, refactor, document). Creates templates with handlebars variables, optimized context structure, and strict output constraints. Not for complex workflows (use skills) or persistent roles (use agents).
---

# Prompt Template Generator (Template Engineer)

## Overview

This skill generates Prompt Template files that are **pure text templates** optimized for:
- **Repeatability:** Same task, different inputs
- **Efficiency:** Manual trigger, snapshot of current editor
- **Simplicity:** No scripts, no thinking processes, just templates

**Key distinction:**
- **Prompts** (this skill) = Quick reusable snippets with variables
- **Skills** = Complex workflows with scripts/references
- **Agents** = Persistent roles with tool constraints
- **Instructions** = Always-on rules

**Example prompts:**
- "Explain this code" (variable: selected code)
- "Fix this bug" (variables: error message, code context)
- "Add unit tests" (variables: function code, framework)
- "Document this API" (variables: endpoint code, method)

---

## Workflow

### Step 1: Intent Validation

Confirm the user wants a **Prompt Template** (not a skill, agent, or instruction).

**Decision tree:**

- **User wants a quick, repeatable snippet?** → Continue to Step 2
  - Examples: "Explain code", "Fix bug", "Add tests"
- **User wants a complex workflow with scripts?**
  - → STOP. Redirect to `generate-agent-skills` instead
  - Explain: Skills have workflows, scripts, progressive disclosure
- **User wants a persistent role/perspective?**
  - → STOP. Redirect to `generate-agent` instead
  - Explain: Agents have identity, tool constraints, thinking processes
- **User wants always-on rules?**
  - → STOP. Redirect to `generate-path-instructions` or `generate-repo-instructions`
  - Explain: Instructions provide continuous guidance

**Proceed only if creating a simple, reusable prompt template.**

---

### Step 2: Task Analysis

**Goal:** Understand what the prompt does and when it's used.

**Load the task analysis checklist:**
```bash
cat references/task_analysis_checklist.md
```

Work through the checklist to define:
1. **Task Description** - What does this prompt do?
2. **Trigger Conditions** - When would someone use this?
3. **Input Requirements** - What data does it need?
4. **Output Format** - What should it produce?
5. **Constraints** - Any rules or limitations?

**Example outputs:**

**"Explain Code" Prompt:**
- Task: Explain what selected code does
- Trigger: User selects unfamiliar code
- Inputs: Selected code, programming language
- Output: Plain English explanation with examples
- Constraints: Keep explanation concise, assume beginner level

**"Fix Bug" Prompt:**
- Task: Fix error in code
- Trigger: User gets error message
- Inputs: Error message, broken code, language
- Output: Fixed code with brief explanation
- Constraints: Only fix the bug, don't refactor unnecessarily

---

### Step 3: Variable Identification

**Goal:** Identify dynamic inputs that change per invocation.

**Load the variable identification guide:**
```bash
cat references/variable_identification_guide.md
```

**Common variable types:**

1. **Editor Context:**
   - `{{selected_code}}` - Currently selected text
   - `{{current_file}}` - Full current file path
   - `{{file_content}}` - Entire file content
   - `{{cursor_line}}` - Line number at cursor

2. **User Inputs:**
   - `{{language}}` - Programming language
   - `{{framework}}` - Framework in use
   - `{{error_message}}` - Error text
   - `{{description}}` - User-provided description

3. **Project Context:**
   - `{{project_name}}` - Repository name
   - `{{tech_stack}}` - Technologies used
   - `{{conventions}}` - Project standards

**Naming conventions:**
- Use `{{snake_case}}` for variables
- Be descriptive: `{{error_message}}` not `{{err}}`
- Avoid abbreviations unless standard

**Example variable sets:**

**Explain Code:**
- `{{selected_code}}` - The code to explain
- `{{language}}` - Programming language (optional, can infer)

**Fix Bug:**
- `{{error_message}}` - The error text
- `{{broken_code}}` - Code that's failing
- `{{language}}` - Programming language

**Add Tests:**
- `{{function_code}}` - Function to test
- `{{framework}}` - Test framework (pytest, jest, etc.)
- `{{language}}` - Programming language

---

### Step 4: Context Optimization

**Goal:** Structure the prompt for maximum effectiveness.

**Load context optimization patterns:**
```bash
cat references/context_optimization_patterns.md
```

**Needle in a Haystack Principle:**
- **Front-load:** System context, rules, constraints
- **Back-load:** Specific data (user code, error messages)
- **Rationale:** LLMs pay more attention to beginning and end of prompts

**Prompt structure:**

```markdown
# {{Prompt Title}}

## System Context (Front)
{{Task description}}
{{Output format requirements}}
{{Constraints and rules}}

## Data (Back)
{{User-provided variables}}
{{Selected code / error messages}}
```

**Examples:**

**Good structure:**
```markdown
# Explain Code

Explain what the following code does in plain English.

**Output format:**
- Start with one-sentence summary
- Explain key concepts
- Include example usage if helpful

**Constraints:**
- Keep explanation concise (under 200 words)
- Assume beginner-level understanding
- Avoid jargon without explaining it

---

**Code to explain:**
```{{language}}
{{selected_code}}
```
```

**Bad structure (data front-loaded):**
```markdown
Here's some code:
{{selected_code}}

Please explain it simply.
```

---

### Step 5: Constraint Definition

**Goal:** Define strict output requirements to ensure consistent, useful results.

**Common constraint types:**

1. **Format Constraints:**
   - "Always output JSON"
   - "Use markdown code fences"
   - "Return only the fixed code, no explanation"

2. **Length Constraints:**
   - "Keep under 200 words"
   - "Provide 3-5 examples"
   - "Single paragraph explanation"

3. **Tone Constraints:**
   - "Assume beginner level"
   - "Be concise and technical"
   - "Explain like teaching a junior developer"

4. **Behavioral Constraints:**
   - "Never change code outside the bug fix"
   - "Don't refactor unnecessarily"
   - "Preserve existing code style"

**Example constraints:**

**Explain Code:**
- Output: Plain English explanation
- Length: Under 200 words
- Tone: Beginner-friendly
- Structure: Summary → Details → Example

**Fix Bug:**
- Output: Fixed code only (no explanation unless asked)
- Behavior: Minimal changes (just fix the bug)
- Format: Same language and style as input

---

### Step 6: Template Generation

**Goal:** Create the prompt file using the template.

**Load prompt template:**
```bash
cat assets/prompt_template.md
```

**Populate these sections:**

1. **YAML Frontmatter:**
   - `name`: kebab-case prompt name (e.g., `explain-code`)
   - `description`: One-sentence summary of what it does
   - `variables`: List of variable names (for documentation)

2. **Prompt Title:**
   - Clear, action-oriented (e.g., "Explain Code", "Fix Bug", "Add Tests")

3. **System Context:**
   - Task description
   - Output format requirements
   - Constraints and rules

4. **Variable Placeholders:**
   - Use `{{variable_name}}` syntax
   - Include context labels (e.g., "**Code to explain:**")
   - Use code fences where appropriate

**File naming convention:**
- `.github/prompts/{{task-name}}.prompt.md`
- Examples: `explain-code.prompt.md`, `fix-bug.prompt.md`, `add-tests.prompt.md`
- Use kebab-case, be action-oriented

---

### Step 7: Validation & Usage Guidance

**Validate the generated prompt file:**

```bash
# 1. Check YAML frontmatter is valid
head -10 .github/prompts/{{prompt-name}}.prompt.md

# 2. Verify variable syntax (all {{variables}} have closing braces)
grep -o "{{[^}]*}}" .github/prompts/{{prompt-name}}.prompt.md

# 3. Test manually with sample data
# Replace variables with real values and test the prompt
```

**Final checklist:**
- [ ] YAML frontmatter is valid (name, description, variables)
- [ ] All variables use `{{snake_case}}` syntax
- [ ] Variables are properly closed (`{{var}}` not `{{var}`)
- [ ] System context is front-loaded
- [ ] Specific data is back-loaded
- [ ] Output constraints are clear and strict
- [ ] Filename is kebab-case and action-oriented
- [ ] No sensitive data in template

**Output to user:**
```
✅ Created: .github/prompts/{{prompt-name}}.prompt.md
📋 Variables: {{var1}}, {{var2}}, {{var3}}
🎯 Use case: {{one-sentence description}}

💡 To use: Open prompt in editor, replace variables, submit to Copilot
```

**Usage guidance:**
1. Open the prompt file
2. Replace `{{variables}}` with actual values
3. Submit to Copilot (or copy into chat)
4. Repeat with different values as needed

---

## Resources

### references/task_analysis_checklist.md
Guides LLM through understanding the prompt's purpose and requirements.

### references/variable_identification_guide.md
Common variable types, naming conventions, and examples.

### references/context_optimization_patterns.md
"Needle in a Haystack" principle and prompt structure best practices.

### assets/prompt_template.md
Complete prompt file template with handlebars variables and structure.

---

## Common Prompt Templates

### Code Understanding
- **explain-code.prompt.md** - Explain selected code
- **analyze-complexity.prompt.md** - Analyze code complexity
- **trace-execution.prompt.md** - Trace code execution flow

### Code Modification
- **fix-bug.prompt.md** - Fix error based on error message
- **refactor-extract.prompt.md** - Extract function/class
- **optimize-performance.prompt.md** - Optimize for performance

### Code Generation
- **add-tests.prompt.md** - Generate unit tests
- **add-docstring.prompt.md** - Add documentation
- **implement-interface.prompt.md** - Implement interface/protocol

### Documentation
- **document-api.prompt.md** - Document API endpoint
- **write-readme.prompt.md** - Generate README section
- **create-changelog.prompt.md** - Generate changelog entry

---

## Anti-Patterns

### ❌ DON'T:
- Create prompts for complex workflows (use skills)
- Include scripts or executable code (prompts are text only)
- Create prompts for persistent roles (use agents)
- Use prompts for always-on rules (use instructions)
- Over-complicate with too many variables
- Forget to close variable braces `{{var}}`

### ✅ DO:
- Create prompts for simple, repeatable tasks
- Use clear, descriptive variable names
- Front-load system context, back-load data
- Include strict output constraints
- Keep prompts focused on single task
- Test prompts with real data before finalizing
