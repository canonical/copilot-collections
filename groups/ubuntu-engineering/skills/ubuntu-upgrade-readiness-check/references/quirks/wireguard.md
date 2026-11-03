# wireguard — upgrade-readiness quirks (from the 2026-10-16 stonking assessment)

## AppArmor profiles (the big one — LP#2165046)

- Ubuntu's `apparmor` package (NOT wireguard-tools) ships `wg` and `wg-quick`
  profiles (+ `wg-quick//ip`, `//nft`, `//sysctl`) from 26.04 (resolute,
  apparmor 5.0.2) onward. Enforced by default → executing /usr/bin/wg-quick
  directly (PATH, interactive, or its own wg-quick@.service unit) SIGSEGVs:
  the profile denies mmap of the interpreter the kernel loads via wg-quick's
  `#!/bin/bash` shebang. Filed as LP#2165046 (2026-08-25, Confirmed, against
  wireguard-tools (Ubuntu) though the fix belongs in the apparmor package).
- The LP-suggested minimal fix (`file mr /usr/bin/bash,` in
  /etc/apparmor.d/wg-quick) removes the SIGSEGV and restored wg-quick on
  resolute (apparmor 5.0.2) but NOT on stonking (apparmor 6.0.0~alpha1):
  there wg-quick fails silently with rc=1 and zero output — even under
  `aa-exec -p wg-quick -- bash -x` (no trace lines at all). Only unloading
  both profiles (`apparmor_parser -R`) restored full function in LXD.
- The shipped profiles also deny ordinary workflows when loaded:
  `wg-quick strip <iface>` ("echo: write error: Bad file descriptor") and
  `wg syncconf <iface> <tmpfile>` ("fopen: Permission denied"). So "fix the
  segv with the mr rule" is not enough for a working system in LXD; a
  report-comment-worthy addendum to LP#2165046.
- Testbed recipe: probe stock behavior (expect rc=139 on 26.04/26.10),
  then `apparmor_parser -R` both profiles before any suite run.

## Versioning trap

Upstream used 0.0.YYYYMMDD versioning between 2022–2025, which Debian-sorts
BELOW 1.0.20210914. Every recent series carries inert leftover universe
publications (noble-updates 0.0.20230223-1ubuntu0.24.04.2, resolute
0.0.20231211-1build1, stonking 0.0.20260522-1). The version real users get
is always the 1.0.x one in main — do not let the 0.0.x noise confuse
rmadison/API output (Launchpad's getPublishedSources pocket filter DOES
work; the entries are real but version-inert).

## wg CLI output details

- `wg show <if> dump` peer line fields: pub, psk, endpoint, allowed-ips,
  latest-handshake, rx, tx, persistent-keepalive — keepalive is field EIGHT.
  Empty psk prints the literal string "(none)" (not empty); disabled
  keepalive prints "0" on resolute-era and "off" on 1.0.20260223 — assert
  on both spellings across the upgrade.
- `wg-quick strip`/`syncconf` legitimately leak the PRIVATE key into the
  emitted config; wg-quick up on resolute+ also prints the configured
  endpoint of non-handshaking peers (`wg show endpoints`), so endpoint
  routes matter even for "offline" fixtures.

## Test-fixture gotchas found this run

- MTU tests: the endpoint whose route decides the auto-MTU must not be a
  LOCAL address — local routes go via `lo` (MTU 65536) and break
  smallest/largest expectations. Use a TEST-NET IP routed via the default
  route on hub/control containers.
- `wg-quick up ... | head -N` SIGPIPEs wg-quick mid-run (kills it around
  the 4th [#] line, leaving set_dns/DNS assertions broken). Redirect to a
  file, then read the file.
- Suite bodies: bash -c bodies need `set -e` AND the real assertion as the
  last statement — otherwise cleanup steps (`rm -f`) mask failures with
  vacuous passes. Inside single-quoted bodies do NOT escape `\$(...)`:
  the container shell must expand it; `\$` leaves literal keys in configs.
- grep patterns with `\t` (BRE) match literal 't', not tab — use awk -F"\t".

## Host/LXD environment notes (this host, not Ubuntu)

The default LXD zfs pool showed multi-minute windows where bash-5.3
containers read freshly-written script files as EMPTY (silent rc=1, zero
output) — e.g. `bash /root/setup.sh` doing nothing, `wg genkey > file`
producing empty files. Never reproduced on a dir/ext4-backed pool. If an
LXD-ZFS testbed starts silently no-op-ing scripts, suspect this before
debugging the guest, and move the topology to a dir pool.

(Attribution: found during the 2026-10-16 resolute→stonking / noble→
resolute→stonking assessment; scripts repro-1/fix-1, repro-2/fix-2 in the
workdir alongside REPORT.md.)