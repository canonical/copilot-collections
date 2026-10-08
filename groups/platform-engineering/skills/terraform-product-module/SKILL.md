---
name: terraform-product-module
description: 'Create, migrate or review a Terraform product module (a ready-to-use Juju solution tying charm modules together with models, secrets and integrations) following the CC008 Charm Terraform Standards. Use when a Terraform module deploys several integrated charms.'
argument-hint: 'Path to a product Terraform module directory, or leave blank to review the current directory.'
allowed-tools: terraform, tofu
---

# Product Terraform module

A product module deploys a solution and owns the `juju_model`, secret and integration resources tying its charm modules together.
Shared rules (file layout, ordering, CI, housekeeping, validation) are in the `terraform-modules` skill; apply them as well.

## Process

1. Read the module's `.tf` files and `README.md`; list the bundled charm modules.
2. Apply the contract below.
3. Validate with the command from `terraform-modules`.

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

## Constraints

- DO NOT declare `requires` outputs; inputs and `offers` cover the product boundary.
- DO NOT give the product the charm-module contract: no single `app_name`/`channel`/`revision` input for the product itself, no `application` output.
- DO pin every charm, component or product module source to a tag or commit. A product module in the same repository may use a relative path.
