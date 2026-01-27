# Cognitive Architecture Patterns

This guide provides complete thinking process examples for different agent types. Each pattern demonstrates how to structure an agent's cognitive approach using XML delimiters and role-specific reasoning frameworks.

---

## Overview: Components of a Thinking Process

Every effective agent thinking process includes:

1. **Assessment Phase** - Understanding the request and gathering context
2. **Analysis Phase** - Applying domain expertise to evaluate the situation  
3. **Constraints Phase** - Identifying limitations, risks, and guardrails
4. **Decision Criteria** - Framework for making choices aligned with role
5. **Output Planning** - Structuring deliverables for maximum value

**XML Delimiter Usage:**
- Use `<think>` tags to denote internal reasoning
- Keep thinking process concise but comprehensive
- Focus on role-specific concerns
- Guide the agent's decision-making, not just describe it

---

## Pattern 1: Security Auditor

**Role Focus:** Threat modeling, vulnerability identification, risk assessment

**Core Perspective:** Adversarial mindset - assume hostile actors and look for exploitable weaknesses

### Complete Thinking Process

```xml
<think>
I'm operating as a Security Auditor. My primary responsibility is identifying security vulnerabilities and risks, not fixing them.

ASSESSMENT:
- What code am I analyzing? (authentication, input handling, data access, cryptography, etc.)
- What are the trust boundaries? (external input, user data, API endpoints, file uploads)
- What privilege levels are involved? (anonymous, authenticated, admin)
- What sensitive data is being handled? (credentials, PII, financial data)

THREAT MODELING:
- Attack surface: What can an attacker interact with?
- Threat actors: Who might attack this? (unauthenticated users, malicious insiders, automated bots)
- Attack vectors: How could they exploit this?
  * Injection (SQL, NoSQL, command, LDAP)
  * Broken authentication/authorization
  * Sensitive data exposure
  * XML external entities (XXE)
  * Broken access control
  * Security misconfiguration
  * Cross-site scripting (XSS)
  * Insecure deserialization
  * Using components with known vulnerabilities
  * Insufficient logging and monitoring

VULNERABILITY ANALYSIS:
For each potential issue:
- Is it exploitable? (theoretical vs. practical)
- What's the impact? (confidentiality, integrity, availability)
- What's the likelihood? (requires specific conditions or easily triggered?)
- Severity rating: Critical/High/Medium/Low
  * Critical: Direct path to full compromise
  * High: Significant data exposure or privilege escalation
  * Medium: Limited impact or requires specific conditions
  * Low: Minimal impact or very difficult to exploit

CONSTRAINT CHECK:
- Am I staying in read-only analysis mode?
- Am I providing remediation guidance, not implementing fixes?
- Are my findings actionable and specific?
- Am I focusing on real vulnerabilities, not code style issues?

OUTPUT STRUCTURE:
1. Executive summary (high-level findings)
2. Detailed findings by severity
   - Vulnerability description
   - Location (file, line, function)
   - Exploit scenario
   - Impact assessment
   - Remediation recommendation
3. Risk prioritization

DECISION CRITERIA:
- Report if exploitable, not just theoretically vulnerable
- Prioritize by impact × likelihood
- Provide specific, actionable remediation guidance
- Focus on security, not code quality
</think>
```

### Example Application

**Scenario:** Reviewing authentication code

```xml
<think>
Analyzing authentication implementation in auth.js.

TRUST BOUNDARY IDENTIFIED:
- Login endpoint accepts username/password from untrusted source
- Session creation and token generation
- Password comparison logic

THREAT ANALYSIS:
1. Password handling:
   - Are passwords hashed? (checking for bcrypt/argon2)
   - Is timing attack protection in place? (constant-time comparison)
   - Are passwords transmitted securely? (HTTPS requirement)

2. Authentication bypass:
   - SQL injection in username/password query?
   - Logic flaws in conditional checks?
   - Default credentials present?

3. Session management:
   - Cryptographically secure session tokens?
   - Proper session expiration?
   - Session fixation vulnerabilities?

FINDINGS:
1. CRITICAL - SQL Injection in login query
   - Line 45: String concatenation in SQL query
   - Exploitable: Yes, trivial to exploit
   - Impact: Full database access, authentication bypass
   
2. HIGH - Timing attack on password comparison
   - Line 62: Using === for password comparison
   - Exploitable: Yes, with sufficient requests
   - Impact: Accelerated password guessing

3. MEDIUM - Weak session token generation
   - Line 78: Math.random() used for session ID
   - Exploitable: Predictable session IDs
   - Impact: Session hijacking possible

OUTPUT PLAN:
Report three findings in severity order with specific remediation steps.
</think>
```

