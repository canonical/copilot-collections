# Variable Identification Guide

Variables are placeholders in prompts that get replaced with actual values at runtime. This guide covers how to identify, name, and use variables effectively.

---

## Variable Categories

### 1. Editor Context Variables
Values derived from the user's current editor state.

```yaml
{{active_file_content}}      # Complete content of the current file
{{selected_code}}             # Code the user has highlighted
{{cursor_position}}           # Current cursor location
{{file_path}}                 # Path to the active file
{{file_name}}                 # Name of the active file
{{file_extension}}            # File extension (.js, .py, etc.)
{{line_number}}               # Current line number
{{surrounding_code}}          # Code around the selection
{{open_files}}                # List of currently open files
{{workspace_path}}            # Root directory of the workspace
```

**When to use:**
- Prompt needs to operate on current code
- Context from editor informs the task
- File-specific operations

**Example:**
```
Analyze the following code for security vulnerabilities:

{{selected_code}}

File: {{file_path}}
Language: {{file_extension}}
```

---

### 2. User Input Variables
Explicit inputs the user provides when invoking the prompt.

```yaml
{{task_description}}          # What the user wants to accomplish
{{user_query}}                # User's question or request
{{target_functionality}}      # Specific feature to implement
{{bug_description}}           # Description of the bug
{{error_message}}             # Error message to debug
{{requirements}}              # Specific requirements or constraints
{{example_input}}             # Sample input for testing
{{expected_output}}           # Expected result or behavior
{{style_preference}}          # Code style preference
{{framework_choice}}          # Preferred framework or library
```

**When to use:**
- Task requires user-specific information
- Customization based on user preferences
- Varying task parameters

**Example:**
```
Generate a {{framework_choice}} component that implements:
{{target_functionality}}

Requirements:
{{requirements}}

Style: {{style_preference}}
```

---

### 3. Project Context Variables
Information about the project, codebase, or environment.

```yaml
{{programming_language}}      # Primary language (JavaScript, Python, etc.)
{{framework}}                 # Framework in use (React, Django, etc.)
{{project_type}}              # Type of project (web, CLI, library, etc.)
{{coding_standards}}          # Project coding conventions
{{test_framework}}            # Testing framework (Jest, pytest, etc.)
{{package_manager}}           # npm, pip, cargo, etc.
{{build_tool}}                # Webpack, Maven, Make, etc.
{{dependencies}}              # Project dependencies
{{project_structure}}         # Organization of the codebase
{{git_branch}}                # Current git branch
{{environment}}               # dev, staging, production
```

**When to use:**
- Output must match project conventions
- Framework-specific code generation
- Project-aware recommendations

**Example:**
```
Create unit tests using {{test_framework}} for the following {{programming_language}} code:

{{selected_code}}

Follow the project's testing patterns:
{{coding_standards}}
```

---

## Complete Variable Reference

### Code Context
| Variable | Description | Example Value |
|----------|-------------|---------------|
| `{{active_file_content}}` | Full text of current file | `"import React from 'react'..."` |
| `{{selected_code}}` | Highlighted code | `"function calculate() { ... }"` |
| `{{cursor_position}}` | Line and column | `"Line 42, Column 15"` |
| `{{surrounding_code}}` | Context around selection | `"...\n{selected}\n..."` |
| `{{file_path}}` | Full file path | `"/src/components/Button.tsx"` |
| `{{file_name}}` | File name only | `"Button.tsx"` |
| `{{file_extension}}` | Extension without dot | `"tsx"` |
| `{{language}}` | Detected language | `"TypeScript"` |

### User Inputs
| Variable | Description | Example Value |
|----------|-------------|---------------|
| `{{user_query}}` | User's request | `"Make this function async"` |
| `{{task_description}}` | Detailed task | `"Add error handling..."` |
| `{{requirements}}` | Specific needs | `"Must support IE11"` |
| `{{error_message}}` | Error to debug | `"TypeError: undefined..."` |
| `{{expected_behavior}}` | What should happen | `"Should return null on error"` |
| `{{test_cases}}` | Test scenarios | `"Empty input, null, large numbers"` |

