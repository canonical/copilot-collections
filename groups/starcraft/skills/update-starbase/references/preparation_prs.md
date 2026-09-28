# Creating Preparation PRs

Use this guide when you encounter fixes, adjustments, or additions during the Starbase merge or validation that are not strictly part of the Starbase sync itself.

Bundling pre-existing or unrelated changes into the Starbase merge PR obscures the merge diff and complicates review. These changes belong in separate **Preparation PRs** based on `origin/main` that are stacked or merged prior to finalizing the merge PR.

---

## 1. This is a mandatory check, not a judgment call

Skipping this check — or only reacting to problems you happen to notice — is
a process violation. A real merge PR was flagged in review for exactly this:
a newly-added `.github/actionlint.yaml` (new default-enabled linter) and a
large mechanical `pyproject.toml` reformat were both bundled into the merge
PR instead of split into prep PRs, and a reviewer had to point out
"this would've been a perfect use case for a prep PR" ([imagecraft
#449](https://github.com/canonical/imagecraft/pull/449)). Passively "keeping
an eye out" is not enough; you must actively audit for these cases.

**Before opening the merge PR**, enumerate every file added or modified by
the merge (`git diff --name-only --diff-filter=d HEAD^1 HEAD`) and explicitly
classify each one: is it a direct Starbase sync/conflict resolution, or does
it match one of the trigger categories below? Do this for every file, not
just the ones involved in a conflict or a failure you already noticed.

## 2. Recognizing a candidate

You won't know upfront which fixes need their own PR — this only becomes
clear while resolving conflicts and running validation. Audit for it
throughout the merge, not just at the end.

For any fix, adjustment, or addition you're about to fold into the merge PR,
ask: **would this still be needed on `main` even without the Starbase merge**,
or does it exist only to patch a side effect of another fixup you just made?
If either is true, it likely belongs in its own PR rather than as a
merge-PR follow-up commit — check it against the trigger categories below to
confirm.

## 3. Triggers for a Preparation PR

A change matching any of these categories **requires** a preparation PR — do
not fold it into the merge PR just because no reviewer has flagged it yet:

- **Unrelated or pre-existing fixes**: A latent bug or issue exposed by new
  tooling that isn't itself a Starbase file or convention.
- **Chain-reaction fixes**: A follow-up fix that only became necessary *because of* an earlier follow-up fix, rather than because of the Starbase merge itself.
- **Unrelated dependency or version bumps**: A bump driven by an external factor (e.g. security scanner finding against a pinned test fixture) rather than the Starbase sync.
- **Purely mechanical reformatting**: Diff produced by a newly introduced formatter or linter (e.g. `tombi`, `shfmt`) with no logic changes. Keep the formatting diff separate so it can be reviewed and reverted independently.
  Check this proactively: if a file's diff in the merge is dominated by
  whitespace/quoting/ordering changes rather than content changes (e.g. a
  large `pyproject.toml` reformat), that is a mechanical-reformatting prep PR
  candidate even if nothing failed because of it.
- **Any new or newly-enabled linter/formatter that changes files**: applies
  regardless of source (a Starbase config file, a `common.mk` target
  change, etc.) and regardless of whether it's already wired into `make
  lint`/`make format` — a tool can be added before it's wired in. Run any
  newly added/enabled tool directly against the repo.
  - If it reformats files or surfaces findings, that's a prep-PR trigger:
    open a prep PR that wires it in (`common.mk`/pre-commit/CI as needed)
    and addresses its findings/reformatting, decoupled from the merge.
  - If it produces no changes and no findings, no prep PR is needed.
  - *Note:* Optional/opt-in Starbase tooling not adopted by this repository does *not* need a prep PR.
- **Large net-new template-derived files**: Net-new files generated from a template (e.g. `AGENTS.md` derived from `AGENTS.lib.md`/`AGENTS.app.md`). Their size and repository-specific content warrant an independent review unit.

---

## 4. Preparation PR Lifecycle & Rules

1. **Use a separate git worktree, and consider delegating to a subagent**:
   - Create the preparation PR in its own `git worktree` (e.g. `git worktree
     add ../prep-<descriptive-name> -b fix/<descriptive-name>
     origin/main`) rather than switching the current checkout away from the
     in-progress merge branch. This lets the merge and the prep PR proceed
     side by side without one blocking the other or requiring repeated
     branch switches.
   - The agent is encouraged to hand off each preparation PR to a background
     subagent (with its own worktree) to implement, validate, and open as a
     draft, then continue the main merge work in parallel. This keeps prep
     PRs from becoming a detour that stalls the merge, especially when
     multiple independent prep PRs are needed at once.

2. **Branch from `origin/main`**:
   - Create a fresh branch from `origin/main` (not the merge branch):
     ```bash
     git checkout -b fix/<descriptive-name> origin/main
     ```
   - Apply only the isolated fix and open a **draft PR** against `main`. Describe the fix on its own merits, not as a Starbase merge follow-up.

3. **Handle dependent fixes via stacked PRs**:
   - If a second preparation fix depends on the first, do not combine them or open parallel PRs from `main`.
   - Branch the second fix from the first preparation PR's branch and open a draft PR targeting that branch ([GitHub Stacked PRs](https://docs.github.com/en/pull-requests/how-tos/stacked-pull-requests)).

4. **Keep preparation PRs in DRAFT**:
   - **The agent must NEVER mark a preparation PR ready for review or merge it.** Only the human operator promotes PRs out of draft.
   - Once CI is green and reviews are addressed, report the PR to the operator and wait for them to promote and merge it.

5. **Report open preparation PRs to the operator**:
   - Whenever you open, update, or check in on a preparation PR, report on
     **every currently open preparation PR** directly to the user/operator —
     not just the one you were just working on. List each by title with a
     direct link, plus its current status (e.g., draft, CI running, ready
     for operator promotion), so they always have an up-to-date view without
     digging through the merge PR's description.

6. **Rebase the merge branch**:
   - Do not block ongoing Starbase merge work while waiting for prep PRs to merge.
   - Note pending preparation PRs in the merge PR description so reviewers
     know why a fix they might expect to see isn't there.
   - Once a preparation PR merges into `main`, rebase the merge branch onto the updated `origin/main` so the fix drops out of the merge PR diff.
   - Do not mark the Starbase merge PR ready for review until all dependent preparation PRs are merged.

---

## 5. Description & Provenance Requirements

Preparation PR descriptions must include explicit provenance links:

- **Link the source template**:
  If the PR content was adapted by the agent from a Starbase template (e.g. `AGENTS.md` from `AGENTS.lib.md`/`AGENTS.app.md`), the description must name the exact source file and link directly to it at the specific commit/ref of `starbase/main` from which it was derived.
- **Link the originating Starbase PR**:
  If the PR introduces a major reorganization (e.g. moving `docs/.sphinx/` to `docs/_dev/`), a significant new file, or a default-enabled linter/formatter, the description must link the specific upstream `starbase` PR that introduced the change.
- **Bot attribution**:
  Follow standard robot-prefix comment templates (`🤖 [BEEP BOOP...]`) and commit message formats where applicable.