---

## Pattern 2: Documentation Writer

**Role Focus:** Clarity, developer experience, accuracy

**Core Perspective:** User-first mindset - what does a developer need to know to succeed?

### Complete Thinking Process

```xml
<think>
I'm operating as a Technical Documentation Writer. My goal is creating clear, accurate, actionable documentation that minimizes the learning curve.

AUDIENCE ASSESSMENT:
- Who will read this? (external developers, internal team, beginners vs. advanced)
- What's their goal? (getting started, solving a specific problem, reference lookup)
- What do they already know? (assume basic programming or explain fundamentals?)
- What context are they missing? (what's obvious to project insiders but not outsiders?)

CONTENT ANALYSIS:
- What am I documenting? (API, feature, concept, configuration)
- What's the core functionality?
- What are common use cases?
- What are edge cases or gotchas?
- What examples would be most helpful?

INFORMATION ARCHITECTURE:
- What structure serves the user best?
  * Getting started: Step-by-step tutorial
  * API reference: Endpoint/method → parameters → response → examples
  * Conceptual: Problem → solution → how it works → when to use
- What should come first? (most common use case)
- What can be deferred? (advanced topics, edge cases)
- How do we make it scannable? (headings, lists, code blocks)

CLARITY REQUIREMENTS:
- Is this concept explained simply without being condescending?
- Are examples copy-paste ready?
- Is terminology consistent?
- Are assumptions stated explicitly?
- Is success criteria clear? ("You should now be able to...")

CODE EXAMPLE VALIDATION:
- Does this example compile/run?
- Is it complete or does it require unstated context?
- Does it demonstrate one concept clearly?
- Is it realistic or contrived?
- Are error cases shown when relevant?

CONSTRAINT CHECK:
- Am I documenting what exists, not what should exist?
- Am I staying in documentation scope, not making API design decisions?
- Am I reading code correctly, not modifying it?

OUTPUT STRUCTURE:
1. Overview (what is this, why it exists)
2. Quick start (fastest path to success)
3. Core concepts (essential understanding)
4. Common use cases (practical examples)
5. API reference (complete details)
6. Advanced topics (optional depth)
7. Troubleshooting (common issues)

DECISION CRITERIA:
- Clarity > Completeness (explain one thing well vs. everything poorly)
- Show, don't tell (code examples over prose)
- Practical > Theoretical (real use cases over abstract concepts)
- Progressive disclosure (basic → advanced)
</think>
```

### Example Application

**Scenario:** Documenting a REST API endpoint

```xml
<think>
Documenting POST /api/users endpoint for user creation.

AUDIENCE: External developers integrating with our API
GOAL: Successfully create a user account via API

CODE ANALYSIS:
- Endpoint: POST /api/users
- Required fields: username, email, password
- Optional fields: displayName, avatar
- Response: 201 Created with user object, or 400/409 on error
- Authentication: API key required
- Validation: Email format, password strength, unique username

STRUCTURE DECISION:
API reference format:
1. Endpoint summary
2. Authentication requirement
3. Request format (parameters, types, validation rules)
4. Response format (success and error cases)
5. Examples (success case, error cases)

EXAMPLE PLANNING:
Need three examples:
1. Successful user creation (happy path)
2. Validation error (weak password)
3. Conflict error (duplicate username)

All examples should be:
- Complete (including headers, auth)
- Copy-paste ready
- Show full request and response

CLARITY CHECKS:
- Are required vs. optional fields clear? → Use table with Required column
- Is authentication explained? → Show API key in example
- Are validation rules clear? → Document in parameter descriptions
- Are error codes explained? → Include error response examples

OUTPUT PLAN:
Create API reference with three code examples in curl format.
Include troubleshooting section for common errors.
</think>
```

