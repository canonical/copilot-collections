---
name: ubuntu-upgrade-readiness-check
description: Assess an Ubuntu package's release-upgrade readiness in LXD.
version: 0.3.1
license: MIT
platforms: [linux]
tags: [ubuntu, packaging, release-upgrade, lxd, qa]
---

# Upgrade Readiness Check

Assess whether a package survives Ubuntu release-upgrade paths (e.g.
old-LTS -> current-LTS, current-LTS -> devel, old-LTS -> current-LTS -> devel)
with realistic configurations, and whether users are adequately warned about
any manual work required afterwards. Produces a results matrix (rows =
features under test, columns = upgrade paths, cells PASS / FAIL / NOT
APPLICABLE), root-caused failures, verified fixes, and a release-notes /
ubuntu-release-upgrader notification verdict.

Runs in LXD containers on any Linux host with LXD installed; upgrades go
through the real `do-release-upgrade`, never hand-edited apt sources.

## When to Use

- A release is approaching and you need to know what breaks for real users
  of a package across upgrade paths.
- You suspect an Ubuntu delta patch or upstream version jump changes runtime
  behavior (defaults, config parsing, on-disk formats, daemon behavior).
- Asked "do the release notes / release-upgrader cover the needed manual
  work?"
- Don't use for: fresh-install testing of the target series (no upgrade
  involved), autopkgtest/FTBFS triage, or CI regression testing.

## Prerequisites

- Linux host with LXD (`lxc --version`), disk for the containers (typically
  2-5; see Topology).
- Image remotes for server containers:
  `lxc remote add ubuntu-releases https://cloud-images.ubuntu.com/releases --protocol=simplestreams --public`
  (`ubuntu-daily` typically exists already and carries the devel series).
  The default `images:` remote may only carry desktop VM images.
- A working directory for artifacts, e.g. `<pkg>-upgrade-tests/`.
- `rmadison` (devscripts) or the archive web UI for version lookups.
- The package's Debian/Ubuntu source checkout for delta analysis, and web
  access for upstream release notes. Verify early that your fetch tool can
  actually retrieve pages — some fetch backends are search-only; curl plus
  tag-stripping is the fallback (vendor doc pages can be multi-MB JS
  bundles where curl + grep still works).
- `update-manager-core` installed inside every test container.

## Procedure

Each step has a checkable completion criterion.

Budget: with local LXD, expect up to a few hours end-to-end. The dominant
cost is authoring and debugging the harness, not the hops: a hop typically
completes unattended in well under an hour and parallelizes across
containers, while harness authoring plus control-container debugging easily
runs long — and a suite bug found after the full fan-out costs a re-run in
every container. Rough figures: delta analysis 20-30 min, container setup
~15 min, suite runs ~5 min each. Try to make this as fast as reasonable,
though the upgrades themselves will necessarily take time.

1. Delta analysis — do this BEFORE building containers; it decides what
   you test.
   - If `references/quirks/<pkg>.md` exists (quirks accumulated from
     earlier assessments of this package), read it FIRST — it feeds both
     the delta analysis and the test suite.
   - Look up the package's version in every involved series (rmadison),
     including binary packages: do any disappear between series?
   - Read debian/control for every involved series: binary Conflicts /
     Provides / Depends changes decide whether roles can coexist in one
     container, whether a fresh target-series install can even host each
     role (a flavor the metapackage no longer selects may conflict with
     the new default), and whether the topology needs more containers
     than upgrade paths. Discovered here, not mid-setup.
   - Read the Debian changelog, Ubuntu changelog entries, and NEWS between
     the from-version and to-version. List every Ubuntu delta patch.
   - Fetch upstream release notes for each upstream version step.
   - Configuration-language drift: when the from- and to-series speak
     different configuration languages (a major-version rewrite: renamed
     or removed settings, new section grammar), treat the TO-series'
     shipped example conffiles — read from the target series' packaging
     branch or out of an installed target-series container — as the
     authoritative target language, and prefer them over upstream prose
     migration docs, which state intent but can lag or misstate the exact
     shipped syntax. Every piece of harness config you apply to a
     container (and every client probe it drives) must then be written in
     the language of THAT container's deployed series.
   - Criterion: a written list of
     * (a) behavior changes that could break existing deployments
     * (b) state that must survive the upgrade (conffiles, databases,
       key material, state dirs)
     * (c) the package roles real users deploy (server/daemon,
       client, PAM/library consumer, unattended/key-based setups).
   - Inspect the upgrader's quirks hooks for special handling of the
     package (e.g. package splits with automatic variant switching). The
     local /usr/lib/python3/dist-packages/DistUpgrade/DistUpgradeQuirks.py
     covers only the CURRENT series' upgrader; fetch the quirks file for EACH
     hop's target series (a multi-hop chain fires the gate that ships with
     each hop's target):
     https://git.launchpad.net/ubuntu/+source/ubuntu-release-upgrader/plain/DistUpgrade/DistUpgradeQuirks.py?h=applied/ubuntu/<series>.
     Do not assume that these are the only breaking changes in the
     package.
