# Tool Selection Guide

This guide helps you choose the right tools for your agent based on security principles, functional requirements, and role responsibilities.

---

## Core Principle: Least Privilege

**Default stance: Read-only unless write access is essential to the role.**

- Start with minimal tools
- Add tools only when justified by core responsibilities
- Prefer analysis over modification
- When in doubt, leave it out

---

## Tool Categories

### 1. Read Tools (Low Risk)

**Purpose:** Gather information, analyze existing state

```
view          - Read file contents
list          - List directory contents  
grep          - Search file contents
glob          - Find files by pattern
bash (read)   - Execute read-only commands (git log, ls, cat)
```

**Risk level:** Low  
**Justification needed:** Minimal - most agents need these

**Example agents:**
- Security Auditor: All read tools
- Documentation Writer: All read tools
- Code Reviewer: All read tools

---

### 2. Search Tools (Low Risk)

**Purpose:** Navigate and discover information

```
grep          - Content search
glob          - File pattern matching
task/explore  - Code exploration sub-agent
```

**Risk level:** Low  
**Justification needed:** Minimal

**Example agents:**
- Documentation Writer: Needs to find related code
- Security Auditor: Needs to find security-relevant code patterns
- Release Engineer: Needs to find changed files

---

### 3. Write Tools (Medium Risk)

**Purpose:** Modify files and create content

```
create        - Create new files
edit          - Modify existing files
bash (write)  - File manipulation commands
```

**Risk level:** Medium  
**Justification needed:** Must be core to agent's role