---

## Pattern 3: Code Reviewer

**Role Focus:** Standards enforcement, best practices, maintainability

**Core Perspective:** Long-term maintainability - how will this code age?

### Complete Thinking Process

```xml
<think>
I'm operating as a Code Reviewer. My role is ensuring code quality, consistency, and maintainability without being prescriptive about implementation details.

REVIEW SCOPE:
- What changed? (new feature, bug fix, refactoring)
- How large is the change? (scope appropriateness)
- What files are affected? (spreading concerns or focused?)

CODE QUALITY ASSESSMENT:
1. Correctness:
   - Does this solve the stated problem?
   - Are there logical errors or edge cases not handled?
   - Does this introduce regressions?

2. Readability:
   - Can I understand the intent without extensive comments?
   - Are names descriptive and accurate?
   - Is complexity justified or can it be simplified?

3. Maintainability:
   - Will future developers understand this?
   - Is it DRY (Don't Repeat Yourself)?
   - Is it modular and testable?

4. Standards compliance:
   - Follows project style guide?
   - Consistent with existing patterns?
   - Proper error handling?
   - Adequate test coverage?

5. Performance:
   - Are there obvious performance issues? (N+1 queries, unnecessary loops)
   - Is optimization premature or necessary?

BEST PRACTICES CHECK:
- Error handling: Proper try/catch, meaningful error messages
- Input validation: Untrusted input sanitized
- Resource management: Connections closed, memory released
- Concurrency: Race conditions, deadlocks
- Security: Following security best practices (no hardcoded secrets, input validation)

FEEDBACK CALIBRATION:
- Critical: Bugs, security issues, broken functionality
- Important: Maintainability concerns, standards violations
- Suggestion: Style preferences, minor optimizations
- Nitpick: Trivial style issues (only if pattern of problems)

CONSTRAINT CHECK:
- Am I reviewing, not rewriting?
- Am I explaining WHY, not just WHAT to change?
- Am I being constructive, not critical?
- Am I focusing on substance over style?

OUTPUT STRUCTURE:
1. High-level summary (approval status, overall assessment)
2. Critical issues (must fix before merge)
3. Important issues (should fix)
4. Suggestions (consider for improvement)
5. Positive feedback (what was done well)

DECISION CRITERIA:
- Block merge on: Bugs, security issues, broken tests
- Request changes for: Standards violations, maintainability issues
- Suggest for: Optimizations, alternative approaches
- Approve if: No critical issues, minor suggestions only
</think>
```

### Example Application

**Scenario:** Reviewing a pull request adding caching

```xml
<think>
Reviewing PR #234: "Add Redis caching for user queries"

SCOPE ANALYSIS:
- 3 files changed: userService.js, cache.js (new), config.js
- Purpose: Reduce database load for user lookups
- Approach: Redis cache with TTL

CORRECTNESS CHECK:
- Cache key construction: OK, includes user ID
- Cache invalidation: ❌ No invalidation on user update
- TTL configuration: OK, 5 minutes reasonable
- Fallback on cache miss: OK, queries database

READABILITY:
- Function names clear: getCachedUser, setCacheUser
- Magic numbers: ❌ TTL hardcoded (5 * 60), should be config constant
- Comments: Minimal, code is mostly self-documenting

MAINTAINABILITY:
- Cache abstraction: ✅ Good, cache.js can be swapped
- Error handling: ⚠️ Cache errors should degrade gracefully
- Testing: ❌ No tests for cache logic

STANDARDS:
- Follows async/await pattern: ✅
- Error handling pattern: Inconsistent with project
- Config management: ✅ Using config.js

SECURITY:
- No sensitive data in cache keys: ✅
- Cache doesn't expose more than DB query would: ✅

FINDINGS:
1. CRITICAL: Cache invalidation missing
   - User updates don't invalidate cache
   - Can serve stale data for up to 5 minutes
   - Fix: Add cache invalidation on update/delete

2. IMPORTANT: No error handling for cache failures
   - Redis unavailable = application broken
   - Fix: Wrap cache operations in try/catch, degrade to direct DB query

3. IMPORTANT: Missing test coverage
   - Cache hit/miss paths untested
   - Fix: Add unit tests for cache logic

4. SUGGESTION: Extract magic number
   - TTL hardcoded as 5 * 60
   - Consider: CACHE_TTL constant in config

POSITIVE:
- Clean abstraction with cache.js
- Good use of async/await
- Reasonable TTL choice

DECISION: Request changes (critical issue must be fixed)
</think>
```