### Project Info
| Variable | Description | Example Value |
|----------|-------------|---------------|
| `{{programming_language}}` | Primary language | `"Python"` |
| `{{framework}}` | Framework used | `"React"` or `"Django"` |
| `{{test_framework}}` | Testing framework | `"Jest"` or `"pytest"` |
| `{{style_guide}}` | Style standard | `"Airbnb"` or `"PEP 8"` |
| `{{version}}` | Language/framework version | `"Python 3.11"` |
| `{{package_manager}}` | Package manager | `"npm"` or `"poetry"` |

---

## Naming Conventions

### Rules for Variable Names

1. **Use snake_case**
   ```
   ✓ {{user_input}}
   ✓ {{file_path}}
   ✓ {{expected_output}}
   ✗ {{userInput}}
   ✗ {{filepath}}
   ✗ {{ExpectedOutput}}
   ```

2. **Be descriptive, not cryptic**
   ```
   ✓ {{target_functionality}}
   ✓ {{error_message}}
   ✓ {{coding_standards}}
   ✗ {{tgt_func}}
   ✗ {{err_msg}}
   ✗ {{stds}}
   ```

3. **Use full words**
   ```
   ✓ {{description}}
   ✓ {{configuration}}
   ✓ {{requirements}}
   ✗ {{desc}}
   ✗ {{config}}
   ✗ {{reqs}}
   ```

4. **Avoid ambiguity**
   ```
   ✓ {{user_query}}          # Clear: what user asked
   ✓ {{selected_code}}       # Clear: code user selected
   ✗ {{input}}               # Ambiguous: input from where?
   ✗ {{data}}                # Ambiguous: what kind of data?
   ```

5. **Include context in name**
   ```
   ✓ {{test_framework}}      # Not just {{framework}}
   ✓ {{bug_description}}     # Not just {{description}}
   ✓ {{target_language}}     # Not just {{language}}
   ```

---

## Variable Syntax Rules

### Basic Syntax
Variables must be enclosed in double curly braces:

```
Correct:   {{variable_name}}
Incorrect: {variable_name}
Incorrect: {{variable_name}
Incorrect: {{{variable_name}}}
```

### In Text
```markdown
Please analyze the following {{programming_language}} code:

{{selected_code}}

Provide suggestions for improving {{aspect_to_improve}}.
```

### In YAML Frontmatter
```yaml
---
description: Generate tests for {{language}} code
context: |
  Language: {{programming_language}}
  Framework: {{test_framework}}
---
```

### Multiline Context
```markdown
Here is the code to refactor:

{{selected_code}}

Apply these requirements:
{{requirements}}

Target framework: {{framework}}
```

### Nested Context (Avoid)
```markdown
# Don't do this:
The {{type_of_{{language}}_code}} needs review.

# Do this instead:
The {{language}} {{code_type}} needs review.
```

---

## Examples by Prompt Type

### Example 1: Code Generation Prompt

**Identified Variables:**
```yaml
Editor Context:
  - {{file_path}}             # Where to create/modify
  - {{file_extension}}        # Language hint
  - {{surrounding_code}}      # Existing context

User Inputs:
  - {{feature_description}}   # What to build
  - {{requirements}}          # Constraints
  - {{style_preference}}      # Code style choice

Project Context:
  - {{programming_language}}  # Language
  - {{framework}}             # Framework
  - {{coding_standards}}      # Style guide
```

**Usage in Prompt:**
```markdown
You are generating {{programming_language}} code using {{framework}}.

Create the following feature:
{{feature_description}}

Requirements:
{{requirements}}

File context: {{file_path}}
Existing code:
{{surrounding_code}}

Follow these standards:
{{coding_standards}}

Style preference: {{style_preference}}
```

---

### Example 2: Code Review Prompt

**Identified Variables:**
```yaml
Editor Context:
  - {{selected_code}}         # Code to review
  - {{file_name}}             # File being reviewed
  - {{language}}              # Language context

User Inputs:
  - {{review_focus}}          # What to focus on (security, performance, etc.)
  
Project Context:
  - {{coding_standards}}      # Standards to check against
  - {{framework}}             # Framework conventions
```

**Usage in Prompt:**
```markdown
Review the following {{language}} code for {{review_focus}}:

File: {{file_name}}

{{selected_code}}

Check against:
- {{coding_standards}}
- {{framework}} best practices

Provide specific, actionable feedback.
```

