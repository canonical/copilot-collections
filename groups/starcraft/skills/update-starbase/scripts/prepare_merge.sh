#!/usr/bin/env bash
# prepare_merge.sh — Automates steps 1-6 of the update-starbase skill workflow.
#
# Usage: prepare_merge.sh [BRANCH_SUFFIX]
#
#   BRANCH_SUFFIX  Optional. Appended to the work branch name.
#                  Defaults to today's date: work/update-starbase-YYYY-MM-DD
#
# The script exits non-zero on any hard failure. It prints a compact,
# machine-parsable key=value block for the agent to act on (see SKILL.md
# for what to do with each STATUS value):
#
#   STATUS=clean|conflicted|already-up-to-date|failed
#   BRANCH=<branch-name>
#   BASE=starbase/main (<commit-short>)
#   CHANGED_FILES:
#   <file1>
#   CONFLICTED_FILES:
#   <file1>
#   PLACEHOLDER_WARNINGS:
#   <file1>:<line>
#   STRUCTURAL_DIFF_FILES:   (clean merges only)
#   <file1>

set -euo pipefail

STARBASE_URL="https://github.com/canonical/starbase.git"
DATE=$(date +%Y-%m-%d)
SUFFIX="${1:-${DATE}}"
BRANCH="work/update-starbase-${SUFFIX}"

# ── Helpers ──────────────────────────────────────────────────────────────────

info()  { printf '\033[1;34m[INFO]\033[0m  %s\n' "$*" >&2; }
ok()    { printf '\033[1;32m[ OK ]\033[0m  %s\n' "$*" >&2; }
warn()  { printf '\033[1;33m[WARN]\033[0m  %s\n' "$*" >&2; }
die()   { printf '\033[1;31m[FAIL]\033[0m  %s\n' "$*" >&2; exit 1; }

# ── Step 1: Confirm safe state ────────────────────────────────────────────────

info "Step 1: Checking working-tree state..."
git --no-pager status --short --branch >&2

DIRTY=$(git status --porcelain)
if [[ -n "$DIRTY" ]]; then
  die "Working tree is not clean. Stash or commit local changes before running this script."
fi
ok "Working tree is clean."

# ── Step 2: Ensure starbase remote ───────────────────────────────────────────

info "Step 2: Configuring 'starbase' remote → ${STARBASE_URL}"
if git remote get-url starbase > /dev/null 2>&1; then
  CURRENT_URL=$(git remote get-url starbase)
  if [[ "$CURRENT_URL" != "$STARBASE_URL" ]]; then
    warn "Remote 'starbase' exists but points to '${CURRENT_URL}'. Updating..."
    git remote set-url starbase "$STARBASE_URL"
  fi
  ok "Remote 'starbase' already exists and is correct."
else
  git remote add starbase "$STARBASE_URL"
  ok "Remote 'starbase' added."
fi

# ── Step 3: Fetch ────────────────────────────────────────────────────────────

info "Step 3: Fetching starbase (--prune)..."
git fetch starbase --prune >&2
ok "Fetch complete."

# ── Step 3b: Bail out early if there's nothing new to sync ──────────────────

if git merge-base --is-ancestor starbase/main HEAD; then
  ok "Already up to date with starbase/main — no new commits to sync."
  echo ""
  echo "STATUS=already-up-to-date"
  exit 0
fi

# ── Step 4: Create work branch ───────────────────────────────────────────────

info "Step 4: Creating branch '${BRANCH}'..."
if git show-ref --verify --quiet "refs/heads/${BRANCH}"; then
  die "Branch '${BRANCH}' already exists. Delete it or pass a different suffix: prepare_merge.sh <suffix>"
fi
git switch -c "$BRANCH" >&2
ok "Switched to new branch '${BRANCH}'."

# ── Step 5-6: Merge and capture state ────────────────────────────────────────

info "Step 5: Merging starbase/main (--no-ff)..."
MERGE_EXIT=0
git merge --no-ff --allow-unrelated-histories starbase/main >&2 || MERGE_EXIT=$?

echo ""  # blank line before the structured output block

# ── Structured output for the agent ──────────────────────────────────────────

