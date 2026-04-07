# Starcraft documentation instructions

This directory contains documentation instruction files for Copilot for use in Starcraft
projects.

## Instructions

| File | Source |
|------|--------|
| `starcraft-docs-style.instructions.md` | [Starcraft style guide](https://canonical-starflow.readthedocs-hosted.com/how-to/starcraft-style-guide/) |
| `starcraft-docs-meta.instructions.md` | [Add a page meta description](https://canonical-starflow.readthedocs-hosted.com/how-to/add-a-page-meta-description/) |

Each file has an `applyTo` header specifying which files the instructions apply to.

## Generating the instructions

The instruction files are compiled by `scripts/compile-llm-instructions.py`. It fetches
the RST source files from [canonical/starflow](https://github.com/canonical/starflow) on
GitHub and converts them to Markdown using [pandoc](https://pandoc.org/).

**Prerequisites:**

```bash
apt install pandoc
```

**Usage**:

From the `groups/starcraft/instructions/documentation/` directory, run:

```bash
python3 scripts/compile-llm-instructions.py
```

This process is not automated. To update the instructions, run the script locally,
review the changes, and submit a PR.
