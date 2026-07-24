# Command Classification Reference

Walk every fenced code block in `docs/tutorial.md` in reading order. For each
command inside a block, decide one of three outcomes. Use these criteria — do
**not** rely on a hard-coded list of commands.

## 1. Keep visible and run (default)

The command is deterministic, non-interactive, and a fresh CI runner can
execute it without human input. Examples of the *shape* to look for:

- Model/namespace creation.
- Non-interactive `juju deploy`, `juju integrate`, `juju config`,
  `juju refresh`.
- Package or add-on installation that has an idempotent, non-prompting form.
- Non-interactive file edits (append-to-`/etc/hosts` via `tee`, `sed -i`,
  redirection).
- HTTP smoke checks such as `curl -sSf ...`.

Leave these blocks untouched.

## 2. `SPREAD SKIP` with no hidden replacement

The command or block is user-facing illustration that cannot or should not
execute in CI, and no automated substitute is required. Examples of the
*shape*:

- Sample output blocks (`juju status`, `kubectl get ...`, log excerpts,
  screenshots, terminal-style code fences that only show output).
- "Open the browser and visit …" steps.
- Manual DNS-provider edits.
- Guidance to run something "inside a Multipass VM" — the reusable workflow
  already provides its own runner.
- Cleanup commands that would destroy the runner itself
  (`multipass delete`, `snap remove` of tooling the runner still needs).
- Interactive prompts (`sudo` with password entry, `read`, TUI editors).

Wrap the block with:

```markdown
<!-- SPREAD SKIP -->

...user-facing content that Spread must not run...

<!-- SPREAD SKIP END -->
```

## 3. `SPREAD SKIP` with a hidden `<!-- SPREAD ... -->` replacement

The visible command is illustrative for the reader but a deterministic
equivalent is needed so Spread can run the tutorial unattended. Common
patterns to look for:

- Narrative "wait until the application is Active" or "run `juju status` until
  you see …" — replace with an explicit
  `juju wait-for application <app> --query='status=="active"' --timeout=30m`
  hidden block, one per application the tutorial has deployed at that point.
- A conditional-on-environment step (for example, "if RBAC is enabled, run
  `juju trust …`") — replace with an unconditional deterministic equivalent
  hidden block.
- A visible interactive teardown (`juju destroy-model …` without `--no-prompt`,
  `multipass delete` of a VM the tutorial created) — hide a non-interactive
  equivalent (for example, add `--no-prompt --destroy-storage=true` or the
  workload's equivalent). Keep the visible form inside SPREAD SKIP so
  readers still see it.
- A visible `juju bootstrap` guarded by "if not already bootstrapped" — if
  the Spread `prepare` phase in `spread.yaml` already bootstraps a
  controller, SPREAD SKIP the visible block and add no replacement.

Insert the hidden block **immediately after** the visible SPREAD SKIP block
it augments, so source order pairs them:

```markdown
<!-- SPREAD SKIP -->

    juju destroy-model my-tutorial

<!-- SPREAD SKIP END -->

<!-- SPREAD
juju destroy-model my-tutorial --no-prompt --destroy-storage=true
-->
```