if [[ $MERGE_EXIT -eq 0 ]]; then
  # Merge committed: HEAD is now the merge commit, HEAD^1 is the pre-merge
  # tip of the work branch, so this shows exactly what the merge touched.
  # Deleted files are kept (no --diff-filter=d) so they still get a
  # provenance comment; see references/pr_provenance.md.
  CHANGED_FILES=$(git diff --name-only HEAD^1 HEAD)
else
  # Merge stopped with conflicts: no merge commit exists yet, so compare the
  # working tree/index against the pre-merge HEAD instead.
  CHANGED_FILES=$(git diff --name-only HEAD)
fi
CONFLICTED_FILES=$(git --no-pager diff --name-only --diff-filter=U 2>/dev/null || true)

if [[ $MERGE_EXIT -eq 0 ]]; then
  # ── CLEAN MERGE ─────────────────────────────────────────────────────────────
  PLACEHOLDER_LINES=$(echo "$CHANGED_FILES" | xargs -r grep -n -i -E "starcraft|starbase" -- 2>/dev/null | cut -d: -f1,2 || true)

  # Shared and mixed-ownership files from references/file_ownership.md that the
  # merge touched. Keep this list in sync with the ownership map.
  MIXED_OWNERSHIP_FILES=(
    "docs/conf.py"
    "Makefile"
    "pyproject.toml"
    "SECURITY.md"
    ".github/.jira_sync_config.yaml"
    ".github/PULL_REQUEST_TEMPLATE.md"
    ".gitignore"
    ".pre-commit-config.yaml"
    ".readthedocs.yaml"
  )
  STRUCTURAL_DIFF_FILES=$(echo "$CHANGED_FILES" | tr ' ' '\n' \
    | grep -x -F -f <(printf '%s\n' "${MIXED_OWNERSHIP_FILES[@]}") || true)

  cat <<EOF
STATUS=clean
BRANCH=${BRANCH}
BASE=starbase/main ($(git rev-parse --short starbase/main))
CHANGED_FILES:
$(echo "$CHANGED_FILES" | sed 's/^/  /')
EOF

  if [[ -n "$PLACEHOLDER_LINES" ]]; then
    cat <<EOF
PLACEHOLDER_WARNINGS:
$(echo "$PLACEHOLDER_LINES" | sed 's/^/  /')

NOTE: Do not overwrite legitimate Starbase attribution/ownership comments
(see references/file_ownership.md) — only replace true placeholder text.
EOF
  fi

  if [[ -n "$STRUCTURAL_DIFF_FILES" ]]; then
    cat <<EOF
STRUCTURAL_DIFF_FILES:
$(echo "$STRUCTURAL_DIFF_FILES" | sed 's/^/  /')

NOTE: Diff each file above against starbase/main (git diff starbase/main -- <file>).
Confirm all remaining differences are child-owned per references/file_ownership.md.
Check deletions explicitly: git merge does not flag deleted declarations as conflicts.
EOF
  fi

else
  # ── HARD FAILURE vs. CONFLICTED MERGE ───────────────────────────────────────
  # A nonzero exit with no conflicted files means git failed for some other
  # reason (untracked files that would be overwritten, a failing merge hook,
  # etc.), not an ordinary merge conflict — don't send the agent down the
  # conflict-resolution path for an error that doesn't exist.
  if [[ -z "$CONFLICTED_FILES" ]]; then
    git merge --abort 2>/dev/null || true
    cat <<EOF
STATUS=failed
BRANCH=${BRANCH}

git merge exited non-zero (exit ${MERGE_EXIT}) but left no conflicted
files, so this is not an ordinary merge conflict. See the git output
above for the actual error (e.g. untracked files that would be
overwritten, a failing merge hook). The merge has been aborted; fix
the underlying issue, then re-run this script.
EOF
    exit 1
  fi

  # ── CONFLICTED MERGE ────────────────────────────────────────────────────────
  cat <<EOF
STATUS=conflicted
BRANCH=${BRANCH}
BASE=starbase/main ($(git rev-parse --short starbase/main))
CHANGED_FILES:
$(echo "$CHANGED_FILES" | sed 's/^/  /')
CONFLICTED_FILES:
$(echo "$CONFLICTED_FILES" | sed 's/^/  /')

NOTE: Do not overwrite legitimate Starbase attribution/ownership comments
(see references/file_ownership.md) — only replace true placeholder text.
EOF
  exit 1
fi
