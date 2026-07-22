# UI Freeze Exception (UIFe) Review Checks

Source of truth:
<https://github.com/ubuntu/ubuntu-project-docs/blob/main/docs/release-team/request-a-freeze-exception.md>

Evaluate the **Common checks** for every request, then the **UI Freeze**
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

---

## UI Freeze exception — additional checks

Applies to any change of the UI, whether a string or a layout change.

U1. **Documentation team notified** — The
   [`ubuntu-doc@`](https://lists.ubuntu.com/mailman/listinfo/ubuntu-doc) team
   has been notified of the UI change.
U2. **Translation team notified** — The
   [`ubuntu-translators@`](https://lists.ubuntu.com/mailman/listinfo/ubuntu-translators)
   team has been notified.
U3. **Mailing-list links in the bug** — Links to the posts in the
   [ubuntu-doc](https://lists.ubuntu.com/archives/ubuntu-doc/) and
   [ubuntu-translators](https://lists.ubuntu.com/archives/ubuntu-translators/)
   archives are added to the bug.
U4. **ubuntu-release subscribed, not assigned** — (Reconfirm for UI freeze.)
