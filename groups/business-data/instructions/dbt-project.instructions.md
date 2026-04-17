---
applyTo: "**"
---

# dbt Project — Copilot Instructions

## Overview

This repository contains dbt (data build tool) models for data transformations run against a **Trino**-based federated data platform. It is structured as a fork of Canonical's dbt template. Data is read from source catalogs and written to a team workspace catalog via Trino.

The repository may contain one or more **catalog directories** at the root level. Each catalog directory corresponds to a single Trino target catalog and is a self-contained dbt project.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Transformation engine | dbt Core ^1.8 |
| Data platform | Trino (via `dbt-trino`) |
| Package manager | Poetry |
| SQL linter/formatter | SQLFluff ^3.3 (dialect: `trino`, templater: `dbt`) |
| YAML linter | yamllint |
| Environment variables | python-dotenv |
| CI | GitHub Actions |
| Scheduling | Custom `schedules.yml` + deployed Temporal worker |

---

## Repository Structure

```
<root>/
├── .env                        # Local environment variables (not committed)
├── pyproject.toml              # Poetry dependencies (shared across all catalogs)
├── poetry.lock
├── install.sh                  # Installs poetry + dependencies
├── <catalog-name>/             # One directory per target Trino catalog
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── schedules.yml
│   ├── packages.yml
│   ├── Makefile
│   ├── .sqlfluff
│   ├── models/
│   │   ├── staging/            # Raw → cleaned; one subdir per source
│   │   ├── intermediate/       # Complex transformations
│   │   └── marts/              # Final business-layer tables
│   ├── seeds/                  # CSV static data files
│   ├── macros/                 # Shared SQL macros
│   ├── snapshots/
│   └── analyses/
└── .github/
    ├── config/
    │   ├── yaml_rules.yaml     # yamllint configuration
    │   └── sql_rules.toml      # SQLFluff CI configuration
    └── workflows/
        └── ci.yaml             # Lint + validate on PRs
```

The catalog directory name must exactly match:
- The `name` and `profile` keys in `dbt_project.yml`
- The root key in `profiles.yml`
- The `profile` key in `.sqlfluff`
- The `APP_TARGET` environment's catalog references

---

## Build & Run Commands

All commands are run from inside the relevant **catalog directory** using `make`:

```bash
make run      # dbt run — build models in the data platform
make test     # dbt test — run schema and data tests
make build    # dbt build — test + run
make seed     # dbt seed — load CSV seeds
make docs     # dbt docs generate — generate documentation site
make lint     # yamllint + sqlfluff lint
make fmt      # sqlfluff format — auto-format SQL files
make clean    # dbt clean — remove target/ and dbt_packages/
```

To pass dbt CLI options directly:
```bash
poetry run dotenv -f ../.env run dbt [command] [options]
```

Install dependencies from the repository root:
```bash
./install.sh
```

---

## Environment Variables

Keep a single `.env` file at the **repository root** (not inside catalog directories). It is consumed by `dotenv -f ../.env` in the Makefile.

```env
DBT_ENV_<CATALOG>_TRINO_HOST=<hostname>   # e.g. trino.canonical.com
DBT_ENV_<CATALOG>_TRINO_SCHEMA=<schema>   # e.g. dbt_dev
```

Authentication uses **Google OAuth** for `dev` and **JWT** for `prod`. The `.env` file must never be committed.

---

## Linting & Formatting

SQL and YAML rules are defined in and enforced by the linter config files — treat those as the source of truth:

- **SQL:** `.sqlfluff` (per catalog directory) and `.github/config/sql_rules.toml` (CI)
- **YAML:** `.github/config/yaml_rules.yaml`

Run `make lint` to check, and `make fmt` to auto-format SQL before opening a PR.

---

## Model Layering Convention

Follow the three-layer architecture strictly:

### `staging/`
- **Purpose:** Bring raw source data into the project with minimal, consistent transformations.
- **Allowed operations:** Column renaming, type casting, basic computations, conditional categorization.
- **Forbidden:** Joins, aggregations (unless strictly necessary).
- **Sources:** This is the **only** layer that references `{{ source(...) }}`.
- **Subdirectory convention:** One subdirectory per data source (e.g. `staging/salesforce/`).
- **Naming:** `stg_[source]__[entity]s.sql` (use plurals where sensible).
- **Materialization:** `table` (views are not supported by Trino).

