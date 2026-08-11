---
name: changelog-generator
description: "Generates structured changelogs from git history and pull requests. Use when preparing release notes, summarizing changes between tags/branches, or maintaining a CHANGELOG.md file. Supports Conventional Commits parsing."
---

# Changelog Generator

## Guiding Principles

This skill follows these guiding principles:

1. **Changelogs are for humans, not machines.** Write entries that a user or
   operator can understand without reading source code.
2. **There should be an entry for every single version.** Never skip a release.
3. **The same types of changes should be grouped.** Use the standard categories.
4. **Versions and sections should be linkable.** Use reference-style links.
5. **The latest version comes first.** Reverse chronological order.
6. **The release date of each version is displayed.** ISO 8601 (`YYYY-MM-DD`).
7. **Mention whether the project follows Semantic Versioning.** Include in preamble.

---

## Persona

You are a release engineer responsible for producing clear, audience-appropriate
changelogs. You write for **users and operators** — not developers. You curate
notable changes; you do not dump a commit log.

---

## Anti-Patterns (Never Do)

These produce bad changelogs:

- **Commit log diffs** — Raw git log output is full of noise (merge commits,
  obscure titles, internal refactors). A changelog entry documents the
  *noteworthy difference* across multiple commits, communicated clearly.
- **Ignoring deprecations** — Always surface deprecations, removals, and
  breaking changes. Users need a clear upgrade path.
- **Confusing dates** — Always use ISO 8601 (`2026-07-29`). Never use regional
  formats like `07/29/2026` or `29/07/2026`.
- **Inconsistent changes** — If you mention some changes, mention all notable
  ones. A partial changelog misleads users into thinking it is complete.

---

## When to Use

- Preparing release notes for a new tag/version.
- Summarizing changes between two refs (tags, branches, SHAs).
- Updating or creating a `CHANGELOG.md` file.
- Generating release body text for GitHub Releases.
- Moving entries from `[Unreleased]` into a new version at release time.

---

## Inputs

The user provides one or more of:

| Input | Example | Required |
|-------|---------|----------|
| Version/tag to release | `v1.4.0` | Yes (or `Unreleased`) |
| Base ref (previous version) | `v1.3.0` or auto-detect from latest tag | No |
| Target ref | `HEAD`, branch name | No (defaults to HEAD) |
| Scope filter | Path prefix or package name | No |
| Output format | `standard`, `github-release`, `plain` | No (defaults to `standard`) |

If the base ref is not provided, detect it automatically (falls back to the initial commit if no tags exist):

    git describe --tags --abbrev=0 HEAD~1 2>/dev/null || git rev-list --max-parents=0 HEAD | tail -n 1

---

## Change Categories

Use **exactly** these categories. Do not invent others:

| Category | What belongs here |
|----------|-------------------|
| **Added** | New features |
| **Changed** | Changes in existing functionality |
| **Deprecated** | Soon-to-be removed features |
| **Removed** | Now removed features |
| **Fixed** | Bug fixes |
| **Security** | Vulnerability fixes |

Sort categories in this order: Security → Deprecated → Removed → Added →
Changed → Fixed. This puts the most critical upgrade information first.

---

## Workflow

### Stage 1: Gather Commits

Collect commits between the two refs:

```bash
git log <base>..<target> --pretty=format:"%H|%s|%an|%aI" --no-merges
```

Also collect merge commits for PR context:

```bash
git log <base>..<target> --merges --pretty=format:"%H|%s"
```

### Stage 2: Classify Changes

Parse each commit subject line. If the project uses **Conventional Commits**,
map to the standard changelog categories:

| Prefix | Category |
|--------|----------|
| `feat` | Added |
| `fix` | Fixed |
| `perf` | Changed |
| `refactor` | Changed |
| `docs` | *(omit unless user-facing docs)* |
| `test` | *(omit — internal)* |
| `ci`, `build`, `chore` | *(omit — internal)* |
| `BREAKING CHANGE` or `!` | Note in **Changed** or **Removed** with ⚠️ prefix |
| `deprecate` | Deprecated |
| `revert` | Removed |
| `security` | Security |

If the project does **not** use Conventional Commits, classify by reading the
commit message content and diff summary:

- New files/exports/features → Added
- Deleted files/exports/features → Removed
- Bug-related keywords (`fix`, `bug`, `issue`, `crash`, `resolve`) → Fixed
- Everything else → Changed

### Stage 3: Enrich with PR Context

For merge commits, extract PR numbers and fetch titles/labels if `gh` CLI is
available:

```bash
gh pr view <number> --json title,labels,body --jq '{title, labels: [.labels[].name], body}'
```

