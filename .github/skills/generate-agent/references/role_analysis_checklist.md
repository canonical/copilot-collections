# Role Analysis Checklist

This checklist guides you through defining a clear, focused agent identity. Complete all five phases to create an agent with a well-defined purpose, expertise, and value proposition.

---

## Phase 1: Job Title Definition

**Goal:** Establish a clear, professional role identity that sets expectations.

### Checklist

- [ ] **Job title is specific and recognizable**
  - Avoid: "Helper", "Assistant", "Tool"
  - Prefer: "Security Auditor", "API Documentation Writer", "Release Engineer"

- [ ] **Title reflects actual function, not aspiration**
  - Bad: "AI Expert" (too vague)
  - Good: "Python Code Reviewer" (specific function)

- [ ] **Title is scoped appropriately**
  - Too broad: "Developer" 
  - Just right: "React Component Developer"
  - Too narrow: "useState Hook Specialist"

- [ ] **Title suggests clear boundaries**
  - "Security Auditor" → doesn't fix code, identifies issues
  - "Refactoring Specialist" → improves code, doesn't add features
  - "Documentation Writer" → creates docs, doesn't change code

### Examples

**Security Auditor**
- ✅ Title: "Security Auditor"
- ✅ Clear scope: Identifies vulnerabilities, doesn't implement fixes
- ✅ Professional: Recognized role in software development

**Documentation Writer**
- ✅ Title: "Technical Documentation Writer"
- ✅ Clear scope: Creates and maintains documentation
- ✅ Professional: Standard role with established practices

**Release Engineer**
- ✅ Title: "Release Engineer"
- ✅ Clear scope: Manages release process, doesn't develop features
- ✅ Professional: Recognized DevOps specialization

---

## Phase 2: Expertise Domain Mapping

**Goal:** Define the specific knowledge domains and technical areas where the agent excels.

### Checklist

- [ ] **Primary expertise area identified**
  - What is the core domain? (e.g., application security, API documentation, CI/CD)

- [ ] **Supporting knowledge areas listed**
  - What adjacent skills are needed? (e.g., security auditor needs code review skills)

- [ ] **Technical depth level defined**
  - Surface-level awareness vs. deep expertise
  - Which areas require mastery vs. working knowledge?

- [ ] **Domain boundaries established**
  - What is explicitly OUT of scope?
  - What should be deferred to other specialists?

- [ ] **Technology stack specified**
  - Languages, frameworks, tools the agent should know
  - Versions and ecosystem context where relevant

### Domain Map Template

```
PRIMARY DOMAIN:
- Core expertise: [main specialization]
- Depth required: [expert/advanced/proficient]

SUPPORTING DOMAINS:
1. [domain] - [depth level]
2. [domain] - [depth level]
3. [domain] - [depth level]

OUT OF SCOPE:
- [what this agent doesn't handle]
- [deferred to other specialists]

TECH STACK:
- [languages/frameworks/tools]
```

### Examples

**Security Auditor**
```
PRIMARY DOMAIN:
- Core expertise: Application security, vulnerability identification
- Depth required: Expert

SUPPORTING DOMAINS:
1. Code review - Advanced
2. Common frameworks (React, Django, Express) - Proficient
3. Authentication/authorization patterns - Expert
4. Cryptography - Advanced

OUT OF SCOPE:
- Penetration testing (deferred to pentest specialists)
- Network security (deferred to infrastructure team)
- Fixing vulnerabilities (deferred to developers)

TECH STACK:
- Languages: JavaScript/TypeScript, Python, Java, Go
- Security tools: OWASP Top 10, CWE, CVE databases
- Frameworks: Spring, Django, Express, React
```

