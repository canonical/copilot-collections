---
description: 'Guidelines for creating release notes artifacts in the Indico Operator repository'
applyTo: 'docs/release-notes/**/*.yaml'
---

# Release Notes Instructions for GitHub Copilot

## Purpose
This file provides specific guidance for creating and maintaining release notes artifacts in the Indico Operator repository.

## Change Artifact Requirements

### When to Create
A change artifact is **required** for any PR that modifies:
- Source code (`src/**/*.py`)
- Charm configuration (`config.yaml`, `charmcraft.yaml`)
- Actions (`actions.yaml`)
- Libraries (`lib/**/*.py`)
- Dependencies (`requirements.txt`, `pyproject.toml`)
- Metadata (`metadata.yaml`)

### File Location and Naming
- Path: `docs/release-notes/artifacts/pr<PR_NUMBER>.yaml`
- Example: `docs/release-notes/artifacts/pr123.yaml`
- Use the actual PR number (not placeholder)

### Required Schema
```yaml
schema_version: 1
changes:
  - title: "Brief description of the change (imperative mood)"
    author: "GitHub username"
    type: "minor|major|breaking|security|bugfix"
    description: "Detailed explanation of what changed and why"
    urls: 
      pr: "https://github.com/canonical/indico-operator/pull/<NUMBER>"
      related_doc: "URL to documentation (optional)"
      related_issue: "URL to issue (optional)"
    visibility: public
    highlight: false  # Set to true for major/breaking changes
```

### Change Types

#### User-Facing vs Internal Changes
**CRITICAL**: Distinguish between changes that affect **charm users** vs **charm developers**:

- **User-facing**: Changes to charm configuration, actions, relations, behavior that users interact with
- **Internal**: Library updates, code refactoring, dependency changes that don't change user experience

#### Type Definitions
- **minor**: New user-facing features, enhancements (backward compatible for users)
- **major**: Significant new user functionality (backward compatible for users)  
- **breaking**: Changes requiring **user action** or breaking **user compatibility**
- **security**: Security fixes or improvements
- **bugfix**: Bug fixes affecting user-visible behavior

#### Library and Dependency Updates
Library updates (including breaking changes to internal APIs) should typically be:
- **minor**: If they add functionality without changing user experience
- **bugfix**: If they fix issues affecting users
- **security**: If they address security vulnerabilities
- **breaking**: ONLY if users must change their configuration or lose functionality

### Best Practices

#### Title (Imperative Mood)
✅ Good:
- "Add support for external PostgreSQL database"
- "Fix config-changed event handler crash"
- "Update TLS certificate rotation logic"

❌ Bad:
- "Added support..." (past tense)
- "Adding support..." (progressive)
- "Adds support..." (third person)

#### Description
Should answer:
1. **What** changed (specific functionality/behavior)
2. **Why** it changed (problem solved, requirement met)
3. **Impact** on users (if any action needed)
4. **Consise** Be consise and to the point.

For breaking changes, include:
- Migration steps
- Deprecated functionality
- New requirements

#### Examples

**Minor Feature:**
```yaml
schema_version: 1
changes:
  - title: "Add connection pooling for database connections"
    author: "johndoe"
    type: minor
    description: "Implements connection pooling to reduce database connection overhead and improve performance under high load. No configuration changes required."
    urls: 
      pr: "https://github.com/canonical/indico-operator/pull/42"
    visibility: public
    highlight: false
```

**Breaking Change:**
```yaml
schema_version: 1
changes:
  - title: "Remove deprecated 'legacy-config' configuration option"
    author: "janedoe"
    type: breaking
    description: "The 'legacy-config' option deprecated in v1.5 has been removed. Users must migrate to 'config-v2' format. See migration guide at docs/migration.md."
    urls: 
      pr: "https://github.com/canonical/indico-operator/pull/67"
      related_doc: "https://github.com/canonical/indico-operator/blob/main/docs/migration.md"
      related_issue: "https://github.com/canonical/indico-operator/issues/45"
    visibility: public
    highlight: true
```

**Security Fix:**
```yaml
schema_version: 1
changes:
  - title: "Fix authentication bypass in admin action"
    author: "security-team"
    type: security
    description: "Addresses CVE-2024-XXXX by enforcing proper authentication checks in admin-level actions. All users should update immediately."
    urls: 
      pr: "https://github.com/canonical/indico-operator/pull/89"
      related_issue: "https://github.com/canonical/indico-operator/security/advisories/GHSA-XXXX"
    visibility: public
    highlight: true
```

**Bugfix:**
```yaml
schema_version: 1
changes:
  - title: "Fix relation-broken event not cleaning up resources"
    author: "contributor"
    type: bugfix
    description: "Ensures that database credentials and connection strings are properly removed when a relation is broken, preventing resource leaks."
    urls: 
      pr: "https://github.com/canonical/indico-operator/pull/34"
      related_issue: "https://github.com/canonical/indico-operator/issues/28"
    visibility: public
    highlight: false
```

## Template Usage

Use the template at `docs/release-notes/template/_change-artifact-template.yaml` as a starting point:

```bash
# Create artifact for PR #123
cp docs/release-notes/template/_change-artifact-template.yaml \
   docs/release-notes/artifacts/pr123.yaml
```

Then fill in all required fields.

## Validation Checklist

Before committing a change artifact, verify:
- [ ] File is named `pr<NUMBER>.yaml` with correct PR number
- [ ] `schema_version` is set to `1`
- [ ] `title` uses imperative mood and is concise
- [ ] `author` is the GitHub username
- [ ] `type` is one of: minor, major, breaking, security, bugfix
- [ ] `description` explains what, why, and impact
- [ ] `pr` URL is correct and complete
- [ ] `visibility` is set (usually `public`)
- [ ] `highlight` is `true` for breaking/major/security changes
- [ ] YAML syntax is valid (no tabs, proper indentation)

## Common Mistakes to Avoid

1. **Using PR title as-is**: PR titles are often too technical; craft user-focused titles
2. **Forgetting the artifact**: Always create when modifying code/config
3. **Wrong file path**: Must be in `docs/release-notes/artifacts/`
4. **Invalid YAML**: Use spaces (not tabs), check syntax
5. **Vague descriptions**: Be specific about functionality and impact
6. **Wrong type**: Security fixes are `security`, not `bugfix`
7. **Missing highlight**: Set `highlight: true` for breaking changes

## Integration with Release Process

Change artifacts are automatically processed during releases:
1. Artifacts are collected from `docs/release-notes/artifacts/`
2. Combined with release metadata from `docs/release-notes/releases/`
3. Rendered into markdown using template `docs/release-notes/template/release-template.md.j2`
4. Published to documentation site

## Questions?

If unsure about:
- **Change type**: Default to `minor` for new features, `bugfix` for fixes
- **Highlight**: Set `true` if users need to take action
- **Visibility**: Use `public` unless it's internal-only change

Refer to existing artifacts in `docs/release-notes/artifacts/` for examples.
