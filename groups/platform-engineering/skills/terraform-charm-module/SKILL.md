---
name: terraform-charm-module
description: 'Create, migrate or review a Terraform module for a single Juju charm following the CC008 Charm Terraform Standards: mandatory and optional variables, and the application/provides/requires/offers outputs. Use when a Terraform module deploys one charm with the Juju provider.'
argument-hint: 'Path to a charm Terraform module directory, or leave blank to review the current directory.'
allowed-tools: terraform, tofu
---

# Charm Terraform module

A charm module wraps one charm. It is only required if the charm can be used standalone.
Shared rules (file layout, ordering, CI, housekeeping, validation) are in the `terraform-modules` skill; apply them as well.

## Process

1. Read the module's `.tf` files and `README.md`, and the charm's `charmcraft.yaml` (walk up from `terraform/`) for its name, `provides`/`requires` endpoints and `subordinate:` key.
2. Define inputs in `variables.tf`, outputs in `outputs.tf`, and the `juju_application` in `main.tf`.
3. Validate with the command from `terraform-modules`.

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

## Constraints

- DO NOT add `units` for subordinate charms.
- DO NOT give a charm module product outputs (`models`, `metadata`).
