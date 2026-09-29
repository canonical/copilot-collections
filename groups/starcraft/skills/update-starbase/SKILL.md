---
name: update-starbase
description: Syncs Starbase-managed project files by adding the canonical/starbase remote and merging starbase/main into the current branch. Use when updating common.mk and related shared Starcraft build/CI conventions.
---

# Update Starbase

## Phase 1: Merge Starbase

Run the preparation script from the root of the child repository:

```bash
bash <path-to-skill>/scripts/prepare_merge.sh [BRANCH_SUFFIX]
```

- `BRANCH_SUFFIX` is optional; defaults to today's date
  (`work/update-starbase-YYYY-MM-DD`).
- The script handles steps 1–6: safe-state check, remote setup, fetch,
  work-branch creation, merge, and conflict detection.
- It prints a compact `STATUS=...` block (`BRANCH`, `BASE`, `CHANGED_FILES`,
  and — when relevant — `CONFLICTED_FILES` and `PLACEHOLDER_WARNINGS`) for
  one of four `STATUS` values, then continue with the matching step below:
  - `STATUS=clean` (exit 0): merge succeeded with no conflicts. Continue to
    Phase 2.
  - `STATUS=conflicted` (exit non-zero): merge stopped with conflicts.
    Resolve each file in `CONFLICTED_FILES` per
    [`references/file_ownership.md`](references/file_ownership.md), then
    `git add` the resolved files and `git merge --continue` before
    continuing to Phase 2.
  - `STATUS=already-up-to-date` (exit 0): `starbase/main` has no commits
    that aren't already in the branch. No work branch was created — there
    is nothing to sync or open a PR for. Stop here and report this to the
    user.
  - `STATUS=failed` (exit non-zero): `git merge` failed for a reason other
    than an ordinary conflict (e.g. untracked files that would be
    overwritten, a failing merge hook). The merge was aborted; fix the
    underlying issue from the git output above the status block, then
    re-run the script.

If the script cannot be run, follow [`references/manual_merge_steps.md`](references/manual_merge_steps.md) instead.

Report one of: `merge-clean`, `merge-conflicted` (with the conflicted file
list), `already-up-to-date`, or `merge-failed`.


### Conflict resolution

When resolving merge conflicts, consult
[`references/file_ownership.md`](references/file_ownership.md) for the
complete ownership map and decision rules, including:

- **Conflict rule 1** – File ownership map (always take starbase, always take
  child, and mixed-ownership rules by file/section).
- **Conflict rule 1b** – Files that must be deleted; check every merge,
  clean or conflicted, since these deletions never raise a conflict.
- **Conflict rule 2** – Python type annotation modernisation (when to apply
  `X | Y`, `tuple[X, Y]`, etc., and Python version caveats).
- **Conflict rule 3** – AGENTS template handling (library vs. application
  repositories).

If a reviewer's PR feedback asks for something that contradicts one of these
rules (or any other rule in this skill), see
[`references/reviewer_feedback_conflicts.md`](references/reviewer_feedback_conflicts.md)
for how to resolve it — don't silently follow one side without recording why.

### Merge commit message format

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

## Phase 2: Validation & Cleanup

1. Run the deletion checklist (required, every merge):
   Before validation, work through
   [`references/file_ownership.md`](references/file_ownership.md)'s
   "Conflict rule 1b" — it doesn't show up as a conflict, so this is the
   only point it gets caught.
2. Verify mixed-ownership files and clean up placeholders:
   - **Structural diff**: For any modified mixed-ownership file, diff against Starbase (`git diff starbase/main -- <file>`) and verify only child-owned values differ per [`references/file_ownership.md`](references/file_ownership.md).
   - **Placeholder grep**: Scan for residual `starcraft|starbase` placeholder text:

     ```bash
     git diff --name-only --diff-filter=d HEAD^1 HEAD | xargs -r grep -i -E "starcraft|starbase"
     ```

     Update any matches found (except external docs/style guide URLs) to use the child repository's name/purpose. Do **not** touch legitimate Starbase-ownership comments. Explicitly disposition every hit (fix or note as legitimate attribution in the merge commit message).

3. Run pre-PR validation (required):

   Before creating a PR, ensure repository checks pass:

   ```bash
   make format
   make lint
   make docs
   make test-fast
   ```

   `make lint` builds the docs as part of linting, but run `make docs` too so
   docs-specific failures are caught and reported clearly on their own, not
   just as a side effect of the lint target.

   `make format` can rewrite doc-referenced code snippets (e.g. quote style)
   pulled in via `include`/`literalinclude` (or equivalent) directives
   without failing `make docs`. After formatting, verify each such directive
   still resolves to the in-sync excerpt the docs page expects, adjusting
   anchors/line numbers if formatting shifted them.

   Do not create the PR until these commands complete successfully.

