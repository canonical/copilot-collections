# PR Provenance and Review Comments

Use this reference whenever you need to document the provenance of a change
on the merge PR — both for the initial merge and for every follow-up fix made
while the PR is open.

## Documenting change provenance on each file

For every file added, deleted, or modified by the merge, make review comments
on the GitHub PR explaining the provenance of the changes. Additionally, post
inline review comments pointing out specific custom changes (e.g., removing a
duplicate directive or fixing a type ignore).

Files that already existed in the child repository and merged cleanly
without conflicts or custom changes do not need a comment.

**Provenance and rationale for manual changes belong exclusively in PR review
comments, never as comments inside the source file.** If you catch yourself
writing "why a bot changed this" as a `#`/`//` comment in code, stop and move
it to a PR review comment instead. This applies just as much to config files
like `docs/conf.py`: e.g. explaining *why* only specific `sphinx_toolbox`
submodules are loaded (instead of the top-level package) belongs in a PR
file-level comment, not a multi-line `#` block above the `extensions` entries.

The comments must follow these guidelines:

- **Prefix Template**: Each comment must begin with a robot emoji and a
  prefix in square brackets announcing that a bot wrote it, along with the
  model and harness. E.g. `🤖 [BEEP BOOP, A BOT WROTE THIS COMMENT - <model>, <harness>]`.
  Example: `🤖 [BEEP BOOP, A BOT WROTE THIS COMMENT - Gemini 3.5 Flash (High), antigravity]`
- **Provenance Descriptions**:
  - For new files: `"new file from starbase"`
  - For modified files: `"file updated from starbase"`
  - For renamed or moved files: `"file moved in starbase"`
  - For complex/mixed files (e.g. `uv.lock` or `pyproject.toml`): Provide
    specific intermediate/complex details (e.g. `"file updated from starbase
    (child-owned file, regenerated locally based on merged dependencies)"`).
- **Implementation via GitHub API**:
  - Post file-level comments on the PR using the REST API (`POST
    /repos/{owner}/{repo}/pulls/{pull_number}/comments`) with the
    `"subject_type": "file"` parameter so that a specific line number is not
    required.
  - Post inline line-level review comments for specific code changes
    (specifying `"line"` and `"side": "RIGHT"`) to highlight specific
    modifications made (such as resolving duplicate extensions or custom
    linter ignores).
  - **Handling Rate Limits**: When posting a batch of comments, enforce a
    delay (e.g., 4-5 seconds) between calls to avoid GitHub's spam rate
    limiter (`was submitted too quickly`). Implement an automatic
    backoff/retry (e.g., sleeping 30 seconds upon hitting a rate limit) to
    guarantee all comments are registered.
- **Own-invention workarounds require a suggestion, not a direct push**: for
  a change that is neither sourced from `starbase/main` nor an obvious
  conflict resolution — for example, a hand-written workaround like adding
  an `export SPHINX_OPTS := ... -j 1` override to fix a `--fail-on-warning`
  failure caused by a Sphinx extension's parallel-read warning — do not push
  the change directly into the merge commit. Instead, push the merge without
  it, then leave an inline review comment at the relevant location using the
  standard robot-prefix template that explains the problem and proposes the
  fix as an actual GitHub suggestion (a fenced ` ```suggestion ` block), so a
  human reviewer can review and apply it explicitly rather than the bot
  self-approving its own invented fix.
- **Skip comments on routine mechanical regenerations**: a purely mechanical,
  expected side effect of the merge (for example, `uv.lock` being
  regenerated after merging dependency changes) does not need its own
  provenance comment unless something about that specific regeneration is
  non-obvious (e.g. an unexpected transitive version change worth flagging).
  Reviewers have called out such comments as unnecessary noise; when in
  doubt, prefer silence over a comment that just restates the expected
  mechanical outcome.
- **Cite precedent with a link, not just a claim**: when a provenance or
  custom-change comment says a resolution "matches" or was "already used in"
  another repository's Starbase merge (for example, the same `Makefile`
  lint-target conflict resolved the same way in `craft-application`), the
  comment must link the actual PR where that precedent was set, and briefly
  note any discussion that happened there — not just assert the precedent by
  name.

## Ongoing provenance after the initial merge

The rules above apply for the entire life of the PR, not just the initial
merge. Any manual code change made while fixing CI failures or responding to
review feedback — including one-line bugfixes — must be explained via a PR
review comment (inline on the changed line, using the same robot-prefix
template), never as a comment added to the source file itself. Do not add
explanatory `#`/`//` comments to files to document *why a bot made this
change*; source comments are only for genuinely non-obvious code, not for
change provenance.

Post each of these follow-up-fix review comments (and remember the
robot-prefix template) in the same turn you push the corresponding fix —
don't defer it, and don't wait to be reminded.
