---
description: 'Guidelines for GitHub Copilot when writing, reviewing or refactoring Terraform plans in Canonical "terraform-plans" style repositories (module + environments layout, Juju provider, S3-compatible remote state).'
applyTo: '**/*.tf,**/*.tfvars,Makefile'
---

# Terraform Plan Repository Instructions

These instructions apply to repositories that manage infrastructure 
as Terraform "plans" following Canonical's common layout.

## Repository Layout

- `modules/<name>/` — reusable, environment-agnostic building blocks. Each module owns its own
  `main.tf`, `variables.tf`, and `versions.tf` (provider/version pins). Modules must not hardcode
  environment-specific values (model names, secrets, hostnames) — accept them as variables.
- `environments/<env>/` — one directory per deployment target (e.g. `stg`, `prod`). Each environment
  wires modules together via `main.tf`, declares its own `backend.tf` (remote state), `versions.tf`,
  and `variables.tf`/`*.tfvars`. Do not duplicate module logic inside an environment directory —
  compose modules instead.
- `scripts/` — helper scripts invoked by the `Makefile` (e.g. secret generation, backend bootstrap).
- Root `Makefile` — the single entry point for linting, formatting and (where present) applying.

## Module Conventions

- Keep `variables.tf` typed and documented: every variable has `description` and `type`; prefer
  `optional(...)` with sensible defaults over required variables when a safe default exists.
- Use `object({...})` types to group related configuration (e.g. charm deployment config) instead of
  many loose scalar variables.
- Pin provider versions in each module's `versions.tf` (`required_version`, `required_providers`).
  Don't rely on the environment's pin alone — modules should be usable independently.
- Favor small, single-purpose modules (one Juju application/integration group per module) over large
  multi-purpose modules.

## Environment Conventions

- Each environment must define its own `backend.tf` using the shared S3-compatible remote state
  convention:
  ```hcl
  terraform {
    backend "s3" {
      endpoints = { s3 = "https://radosgw.ps6.canonical.com" }
      bucket                      = "<env>-<system>-tfstate"
      region                      = "prodstack6"
      key                         = "state"
      skip_region_validation      = true
      skip_credentials_validation = true
      skip_requesting_account_id  = true
      skip_s3_checksum            = true
      use_path_style              = true
    }
  }
  ```
- Never commit real secret values into `.tf`/`.tfvars`. Reference Juju secrets, Vault paths, or
  environment variables instead.
- Keep `stg`/`prod` (and any other environment) structurally symmetrical — a module wired into one
  environment should be wired the same way (same variable names/shapes) in the others, differing
  only in values.

## Linting, Formatting & CI

- All repos expose a standard `Makefile` contract; do not invent new target names.
  - `make fmt` → `terraform fmt -recursive`
  - `make lint` → `terraform fmt -recursive -check`, then `make lint-terraform-env` for every
    environment (`TERRAFORM_ENV=<env>`).
  - `lint-terraform-env` → `cd environments/$(TERRAFORM_ENV) && terraform init -backend=false && terraform validate` (add `-upgrade`/`-input=false` only if the repo already does so consistently).
- When adding a new environment, add it to the `lint` target's `TERRAFORM_ENV=` loop so CI covers it.
- Prefer `snap`-installed tooling guarded by existence checks (see `$(TERRAFORM)`, `$(JUJU)`, `$(YQ)`
  targets) over assuming tools are pre-installed.

## Review Guidance (for Copilot code review)

- Flag any hardcoded secret, credential, or environment-specific literal (hostnames, model names)
  inside a `modules/` directory — these belong in `environments/`.
- Flag missing `description`/`type` on new variables.
- Flag new environments that lack a `backend.tf`, or whose `backend.tf` diverges from the shared
  S3-compatible convention without explanation.
- Flag drift between environments — e.g. a module argument set in `prod` but silently omitted in
  `stg` — and ask whether the omission is intentional.
- Flag `terraform.tfstate`/`*.tfstate.backup` files being committed; state must live in the remote
  S3-compatible backend, never in git.
- Prefer `terraform fmt`-clean diffs; suggest running `make fmt` before requesting review.
