# Context Optimization Patterns

Effective prompts deliver the right information in the right order. This guide shows how to structure prompts for maximum clarity and performance.

---

## The "Needle in a Haystack" Principle

### The Problem
Language models process prompts sequentially. Information buried in the middle of long prompts is harder to recall than information at the beginning or end. This is called the "needle in a haystack" problem.

### The Solution
**Strategic positioning of critical information:**

1. **Front-load** critical instructions and constraints
2. **Back-load** the specific task and output requirements
3. **Middle** contains supporting context and examples

### Why This Works
```
[STRONG RECALL]  ← Beginning: Role, rules, critical constraints
[WEAKER RECALL]  ← Middle: Examples, context, background
[STRONG RECALL]  ← End: Specific task, output format
```

The model pays most attention to what it saw first (recency in training) and last (what it needs to act on immediately).

---

## Prompt Structure Best Practices

### Optimal Structure Template

```markdown
1. ROLE & CONSTRAINTS          [Front-loaded, top priority]
   - Who the AI should be
   - Critical rules and limitations
   - Non-negotiable requirements

2. CONTEXT & BACKGROUND        [Middle, supporting information]
   - Domain knowledge
   - Project context
   - Relevant background

3. EXAMPLES                    [Middle-to-late, pattern setting]
   - Input/output examples
   - Edge cases
   - Format demonstrations

4. SPECIFIC TASK               [Back-loaded, immediate action]
   - Exact task to perform
   - Input data/variables
   - Output format requirements
```

---

## Complete Structure Examples

### Example 1: Code Review Prompt

#### ❌ Bad Structure (Poorly Organized)
```markdown
Review this code. Here's the code:

{{selected_code}}

Oh, and make sure you check for security issues, and also performance 
problems would be good to find. We use React here and follow Airbnb 
style guide. The code is in {{file_name}}. Don't suggest style changes 
that are just personal preference. Focus on real issues. Here are some 
things we've found before in other reviews: XSS vulnerabilities, memory 
leaks, N+1 queries. Output should be a list of issues with severity.
```

**Problems:**
- Instructions scattered throughout
- Critical constraints mentioned late
- Task buried in the middle
- No clear structure

#### ✅ Good Structure (Optimized)
```markdown
You are a senior code reviewer specializing in {{programming_language}}.

CRITICAL RULES:
- Only report genuine bugs, security issues, or performance problems
- Do NOT flag style preferences or minor formatting
- Every issue must include severity (Critical/High/Medium/Low)

PROJECT CONTEXT:
- Framework: {{framework}}
- Standards: {{coding_standards}}
- File: {{file_name}}

Common issues to watch for:
- XSS vulnerabilities
- Memory leaks
- N+1 query problems
- Race conditions

OUTPUT FORMAT:
For each issue provide:
1. Severity level
2. Line number(s)
3. Description of the problem
4. Specific fix recommendation

Review this code:

{{selected_code}}
```

**Improvements:**
- Role and critical rules up front
- Context in the middle
- Specific task at the end
- Clear output format
- Easy to parse and follow

---

### Example 2: Test Generation Prompt

#### ❌ Bad Structure
```markdown
I need tests for this function:

{{selected_code}}

Use {{test_framework}} and make sure you cover edge cases. Also we 
normally use the AAA pattern (Arrange, Act, Assert) in our tests. Don't 
forget to test error conditions. The tests should be in the same style 
as our other tests. Here's what a typical test looks like:

test('example', () => {
  // setup
  const input = createInput();
  // execute
  const result = doThing(input);
  // verify
  expect(result).toBe(expected);
});

Make the test names descriptive. Cover normal cases and edge cases.
```

**Problems:**
- Task stated before context
- Instructions fragmented
- Example disconnected from requirements
- Repetitive points