2. Topology — minimum: one container per upgrade path, plus a control group.
   - Minimum viable setup: one container per upgrade path under test (e.g.
     A->B, B->C, A->B->C need three), plus one current-series container as
     the control group (its failures predate any upgrade and are not upgrade
     regressions). If a path's endpoint equals the control group's series,
     one container can serve both roles.
   - Add role-specific containers only if the package has meaningfully
     distinct deployment roles (daemon vs. client, server vs. PAM consumer,
     unattended/key-based vs. interactive). If the roles share configuration
     and code paths, a single container per path is sufficient — don't
     multiply containers for form's sake. A binary Conflicts between two
     flavors (found in step 1) forces the split into separate containers.
   - When roles ARE split across containers, point client-role containers
    at a server-role container so mixed-version interop is tested (real
    fleets upgrade clients and servers at different times).
   - Stagger the hops to capture BOTH mixed states: upgrade the
    client-role container first and run its suite against the
    still-unupgraded server, then upgrade the server; afterwards launch a
    throwaway from-series container to test old-client -> new-server —
    default changes (a new client requiring TLS, an old server shipping it
    disabled) often break only one direction, and only the stagger exposes
    which.
   - Configure BOTH a modern/default deployment AND the legacy features the
     delta analysis flagged (old key/data formats, deprecated options, state
     created by the old version). Legacy configurations are where upgrades
     actually break users.
   - Criterion: containers launched, addresses recorded, hostname entries
     for all test hosts in each container, cloud-init finished
     (`cloud-init status --wait`) before any package operations.
3. Test suite + baseline.
   - Write a single test suite (see `templates/test-suite-template.sh`),
     parameterized by role ONLY if the package has multiple deployment
     roles; otherwise one unparameterized suite. It emits `PASS:`/`FAIL:`
     lines, with a header recording the phase label and installed package
     versions. Include conffile-preservation and state-file checks, not
     just service health. Each test must be self-contained (acquire its own
     credentials/state; isolated env or temp dir).
   - Debug the harness control-first: stand up the control-group container
     plus its peer/server only, run the suite there, and fix suite/setup
     bugs until it is all-PASS; only then fan setup out to the remaining
     containers. A setup bug found after a full fan-out costs a re-run in
     every container (a six-container strongSwan run took four full
     re-runs before this rule existed).
   - The control validates only the TARGET series: also bring one
     FROM-series container (and for multi-hop paths the mid-path series)
     to an all-PASS baseline before the fan-out — legacy-deployment-only
     gaps (missing privileges, old wire/dialog behavior) surface there and
     not on the control, and mid-path series can differ from both ends
     (e.g. an AppArmor profile tightened between two series).
   - When the series under test change the package's protocol or CLI
     surface (not just its config), parameterize the setup script and the
     suite's client probes by deployed series — one flavor per config
     language, per step 1's target-language rule. Debug protocol probes
     through a line-logging TCP proxy between probe and service that
     prints both directions' raw bytes: reading the exact bytes on the
     wire finds dialog bugs (an encoder swallowing a literal's closing
     brace, a multiline greeting read as one line) in minutes, where
     trial-and-error against live error strings takes hours.
   - Assert probe results on shape, not arithmetic: have probes print a
     final result line and assert on it with `grep -qx 1` (or
     `grep -qxE '[1-9][0-9]*'`) — never `test $(cmd) -eq N` inside
     `bash -c`, where empty or multiline probe output makes command
     substitution expand to zero or several arguments and the test
     explodes with "too many arguments" or "integer expression
     expected", muddying which test actually failed. Beware
     tools that echo their own command line in banners on error paths
     (dig prints "DiG ... <zone> <type> ..." even when the server is
     unreachable): never grep for a token that also appears in the
     banner (e.g. `grep -q SOA` false-PASSes a dead server); match the
     answer RECORD shape instead (`grep -qE 'IN[[:space:]]+SOA'`).
   - Run it in every container and save per-container baseline results.
     Baseline the current-series container too — it reveals which failures
     predate any upgrade (a fresh install of the target series shows the
     same failures that are NOT upgrade regressions).
   - Criterion: a baseline results file per container, all-PASS except
     failures you can already explain.
