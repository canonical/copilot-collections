---
name: terraform-cc008-migration
description: Migrates Terraform charm, component and product modules to the CC008 Charm Terraform Standards, enforcing the required file layout, variable and output contracts, MAJOR_VERSION markers, module tests and the operator-workflows reusable CI workflows. Use whenever a repository's Terraform modules must be brought to (or audited against) CC008.
metadata:
  author: canonical/platform-engineering
  version: "1.0.0"
---

# Terraform CC008 Migration

## Overview

Bring every Terraform module in a repository up to the **CC008 — Charm Terraform
Standards** specification, and wire the repository to the compliance, test and
release automation provided by
[canonical/operator-workflows](https://github.com/canonical/operator-workflows/tree/main/terraform-compliance).

## When To Use

- A repository ships one or more Terraform modules that predate CC008 (CC006-era
  layout, `versions.tf`, combined `endpoints` output, unpinned module sources).
- A new module must be authored so that it is CC008-compliant from the start.
- A CC008 compliance check fails in CI and the module needs to be corrected.

## Source Of Truth

[`assets/cc008.spec.md`](assets/cc008.spec.md) **is** the specification. Read the
sections relevant to the modules you are migrating *before* editing anything, and
resolve every question against it. This skill does not restate the spec; it only
reinforces the parts that are most often missed and describes the repository
plumbing the spec does not cover.

### Fetching The Companion Files

This skill ships two companion files next to `SKILL.md`: `assets/cc008.spec.md`
and `scripts/check_cc008.sh`. When the skill is installed as a directory — for
example synced to `.github/skills/terraform-cc008-migration/` — they are already
on disk and the relative paths above resolve.

When only `SKILL.md` was fetched (`copilot skill add <url>` materializes a single
file), download them first and use the downloaded copies wherever this document
refers to them:

```bash
CC008_BASE="https://raw.githubusercontent.com/canonical/copilot-collections/feat-terraform-cc008-migration-skill/groups/platform-engineering/skills/terraform-cc008-migration"
mkdir -p /tmp/cc008
curl -fsSL -o /tmp/cc008/cc008.spec.md "$CC008_BASE/assets/cc008.spec.md"
curl -fsSL -o /tmp/cc008/check_cc008.sh "$CC008_BASE/scripts/check_cc008.sh"
chmod +x /tmp/cc008/check_cc008.sh
```

Delete `/tmp/cc008` once the migration is verified; it must never be committed.

### Secondary References

In order of authority when they disagree:

1. [platform-engineering-charm-template/terraform](https://github.com/canonical/platform-engineering-charm-template/tree/main/terraform)
   — the canonical, always-up-to-date reference module. Prefer copying its exact
   patterns.
2. [operator-workflows/terraform-compliance](https://github.com/canonical/operator-workflows/tree/main/terraform-compliance)
   — the checker that decides whether the migration passed.
3. Finished migrations:
   [gateway-api-integrator-operator#320](https://github.com/canonical/gateway-api-integrator-operator/pull/320/files),
   [mailserver-operators#48](https://github.com/canonical/mailserver-operators/pull/48/files).

## Module Discovery

Treat every directory containing a `main.tf` (or an existing `versions.tf` /
`terraform.tf`) as one module, whether the repository has a single `terraform/`
directory or several — per-charm `<charm>/terraform`, product modules under
`terraform/<product>` or `terraform-product/`. Enumerate them all before
starting, and apply the rules below to each one:

```bash
find . -type f -name 'main.tf' -not -path '*/.terraform/*' -exec dirname {} \; | sort -u
```

## DO — Module Structure And Contracts

- **DO** ensure each module has `terraform.tf`, `variables.tf`, `outputs.tf`,
  `main.tf` and `README.md`. Rename a legacy `versions.tf` to `terraform.tf`,
  leaving the content unchanged except where the next rule requires otherwise.
- **DO** require, in `terraform.tf`, a Terraform `required_version` and a
  `juju/juju` provider version that admits `>= 1.0.0` (for example `~> 1.0`, or
  `> 1.0.0, < 2.0.0`).
- **DO** order `variable` blocks in `variables.tf` and `output` blocks in
  `outputs.tf` alphabetically by name.
- **DO**, for charm modules, declare the mandatory variables: `app_name`,
  `channel`, `config`, `constraints`, `model_uuid` (no default) and `revision`.
  Add `units` unless the charm is a subordinate charm, which must omit it.
- **DO** add the optional CC008 variables when they are relevant to the charm:
  `base`, `expose`, `resources`, `machines`, `endpoint_bindings`,
  `storage_directives`.
- **DO** set `nullable = false` on every variable that must always resolve to a
  concrete value (`app_name`, `channel`, `model_uuid`, …) so callers cannot pass
  an explicit `null` and bypass the default. Leave variables that intentionally
  default to `null` (`base`, `constraints`, `revision`, …) nullable.
- **DO**, for charm modules, provide the `application`, `provides` and `requires`
  outputs, each with a `description`. `application` must be the
  `juju_application` resource object itself — `value = juju_application.<name>` —
  not its `.name`.
- **DO** type `provides` and `requires` as `map(object({...}))`, one key per
  relation endpoint the charm actually declares, each entry carrying at least
  `kind = "endpoint"`, `name = juju_application.<name>.name` and
  `endpoint = "<relation-endpoint-name>"`. Add `controller = null` when the
  relation supports cross-model integration. Use `value = {}` only when the charm
  declares no endpoints of that kind.
- **DO** replace any deprecated combined `endpoint` / `endpoints` output with the
  `provides` / `requires` split.
- **DO** add a `terraform/MAJOR_VERSION` file at the root of each independent
  module family, containing only the current major version number and no trailing
  newline (start at `1` for a first migration). In multi-module repositories,
  make additional modules' `MAJOR_VERSION` files a relative symlink to that root
  file **only** when those modules share the same release train (the
  mailserver-operators#48 pattern); otherwise give each independently tagged
  module family its own file.
- **DO** add a `tests/main.tftest.hcl` per module, using `mock_provider "juju"`
  and asserting the module's key outputs, when the module has no test yet.
- **DO** pin every Terraform module `source = "git::...//terraform..."` reference
  — in README examples and in product modules — to a `?ref=` tag such as
  `?ref=tf-1.0.0`, never to an unpinned or floating branch.

## DO — CI Workflows

Use operator-workflows' reusable workflows instead of hand-written scripts.

- **DO** add or update `.github/workflows/terraform_modules_release.yaml` calling
  `canonical/operator-workflows/.github/workflows/terraform_modules_release.yaml`,
  triggered on push to `main` and on pull requests touching `terraform/**` (plus
  any other module paths), with `permissions: contents: write`.
- **DO** add `.github/workflows/terraform_modules_compliance.yaml` calling
  `canonical/operator-workflows/.github/workflows/terraform_modules_compliance.yaml`,
  triggered on pull requests touching `**/terraform/**`, with a
  `terraform-directories` input listing every discovered module directory.
- **DO** update `.github/workflows/test_terraform_modules.yaml` to call
  `canonical/operator-workflows/.github/workflows/terraform_modules_test.yaml`
  with `terraform-directories` listing every discovered module directory, and
  trigger it on
  `pull_request.paths: ['**/terraform/**', '.github/workflows/test_terraform_modules.yaml']`.
- **DO** pin every new — and every pre-existing unpinned — reusable-workflow call
  to a commit SHA. Reuse the SHA already used elsewhere in the repository for
  `canonical/operator-workflows` if one exists; otherwise resolve the latest
  `main` commit yourself and pin to it with a `# main` comment, as
  platform-engineering-charm-template does:

  ```bash
  git ls-remote https://github.com/canonical/operator-workflows.git main
  ```

## DO — Repository Housekeeping

- **DO** add `**/.terraform/` and `**/.terraform.lock.hcl` to the top-level
  `.gitignore` if they are not already ignored.
- **DO** add `**/MAJOR_VERSION` to the `header.ignore` list in `.licenserc.yaml`
  so the version markers are exempt from license headers.
- **DO** add a changelog entry — in `docs/changelog.md`, or a new file under
  `docs/release-notes/artifacts/` if the repository uses that convention —
  describing the CC008 migration and any breaking default change (for example
  `expose` now defaulting to `{}` instead of `null`).

## DON'T

- **DON'T** change any module's deployment behaviour — resource arguments,
  variable defaults — beyond what CC008 requires. Preserve existing defaults
  unless the spec mandates a different one.
- **DON'T** touch charm source code, `charmcraft.yaml`, or workflows unrelated to
  the Terraform modules.
- **DON'T** hand-roll a tagging or release workflow; call the canonical reusable
  workflow instead.
- **DON'T** leave `@main` or any floating branch or tag in a reusable-workflow
  call in the final diff, not even as a placeholder.
- **DON'T** commit the scratch directory used by the compliance checker, or any
  `.terraform/` artefact produced while validating.
- **DON'T** declare the migration finished on inspection alone — the compliance
  checker is the arbiter.

## Validate Before Declaring Done

Do not guess at compliance. Run the checker against every discovered module and
iterate until it passes clean:

```bash
<skill-dir>/scripts/check_cc008.sh
```

`<skill-dir>` is wherever this skill is installed — typically
`.github/skills/terraform-cc008-migration/`. If you downloaded the companion
files instead, run `/tmp/cc008/check_cc008.sh`.

Called with no arguments the script discovers every module directory itself; pass
explicit directories to narrow the run:

```bash
<skill-dir>/scripts/check_cc008.sh terraform charms/foo/terraform
```

It downloads the checker from operator-workflows into a temporary directory and
removes it afterwards, so nothing is left behind to commit.

Then run the repository's Terraform quality gates:

```bash
tflint --init && tflint --recursive
terraform fmt -recursive -check
terraform -chdir=<module-dir> init -backend=false && terraform -chdir=<module-dir> test
```

## Quality Bar

- The compliance checker passes for every discovered module directory.
- `tflint --recursive` and `terraform fmt -recursive -check` are clean.
- `terraform test` passes for every module.
- Every reusable-workflow call is pinned to a commit SHA.
- The diff contains no scratch directory, no `.terraform/` artefact and no
  behavioural change beyond what CC008 requires.
