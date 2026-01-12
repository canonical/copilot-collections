#!/bin/bash

# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🧪 Starting Validation Script Tests..."

REPO_ROOT=$(pwd)
TEST_DIR="$REPO_ROOT/_test_validation_workspace"
VALIDATOR="$REPO_ROOT/scripts/validate_collections.sh"

setup() {
    rm -rf "$TEST_DIR"
    mkdir -p "$TEST_DIR"
}

fail_test() {
    echo -e "${RED}❌ Test Failed: $1${NC}"
    exit 1
}

pass_test() {
    echo -e "${GREEN}✅ Test Passed: $1${NC}"
}

# Test 1: Valid State
setup
mkdir -p "$TEST_DIR/assets"
touch "$TEST_DIR/assets/file.md"
cat <<EOF > "$TEST_DIR/collections.yaml"
col1:
  items:
    - src: assets/file.md
      dest: out.md
col2:
  includes:
    - col1
EOF

echo "   - Running Test 1: Valid State"
if "$VALIDATOR" "$TEST_DIR" > /dev/null; then
    pass_test "Valid State"
else
    fail_test "Valid State should have passed"
fi

# Test 2: Duplicate Name
setup
mkdir -p "$TEST_DIR/groups/g1"
cat <<EOF > "$TEST_DIR/collections.yaml"
col1:
  items: []
EOF
cat <<EOF > "$TEST_DIR/groups/g1/collections.yaml"
col1:
  items: []
EOF

echo "   - Running Test 2: Duplicate Name"
if ! "$VALIDATOR" "$TEST_DIR" > /dev/null 2>&1; then
    pass_test "Duplicate Name caught"
else
    fail_test "Duplicate Name should have failed"
fi

# Test 3: Missing Include
setup
cat <<EOF > "$TEST_DIR/collections.yaml"
col1:
  includes:
    - missing-col
EOF

echo "   - Running Test 3: Missing Include"
if ! "$VALIDATOR" "$TEST_DIR" > /dev/null 2>&1; then
    pass_test "Missing Include caught"
else
    fail_test "Missing Include should have failed"
fi

# Test 4: Missing Asset (Relative)
setup
cat <<EOF > "$TEST_DIR/collections.yaml"
col1:
  items:
    - src: missing.md
      dest: out.md
EOF

echo "   - Running Test 4: Missing Asset"
if ! "$VALIDATOR" "$TEST_DIR" > /dev/null 2>&1; then
    pass_test "Missing Asset caught"
else
    fail_test "Missing Asset should have failed"
fi

# Test 5: Missing Asset (Absolute)
setup
cat <<EOF > "$TEST_DIR/collections.yaml"
col1:
  items:
    - src: /assets/missing.md
      dest: out.md
EOF

echo "   - Running Test 5: Missing Absolute Asset"
if ! "$VALIDATOR" "$TEST_DIR" > /dev/null 2>&1; then
    pass_test "Missing Absolute Asset caught"
else
    fail_test "Missing Absolute Asset should have failed"
fi

# Test 6: Directory Src without Trailing Slash in Dest
setup
mkdir -p "$TEST_DIR/assets/folder"
cat <<EOF > "$TEST_DIR/collections.yaml"
col1:
  items:
    - src: assets/folder
      dest: out-folder # Missing trailing slash
EOF

echo "   - Running Test 6: Directory Src without Trailing Slash in Dest"
if ! "$VALIDATOR" "$TEST_DIR" > /dev/null 2>&1; then
    pass_test "Directory Dest Check caught"
else
    fail_test "Directory Dest Check should have failed"
fi

echo -e "${GREEN}🎉 All validation tests passed!${NC}"
