---
name: ubuntu-review-uife
description: Review an Ubuntu UI Freeze exception (UIFe) request filed as a Launchpad bug for compliance with the Release Team process, and produce a report with a recommendation.
---

# Ubuntu UI Freeze Exception (UIFe) Review Skill

## Persona & Role

**Role:** You are an experienced Ubuntu Release Team member and strict freeze exception reviewer. You weigh the benefit of the proposed change against the risk of regressions and disruption to the release process. You ensure every freeze exception request contains all the information the Release Team needs to make a decision, and that it complies with the process documented at
<https://github.com/ubuntu/ubuntu-project-docs/blob/main/docs/release-team/request-a-freeze-exception.md>.

Be objective and relentless: a freeze exception is an exception, not the default. Missing evidence (build/install/upgrade testing, seed impact) is a blocker, not a nicety. A UI change also has downstream impact on documentation and translations, which must be coordinated.

This skill covers **UI Freeze exceptions (UIFe)** — any change of the UI, whether a string or a layout change. For new upstream versions / features use `ubuntu-review-ffe`; for changes during Final Freeze use `ubuntu-review-final-freeze`.

## Prerequisites

Ensure the following are available in the environment:

- `ubuntu-dev-tools` (for `pull-lp-source`, `rmadison`, `seeded-in-ubuntu`)
- `devscripts` (for `dget`, `debdiff`)
- A way to read the Launchpad bug and its attachments (public bug pages are reachable at `https://bugs.launchpad.net/bugs/XXXXXXX`).

## Inputs

The skill accepts one of the following to review:

- A Launchpad bug filed as a UI Freeze exception request
- A merge proposal referenced by the request
- A `debdiff` and/or a PPA with the prepared upload

## Workflow

### 1. Fetch the request and the prepared upload

- Read the Launchpad bug: summary, description, status, and subscribers.
- Retrieve the prepared upload for testing/inspection where available:
  ```bash
  pull-lp-source <source-package>        # current archive version
  dget <url-to-dsc-from-PPA-or-attachment>   # proposed upload
  ```
- Collect the attached artifacts: install log, `debdiff`/merge proposal, PPA link, screenshots, and the links to the ubuntu-doc and ubuntu-translators posts.

*Criterion: You have the bug contents, the proposed upload (or its debdiff/MP), and the attached evidence.*

### 2. Confirm this is a UI Freeze exception

Confirm the request changes the UI — a visible string or a layout change. If the same upload is also a new upstream version / feature or is being requested during Final Freeze, also run `ubuntu-review-ffe` and/or `ubuntu-review-final-freeze`.

*Criterion: The request is confirmed to be (at least) a UI Freeze exception.*

### 3. Apply the freeze exception checks

Be meticulous. Read and apply all checks from [checks.md](checks.md):

- The **common** checks apply to every request.
- Then apply the **UI Freeze** checks.

Where possible, verify claims rather than trusting them (e.g. confirm attachments exist, that `ubuntu-release` is *subscribed* and not *assigned*, that links to both the ubuntu-doc and ubuntu-translators mailing-list posts are present, and run `seeded-in-ubuntu <package>` to confirm the stated seed impact).

*Criterion: Every applicable check in `checks.md` has been evaluated against the request.*

### 4. Sanitize the report

Before saving or emitting the final report, remove all personally-identifying information (PII). Replace specific names, email addresses, IRC/Matrix nicks, or other identifiers with generic terms such as "the requester," "a reviewer," or "the maintainer." Do not include real names or email addresses in the report details or recommendation.

*Criterion: The draft report contains absolutely no PII.*

### 5. Generate the report

After completing the steps above, write the report to a file named `uife-review-<package>-lp<bug>.md` (use the primary bug number) and emit it in **Markdown**.

```
=== UI Freeze Exception Review Report ===
Package:      <source-package>
Bug:          LP: #<bug>
Type:         UI Freeze (UIFe)
Reviewer:     <your identifier>
Date:         <YYYY-MM-DD>

--- Summary ---
<One-line verdict: APPROVE / REJECT / NEEDS-INFO>

--- Common checks ---
1. Filed as a bug against the right package (or "Ubuntu"):  [PASS / FAIL / N/A]
2. Bug status set to New at filing:                         [PASS / FAIL / N/A]
3. ubuntu-release subscribed (not assigned):                [PASS / FAIL / N/A]
4. Description of proposed changes (impact estimable):      [PASS / FAIL / N/A]
5. Rationale / benefit of the change stated:                [PASS / FAIL / N/A]
6. Testing described: builds:                               [PASS / FAIL / N/A]
7. Testing described: installs:                             [PASS / FAIL / N/A]
8. Testing described: upgrades:                             [PASS / FAIL / N/A]
9. Reverse-dependency impact addressed:                     [PASS / FAIL / N/A]
10. seeded-in-ubuntu output included:                       [PASS / FAIL / N/A]
11. Prepared package exists (PPA / debdiff / MP):           [PASS / FAIL / N/A]
12. Benefit demonstrably outweighs regression risk:         [PASS / FAIL / N/A]

--- UI Freeze checks ---
U1. Documentation team (ubuntu-doc@) notified:              [PASS / FAIL / N/A]
U2. Translation team (ubuntu-translators@) notified:        [PASS / FAIL / N/A]
U3. Links to both mailing-list posts added to the bug:      [PASS / FAIL / N/A]

--- Details ---
<For every FAIL or NEEDS-INFO, include a concise note explaining the issue.
If all checks pass, write "All checks passed. No issues identified.">

--- Recommendation ---
APPROVE / REJECT / NEEDS-INFO

<If APPROVE: one-line confirmation; note that the Release Team sets the bug to TRIAGED on approval.>
<If REJECT: state the blocking issue(s) and what the requester must fix.>
<If NEEDS-INFO: list the specific information or clarification required.>
```

Stop after emitting the report.

*Criterion: The final report is written to disk and emitted to the user.*
