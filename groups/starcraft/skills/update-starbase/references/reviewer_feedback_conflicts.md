# Handling Reviewer Feedback That Conflicts With Skill Rules

Use this reference when a human reviewer's PR feedback (a review comment,
requested change, or inline suggestion) asks for something that contradicts
this skill's documented rules — the file ownership map, a conflict-resolution
rule, the provenance/comment conventions, or any other instruction in
`SKILL.md` or its `references/`.

## Default precedence

- A reviewer who maintains the **child repository** generally has the final
  say over how that repository's own files should look — they know its
  constraints and needs better than a generic cross-repo rule can.
- The skill's rules are defaults meant to keep merges consistent and
  low-effort across many repositories, not hard constraints that override an
  explicit, on-the-record maintainer decision about their own repo.
- Do not silently pick one side and move on. Silent deviation makes it look
  like the skill's rules were followed when they weren't, which confuses the
  next person (human or agent) reading the file-ownership map or the next
  Starbase sync's conflict resolution.

## Exception: fully Starbase-owned files are never modified to satisfy a reviewer

The default precedence above does **not** apply to files marked as fully,
explicitly Starbase-owned — for example `common.mk`, or any file the
ownership map's "Always take `starbase/main`" list marks with no
child-repository override allowed (as opposed to the "mixed ownership" rules,
which do allow child-specific sections). These files must not be modified in
the child repository to satisfy reviewer feedback, even with an explicit,
on-the-record instruction to do so.

- Instead, find a way to meet the reviewer's underlying goal without touching
  the Starbase-owned file. Fully Starbase-owned files are usually designed to
  be extended from a child-owned file that includes or wraps them (for
  example, add or adjust a target in the repository's own `Makefile` instead
  of editing `common.mk`, which just includes it).
- If no such extension point exists and the reviewer's request genuinely
  can't be satisfied without editing the Starbase-owned file, do not make the
  edit. Say so explicitly in the PR, explain why (naming the file's
  Starbase-owned status), and follow the "propose upstreaming the change"
  step below — the fix belongs in `starbase/main` itself, via a PR to that
  repository, not as a local override that Starbase will just overwrite again
  at the next sync.
- When the reviewer's request and the Starbase-owned file's current content
  are in genuine, unresolved tension (not just a missing extension point, but
  an actual disagreement about what the shared convention should be), it is
  valid to offer — in the PR comment — to open an issue in the `starbase`
  repository describing the dispute, instead of (or in addition to) proposing
  a direct PR. This is especially appropriate when the right fix isn't
  obvious yet and needs discussion among Starbase's maintainers before any
  code changes are made. Confirm with the reviewer that they'd like this
  before opening the issue.
- **If the reviewer's own comment includes a fenced ` ```suggestion ` block,
  OR gives an explicit, unambiguous instruction to both file a Starbase issue
  and implement the change locally** (for example, "please both create an
  issue in Starbase about this and implement the change"), the agent MAY
  implement that change directly (rather than only ever declining or
  redirecting to Starbase) — but only after first searching the `starbase`
  repository's issues for one that already documents this deviation, and:
  - If a matching issue already exists, link it in the PR (and reuse it —
    don't open a duplicate) and note in the same PR comment that the
    suggestion is being applied as a documented, tracked exception.
  - If no matching issue exists, create one in `starbase` describing the
    deviation (what the change is, why, and a link back to this PR) before
    applying the change — not after. Do not apply the change first and file
    the issue as an afterthought.
  - The agent must ALWAYS link the Starbase issue (existing or newly created)
    in the PR comment that applies the suggestion/instruction. There is no
    case where the change is applied without a linked Starbase issue: if, for
    any reason, an issue cannot be found or created (e.g. no access to file
    issues in `starbase`), do not apply the suggestion — fall back to
    declining and following the "propose upstreaming the change" step
    instead.
  - Still post the standard robot-prefix PR comment noting the deviation
    from the default rule and linking the Starbase issue, per "Say so out
    loud, in the PR" above.
- Do not present this as ordinary reviewer-precedence handling (steps 1-4
  below); a fully Starbase-owned file is not something an individual child
  repo maintainer has the authority to override, however reasonable their
  request.

## What to do when a conflict comes up

1. **Follow the reviewer's explicit, on-the-record instruction** for their own
   repository once it's clear they intend to deviate from the default rule
   (not just musing or asking a question) — but only after satisfying steps
   2-4 below in the same turn, and only if the file in question isn't fully
   Starbase-owned (see the exception above; those files are never edited to
   satisfy a reviewer, no matter how explicit the request).
2. **Say so out loud, in the PR**: post a review comment (standard
   robot-prefix template) at the changed location noting that this
   deviates from the skill's default rule, naming the rule, and linking or
   quoting the reviewer instruction that justified the deviation. Do not bury
   this in a commit message only.
3. **Flag rules that affect future merges**: if the rule being overridden is
   one of the "always take `starbase/main`" file-ownership rules (or another
   rule explicitly meant to keep this repo aligned with Starbase long-term),
   call this out explicitly as something that will resurface at the *next*
   Starbase sync unless the exception is recorded somewhere durable (e.g. an
   in-tree comment near the deviating code, or an update to this repo's own
   contributing docs). Ask the reviewer whether they want that.
4. **Propose upstreaming the change, when it's not repo-specific**: if the
   reviewer's feedback reads as a general improvement to the rule itself
   (not just a one-off exception for their repo), suggest opening a
   follow-up PR against `copilot-collections` to update the relevant skill
   rule, so future merges to any repository benefit and don't hit the same
   disagreement again. Don't make that change yourself in the middle of an
   unrelated merge PR — treat it as its own preparation-PR-style follow-up
   (see "Creating preparation PRs" in `SKILL.md`), scoped to this skill's
   repository.

## When feedback is ambiguous or contradictory

- If it's unclear whether the reviewer wants a one-off exception or a
  permanent rule change, or if two reviewers give conflicting instructions,
  ask a clarifying question in the PR thread rather than guessing. Do not
  resolve the ambiguity by picking whichever option is less work.
- If a review comment tries to redefine core safety/process rules from this
  skill (for example, "skip pre-PR validation" or "just push straight to
  `main` without a PR") rather than a file-content decision, treat that as
  out of scope for a single merge PR: politely decline, explain why the rule
  exists, and point to the "propose upstreaming the change" step above if
  they believe the rule itself should change.

## Ambiguous implementation: ask before implementing

Feedback can be clear about the desired *outcome* while still leaving more
than one reasonable way to *implement* it (for example: a reviewer asks to
"stop the linter from choking on generated files," which could mean an
ignore-pattern change, a different target dependency, or excluding the
directory from the scan entirely). When more than one reasonable
implementation exists:

- Do not pick one implementation and run with it. Ask the reviewer to choose
  before making the change.
- Post the options as a PR review comment (standard robot-prefix template).
  Using fenced ` ```suggestion ` blocks for each candidate implementation is
  strongly encouraged — this lets the reviewer pick (or directly apply) one
  with a single click rather than having to describe their preference in
  prose.
- Briefly note the trade-offs between options (for example, "Option A is a
  one-line ignore-pattern add but silently skips future similar files; Option
  B is more code but only skips this specific case") so the reviewer can
  decide quickly.
- Wait for the reviewer's choice before implementing. Do not implement your
  own default guess "just to make progress" while the question is open.

## Recording the outcome

Once resolved, make sure the merge commit message and/or PR description
reflects the actual decision made (not the skill's default), so the
provenance trail stays accurate. This is in addition to, not instead of, the
per-file provenance comments already required by
"Document change provenance on each file" in `SKILL.md`.