4. Check every file changed by the merge for preparation PR candidates
   (required):

   Some fixes discovered while merging or validating are pre-existing or
   unrelated issues (e.g. latent bugs, mechanical formatting diffs, new
   default-enabled tooling, or large net-new template files). Bundling these
   into the merge PR obscures the merge diff. This is a mandatory audit, not
   a reactive check — do not wait for a reviewer to flag it.

   When you find one, split it into a separate draft preparation PR against
   `origin/main` before finalizing the merge — using its own git worktree,
   and optionally delegated to a background subagent, so it doesn't block
   the main merge work. Consult
   [`references/preparation_prs.md`](references/preparation_prs.md) for
   trigger criteria, the worktree/subagent workflow, stacked PR workflows,
   lifecycle requirements (draft-only, operator promotion), and provenance
   link rules.

## Phase 3: Pull Request Creation

When opening the PR, apply the label:
- `PR: Merge`

Document change provenance on each file:
For every file added, deleted, or modified by the merge, post GitHub PR
review comments explaining the provenance of the changes. Consult
[`references/pr_provenance.md`](references/pr_provenance.md) for the
comment format, prefix template, provenance-description conventions, the
GitHub API details (rate limiting, `subject_type: file`), and the rules
for suggestion-only own-invention workarounds and precedent citations.

Open the PR as a draft, request a Copilot review while it is still draft
(`gh pr create --draft --reviewer "copilot-pull-request-reviewer[bot]" ...`,
or `gh pr edit <PR_NUMBER> --add-reviewer
"copilot-pull-request-reviewer[bot]"` on an already-open PR), and keep
iterating until the review is clean enough for the operator to mark it
ready.

## Phase 4: Review, Squashing & Promotion

- Check the PR's CI status before handing it off.
- If a reviewer's requested change contradicts a rule in this skill (the
  file-ownership map, a conflict-resolution rule, or any other documented
  rule), see
  [`references/reviewer_feedback_conflicts.md`](references/reviewer_feedback_conflicts.md)
  before acting on it.
- If CI is still running or likely to fail, start a background agent to watch
  the PR checks and report failures so they can be fixed promptly.
- You do not need to wait for the full matrix to finish before fixing failures
  in jobs that are already failing or have enough signal to act on.
- While the PR is still in draft (fixing initial CI failures and addressing
  the first round of review comments), make separate commits for each
  follow-up fix rather than amending; this keeps the history of what changed
  and why easy to review incrementally.
- If significant time has passed since the merge PR was opened and either
  `origin/main` or `starbase/main` has gained new commits (including
  "GitHub reports conflicts with `main`"), do not layer another merge commit
  on top of the existing one. Follow
  [`references/refresh_stale_pr.md`](references/refresh_stale_pr.md) to
  rebuild the merge commit and preserve all existing follow-up commits.
- Squash the follow-up-fix commits back into the single merge commit twice,
  at two distinct points:
  1. Once CI is green and the PR is ready to come out of draft: squash all
     follow-up-fix commits made so far into the original merge commit, then
     send the operator a message with the draft PR URL and a brief summary
     (what was merged, any conflicts resolved, any custom changes made) and
     stop. **The agent must never mark any PR ready for review itself** —
     regardless of harness type (interactive or non-interactive) — only the
     operator takes a PR out of draft. Leave promoting the PR to the
     operator.
  2. Right before the final merge into the base branch: squash any further
     follow-up commits made during the ready-for-review round (e.g., fixes
     from human reviewers) back into that same single merge commit.
  Between these two squash points, follow-up fixes should again land as
  separate commits, not be squashed continuously.
  Use this non-destructive recipe for each squash (a plain `git rebase -i`
  can drop the merge commit's second parent or flatten the history, since
  the branch's first commit is itself a merge commit):
  ```bash
  # Find the merge commit created by the sync (its only merge commit).
  MERGE_HASH=$(git log --merges -n 1 --format=%H)

  # Soft-reset to it: this keeps every follow-up-fix diff staged, without
  # touching the merge commit's parents.
  git reset --soft "$MERGE_HASH"

  # Fold the staged diffs into the merge commit, keeping its message/parents.
  git commit --amend --no-edit

  # Push the rewritten branch.
  git push --force-with-lease origin <branch>
  ```
- **The provenance/documentation rules for follow-up fixes are documented in
  [`references/pr_provenance.md`](references/pr_provenance.md)** — they
  apply for the entire life of the PR, not just the initial merge, and
  every follow-up-fix review comment must be posted in the same turn you
  push the corresponding fix.
