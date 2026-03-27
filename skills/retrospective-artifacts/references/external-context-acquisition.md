# External Context Acquisition (MCP-First)

This skill must acquire external context with the following strict order:

1. **Primary path: MCP servers**
   - Use available MCP integrations for GitHub, Jira, and Mattermost first.
   - If MCP is available and succeeds, do not invoke fallback scripts.

2. **Fallback path: local scripts (only when MCP unavailable/fails)**
    - GitHub: `scripts/fetch_github_context.py`
    - Jira: `scripts/fetch_jira_context.py`
    - Mattermost: `scripts/fetch_mattermost_thread.py`

All fallback scripts must remain **self-contained within this skill's `scripts/` directory** and must not depend on repository-level helper scripts.

## Error-handling requirements

Fallback scripts must be explicit and actionable:

- Missing binary/dependency => print exact missing requirement and install hint.
- Missing env var/token => print exact variable name and example export command.
- Invalid URL/ID => print accepted formats and one valid example.
- Auth failure => report status and likely remediation.

Never fail silently. Never return success-shaped empty outputs.

## Required environment variables

### GitHub fallback
- `GITHUB_READ_TOKEN`

### Jira fallback
- `JIRA_URL`
- `JIRA_USERNAME`
- `JIRA_READ_TOKEN` (or `JIRA_FULL_ACCESS_TOKEN`)

### Mattermost fallback
- `MM_URL`
- `MM_TOKEN`

## Output conventions

- Save fetched content in artifact `context/` by source.
- Include source URL and retrieval timestamp in frontmatter or header.
- Preserve raw evidence snippets where possible.
- For markdown outputs, include a high-signal `## Summary` section near the top.
- If source content has no usable body/details, summary must explicitly state that and include available metadata/signals.

## Default recursive gathering policy

Recursive gathering is enabled by default with bounded depth.

Rules:
- Parse fetched content for first-level referenced URLs.
- Acquire linked artifacts when relevant to current focus directive and incident chain.
- Default max depth: `1` (seed links + their direct references).
- Do not recurse further unless explicitly requested by the user.
- Deduplicate by canonical URL.
- Skip known low-signal links (avatars, badges, static assets, generic nav pages).
- Record parent-child trace in each acquired file header:
  - `Discovered From: <source-file-or-url>`

## Manual fallback handoff

If MCP and scripts both fail, use this baked-in handoff format to request user-provided raw context.

### Required handoff sections

1) Acquisition Failure
- Source type
- Source URL/ID
- Failure reason
- Missing requirements

2) What I Need From You
- Request only minimum required fields for the current retrospective.

3) Copy-Paste Response Template

```markdown
Source: <github|jira|mattermost|other>
URL/ID: <original source>

Summary:

Key timeline/events:

Important decisions:

Errors/logs (raw excerpts):

Relevant links or IDs mentioned in thread/ticket:
```

4) Assurance sentence (exact)

`I will only use the evidence you provide and will flag any missing data explicitly.`
