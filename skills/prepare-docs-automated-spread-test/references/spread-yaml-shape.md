# Target `spread.yaml` Shape

Derive the charm's name from `charmcraft.yaml` or `metadata.yaml` (the
`name:` field). Fall back to the repository directory name only if neither
file provides a name.

If `spread.yaml` already exists at the repository root, do **not** overwrite
it. Record the conflict as a follow-up and leave the file untouched.

## Required structure

The generated file must:

- Begin with the copyright header (use the current year):
  ```
  # Copyright <year> Canonical Ltd.
  # See LICENSE file for licensing details.
  ```
- Set `project: <charm-name>`, `path: /<charm-name>`, `kill-timeout: 90m`.
- Set `environment` with `PROJECT_PATH: /<charm-name>`, empty `SUDO_USER`
  and `SUDO_UID`, `LANG: "C.UTF-8"`, `LANGUAGE: "en"`.
- Set `exclude` to `[.git, .github, .tox, .venv, .*_cache, charmcraft,
  libexec, schema, snap]`.
- Define `backends.github-ci` as a verbatim copy of the adhoc block from the
  synapse reference (`type: adhoc`, `allocate` that requires
  `GITHUB_RUN_ID`, `ADDRESS localhost:22`, a single
  `ubuntu-24.04-64` system with `username: ubuntu`, `password: ubuntu`,
  `workers: 1`).
- Provide a project-level `prepare:` that installs concierge and runs
  `sudo concierge prepare -p microk8s`, matching the synapse reference.
- Declare `suites: tests/spread/:` with `summary: Charm tutorial test` and
  `systems: [ubuntu-24.04-64]`.

## Reference example

See the synapse-operator spread.yaml for a working example:
<https://github.com/canonical/synapse-operator/blob/track/1/spread.yaml>
