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
  append repository-specific ignore entries at the bottom. **Don't silently
  remove child entries that look redundant with the shared baseline** — a
  reviewer may know of a real (if undocumented) reason a repo-specific entry
  exists (e.g. files generated only by running that repo's own scripts). If
  an entry looks removable, keep it and add a short comment marking it as a
  repository-specific addition instead of deleting it; only remove an entry
  outright when you have positive confirmation it's obsolete (e.g. `git
  blame`/history showing it's unused, or explicit reviewer confirmation).
- `.pre-commit-config.yaml` for the shared hook set; if the same hook appears
  in both repos, keep the newer revision pin. **Never downgrade a hook**: for
  every hook present in both the child repo's current config and Starbase's,
  explicitly compare the `rev` (or version) pins before merging — don't
  assume Starbase's value is always newer just because it's the sync source.
  If Starbase's pin for a hook is actually older than the child's current
  pin, keep the child's newer pin for that hook and note the exception in the
  merge commit message (see "Conflict resolution applied" in the merge commit
  message template); this is a case where the "always take starbase/main"
  default is overridden by a concrete version comparison, not by reviewer
  preference. As part of pre-PR validation, diff the resulting
  `.pre-commit-config.yaml` against both source files' hook lists to confirm
  no hook's version regressed.
- `.readthedocs.yaml`.
- `README.md`.
- Any other shared build or workflow file that is explicitly documented as
  Starbase-managed in this skill or the repository docs.

### Always take the child repository version

- `.github/CODEOWNERS`
- `.github/workflows/qa.yaml`
- `uv.lock`

### Mixed ownership

In mixed-ownership files, resolve per declaration rather than per section. Starbase owns structure and syntax (including upstream deletions and commented-out scaffolding); the child repository only provides values. Verify with:

```bash
git diff starbase/main -- <mixed-ownership-file>
```

Check deletions explicitly: when Starbase removes a declaration, `git merge` raises no conflict marker and placeholder greps cannot detect the omission, leaving stale lines in place. Every surviving difference must map to an allowed child-owned value below.

- `.github/.jira_sync_config.yaml`: keep `settings.components` and
  `settings.jira_project_key` from the child repository; take the rest from
  `starbase/main`.
- `.github/PULL_REQUEST_TEMPLATE.md`: keep Starbase's template content and
  replace only the contribution-guidelines link with the child repository's
  `CONTRIBUTING.md` URL.
- `SECURITY.md`: keep the Starbase comment under `Release cycle`, keep the
  child repository's release-cycle wording, and keep the project-specific
  reporting links from the child repository.
- `docs/.sphinx/` → `docs/_dev/` (or any similar Starbase docs-tooling
  directory rename/consolidation): take the new directory from
  `starbase/main`, then delete the old directory outright — do not leave it
  in place alongside the new one. Search the repo for remaining references
  to the old path (`Makefile`, `docs/conf.py`, `.readthedocs.yaml`, CI
  workflows, `tox.ini`/`noxfile.py`, etc.) and update or remove each one; a
  clean `grep` for the old directory name across the repo should return
  nothing once the migration is finished.
- `docs/**/*.rst`: keep the repository's own documentation pages, including the
  files inside the diataxis directories. Update any copied Starbase text to the
  child repository's name and purpose; if the landing page is being published,
  make sure it is not excluded from the Sphinx build.
- If the empty-diataxis landing pages are still placeholders, keep them excluded
  from `docs/conf.py`; only un-exclude them when the content is ready to ship.
- `docs/{how-to,explanation,reference,tutorials}`: the directory names are
  Starbase-owned; if they move, move the whole docs tree accordingly.
- `docs/.custom_wordlist.txt` (or equivalent global spelling/vale wordlist):
  take the union of both sides' entries by default, but **only add terms
  that are genuinely global** — safe to accept everywhere in the docs, such
  as product/project names (`Starcraft`, the child repo's own name) or other
  terms that should never be flagged regardless of context. For a narrow,
  one-off term that only applies to a specific page or sentence, use the
  docs tooling's scoped/inline ignore mechanism instead (e.g. a
  `vale-ignore`-style comment at the point of use) rather than adding it to
  the global wordlist. If it's unclear whether a file like this should be
  reclassified as fully Starbase-owned going forward (so that future
  additions come only from `starbase/main` and get expressed as scoped
  ignores in child repos), raise that as an explicit question for the
  reviewer/maintainer rather than deciding unilaterally — this changes the
  file's entry in this ownership map and should be confirmed before treating
  it as settled.
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
- File-deletion rules for library repositories (`docs/release-notes/`,
  `.github/README.md`, `starcraft/__init__.py`, AGENTS templates) live in
  "Conflict rule 1b: Files that must be deleted" below.
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
- `docs/conf.py`: keep the Starbase docs scaffold; substitute child-owned values:
  - **Starbase-owned**: `version`/`release` logic (including commented-out blocks and Read the Docs branch logic), `copyright` format, `html_title` (remove if deleted upstream), `html_favicon`, `html_extra_path`, and new upstream `exclude_patterns` entries.
  - **Child-owned values**: `project`, `author`, `ogp_*`, `html_context` URLs, `llms_txt_description`, license name, and quadrant exclusion toggles in `exclude_patterns`.
  - **Copyright start year**: derive from first commit (`git log --reverse --format=%ad --date=format:%Y | head -1`); if history is shallow, squashed, or the year looks wrong, ask the reviewer.
- `.readthedocs.yaml`: keep the Read the Docs build using a separate docs
  virtualenv instead of pointing both the docs venv and the uv project env at
  the same path.
- Branch names for this workflow should start with `work/`.
- `tests/`: keep the child repository versions for everything under `tests/`.
  Do not add `tests/integration/test_setuptools.py` from `starbase/main`; it is
  a Starbase-scaffold-only test and is not needed in child repositories, even
  though shared fixtures it relies on (e.g. `project_main_module`) may
  legitimately live in the child's `conftest.py` for other tests.

## Conflict rule 1b: Files that must be deleted

These deletions never raise a git conflict, so check this list explicitly on
every merge — clean or conflicted — even if the files never appear in the
diff:

- For library repositories, delete `docs/release-notes/`,
  `.github/README.md`, and the Starbase scaffold package
  `starcraft/__init__.py`.
- `AGENTS.lib.md`/`AGENTS.app.md`: delete per repository type, per
  "Conflict rule 3: AGENTS templates" below.
- Any old directory superseded by a Starbase reorg (e.g. `docs/.sphinx/` →
  `docs/_dev/`, see "Mixed ownership" above): delete the old directory and
  its dangling references.

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

Preserving template structure while filling it in:
- Preserve the source template's structure and formatting (tables, headings,
  list types) when filling in TODOs and repo-specific details. Only change
  formatting if the content genuinely cannot fit in the existing structure
  (e.g. a table column is too narrow for a required value), and if so, explain
  why in the merge commit message.
- When the current repository's own package must be removed from a list of
  dependencies (e.g. a self-reference in a "Craft apps and libraries" table),
  do this as a targeted row/item removal — not as a side effect of
  reformatting the surrounding list or table into a different structure.
- Before finalizing `AGENTS.md`, diff its structure against the source
  template (headings, tables vs. prose, list types) to confirm only intended
  repo-specific substitutions and deletions were made. Flag any unintended
  structural drift (e.g. a table collapsed into a flat list) for review rather
  than merging it silently.
