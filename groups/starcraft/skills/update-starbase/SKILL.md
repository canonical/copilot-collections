---
name: update-starbase
description: Syncs Starbase-managed project files by adding the canonical/starbase remote and merging starbase/main into the current branch. Use when updating common.mk and related shared Starcraft build/CI conventions.
---

# Update Starbase

## Scope

This is the first part of the workflow: bringing upstream Starbase changes into
the current repository. Conflict resolution guidance is intentionally separate
and will be added in the next part.

## Part 1: Add the remote and merge Starbase

1. Confirm the repository is in a safe state before merge:

   ```bash
   git --no-pager status --short --branch
   ```

   If there are unrelated local edits, stop and decide whether to stash or
   commit first.

2. Ensure a `starbase` remote exists and points to Canonical Starbase:

   ```bash
   git remote get-url starbase >/dev/null 2>&1 \
     && git remote set-url starbase https://github.com/canonical/starbase.git \
     || git remote add starbase https://github.com/canonical/starbase.git
   ```

3. Fetch the Starbase refs:

   ```bash
   git fetch starbase --prune
   ```

4. Create a work branch before starting the merge:

   ```bash
   git switch -c work/<descriptive-branch-name>
   ```

5. Merge from Starbase main into the current branch:

   ```bash
   git merge --no-ff starbase/main
   ```

6. Capture merge state:
   - If merge succeeds, continue to project checks.
   - If merge conflicts, stop and report conflicted files:

   ```bash
   git --no-pager status --short
   ```

7. If GitHub reports conflicts with `main`, fetch the latest `origin/main` and
   redo the merge from that branch before continuing.

## Output

Report one of:
- `merge-clean`: Starbase merged with no conflicts.
- `merge-conflicted`: merge stopped with conflicts, including the file list from `git status --short`.

## Pre-PR validation (required)

Before creating a PR, ensure repository checks pass:

```bash
make format
make lint
make test-fast
```

Do not create the PR until these commands complete successfully.

## PR labeling (required)

When opening the PR, apply the label:
- `PR: Merge`

## PR review and CI

- Open the PR as a draft, request a Copilot review while it is still draft, and
  keep iterating until the review is clean enough to mark ready.
- Check the PR's CI status before handing it off.
- If CI is still running or likely to fail, start a background agent to watch
  the PR checks and report failures so they can be fixed promptly.
- You do not need to wait for the full matrix to finish before fixing failures
  in jobs that are already failing or have enough signal to act on.
- Once the PR is out of draft, make separate commits for follow-up fixes until
  the PR is fully approved.
- Once CI is running, squash any follow-up fixes back into the original merge
  commit instead of layering new commits on top of the merge branch.
- Right before merging, fold those follow-up commits back into a single merge
  commit.

## Merge commit message format

When finalizing the Starbase merge commit, include the merge date as an
ISO 8601 date only (`YYYY-MM-DD`) in the commit message.

Do not include time or timezone.

Example:
- `chore(merge): update starbase (2026-06-18)`

The commit body must include a concise overview of the Starbase changes that
were pulled in (for example: build-system updates, workflow changes, docs
tooling changes, or dependency-management adjustments).

Use this template:

```text
chore(merge): update starbase (<ISO-8601-DATE: YYYY-MM-DD>)

Merge `starbase/main` into this branch and sync Starbase-managed updates.

Overview of Starbase changes pulled in:
- <high-level change area 1>
- <high-level change area 2>
- <high-level change area 3>
- <high-level change area 4>

Conflict resolution applied:
- Kept child-repo version of `<child-owned-file-1>` (`--ours`).
- Kept child-repo version of `<child-owned-file-2>` (`--ours`).
- Took full `<source-of-truth-file-1>` from `starbase/main` (source-of-truth file).
- Took full `<source-of-truth-file-2>` from `starbase/main` (source-of-truth file).
- For this `<library|application>` repo:
  - kept `<agents-template-file-to-delete-1>` deleted,
  - kept `<agents-template-file-to-delete-2>` deleted,
  - kept `AGENTS.md` authoritative and applied relevant updates from `<agents-template-reference-file>`.
```

## Next part

Add conflict resolution playbooks for typical Starbase sync conflicts
(`common.mk`, Makefile targets, and workflow template drift).

## Conflict rule 1: File ownership map

Use the following ownership map when resolving Starbase sync conflicts:

### Always take `starbase/main`

- Files marked in-tree as Starbase source-of-truth files (for example,
  comments like "Should only be edited in the `starbase` repository").
- `.editorconfig` for the shared baseline; the child repository may extend it
  with additional sections, but the Starbase config is authoritative.
- `common.mk` (explicitly marked as Starbase-owned in-tree).
- `.github/workflows/check-renovate.yaml`.
- `.github/workflows/policy.yaml`.
- `.github/workflows/release-publish.yaml`.
- `.github/workflows/tics.yaml`: keep the reusable workflow call, but set
  `with.project` to the child repository name; do not leave the project
  commented out in the shipped PR.
- `.gitignore` for the shared baseline; the child repository may append
  repository-specific ignore entries at the bottom.
