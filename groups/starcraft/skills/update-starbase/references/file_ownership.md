# File Ownership Map and Conflict Resolution Rules

Use this reference when resolving conflicts during a Starbase sync merge.

## Conflict rule 1: File ownership map

### Always take `starbase/main`

- Files marked in-tree as Starbase source-of-truth files (for example,
  comments like "Should only be edited in the `starbase` repository").
- `.editorconfig`: the shared baseline is Starbase-owned; the child repository
  may append additional sections, but must not override the shared defaults.
- `common.mk` (explicitly marked as Starbase-owned in-tree).
- `.github/workflows/check-renovate.yaml`.
- `.github/workflows/policy.yaml`.
- `.github/workflows/release-publish.yaml`.
- `.github/workflows/tics.yaml`: keep the reusable workflow call, but set
  `with.project` to the child repository name; do not leave the project
  commented out in the shipped PR.
- `.github/workflows/security-scan.yaml`: keep the osv-scanner config pointing
  at the root `osv-scanner.toml`, not a nested `source/` path.
- `.gitignore`: the shared baseline is Starbase-owned; the child repository may
  append repository-specific ignore entries at the bottom.
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
  files inside the diataxis directories. Update any copied Starbase text to the
  child repository's name and purpose; if the landing page is being published,
  make sure it is not excluded from the Sphinx build.
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
- `pyproject.toml`:
  - Keep the entire `[project]` block (including `[project.scripts]` and the
    `license` key) from the child repository.
  - Keep all `[dependency-groups]` entries from the child repository.
  - The `docs-sphinx-stack` dependency group (and its list of
    active/commented-out packages) is fully owned by `starbase/main`; take it
    verbatim, including which entries are commented out. Do not add, remove, or
    uncomment entries in this group to suit the child repository — any
    child-specific docs extensions belong in the `docs` group instead,
    alongside the `{ include-group = "docs-sphinx-stack" }` reference.
    If a conflict arises here, prefer starbase's content and regenerate
    `uv.lock`.
  - Merge `tool.uv.constraint-dependencies` by keeping the higher version from
    each side, ordered alphabetically by package name.
  - Keep `[build-system]` from the child repository.
  - Keep `[tool.setuptools_scm]` from `starbase/main`.
  - Treat `tool.pytest.ini_options.markers` as shared; update the
    Starbase-defined markers and append any child-specific markers as needed.
  - Keep `[tool.pyright]` from the child repository.
  - Keep `[tool.mypy]` from the child repository.
  - Any Starbase-side reference to the `starcraft` module is child-owned; keep
    the child repository's module names instead.
  - Keep `tool.ruff` from `starbase/main`, except for `tool.ruff.src` and
    `tool.ruff.target-version`; the child repository may add values to
    `tool.ruff.extend-exclude`, `tool.ruff.lint.select`,
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
- The `X | Y` union syntax requires `from __future__ import annotations` in any
  module that must run on Python 3.9 (it is available natively at runtime from
  Python 3.10+). Verify the child project's minimum Python version before
  relying on it at runtime.
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
