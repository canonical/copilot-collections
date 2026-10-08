---
name: terraform-charm-module
description: 'Create, migrate or review a Terraform module for a single Juju charm following the CC008 Charm Terraform Standards: mandatory and optional variables, and the application/provides/requires/offers outputs. Use when a Terraform module deploys one charm with the Juju provider.'
argument-hint: 'Path to a charm Terraform module directory, or leave blank to review the current directory.'
allowed-tools: terraform, tofu
---

# Charm Terraform module

A charm module wraps one charm. It is only required if the charm can be used standalone.

## Process

1. Read the module's `.tf` files and `README.md`, and the charm's `charmcraft.yaml` (walk up from `terraform/`) for its name, `provides`/`requires` endpoints and `subordinate:` key.
2. Define inputs in `variables.tf`, outputs in `outputs.tf`, and the `juju_application` in `main.tf`.
3. Apply the module rules, set up the repository and validate (below).

## Mandatory inputs

| Name | Type | Default | Notes |
| :--- | :--- | :--- | :--- |
| `app_name` | `string` | charm-specific, non-null | |
| `channel` | `string` | charm-specific, non-null | not nullable if the default would be `null` |
| `config` | `map(string)` | `{}` | |
| `constraints` | `string` | `null` | |
| `model_uuid` | `string` | none | not nullable |
| `revision` | `number` | `null` | `null` deploys the latest on the channel |
| `units` | `number` | `1` | omit for subordinate charms |

Subordinate means `subordinate: true` in `charmcraft.yaml`; a missing key means not subordinate. Decide from the file, never from the charm's name or description. The checker treats `units` as optional, so it will not catch a mistake.

## Optional inputs

If present, use these names and types (matching the `juju_application` schema).

| Name | Type | Default |
| :--- | :--- | :--- |
| `base` | `string` | `null` |
| `endpoint_bindings` | attribute set | `{}` |
| `expose` | block list | `{}` |
| `machines` | `set(string)` | `[]` |
| `offered_endpoints` | `list(string)` | `[]` |
| `resources` | `map(string)` | `{}` |
| `storage_directives` | `map(string)` | `{}` |

Other inputs are allowed.

## Outputs

- `application` (mandatory): the resource itself, `value = juju_application.<name>`, not its `.name`.
- `provides` / `requires`: `map(object)`, one key per endpoint the charm declares, mandatory as soon as it declares any (`value = {}` otherwise). Replace any legacy `endpoint`/`endpoints` output.
- `offers` (optional): `map(object)` of offers, keys compatible with the endpoint names.

```hcl
output "application" {
  value = juju_application.<charm>
}

output "provides" {
  value = {
    metrics = {
      kind     = "endpoint"
      name     = juju_application.<charm>.name
      endpoint = "prometheus-metrics"
    }
  }
}

output "offers" {
  value = {
    metrics = {
      kind = "offer"
      url  = <offer-url>
    }
  }
}
```

Add `controller = null` to an endpoint entry when the relation supports cross-model integration.

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

- DO NOT add `units` for subordinate charms.
- DO NOT give a charm module product outputs (`models`, `metadata`).
