# Refreshing a Stale Merge PR

Use these steps when significant time has passed since the merge PR was opened and either `origin/main` or `starbase/main` has gained new commits.

Do not layer another merge commit on top of an existing one. Instead, rebuild the merge commit from the current heads of both branches while preserving every follow-up-fix commit already pushed to the PR:

1. **Fetch latest state**:
   ```bash
   git fetch origin --prune && git fetch starbase --prune
   ```

2. **Branch from fresh `origin/main`** (do not reuse the old merge base):
   ```bash
   git checkout -b <new-branch> origin/main
   ```

3. **Re-merge `starbase/main` without committing**:
   ```bash
   git merge --no-ff --no-commit starbase/main
   ```
   Resolve conflicts using the file ownership map in [`file_ownership.md`](file_ownership.md).
   
   Diff the new working tree against the old merge commit to catch any conflict resolutions, placeholder cleanups, or lint fixes that git may have silently skipped:
   ```bash
   git diff <old-merge-commit>
   # or with --stat for a summary:
   git diff <old-merge-commit> --stat
   ```
   Reapply any missing changes manually from the old merge commit.

4. **Commit the rebuild**:
   Use the standard Starbase merge commit message template (see `SKILL.md`), updating the date to today's date (`YYYY-MM-DD`).

5. **Cherry-pick follow-up fixes**:
   Replay every follow-up-fix commit from the old branch in chronological order onto the new merge commit:
   ```bash
   git cherry-pick <fix-1> <fix-2> ...
   ```
   These commits must be preserved, not redone from scratch or squashed away.

6. **Validate**:
   Re-run pre-PR validation against the rebuilt branch before pushing:
   ```bash
   make format && make lint && make docs
   # make test-fast (at your discretion)
   ```

7. **Force-push**:
   Push the rebuilt branch to the existing PR branch safely using `--force-with-lease`:
   ```bash
   git push --force-with-lease origin <new-branch>:<pr-branch>
   ```

8. **Update PR title**:
   Update the PR title date to match the new merge date (`chore(merge): update starbase (YYYY-MM-DD)`):
   ```bash
   gh pr edit --title "chore(merge): update starbase (YYYY-MM-DD)"
   ```
   *Note: If `gh pr edit` fails on repos with legacy classic projects, fall back to:*
   ```bash
   gh api repos/{owner}/{repo}/pulls/{number} -X PATCH -f title="chore(merge): update starbase (YYYY-MM-DD)"
   gh pr view --json title
   ```

9. **Notify in PR comment**:
   Post a PR comment using the standard robot-prefix template:
   - Note that history was rewritten and force-pushed.
   - Summarize what changed on each side (new commits pulled from `origin/main` and/or `starbase/main`).
   - Confirm all follow-up-fix commits were preserved.