**Appropriate for:**
- ✅ Documentation Writer (creates/updates docs)
- ✅ Code Refactoring Agent (modifies code)
- ❌ Security Auditor (analyzes, doesn't fix)
- ❌ Code Reviewer (reviews, doesn't modify)

**Constraints:**
- Specify allowed file patterns (e.g., only `docs/**/*.md`)
- Document what should NOT be modified
- Consider requiring confirmation for destructive changes

---

### 4. Execute Tools (High Risk)

**Purpose:** Run commands, install packages, modify system state

```
bash          - Arbitrary command execution
npm/pip       - Package installation
git (write)   - Commit, push, branch operations
```

**Risk level:** High  
**Justification needed:** Critical to core function

**Appropriate for:**
- ✅ Release Engineer (needs git tag, version bump)
- ✅ Dependency Updater (needs package manager)
- ❌ Documentation Writer (no execution needed)
- ❌ Security Auditor (analysis only)

**Constraints:**
- List allowed commands explicitly
- Prohibit destructive operations (rm -rf, git push --force)
- Require confirmation for state changes

---

## Decision Tree

```
START: What is the agent's core function?

├─ Analysis/Review only
│  └─ READ TOOLS ONLY
│     ├─ view, list, grep, glob
│     └─ bash (read-only: ls, cat, git log, git diff)
│
├─ Content Creation (docs, configs)
│  └─ READ + WRITE (limited scope)
│     ├─ All read tools
│     ├─ create, edit (docs/** only)
│     └─ NO bash execution
│
├─ Code Modification
│  └─ READ + WRITE (source code)
│     ├─ All read tools
│     ├─ create, edit (src/** only)
│     ├─ bash (linting, testing)
│     └─ NO package installation without approval
│
└─ Release/Deployment
   └─ READ + WRITE + EXECUTE
      ├─ All read tools
      ├─ create, edit (version files, changelogs)
      ├─ bash (git tag, version bump)
      └─ CONSTRAINTS: no force push, require approval
```

---

## Tool Justification Framework

For each tool, answer:

### 1. Is this tool necessary for core responsibilities?

**Ask:**
- Can the agent fulfill its primary role without this tool?
- Is this a "nice to have" or "must have"?

**Example:**
- Security Auditor + `edit` tool: ❌ Not necessary (analyzes, doesn't fix)
- Documentation Writer + `edit` tool: ✅ Necessary (must update docs)

### 2. What is the blast radius?

**Ask:**
- What damage could occur if this tool is misused?
- What files/systems could be affected?

**Example:**
- `view` tool: Low blast radius (read-only)
- `bash` with write access: High blast radius (arbitrary commands)

### 3. Can we constrain this tool?

**Ask:**
- Can we limit to specific file patterns?
- Can we prohibit certain operations?
- Can we require human confirmation?

**Example:**
```yaml
# Good: Constrained write access
constraints:
  - "Only modify files matching docs/**/*.md"
  - "Never modify source code in src/**"
  - "Require confirmation before deleting files"

# Bad: Unconstrained access
tools:
  - bash  # No limitations specified
```

### 4. Is there a safer alternative?

**Ask:**
- Can we achieve the same goal with lower-risk tools?
- Can we use a sub-agent instead?

**Example:**
- Instead of: `bash` for running tests
- Consider: `task` sub-agent (isolated execution context)

---

## Common Agent Types with Typical Tool Sets

### Security Auditor

```yaml
tools:
  # Read-only analysis
  - view
  - list  
  - grep
  - glob
  
  # Read-only bash commands
  - bash  # git log, git diff, git show

constraints:
  - "Read-only access - no file modifications"
  - "No command execution beyond git read operations"
  
justification:
  - "Analysis-only role requires no write access"
  - "Must inspect code but not modify it"
```

### Documentation Writer

```yaml
tools:
  # Read tools for code analysis
  - view
  - list
  - grep
  - glob
  
  # Write tools for documentation
  - create  # New documentation files
  - edit    # Update existing docs
  
constraints:
  - "File modifications limited to: docs/**, README.md, *.mdx"
  - "No source code modifications (src/**, lib/**)"
  - "No command execution"
  
justification:
  - "Must read code to document it"
  - "Must write/update documentation files"
  - "No need for code modification or execution"
```

### Code Reviewer

```yaml
tools:
  # Read-only analysis
  - view
  - grep
  - glob
  - bash  # git diff, git log

constraints:
  - "Read-only access - review only, no modifications"
  - "Can analyze diffs and history"
  - "Cannot modify code or commit changes"
  
justification:
  - "Review role is inherently read-only"
  - "Must inspect changes but not alter them"
```

### Refactoring Specialist

```yaml
tools:
  # Read tools
  - view
  - grep
  - glob
  
  # Write tools for code changes
  - edit    # Modify source files
  
  # Execution for verification
  - bash    # Run linters, tests
  
constraints:
  - "Code modifications only - no doc or config changes without approval"
  - "Must run tests after modifications"
  - "No package installation without approval"
  
justification:
  - "Core function is code modification"
  - "Must verify refactoring doesn't break functionality"
  - "Execution limited to verification commands"
```

### Release Engineer

```yaml
tools:
  # Read tools
  - view
  - list
  - grep
  - glob
  
  # Write tools for release artifacts
  - create  # CHANGELOG, release notes
  - edit    # Version files, package.json
  
  # Execution for release process
  - bash    # git tag, version bumping, build commands
  
constraints:
  - "Git operations: tag creation only, no force push"
  - "Version file modifications: package.json, version.txt, CHANGELOG.md"
  - "Build commands: approved release scripts only"
  - "Require approval: Production deployments, version bumps"
  
justification:
  - "Release process requires version updates and tagging"
  - "Must generate release artifacts (notes, changelogs)"
  - "Execution necessary for build verification and git operations"
```

### Test Generator

```yaml
tools:
  # Read tools for code analysis
  - view
  - grep
  - glob
  
  # Write tools for test creation
  - create  # New test files
  - edit    # Update existing tests
  
  # Execution for test validation
  - bash    # Run tests to verify they work
  
constraints:
  - "File creation limited to: **/*.test.*, **/*.spec.*"
  - "No modification of source code under test"
  - "Test execution only - no deployment or release commands"
  
justification:
  - "Must create test files (core function)"
  - "Must run tests to validate correctness"
  - "No need to modify source code"
```

---

## Anti-Patterns

### ❌ Over-Permissioning

**Problem:** Granting tools "just in case"

```yaml
# BAD: Security Auditor with edit access
tools:
  - view
  - edit    # ❌ Why does an auditor need to edit files?
  - bash
```

**Fix:** Only grant tools needed for core responsibilities

```yaml
# GOOD: Security Auditor - read only
tools:
  - view
  - grep
  - glob
```

---

### ❌ Unconstrained Execution

**Problem:** Bash access without constraints

```yaml
# BAD: No constraints
tools:
  - bash  # Can run ANY command
```

**Fix:** Document constraints and prohibited operations

```yaml
# GOOD: Explicit constraints
tools:
  - bash

constraints:
  - "Allowed: git log, git diff, git show, ls, cat"
  - "Prohibited: rm, git push, package installation"
  - "Read-only operations only"
```

---

### ❌ Undefined Scope

**Problem:** Write access without scope boundaries

```yaml
# BAD: Can modify anything
tools:
  - edit
```

**Fix:** Define explicit file patterns

```yaml
# GOOD: Limited to documentation
tools:
  - edit

constraints:
  - "Modifications limited to: docs/**/*.md, README.md"
  - "Cannot modify: src/**, package.json, .github/**"
```

---

### ❌ Role Confusion

**Problem:** Agent can both review and modify

```yaml
# BAD: Code Reviewer that modifies code
name: Code Reviewer
tools:
  - view
  - edit  # ❌ Reviewers shouldn't modify code
```

**Fix:** Separate concerns - review vs. modification

```yaml
# GOOD: Pure review agent
name: Code Reviewer
tools:
  - view
  - grep
  - glob
# No edit tool - reviewing only
```

---

## Tool Selection Checklist

Before adding a tool to your agent:

- [ ] **Is this tool necessary for core responsibilities?**
  - Can the agent function without it?
  
- [ ] **What is the risk level?**
  - Read-only: Low risk
  - Write: Medium risk  
  - Execute: High risk
  
- [ ] **Have we defined constraints?**
  - File patterns for write access
  - Allowed/prohibited commands for bash
  - Approval requirements for destructive operations
  
- [ ] **Is there a safer alternative?**
  - Sub-agent instead of direct tool access?
  - More specific tool instead of bash?
  
- [ ] **Does this align with the agent's role?**
  - Auditor: Analyzes, doesn't fix
  - Writer: Creates content, doesn't execute
  - Reviewer: Reviews, doesn't modify
  
- [ ] **Have we documented the justification?**
  - Why this tool is needed
  - What it enables
  - Why alternatives aren't sufficient

---

## Summary

**Security-First Approach:**
1. Start with read-only tools
2. Add write access only when essential
3. Constrain execution capabilities
4. Document all tool justifications

**Tool Categories by Risk:**
- **Low risk:** view, list, grep, glob
- **Medium risk:** create, edit (with constraints)
- **High risk:** bash execution, package management

**Decision Framework:**
- Is it necessary? (Core responsibility)
- What's the blast radius? (Risk assessment)
- Can we constrain it? (Mitigation)
- Is there a safer alternative? (Optimization)

**Remember:** Every tool is a potential security surface. Grant access intentionally, not speculatively.
