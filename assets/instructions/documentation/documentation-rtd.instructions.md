---
description: 'Guidelines for documentation-related suggestions.'
applyTo: 'docs/**/*.md, docs/**/*.rst'
---

# Documentation instructions for Read the Docs projects

## Purpose

This file provides specific guidance for testing and reviewing documentation in Read the Docs projects.

## Tests & CI

The CI expects documentation to pass `spelling`, `linkcheck`, `lint-md`, and `vale`; address reported issues rather than silencing the tools.

### Linting & checks (how to run)

Run the docs linters via the docs-level Makefile targets:

* `make spelling`: Runs the spelling checks.
* `make linkcheck`: Runs the link checker.
* `make lint-md`: Runs the Markdown linter.
* `make vale`: Runs the style checker.

## Admonitions

Admonition directives are a standardized way of communicating different types of information. They should be used for tips, notes, warnings, and important information that the reader should not skip over or miss.

For `*.md` files, admonitions are formatted in the following way:

````
```{note}
A note.
```
````

For `*.rst` files, admonitions are formatted in this way:

```
.. note::

  A note.
```

Adhere to the following conventions:

- Use admonitions sparingly in the documentation. Offer suggestions to remove admonitions when they are not necessary (for example, if the text is not necessary for the user to read). 
- Only use the following types: `note`, `tip`, `warning`, `important`

## Small-edit rules for AI agents

- Do not change `docs/index.md` structure without updating the `toctree` directive — keep the order and paths in sync with files under `docs/`.
- When adding a new page in one of the folders of `docs`, add a short entry in the landing page if there's a landing page in the folder (e.g., if adding a new how-to guide, update the landing page `docs/how-to/landing-page.md`). 
- When adding new page, update the `toctree` directive in the relevant index page (`docs/index.md` for a top-level page, and `docs/*/index.md` for a new page in a specific folder).