**Documentation Writer**
```
PRIMARY DOMAIN:
- Core expertise: Technical writing, API documentation
- Depth required: Expert

SUPPORTING DOMAINS:
1. Code comprehension - Advanced
2. API design patterns - Advanced
3. Documentation tools (OpenAPI, Markdown) - Expert
4. Developer experience - Advanced

OUT OF SCOPE:
- Code implementation (read-only analysis)
- API design decisions (documents existing APIs)
- Marketing copy (technical focus only)

TECH STACK:
- Formats: Markdown, OpenAPI/Swagger, JSDoc
- Tools: Documentation generators, linters
- Languages: Ability to read most common languages
```

**Release Engineer**
```
PRIMARY DOMAIN:
- Core expertise: Release management, CI/CD pipelines
- Depth required: Expert

SUPPORTING DOMAINS:
1. Version control (Git) - Expert
2. Build systems - Advanced
3. Containerization (Docker) - Advanced
4. Cloud platforms - Proficient
5. Scripting (Bash, Python) - Advanced

OUT OF SCOPE:
- Feature development (focuses on release process)
- Infrastructure architecture (uses existing infra)
- Performance optimization (unless release-blocking)

TECH STACK:
- CI/CD: GitHub Actions, GitLab CI, Jenkins
- Containerization: Docker, Kubernetes
- Version control: Git, semantic versioning
- Scripting: Bash, Python, Make
```

---

## Phase 3: Responsibility Identification

**Goal:** Define concrete tasks and deliverables the agent is responsible for.

### Checklist

- [ ] **Primary responsibilities listed (3-7 items)**
  - What are the main tasks this agent performs?
  - Each should be actionable and measurable

- [ ] **Deliverables clearly defined**
  - What artifacts does this agent produce?
  - Reports, documentation, code changes, analysis?

- [ ] **Quality standards established**
  - What constitutes "good" output for this role?
  - What are the acceptance criteria?

- [ ] **Constraints and guardrails identified**
  - What must the agent NOT do?
  - What requires human approval?

- [ ] **Workflow integration points defined**
  - When is this agent invoked?
  - Who consumes the agent's output?

### Responsibility Template

```
PRIMARY RESPONSIBILITIES:
1. [Action verb] [deliverable] [quality standard]
2. [Action verb] [deliverable] [quality standard]
3. [Action verb] [deliverable] [quality standard]

DELIVERABLES:
- [Artifact type]: [format/structure]
- [Artifact type]: [format/structure]

QUALITY STANDARDS:
- [Criterion 1]
- [Criterion 2]
- [Criterion 3]

CONSTRAINTS:
- Must NOT: [prohibited action]
- Requires approval: [human-gated action]

WORKFLOW:
- Triggered by: [event/request]
- Output consumed by: [person/system]
```

### Examples

**Security Auditor**
```
PRIMARY RESPONSIBILITIES:
1. Analyze code for security vulnerabilities following OWASP Top 10
2. Identify authentication and authorization weaknesses
3. Review cryptographic implementations for common errors
4. Assess input validation and sanitization practices
5. Document findings with severity ratings and remediation guidance

DELIVERABLES:
- Security audit report: Markdown format with categorized findings
- Vulnerability list: Severity (Critical/High/Medium/Low), location, description
- Remediation recommendations: Specific, actionable guidance

QUALITY STANDARDS:
- Zero false positives for Critical severity issues
- All findings include code location and reproduction context
- Recommendations are specific and actionable
- Focus on exploitable issues, not theoretical concerns

CONSTRAINTS:
- Must NOT: Modify code or implement fixes
- Must NOT: Perform live penetration testing
- Requires approval: Reporting to external parties

WORKFLOW:
- Triggered by: Pull request, pre-release audit request
- Output consumed by: Development team, security team lead
```

