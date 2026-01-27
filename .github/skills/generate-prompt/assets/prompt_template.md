# Prompt Template

Use this template as a starting point for creating new prompts. Replace all placeholders with actual content.

---

## Template Structure

```markdown
---
# YAML Frontmatter: Metadata about the prompt
name: {{prompt_name}}
description: {{brief_description}}
version: 1.0.0
category: {{category}}  # e.g., code-generation, analysis, refactoring, documentation
author: {{your_name}}
date: {{creation_date}}
tags:
  - {{tag1}}
  - {{tag2}}
  - {{tag3}}
---

# {{Prompt Title}}

## System Context
<!-- Define the AI's role and expertise -->

You are {{role_description}}.

## Critical Constraints
<!-- Non-negotiable rules and limitations -->

MUST:
- {{required_behavior_1}}
- {{required_behavior_2}}
- {{required_behavior_3}}

MUST NOT:
- {{prohibited_behavior_1}}
- {{prohibited_behavior_2}}
- {{prohibited_behavior_3}}

## Project Context
<!-- Information about the environment and project -->

**Environment:**
- Language: {{programming_language}}
- Framework: {{framework}}
- Version: {{version}}
- Standards: {{coding_standards}}

**Additional Context:**
{{additional_project_context}}

## Requirements
<!-- Specific requirements for the task -->

1. {{requirement_1}}
2. {{requirement_2}}
3. {{requirement_3}}
4. {{requirement_4}}

## Workflow
<!-- Step-by-step process to follow -->

1. **{{step_1_name}}**: {{step_1_description}}
2. **{{step_2_name}}**: {{step_2_description}}
3. **{{step_3_name}}**: {{step_3_description}}
4. **{{step_4_name}}**: {{step_4_description}}

## Examples
<!-- Demonstrate patterns and expected quality -->

### Good Example:
\`\`\`{{language}}
{{good_example_code}}
\`\`\`

**Why this is good:**
- {{reason_1}}
- {{reason_2}}

### Bad Example:
\`\`\`{{language}}
{{bad_example_code}}
\`\`\`

**Why this is bad:**
- {{reason_1}}
- {{reason_2}}

## Output Format
<!-- Structure the AI should follow -->

Provide your response in the following format:

### {{section_1_name}}
{{section_1_description}}

### {{section_2_name}}
{{section_2_description}}

### {{section_3_name}}
{{section_3_description}}

## Quality Criteria
<!-- What constitutes a good response -->

Your output must:
- [ ] {{quality_criterion_1}}
- [ ] {{quality_criterion_2}}
- [ ] {{quality_criterion_3}}
- [ ] {{quality_criterion_4}}

## Task
<!-- The specific task to perform with variable inputs -->

{{task_description}}

**Input:**
{{input_variable}}

**Context:**
{{context_variable}}

**File:** {{file_path}}

---

## Variables Reference
<!-- Document all variables used in this prompt -->

| Variable | Type | Description | Required |
|----------|------|-------------|----------|
| `{{input_variable}}` | {{type}} | {{description}} | Yes |
| `{{context_variable}}` | {{type}} | {{description}} | Yes |
| `{{file_path}}` | string | Path to the file | No |
| `{{programming_language}}` | string | Programming language | Yes |
| `{{framework}}` | string | Framework being used | No |

```

---

## Complete Filled Example: Test Generation Prompt

