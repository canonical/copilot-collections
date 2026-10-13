---
name: configure-gh-jira-sync-bot
description: Configures canonical/gh-jira-sync-bot in a repository by creating or updating .github/.jira_sync_config.yaml following the platform-engineering-charm-template conventions, then validates it. Use when a repository needs GitHub-to-Jira issue synchronization or its Jira sync config must be created, fixed or audited.
metadata:
  author: canonical/platform-engineering
  version: "1.0.0"
---

# Configure gh-jira-sync-bot

Reference: https://github.com/canonical/gh-jira-sync-bot and
canonical/platform-engineering-charm-template#165.

## Workflow

1. Check whether `.github/.jira_sync_config.yaml` exists. If so, keep user-specific values (project key, mappings) and only align it with the template.
2. Copy `assets/jira_sync_config.template.yaml` to `.github/.jira_sync_config.yaml` when missing.
3. Ask the user which Jira component(s) the repository belongs to and set `settings.components` (a list, case-sensitive names). Valid names are listed in `VALID_COMPONENTS` of `scripts/validate_config.py`. Change `jira_project_key` only if the project is not `ISD`.
4. Validate:

   ```bash
   uv run scripts/validate_config.py .github/.jira_sync_config.yaml
   ```

   Or, without a local copy of the skill:

   ```bash
   uvx --from "git+https://github.com/canonical/copilot-collections#subdirectory=groups/platform-engineering/skills/configure-gh-jira-sync-bot" validate-jira-sync-config .github/.jira_sync_config.yaml
   ```

   Fix every reported error and re-run until it prints `OK`.
5. Remind the user that the GitHub App of the bot must be installed on the repository.

## Template conventions

- Keep the 3-line `# template-version` header; removing it opts the file out of template propagation.
- `labels: [bug, enhancement]` prevents "Dependency dashboard" issues from being synced.
- `label_mapping`: `bug: Bug`, `enhancement: Story`.
- No `epic_key`.
- `add_gh_comment: true`.

## Mandatory fields (checked by the validator)

`settings.jira_project_key`, `settings.status_mapping.opened`, `settings.status_mapping.closed`,
a non-empty `settings.components` list of known Jira components, and `settings.labels` containing `bug` and `enhancement`. `settings.epic_key` must not be defined. Every template in `.github/ISSUE_TEMPLATE/` (next to the config) must have a `labels` key containing `bug` or `enhancement`.

## Refreshing the component list

Jira has no component listing through the Atlassian MCP server. Query
`project = ISD AND component is not EMPTY` with `fields: ["components"]` and update `VALID_COMPONENTS`.
