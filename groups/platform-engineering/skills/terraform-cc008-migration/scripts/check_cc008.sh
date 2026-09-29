#!/bin/bash

# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

# Run the CC008 Terraform compliance checker from canonical/operator-workflows
# against the given module directories. With no arguments, every directory
# containing a main.tf is discovered and checked.

set -euo pipefail

CHECKER_BASE_URL="https://raw.githubusercontent.com/canonical/operator-workflows/main/terraform-compliance"
HCL2_VERSION="8.1.3"

if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed. See https://docs.astral.sh/uv/." >&2
    exit 1
fi

module_dirs=("$@")

if [ ${#module_dirs[@]} -eq 0 ]; then
    while IFS= read -r module_dir; do
        module_dirs+=("$module_dir")
    done < <(find . -type f -name 'main.tf' -not -path '*/.terraform/*' -exec dirname {} \; | sort -u)
fi

if [ ${#module_dirs[@]} -eq 0 ]; then
    echo "❌ Error: no Terraform module directory found (no main.tf)." >&2
    exit 1
fi

scratch_dir="$(mktemp -d)"
trap 'rm -rf "$scratch_dir"' EXIT

echo "⬇️  Fetching the CC008 compliance checker..."
for checker_file in terraform_spec.py terraform_hcl.py terraform_check.py; do
    curl -fsSL -o "$scratch_dir/$checker_file" "$CHECKER_BASE_URL/$checker_file"
done

echo "🔍 Checking CC008 compliance for: ${module_dirs[*]}"
uv run --with "python-hcl2==$HCL2_VERSION" python "$scratch_dir/terraform_check.py" --verbose "${module_dirs[@]}"
