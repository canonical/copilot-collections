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

8. Clean up placeholder text in all merged files (both conflicted and cleanly merged):
   Scan all files that were added or modified by the merge for any remaining "Starcraft" or "Starbase" placeholder text:

   ```bash
   git diff --name-only starbase/main...HEAD | xargs grep -i -E "starcraft|starbase"
   ```

   Update any matches found (except external docs/style guide URLs) to use the child repository's name and purpose.

9. Document change provenance on each file:
   For every file added, deleted, or modified by the merge, make review comments on the GitHub PR explaining the provenance of the changes. Additionally, post inline review comments pointing out specific custom changes (e.g., removing a duplicate directive or fixing a type ignore).
   Files that already existed in the child repository and merged cleanly without conflicts or custom changes do not need a comment.
   **Provenance and rationale for manual changes belong exclusively in PR review comments, never as comments inside the source file.** If you catch yourself writing "why a bot changed this" as a `#`/`//` comment in code, stop and move it to a PR review comment instead. This applies just as much to config files like `docs/conf.py`: e.g. explaining *why* only specific `sphinx_toolbox` submodules are loaded (instead of the top-level package) belongs in a PR file-level comment, not a multi-line `#` block above the `extensions` entries.
   The comments must follow these guidelines:
   - **Prefix Template**: Each comment must begin with a robot emoji and a prefix in square brackets announcing that a bot wrote it, along with the model and harness. E.g. `🤖 [BEEP BOOP, A BOT WROTE THIS COMMENT - <model>, <harness>]`.
     Example: `🤖 [BEEP BOOP, A BOT WROTE THIS COMMENT - Gemini 3.5 Flash (High), antigravity]`
   - **Provenance Descriptions**:
     - For new files: `"new file from starbase"`
     - For modified files: `"file updated from starbase"`
     - For renamed or moved files: `"file moved in starbase"`
     - For complex/mixed files (e.g. `uv.lock` or `pyproject.toml`): Provide specific intermediate/complex details (e.g. `"file updated from starbase (child-owned file, regenerated locally based on merged dependencies)"`).
   - **Implementation via GitHub API**:
     - Post file-level comments on the PR using the REST API (`POST /repos/{owner}/{repo}/pulls/{pull_number}/comments`) with the `"subject_type": "file"` parameter so that a specific line number is not required.
     - Post inline line-level review comments for specific code changes (specifying `"line"` and `"side": "RIGHT"`) to highlight specific modifications made (such as resolving duplicate extensions or custom linter ignores).
     - **Handling Rate Limits**: When posting a batch of comments, enforce a delay (e.g., 4-5 seconds) between calls to avoid GitHub's spam rate limiter (`was submitted too quickly`). Implement an automatic backoff/retry (e.g., sleeping 30 seconds upon hitting a rate limit) to guarantee all comments are registered.
   - **Own-invention workarounds require a suggestion, not a direct push**: for
     a change that is neither sourced from `starbase/main` nor an obvious
     conflict resolution — for example, a hand-written workaround like adding
     an `export SPHINX_OPTS := ... -j 1` override to fix a `--fail-on-warning`
     failure caused by a Sphinx extension's parallel-read warning — do not
     push the change directly into the merge commit. Instead, push the merge
     without it, then leave an inline review comment at the relevant location
     using the standard robot-prefix template that explains the problem and
     proposes the fix as an actual GitHub suggestion (a fenced
     ` ```suggestion ` block), so a human reviewer can review and apply it
     explicitly rather than the bot self-approving its own invented fix.

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
- While the PR is still in draft (fixing initial CI failures and addressing
  the first round of review comments), make separate commits for each
  follow-up fix rather than amending; this keeps the history of what changed
  and why easy to review incrementally.
- Squash the follow-up-fix commits back into the single merge commit twice,
  at two distinct points:
  1. Once CI is green and the PR is ready to come out of draft: squash all
     follow-up-fix commits made so far into the original merge commit before
     marking the PR ready for review.
  2. Right before the final merge into the base branch: squash any further
     follow-up commits made during the ready-for-review round (e.g., fixes
     from human reviewers) back into that same single merge commit.
  Between these two squash points, follow-up fixes should again land as
  separate commits, not be squashed continuously.
- **The provenance/documentation rules in "Document change provenance on each
  file" apply for the entire life of the PR, not just the initial merge.**
  Any manual code change made while fixing CI failures or responding to review
  feedback — including one-line bugfixes — must be explained via a PR review
  comment (inline on the changed line, using the same robot-prefix template),
  never as a comment added to the source file itself. Do not add explanatory
  `#`/`//` comments to files to document *why a bot made this change*; source
  comments are only for genuinely non-obvious code, not for change provenance.
- Post each of these follow-up-fix review comments (and remember the
  robot-prefix template) in the same turn you push the corresponding fix —
  don't defer it, and don't wait to be reminded.

## Refreshing a stale merge PR (required when either main has moved on)

If significant time has passed since the merge PR was opened and either
`origin/main` or `starbase/main` has gained new commits, do not layer another
merge commit on top of the existing one. Instead, rebuild the merge commit
from the current heads of both branches while preserving every follow-up-fix
commit already pushed to the PR:

1. `git fetch origin --prune && git fetch starbase --prune` to get both
   branches' latest state.
2. Create a fresh branch from the current `origin/main` (do not reuse the old
   merge base): `git checkout -b <new-branch> origin/main`.
3. `git merge --no-ff --no-commit starbase/main` and resolve conflicts using
   the same file-ownership map and decisions as the original merge. Diff the
   new merge tree against the old merge commit
   (`git diff <new-working-tree> <old-merge-commit> --stat`) to catch any
   conflict-map resolutions, placeholder-text cleanups, or lint-rule fixes
   that the new merge silently skipped (for example, because
   `starbase/main` didn't touch a file that the old merge still needed to
   modify, so git raises no conflict for it at all — reapply those changes
   manually from the old merge commit).
4. Commit the merge using the same commit message template as any other
   Starbase merge (see "Merge commit message format"), updating the date.
5. Cherry-pick every follow-up-fix commit from the old branch, in order, onto
   the new merge commit: `git cherry-pick <fix-1> <fix-2> ...`. These commits
   must be preserved, not redone from scratch or squashed away.
6. Re-run the pre-PR validation commands (`make format`, `make lint`,
   `make docs`; `make test-fast` at your discretion) against the rebuilt
   branch before pushing.
7. Force-push the rebuilt branch to the existing PR branch (use
   `--force-with-lease` against the branch's current remote tip for safety).
8. Update the PR title's date to match the new merge date (see "Merge commit
   message format" for the title/subject format). `gh pr edit --title` can
   spuriously fail on repos with legacy Projects (classic) boards; if it
   errors, fall back to
   `gh api repos/{owner}/{repo}/pulls/{number} -X PATCH -f title="..."` and
   confirm the new title with a follow-up `gh pr view --json title`.
9. Post a PR comment (standard robot-prefix template) noting that history was
   rewritten and force-pushed, and summarizing what changed on each side
   (new commits pulled in from `origin/main` and/or `starbase/main`) and
   confirming the follow-up-fix commits were preserved.

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
- `.github/workflows/security-scan.yaml`: keep the osv-scanner config pointing
  at the root `osv-scanner.toml`, not a nested `source/` path.
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
- Whenever a Starbase-driven rename or move deletes a documentation file or
  directory that existed before the merge (for example
  `docs/how-to-guides/` → `docs/how-to/`), add a matching entry to
  `docs/redirects.txt` (using the repository's existing redirect mechanism,
  e.g. `sphinx-rerediraffe`) so old links keep resolving. Confirm with
  `make docs` that the build reports `(good) <old path> --> <new path>` for
  each added redirect. **A directory-level redirect (with
  `rediraffe_dir_only`) only redirects that directory's own index page, not
  the individual files that used to live inside it** — add one explicit
  redirect entry per moved file as well (e.g. both
  `"how-to-guides" "how-to"` and `"how-to-guides/add_repo" "how-to/add_repo"`)
  and confirm each one individually reports `(good) ...` in the `make docs`
  output; do not assume the directory entry alone covers its contents.
- When a moved/renamed file lands via delete+add rather than a clean git
  rename (so the diff doesn't show the content as untouched), diff the old
  and new file contents directly and compare the new file against sibling
  pages that already follow the child repository's conventions (for example,
  other `docs/*/index.rst` files). Reconcile any stale conventions the move
  carried over (e.g. an old `toctree` option like `:maxdepth:` where sibling
  pages now use `:hidden:`) rather than assuming the moved file is
  already up to date.
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
- `pyproject.toml`: the `docs-sphinx-stack` dependency group (and its list of
  active/commented-out packages) is fully owned by `starbase/main`; take it
  verbatim, including which entries are commented out. Do not add, remove, or
  uncomment entries in this group to suit the child repository — any
  child-specific docs extensions belong in the `docs` group instead, alongside
  the `{ include-group = "docs-sphinx-stack" }` reference. If a conflict
  arises here, prefer starbase's content and regenerate `uv.lock`.
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
  existing variable. Use it to set the child repo's docs venv default so docs
  install into a separate environment from the main `uv` project venv.
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
- `tests/`: keep the child repository versions for everything under `tests/`.
  Do not add `tests/integration/test_setuptools.py` from `starbase/main`; it is
  a Starbase-scaffold-only test and is not needed in child repositories, even
  though shared fixtures it relies on (e.g. `project_main_module`) may
  legitimately live in the child's `conftest.py` for other tests.

## Conflict rule 2: Type annotations

After resolving conflicts, check for Python type annotation updates needed:
- If Starbase imports change (e.g., removing `Tuple`, `Union` from typing imports),
  update the child repository's code to use modern Python 3.10+ syntax:
  - Replace `Tuple[X, Y]` with `tuple[X, Y]`
  - Replace `Union[X, Y]` with `X | Y`
  - Replace `Dict[K, V]` with `dict[K, V]`
  - Replace `List[X]` with `list[X]`
- These changes are safe for Python 3.9+ and improve code readability.
- Run `ruff check --fix` and `ruff format` to auto-fix these issues.

## Conflict rule 3: AGENTS templates

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
