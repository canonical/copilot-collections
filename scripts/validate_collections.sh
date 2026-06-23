#!/bin/bash

# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

# scripts/validate_collections.sh
# Validates integrity of collection definitions:
# 1. No duplicate collection names.
# 2. All 'includes' reference existing collections.
# 3. All 'src' items reference existing files/folders.

set -e

TOOLKIT_DIR="${1:-.}"
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "🔍 Validating collections in $TOOLKIT_DIR..."

if ! command -v yq &> /dev/null; then
    echo "❌ Error: yq is not installed."
    exit 1
fi

# 1. Discovery & Collision Check
echo "   - Checking for name collisions..."
declare -A ALL_COLLECTIONS
FAILED=0

# Find all yaml files
while read -r manifest; do
    # Get keys (collection names)
    # We use -r to get raw output (no quotes)
    keys=$(cat "$manifest" | yq e 'keys | .[]' 2>/dev/null || true)
    
    for key in $keys; do
        if [[ -n "${ALL_COLLECTIONS[$key]}" ]]; then
            echo -e "${RED}❌ Error: Duplicate collection name '$key'${NC}"
            echo "      Defined in: ${ALL_COLLECTIONS[$key]}"
            echo "      And in:     $manifest"
            FAILED=1
        else
            ALL_COLLECTIONS[$key]="$manifest"
        fi
    done
done < <(find "$TOOLKIT_DIR" -name "collections.yaml")

if [ "$FAILED" -eq 1 ]; then
    echo -e "${RED}Validation Failed: Name collisions detected.${NC}"
    exit 1
fi

# 2. Integrity Check (Includes & Assets)
echo "   - Checking referential integrity..."

while read -r manifest; do
    manifest_dir=$(dirname "$manifest")
    keys=$(cat "$manifest" | yq e 'keys | .[]' 2>/dev/null || true)

    for col in $keys; do
        # Check Includes
        includes=$(cat "$manifest" | yq e ".[\"$col\"].includes[]" 2>/dev/null || true)
        for inc in $includes; do
            if [[ -z "${ALL_COLLECTIONS[$inc]}" ]]; then
                echo -e "${RED}❌ Error: Collection '$col' (in $manifest) includes missing collection '$inc'${NC}"
                FAILED=1
            fi
        done

        # Check Assets
        count=$(cat "$manifest" | yq e ".[\"$col\"].items | length")
        if [ "$count" -gt 0 ]; then
            for ((i=0; i<count; i++)); do
                src=$(cat "$manifest" | yq e ".[\"$col\"].items[$i].src")
                
                # Resolve Path
                if [[ "$src" == /* ]]; then
                    # Absolute path relative to toolkit root
                    # Remove leading / for joining
                    # Note: TOOLKIT_DIR might be relative or absolute.
                    # If src is "/assets/foo", we want "$TOOLKIT_DIR/assets/foo"
                    full_path="$TOOLKIT_DIR$src"
                else
                    # Relative to manifest
                    full_path="$manifest_dir/$src"
                fi

                if [ ! -e "$full_path" ]; then
                    echo -e "${RED}❌ Error: Collection '$col' references missing asset: '$src'${NC}"
                    echo "      In file: $manifest"
                    echo "      Resolved to: $full_path"
                    FAILED=1
                elif [ -d "$full_path" ]; then
                    # If src is a directory, dest MUST end with /
                    dest=$(cat "$manifest" | yq e ".[\"$col\"].items[$i].dest")
                    if [[ "$dest" != */ ]]; then
                        echo -e "${RED}❌ Error: Collection '$col' item '$src' is a directory, so dest '$dest' must end with '/'${NC}"
                        FAILED=1
                    fi
                fi
            done
        fi
    done
done < <(find "$TOOLKIT_DIR" -name "collections.yaml")

if [ "$FAILED" -eq 1 ]; then
    echo -e "${RED}Validation Failed.${NC}"
    exit 1
else
    echo -e "${GREEN}✅ All collections valid.${NC}"
    exit 0
fi
