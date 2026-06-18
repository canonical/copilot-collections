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

4. Merge from Starbase main into the current branch:

   ```bash
   git merge --no-ff starbase/main
   ```

5. Capture merge state:
   - If merge succeeds, continue to project checks.
   - If merge conflicts, stop and report conflicted files:

   ```bash
   git --no-pager status --short
   ```

## Output

Report one of:
- `merge-clean`: Starbase merged with no conflicts.
- `merge-conflicted`: merge stopped with conflicts, including the file list from `git status --short`.

## Merge commit message format

When finalizing the Starbase merge commit, include the merge date in ISO 8601
format in the commit message.

Example:
- `chore(merge): update starbase (2026-06-18)`

The commit body must include a concise overview of the Starbase changes that
were pulled in (for example: build-system updates, workflow changes, docs
tooling changes, or dependency-management adjustments).

Use this template:

```text
chore(merge): update starbase (<ISO-8601-DATETIME>)

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

## Conflict rule 1: Starbase source-of-truth marker

If a conflicted file contains a comment stating Starbase is the source of
truth (for example: "Should only be edited in the `starbase` repository"),
resolve the conflict by taking the full file content from `starbase/main`.

Do not perform line-by-line reconciliation for those files.

## Conflict rule 2: CODEOWNERS belongs to the child repository

Always resolve `.github/CODEOWNERS` by taking the child repository version
(`--ours` in the merge), not `starbase/main`.

## Conflict rule 3: qa workflow belongs to the child repository

Always resolve `.github/workflows/qa.yaml` by taking the child repository
version (`--ours` in the merge), not `starbase/main`.

## Conflict rule 4: AGENTS templates in library repositories

For library repositories:
- keep `AGENTS.app.md` deleted,
- keep `AGENTS.lib.md` deleted after using it only as a template reference,
- keep `AGENTS.md` as the authoritative file and apply only relevant
  library-template improvements from `AGENTS.lib.md`.

## Conflict rule 5: AGENTS templates in application repositories

For application repositories:
- keep `AGENTS.lib.md` deleted,
- keep `AGENTS.app.md` deleted after using it only as a template reference,
- keep `AGENTS.md` as the authoritative file and apply only relevant
  application-template improvements from `AGENTS.app.md`.