#### ✅ Good Structure
```markdown
You are a test engineer writing {{test_framework}} tests for {{programming_language}} code.

REQUIREMENTS:
- Follow AAA pattern (Arrange, Act, Assert)
- Descriptive test names that explain what is tested
- Cover both happy path and edge cases
- Include error condition tests
- Match the project's existing test style

STANDARD TEST PATTERN:
test('descriptive name explaining scenario', () => {
  // Arrange: setup
  const input = createInput();
  
  // Act: execute
  const result = doThing(input);
  
  // Assert: verify
  expect(result).toBe(expected);
});

COVERAGE REQUIREMENTS:
- Normal input cases
- Boundary conditions
- Invalid input handling
- Error states
- Edge cases

Generate comprehensive tests for:

{{selected_code}}

Test file: {{test_file_path}}
```

**Improvements:**
- Clear role and requirements first
- Pattern demonstrated once, clearly
- Coverage needs explicit
- Code at the end where AI focuses

---

### Example 3: Bug Fix Prompt

#### ❌ Bad Structure
```markdown
Fix this bug:

{{selected_code}}

The error is: {{error_message}}

Expected: {{expected_behavior}}
Actual: {{actual_behavior}}

Don't change unrelated code. Provide an explanation of what was wrong.
Make sure the fix doesn't break other things. We're using {{framework}}.
```

**Problems:**
- Code shown before understanding the problem
- Constraints mentioned too late
- No clear workflow
- Output format not specified

#### ✅ Good Structure
```markdown
You are debugging {{programming_language}} code in a {{framework}} project.

CONSTRAINTS:
- Fix ONLY the specific bug described
- Preserve all unrelated code and functionality
- Ensure fix doesn't introduce new issues
- Follow existing code style

PROBLEM DESCRIPTION:
Error: {{error_message}}
Expected behavior: {{expected_behavior}}
Actual behavior: {{actual_behavior}}

ANALYSIS WORKFLOW:
1. Identify root cause
2. Determine minimal fix
3. Verify fix doesn't break related code
4. Explain the issue and solution

OUTPUT FORMAT:
1. **Root Cause**: Brief explanation of what's wrong
2. **Fixed Code**: Complete corrected version
3. **Changes Made**: Specific lines changed and why
4. **Verification**: How to confirm the fix works

Problematic code:

{{selected_code}}

File: {{file_path}}
```

**Improvements:**
- Constraints before seeing code
- Problem context clearly organized
- Explicit workflow to follow
- Structured output format
- Code presented last for fixing

---

### Example 4: Documentation Generation

#### ❌ Bad Structure
```markdown
Document this:

{{selected_code}}

Use {{documentation_style}}. Include parameters, return values, and 
examples. Be comprehensive but concise. Don't document obvious things.
Make sure to mention edge cases and any important notes.
```

**Problems:**
- Too terse, missing context
- No clear sections
- Conflicting instructions (comprehensive but concise?)
- No quality criteria

#### ✅ Good Structure
```markdown
You are generating {{documentation_style}} documentation for {{programming_language}} code.

DOCUMENTATION STANDARDS:
- Follow {{documentation_style}} format exactly
- Be thorough for public APIs, concise for obvious behavior
- Include type information where applicable
- Use proper tags (@param, @returns, @throws, etc.)

REQUIRED SECTIONS:
1. Brief description (1-2 sentences)
2. Detailed explanation (if complex)
3. Parameters: name, type, description
4. Return value: type and description
5. Exceptions/Errors: what can be thrown
6. Examples: for non-trivial functionality
7. Notes: edge cases, warnings, gotchas

QUALITY CRITERIA:
- Accurate type information
- Examples are runnable
- Edge cases documented
- Clear and professional language

Code to document:

{{selected_code}}

Context: {{file_path}}
Project: {{framework}} application
```

**Improvements:**
- Standards established first
- Required sections explicit
- Quality criteria defined
- Code comes after instructions

---

### Example 5: Code Refactoring

#### ❌ Bad Structure
```markdown
Refactor:

{{selected_code}}

Make it better. Improve readability and performance. Don't break tests.
Use modern {{language}} features. Follow {{style_guide}}.
```

**Problems:**
- "Better" is subjective
- Multiple goals potentially conflict
- No prioritization
- No output structure