---

### Example 3: Debugging Prompt

**Identified Variables:**
```yaml
Editor Context:
  - {{selected_code}}         # Problematic code
  - {{file_path}}             # File location
  
User Inputs:
  - {{error_message}}         # The error
  - {{expected_behavior}}     # What should happen
  - {{actual_behavior}}       # What actually happens
  
Project Context:
  - {{programming_language}}  # Language
  - {{dependencies}}          # Relevant libraries
```

**Usage in Prompt:**
```markdown
Debug the following {{programming_language}} code:

Location: {{file_path}}

Code:
{{selected_code}}

Error:
{{error_message}}

Expected: {{expected_behavior}}
Actual: {{actual_behavior}}

Dependencies: {{dependencies}}

Provide:
1. Root cause analysis
2. Fixed code
3. Explanation
```

---

### Example 4: Documentation Prompt

**Identified Variables:**
```yaml
Editor Context:
  - {{selected_code}}         # Code to document
  - {{file_name}}             # File name
  
User Inputs:
  - {{documentation_style}}   # JSDoc, docstring, etc.
  - {{detail_level}}          # Brief, standard, comprehensive
  
Project Context:
  - {{programming_language}}  # Language
  - {{documentation_standard}} # Project doc standard
```

**Usage in Prompt:**
```markdown
Generate {{documentation_style}} documentation for this {{programming_language}} code:

{{selected_code}}

From file: {{file_name}}

Detail level: {{detail_level}}
Follow: {{documentation_standard}}

Include:
- Function/class description
- Parameters with types
- Return values
- Examples
- Edge cases
```

---

## Anti-Patterns: What NOT to Do

### ❌ Bad Variable Names
```yaml
{{x}}                    # Too vague
{{data}}                 # Ambiguous
{{stuff}}                # Meaningless
{{temp}}                 # What kind of temp?
{{val}}                  # Abbreviation
{{foo}}                  # Placeholder, not descriptive
```

### ❌ Missing Braces
```markdown
# Wrong:
Analyze this code: selected_code

# Right:
Analyze this code: {{selected_code}}
```

### ❌ Mismatched Braces
```markdown
# Wrong:
{{variable_name}
{variable_name}}
{{{variable_name}}

# Right:
{{variable_name}}
```

### ❌ Hardcoded Values That Should Be Variables
```markdown
# Wrong:
Generate Python code following PEP 8 standards.

# Right:
Generate {{programming_language}} code following {{coding_standards}} standards.
```

### ❌ Over-Generic Variables
```markdown
# Wrong:
{{input}}                # Input from where?
{{output}}               # Output of what?
{{config}}               # What configuration?

# Right:
{{user_query}}           # Specific
{{expected_output}}      # Clear context
{{build_configuration}}  # Precise
```

### ❌ Inconsistent Naming
```markdown
# Wrong - mixing styles:
{{userName}}
{{file_path}}
{{LANGUAGE}}
{{Test-Framework}}

# Right - consistent snake_case:
{{user_name}}
{{file_path}}
{{language}}
{{test_framework}}
```

---

## Variable Checklist

Before finalizing your prompt, verify:

- [ ] All variables use `{{double_braces}}`
- [ ] Names are in snake_case
- [ ] Names are descriptive and unambiguous
- [ ] No abbreviations (unless universally known like `url`, `id`)
- [ ] Variables are categorized correctly (editor/user/project)
- [ ] Required vs optional variables are clear
- [ ] No hardcoded values that should be variables
- [ ] Variable names are consistent throughout the prompt
- [ ] Documentation explains what each variable contains

---

## Quick Reference Card

```
SYNTAX:          {{variable_name}}
CASE:            snake_case
LENGTH:          Descriptive, not abbreviated
CONTEXT:         Included in name when needed
CONSISTENCY:     Same name = same value throughout

Common Patterns:
  {{selected_code}}
  {{user_query}}
  {{programming_language}}
  {{framework}}
  {{file_path}}
  {{requirements}}
  {{coding_standards}}
  {{error_message}}
  {{expected_output}}
  {{test_framework}}
```

Use this guide every time you identify variables for a new prompt.