- `.pre-commit-config.yaml` for the shared hook set; if the same hook appears
  in both repos, keep the newer revision pin.
- `.readthedocs.yaml`.
- `README.md`.
- Any other shared build or workflow file that is explicitly documented as
  Starbase-managed in this skill or the repository docs.

### Always take the child repository version

- `.github/CODEOWNERS`
- `.github/workflows/qa.yaml`
- `uv.lock`

### Mixed ownership

- `.github/.jira_sync_config.yaml`: keep `settings.components` and
  `settings.jira_project_key` from the child repository; take the rest from
  `starbase/main`.
- `.github/PULL_REQUEST_TEMPLATE.md`: keep Starbase's template content and
  replace only the contribution-guidelines link with the child repository's
  `CONTRIBUTING.md` URL.
- `SECURITY.md`: keep the Starbase comment under `Release cycle`, keep the
  child repository's release-cycle wording, and keep the project-specific
  reporting links from the child repository.
- `docs/**/*.rst`: keep the repository's own documentation pages, including the
  files inside the diataxis directories.
- `docs/**/*.rst`: update any copied Starbase text to the child repository's
  name and purpose; if the landing page is being published, make sure it is not
  excluded from the Sphinx build.
- If the empty-diataxis landing pages are still placeholders, keep them excluded
  from `docs/conf.py`; only un-exclude them when the content is ready to ship.
- `docs/{how-to,explanation,reference,tutorials}`: the directory names are
  Starbase-owned; if they move, move the whole docs tree accordingly.
- For library repositories, delete `docs/release-notes/`.
- For library repositories, delete `.github/README.md`.
- For library repositories, delete `AGENTS.app.md`, `AGENTS.lib.md`, and the
  Starbase scaffold package `starcraft/__init__.py`.
- For library repositories, replace any scaffolded `CONTRIBUTING.md` with a
  short repository-specific guide that matches the actual project name, repo
  URLs, and commands.
- `pyproject.toml`: keep the `[project]` metadata and `[project.scripts]`
  section from the child repository; resolve the later sections separately.
- `pyproject.toml`: keep the entire `[project]` block from the child
  repository.
- `pyproject.toml`: keep all `[dependency-groups]` entries from the child
  repository.
- `pyproject.toml`: merge `tool.uv.constraint-dependencies` by keeping the
  higher version from each side, ordered alphabetically by package name.
- `pyproject.toml`: keep `[build-system]` from the child repository.
- `pyproject.toml`: keep `[tool.setuptools_scm]` from `starbase/main`.
- `pyproject.toml`: treat `tool.pytest.ini_options.markers` as shared; update
  the Starbase-defined markers and append any child-specific markers as needed.
- `pyproject.toml`: keep `[tool.pyright]` from the child repository.
- `pyproject.toml`: keep `[tool.mypy]` from the child repository.
- `pyproject.toml`: any Starbase-side reference to the `starcraft` module is
  child-owned; keep the child repository's module names instead.
- `pyproject.toml`: keep `tool.ruff` from `starbase/main`, except for
  `tool.ruff.src` and `tool.ruff.target-version`; the child repository may add
  values to `tool.ruff.extend-exclude`, `tool.ruff.lint.select`,
  `tool.ruff.lint.ignore`, and `tool.ruff.lint.per-file-ignores`.
- `Makefile`: keep child-owned variables such as `PROJECT`, but include new
  Starbase-added variables and take the Starbase version when it extends an
  existing variable.
- `docs/conf.py`: keep the Starbase docs scaffold, but keep project identity,
  branding, repo URLs, and other child-specific documentation values from the
  child repository. If you publish the diataxis landing pages, remove them from
  `exclude_patterns` so the docs actually build the new content; otherwise keep
  the empty quadrant exclusions in place.
- `.readthedocs.yaml`: keep the Read the Docs build using a separate docs
  virtualenv instead of pointing both the docs venv and the uv project env at
  the same path.
- Branch names for this workflow should start with `work/`.
- `.editorconfig`: keep the Starbase baseline and only retain child-specific
  extensions that do not override the shared defaults.
- `tests/`: keep the child repository versions for everything under `tests/`
  except `tests/integration/test_setuptools.py`, which comes from `starbase/main`.

## Conflict rule 2: AGENTS templates

For repository-specific AGENTS templates:
- keep `AGENTS.md` as the authoritative file,
- keep the template file for the repository type deleted after using it only as
  a reference,
- apply only relevant improvements from the template into `AGENTS.md`.
- when the scaffold ships `AGENTS.md` from Starbase, replace it with the
  repository-specific version derived from the matching template (`AGENTS.lib.md`
  for libraries or `AGENTS.app.md` for applications), then delete both template
  files.

For library repositories:
- use `AGENTS.lib.md` as the source template for `AGENTS.md`,
- keep `AGENTS.app.md` deleted,
- keep `AGENTS.lib.md` deleted after using it only as a template reference.

For application repositories:
- use `AGENTS.app.md` as the source template for `AGENTS.md`,
- keep `AGENTS.lib.md` deleted,
- keep `AGENTS.app.md` deleted after using it only as a template reference.
