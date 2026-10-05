# Manual Merge Steps (fallback)

Use these steps if `scripts/prepare_merge.sh` cannot be run directly
(e.g. no shell access, restricted environment, or debugging a script failure).
They are the exact equivalent of what the script does.

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

4. Check whether there's anything new to sync — stop here (without creating
   a work branch) if `starbase/main` has no commits that aren't already in
   `HEAD`:

   ```bash
   git merge-base --is-ancestor starbase/main HEAD && echo "Already up to date with starbase/main"
   ```

   If that prints the message, there is nothing to merge and no PR is
   needed; stop before creating a branch.

5. Create a work branch before starting the merge (match `prepare_merge.sh`'s
   naming so both paths are consistent: `work/update-starbase-YYYY-MM-DD`,
   or append a custom suffix instead of the date):

   ```bash
   git switch -c work/update-starbase-YYYY-MM-DD
   ```

6. Merge from Starbase main into the current branch (`--allow-unrelated-histories`
   is required for a repository's first-ever Starbase sync, and is a safe
   no-op on repositories that already share history with Starbase):

   ```bash
   git merge --no-ff --allow-unrelated-histories starbase/main
   ```

7. Capture merge state:
   - If merge succeeds, continue to project checks.
   - If merge conflicts, stop and report conflicted files:

   ```bash
   git --no-pager status --short
   ```

   Then consult [`file_ownership.md`](file_ownership.md) to resolve each conflict.
