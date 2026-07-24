# Target `.github/workflows/spread_docs.yaml` Shape

If this file already exists, do **not** overwrite it. Record the conflict
as a follow-up.

## Required structure

The generated file must:

- Begin with the copyright header (use the current year):
  ```
  # Copyright <year> Canonical Ltd.
  # See LICENSE file for licensing details.
  ```
- Use `name: Test documentation with Spread`.
- Trigger on `workflow_dispatch`, a weekly `schedule` (`cron: '0 8 * * 1'`),
  and `pull_request` filtered to `paths: ['docs/tutorial.md']`.
- Define one job `tutorial-spread-test` that:
  - `uses: canonical/operator-workflows/.github/workflows/docs_spread.yaml@main`
  - `secrets: inherit`
  - passes `with.input-file: docs/tutorial.md`,
    `with.output-dir: tests/spread/tutorial/`,
    `with.spread-job: github-ci:ubuntu-24.04-64:tests/spread/tutorial`.

## Reference example

See the synapse-operator workflow for a working example:
<https://github.com/canonical/synapse-operator/blob/track/1/.github/workflows/spread_docs.yaml>