### `intermediate/`
- **Purpose:** Complex transformations, joins, and aggregations that serve multiple downstream models.
- **Subdirectory convention:** Group by business logic domain.
- **Forbidden:** Direct references to `{{ source(...) }}`; reference only staging or other intermediate models.
- **Naming:** `int_[entity]__[verb]s.sql` — the verb describes the transformation (e.g. `int_orders__pivoted.sql`, `int_sessions__joined.sql`).
- **Materialization:** `ephemeral` by default. Use `table` when results need to be cached for performance (e.g. when the model is referenced by multiple downstream marts).

### `marts/`
- **Purpose:** Final, business-ready models for consumption in dashboards and downstream tools.
- **Subdirectory convention:** Group by consumer or business area.
- **Naming:** By entity, e.g. `accounts.sql`, `opportunities.sql`.
- **Materialization:** `table`.

---

## Schema & Documentation Files

Each model subdirectory should contain YAML schema files following this naming convention:

```
_<source>__models.yml     # Model column definitions and tests
_<source>__sources.yml    # Source declarations (staging layer only)
_<source>__docs.md        # Extended descriptions (optional)
```

Every model should have:
- A `description` field.
- Column-level descriptions for all significant columns.
- At minimum `unique` and `not_null` tests on primary key columns.

---

## Seeds

Place CSV files in `seeds/` within the catalog directory. Document them in `seeds/properties.yml` with column descriptions and data tests. Seeds are materialized into the `seed_data` schema.

---

## Scheduling

Each catalog directory contains a `schedules.yml` file. The deployed Temporal worker reads this to schedule automated runs.

```yaml
schedules:
  - name: <unique_descriptive_name>   # Convention: <project>__<model>__<frequency>
    models:
      - +<model_name>                 # Use + prefix to include ancestors
    interval: "0 17 * * *"           # Cron format; minute-level not supported
    target:
      - prod                          # Must match APP_TARGET env var on the worker
    full-refresh: false               # Optional; passes --full-refresh to dbt (default: false)
    exclude:                          # Optional; passes --exclude to dbt (default: none)
      - <model_to_exclude>
```

**Attributes:**

| Key | Type | Default | Description |
|---|---|---|---|
| `name` | string | required | Unique identifier for the schedule |
| `models` | list[str] | required | Models to build; supports dbt graph operators |
| `interval` | string | required | Cron expression; minute-level granularity not guaranteed |
| `target` | list[str] | required | Must match `APP_TARGET` on the worker to activate |
| `full-refresh` | bool | `false` | Runs dbt with `--full-refresh`, rebuilding incremental models from scratch |
| `exclude` | list[str] | `[]` | Models to exclude from the run, passed as `--exclude` to dbt |

Use dbt graph operators (`+model`, `model+`, `@model`) in `models` and `exclude` to control which ancestors/descendants are included or skipped.

---

## CI Pipeline

The CI workflow runs on all pull requests targeting `main`:

1. **Detect changed directories** — only lints catalog directories with modified files.
2. **Lint YAML** — runs `yamllint` with `.github/config/yaml_rules.yaml`.
3. **Validate YAML** — validates `schedules.yml` against `.github/config/schedules_schema.json`.
4. **Lint SQL** — runs `sqlfluff lint models` with `.github/config/sql_rules.toml`.

All three lint steps run independently (`success() || failure()`). Fix all reported issues before merging.

---

## dbt Features to Use

- **Graph operators** for selective builds: `+model` (with ancestors), `model+` (with descendants), `@model` (full family).
- **Model versions:** Define multiple versions in schema YAML to allow staged rollouts.
- **Data tests:** Add `unique`, `not_null`, `accepted_values`, and `relationships` tests in schema YAML files.
- **Unit tests:** Use dbt unit tests with mock data for models with complex logic.
- **Packages:** Declare dbt packages in `packages.yml`; install with `dbt deps`.

---

## Key Principles

- Each catalog directory is an independent dbt project. Keep configurations self-contained within it.
- Reusability over convenience: prefer filtering in intermediate models rather than staging, so staging models can serve multiple downstream use cases.
- Sources are declared once, in staging. Never reference `{{ source(...) }}` from intermediate or marts.
- The `template/` directory in the repo root is a reference example — copy it; do not modify it directly.
- Store all secrets and credentials in environment variables or a secrets manager. Never commit credentials.
