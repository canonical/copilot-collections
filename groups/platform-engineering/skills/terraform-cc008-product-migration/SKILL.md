---
name: terraform-cc008-product-migration
description: Migrates a Terraform product module (a ready-to-use solution owning its own juju_model, secrets and integrations) to the CC008 Charm Terraform Standards — proxy/logging-config/risk inputs, bundled-charm revision and OCI resource variables, the models/metadata/offers output contract, MAJOR_VERSION markers, module tests and the operator-workflows reusable CI workflows. Part of the terraform-cc008-migration skill family; use directly when a repository's modules are already known to be product modules, or let terraform-cc008-migration classify and dispatch to it.
metadata:
  author: canonical/platform-engineering
  version: "1.0.0"
---

# Terraform CC008 Migration — Product Modules

## Overview

Bring a Terraform **product module** (a module that deploys a ready-to-use
solution, owning the model(s) and integrations that tie its charms together)
up to the **CC008 — Charm Terraform Standards** specification, and wire its
repository to the compliance, test and release automation provided by
[canonical/operator-workflows](https://github.com/canonical/operator-workflows/tree/main/terraform-compliance).

This skill is one of a four-skill family. `terraform-cc008-migration` is the
family's entry point and **source of truth** for everything shared across
categories (the spec, the compliance checker, and the universal DO/DON'T
rules below) — this skill carries its own physical copy of that shared
content, tagged with `SOURCE OF TRUTH: terraform-cc008-migration/...`
comments, so it is fully self-contained: it can be fetched, read and followed
entirely on its own, with nothing to resolve outside this directory. Those
comments are maintenance metadata for whoever edits this skill family next —
they tell *editors* where to make a change first, they are not instructions
for *you* to go read `terraform-cc008-migration` before following the rules
below. Its sibling skills, `terraform-cc008-charm-migration` and
`terraform-cc008-deployment-migration`, cover the other CC008 module
categories.

## When To Use

- You already know — or `terraform-cc008-migration` classified — the module(s)
  you are migrating as **product modules**: each deploys a ready-to-use
  solution, including its own models and integrations.
- A product's Terraform module predates CC008 (CC006-era layout,
  `versions.tf`, unpinned module sources, missing reproducibility inputs).
- A new product module must be authored so that it is CC008-compliant from
  the start.
- A CC008 compliance check fails in CI for a product module and it needs to
  be corrected.

If you are not sure whether the module(s) in front of you are charm modules,
product modules or deployments, use `terraform-cc008-migration` first — it
classifies modules and either migrates them directly or dispatches to the
matching skill(s) in this family, keeping each category's migration isolated
when a repository mixes several.

<!-- SOURCE OF TRUTH: terraform-cc008-migration/SKILL.md § Source Of Truth.
     Edit there first, then copy this section here verbatim. -->

## Source Of Truth

[`assets/cc008.spec.md`](assets/cc008.spec.md) **is** the specification. Read the
sections relevant to the modules you are migrating *before* editing anything, and
resolve every question against it. This skill does not restate the spec; it only
reinforces the parts that are most often missed and describes the repository
plumbing the spec does not cover.

### Fetching The Companion Files

This skill ships two companion files next to `SKILL.md`: `assets/cc008.spec.md`
and `scripts/check_cc008.sh`. When the skill is installed as a directory — for
example synced to `.github/skills/terraform-cc008-product-migration/` — they
are already on disk and the relative paths above resolve.

When only `SKILL.md` was fetched (`copilot skill add <url>` materializes a single
file), download them first and use the downloaded copies wherever this document
refers to them:

```bash
CC008_BASE="https://raw.githubusercontent.com/canonical/copilot-collections/main/groups/platform-engineering/skills/terraform-cc008-product-migration"
CC008_TMP="$(mktemp -d -t cc008-product.XXXXXXXX)"
curl -fsSL -o "$CC008_TMP/cc008.spec.md" "$CC008_BASE/assets/cc008.spec.md"
curl -fsSL -o "$CC008_TMP/check_cc008.sh" "$CC008_BASE/scripts/check_cc008.sh"
chmod +x "$CC008_TMP/check_cc008.sh"
```

`mktemp -d` creates a directory unique to this run (e.g. `/tmp/cc008-product.a1B2c3D4`),
so concurrent migrations never collide. Delete `$CC008_TMP` once the migration is
verified; it must never be committed.

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

<!-- SOURCE OF TRUTH: terraform-cc008-migration/SKILL.md § Module Discovery And Classification.
     Edit there first, then copy this section here verbatim (product-only note added below). -->

## Module Discovery (Standalone Use)

