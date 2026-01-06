---
description: 'Guidelines for documentation-related suggestions.'
applyTo: 'docs/**/*.md'
---

# Documentation instructions

## Purpose

This file provides specific guidance for testing and reviewing documentation.

## Tests & CI

The CI expects documentation to pass `vale` and `lychee`; address reported issues rather than silencing the tools.

### Linting & checks (how to run)

Run the docs linters using the top-level Makefile targets: `make docs-check` (this runs `vale` and `lychee`).

## Small-edit rules for AI agents

- Do not change `docs/index.md` structure without updating the numeric Contents list — keep the order and paths in sync with files under `docs/`.
- When adding a new page in one of the folders of `docs`, add a short entry in the landing page if there's a landing page in the folder (e.g., if adding a new how-to guide, update the landing page `docs/how-to/landing-page.md`). 
- When adding new page, update the "Contents" section of `docs/index.md` with a new entry for the page.

