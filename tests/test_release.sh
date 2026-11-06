#!/bin/bash

# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

set -euo pipefail

REPO_ROOT=$(pwd)
PUBLISHER="$REPO_ROOT/scripts/create_release.sh"
TEST_DIR=$(mktemp -d "$REPO_ROOT/.test-release.XXXXXX")
trap 'rm -rf "$TEST_DIR"' EXIT

mkdir "$TEST_DIR/repo"
cd "$TEST_DIR/repo"
git init -q
git config user.name "Release Test"
git config user.email "release-test@example.invalid"
git config commit.gpgSign false
git config tag.gpgSign false
git config core.hooksPath /dev/null
git commit -q --allow-empty -m "Initial commit"
BASE_SHA=$(git rev-parse HEAD)
git tag v0.22.0
git commit -q --allow-empty -m "First merge"
FIRST_SHA=$(git rev-parse HEAD)
git commit -q --allow-empty -m "Second merge"
SECOND_SHA=$(git rev-parse HEAD)

export GITHUB_REPOSITORY="example/toolkit"
export RELEASE_SHA="$SECOND_SHA"
export TEST_LATEST_TAG="v0.22.0"
export TEST_VIEW_STATUS=0 TEST_CREATE_STATUS=0
export TEST_CALLS="$TEST_DIR/calls"

# Only the network boundary is mocked; version and ancestry checks use real git.
gh() {
    if [[ "$1 $2" == "release view" ]]; then
        printf '%s\n' "$TEST_LATEST_TAG"
        return "$TEST_VIEW_STATUS"
    fi
    if [[ "$1 $2" == "release create" ]]; then
        printf '%s\n' "$@" >> "$TEST_CALLS"
        return "$TEST_CREATE_STATUS"
    fi
    echo "Unexpected gh invocation: $*" >&2
    return 1
}
export -f gh

fail_test() {
    echo "FAIL: $1" >&2
    exit 1
}

run_success() {
    : > "$TEST_CALLS"
    bash "$PUBLISHER" > "$TEST_DIR/output" 2>&1 ||
        { cat "$TEST_DIR/output"; fail_test "$1"; }
    echo "PASS: $1"
}

run_failure() {
    : > "$TEST_CALLS"
    if bash "$PUBLISHER" > "$TEST_DIR/output" 2>&1; then
        fail_test "$1 should fail"
    fi
    grep -q "$2" "$TEST_DIR/output" || { cat "$TEST_DIR/output"; fail_test "$1 error"; }
    [[ ! -s "$TEST_CALLS" ]] || fail_test "$1 must not publish"
    echo "PASS: $1"
}

run_success "Increment minor and publish the exact tested SHA with generated notes"
printf '%s\n' release create v0.23.0 --repo example/toolkit \
    --target "$SECOND_SHA" --title v0.23.0 --generate-notes \
    --notes-start-tag v0.22.0 --latest > "$TEST_DIR/expected"
cmp -s "$TEST_DIR/expected" "$TEST_CALLS" || fail_test "Release command"

RELEASE_SHA="$BASE_SHA"
run_success "Rerun of an already released commit"
[[ ! -s "$TEST_CALLS" ]] || fail_test "Duplicate release"

RELEASE_SHA="$FIRST_SHA"
git tag v0.23.0 "$SECOND_SHA"
TEST_LATEST_TAG="v0.23.0"
run_success "Out-of-order completion cannot roll back the latest release"
[[ ! -s "$TEST_CALLS" ]] || fail_test "Older commit published"
git tag -d v0.23.0 > /dev/null

RELEASE_SHA="$SECOND_SHA"
TEST_LATEST_TAG="v1.9.7"
git tag -a v1.9.7 "$BASE_SHA" -m "Annotated release"
run_success "Increment minor and reset patch for annotated tags"
grep -qx v1.10.0 "$TEST_CALLS" || fail_test "Minor increment"

TEST_LATEST_TAG="v0.22.0"
git tag v0.23.0 "$FIRST_SHA"
run_failure "Existing next tag must not be reused" "already exists"
git tag -d v0.23.0 > /dev/null

TEST_VIEW_STATUS=1
run_failure "GitHub lookup failure" "Could not read"
TEST_VIEW_STATUS=0
TEST_LATEST_TAG="v0.23.0-rc.1"
run_failure "Unsupported latest version" "stable version"
TEST_LATEST_TAG="v0.99.0"
run_failure "Missing latest tag" "Could not resolve"

git checkout -q --orphan unrelated
git commit -q --allow-empty -m "Unrelated history"
git tag v2.0.0
git checkout -q "$SECOND_SHA"
TEST_LATEST_TAG="v2.0.0"
run_failure "Divergent history" "not descended"

TEST_LATEST_TAG="v0.22.0"
RELEASE_SHA="main"
run_failure "Invalid target" "full commit SHA"
RELEASE_SHA="$SECOND_SHA"
TEST_CREATE_STATUS=1
: > "$TEST_CALLS"
if bash "$PUBLISHER" > "$TEST_DIR/output" 2>&1; then
    fail_test "Publication failure must fail the job"
fi
grep -q "Could not publish" "$TEST_DIR/output" || fail_test "Publication error"
echo "PASS: Publication failure is surfaced"

echo "All release tests passed."
