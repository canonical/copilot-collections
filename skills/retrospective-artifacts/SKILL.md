---
name: retrospective-artifacts
description: Builds and parses structured retrospective artifact folders for troubleshooting, incident review, and delivery retros. Use this skill when capturing session context, synthesizing external context (GitHub, Jira, Mattermost, logs), querying prior retrospectives, or preparing downstream inputs for OKB entries, postmortems, and agent/skills/instruction improvements.
---

# Retrospective Artifacts

## Overview

Create durable, queryable retrospective artifacts under `.retrospectives/` and provide deterministic retrieval of key learnings from prior artifacts.

This skill has two modes:

- **CREATE mode**: interview, gather context, and build a standardized retrospective folder.
- **PARSE mode**: read existing retrospective folders and return only the requested facts.

## Routing

Use **CREATE mode** when the request asks to:
- run a retrospective
- capture session learnings
- build a retro artifact folder
- summarize current work and preserve context

Use **PARSE mode** when the request asks to:
- query previous retrospectives
- extract specific learnings/code snippets/logs
- shortlist `okb_worthy` items
- find sessions needing context asset improvement

## Workflow 1: CREATE mode

Follow these steps in order.

### Step 1: Context triage
1. Inspect current conversation and workspace context.
2. Identify missing facts: catalyst, impact, investigation, resolution, and downstream signals.
3. Use `references/context-intake-checklist.md` to drive coverage.

### Step 2: Progressive interview
Ask 1-3 targeted questions to fill missing gaps.
Always request relevant external links if available:
- GitHub issues/PRs/Actions logs
- Jira tickets
- Mattermost threads
- external incident docs

Before extraction, require a **focus directive** from the user to control what gets exported from large contexts.
Accept examples like:
- "only moments where Copilot iterated 3+ times"
- "only failed attempts and workarounds"
- "only final solutions and why they worked"
- "exclude routine successful steps"

Do not proceed to generation until the required minimum context is present.

### Step 3: External context acquisition
For each provided link:
1. **Prefer MCP integrations first** (GitHub/Jira/Mattermost MCP servers when available).
2. If MCP is unavailable for a source, use fallback scripts in `scripts/`.
3. If retrieval fails or access is denied, state that clearly and request pasted text.
4. Do not infer missing external content.

By default, perform bounded recursive gathering:
- discover first-level referenced URLs in fetched content
- acquire relevant linked artifacts (GitHub/Jira/Mattermost/docs) when they add incident value
- stop at one recursive level unless user explicitly asks for deeper traversal
- respect focus directive to avoid low-signal expansion

Use `references/context-intake-checklist.md` and `references/external-context-acquisition.md` as mandatory guidance.

### Step 3.1: Markdown summary quality gate
Any acquired context saved as markdown must include an explicit, high-signal summary section near the top.

Minimum requirement:
- `## Summary`

Summary quality expectations:
- 3-7 concise bullets or short paragraphs
- include what changed, why it mattered, and key technical signals
- prioritize incident-relevant facts over low-signal detail

When using MCP for retrieval, enforce this summary section before finalizing the artifact.

### Step 4: Artifact generation
Create a timestamped folder under:
`.retrospectives/YYYY-MM-DD_short-session-name/`

Expected structure:
- `retro-summary.md`
- `context/` (external threads/docs)
- `logs/` (errors, traces, diagnostics)
- `code-snippets/` (before/after or key snippets)

Use `references/retro-summary-template.md` as the required output schema.
Ensure the generated summary clearly states the selected focus directive and what was intentionally excluded.

### Step 5: Quality gate
Before finalizing:
1. Validate frontmatter is complete and truthful.
2. Ensure all referenced relative paths exist.
3. Set downstream flags (`okb_worthy`, `context_asset_improvement_needed`) conservatively from evidence.
4. Never fabricate snippets, logs, or external thread content.

## Workflow 2: PARSE mode

When asked to retrieve past information:
1. Locate matching folders in `.retrospectives/`.
2. Read `retro-summary.md` first.
3. Use `references/parse-query-patterns.md` to map request type to extraction strategy.
4. If requested data points to relative files (for example in `context/`, `logs/`, `code-snippets/`), open only those files.
5. Return only requested information with concise synthesis.

Do not dump full directories unless explicitly requested.

## Output contract

- For CREATE mode, output:
  - artifact path
  - generated file index
  - concise summary of captured catalyst, resolution, and downstream signals
- For PARSE mode, output:
  - direct answer to query
  - supporting artifact path(s)
  - confidence caveat when data is missing or inaccessible

## Constraints

- Anti-hallucination: never invent context, logs, or links.
- Path discipline: use explicit relative paths inside artifacts.
- Evidence-first tagging: set metadata flags from observable evidence.
- Non-destructive behavior: read/summarize existing retros by default.
- Integration priority: MCP servers first, local scripts second.
- Fallback scripts must fail loudly with explicit setup instructions when dependencies/tokens are missing.

## References

- `references/context-intake-checklist.md`
- `references/retro-summary-template.md`
- `references/parse-query-patterns.md`
- `references/external-context-acquisition.md`

## Manual fallback handoff

When acquisition fails after MCP + script fallback, use the baked-in handoff format in `references/external-context-acquisition.md` and request user-provided raw context.

## Script fallback quick reference

Only use these scripts when MCP is unavailable for the source.

- GitHub URL fetch:
  - `python3 scripts/fetch_github_context.py --url "<github-url>" --output "<artifact>/context/github-*.md"`
- Jira issue fetch:
  - `python3 scripts/fetch_jira_context.py --url "<jira-url>" --output "<artifact>/context/jira-*.md"`
- Mattermost thread fetch:
  - `python3 scripts/fetch_mattermost_thread.py --thread "<mm-thread-url-or-id>" --output "<artifact>/context/mm-*.md"`
