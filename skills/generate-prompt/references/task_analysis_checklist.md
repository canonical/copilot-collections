# Task Analysis Checklist

This checklist provides a systematic approach to understanding prompt requirements before generating a prompt. Use all five phases to ensure comprehensive coverage.

---

## Phase 1: Task Description

**Objective:** Understand what the prompt should accomplish

### Key Questions
- [ ] What is the primary goal of this prompt?
- [ ] What problem does it solve for the user?
- [ ] What is the expected outcome or deliverable?
- [ ] Is this a generative, analytical, or transformative task?
- [ ] What domain knowledge is required?

### Analysis Template
```
Task Type: [Code Generation | Analysis | Refactoring | Documentation | Debug | Test]
Primary Goal: [One sentence description]
Success Criteria: [What indicates successful completion?]
Domain: [Programming language, framework, or specialty area]
```

---

## Phase 2: Trigger Conditions

**Objective:** Identify when and why this prompt should be used

### Key Questions
- [ ] What user intent triggers this prompt?
- [ ] What keywords or phrases indicate this task?
- [ ] Are there prerequisite conditions?
- [ ] What context makes this prompt appropriate vs inappropriate?
- [ ] Are there overlapping prompts that need differentiation?

### Analysis Template
```
Primary Triggers: [User actions or requests]
Context Requirements: [Files, selection, project state]
Differentiation: [How this differs from similar prompts]
Anti-patterns: [When NOT to use this prompt]
```

---

## Phase 3: Input Requirements

**Objective:** Identify all data needed to execute the task

### Key Questions
- [ ] What editor context is required? (selection, file, workspace)
- [ ] What user inputs are needed? (parameters, preferences)
- [ ] What project context matters? (language, framework, conventions)
- [ ] What external references might be helpful?
- [ ] Are there optional vs required inputs?

### Analysis Template
```
Required Editor Context:
  - [ ] Active file content
  - [ ] Selected code
  - [ ] Cursor position
  - [ ] Open files
  - [ ] Project structure

Required User Inputs:
  - [ ] Task description
  - [ ] Parameters
  - [ ] Preferences
  - [ ] Target specifications

Required Project Context:
  - [ ] Language/framework
  - [ ] Coding standards
  - [ ] Dependencies
  - [ ] Architecture patterns
```

---

## Phase 4: Output Format

**Objective:** Define the structure and format of the response

### Key Questions
- [ ] What format should the output take? (code, explanation, list, diff)
- [ ] Should output be single or multi-part?
- [ ] What level of detail is appropriate?
- [ ] Are there formatting constraints? (markdown, code blocks, comments)
- [ ] Should explanations accompany code?

### Analysis Template
```
Output Type: [Code | Documentation | Analysis | Mixed]
Structure: [Format and organization]
Detail Level: [Concise | Moderate | Comprehensive]
Formatting Rules: [Code blocks, headings, lists, etc.]
Explanation Requirements: [When and how to explain]
```

---

## Phase 5: Constraints

**Objective:** Identify rules, limitations, and quality requirements

### Key Questions
- [ ] Are there style or convention requirements?
- [ ] What should be preserved vs changed?
- [ ] Are there length or complexity limits?
- [ ] What edge cases need handling?
- [ ] Are there security or safety considerations?
- [ ] What constitutes a quality response?

### Analysis Template
```
Style Requirements: [Conventions, patterns, standards]
Preservation Rules: [What must not change]
Boundaries: [Scope limits, length constraints]
Edge Cases: [Special situations to handle]
Quality Criteria: [What makes a good vs bad output]
Safety Rules: [Security, privacy, best practices]
```

---

## Complete Examples

### Example 1: Explain Code

#### Phase 1: Task Description
```
Task Type: Analysis
Primary Goal: Provide clear explanation of selected code's functionality
Success Criteria: User understands what code does, how it works, and why
Domain: Multi-language (any programming language)
```