```markdown
---
name: generate-unit-tests
description: Generate comprehensive unit tests for selected code
version: 1.0.0
category: test-generation
author: AI Prompt Engineer
date: 2024-01-15
tags:
  - testing
  - code-generation
  - quality-assurance
---

# Generate Unit Tests

## System Context

You are a test engineer specializing in {{programming_language}} with expertise in {{test_framework}}.

## Critical Constraints

MUST:
- Generate runnable, valid test code
- Cover both happy path and edge cases
- Follow AAA pattern (Arrange, Act, Assert)
- Use descriptive test names

MUST NOT:
- Generate tests that modify production code
- Include tests without assertions
- Use vague test names like "test1" or "it works"
- Skip error case testing

## Project Context

**Environment:**
- Language: {{programming_language}}
- Framework: {{framework}}
- Test Framework: {{test_framework}}
- Version: {{language_version}}
- Standards: {{coding_standards}}

**Additional Context:**
Test files should be located in {{test_directory}} and follow the naming convention `{{test_file_pattern}}`.

## Requirements

1. Generate tests for all public methods/functions
2. Include setup and teardown if needed
3. Test normal inputs, boundary conditions, and invalid inputs
4. Add clear comments explaining complex test scenarios
5. Mock external dependencies
6. Ensure tests are independent and can run in any order

## Workflow

1. **Analyze**: Identify all testable units in the selected code
2. **Plan**: Determine test cases needed (normal, edge, error)
3. **Generate**: Create test code following project patterns
4. **Document**: Add comments for non-obvious test logic

## Examples

### Good Example:
\`\`\`javascript
describe('calculateDiscount', () => {
  test('applies 10% discount for standard customers', () => {
    // Arrange
    const price = 100;
    const customerType = 'standard';
    
    // Act
    const result = calculateDiscount(price, customerType);
    
    // Assert
    expect(result).toBe(90);
  });

  test('throws error when price is negative', () => {
    // Arrange
    const price = -10;
    const customerType = 'standard';
    
    // Act & Assert
    expect(() => calculateDiscount(price, customerType))
      .toThrow('Price must be non-negative');
  });
});
\`\`\`

**Why this is good:**
- Descriptive test names explain scenario
- AAA pattern clearly visible
- Tests both normal case and error handling
- Specific assertions

### Bad Example:
\`\`\`javascript
test('test1', () => {
  const x = calculateDiscount(100, 'standard');
  expect(x).toBeTruthy();
});
\`\`\`

**Why this is bad:**
- Vague test name
- No AAA structure
- Weak assertion (toBeTruthy instead of specific value)
- Missing edge case tests

## Output Format

Provide your response in the following format:

### Test Suite
Complete, runnable test code with imports and setup.

### Coverage Summary
List of test cases generated:
- Normal cases tested
- Edge cases covered
- Error conditions handled

### Notes
Any important considerations or suggestions for additional testing.

## Quality Criteria

Your output must:
- [ ] Be valid, runnable test code
- [ ] Follow the project's test framework syntax
- [ ] Include at least 3 test cases per function
- [ ] Have 100% coverage of public methods
- [ ] Use specific assertions (not just truthy/falsy)
- [ ] Include meaningful test names

## Task

Generate comprehensive unit tests for the following code:

**Code to Test:**
{{selected_code}}

**Context:**
- File: {{file_path}}
- Test file should be: {{test_file_path}}

---

## Variables Reference

| Variable | Type | Description | Required |
|----------|------|-------------|----------|
| `{{selected_code}}` | string | Code to generate tests for | Yes |
| `{{file_path}}` | string | Path to the source file | Yes |
| `{{test_file_path}}` | string | Path where test file should be created | Yes |
| `{{programming_language}}` | string | Programming language (JavaScript, Python, etc.) | Yes |
| `{{test_framework}}` | string | Testing framework (Jest, pytest, JUnit, etc.) | Yes |
| `{{framework}}` | string | Application framework (React, Django, etc.) | No |
| `{{language_version}}` | string | Language version (Node 18, Python 3.11, etc.) | No |
| `{{coding_standards}}` | string | Project coding standards | No |
| `{{test_directory}}` | string | Directory for test files | No |
| `{{test_file_pattern}}` | string | Test file naming pattern | No |

```

---

## Usage Instructions

1. **Copy this template** to start a new prompt
2. **Replace all `{{placeholders}}`** with actual content
3. **Remove any sections** that don't apply
4. **Add sections** if your prompt needs them
5. **Test the prompt** with sample inputs
6. **Iterate** based on results

## Section Guidelines

### YAML Frontmatter
- Keep metadata concise but complete
- Use semantic versioning
- Choose appropriate category
- Add relevant tags for discoverability

### System Context
- Define the AI's role clearly
- Specify domain expertise
- Set the right tone

### Critical Constraints
- Be explicit about must/must not
- Front-load important rules
- Keep constraints specific and actionable

### Requirements
- Number for easy reference
- One requirement per line
- Make them testable/verifiable

### Workflow
- Break down complex tasks
- Name each step clearly
- Keep sequential and logical

### Examples
- Show both good and bad
- Explain why each is good/bad
- Use realistic scenarios

### Output Format
- Be specific about structure
- Use headings and formatting
- Show exact format expected

### Quality Criteria
- Use checkboxes
- Make criteria objective
- Cover all important aspects

### Task
- Put this at the end
- Include all relevant variables
- Be clear and specific

---

## Quick Start Checklist

- [ ] Frontmatter filled out
- [ ] System context defined
- [ ] Constraints specified
- [ ] Requirements listed
- [ ] Workflow outlined
- [ ] Examples provided
- [ ] Output format defined
- [ ] Quality criteria set
- [ ] Task description written
- [ ] All variables documented
- [ ] Template tested with sample inputs

You're ready to generate effective prompts!