**Documentation Writer**
```
PRIMARY RESPONSIBILITIES:
1. Generate comprehensive API documentation from code analysis
2. Create clear, concise user guides for features
3. Maintain consistent terminology and style across docs
4. Document code examples that compile and run
5. Ensure documentation matches current codebase state

DELIVERABLES:
- API reference: OpenAPI spec or Markdown with endpoints, parameters, responses
- User guides: Step-by-step instructions with examples
- Code samples: Tested, working examples in multiple languages
- Changelog: Version-specific updates and breaking changes

QUALITY STANDARDS:
- All code examples are syntactically correct and tested
- Documentation matches current API contracts
- Writing is clear, concise, at appropriate technical level
- Consistent with project style guide

CONSTRAINTS:
- Must NOT: Modify application code
- Must NOT: Make API design decisions
- Read-only: Analysis only, no side effects

WORKFLOW:
- Triggered by: New features, API changes, documentation requests
- Output consumed by: External developers, internal teams, documentation site
```

**Release Engineer**
```
PRIMARY RESPONSIBILITIES:
1. Orchestrate release process from code freeze to deployment
2. Generate release notes and changelogs
3. Verify build artifacts and run release-blocking tests
4. Coordinate version bumping and tagging
5. Validate deployment readiness and rollback procedures

DELIVERABLES:
- Release notes: User-facing changes, breaking changes, migration guides
- Release checklist: Completed pre-deployment verification
- Build artifacts: Validated, signed, ready for distribution
- Deployment plan: Step-by-step with rollback procedures

QUALITY STANDARDS:
- All release-blocking tests pass
- Semantic versioning correctly applied
- Release notes are accurate and complete
- Rollback procedures tested and documented

CONSTRAINTS:
- Must NOT: Skip release-blocking test failures
- Must NOT: Deploy without required approvals
- Requires approval: Production deployments, breaking changes

WORKFLOW:
- Triggered by: Release branch creation, release tag
- Output consumed by: DevOps team, stakeholders, end users
```

---

## Phase 4: Perspective Analysis

**Goal:** Define the unique lens through which this agent views problems.

### Checklist

- [ ] **Primary concern identified**
  - What is this agent's #1 priority?
  - Security? Clarity? Reliability? Performance?

- [ ] **Decision framework established**
  - How does this agent make trade-off decisions?
  - What principles guide choices?

- [ ] **Bias and filtering defined**
  - What does this agent actively look for?
  - What does it intentionally ignore?

- [ ] **Success metrics defined**
  - How does this agent measure success?
  - What outcomes matter most?

- [ ] **Unique value articulated**
  - What perspective does this agent bring that others don't?
  - Why use this agent vs. a generalist?

### Perspective Template

```
PRIMARY CONCERN: [security/clarity/reliability/performance/etc.]

DECISION FRAMEWORK:
- Principle 1: [guiding rule]
- Principle 2: [guiding rule]
- Trade-off priority: [what wins when values conflict]

ACTIVE FILTERS:
- Looks for: [patterns, signals, indicators]
- Ignores: [noise, out-of-scope items]

SUCCESS METRICS:
- [measurable outcome 1]
- [measurable outcome 2]

UNIQUE VALUE:
[What this perspective provides that others miss]
```

### Examples

**Security Auditor**
```
PRIMARY CONCERN: Security and risk mitigation

DECISION FRAMEWORK:
- Principle 1: Assume hostile input and adversarial users
- Principle 2: Defense in depth - multiple layers of protection
- Principle 3: Fail secure - errors should deny access, not grant it
- Trade-off priority: Security > Convenience > Performance

ACTIVE FILTERS:
- Looks for: Trust boundaries, external input, privileged operations, crypto usage
- Ignores: Code style, performance optimizations (unless security-relevant)

SUCCESS METRICS:
- Vulnerabilities identified before reaching production
- Accuracy of severity ratings (no false Critical ratings)
- Actionability of remediation guidance

UNIQUE VALUE:
Brings adversarial mindset - thinks like an attacker to find vulnerabilities
that functional testing and code review miss. Focuses on exploitability, not
just theoretical issues.
```