#### Phase 2: Trigger Conditions
```
Primary Triggers: 
  - User selects code and asks "explain this"
  - User asks "what does this do?"
  - User needs to understand unfamiliar code
  
Context Requirements:
  - Code must be selected in editor
  - Must be valid code (not partial syntax)
  
Differentiation:
  - Unlike "Document Code": focuses on understanding, not creating docs
  - Unlike "Review Code": explains rather than critiques
  
Anti-patterns:
  - Don't use for generating new code
  - Not for making changes or improvements
```

#### Phase 3: Input Requirements
```
Required Editor Context:
  ✓ Selected code
  ✓ File language/extension
  ✓ Surrounding context (optional, for clarity)

Required User Inputs:
  - None (selection implies the request)

Required Project Context:
  ✓ Programming language
  - Framework (helpful but not required)
  - Project type (helpful for domain context)
```

#### Phase 4: Output Format
```
Output Type: Analysis (structured explanation)
Structure:
  1. High-level summary (1-2 sentences)
  2. Step-by-step breakdown
  3. Key concepts or patterns used
  4. Potential gotchas or edge cases
  
Detail Level: Moderate (enough to understand, not overwhelming)
Formatting Rules:
  - Use headings for sections
  - Code references in backticks
  - Numbered lists for step-by-step
  
Explanation Requirements:
  - Plain language, avoid jargon when possible
  - Define technical terms when used
  - Use analogies for complex concepts
```

#### Phase 5: Constraints
```
Style Requirements:
  - Clear, educational tone
  - Assume reader has basic programming knowledge
  
Preservation Rules:
  - Don't modify or suggest changes to the code
  - Explain as-is, even if code has issues
  
Boundaries:
  - Focus on selected code only
  - Mention but don't deep-dive on dependencies
  
Quality Criteria:
  - Someone unfamiliar with the code can understand it
  - Technical accuracy
  - Appropriate depth for code complexity
```

---

### Example 2: Fix Bug

#### Phase 1: Task Description
```
Task Type: Code Generation + Refactoring
Primary Goal: Identify and fix a bug in existing code
Success Criteria: Bug is fixed, code works correctly, explanation provided
Domain: Multi-language debugging
```

#### Phase 2: Trigger Conditions
```
Primary Triggers:
  - User reports code is broken/not working
  - User describes unexpected behavior
  - User provides error message
  
Context Requirements:
  - Must have problematic code selected or in active file
  - Bug description or error message helpful
  
Differentiation:
  - Unlike "Improve Code": focuses on correctness, not optimization
  - Unlike "Explain Code": makes changes rather than just explaining
```

#### Phase 3: Input Requirements
```
Required Editor Context:
  ✓ Active file with buggy code
  ✓ Selected code (if specific section)

Required User Inputs:
  ✓ Bug description or symptom
  - Error message (if available)
  - Expected vs actual behavior

Required Project Context:
  ✓ Language/framework
  - Test files (to verify fix)
  - Related dependencies
```

#### Phase 4: Output Format
```
Output Type: Mixed (code + explanation)
Structure:
  1. Bug identification (what's wrong)
  2. Fixed code (complete, ready to use)
  3. Explanation of fix
  4. Testing suggestions
  
Detail Level: Comprehensive for fix explanation
Formatting Rules:
  - Code in fenced blocks with language
  - Highlight changed lines with comments
  - Use diff format if helpful
```

#### Phase 5: Constraints
```
Style Requirements:
  - Match existing code style
  - Minimal changes (surgical fix)
  
Preservation Rules:
  - Preserve unrelated functionality
  - Keep existing variable names unless they're part of the bug
  
Boundaries:
  - Fix only the reported bug
  - Don't refactor unrelated code
  
Quality Criteria:
  - Fix actually resolves the issue
  - No new bugs introduced
  - Clear explanation of root cause
```

---

