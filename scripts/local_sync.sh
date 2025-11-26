#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

CONFIG_FILE=".collections-config.yaml"
TOOLKIT_REPO="https://github.com/canonical/copilot-collections.git"
TEMP_DIR=$(mktemp -d -t copilot-toolkit-XXXXXX)

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

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}❌ Error: Configuration file '$CONFIG_FILE' not found in current directory.${NC}"
    echo "   Are you in the root of your project?"
    exit 1
fi

VERSION=$(yq '.copilot.version' "$CONFIG_FILE")
if [ "$VERSION" == "null" ] || [ -z "$VERSION" ]; then
     echo -e "${RED}❌ Error: Could not read '.copilot.version' from $CONFIG_FILE${NC}"
     exit 1
fi

echo -e "${BLUE} Target Version:${NC} $VERSION"

echo -e "${BLUE}⬇  Fetching toolkit...${NC}"
git clone --quiet --depth 1 --branch "$VERSION" "$TOOLKIT_REPO" "$TEMP_DIR"

# Debug step
ls -la "$TEMP_DIR"

# 4. Run the Installer
chmod +x "$TEMP_DIR/scripts/install_collections.sh"

echo -e "${BLUE}  Applying collections...${NC}"
"$TEMP_DIR/scripts/install_collections.sh" "$CONFIG_FILE" "$TEMP_DIR"

echo -e "${GREEN} Update Complete!${NC}"