4. Upgrades.
   - Per container, in order: in-release `apt-get update && apt-get
     full-upgrade`; restart the container if /var/run/reboot-required* is
     set; then:
     `env DEBIAN_FRONTEND=noninteractive do-release-upgrade -f DistUpgradeViewNonInteractive`
     (upgrading an LTS to an unreleased devel series also needs
     `Prompt=normal` in /etc/update-manager/release-upgrades plus `-d`;
     to a RELEASED interim series it needs `Prompt=normal` but NOT
     `-d` — the hop driver template's mode argument distinguishes
     lts / normal / devel).
     Make the update phase of your driver itself check reboot-required and
     restart — an upgrade phase launched separately against an un-rebooted
     system is refused ("You have not rebooted after updating a package
     which requires a reboot") and wastes the run.
   - Run each upgrade detached/monitored (nohup or your agent's background
     job mechanism) so a supervisor timeout can never kill the host-side
     lxc exec mid-upgrade. Independent container upgrades can run in
     parallel; hops on the SAME container run sequentially. Start each hop
     from `templates/hop-driver-template.sh` (usage contract,
     reboot-required handling, detached in-container launch, robust
     completion polling, per-hop log pulls, recovered-hop detection,
     gate-abort detection) instead of improvising a driver under time
     pressure — the template encodes the polling pitfalls listed below.
   - PRE-FLIGHT GATE ABORTS: many packages ship upgrader quirk gates that
     abort do-release-upgrade BEFORE any change (config checks, account
     checks). Treat the abort as the documented UX, not a failed run: pull
     the refusal message, apply the remediation the gate prescribes, then
     re-run the hop driver from the top — the aborted attempt leaves the
     container untouched. The driver exits 3 on such an abort so the
     remediate-and-retry loop never waits the full hop timeout on a
     three-minute refusal.
   - Pull /var/log/dist-upgrade/{main,apt-term}.log into the workdir
     after EVERY hop, before starting the next: each do-release-upgrade
     OVERWRITES them, so a multi-hop container's surviving on-disk log is
     only the last hop's — earlier-hop evidence is unrecoverable later.
     These per-hop copies are run intermediates, not final artifacts:
     step 7's artifact policy has you mine them into evidence.txt and
     delete them at report time — don't try to satisfy the final manifest
     mid-run.
   - Multi-hop paths: record the RAW post-hop state at the intermediate
     series (baseline for the next hop, and the data the report needs),
     then apply the documented remediation for any hop-blocking failure
     BEFORE starting the next hop — a real admin cannot continue an
     upgrade path with the service broken — and say in the report that
     later hops started from the remediated state.
   - Restart the container after every hop BEFORE running the
     post-upgrade suite: /run is tmpfs and one-shot transition shims (a
     postinst symlink bridging an old runtime-dir) only hold until the
     first reboot — a service running right after the upgrade can
     crash-loop from that reboot on, and the post-reboot state is the
     steady state users actually get (mariadb precedent: a conffile
     renamed during the upgrade kept the old runtime-dir pid path, and
     nothing recreated that directory at boot).
   - Criterion: each container's /etc/os-release shows the target series
     and /var/log/dist-upgrade/main.log ends without errors, with a
     per-hop copy of main.log in the workdir for every completed hop.
     RECOVERED HOPS ARE A VALID EXCEPTION: a package maintainer-script
     failure can make do-release-upgrade ABORT mid-hop ("Could not
     install the upgrades ... A recovery will run now (dpkg --configure
     -a)") and then complete the hop via its built-in recovery, landing
     correctly on the target series. Do NOT re-run such a container hoping
     for a cleaner log — the landing is valid, and the abort is usually
     the headline finding of the assessment (a local-config break that
     stops the release upgrade itself): record it and root-cause it.
5. Notification assessment — the "would a user see this coming" verdict.
   - *Do this while the upgrades in step (4) are running in the background to save time.*
   - Search /var/log/dist-upgrade/{main,apt-term}.log for the package
    name, removals, demotions, quirks, and conffile-move lines
    ("Preserving user changes to ... (renamed from ...)", "Removing
    obsolete conffile ...") — path-migrated conffiles are exactly where
    locally-modified conffiles get burned, and those lines are the
    smoking-gun evidence.
   - Check the target series release notes
     (https://documentation.ubuntu.com/release-notes/) for the observed
     breakage AND its remediation. Package entries live on SUBPAGES, not
     the series landing page: for an LTS target check
     <series>/summary-for-lts-users/ and <series>/changes-since-previous-interim/;
     also check the previous interim series' changes page, which covers
     the upstream version jump's behavior changes.
   - Coverage is often role-asymmetric: notes may document a client-side
     default change while the server/daemon-side effect and the
     remediation are missing (krb5 precedent: client kinit change
     documented, KDC-side refusal not). Check coverage for every
     deployment role, not just whether the package is mentioned.
   - A remediation documented in the TO series' notes speaks the TO series'
     config language, but a user hitting the gate is still running the FROM
     series: verify any settings the remediation adds can be applied on the
     FROM series without breaking the running service (a TO-series option
     may be an unknown variable to the still-running FROM-series daemon, so
     a restart with it in place crash-loops the service until the hop lands).
     If they cannot be applied safely, that is a release-notes finding.
   - Note: the upgrader sets APT_LISTCHANGES_FRONTEND=none, so package
     NEWS files never surface during an upgrade; also note which binary
     packages carry NEWS at all (server-only packages leave client-only
     hosts uninformed).
   - Criterion: per finding, one verdict — documented / notified / handled
     automatically / gap — with evidence (release-note quote or log line).
6. Post-upgrade diff; root-cause every new FAIL.
   - Re-run the suite after each hop with a new phase label; diff PASS/FAIL
     against baseline.
   - Classify every FAIL before investigating:
     * (a) new after the upgrade = upgrade regression, root-cause it;
     * (b) also fails on the current-series control container = version-
       jump behavior, not an upgrade regression, but still root-cause it;
     * (c) fails uniformly from BASELINE on every series including the
       control = pre-existing condition of the setup/package — root-cause
       and remediate it ONCE; do not re-investigate per path. If the
       remediation is demonstrated on the control, capture the control's
       STOCK baseline results file BEFORE applying it (or revert cleanly
       afterward) — otherwise the matrix loses its stock control column.
   - A down or crash-looping daemon fails every dependent test: keep a
     service-health canary first in the suite — one root cause renders as
     twenty red cells, which the report should annotate as cascading
     rather than numbering each.
   - For each FAIL in classes (a) and (b): reproduce interactively,
     capture the exact user-facing error, root-cause it in the source or
     upstream notes, then verify BOTH a workaround (explicit config
     re-enabling old behavior; if none exists, show that from the source,
     not by assertion) AND the proper fix (re-key/reformat/migrate) —
     demonstrating that the proper fix restores stock-default behavior.
   - Save each remediation run as its own results file with an explicit
     phase suffix (e.g. `<hop>-fixed`) so the aggregator gives it its own
     column; relabel that column by hand in the report matrix and state
     in the matrix header that post-fix columns show the REMEDIATED state,
     not a stock upgrade.
   - Criterion: no unexplained diff lines; fixes demonstrated, not proposed.
7. Report (see `templates/report-template.md`); keep raw per-phase results
   files next to it. Present results as a matrix: one row per feature/thing
   under test, one column per upgrade path (plus a baseline column), cells
   PASS / FAIL / NOT APPLICABLE; every FAIL row gets a numbered
   root-cause/fix section. Build and check the matrix with
   `templates/results-aggregate.py` (reads results-*.txt, prints the
   cross-tabulation plus per-file FAIL lists) instead of transcribing by
   hand; annotate N/A and relabel columns in the report from its output.
   The aggregator MERGES identical phase labels across files into one
   column — give phases series-distinct names up front (e.g.
   `noble-baseline`, not `baseline`, when several series emit baselines)
   or the per-series baselines collapse into a single column.
   Leave containers running for inspection and say so.
   - Record package-specific CLI/config gotchas hit during the run in
     `references/quirks/<pkg>.md` — ONE file PER PACKAGE, extended on
     each assessment; never fork a new file per topic. `ls
     references/quirks/` must stay a clean index of packages, and the
     next assessment of this package must load exactly one file. Append
     new sections, attributing them to the run that found them.
   - Artifact policy (anti-bloat): the finished workdir holds a FIXED
     manifest and nothing else —
     * REPORT.md, delta-analysis.md, container-ips.txt
     * the harness scripts (setup / suite / hop driver)
     * one results-<container>-<phase>.txt per suite run (the matrix's
       source; small by design — this is the only category whose count
       scales with phases x containers). Put these in a subdirectory
       `results`
     * ONE minimal reproducer + remediation script pair per numbered FAIL
       row — repro-<n>-*.sh / fix-<n>-*.sh, self-contained, named after
       the failure section, with a header stating what they reproduce,
       their preconditions, and the expected output. These are the most
       useful emitted artifacts; a regression with no reproducer script
       is an unfinished report. These should be as small as reasonable
       while maintaining readability for the triage.
     * ONE evidence.txt holding the exact excerpts (log lines with their
       source, or URL + fetch date + grep counts for web sources) that
       back every quoted claim in the report.
     Everything else is intermediate: setup/update/upgrade full logs,
     downloaded release-notes or quirks files, generated key material —
     mine the useful lines into evidence.txt and DELETE the files. Full
     do-release-upgrade logs remain inside each container at
     /var/log/dist-upgrade (containers are left running), and web sources
     are re-fetchable from the cited URLs, so nothing is lost.
   - Criterion: report written; its results matrix matches the raw
     per-phase results files and the aggregator's output; the workdir
     contains only the manifest (no full logs or downloaded pages).

## Pitfalls

- When supervising do-release-upgrade from the host, match the real process
  name: after download the in-container upgrader runs as
  "/tmp/ubuntu-release-upgrader-*/<series> --frontend=... --devel-release" —
  pgrep patterns for "do-release-upgrade" go stale mid-upgrade and report
  completion while dpkg is still running. Match "ubuntu-release-upgrader"
  plus a re-check after a short delay. Count with
  `pgrep -f <pattern> | wc -l`, never `pgrep -cf <pattern> || echo 0`:
  pgrep exits 1 on no match, so the fallback echoes a second, non-numeric
  line into the count, the completion test never succeeds, and the poll
  loop spins to its deadline on a container that already landed.
- Never wait unbounded on `systemctl is-system-running -q` after a
  container restart: a container routinely comes up "degraded", -q
  suppresses the answer instead of succeeding, and the wait hangs forever —
  before the upgrader has even started, wasting the whole launch. Wait
  only out "initializing", bounded, and tolerate "degraded".
- A supervisor timeout during a detached-in-name-only `do-release-upgrade`
  kills only the host-side lxc exec; the in-container upgrade continues
  orphaned and taints later attempts (dpkg locks; a subsequent plain
  `apt-get full-upgrade` finishes the release upgrade WITHOUT the
  upgrader's quirks — silently unrepresentative). If it happens: let it
  finish or kill it inside the container, then
  `dpkg --configure -a; apt-get -f install`, and keep a clean single-run
  container as the representative for that path.
- Never restart a container mid-dpkg; if it happens, repair with
  `dpkg --configure -a`.
- The upgrader refuses to start until the system is fully updated
  in-release, and again after kernel/libc updates until a reboot (restart
  the container). After landing on a new series there are usually NEW
  pending updates — repeat the update + restart loop before the next hop.
- Setup scripts must be idempotent (re-runnable after a partial failure)
  and must RESTART services after changing config or key material:
  `systemctl enable --now` is a no-op on an already-running daemon, and
  reload commands often cover only secrets/settings, not NEW certificate
  or key files — `systemctl restart <service>` after material changes is
  the reliable pattern.
- Cloud images may enable only the `main` component; helper packages often
  live in universe — extend Components in /etc/apt/sources.list.d/ubuntu.sources.
- do-release-upgrade caches meta-release files under
  /var/lib/update-manager/; delete them when debugging "no new release
  found" oddities after changing Prompt.
- A current-series fresh-install container is the control group: a
  "failure" that also happens there is not an upgrade regression.
- When a delta patch changes library defaults, both client tools AND
  daemons pick up the new default — test each role separately, and expect
  the obvious override knob to gate a different code path than the one that
  broke (verify the override actually fixes it before recommending it).
- A daemon that ships a MAC profile (AppArmor on Ubuntu) confines your
  HARNESS's isolated test instances too, not just the deployment under
  test: put scratch data/state directories under paths the profile
  allows, owned by the service user, and expect /tmp or
  capability-requiring spots to fail on some series. Before concluding
  the probe is broken, decide whether the profile is the actual finding
  (a custom-path denial) or just harness noise — both look like EPERM in
  the probe's own log.
- AppArmor/audit denials for a containerized daemon are invisible inside
  the container (dmesg and the kernel journal are unavailable there): read
  the HOST kernel journal and match lines by the container namespace
  string (namespace="root//lxd-<name>_..."). That attribution doubles as
  the report's evidence trail.
- Harness fixtures that must survive until the post-upgrade suite run
  (probe backends, content the suite starts on demand) belong on
  PERSISTENT storage such as /var/lib/<pkg>-test, never /tmp: /tmp is
  tmpfs and the post-hop container restart wipes it, producing a
  first-post-upgrade FAIL that looks exactly like an upgrade regression
  (apache2 precedent: a python3 proxy backend vanished mid-path; the
  service under test was fine — only the fixture was gone).
- Never use `pkill -f <pattern>` inside a `bash -c` probe whose own
  command line contains the pattern (starting a probe daemon and then
  pkill-ing its command string): pkill matches the probe shell's OWN
  /proc cmdline and SIGTERMs the running test. Track the daemon with
  `pid=$!` and `kill $pid` instead.
- `lxc list <name>` is a pattern match, not an exact lookup: whenever
  one container name is a prefix of another, the shorter name's query
  returns both, and a state check sees a multi-line value that never
  equals "RUNNING". Anchor the pattern (`lxc list ^<name>$`) or use
  `lxc info <name>` for exact per-container state.
- When reverting a shipped-AppArmor-profile site rule to re-establish
  stock behavior (e.g. re-baselining the control after demonstrating a
  fix), TRUNCATE /etc/apparmor.d/local/<profile> — never delete it: the
  main profile's `#include <local/...>` is mandatory, `apparmor_parser -r`
  fails on the missing file, and the previously-loaded (fixed) profile
  silently stays active, contaminating "stock" runs with stale rules.

## Verification

- Every upgrade path has baseline + post-upgrade results files, and every
  cell in the report's results matrix matches them (each FAIL row has a
  numbered failure-detail entry).
- Each failure has: exact error text, root cause, verified workaround, and
  verified proper fix — plus its repro-<n>-*.sh / fix-<n>-*.sh script pair
  in the workdir.
- The workdir matches the artifact manifest from step 7: no full upgrade or
  setup logs, no downloaded web pages, no generated key material left
  beside the manifest files.
- The report states the notification verdict per finding with evidence.
- All containers report the intended final series in /etc/os-release.

Supporting files in this directory:
- `templates/test-suite-template.sh` — PASS/FAIL harness (role-parameterized
  only when the package has multiple deployment roles).
- `templates/hop-driver-template.sh` — host-side release-upgrade hop
  driver (usage contract, reboot-required handling, detached in-container
  upgrader, robust completion polling, per-hop log pulls, recovered-hop
  detection); start step 4's hops from it instead of improvising a driver
  under time pressure.
- `templates/results-aggregate.py` — cross-tabulates results-*.txt into
  the report matrix and lists per-file FAILs; build and verify the report
  matrix with it instead of transcribing by hand.
- `templates/report-template.md` — report skeleton with the results matrix.
- `references/quirks/<pkg>.md` — ONE file per package (never one per topic), holding
  the package-specific CLI/config pitfalls and findings from every past assessment.
  Read the package's file in step 1 if it exists; extend it in step 7.
  `ls references/quirks/` is the live index of assessed packages — never
  re-enumerate the files here, or this section goes stale the moment a new
  package file is added.
