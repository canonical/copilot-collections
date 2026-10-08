---
name: terraform-product-module
description: 'Create, migrate or review a Terraform product module (a ready-to-use Juju solution tying charm modules together with models, secrets and integrations) following the CC008 Charm Terraform Standards. Use when a Terraform module deploys several integrated charms.'
argument-hint: 'Path to a product Terraform module directory, or leave blank to review the current directory.'
allowed-tools: terraform, tofu
---

# Product Terraform module

A product module deploys a solution and owns the `juju_model`, secret and integration resources tying its charm modules together.

## Process

1. Read the module's `.tf` files and `README.md`; list the bundled charm modules.
2. Apply the contract below.
3. Apply the module rules, set up the repository and validate (below).

## Inputs

- Mandatory: `risk` (`string`, channel risk of the bundled components).
- Mandatory when the module creates or manages its own `juju_model`: `proxy` (`object({ http, https, no-proxy })`) and `logging-config` (`string`).
- Expose the charm revision **and** the OCI resources of every bundled charm, so deployments are reproducible and air-gap capable. Defaults are `null` (latest on the channel) or tested revisions.
- Express every external requirement (database, TLS, ingress, COS) as an input carrying the endpoint or offer to integrate with.
- Provide a default implementation for mandatory external integrations (database, TLS) with `count = 0` when the user supplies their own.
- Recommended: reuse the charm modules' input names (flat for charm modules, nested objects for component modules) to configure bundled charms.

## Outputs

- `models` (mandatory): `map(object)` from model key to `{ model_uuid, components = { <name> = <module>.application } }`.
- `metadata` (mandatory): object with at least `version`, `deployed_at`, `updated_at`.
- `offers` (optional): `map(string)` of offer name to URL.
- `credentials` (optional): `map(object)` such as `{ url, username, password, ca }`.

## Secrets

When creating `juju_secret` from input variables, mark each credential variable `sensitive = true` and `ephemeral = true`, use `value_wo` with `value_wo_version` (a separate rotation number variable) and a separate boolean to control creation. Requires Terraform/OpenTofu `>= 1.11` and provider `>= 2.2.1`. See the "Product modules" section of the CC008 spec (DA289) for the full pattern.

## Module rules

- Provide `README.md`, `terraform.tf`, `main.tf`, `variables.tf` and `outputs.tf`. Add `locals.tf` only when needed, and `providers.tf` for provider configuration. Rename a legacy `versions.tf` to `terraform.tf`.
- `terraform.tf` holds a single `terraform` block with `required_version` and a `juju/juju` constraint admitting `>= 1.0.0` (for example `~> 1.0`).
- Keep `variable`, `output` and `locals` entries in alphabetical order.
- Set `nullable = false` on variables that must always resolve to a value (`app_name`, `channel`, `model_uuid`, ...). Leave variables that default to `null` (`base`, `constraints`, `revision`, ...) nullable.
- Give every output a `description`.
- Add `terraform/MAJOR_VERSION` per independently tagged module family: the major version only, no trailing newline, starting at `1`. Use a relative symlink only for modules sharing a release train.
- Add `tests/main.tftest.hcl` with `mock_provider "juju"` asserting key outputs, if missing.
- Pin every `source = "git::...//terraform..."` (README examples, product modules) to a tag or commit, such as `?ref=tf-1.0.0`. No branches.
- Keep `<!-- BEGIN_TF_DOCS -->` and `<!-- END_TF_DOCS -->` markers in `README.md` for generated docs.
- Use plain English in documentation and descriptions, no Latin phrases.
- Update the year in the copyright header of newly added files.
- Do not change deployment behaviour (resource arguments, defaults) beyond what CC008 requires.

## Repository setup

Call the reusable workflows of `canonical/operator-workflows`; do not hand-write release logic.

| File in `.github/workflows/` | Calls | Trigger and inputs |
| :--- | :--- | :--- |
| `terraform_modules_release.yaml` | `terraform_modules_release.yaml` | push to `main`, PRs touching `terraform/**`; `permissions: contents: write` |
| `terraform_modules_compliance.yaml` | `terraform_modules_compliance.yaml` | PRs touching `**/terraform/**`; `terraform-directories` |
| `test_terraform_modules.yaml` | `terraform_modules_test.yaml` | PRs touching `**/terraform/**`; `terraform-directories` |
| `generate_terraform_docs.yaml` | `generate_terraform_docs.yaml` | push to `main` touching `**/terraform/**`; `terraform-directory`; `permissions: contents: write, pull-requests: write`; keep default `auto-merge` |

- List every module directory (comma-separated) in the directory inputs; do not rely on the `terraform` default.
- List each workflow's own file in the `paths` of every trigger it declares, so bumping the pinned SHA runs the new checks.
- Pin every `canonical/operator-workflows` call to a commit SHA: reuse the repository's existing one, else `git ls-remote https://github.com/canonical/operator-workflows.git main` with a `# main` comment. Never leave `@main`.
- Add `**/.terraform/` and `**/.terraform.lock.hcl` to `.gitignore`, and `**/MAJOR_VERSION` to `header.ignore` in `.licenserc.yaml`.
- Add a changelog entry (`docs/changelog.md`, or `docs/release-notes/artifacts/` if used) describing the migration and any breaking default change (for example `expose` now defaulting to `{}`).
- Do not touch charm source, `charmcraft.yaml` or unrelated workflows, and do not commit `.terraform/` artefacts.

## Validate

The compliance check is the arbiter; iterate until it passes.

```bash
uvx --from "git+https://github.com/canonical/operator-workflows@feat/terraform-full-compliance#subdirectory=terraform-compliance" terraform-check-all .
tflint --init && tflint --recursive
terraform fmt -recursive -check
terraform -chdir=<module-dir> init -backend=false && terraform -chdir=<module-dir> test
```

## Constraints

- DO NOT declare `requires` outputs; inputs and `offers` cover the product boundary.
- DO NOT give the product the charm-module contract: no single `app_name`/`channel`/`revision` input for the product itself, no `application` output.
- DO pin every charm, component or product module source to a tag or commit. A product module in the same repository may use a relative path.