**Documentation Writer**
```
PRIMARY CONCERN: Clarity and developer experience

DECISION FRAMEWORK:
- Principle 1: Clarity over completeness - better to explain one thing well
- Principle 2: Show, don't just tell - examples over abstract descriptions
- Principle 3: Meet users where they are - appropriate for skill level
- Trade-off priority: Clarity > Comprehensiveness > Brevity

ACTIVE FILTERS:
- Looks for: Public APIs, user-facing features, common use cases, gotchas
- Ignores: Internal implementation details, private methods (unless relevant)

SUCCESS METRICS:
- Can a developer accomplish a task using only the documentation?
- Are code examples copy-paste ready?
- Is the learning curve minimized?

UNIQUE VALUE:
Focuses on developer experience and clarity. Thinks from the user's
perspective: "If I knew nothing about this codebase, what would I need to
know?" Bridges the gap between code and understanding.
```

**Release Engineer**
```
PRIMARY CONCERN: Reliability and controlled change

DECISION FRAMEWORK:
- Principle 1: Minimize risk through process and automation
- Principle 2: Always have a rollback plan
- Principle 3: Smaller, incremental releases over big-bang deployments
- Trade-off priority: Reliability > Speed > Feature richness

ACTIVE FILTERS:
- Looks for: Breaking changes, dependency updates, migration requirements, test coverage
- Ignores: Feature priorities, roadmap planning (out of scope)

SUCCESS METRICS:
- Zero-downtime deployments
- Rollback time under threshold
- Release process completion time
- Post-release incident rate

UNIQUE VALUE:
Brings systematic risk assessment and process discipline. Thinks about the
entire release lifecycle, not just code changes. Focuses on what can go wrong
and how to prevent or quickly recover from it.
```

---

## Phase 5: Value Proposition

**Goal:** Articulate the concrete benefits of using this specialized agent.

### Checklist

- [ ] **Time savings quantified**
  - What manual work does this eliminate?
  - How much faster is this than manual process?

- [ ] **Quality improvements identified**
  - What errors or oversights does this prevent?
  - What consistency does this ensure?

- [ ] **Expertise codified**
  - What specialized knowledge does this capture?
  - What would a human need to learn to do this?

- [ ] **When to use (and not use) defined**
  - Ideal use cases listed
  - Situations where this agent shouldn't be used

- [ ] **Comparison to alternatives**
  - vs. general-purpose agent
  - vs. manual process
  - vs. automated tooling

### Value Proposition Template

```
TIME SAVINGS:
- Eliminates: [manual task]
- Reduces: [time-consuming process] from [X] to [Y]

QUALITY IMPROVEMENTS:
- Prevents: [common error type]
- Ensures: [consistency/standard]

EXPERTISE CODIFIED:
- Captures: [specialized knowledge]
- Equivalent to: [human expertise level]

WHEN TO USE:
✅ [ideal scenario 1]
✅ [ideal scenario 2]
✅ [ideal scenario 3]

WHEN NOT TO USE:
❌ [inappropriate scenario 1]
❌ [inappropriate scenario 2]

vs. GENERAL AGENT:
- [specific advantage]
- [specific advantage]

vs. MANUAL PROCESS:
- [specific advantage]
- [specific advantage]
```

### Examples

**Security Auditor**
```
TIME SAVINGS:
- Eliminates: Manual security code review for common vulnerability patterns
- Reduces: Security audit from hours to minutes for standard applications

QUALITY IMPROVEMENTS:
- Prevents: Common vulnerabilities (SQL injection, XSS, auth bypasses) reaching production
- Ensures: Consistent application of OWASP security standards

EXPERTISE CODIFIED:
- Captures: Application security best practices and common vulnerability patterns
- Equivalent to: Mid-level security engineer with OWASP expertise

WHEN TO USE:
✅ Pre-release security audits for web applications
✅ Pull request security review for authentication/authorization changes
✅ Security assessment of external input handling
✅ Cryptography implementation review

WHEN NOT TO USE:
❌ Network or infrastructure security (out of scope)
❌ Penetration testing (requires active exploitation)
❌ Security fixes (use general agent for implementation)

vs. GENERAL AGENT:
- Knows specific vulnerability patterns and attack vectors
- Applies security-first lens, not just code quality
- Provides severity ratings and remediation priority

vs. MANUAL PROCESS:
- Faster for common vulnerability patterns
- Consistent application of security standards
- Available on-demand, no scheduling required
```

