---
name: prepare-docs-automated-spread-test
description: "Prepare a charm tutorial for the canonical/operator-workflows automated documentation Spread test. Adds SPREAD / SPREAD SKIP annotations to docs/tutorial.md, generates a top-level spread.yaml, and creates .github/workflows/spread_docs.yaml. WHEN: prepare spread docs, annotate tutorial for spread, create spread yaml, add spread workflow, automate tutorial testing, spread test setup, docs spread."
argument-hint: "Describe the target repository or any specific constraints"
metadata:
  author: canonical/platform-engineering
  version: "1.0.0"
---

# Prepare the tutorial for the automated documentation Spread workflow

You are preparing this repository to use
`canonical/operator-workflows/.github/workflows/docs_spread.yaml@main`, the
reusable workflow that runs a Spread test over a Markdown documentation file.

This skill is **repository-agnostic**. Do not hard-code application names,
model names, hostnames, or commands drawn from any specific charm. Read
`docs/tutorial.md` in the target repository and make your own decisions.

## When to Use

- Setting up automated Spread testing for a charm tutorial
- Annotating `docs/tutorial.md` with `SPREAD` / `SPREAD SKIP` comments
- Generating `spread.yaml` and `.github/workflows/spread_docs.yaml`
- Onboarding a charm repository to the `canonical/operator-workflows` docs Spread workflow

## Goal

Add or update **only** these three files:

1. `docs/tutorial.md` — annotated with `SPREAD` / `SPREAD SKIP` HTML comment
   blocks so the reusable workflow can generate a runnable `task.yaml` from it.
2. `spread.yaml` — Spread project configuration at the repository root.
3. `.github/workflows/spread_docs.yaml` — a thin workflow that delegates to
   the reusable `docs_spread.yaml` workflow.

Do **not** modify any other file. If you find yourself wanting to change
anything else to make the test pass, stop and note it as a follow-up item
instead.

## Procedure

### Step 1 — Gather context

Read these references before you start. The first is the authoritative
specification for SPREAD comment syntax; the other three are a working
example from `canonical/synapse-operator`.

- [SPREAD comment syntax spec](https://github.com/canonical/operator-workflows/blob/main/docs/how-to/docs_spread_manage_commands.md)
- [synapse tutorial (example)](https://github.com/canonical/synapse-operator/blob/track/1/docs/tutorial/getting-started.md)
- [synapse spread.yaml (example)](https://github.com/canonical/synapse-operator/blob/track/1/spread.yaml)
- [synapse spread_docs.yaml (example)](https://github.com/canonical/synapse-operator/blob/track/1/.github/workflows/spread_docs.yaml)

Also read the repository's own `docs/tutorial.md` end-to-end, plus
`charmcraft.yaml` and `metadata.yaml` (whichever exists) to discover the
charm's name.

### Step 2 — Classify tutorial commands

Walk every fenced code block in `docs/tutorial.md` in reading order. For each
command inside a block, decide one of three outcomes using the criteria below.
Do **not** rely on a hard-coded list of commands.

Refer to [the command classification reference](./references/command-classification.md)
for detailed criteria and examples.

### Step 3 — Annotate `docs/tutorial.md`

Apply the following mechanical rules:

- The only permitted edits are additions of HTML comment blocks
  (`<!-- SPREAD ... -->` and `<!-- SPREAD SKIP -->` … `<!-- SPREAD SKIP END -->`).
  Never remove, reword, or reformat rendered content.
- Every `<!-- SPREAD SKIP -->` must be closed by a matching
  `<!-- SPREAD SKIP END -->` before the next top-level heading.
- Every `<!-- SPREAD` hidden-command block must end with `-->` on its own
  line, and the commands inside must not themselves contain `-->`.
- Preserve existing frontmatter, MyST directives, cross-references, and image
  references.
- Do not touch code blocks that are language examples unrelated to the
  tutorial commands (for instance, a `python` block that only shows a
  snippet).

### Step 4 — Generate `spread.yaml`

Refer to [the spread.yaml reference](./references/spread-yaml-shape.md) for
the required structure. Derive the charm name from `charmcraft.yaml` or
`metadata.yaml` (`name:` field). If `spread.yaml` already exists, do **not**
overwrite it — note the conflict as a follow-up.

### Step 5 — Generate `.github/workflows/spread_docs.yaml`

Refer to [the workflow reference](./references/spread-workflow-shape.md) for
the required structure. If this file already exists, do **not** overwrite
it — note the conflict as a follow-up.

### Step 6 — Validate

Run each check. If any fails, fix the generated files and re-run.

1. `yamllint spread.yaml .github/workflows/spread_docs.yaml` — must exit
   zero. (Skip the file if you chose not to write it because it already
   existed.)
2. Grep-based structural check on `docs/tutorial.md`:
   - `grep -c '<!-- SPREAD SKIP -->' docs/tutorial.md` must equal
     `grep -c '<!-- SPREAD SKIP END -->' docs/tutorial.md`.
   - Every line matching `^<!-- SPREAD$` must have a matching `^-->$` line
     later in the file (before the next `<!-- SPREAD` opener).
3. `git status --porcelain` output must list only the three target paths
   (`docs/tutorial.md`, `spread.yaml`,
   `.github/workflows/spread_docs.yaml`). Any other entry is a bug — revert
   it before proceeding.

### Step 7 — Summarize

Provide the user with:

1. **Command mapping** — a Markdown table with columns
   `Tutorial section` | `Command (trimmed)` |
   `Classification (run / skip / skip+hidden)` | `Reason`.
   Include one row per command classified. For *skip+hidden* rows,
   quote the hidden replacement command in the *Reason* column.
2. **Validation output** — trimmed `yamllint` output and the counts from
   the grep-based structural check.
3. **Follow-ups** — anything that could not be expressed as a SPREAD comment
   (for example, a manual browser check with no automated equivalent), plus
   any pre-existing `spread.yaml` or `.github/workflows/spread_docs.yaml`
   that was not overwritten.
