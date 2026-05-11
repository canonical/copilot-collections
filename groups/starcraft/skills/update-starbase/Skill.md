---
name: update-starbase
description: Update Starbase for this repository
---

# Merge latest Starbase commit

Merge the latest commit from the `starbase` remote (`canonical/starbase`) into this repository (`canonical/craft-parts`).

## Context

`canonical/starbase` is a shared scaffold/base repository for the Starcraft team. It contains common build tooling (`common.mk`, `Makefile`), CI workflows, linting configs, documentation templates, and test infrastructure. craft-parts tracks it as a git remote named `starbase` and periodically merges changes from `starbase/main`.

The `common.mk` file states it should only be edited in the `starbase` repository.

## Workflow

### 1. Ensure the starbase remote exists

Check that the `starbase` remote is configured:

```bash
git remote get-url starbase
```

If the remote does not exist, add it:

```bash
git remote add starbase git@github.com:canonical/starbase.git
```

### 2. Fetch the latest starbase changes

```bash
git fetch starbase
```

### 3. Identify the merge base and new commits

Find the current merge base between `main` and `starbase/main`:

```bash
git merge-base main starbase/main
```

List the new commits since the last merge:

```bash
git log --oneline <merge-base>..starbase/main
```

If there are no new commits, stop and inform the user that craft-parts is already up to date with starbase.

### 4. Create a working branch

Create a new branch from `main` for the merge:

```bash
git switch -c work/merge-starbase main
```

### 5. Merge starbase/main

Merge `starbase/main` into the working branch. Use `--allow-unrelated-histories` since the trees may appear unrelated:

```bash
git merge starbase/main --allow-unrelated-histories
```

### 6. Resolve conflicts

If the merge produces conflicts, resolve them following these rules:

- **`common.mk`**: Accept the starbase version. This file should only be edited in starbase.
- **`Makefile`**: Prefer the starbase version for shared targets, but preserve any craft-parts-specific targets or overrides.
- **`pyproject.toml`**: Keep the craft-parts version for project-specific settings. In particular, do **not** merge starbase's auto-find package configuration — craft-parts intentionally uses a manual `[tool.setuptools.package-dir]` with two packages (`craft_parts` and `craft_parts_docs`). For shared tool configs (ruff, mypy, codespell, etc.), prefer the starbase version.
- **`.pre-commit-config.yaml`**, **`.github/workflows/`**: Prefer the starbase version, but preserve craft-parts-specific workflows or hooks.
- **`uv.lock`**: After resolving all other conflicts, regenerate by running `uv lock`.
- **`docs/`**: Prefer the starbase version for templates and static assets. Preserve craft-parts-specific content pages.
- **`tests/`**: Prefer the starbase version for shared test infrastructure (e.g. `conftest.py` fixtures from starbase). Preserve craft-parts-specific tests.
- **Other files**: Use best judgment. When in doubt, ask the user.

After resolving conflicts, stage the files and complete the merge:

```bash
git add -A
git merge --continue
```

### 7. Replace Starcraft/Starbase references with the project name

Files brought in from starbase may contain generic "Starcraft" or "Starbase" references that should be replaced with "Craft Parts" (the name of this project). Search for these in newly added or modified documentation files:

```bash
git diff --name-only HEAD~1 -- docs/ | xargs grep -l 'Starcraft\|Starbase'
```

Replace occurrences contextually:

- "Starcraft" referring to the project → "Craft Parts"
- "Starbase" referring to the project → "Craft Parts"
- Do **not** replace references that are specifically about the Starcraft **team**, the `starbase` **repository**, or intersphinx/cross-references to other Starcraft projects (e.g. `:external+starflow:ref:`).
- Do **not** replace occurrences in `common.mk` (that file belongs to starbase).
- Do **not** replace occurrences in test data (e.g. `org.starcraft` Java package names).

Stage and amend the merge commit after making these replacements.

### 8. Verify the result

Run a quick check to make sure the build isn't broken:

```bash
make lint
make test
```

If tests or linting fail due to the merge, fix the issues before proceeding.

### 9. Inform the user

Tell the user:

- Which starbase/main commit was merged (SHA and subject)
- How many commits were included in the merge
- Whether there were conflicts and how they were resolved
- Suggest the user push the branch and open a PR