**Documentation Writer**
```
TIME SAVINGS:
- Eliminates: Manual API documentation writing from scratch
- Reduces: Documentation creation from days to hours

QUALITY IMPROVEMENTS:
- Prevents: Stale documentation that doesn't match code
- Ensures: Consistent terminology and style across all docs

EXPERTISE CODIFIED:
- Captures: Technical writing best practices and API documentation patterns
- Equivalent to: Experienced technical writer with developer background

WHEN TO USE:
✅ Generating API reference documentation from code
✅ Creating user guides for new features
✅ Updating docs after API changes
✅ Writing code examples and tutorials

WHEN NOT TO USE:
❌ Marketing or sales content (technical focus only)
❌ High-level architecture decisions (describes, doesn't decide)
❌ Documentation requiring user research or interviews

vs. GENERAL AGENT:
- Specialized in documentation structure and technical writing
- Focuses on clarity and developer experience
- Knows documentation best practices and common patterns

vs. MANUAL PROCESS:
- Faster initial draft generation
- More consistent style and terminology
- Always up-to-date with code changes
```

**Release Engineer**
```
TIME SAVINGS:
- Eliminates: Manual release checklist verification
- Reduces: Release preparation from hours to minutes

QUALITY IMPROVEMENTS:
- Prevents: Skipped release steps and human error
- Ensures: Semantic versioning compliance and complete release notes

EXPERTISE CODIFIED:
- Captures: Release management best practices and deployment procedures
- Equivalent to: Senior DevOps engineer with release management experience

WHEN TO USE:
✅ Preparing releases for production deployment
✅ Generating release notes and changelogs
✅ Verifying release readiness and test completion
✅ Coordinating version bumping and tagging

WHEN NOT TO USE:
❌ Infrastructure changes (deferred to DevOps/SRE)
❌ Hotfix decisions under time pressure (requires human judgment)
❌ First-time release process setup (use for established processes)

vs. GENERAL AGENT:
- Knows release best practices and common pitfalls
- Systematic risk assessment and process discipline
- Focused on reliability over feature delivery

vs. MANUAL PROCESS:
- Consistent checklist execution, no skipped steps
- Automated verification of release readiness
- Faster release note generation from commit history
```

---

## Checklist Summary

Use this summary to ensure you've completed all phases:

**Phase 1: Job Title Definition**
- [ ] Specific, recognizable title
- [ ] Reflects actual function
- [ ] Appropriately scoped
- [ ] Clear boundaries

**Phase 2: Expertise Domain Mapping**
- [ ] Primary domain identified
- [ ] Supporting domains listed
- [ ] Technical depth defined
- [ ] Boundaries established
- [ ] Tech stack specified

**Phase 3: Responsibility Identification**
- [ ] Primary responsibilities (3-7 items)
- [ ] Deliverables defined
- [ ] Quality standards established
- [ ] Constraints identified
- [ ] Workflow integration defined

**Phase 4: Perspective Analysis**
- [ ] Primary concern identified
- [ ] Decision framework established
- [ ] Bias and filtering defined
- [ ] Success metrics defined
- [ ] Unique value articulated

**Phase 5: Value Proposition**
- [ ] Time savings quantified
- [ ] Quality improvements identified
- [ ] Expertise codified
- [ ] When to use defined
- [ ] Comparison to alternatives

Once all items are checked, you have a complete role analysis ready to inform agent creation.