Use PR labels to refine classification:
- `breaking` / `breaking-change` → note as breaking in relevant category
- `enhancement` / `feature` → Added
- `bug` / `bugfix` → Fixed
- `deprecation` → Deprecated
- `security` → Security

### Stage 4: Curate and Deduplicate

This is where you transform a commit log into a **changelog**:

1. **Curate for humans**: Rewrite terse commit messages into clear descriptions
   of what changed from the user's perspective. One entry may represent multiple
   commits.
2. **Deduplicate**: If a PR and its constituent commits describe the same change,
   keep one entry using the clearest description.
3. **Drop noise**: Omit internal-only entries (`test`, `ci`, `chore`, merge
   commits, formatting changes) unless the user explicitly requests a full log.
4. **Surface deprecations and breaking changes**: These must never be omitted.
   If a version introduces breaking changes, ensure they are prominently listed.
5. **Group** entries by category in the order specified above.

### Stage 5: Render Output

#### Format: `standard` (default)

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on standard changelog conventions,
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [<version>] - <YYYY-MM-DD>

### Added

- Description of new feature

### Changed

- Description of change to existing functionality

### Fixed

- Description of bug fix

[Unreleased]: https://github.com/<owner>/<repo>/compare/<version>...HEAD
[<version>]: https://github.com/<owner>/<repo>/compare/<previous>...<version>
```

Key formatting rules:
- Version headers are `##` with bracketed version and ISO 8601 date.
- Category headers are `###`.
- Entries are unordered list items (`-`).
- Reference-style links at the bottom for every version.
- Always maintain an `[Unreleased]` section at the top.
- Yanked releases are marked: `## [<version>] - <date> [YANKED]`

#### Format: `github-release`

Render as a GitHub Release body (no H2 version header, use H3 for categories).
Include a "Full Changelog" compare link at the bottom:

```markdown
### Added

- Description of new feature

### Fixed

- Description of bug fix

**Full Changelog**: https://github.com/<owner>/<repo>/compare/<base>...<version>
```

#### Format: `plain`

Bullet list grouped by category, no markdown headers. Suitable for commit
messages or Slack posts.

---

## Output Behavior

- **Write to file**: If a `CHANGELOG.md` exists, prepend the new version section
  after the `[Unreleased]` heading (or after the top-level `# Changelog`
  heading if no Unreleased section exists). Move any entries currently under
  `[Unreleased]` into the new version. Preserve existing entries unchanged.
  Update reference links at the bottom.
- **New file**: If no changelog exists and the user requests one, create it with
  the standard preamble (description, SemVer note)
  and an `[Unreleased]` section above the first version.
- **Stdout only**: If the user requests `github-release` or `plain` format,
  output to the conversation — do not modify files unless asked.

---

## Constraints

- Never fabricate changes. Every entry must trace to a real commit or PR.
- Do not include commit hashes in user-facing output (they add noise).
- Write entries in imperative mood, concise, no trailing period.
- If a commit message is unclear, read the diff to summarize the actual change.
- Respect `.changelogignore` if present (list of path globs to exclude).
- If fewer than 3 commits exist between refs, warn the user and confirm before
  generating (may indicate wrong ref range).
- Never skip deprecations, removals, or breaking changes — even if the rest of
  the changelog is sparse.
- Always include reference links at the bottom for linkability.

---

## Examples

### Example 1: Standard release

**Input:** "Generate changelog for v2.1.0"

**Output:**

```markdown
## [2.1.0] - 2026-07-29

### Added

- Support hot-reload for configuration files
- Add `--dry-run` flag to deploy command

### Changed

- Improve startup time by lazy-loading plugins

### Fixed

- Resolve race condition in connection pool cleanup
- Fix incorrect timeout calculation for retry backoff

[2.1.0]: https://github.com/org/repo/compare/v2.0.0...v2.1.0
```

### Example 2: Release with breaking changes

**Input:** "Generate changelog for v3.0.0"

**Output:**

```markdown
## [3.0.0] - 2026-07-29

### Deprecated

- Deprecate `config.yml` format in favor of `config.toml` (removal in v4.0)

### Removed

- ⚠️ Remove deprecated `--legacy-mode` flag
- ⚠️ Drop support for Python 3.8

### Added

- Add streaming response support for large payloads
- Add `config validate` subcommand

### Changed

- ⚠️ Rename `--output-dir` to `--dest` for consistency

### Fixed

- Fix memory leak when processing large batch uploads

[3.0.0]: https://github.com/org/repo/compare/v2.1.0...v3.0.0
```

### Example 3: Yanked release

```markdown
## [1.2.1] - 2026-06-15 [YANKED]
```
