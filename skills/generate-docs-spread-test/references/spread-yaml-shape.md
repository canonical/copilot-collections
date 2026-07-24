# Target `spread.yaml` Shape

Derive the charm name from `charmcraft.yaml` or `metadata.yaml` (`name:` field).

## Required structure

```yaml
# Copyright <year> Canonical Ltd.
# See LICENSE file for licensing details.
project: <charm-name>
path: /<charm-name>
kill-timeout: 90m

environment:
  PROJECT_PATH: /<charm-name>
  SUDO_USER: ""
  SUDO_UID: ""
  LANG: "C.UTF-8"
  LANGUAGE: "en"

exclude:
  - .git
  - .github
  - .tox
  - .venv
  - .*_cache
  - charmcraft

backends:
  github-ci:
    type: adhoc
    allocate: |
      echo "Allocating ad-hoc $SPREAD_SYSTEM"
      if [ -z "${GITHUB_RUN_ID:-}" ]; then
        FATAL "this back-end only works inside GitHub CI"
        exit 1
      fi
      echo "ubuntu ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/99-spread-users
      ADDRESS localhost:22
    discard: |
      echo "Discarding ad-hoc $SPREAD_SYSTEM"
    systems:
      - ubuntu-24.04-64:
          username: ubuntu
          password: ubuntu
          workers: 1

suites:
  tests/spread/:
    summary: <Charm-name> charm tutorial test
    systems:
      - ubuntu-24.04-64
    prepare: |
      # Bootstrap concierge, MicroK8s, Juju, model, /etc/hosts.
      # Use the commands from docs/tutorial.md.
    restore: |
      # Undo /etc/hosts change if prepare made it.
```

The `github-ci` backend block above must be used **verbatim** (from
`canonical/operator-workflows/spread.yaml`). Do not invent an LXD, Multipass,
or QEMU backend.