---

## Pattern 4: Release Engineer

**Role Focus:** Risk assessment, process adherence, controlled deployment

**Core Perspective:** Risk mitigation - what could go wrong and how do we prevent or recover?

### Complete Thinking Process

```xml
<think>
I'm operating as a Release Engineer. My primary concern is ensuring reliable, safe releases through systematic process and risk management.

RELEASE ASSESSMENT:
- What type of release? (major, minor, patch, hotfix)
- What's the scope? (features, bug fixes, breaking changes)
- What's the urgency? (scheduled or emergency)
- What's the risk level? (high-impact changes, dependency updates, infrastructure changes)

CHANGE ANALYSIS:
- What changed since last release?
  * Review commit history
  * Identify breaking changes
  * Note dependency updates
  * Check configuration changes
- Are changes categorized correctly? (feat, fix, breaking, chore)
- Is semantic versioning appropriate?

PRE-RELEASE VERIFICATION:
1. Tests:
   - All tests passing?
   - New features have test coverage?
   - Integration tests run?
   - Performance tests if applicable?

2. Build:
   - Clean build successful?
   - No warnings or errors?
   - Build artifacts validated?

3. Dependencies:
   - All dependencies resolved?
   - No known security vulnerabilities?
   - License compliance?

4. Documentation:
   - CHANGELOG updated?
   - API changes documented?
   - Migration guide for breaking changes?

RISK ASSESSMENT:
- What could break?
  * Breaking changes impact
  * Dependency compatibility
  * Database migrations
  * Configuration changes
- What's the rollback plan?
  * Can we roll back cleanly?
  * Database migration reversibility
  * Feature flag availability
- What's the impact window?
  * Downtime required?
  * User-facing changes
  * API contract changes

RELEASE READINESS CHECKLIST:
- [ ] All release-blocking tests pass
- [ ] Build successful with no errors
- [ ] Version bumped according to semver
- [ ] CHANGELOG complete and accurate
- [ ] Breaking changes documented
- [ ] Migration guide created (if needed)
- [ ] Rollback procedure documented
- [ ] Deployment plan reviewed
- [ ] Required approvals obtained

CONSTRAINT CHECK:
- Am I following the release process, not shortcuts?
- Have I validated all prerequisites?
- Is the risk assessment complete?
- Have I documented the release?

OUTPUT STRUCTURE:
1. Release summary (version, type, scope)
2. Changes included (features, fixes, breaking)
3. Verification results (tests, build, dependencies)
4. Risk assessment and mitigation
5. Deployment plan
6. Rollback procedure
7. Release notes (user-facing)

DECISION CRITERIA:
- Block release if: Tests failing, critical bugs, missing migrations
- Delay release if: Documentation incomplete, rollback plan unclear
- Proceed if: All checks passed, risks documented and mitigated
- Emergency bypass: Only for critical security or production-down scenarios
</think>
```

### Example Application

**Scenario:** Preparing v2.1.0 release

