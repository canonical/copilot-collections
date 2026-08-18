#!/usr/bin/env bash
# prepare_merge.sh — Automates steps 1-6 of the update-starbase skill workflow.
#
# Usage: prepare_merge.sh [BRANCH_SUFFIX]
#
#   BRANCH_SUFFIX  Optional. Appended to the work branch name.
#                  Defaults to today's date: work/update-starbase-YYYY-MM-DD
#
# The script exits non-zero on any hard failure. On success it prints a
# structured "NEXT STEPS" block for the agent to act on.

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
git merge --no-ff starbase/main >&2 || MERGE_EXIT=$?

echo ""  # blank line before the structured output block

# ── Structured output for the agent ──────────────────────────────────────────

CHANGED_FILES=$(git diff --name-only --diff-filter=d starbase/main...HEAD)
CONFLICTED_FILES=$(git --no-pager diff --name-only --diff-filter=U 2>/dev/null || true)

if [[ $MERGE_EXIT -eq 0 ]]; then
  # ── CLEAN MERGE ─────────────────────────────────────────────────────────────
  PLACEHOLDER_HITS=$(echo "$CHANGED_FILES" | xargs -r grep -li -E "starcraft|starbase" 2>/dev/null || true)

  cat <<EOF
════════════════════════════════════════════════════════════
MERGE RESULT: merge-clean
Branch:       ${BRANCH}
Merged from:  starbase/main → $(git rev-parse --short starbase/main)
════════════════════════════════════════════════════════════

CHANGED FILES ($(echo "$CHANGED_FILES" | grep -c . || echo 0)):
$(echo "$CHANGED_FILES" | sed 's/^/  /')

EOF

  if [[ -n "$PLACEHOLDER_HITS" ]]; then
    cat <<EOF
⚠️  PLACEHOLDER TEXT DETECTED in:
$(echo "$PLACEHOLDER_HITS" | sed 's/^/  /')

  Run to confirm matches:
    git diff --name-only --diff-filter=d starbase/main...HEAD | xargs -r grep -i -E "starcraft|starbase"

  Update any matches (except external URLs) to use this repo's name/purpose.

EOF
  else
    echo "✅  No \"Starcraft\"/\"Starbase\" placeholder text found in changed files."
    echo ""
  fi

  cat <<EOF
NEXT STEPS FOR THE AGENT
─────────────────────────────────────────────────────────────
1. Scan the changed files above for placeholder text (already
   summarised above) and update any matches to this repo's identity.

2. Run pre-PR validation:
     make format
     make lint
     make test-fast

3. Open a DRAFT PR, apply the label "PR: Merge", and request a
   Copilot review.

4. For every changed file, post a provenance comment on the PR via
   the GitHub API (see SKILL.md §"Document change provenance").
   Use subject_type="file" for file-level comments, and add inline
   comments for any custom changes you made.
   Enforce a 4-5 s delay between API calls; retry after 30 s on
   rate-limit errors.

5. Monitor CI; fix failures as separate commits while the PR is
   still in draft, then squash before marking it ready.

Consult references/file_ownership.md if you encounter any conflicts
or mixed-ownership files that need manual resolution.
EOF

else
  # ── CONFLICTED MERGE ────────────────────────────────────────────────────────
  cat <<EOF
════════════════════════════════════════════════════════════
MERGE RESULT: merge-conflicted
Branch:       ${BRANCH}
Merged from:  starbase/main → $(git rev-parse --short starbase/main)
════════════════════════════════════════════════════════════

CONFLICTED FILES ($(echo "$CONFLICTED_FILES" | grep -c . || echo 0)):
$(echo "$CONFLICTED_FILES" | sed 's/^/  /')

ALL CHANGED FILES ($(echo "$CHANGED_FILES" | grep -c . || echo 0)):
$(echo "$CHANGED_FILES" | sed 's/^/  /')

NEXT STEPS FOR THE AGENT
─────────────────────────────────────────────────────────────
1. Resolve each conflict using the ownership map in
   references/file_ownership.md.  Key rules:
     - "Always take starbase/main"  → git checkout --theirs <file>
     - "Always take child repo"     → git checkout --ours   <file>
     - Mixed ownership              → edit manually per the rule

2. After resolving all conflicts:
     git add <resolved-files>
     git merge --continue

3. Scan all changed files for placeholder text:
     git diff --name-only --diff-filter=d starbase/main...HEAD | \\
       xargs -r grep -i -E "starcraft|starbase"
   Update any matches (except external URLs) to this repo's identity.

4. Run pre-PR validation:
     make format
     make lint
     make test-fast

5. Open a DRAFT PR, apply the label "PR: Merge", and request a
   Copilot review.

6. For every changed file, post a provenance comment on the PR via
   the GitHub API (see SKILL.md §"Document change provenance").
   Use subject_type="file" for file-level comments, and add inline
   comments for any custom changes you made.
   Enforce a 4-5 s delay between API calls; retry after 30 s on
   rate-limit errors.

7. Monitor CI; fix failures as separate commits while the PR is
   still in draft, then squash before marking it ready.
EOF
  exit 1
fi
