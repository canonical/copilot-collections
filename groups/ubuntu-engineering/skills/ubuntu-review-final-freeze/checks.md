# Final Freeze Exception Review Checks

Source of truth:
<https://github.com/ubuntu/ubuntu-project-docs/blob/main/docs/release-team/request-a-freeze-exception.md>

Evaluate the **Common checks** for every request, then the **Final Freeze**
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

## Final Freeze exception — additional checks

Applies to changes requested during Final Freeze.

X1. **Earmarked bug** — The change fixes a bug earmarked by the Release Team for
   that particular milestone.
X2. **debdiff or merge proposal provided** — A complete `debdiff` or a merge
   proposal of the proposed upload is provided, preferably as a bug attachment.
X3. **ubuntu-release subscribed, not assigned** — (Reconfirm for Final freeze.)
