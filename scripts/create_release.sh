#!/bin/bash

# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

set -euo pipefail

: "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY must be set}"
: "${RELEASE_SHA:?RELEASE_SHA must be set to the tested commit}"

if [[ ! "$RELEASE_SHA" =~ ^[0-9a-f]{40}$ ]]; then
    echo "::error::Release target must be a full commit SHA."
    exit 1
fi

if ! LATEST_TAG=$(gh release view --repo "$GITHUB_REPOSITORY" --json tagName --jq .tagName); then
    echo "::error::Could not read the latest release."
    exit 1
fi

if [[ ! "$LATEST_TAG" =~ ^v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]]; then
    echo "::error::Latest release must use a stable version tag: vMAJOR.MINOR.PATCH."
    exit 1
fi
MAJOR="${BASH_REMATCH[1]}"
MINOR="${BASH_REMATCH[2]}"
NEXT_TAG="v${MAJOR}.$((MINOR + 1)).0"

if ! LATEST_SHA=$(git rev-parse --verify "refs/tags/$LATEST_TAG^{commit}"); then
    echo "::error::Could not resolve the latest release tag to a commit."
    exit 1
fi
if ! git cat-file -e "$RELEASE_SHA^{commit}"; then
    echo "::error::Tested commit is missing from the checkout."
    exit 1
fi

# Tests can finish out of order; never replace newer released content with older content.
if git merge-base --is-ancestor "$RELEASE_SHA" "$LATEST_SHA"; then
    echo "Commit $RELEASE_SHA is already included in release $LATEST_TAG; skipping."
    exit 0
fi
if ! git merge-base --is-ancestor "$LATEST_SHA" "$RELEASE_SHA"; then
    echo "::error::Tested commit is not descended from the latest release."
    exit 1
fi
if git show-ref --verify --quiet "refs/tags/$NEXT_TAG"; then
    echo "::error::Tag $NEXT_TAG already exists; refusing to reuse it."
    exit 1
fi

if ! gh release create "$NEXT_TAG" --repo "$GITHUB_REPOSITORY" \
    --target "$RELEASE_SHA" --title "$NEXT_TAG" --generate-notes \
    --notes-start-tag "$LATEST_TAG" --latest; then
    echo "::error::Could not publish release $NEXT_TAG."
    exit 1
fi
