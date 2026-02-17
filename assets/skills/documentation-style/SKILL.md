---
name: documentation-style
description: "Evaluates documentation against the project style guide for tone, voice, terminology, and formatting conventions."
---

# Documentation Style Review

## Scope

Style conformance only: tone, voice, terminology, punctuation,
Oxford comma, active versus passive voice, prohibited phrases,
and formatting conventions.

## Inputs

- Documentation file(s) under review.
- Normative style asset: `references/doc-style-guide.md`.
- Syntax-specific style guides (fetched at runtime):
  - MyST: `https://raw.githubusercontent.com/canonical/sphinx-docs-starter-pack/refs/heads/main/docs/reference/myst-syntax-reference.md`
  - reST: `https://raw.githubusercontent.com/canonical/sphinx-docs-starter-pack/refs/heads/main/docs/reference/rst-syntax-reference.rst`

## Actions

1. **Load style guides**: Read `references/doc-style-guide.md`.
   Fetch the syntax-specific guide matching the file type
   (MyST for `.md`, reST for `.rst`).

2. **Syntax compliance**: Check headings, lists, code blocks,
   inline literals, and directives against the applicable syntax guide.
   Treat every instruction in the guide as mandatory;
   do not rely on a subset of rules.

3. **Full style guide compliance**: Read and apply all rules defined
   in `references/doc-style-guide.md`.
   Treat every instruction in the guide as mandatory;
   do not rely on a subset of rules.

4. **Style guide citation**: For every violation found,
   locate and quote the specific passage
   in `references/doc-style-guide.md` or the syntax-specific guide
   that supports the finding.

5. **Fallback behaviour**: If syntax guides cannot be fetched
   (offline or blocked), proceed with best effort
   using `references/doc-style-guide.md`
   and the syntax already present in the documentation set;
   do not block the review.
   If `references/doc-style-guide.md` is unavailable,
   block the review and report that the style guide cannot be accessed.

## Constraints

- Quote style guides when making style suggestions.
- Do not suggest style or markup changes without quoting the style guides.

## Output

A list of style violations, each accompanied by:

- The specific passage quoted from the style guide or syntax reference.
- The observation or suggested change.