If you were dispatched here by `terraform-cc008-migration`, it already gave
you the exact list of module directories to migrate — skip straight to the
rules below. If you are using this skill standalone, find and confirm each
module is a product module yourself before applying any rule:

```bash
find . -type f -name 'main.tf' -not -path '*/.terraform/*' -exec dirname {} \; | sort -u
```

A **product module** deploys a ready-to-use solution, including its models
and integrations; its outputs are `models` and `metadata` (plus `offers` and
sometimes `credentials`). If a candidate module's outputs look like
`application` / `provides` / `requires` (a charm module) or it owns a
`backend.tf` with no module-style outputs (a deployment), it is **not** a
product module — do not apply this skill's rules to it; use
`terraform-cc008-charm-migration` or `terraform-cc008-deployment-migration`
instead.

<!-- SOURCE OF TRUTH: terraform-cc008-migration/SKILL.md § DO - Every files.
     Edit there first, then copy this section here verbatim. -->

## DO - Every files

- Newly added file to the repository containing a copyright header, should
  be updated to refer to the current year.

<!-- SOURCE OF TRUTH: terraform-cc008-migration/SKILL.md § DO — Every Module.
     Edit there first, then copy this section here verbatim. -->

## DO — Every Module

- **DO** ensure each module has `terraform.tf`, `variables.tf`, `outputs.tf`,
  `main.tf` and `README.md`. Rename a legacy `versions.tf` to `terraform.tf`,
  leaving the content unchanged except where the next rule requires otherwise.
- **DO** require, in `terraform.tf`, a Terraform `required_version` and a
  `juju/juju` provider version that admits `>= 1.0.0` (for example `~> 1.0`, or
  `> 1.0.0, < 2.0.0`).
- **DO** order `variable` blocks in `variables.tf` and `output` blocks in
  `outputs.tf` alphabetically by name.
- **DO** set `nullable = false` on every variable that must always resolve to a
  concrete value (`app_name`, `channel`, `model_uuid`, …) so callers cannot pass
  an explicit `null` and bypass the default. Leave variables that intentionally
  default to `null` (`base`, `constraints`, `revision`, …) nullable.
- **DO** give every output a `description`.
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
  — in README examples and in product modules — to a `?ref=` tag
  or commit hash such as `?ref=tf-1.0.0`. Floating references such as branches
  are **not allowed**.

<!-- This is the category-specific section: authoritative here, not a copy. -->

## DO — Product Modules

A product module deploys a ready-to-use solution and owns the `juju_model`,
secret and integration resources tying its charms together. It does **not**
declare `requires`: everything the product needs from the outside is supplied
through input variables, and everything it offers to the outside is exposed
through `offers`.

- **DO** express every external requirement — a database, TLS, an existing
  ingress, a COS stack — as an input variable carrying the endpoint or offer to
  integrate with, rather than as a `requires` output for a caller to wire up.
- **DO** take `proxy` and `logging-config` as mandatory inputs whenever the
  module creates or manages its own `juju_model` resources, plus `risk` to
  control the channel risk of the bundled components.
- **DO** expose the charm revision **and** the OCI resources of every bundled
  charm as input variables, so deployments are reproducible and air-gap capable.
- **DO** provide a default implementation for mandatory external integrations
  (database, TLS) behind `count = 0`, so it is dropped when the user supplies
  their own endpoint or offer through the corresponding variable.
- **DO** output `models`, mapping each model key to its `model_uuid` and the
  components deployed in it, and `metadata` carrying at least `version`,
  `deployed_at` and `updated_at`. Both are mandatory.
- **DO** output `offers` and, where the solution issues them, `credentials`.

<!-- SOURCE OF TRUTH: terraform-cc008-migration/SKILL.md § DO — CI Workflows.
     Edit there first, then copy this section here verbatim. -->

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
  trigger it on pull requests touching `**/terraform/**`.
- **DO** add `.github/workflows/generate_terraform_docs.yaml` calling
  `canonical/operator-workflows/.github/workflows/generate_terraform_docs.yaml`.
  Trigger it on pushes to `main` that touch `**/terraform/**` or this workflow
  file, with these caller permissions so it can create the documentation pull
  request:

  ```yaml
  permissions:
    contents: write
    pull-requests: write
  ```
- **DO** pass every discovered module directory as a comma-separated
  `terraform-directory` input to the docs workflow. Do not rely on its default
  of `terraform` when modules live elsewhere. Ensure each module's
  `README.md` contains `<!-- BEGIN_TF_DOCS -->` and `<!-- END_TF_DOCS -->`
  markers for the generated content.