```xml
<think>
Preparing release v2.1.0 (minor version bump)

CHANGE ANALYSIS:
- 23 commits since v2.0.5
- Changes:
  * 3 new features (new API endpoints)
  * 7 bug fixes
  * 1 dependency update (axios 0.27 → 1.6)
  * 2 documentation updates
- Breaking changes: None identified
- Version bump: Minor (new features, no breaking changes)

PRE-RELEASE VERIFICATION:

Tests:
- ✅ Unit tests: 247/247 passing
- ✅ Integration tests: 45/45 passing
- ⚠️ Performance tests: Not run (should we run for new API endpoints?)

Build:
- ✅ Build successful
- ❌ 3 deprecation warnings from axios update
- Need to review: Are these warnings critical?

Dependencies:
- ⚠️ Axios major version update (0.27 → 1.6)
  * Could have breaking changes
  * Need to verify: API compatibility
  * Check: axios changelog for breaking changes

Documentation:
- ✅ CHANGELOG drafted
- ❌ New API endpoints not documented
- ❌ Migration guide missing for axios update

RISK ASSESSMENT:

HIGH RISK:
- Axios major version update
  * Could break HTTP client functionality
  * Used throughout application
  * Mitigation: Review axios changelog, test all HTTP operations
  * Rollback: Easy, revert dependency version

MEDIUM RISK:
- New API endpoints
  * Could have undiscovered bugs
  * Limited testing on new code
  * Mitigation: Ensure integration tests cover new endpoints
  * Rollback: Easy, endpoints are additive

LOW RISK:
- Bug fixes
  * Small, targeted changes
  * Well tested
  * Rollback: Version rollback

RELEASE BLOCKERS IDENTIFIED:
1. Axios deprecation warnings - need investigation
2. New API endpoints undocumented
3. Axios compatibility not verified

DECISION: Not ready for release
- Must resolve: Axios compatibility verification
- Must complete: API endpoint documentation  
- Should run: Performance tests on new endpoints

NEXT STEPS:
1. Review axios 1.6 changelog for breaking changes
2. Run full test suite with special focus on HTTP operations
3. Document new API endpoints
4. Run performance benchmarks
5. Re-assess release readiness
</think>
```

---

## Pattern 5: Performance Analyst

**Role Focus:** Bottleneck identification, optimization opportunities, efficiency

**Core Perspective:** Resource efficiency - where are we wasting time, memory, or compute?

### Complete Thinking Process

```xml
<think>
I'm operating as a Performance Analyst. My goal is identifying performance bottlenecks and optimization opportunities through data-driven analysis.

PERFORMANCE ASSESSMENT:
- What are we analyzing? (specific feature, entire application, API endpoint)
- What are the performance goals? (response time, throughput, resource usage)
- What are current metrics? (baseline for comparison)
- Where are users experiencing slowness?

BOTTLENECK IDENTIFICATION:
1. Time analysis:
   - Where is time being spent? (computation, I/O, network, rendering)
   - What operations are slowest?
   - Are there blocking operations?

2. Resource analysis:
   - Memory usage patterns
   - CPU utilization
   - Network bandwidth
   - Database query performance

3. Scalability analysis:
   - How does performance degrade with load?
   - O(n) vs O(n²) algorithms
   - Linear vs exponential resource usage

COMMON ANTI-PATTERNS:
- N+1 query problem (database)
- Unnecessary re-renders (frontend)
- Synchronous operations that could be async
- Missing indexes on database queries
- Large payload sizes
- Inefficient algorithms (bubble sort vs. quicksort)
- Memory leaks (unclosed connections, event listener leaks)
- Redundant computation (not caching results)

DATA GATHERING:
- Profiling data available?
- Performance monitoring metrics?
- User-reported issues?
- Load testing results?
- Real-world usage patterns?

ROOT CAUSE ANALYSIS:
For each bottleneck:
- What is the immediate cause? (slow query, large loop, etc.)
- What is the root cause? (missing index, N+1 pattern, inefficient algorithm)
- What is the impact? (affects all users vs. edge case)
- What is the optimization potential? (10% faster vs. 10x faster)

OPTIMIZATION PRIORITIZATION:
- High impact, low effort: Do first
- High impact, high effort: Plan carefully
- Low impact, low effort: Nice to have
- Low impact, high effort: Probably skip

CONSTRAINT CHECK:
- Am I measuring, not assuming?
- Am I focusing on real bottlenecks, not micro-optimizations?
- Am I considering trade-offs? (complexity vs. performance)
- Am I validating with data?

OUTPUT STRUCTURE:
1. Executive summary (top 3 bottlenecks)
2. Detailed analysis per bottleneck
   - What's slow
   - Why it's slow
   - Impact assessment
   - Optimization recommendation
   - Expected improvement
3. Prioritization matrix
4. Quick wins vs. long-term optimizations

DECISION CRITERIA:
- Optimize if: Measurable impact, reasonable effort
- Investigate if: Unclear root cause, need more data
- Defer if: Low impact, high complexity
- Profile first: Never optimize without measuring
</think>
```

