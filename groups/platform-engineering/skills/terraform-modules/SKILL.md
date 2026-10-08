---
name: terraform-modules
description: 'Create, migrate or review the Terraform modules of a repository against the CC008 Charm Terraform Standards. Use first whenever Terraform modules for Juju charms or products are written, restructured or audited; it classifies each module and covers the rules shared by all of them (layout, versioning marker, CI workflows, housekeeping, validation).'
argument-hint: 'Path to a Terraform module directory, or leave blank to process every module in the repository.'
allowed-tools: terraform, tofu
---

# Terraform modules (CC008)

Brings every Terraform module of a repository to the
CC008 Charm Terraform Standards
and wires it to the
[operator-workflows](https://github.com/canonical/operator-workflows/tree/main/terraform-compliance)
automation. The spec assumes the Juju Terraform provider is `>= 1.0.0`.
The reference implementation is
[platform-engineering-charm-template/terraform](https://github.com/canonical/platform-engineering-charm-template/tree/main/terraform): copy its patterns.

## Process

1. **Discover** every module: each directory with a `main.tf` (or legacy `versions.tf`).

   ```bash
   find . -name main.tf -not -path '*/.terraform/*' -exec dirname {} \; | sort -u
   ```

2. **Classify** each module, then follow the matching skill. Apply only that category's contract.

   | Category | Deploys | Skill |
   | :--- | :--- | :--- |
   | Charm module | a single charm | `terraform-charm-module` |
   | Product module | a ready-to-use solution, including models and integrations | `terraform-product-module` |

   Component modules (several charms sharing one release cycle) and deployments are out of scope.

3. **Apply the shared rules** below to every module.
4. **Set up CI and housekeeping** once for the repository.
5. **Validate** (see below) and iterate until clean.

## Rules for every module

- Provide `README.md`, `terraform.tf`, `main.tf`, `variables.tf` and `outputs.tf`. Add `locals.tf` only when local values are needed, and `providers.tf` for provider configuration. Rename a legacy `versions.tf` to `terraform.tf`.
- `terraform.tf` holds a single `terraform` block with `required_version` and a `juju/juju` constraint admitting `>= 1.0.0` (for example `~> 1.0`).
- Keep `variable`, `output` and `locals` entries in alphabetical order.
- Set `nullable = false` on variables that must always resolve to a value (`app_name`, `channel`, `model_uuid`, ...). Leave variables that default to `null` (`base`, `constraints`, `revision`, ...) nullable.
- Give every output a `description`.
- Add `terraform/MAJOR_VERSION` per independently tagged module family: the major version only, no trailing newline, starting at `1`. Use a relative symlink to it only for modules sharing the same release train.
- Add `tests/main.tftest.hcl` with `mock_provider "juju"` asserting key outputs, if the module has no test.
- Pin every `source = "git::...//terraform..."` (README examples, product modules) to a tag or commit: `?ref=tf-1.0.0`. No branches.
- README keeps `<!-- BEGIN_TF_DOCS -->` and `<!-- END_TF_DOCS -->` markers for generated docs.
- Use plain English in documentation and descriptions, no Latin phrases.
- Update the year in the copyright header of newly added files.

## CI workflows

Call the reusable workflows of `canonical/operator-workflows`; do not hand-write tagging or release logic.

| File in `.github/workflows/` | Calls | Trigger |
| :--- | :--- | :--- |
| `terraform_modules_release.yaml` | `terraform_modules_release.yaml` | push to `main`, PRs touching `terraform/**`; `permissions: contents: write` |
| `terraform_modules_compliance.yaml` | `terraform_modules_compliance.yaml` | PRs touching `**/terraform/**`; `terraform-directories` input |
| `test_terraform_modules.yaml` | `terraform_modules_test.yaml` | PRs touching `**/terraform/**`; `terraform-directories` input |
| `generate_terraform_docs.yaml` | `generate_terraform_docs.yaml` | push to `main` touching `**/terraform/**`; `terraform-directory` input; `permissions: contents: write, pull-requests: write`; leave `auto-merge` at its default |

- Pass every module directory (comma-separated) to the `terraform-directories` / `terraform-directory` input; do not rely on the `terraform` default.
- List each workflow's own file in the `paths` of every trigger it declares, so bumping the pinned SHA runs the new checks on that PR.
- Pin every `canonical/operator-workflows` call to a commit SHA, reusing the repository's existing one, or else `git ls-remote https://github.com/canonical/operator-workflows.git main` with a `# main` comment. Never leave `@main`.

## Housekeeping

- Add `**/.terraform/` and `**/.terraform.lock.hcl` to `.gitignore`.
- Add `**/MAJOR_VERSION` to `header.ignore` in `.licenserc.yaml`.
- Add a changelog entry (`docs/changelog.md`, or `docs/release-notes/artifacts/` if used) describing the migration and any breaking default change (for example `expose` now defaulting to `{}`).

## Constraints

- DO NOT change deployment behaviour (resource arguments, defaults) beyond what CC008 requires.
- DO NOT touch charm source, `charmcraft.yaml` or unrelated workflows.
- DO NOT commit `.terraform/` artefacts or scratch files.
- DO NOT declare done on inspection alone: the compliance check is the arbiter.

## Validate

```bash
uvx --from "git+https://github.com/canonical/operator-workflows@feat/terraform-full-compliance#subdirectory=terraform-compliance" terraform-check-all .
tflint --init && tflint --recursive
terraform fmt -recursive -check
terraform -chdir=<module-dir> init -backend=false && terraform -chdir=<module-dir> test
```
