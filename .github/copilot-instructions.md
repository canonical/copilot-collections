# Copilot Instructions for `canonical/copilot-collections`

This repository is the "Toolkit" for centralized context management for GitHub Copilot across the Canonical ecosystem. It distributes standardized Copilot Custom Instructions and Prompts to other repositories via a subscription model.

## High Level Details

- **Type**: Utility/Toolkit.
- **Languages**: Bash (logic), YAML (configuration), Markdown (content).
- **Core Function**: Individual repositories define a `.copilot-collections.yaml` file listing "Collections" they need. This toolkit's scripts (`install_collections.sh`) parse that config and sync the corresponding Markdown files from `assets/` or `groups/<team>/` into the consumer's `.github/` directory.
- **Key Tools**: `yq` (YAML processing), `shellcheck` (Script linting).

## Project Layout

### Directories
- **`collections.yaml`**: The ROOT configuration file defining "Core" collections.
- **`assets/`**: Contains the source Markdown files for core collections.
- **`groups/`**: Contains team-specific collections.
    - Each subfolder (e.g., `groups/charm-tech/`) acts as a mini-repo with its own `collections.yaml` and asset folder.
- **`scripts/`**: Contains the logic binaries.
    - `install_collections.sh`: The main engine that reads config and copies files.
    - `validate_collections.sh`: Validates referential integrity of `collections.yaml` files.
    - `local_sync.sh`: A wrapper for local usage by consumers.
- **`tests/`**: Contains test scripts for the bash logic.
- **`.github/workflows/`**:
    - `test-toolkit.yaml`: The CI pipeline for this repo.
    - `auto_update_collections.yaml`: A **reusable workflow** imported by consumer repos to auto-update their instructions.

### Architecture
The system uses a "Pull" model.
1.  **Manifest**: `collections.yaml` maps a `collection_name` to a list of file operations (`src` -> `dest`).
2.  **Resolution**: The `install_collections.sh` script takes a consumer config, resolves the requested collections against the manifest, and copies `src` files to `dest`.

## Build and Validation Instructions

**Prerequisites**:
- Ensure `yq` (v4+) is installed.
- Ensure `shellcheck` is installed.

### 1. Validate Structure & Integrity
Before submitting changes (especially when editing `collections.yaml`), run the validator. It checks for:
- Duplicate collection names.
- References to missing files in `assets/`.
- Valid YAML syntax.

```bash
# Validates the root and all group configurations
./scripts/validate_collections.sh .
```

### 2. Run Tests
The repository includes a test suite for the bash scripts.

```bash
# Test the validation logic itself
./tests/test_validate.sh

# Test the installation/sync logic (Integration Test)
./tests/test_install.sh
```

### 3. Linting
Scripts should remain POSIX compliant or Bash-compatible as verified by shellcheck.

```bash
# Lint all scripts
shellcheck scripts/*.sh
```

### 4. Manifest Syntax Check
If you edited a YAML file, verify it is valid:

```bash
yq eval . collections.yaml > /dev/null
```

## Common Tasks

### Adding a New Instruction
1.  **Create Content**: Add the `.md` file in `assets/instructions/<category>/` (for valid categories see existing folders).
2.  **Update Manifest**: Edit `collections.yaml`.
    -   Find the appropriate collection key (e.g., `common-python`).
    -   Add a new item to the `items` list:
        ```yaml
        - src: assets/instructions/<category>/file.md
          dest: .github/instructions/file.md
        ```
3.  **Validate**: Run `./scripts/validate_collections.sh .`.

### Adding a Team Collection
1.  Create `groups/<team-name>/`.
2.  Add `groups/<team-name>/collections.yaml` following the schema.
3.  Add assets in that folder.
4.  Run validation.

## CI/CD 
The `Test Toolkit` workflow (`.github/workflows/test-toolkit.yaml`) runs automatically on PRs. It executes the linting, validation, and test steps listed above. If your local `./scripts/validate_collections.sh .` passes, CI should pass.
