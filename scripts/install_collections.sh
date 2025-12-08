#!/bin/bash

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

set -e

# Usage: ./install_collections.sh <path_to_config_yaml> <path_to_toolkit_root>
CONFIG_FILE="$1"
TOOLKIT_DIR="$2"

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

# 2. Build Merged Manifest
# We find all collections.yaml files, and for each, we prepend the directory path 
# to the 'src' fields so they become relative to the repo root.
echo "🔍 Discovering collections..."
# Use a local temp file to avoid snap confinement issues with /tmp
MERGED_MANIFEST="./merged_manifest.tmp.yaml"
rm -f "$MERGED_MANIFEST"
touch "$MERGED_MANIFEST"

# Find all collections.yaml files
while read -r manifest_path; do
    # Calculate relative path from toolkit root to the manifest file's directory
    rel_dir=${manifest_path#"$TOOLKIT_DIR/"}
    rel_dir=${rel_dir%collections.yaml}
    
    echo "   - Loading definitions from: $rel_dir"

    if [ -z "$rel_dir" ]; then
        cat "$manifest_path" >> "$MERGED_MANIFEST"
    else
        # Use yq to update items.src
        # 1. Prepend relative dir to everything
        # 2. Fix absolute paths to remain absolute
        cp "$manifest_path" "${manifest_path}.tmp"
        yq -i e "
            .[] .items[] .src |= \"$rel_dir\" + . |
            .[] .items[] .src |= sub(\"^$rel_dir/\", \"\")
        " "${manifest_path}.tmp"
        cat "${manifest_path}.tmp" >> "$MERGED_MANIFEST"
        rm "${manifest_path}.tmp"
    fi
done < <(find "$TOOLKIT_DIR" -name "collections.yaml")

# 3. Parse Collections from Config
COLLECTIONS_LIST=$(yq '.copilot.collections[]' "$CONFIG_FILE" | tr '\n' ' ')

if [ -z "$COLLECTIONS_LIST" ]; then
    echo "⚠️  No collections found in config file."
    rm "$MERGED_MANIFEST"
    exit 0
fi

# 4. Logic: Process Collections
process_collection() {
    local col_name=$1
    echo "   📦 Processing Collection: $col_name"

    if ! yq -e ".${col_name}" "$MERGED_MANIFEST" > /dev/null; then
        echo "   ❌ Error: Collection '$col_name' not found in any manifest."
        exit 1
    fi

    # Handle Includes (Recursion)
    local includes
    includes=$(yq ".${col_name}.includes[]" "$MERGED_MANIFEST" 2>/dev/null || true)
    for included_col in $includes; do
        process_collection "$included_col"
    done

    # Handle Items
    local count
    count=$(yq ".${col_name}.items | length" "$MERGED_MANIFEST")

    if [ "$count" -gt 0 ]; then
        for ((i=0; i<count; i++)); do
            local src dest
            src=$(yq ".${col_name}.items[$i].src" "$MERGED_MANIFEST")
            dest=$(yq ".${col_name}.items[$i].dest" "$MERGED_MANIFEST")
            
            # Resolve full path for source
            local full_src="$TOOLKIT_DIR/$src"

            echo "      - Installing $src -> $dest"
            
            if [ -d "$full_src" ]; then
                # Folder Copy
                mkdir -p "$dest"
                cp -r "$full_src/." "$dest/"
            elif [ -f "$full_src" ]; then
                # File Copy
                mkdir -p "$(dirname "$dest")"
                cat "$full_src" > "$dest"
            else
                echo "      ❌ Error: Source '$full_src' not found."
                exit 1
            fi
        done
    fi
}

# 5. Execution Loop
for col in $COLLECTIONS_LIST; do
    process_collection "$col"
done

rm "$MERGED_MANIFEST"
echo "✅ Sync complete."
