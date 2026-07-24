# Target `tests/spread/tutorial/task.yaml` Shape

## Required structure

```yaml
# Copyright <year> Canonical Ltd.
# See LICENSE file for licensing details.
summary: Deploy <charm-name> end-to-end following docs/tutorial.md
kill-timeout: 60m
execute: |
  # 1. juju deploy chain (e.g. postgresql-k8s --trust, redis-k8s, main app).
  # 2. juju integrate chain.
  # 3. juju config commands.
  # 4. juju deploy ingress; juju trust ... --scope cluster if RBAC.
  # 5. juju integrate <app> <ingress>.
  # 6. juju wait-for application <app> --query='status=="active"' --timeout=30m
  #    for each deployed application.
  # 7. curl -sSf http://<hostname> | MATCH "<expected marker>".
restore: |
  juju destroy-model <model-name> --no-prompt --destroy-storage=true || true
```

## Key rules

- **Verbatim commands**: Extract shell commands from `docs/tutorial.md` in
  tutorial order. Do not paraphrase or reorder them.
- **Deterministic waits**: Replace narrative "wait until Active" with
  `juju wait-for application <app> --query='status=="active"' --timeout=30m`
  for each deployed application.
- **HTTP smoke check**: Use Spread's `MATCH` helper:
  `curl -sSf http://<hostname> | MATCH "<expected marker>"`.
- **Channels**: Match channels from the project's integration test workflow
  (e.g., `.github/workflows/integration_test.yaml`). Let `concierge` handle
  the install unless the tutorial specifies channels explicitly.
- **RBAC trust**: Make `juju trust ... --scope cluster` unconditional in
  the task (it's a no-op when RBAC is disabled).
