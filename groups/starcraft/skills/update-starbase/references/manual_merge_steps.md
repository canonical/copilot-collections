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

   Then consult [`file_ownership.md`](file_ownership.md) to resolve each conflict.