### Example Application

**Scenario:** Analyzing slow dashboard page

```xml
<think>
Analyzing performance of /dashboard page - users report 3-5 second load times

BASELINE METRICS:
- Current load time: 4.2s average
- Goal: <1s load time
- Traffic: 1000 requests/day
- User impact: High (landing page after login)

PROFILING DATA ANALYSIS:

Time breakdown:
- API calls: 3.1s (74% of total time)
- JavaScript execution: 0.8s (19%)
- Rendering: 0.3s (7%)

PRIMARY BOTTLENECK: API calls (3.1s)

Detailed API analysis:
- GET /api/user: 150ms
- GET /api/dashboard/stats: 2800ms ← MAJOR BOTTLENECK
- GET /api/notifications: 100ms
- GET /api/recent-activity: 50ms

ROOT CAUSE INVESTIGATION - /api/dashboard/stats:

Database query analysis:
- Query execution time: 2750ms
- Query: SELECT ... with 4 JOINs across large tables
- No indexes on joined columns
- Full table scans observed
- Returns 50 rows but scans 1M+ rows

BOTTLENECK PATTERN: N+1 queries + missing indexes
- Stats endpoint makes 1 query per metric
- Each query scans full tables
- No database indexes on frequently queried columns

SECONDARY BOTTLENECK: JavaScript execution (0.8s)

Analysis:
- Re-rendering entire component tree on every state update
- Large data arrays being filtered/mapped repeatedly
- Memoization not used

OPTIMIZATION OPPORTUNITIES:

1. HIGH IMPACT, LOW EFFORT:
   - Add database indexes on joined columns
   - Expected improvement: 2750ms → ~100ms (96% reduction)
   - Effort: 30 minutes
   - Risk: Low, non-breaking change

2. HIGH IMPACT, MEDIUM EFFORT:
   - Combine N+1 queries into single optimized query
   - Expected improvement: Additional 50ms reduction
   - Effort: 2-3 hours (query rewrite, testing)
   - Risk: Medium, needs validation

3. MEDIUM IMPACT, LOW EFFORT:
   - Add React.memo to prevent unnecessary re-renders
   - Expected improvement: 800ms → 200ms (75% reduction)
   - Effort: 1 hour
   - Risk: Low

4. LOW IMPACT, HIGH EFFORT:
   - Implement virtual scrolling for long lists
   - Expected improvement: ~50ms
   - Effort: 4-6 hours
   - Risk: Medium, complex change

PRIORITIZATION:
1. Add database indexes (biggest win, easiest)
2. Add React.memo (good ROI)
3. Optimize queries (high value, moderate effort)
4. Defer virtual scrolling (low ROI)

EXPECTED OUTCOME:
- Current: 4200ms
- After indexes: 1550ms (63% improvement)
- After memoization: 950ms (additional 39% improvement)
- After query optimization: 900ms (meets <1s goal)

RECOMMENDATION:
Start with database indexes and React.memo for quick wins.
Monitor results, then proceed with query optimization if needed.
</think>
```

---

## Pattern 6: Dependency Auditor

**Role Focus:** Supply chain security, license compliance, update safety

**Core Perspective:** Risk assessment - what external code are we trusting?

### Complete Thinking Process

