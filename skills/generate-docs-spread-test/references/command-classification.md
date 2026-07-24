# Command Classification by Spread Phase

Extract shell commands from `docs/tutorial.md` in tutorial order. Do not
paraphrase or reorder them. Assign each command to one of these Spread
lifecycle phases:

## Project-level `prepare:`

Cluster bootstrap that must run once before the task:

- `snap install --classic concierge`
- `concierge prepare -p microk8s`
- `microk8s enable ingress`
- `juju add-model <model-name>`
- Add hostnames to `/etc/hosts`

## Task `execute:`

The tutorial's deploy chain, integrate chain, config steps, wait-for-active
checks, and smoke tests:

- `juju deploy` commands
- `juju integrate` commands
- `juju config` commands
- `juju deploy nginx-ingress-integrator` (or equivalent ingress)
- `juju trust ... --scope cluster` when RBAC is enabled (make unconditional)
- `juju integrate <app> nginx-ingress-integrator`
- Wait for Active — replace narrative waits with deterministic checks:
  `juju wait-for application <app> --query='status=="active"' --timeout=30m`
  for each deployed application
- HTTP smoke check — use Spread's `MATCH` helper:
  `curl -sSf http://<hostname> | MATCH "<expected marker>"`

## Task `restore:`

Cleanup that undoes the task's effects:

- `juju destroy-model <model-name> --no-prompt --destroy-storage=true || true`
- Revert `/etc/hosts` changes if prepare made them
- No VM teardown — `github-ci` runs on the runner itself

## Spread quick reference

- Cascade order: `project` → `backend` → `system` → `suite` → `task`. Each
  level may set `environment`, `prepare`, `restore`, `prepare-each`,
  `restore-each`, `debug`, and `debug-each`.
- Helpers available inside scripts:
  `MATCH` (assert stdin matches a pattern), `NOMATCH` (assert it doesn't),
  `ERROR` (fail with a message), `FATAL` (fail without retry — adhoc only).
- `path:` sets the remote base directory the project is uploaded into.
- `exclude:` filters out repo files that should not be shipped to the system.
- `kill-timeout:` bounds task/suite execution.