#### ✅ Good Structure
```markdown
You are refactoring {{programming_language}} code following {{style_guide}} standards.

GOALS (in priority order):
1. Improve readability and maintainability
2. Optimize performance (if significant gains possible)
3. Modernize syntax using {{language}} {{version}} features
4. Reduce complexity and code smell

CONSTRAINTS:
- Preserve exact functionality (same inputs → same outputs)
- Do not break existing tests
- Keep changes minimal and focused
- Maintain backward compatibility

REFACTORING PATTERNS TO APPLY:
- Extract complex logic into well-named functions
- Replace loops with declarative methods (map, filter, reduce)
- Use modern syntax (destructuring, arrow functions, etc.)
- Eliminate code duplication
- Simplify conditional logic

OUTPUT FORMAT:
1. **Refactored Code**: Complete, ready to use
2. **Changes Summary**: List of improvements made
3. **Performance Impact**: Expected impact if any
4. **Potential Risks**: Any compatibility or behavior concerns

Code to refactor:

{{selected_code}}

File: {{file_path}}
Framework: {{framework}}
```

**Improvements:**
- Clear prioritized goals
- Explicit constraints
- Specific patterns to look for
- Structured output
- All context before the code

---

### Example 6: API Endpoint Generation

#### ❌ Bad Structure
```markdown
Create a {{http_method}} endpoint for {{endpoint_purpose}}.

Requirements: {{requirements}}

Use {{framework}} and follow REST principles. Should handle errors.
Return JSON. Validate input. Add logging. Use async/await.
```

**Problems:**
- Too many requirements in a list
- No structure or prioritization
- Missing security considerations
- No example format

#### ✅ Good Structure
```markdown
You are building a {{http_method}} REST API endpoint using {{framework}}.

ENDPOINT SPECIFICATION:
- Purpose: {{endpoint_purpose}}
- Route: {{endpoint_route}}
- Method: {{http_method}}

REQUIREMENTS:
{{requirements}}

IMPLEMENTATION CHECKLIST:
1. Input validation with clear error messages
2. Authentication/authorization checks
3. Business logic implementation
4. Error handling (try/catch with specific errors)
5. Logging (request received, errors, success)
6. Async/await for I/O operations
7. JSON response format

SECURITY:
- Validate and sanitize all inputs
- Check user permissions
- Prevent injection attacks
- Rate limiting considerations

ERROR HANDLING:
- 400: Invalid input
- 401: Unauthorized
- 403: Forbidden
- 404: Not found
- 500: Server error

RESPONSE FORMAT:
Success: 
{
  "success": true,
  "data": { ... }
}

Error:
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message"
  }
}

Generate the complete endpoint handler:

Existing code context (if any):
{{surrounding_code}}
```

**Improvements:**
- Clear specification upfront
- Checklist ensures nothing missed
- Security explicitly addressed
- Error codes defined
- Response format shown
- Code context at end

---

## Context Ordering Principles

### 1. Role Before Task
```markdown
# Good:
You are a {{language}} expert. Generate a function that...

# Bad:
Generate a function that... (Oh, you're a {{language}} expert)
```

### 2. Constraints Before Freedom
```markdown
# Good:
MUST NOT modify database schema. Now, optimize this query...

# Bad:
Optimize this query... (don't change the schema though)
```

### 3. Format Before Content
```markdown
# Good:
Output must be valid JSON with these fields: {...}
Here's the data: {{data}}

# Bad:
Here's the data: {{data}}
Make it JSON somehow
```

### 4. Examples Before Task
```markdown
# Good:
Good commit message: "feat(auth): add OAuth2 support"
Bad commit message: "fixed stuff"
Now write a message for: {{changes}}

# Bad:
Write a message for: {{changes}}
Here's what good ones look like: ...
```

---

## Output Constraint Patterns

### Format Constraints
```markdown
OUTPUT REQUIREMENTS:
- Format: {{format_type}}
- Length: {{max_length}}
- Structure: {{structure_requirements}}
- Language: {{output_language}}
```

### Length Constraints
```markdown
RESPONSE LENGTH:
- Concise: 2-3 sentences maximum
- Standard: 1-2 paragraphs
- Comprehensive: Detailed multi-section response
- Code only: No explanation unless errors found
```

### Tone Constraints
```markdown
TONE AND STYLE:
- Professional and technical
- Assume expert audience
- Direct and actionable
- No marketing language
- No apologetic hedging
```

