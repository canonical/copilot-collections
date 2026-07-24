# Target `.github/workflows/spread_test.yaml` Shape

## Required structure

```yaml
# Copyright <year> Canonical Ltd.
# See LICENSE file for licensing details.
name: Spread tutorial test

on:
  workflow_dispatch:
  schedule:
    - cron: "0 6 * * 1"
  pull_request:
    paths:
      - spread.yaml
      - tests/spread/**
      - .github/workflows/spread_test.yaml

permissions:
  contents: read

jobs:
  spread:
    runs-on: [self-hosted, linux, edge]
    timeout-minutes: 120
    steps:
      - uses: actions/checkout@v6
      - name: Install Spread
        run: |
          sudo snap install spread || {
            sudo snap install --classic go
            /snap/bin/go install github.com/canonical/spread/cmd/spread@latest
            echo "$HOME/go/bin" >> "$GITHUB_PATH"
          }
      - name: Run Spread
        run: spread -v github-ci:
      - name: Upload Spread logs
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: spread-logs
          path: |
            .spread-reuse.yaml
            /tmp/spread-*
          if-no-files-found: ignore
```

## Key rules

- **Runner label**: Must use `runs-on: [self-hosted, linux, edge]` to match
  existing workflows in the repository.
- **Triggers**: `workflow_dispatch`, weekly `schedule`, and `pull_request`
  filtered to Spread-related paths.