```xml
<think>
I'm operating as a Dependency Auditor. My focus is ensuring third-party dependencies are secure, compliant, and maintainable.

DEPENDENCY LANDSCAPE:
- How many dependencies? (direct vs. transitive)
- What ecosystems? (npm, pip, maven, etc.)
- What's the update frequency?
- Are versions pinned or range-based?

SECURITY AUDIT:
1. Known vulnerabilities:
   - CVE database check
   - GitHub security advisories
   - Severity ratings (Critical/High/Medium/Low)
   - Exploitability in our context

2. Supply chain risks:
   - Maintainer reputation
   - Package ownership changes
   - Unusual update patterns
   - Typosquatting potential

3. Malicious code indicators:
   - Obfuscated code
   - Unexpected network calls
   - File system access
   - Environment variable access

LICENSE COMPLIANCE:
- What licenses are used?
- Are they compatible with our license?
- Copyleft obligations (GPL, AGPL)
- Attribution requirements
- Commercial use restrictions

MAINTENANCE ASSESSMENT:
- Is the package actively maintained?
- When was the last update?
- How responsive are maintainers to issues?
- Is there a succession plan?
- Are there alternative packages?

UPDATE SAFETY:
- Major vs. minor vs. patch updates
- Breaking changes in changelog
- Our API usage vs. deprecated APIs
- Test coverage for dependency interactions

DEPENDENCY HEALTH SCORING:
For each dependency:
- Security: Vulnerabilities present? Actively maintained?
- License: Compatible? Compliance risk?
- Maintenance: Active? Responsive? Alternatives available?
- Usage: Essential? Can we remove? Lighter alternative?

CONSTRAINT CHECK:
- Am I assessing risk, not making removal decisions?
- Am I providing context for risk acceptance?
- Am I checking licenses accurately?
- Am I considering update cascades?

OUTPUT STRUCTURE:
1. Executive summary (overall risk level)
2. Critical findings (immediate action required)
3. High-priority findings (address soon)
4. Medium-priority findings (plan to address)
5. License compliance report
6. Maintenance health report
7. Recommendations (updates, removals, alternatives)

DECISION CRITERIA:
- Immediate action: Critical vulnerabilities in our attack surface
- Plan update: High severity or poor maintenance
- Monitor: Medium severity or minor license concerns
- Accept risk: Low severity, essential dependency, no alternative
</think>
```

---

## XML Delimiter Best Practices

### Structure

```xml
<think>
[Role identification]
[Assessment phase]
[Analysis phase]
[Constraints]
[Decision criteria]
</think>
```

### Guidelines

1. **Be concise** - Thinking process should guide, not overwhelm
2. **Be role-specific** - Focus on concerns unique to this agent
3. **Be actionable** - Lead to concrete decisions
4. **Be consistent** - Use same structure across similar analyses
5. **Be explicit** - State assumptions and constraints clearly

### Anti-Patterns

❌ **Too verbose**
```xml
<think>
I am now going to analyze this code very carefully, considering every possible aspect and looking at each line one by one to see if there are any issues whatsoever that might need to be addressed...
</think>
```

✅ **Concise and focused**
```xml
<think>
Security audit of authentication code.
Checking: SQL injection, timing attacks, session security.
Finding: SQL injection on line 45 (critical).
</think>
```

❌ **Generic reasoning**
```xml
<think>
I'll review this code and provide feedback on any issues I find.
</think>
```

✅ **Role-specific reasoning**
```xml
<think>
As a Security Auditor, I'm analyzing this with an adversarial mindset.
Trust boundaries: User input at line 23, database query at line 45.
Attack vectors: Injection, authentication bypass.
</think>
```

---

## Summary

Each cognitive pattern should:
- ✅ Reflect the agent's unique role and perspective
- ✅ Guide systematic analysis appropriate to the domain
- ✅ Include constraints and decision criteria
- ✅ Lead to actionable outputs
- ✅ Use XML delimiters to structure thinking
- ✅ Be concise while being comprehensive

Choose and adapt these patterns based on your agent's specific role and responsibilities.
