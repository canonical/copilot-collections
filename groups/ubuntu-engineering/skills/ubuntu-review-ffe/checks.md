# Feature Freeze Exception (FFe) Review Checks

Source of truth:
<https://github.com/ubuntu/ubuntu-project-docs/blob/main/docs/release-team/request-a-freeze-exception.md>

Evaluate the **Common checks** for every request, then the **Feature Freeze**
checks. Mark each check `PASS`, `FAIL`, or `N/A`, and justify every
`FAIL`/`NEEDS-INFO` in the report.

---

## Common checks (all requests)

1. **Filed against the right target** — The request is a Launchpad bug against
   the relevant package, or against "Ubuntu" if the package is not available in
   the archive yet.
2. **Status New at filing** — The bug was set to *New* so the Release Team sees
   the request.
3. **ubuntu-release subscribed, not assigned** — The
   [`ubuntu-release`](https://launchpad.net/~ubuntu-release) team is
   *subscribed* to the bug. It must **not** be *assigned*.
4. **Description of proposed changes** — Enough detail to estimate the potential
   impact on the distribution.
5. **Rationale / benefit** — A clear rationale explaining the benefit of the
   change.
6. **Testing: builds** — Evidence the new package builds.
7. **Testing: installs** — Evidence the new package installs (e.g. install log).
8. **Testing: upgrades** — Evidence the new package upgrades cleanly.
9. **Reverse-dependency impact** — Confirmation that dependent packages are not
   broken, or that corresponding updates have been prepared. Consider verifying
   with a reverse-dependency check.
10. **seeded-in-ubuntu output** — The output of `seeded-in-ubuntu <package>` is
    included so the seed/impact footprint can be assessed.
11. **Prepared package exists** — An updated package is already prepared and
    tested (PPA link, `debdiff`, or merge proposal), so proper build logs are
    available.
12. **Benefit outweighs risk** — Overall, the request *demonstrates* that the
    benefit of the change outweighs the risk of regressions and disruption to
    the release process.

If the upload is a **new upstream micro-release**, the relevant part of the
upstream changelog and/or release notes must also be included (see FFe checks).

---

## Feature Freeze exception (FFe) — additional checks

Applies to new upstream versions, new features, and/or ABI/API changes.

F1. **`FFe:` in the bug summary** — The bug title (large summary) is prefixed
   with `FFe:`.
F2. **`## FFe ##` stanza** — The description contains an FFe stanza starting
   with `## FFe ##`.
F3. **Reason stated** — The requester states why the exception is necessary
   (e.g. other bugs it fixes).
F4. **Upstream changelog diff attached** — A diff of the **upstream** changelog
   (not `debian/changelog`) is attached as a file, e.g.
   `diff -u <package>-{old,new}/ChangeLog > changelog.diff`. The file may be
   called `ChangeLog`, `CHANGES`, or be replaced by a `NEWS` file.
F5. **NEWS file** — The `NEWS` file is attached where it aids review (commonly
   true for GNOME packages).
F6. **PPA link** — A link to the PPA with the uploaded changes is provided so
   the Release Team can review the build artifacts/logs.
F7. **Install log** — An install log (e.g. console messages from installing) is
   included.
F8. **Functional testing described** — The requester states what testing was
   done to confirm the change works.
F9. **Regression potential** — Regression potential is described, using the
   [SRU bug template](https://documentation.ubuntu.com/sru/en/latest/reference/bug-template/)
   for guidance.
F10. **(Optional) Screenshot** — A screenshot of the main features is a nice
    extra, not a blocker.
F11. **ubuntu-release subscribed, not assigned** — (Reconfirm for FFe.)
