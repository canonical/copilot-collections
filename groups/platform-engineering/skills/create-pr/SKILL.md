---
name: create-pr
description: Create a pull request for the current session. Use when the user wants to open a PR with the session's changes.
# reference documentation: https://github.com/canonical/platform-engineering-docs/edit/main/docs/delivery-workflows/github/pull-requests/index.rst
---

# Create Pull Request

Use the GitHub MCP server to create a pull request — do NOT use the `gh` CLI.

1. Run the compile and hygiene tasks (fixing any errors)
2. If there are any uncommitted changes, use the `/commit` skill to commit them
3. Review all changes in the current session
4. Write a clear, concise PR title with a short area prefix (e.g. "sessions: …", "editor: …")
5. Write a description covering what changed, why, and anything reviewers should know
6. Create the pull request following the guidelines from the next sections.

## PR description

Unless the PR is trivial or self-explanatory (for example, fixing typos in the
documentation, a well known task that needs to be done across many repositories
such as enabling a new bot), the PR description should include:

- A high level overview of the change
- The reason the change is needed
- Any additional information requested in the pull request template.

Use the template available in `.github/pull_request_template.md>` if available.

## PR branch name

PR branches should be named in a way that indicates the purpose of the branch.

Format: **type/scope-short-description[-optional-identifier]** (all lowercase, words separated by hyphens)

Where the type can be one of the following:

- `feat`: a new feature
- `fix`: a bug fix
- `docs`: documentation changes
- `chore`: a change that doesn't add a feature or fix a bug
           (typically a maintenance change, such as updating dependencies or aligning with standards)
- `test`: adding or updating tests (if not related to a specific feature or bug fix,
          in which case it should be tagged with the relevant type)
- `ci`: changes to our CI configuration or scripts (if not related to a specific feature or bug fix,
        in which case it should be tagged with the relevant type)

Examples:

- `feat/tcp-wildcard-sni-support-isd-1234`
- `fix/non-working-tls-relation`
- `chore/terraform-align-module`

## PR title

The PR title follows the same philosophy as the branch name.

Format: **type(scope):short description [optional-identifier]** (all lowercase, words separated by spaces)

Where the type is the same as described in the branch name section.

Examples:

- `feat(tcp): add wildcard SNI support (ISD-1234)`
- `fix(tls): non-working TLS relation`
- `chore(terraform): align module with standards`
