---
name: generate-agent
description: Generates Custom Agent files (.github/agents/*.agent.md) with persona-based configurations, specialized tool sets, and role-specific cognitive architectures. Use when the user requests a specialized role or perspective (Security Auditor, Documentation Writer, Release Engineer, etc.). Creates agents with defined identity, constrained tools, and thinking processes aligned to their role. Not for general capabilities—use generate-agent-skills for those.
---

# Custom Agent Generator (Persona Factory)

## Overview

This skill generates Custom Agent files that act as **persistent specialized roles** with:
- **Identity:** Job title, expertise domain, perspective
- **Tool Set:** Constrained capabilities (read-only by default, write when needed)
- **Cognitive Architecture:** Role-specific thinking process

**Key distinction:**
- **Custom Agents** (this skill) = *Who* (role, perspective, persona)
- **Agent Skills** (generate-agent-skills) = *What* (capability, workflow, task)

**Example agents:**
- Security Auditor (reads code, thinks like attacker, reports vulnerabilities)
- Documentation Writer (writes docs, enforces style, maintains consistency)
- Release Engineer (manages releases, validates readiness, updates changelogs)
- Code Reviewer (analyzes PRs, checks standards, suggests improvements)

---

## Workflow

### Step 1: Intent Validation

Confirm the user wants a **Custom Agent** (not a skill or instruction).

**Decision tree:**

- **User wants a specialized role/perspective?** → Continue to Step 2
  - Examples: "Security Auditor", "Documentation Writer", "Release Manager"
- **User wants a repeatable workflow/task?**
  - → STOP. Redirect to `generate-agent-skills` instead
  - Explain: Skills are for capabilities (generate tests, refactor code)
- **User wants file/directory-specific rules?**
  - → STOP. Redirect to `generate-path-instructions` instead
  - Explain: Path instructions are for scoped rules
- **User wants global repository rules?**
  - → STOP. Redirect to `generate-repo-instructions` instead
  - Explain: Repo instructions are for project-wide standards

**Proceed only if creating a role-based agent.**

---

### Step 2: Role Analysis

**Goal:** Define the agent's identity, expertise, and perspective.

**Load the role analysis checklist:**
```bash
cat references/role_analysis_checklist.md
```

Work through the checklist to define:
1. **Job Title** - What is this agent's role?
2. **Expertise Domain** - What does it specialize in?
3. **Primary Responsibilities** - What does it do?
4. **Perspective** - How does it think differently?
5. **Value Proposition** - Why use this agent vs default?

**Critical questions:**
- What makes this role distinct from the default agent?
- What unique perspective or constraints does this role have?
- What decisions require this role's specialized judgment?

**Example outputs:**

**Security Auditor:**
- Job Title: Security Auditor
- Expertise: Application security, vulnerability detection, threat modeling
- Responsibilities: Find security flaws, suggest mitigations, prevent vulnerabilities
- Perspective: Think like an attacker first, assume breach mindset
- Value: Finds security issues developers miss

**Documentation Writer:**
- Job Title: Documentation Writer
- Expertise: Technical writing, information architecture, user experience
- Responsibilities: Create/maintain docs, enforce style, ensure clarity
- Perspective: Think from user's perspective, optimize for understanding
- Value: Produces consistent, high-quality documentation

---

### Step 3: Tool Selection

**Goal:** Determine which tools the agent needs (read/write/search).

**Load the tool selection guide:**
```bash
cat references/tool_selection_guide.md
```

**Default stance: Read-only**
- Agents should observe and advise by default
- Only grant write permissions when explicitly needed

**Decision framework:**

| Agent Type | Typical Tools | Rationale |
|------------|---------------|-----------|
| **Auditor/Reviewer** | Read + Grep + View | Analyzes, doesn't modify |
| **Writer/Editor** | Read + Write + Edit | Creates/updates content |
| **Analyst** | Read + Grep + Search | Discovers patterns |
| **Maintainer** | Read + Write + Bash | Manages files/configs |

**Constraint checking:**
- Does this role need to CREATE files? → Needs `create`
- Does this role need to MODIFY files? → Needs `edit`
- Does this role need to RUN commands? → Needs `bash`
- Does this role need to SEARCH semantically? → Needs semantic search

**Output:** List of tools with justification

**Example:**

**Security Auditor:** `view`, `grep`, `bash` (read-only analysis + command scanning)
- Rationale: Reads code, searches patterns, runs static analysis tools
- NO write tools: Reports findings, doesn't fix (stays in audit role)

**Documentation Writer:** `view`, `grep`, `create`, `edit`
- Rationale: Reads existing docs, creates new docs, updates content
- YES write tools: Primary job is creating/maintaining documentation

---

### Step 4: Cognitive Architecture Design

**Goal:** Define how this agent thinks (role-specific reasoning process).

**Load cognitive architecture patterns:**
```bash
cat references/cognitive_architecture_patterns.md
```

Design the `<thinking_process>` based on role:

**Components:**
1. **Initial Assessment** - How does agent approach a new request?
2. **Domain-Specific Analysis** - What does agent look for first?
3. **Constraint Application** - What rules/principles guide thinking?
4. **Decision Criteria** - How does agent prioritize/evaluate?
5. **Output Formulation** - How does agent structure responses?

**Example thinking processes:**

**Security Auditor:**
```xml
<thinking_process>
1. **Threat Model First:** What could go wrong? What's the attack surface?
2. **Assume Breach Mindset:** If an attacker had access, what could they do?
3. **Check Common Vulnerabilities:** SQL injection, XSS, auth bypass, secrets exposure
4. **Trace Data Flow:** Where does user input flow? Is it sanitized?
5. **Prioritize by Impact:** Critical > High > Medium > Low severity
6. **Report with Evidence:** Include code snippets, line numbers, exploitation scenarios
</thinking_process>
```

**Documentation Writer:**
```xml
<thinking_process>
1. **Audience First:** Who will read this? What's their knowledge level?
2. **Information Architecture:** How does this fit in existing docs structure?
3. **Clarity over Cleverness:** Simple, direct language. Avoid jargon.
4. **Show, Don't Tell:** Include examples, code snippets, screenshots
5. **Style Consistency:** Follow established voice, tone, formatting
6. **Completeness Check:** Did I answer what/why/how? Include edge cases?
</thinking_process>
```

---

### Step 5: Template Population

**Goal:** Generate the agent file using the template.

**Load agent template:**
```bash
cat assets/agent_template.md
```

**Populate these sections:**

1. **YAML Frontmatter:**
   - `name`: kebab-case role name (e.g., `security-auditor`)
   - `description`: One-sentence summary of role and purpose
   - `tools`: Array of tool names (validated in Step 3)

2. **Agent Identity:**
   - Role title and expertise domain
   - What makes this agent special
   - When to use this agent vs default

3. **Thinking Process:**
   - Role-specific `<thinking_process>` from Step 4
   - Structured with XML delimiters (prevents system prompt leakage)

4. **Instructions:**
   - Role-specific guidelines
   - Constraints and principles
   - Output format expectations

5. **Examples (Optional but Recommended):**
   - Show agent in action
   - Demonstrate role-specific reasoning
   - Illustrate unique value

**File naming convention:**
- `.github/agents/{{role-name}}.agent.md`
- Examples: `security-auditor.agent.md`, `doc-writer.agent.md`, `release-engineer.agent.md`
- Use kebab-case, be descriptive

**Critical: XML Delimiters**
- Use `<thinking_process>`, `<examples>`, `<constraints>` tags
- Prevents agent instructions from leaking into system prompt
- Maintains clean separation of agent config vs runtime behavior

---

### Step 6: Validation & Testing

**Validate the generated agent file:**

```bash
# 1. Validate YAML frontmatter and structure
python3 .github/skills/generate-agent-skills/scripts/validate_skill.py --path .github/agents/

# 2. Check XML delimiter syntax
grep -E "<thinking_process>|</thinking_process>" .github/agents/{{agent-name}}.agent.md

# 3. Verify tool list matches allowed tools
# Allowed: view, edit, create, grep, glob, bash, task, etc.
```

**Final checklist:**
- [ ] YAML frontmatter is valid (name, description, tools)
- [ ] Tools list is minimal (read-only unless justified)
- [ ] Thinking process is role-specific (not generic)
- [ ] XML delimiters are properly closed
- [ ] Agent identity clearly explains unique value
- [ ] Examples demonstrate role-specific behavior (if included)
- [ ] No secrets or sensitive data

**Output to user:**
```
✅ Created: .github/agents/{{agent-name}}.agent.md
🎭 Role: {{Job Title}}
🛠️ Tools: {{tool1, tool2, tool3}}
💡 Unique Value: {{one-sentence value prop}}

📖 To use: Reference this agent in your request or switch to it in VS Code
```

---

### Step 7: Usage Guidance (Optional)

**Help the user understand how to use their new agent:**

**Activation methods:**
1. **Explicit request:** "Use the security-auditor agent to review this code"
2. **VS Code switcher:** Select agent from dropdown
3. **Auto-matching:** Agent activates based on task keywords (if configured)

**Best practices:**
- Use for tasks that benefit from the role's perspective
- Don't overuse—default agent is fine for general tasks
- Combine with skills for powerful workflows (e.g., Security Auditor + generate-tests)

---

## Resources

### references/role_analysis_checklist.md
Guides LLM through defining agent identity, expertise, and perspective.

### references/tool_selection_guide.md
Decision framework for choosing agent tools with security constraints.

### references/cognitive_architecture_patterns.md
Examples of role-specific thinking processes for common agent types.

### assets/agent_template.md
Complete agent file template with XML delimiters and structure.

---

## Examples of Common Agents

### Auditor/Reviewer Agents
- Security Auditor (finds vulnerabilities)
- Code Reviewer (enforces standards)
- Accessibility Auditor (checks WCAG compliance)
- **Tools:** Read-only (view, grep, bash for analysis)

### Writer/Editor Agents
- Documentation Writer (creates/maintains docs)
- Release Notes Generator (writes changelogs)
- API Documentation Specialist (documents APIs)
- **Tools:** Read + Write (view, create, edit)

### Analyst Agents
- Performance Analyst (finds bottlenecks)
- Dependency Auditor (analyzes deps)
- Tech Debt Analyst (identifies tech debt)
- **Tools:** Read + Search (view, grep, semantic search)

### Maintainer Agents
- Release Engineer (manages releases)
- Configuration Manager (maintains configs)
- Migration Specialist (executes migrations)
- **Tools:** Read + Write + Execute (full toolset)

---

## Anti-Patterns

### ❌ DON'T:
- Create agents for capabilities (use skills instead)
- Grant unnecessary write permissions
- Use generic thinking processes
- Mix multiple roles in one agent
- Create agents without clear unique value
- Forget XML delimiters (causes prompt leakage)

### ✅ DO:
- Create agents for distinct perspectives/roles
- Default to read-only tools
- Design role-specific thinking processes
- Include concrete examples
- Explain unique value vs default agent
- Use XML delimiters consistently