- **DO** leave the docs workflow's `auto-merge` input unset to retain its
  default of `true`. It generates the README changes and opens or updates a
  `terraform-docs` pull request after the push to `main`.
- **DO** add each of these three workflow files to *its own* `paths` filter, on
  every trigger it declares:

  ```yaml
  on:
    pull_request:
      paths:
        - '**/terraform/**'
        - '.github/workflows/terraform_modules_compliance.yaml'
  ```

  Without this, bumping the pinned reusable-workflow SHA does not run the new
  checks on the pull request that bumps it, so a breaking change in
  operator-workflows lands unverified.
- **DO** pin every new — and every pre-existing unpinned — reusable-workflow call
  to a commit SHA. Reuse the SHA already used elsewhere in the repository for
  `canonical/operator-workflows` if one exists; otherwise resolve the latest
  `main` commit yourself and pin to it with a `# main` comment, as
  platform-engineering-charm-template does:

  ```bash
  git ls-remote https://github.com/canonical/operator-workflows.git main
  ```

  Apply this SHA-pinning requirement to the Terraform docs workflow as well.

<!-- SOURCE OF TRUTH: terraform-cc008-migration/SKILL.md § DO — Repository Housekeeping.
     Edit there first, then copy this section here verbatim. -->

## DO — Repository Housekeeping

- **DO** add `**/.terraform/` and `**/.terraform.lock.hcl` to the top-level
  `.gitignore` if they are not already ignored.
- **DO** add `**/MAJOR_VERSION` to the `header.ignore` list in `.licenserc.yaml`
  so the version markers are exempt from license headers.
- **DO** add a changelog entry — in `docs/changelog.md`, or a new file under
  `docs/release-notes/artifacts/` if the repository uses that convention —
  describing the CC008 migration and any breaking default change (for example
  `expose` now defaulting to `{}` instead of `null`).

<!-- SOURCE OF TRUTH: terraform-cc008-migration/SKILL.md § DON'T.
     Edit there first, then copy this section here verbatim. -->

## DON'T

- **DON'T** change any module's deployment behaviour — resource arguments,
  variable defaults — beyond what CC008 requires. Preserve existing defaults
  unless the spec mandates a different one.
- **DON'T** give a product module itself the charm-module contract — no
  single `app_name`/`channel`/`revision` input *on the product module*, no
  `application` output, and no `provides` / `requires`. (This is distinct from
  — and does not override — the requirement above, under "DO — Product
  Modules", to expose each *bundled charm's* revision and OCI resources as
  their own input variables.)
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
- **DON'T** document *requirements*, *providers*, *modules*, *resources*, *inputs*
  or *outputs* yourself in the terraform README.md. This will be handle by the
  automated doc generation workflow.

<!-- SOURCE OF TRUTH: terraform-cc008-migration/SKILL.md § Validate Before Declaring Done.
     Edit there first, then copy this section here verbatim. -->

## Validate Before Declaring Done

Do not guess at compliance. Run the checker against every discovered module and
iterate until it passes clean:

```bash
<skill-dir>/scripts/check_cc008.sh
```

`<skill-dir>` is wherever this skill is installed — typically
`.github/skills/terraform-cc008-product-migration/`. If you downloaded the
companion files instead, run `$CC008_TMP/check_cc008.sh` (the session-scoped
directory created above).

Called with no arguments the script discovers every module directory itself; pass
explicit directories to narrow the run:

```bash
<skill-dir>/scripts/check_cc008.sh terraform/product-foo
```

It downloads the checker from operator-workflows into a temporary directory and
removes it afterwards, so nothing is left behind to commit.

Then run the repository's Terraform quality gates:

```bash
tflint --init && tflint --recursive
terraform fmt -recursive -check
terraform -chdir=<module-dir> init -backend=false && terraform -chdir=<module-dir> test
```

<!-- SOURCE OF TRUTH: terraform-cc008-migration/SKILL.md § Quality Bar.
     Edit there first, then copy this section here verbatim. -->

## Quality Bar

- The compliance checker passes for every discovered module directory.
- Every module was confirmed to be a product module before editing.
- `tflint --recursive` and `terraform fmt -recursive -check` are clean.
- `terraform test` passes for every module.
- Every reusable-workflow call is pinned to a commit SHA, and every terraform
  workflow lists its own file in its `paths` filter.
- The Terraform docs workflow passes all discovered module directories,
  targets README files with the Terraform docs markers, and retains the default
  auto-merge behavior.
- The diff contains no scratch directory, no `.terraform/` artefact and no
  behavioural change beyond what CC008 requires.
