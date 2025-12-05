#!/bin/bash

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

set -e

# Usage: ./install_collections.sh <path_to_config_yaml> <path_to_toolkit_root>
CONFIG_FILE="$1"
TOOLKIT_DIR="$2"
MANIFEST_FILE="$TOOLKIT_DIR/collections.yaml"

# 1. Validation
if [ -z "$CONFIG_FILE" ] || [ -z "$TOOLKIT_DIR" ]; then
    echo "❌ Usage: $0 <config_file> <toolkit_dir>"
    exit 1
fi

if ! command -v yq &> /dev/null; then
    echo "❌ Error: yq is not installed."
    exit 1
fi

echo "📖 Reading configuration from: $CONFIG_FILE"

# 2. Parse Collections from Config
# We use yq to extract the list of collections as a space-separated string
COLLECTIONS_LIST=$(yq '.copilot.collections[]' "$CONFIG_FILE" | tr '\n' ' ')

if [ -z "$COLLECTIONS_LIST" ]; then
    echo "⚠️  No collections found in config file."
    exit 0
fi

# 3. Logic: Process Collections
process_collection() {
    local col_name=$1
    echo "   📦 Processing Collection: $col_name"

    if ! yq -e ".${col_name}" "$MANIFEST_FILE" > /dev/null; then
        echo "   ❌ Error: Collection '$col_name' not found in manifest ($MANIFEST_FILE)."
        exit 1
    fi

    # Handle Includes (Recursion)
    local includes
    includes=$(yq ".${col_name}.includes[]" "$MANIFEST_FILE" 2>/dev/null || true)
    for included_col in $includes; do
        process_collection "$included_col"
    done

    # Handle Items
    local count
    count=$(yq ".${col_name}.items | length" "$MANIFEST_FILE")

    if [ "$count" -gt 0 ]; then
        for ((i=0; i<count; i++)); do
            local src dest
            src=$(yq ".${col_name}.items[$i].src" "$MANIFEST_FILE")
            dest=$(yq ".${col_name}.items[$i].dest" "$MANIFEST_FILE")
            
            # Resolve full path for source
            local full_src="$TOOLKIT_DIR/$src"

            echo "      - Installing $src -> $dest"
            mkdir -p "$(dirname "$dest")"
            
            if [ -f "$full_src" ]; then
                cat "$full_src" > "$dest"
            else
                echo "      ❌ Error: Source file missing: $full_src"
                exit 1
            fi
        done
    fi
}

# 4. Execution Loop
for col in $COLLECTIONS_LIST; do
    process_collection "$col"
done

echo "✅ Sync complete."
