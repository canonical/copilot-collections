#!/bin/bash

# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default locations to search (in order of preference)
CONFIG_LOCATIONS=(".github/.copilot-collections.yaml" ".copilot-collections.yaml")
TOOLKIT_REPO="https://github.com/canonical/copilot-collections.git"
TEMP_DIR="$(pwd)/copilot-toolkit-temp"

cleanup() {
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

echo -e "${BLUE} Canonical Copilot Context Sync${NC}"

if ! command -v yq &> /dev/null; then
    echo -e "${RED}❌ Error: 'yq' is required but not installed.${NC}"
    echo "   Please install it (e.g., 'sudo snap install yq')."
    exit 1
fi

# Allow override via environment variable or command-line argument
if [ -n "$1" ]; then
    CONFIG_FILE="$1"
elif [ -n "$COPILOT_CONFIG_FILE" ]; then
    CONFIG_FILE="$COPILOT_CONFIG_FILE"
else
    # Search through default locations
    CONFIG_FILE=""
    for loc in "${CONFIG_LOCATIONS[@]}"; do
        if [ -f "$loc" ]; then
            CONFIG_FILE="$loc"
            break
        fi
    done
fi

if [ -z "$CONFIG_FILE" ] || [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}❌ Error: Configuration file not found.${NC}"
    echo "   Searched in: ${CONFIG_LOCATIONS[*]}"
    echo "   You can also specify a custom location via:"
    echo "     - Command-line argument: $0 <path-to-config>"
    echo "     - Environment variable: COPILOT_CONFIG_FILE=<path>"
    exit 1
fi

echo -e "${BLUE}📄 Using config:${NC} $CONFIG_FILE"

VERSION=$(yq '.copilot.version' "$CONFIG_FILE")
if [ "$VERSION" == "null" ] || [ -z "$VERSION" ]; then
     echo -e "${RED}❌ Error: Could not read '.copilot.version' from $CONFIG_FILE${NC}"
     exit 1
fi

echo -e "${BLUE} Target Version:${NC} $VERSION"

echo -e "${BLUE}⬇  Fetching toolkit...${NC}"
git clone --quiet --depth 1 --branch "$VERSION" "$TOOLKIT_REPO" "$TEMP_DIR"

# 4. Run the Installer
chmod +x "$TEMP_DIR/scripts/install_collections.sh"

echo -e "${BLUE}  Applying collections...${NC}"
"$TEMP_DIR/scripts/install_collections.sh" "$CONFIG_FILE" "$TEMP_DIR"

echo -e "${GREEN} Update Complete!${NC}"