### Behavioral Constraints
```markdown
BEHAVIOR RULES:
- Ask clarifying questions if requirements are ambiguous
- Refuse requests that would generate insecure code
- Suggest alternatives when asked approach is suboptimal
- Admit when you don't have enough context
```

---

## Before/After Complete Examples

### Example A: Code Explanation

**Before (Unoptimized):**
```markdown
Explain this code: {{selected_code}}

Be clear and thorough. Use simple language. The user might not be 
familiar with {{language}}. Explain what it does and how it works.
Don't assume too much knowledge. Also explain why certain approaches 
were used if it's not obvious.
```

**After (Optimized):**
```markdown
You are a technical educator explaining {{language}} code to a developer 
with basic programming knowledge.

EXPLANATION STRUCTURE:
1. **What it does** (1-2 sentence summary)
2. **How it works** (step-by-step breakdown)
3. **Key concepts** (techniques or patterns used)
4. **Why this approach** (rationale for design choices)

STYLE GUIDELINES:
- Use plain language, define technical terms
- Code references in `backticks`
- Numbered steps for sequential logic
- Examples or analogies for complex concepts

Explain this code:

{{selected_code}}

File: {{file_name}}
Language: {{programming_language}}
```

---

### Example B: Performance Optimization

**Before (Unoptimized):**
```markdown
Make this faster:

{{selected_code}}

Look for performance issues. Consider algorithmic complexity, unnecessary 
loops, redundant operations, inefficient data structures. Profile hot 
paths. Don't break functionality. Explain what you changed and why it's 
faster. Benchmark if possible.
```

**After (Optimized):**
```markdown
You are optimizing {{programming_language}} code for performance.

ANALYSIS PRIORITIES:
1. Algorithmic complexity (O(n²) → O(n log n) → O(n))
2. Data structure efficiency (array vs set vs map)
3. Redundant operations (caching, memoization)
4. I/O optimization (batching, async)
5. Memory usage (avoid unnecessary allocations)

CONSTRAINTS:
- Preserve exact functionality
- No breaking changes to API
- Maintain code readability
- Only optimize if measurable improvement expected

OPTIMIZATION WORKFLOW:
1. Identify bottlenecks
2. Propose optimizations
3. Implement changes
4. Explain performance impact

OUTPUT:
1. **Identified Issues**: What's slow and why
2. **Optimized Code**: Complete improved version
3. **Performance Gain**: Expected improvement (e.g., "O(n²) → O(n)")
4. **Trade-offs**: Any costs (memory, complexity)

Code to optimize:

{{selected_code}}

Context: {{file_path}}
Framework: {{framework}}
```

---

## Context Optimization Checklist

Before finalizing your prompt, verify:

- [ ] Critical constraints at the top
- [ ] Role defined before task assigned
- [ ] Examples positioned before the specific task
- [ ] The actual task/data at the end
- [ ] Output format specified near the task
- [ ] No critical information buried in middle
- [ ] Instructions flow logically
- [ ] No repetition or conflicting statements
- [ ] Clear section headers for easy scanning
- [ ] Variables positioned where they're most relevant

---

## Quick Reference: Optimal Flow

```
┌─────────────────────────────────────┐
│  1. ROLE & CRITICAL CONSTRAINTS     │  ← Front-loaded
│     "You are X. You MUST/MUST NOT"  │
├─────────────────────────────────────┤
│  2. CONTEXT & BACKGROUND            │  ← Middle
│     "Project uses X, follows Y"     │
├─────────────────────────────────────┤
│  3. REQUIREMENTS & WORKFLOW         │  ← Middle
│     "Do A, then B, then C"          │
├─────────────────────────────────────┤
│  4. EXAMPLES & PATTERNS             │  ← Middle-to-late
│     "Good: X, Bad: Y"               │
├─────────────────────────────────────┤
│  5. OUTPUT FORMAT                   │  ← Late
│     "Provide: 1. X, 2. Y, 3. Z"     │
├─────────────────────────────────────┤
│  6. SPECIFIC TASK & DATA            │  ← Back-loaded
│     "Now do this: {{data}}"         │
└─────────────────────────────────────┘
```

Follow this pattern for maximum effectiveness.
