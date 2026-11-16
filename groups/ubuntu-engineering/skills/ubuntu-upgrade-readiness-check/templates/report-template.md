<package> upgrade-path testing for Ubuntu <target series>
=========================================================
Date: <date>
Host: <host series>, LXD <version>, containers from cloud-images.ubuntu.com
Versions under test:
  <series A>  <pkg> <version>
  <series B>  <pkg> <version>
  <series C>  <pkg> <version>

Upgrade paths tested: <e.g. A->B, B->C, A->B->C — the letters/series change
with the release cycle or per request; use whatever paths were asked for>

Containers
----------
  <name>  <series>  <role, if applicable> -> upgrade path taken
  (one line per container; mark which run is the "clean single-run"
  representative if any run was interrupted and repaired)

Configurations tested
---------------------
(Bullet list, one line each, phrased for a reader new to <package>:
what real-world deployment pattern each configuration models, and what each
legacy/deprecated configuration represents.)

Results matrix
==============
Cell values: PASS | FAIL | NOT APPLICABLE (feature absent on that path).
Every FAIL gets a numbered entry in "Failure details" below; a NOT
APPLICABLE may carry a short parenthesized reason in the cell.

| Feature / thing under test          | baseline | A->B | B->C | A->B->C |
|-------------------------------------|----------|------|------|---------|
| <basic service operation>           | PASS     | PASS | PASS | PASS    |
| <auth with default config>          | PASS     | PASS | PASS | PASS    |
| <legacy feature, default config>    | PASS     | FAIL | FAIL | FAIL    |
| <legacy feature, explicit override> | PASS     | FAIL | FAIL | FAIL    |
| <admin/management operation>        | PASS     | PASS | PASS | PASS    |
| <conffile preserved>                | n/a      | PASS | PASS | PASS    |
| <state files still valid>           | PASS     | PASS | PASS | PASS    |
| <feature only series C has>         | NOT APPLICABLE (absent in A/B) | ... | ... | ... |

The baseline column is the pre-upgrade state on the oldest series. If the
current-series control container's results differ from any path's endpoint,
note it below — failures the control group also shows are NOT upgrade
regressions.

Control group note: <e.g. "control container (fresh <series C> install)
shows the same legacy-feature failures, so they stem from the version jump,
not the upgrade process">

Mixed-version interop: <verdict, e.g. "client@B against server@C: PASS for
all tested operations"; omit this line entirely if the package has no
role split>

Failure details
---------------
### 1. <feature> — FAILS on <paths>
  Exact user-facing error:
    "<verbatim error message>"
  Root cause: <from source/upstream notes — cite file or release note>
  Verified workaround: <explicit-config override; include any warning the
    package emits when it is used>
  Verified proper fix: <re-key/reformat/migrate command or procedure>;
    demonstrated restoring stock-default behavior on <container>.
  Release note analysis does *NOT* go here, it goes in the next section.
    One release note entry might cover multiple failures, so we need not
    be redundant here, we have a dedicated section below for this.

(One numbered section per distinct FAIL row in the matrix.)

Notification / release-notes assessment
=======================================
1. <finding 1>:
   * Release notes: quote what they cover; state what they miss
     (e.g. server/daemon-side effects, remediation steps).
   * ubuntu-release-upgrader: notification observed? Quirks hook present?
     NEWS surfaced? (remember APT_LISTCHANGES_FRONTEND=none; which binary
     packages carry NEWS at all). Verdict: documented / notified /
     handled-automatically / gap.
2. <finding 2>: ...


Suggested Release Notes Entry
---------------
If _(and only if)_ you determine the release notes need fixing or updating, propose a new entry for this package.
Follow the existing style of relesae notes and consult previous releases for reference.
If there are no gaps in the relesae notes, skip this section.

Do this seperately for each *target* version, as follows:

### XX.04 (under $existing_subheading)
```md
#### OpenExample

OpenExample has been updated from 1.0 to 1.1. The upstream release notes can be found [here](https://example.com)

Some defaults were changed:
- Phasers were changed from kill to stun. (See [LP: #12345678](https://bugs.launchpad.net/ubuntu/+source/openexample/+bug/12345678))
- Favorite color is now fluorescent neon green.

Upstream no longer supports using libdependency 3. The Ubuntu release upgrader
will detect if your system is using libdependency 3 and block upgrading until
your configuration is manually migrated to libdependency 4 or later.

418 CVEs were also fixed.

```
### XX.10 (under $existing_subheading)
*No change needed.*


Upgrader mechanics observed (expected refusals, Prompt handling, etc.)

Raw artifacts (fixed manifest — mine intermediates into evidence and delete them)
-------------------------------------------------------------------------------
  REPORT.md                        this report
  delta-analysis.md                step-1 analysis
  evidence.txt                     the exact log/web excerpts (with URL +
                                   fetch date) backing every quoted claim
  <setup>, <suite>, <hop> scripts  the harness
  repro-<n>-*.sh, fix-<n>-*.sh     minimal reproducer + remediation pair per
                                   numbered FAIL row (the most useful output)
  results-<container>-<phase>.txt one per suite run — the matrix's source
  container-ips.txt               addresses of the still-running containers
  Full do-release-upgrade logs stay inside each container at
  /var/log/dist-upgrade. Containers left running for inspection:
  <names and final series>.


Summary
--------------
A one-paragraph summary of findings and general judgement on the package.

Meta-Analysis
--------------
Mention any issues in the skill that impeded your investigation. This could be gaps,
misinformation, or general places where the skill could be improved. When proposing changes,
be sure to make them sufficiently general to allow them to be helpful for any package or
user workflow, not just this package or this user.