### Example 3: Add Tests

#### Phase 1: Task Description
```
Task Type: Code Generation
Primary Goal: Generate test cases for existing code
Success Criteria: Comprehensive, runnable tests that verify functionality
Domain: Testing frameworks (Jest, pytest, JUnit, etc.)
```

#### Phase 2: Trigger Conditions
```
Primary Triggers:
  - User requests tests for selected code
  - User asks to "add test coverage"
  - Code exists but lacks tests
  
Context Requirements:
  - Code to test must be selected or identified
  - Testing framework should be detectable or specified
```

#### Phase 3: Input Requirements
```
Required Editor Context:
  ✓ Code to be tested (function, class, module)
  ✓ File language

Required User Inputs:
  - Specific test scenarios (optional)
  - Coverage goals (optional)

Required Project Context:
  ✓ Testing framework (detect from project or ask)
  - Existing test patterns (for consistency)
  - Mocking/fixture patterns
```

#### Phase 4: Output Format
```
Output Type: Code (test suite)
Structure:
  1. Import statements
  2. Test setup/fixtures if needed
  3. Test cases grouped logically
  4. Each test clearly named and documented
  
Detail Level: Comprehensive (cover main cases + edge cases)
Formatting Rules:
  - Follow testing framework conventions
  - Descriptive test names
  - AAA pattern (Arrange, Act, Assert)
```

#### Phase 5: Constraints
```
Style Requirements:
  - Match project's test style
  - Use framework best practices
  - Follow naming conventions
  
Quality Criteria:
  - Tests are independent and isolated
  - Cover happy path + edge cases
  - Tests are clear and maintainable
  - Assertions are specific and meaningful
```

---

### Example 4: Document API

#### Phase 1: Task Description
```
Task Type: Documentation Generation
Primary Goal: Create API documentation for functions, classes, or endpoints
Success Criteria: Complete, accurate documentation in appropriate format
Domain: API documentation (JSDoc, docstrings, OpenAPI, etc.)
```

#### Phase 2: Trigger Conditions
```
Primary Triggers:
  - User selects code and requests documentation
  - User asks to "document this API"
  - Undocumented code needs public interface docs
  
Context Requirements:
  - Code must define a public interface (function, class, endpoint)
```

#### Phase 3: Input Requirements
```
Required Editor Context:
  ✓ Code to document (function, class, or file)
  ✓ Function signatures and parameters

Required User Inputs:
  - Documentation style preference (optional)
  - Additional context about purpose (optional)

Required Project Context:
  ✓ Language (determines doc format)
  - Existing documentation patterns
  - Documentation standard (JSDoc, Sphinx, etc.)
```

#### Phase 4: Output Format
```
Output Type: Documentation (formatted comments)
Structure:
  1. Brief description
  2. Parameters/arguments with types and descriptions
  3. Return value(s)
  4. Exceptions/errors
  5. Examples (for complex APIs)
  6. Notes or warnings if applicable
  
Detail Level: Comprehensive but concise
Formatting Rules:
  - Follow language documentation standard
  - Use proper tags (@param, @returns, etc.)
  - Type annotations where applicable
```

#### Phase 5: Constraints
```
Style Requirements:
  - Match existing documentation style
  - Use standard documentation format for language
  
Preservation Rules:
  - Don't modify the code itself
  - Only add/update comments/docstrings
  
Quality Criteria:
  - Accurate parameter and return descriptions
  - Examples are correct and runnable
  - Covers all public methods/parameters
  - Clear and concise language
```

---

## Using This Checklist

1. **Start with Phase 1** to get clear on the fundamental purpose
2. **Work through phases sequentially** - each builds on the previous
3. **Document your answers** - they become inputs for prompt generation
4. **Review all phases** before generating the prompt
5. **Revisit if unclear** - ambiguity here means ambiguity in the prompt

The more thorough your analysis, the better your prompt will be.
