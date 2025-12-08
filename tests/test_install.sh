#!/bin/bash

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🧪 Starting Integration Tests..."

# Setup temporary workspace
# Note: We use a local directory because yq (snap) cannot read from /tmp
REPO_ROOT=$(pwd)
TEST_DIR="$REPO_ROOT/_test_workspace"
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"

SCRIPT_PATH="$REPO_ROOT/scripts/install_collections.sh"

# Ensure cleanup
trap 'rm -rf "$TEST_DIR"' EXIT

# 1. Setup Mock Repository Structure in TEST_DIR
echo "   - Setting up mock repository..."
mkdir -p "$TEST_DIR/assets/common"
mkdir -p "$TEST_DIR/groups/team-a/instructions"
mkdir -p "$TEST_DIR/groups/team-a/folder-assets"

# Create dummy assets
echo "Core Content" > "$TEST_DIR/assets/common/core.md"
echo "Team Content" > "$TEST_DIR/groups/team-a/instructions/team.md"
echo "Folder File 1" > "$TEST_DIR/groups/team-a/folder-assets/file1.md"
echo "Folder File 2" > "$TEST_DIR/groups/team-a/folder-assets/file2.md"

# Create Root collections.yaml
cat <<EOF > "$TEST_DIR/collections.yaml"
core:
  description: "Core Collection"
  items:
    - src: assets/common/core.md
      dest: .github/core.md
EOF

# Create Group collections.yaml
cat <<EOF > "$TEST_DIR/groups/team-a/collections.yaml"
team-a-col:
  description: "Team A Collection"
  includes:
    - core
  items:
    # Relative path test
    - src: instructions/team.md
      dest: .github/team.md
    # Absolute path test (referencing root asset)
    - src: /assets/common/core.md
      dest: .github/team-core-ref.md
    # Folder copy test
    - src: folder-assets/
      dest: .github/folder-out/
EOF

# Create Consumer Config
cat <<EOF > "$TEST_DIR/consumer-config.yaml"
copilot:
  collections:
    - team-a-col
EOF

# 2. Run the Script
echo "   - Running install_collections.sh..."
# We run the script, passing the consumer config and the TEST_DIR as the toolkit root
# The script will write to the current directory (which we should probably switch to TEST_DIR or a separate output dir)
# The script writes relative to where it is run, based on 'dest'.
# Let's run it inside a "consumer" directory.

CONSUMER_DIR="$TEST_DIR/consumer_repo"
mkdir -p "$CONSUMER_DIR"
cd "$CONSUMER_DIR"

# Run script
"$SCRIPT_PATH" "$TEST_DIR/consumer-config.yaml" "$TEST_DIR"

# 3. Assertions
echo "   - Verifying results..."

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅ Found $1${NC}"
    else
        echo -e "${RED}❌ Missing $1${NC}"
        exit 1
    fi
}

# Check Core inheritance
check_file ".github/core.md"

# Check Team relative path
check_file ".github/team.md"

# Check Team absolute path reference
check_file ".github/team-core-ref.md"

# Check Folder copy
check_file ".github/folder-out/file1.md"
check_file ".github/folder-out/file2.md"

echo -e "${GREEN}🎉 All tests passed!${NC}"
