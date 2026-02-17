---
name: documentation-build
description: "Runs documentation build targets and reports all errors and warnings from the Sphinx/RTD build pipeline."
---

# Documentation Build Validation

## Scope

Build validation only: detect documentation build configuration,
run applicable build targets, collect all errors and warnings,
and categorise by severity.

## Inputs

- Repository root.

## Actions

1. **Identify documentation directory**: The `docs/` directory
   is the default location for Sphinx documentation.
   If not found, search common doc roots in this order:
   `doc/`, `documentation/`, `site/`, `docs-src/`.
   If still not found, perform a bounded search for `conf.py`
   (max depth 4) and use its parent as the docs root.

2. **Detect build configuration**: Check for the presence of:

   - `.readthedocs.yaml`
   - `docs/conf.py`
   - Makefile targets in the `docs/` directory

   If RTD artefacts are absent in the target repository,
   report "not applicable" in findings and exit cleanly.

3. **Run build targets** (when applicable):

   ```bash
   cd docs
   make clean
   make html
   ```

   Run additional checks if targets exist:

   ```bash
   make spelling linkcheck woke lint-md
   ```

4. **Capture output**: If any command fails, capture the output
   and report build issues. Attempt recovery once or twice,
   but do not proceed to content analysis until the documentation
   builds successfully without errors.
   Warnings must be collected and reported, but are not blocking
   unless the repository explicitly treats warnings as errors.

5. **Categorise findings by severity**:

   - **Errors**: Build failures, broken links, missing files.
   - **Warnings**: Deprecation notices, missing references,
     formatting issues.
   - **Info**: Suggestions, minor notices.

## Constraints

- Do not approve documentation that fails the Sphinx build.
- Build docs locally to catch build warnings.
- Do not invent Makefile targets;
  only use targets confirmed to exist in the target repository.

## Output

A build validation report listing all errors and warnings,
categorised by severity. If RTD artefacts are not detected,
report "Not applicable -- RTD artefacts not detected in target repo".
