---
name: documentation-structure
description: "Audits documentation structure: heading levels, section completeness, and logical ordering of content."
---

# Documentation Structure Audit

## Scope

Document structure only: heading hierarchy, section ordering,
presence of required sections (introduction, prerequisites, steps, reference),
file naming, metadata blocks, navigation, and cross-references.

## Inputs

- Documentation file(s) under review.
- Documentation directory structure.
- Diataxis classification output
  (from the `documentation-diataxis` skill, when run as part of the orchestrated review).

## Actions

### File Naming

- Verify files use lowercase with dashes
  and the correct extension for their syntax
  (for example, `connect-vscode.rst` for reST, `connect-vscode.md` for MyST).

### Metadata

- Ensure every page has required metadata near the top
  when the repository's docs conventions require it:
  `.. meta::` after the anchor label for reST,
  or the MyST equivalent (front matter or `meta` directive) for Markdown sources.

### Directory Placement

- Confirm the file is located in the directory matching its intended
  Diataxis category
  (for example, tutorials in `tutorial/`, how-to guides in `how-to/`).

### Navigation

- Ensure new pages are added to the `toctree`.

### Cross-References

- Prefer stable reference roles
  (`:ref:` for reST, `{ref}`/`{numref}` for MyST) over page-level links.
- Flag uses of `:doc:`/`{doc}` (or equivalents)
  except for index-like pages that are unlikely to be moved or renamed.
- Suggest adding links to improve documentation discoverability.
- Verify cross-references resolve correctly.

## Output

A list of structural or metadata violations covering file naming,
metadata, directory placement, navigation, and cross-reference issues.
