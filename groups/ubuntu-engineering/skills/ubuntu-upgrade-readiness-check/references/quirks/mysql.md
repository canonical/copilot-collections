# mysql — upgrade-readiness quirks and findings

Accumulated per-package notes from upgrade-readiness assessments. One file
per package; extend, never fork. NOTE: mysql is a CHAIN of differently-named
source packages per series (mysql-8.0 / mysql-8.4 / mysql-9.7 ...), assessed
as one unit — this file covers the whole chain.

## 2026-10-20 assessment (noble->resolute->stonking; stonking = 9.7.2-4ubuntu1)

CLI/config/packaging pitfalls hit during the run:
- The chain's upgrade gates live in THREE places, all verified live:
  1) ubuntu-release-upgrader quirk `_test_and_fail_mysql_server_using_
  mysql_native_password` (both resolute and stonking upgraders):
     * toDist==resolute: aborts if accounts use mysql_native_password AND
       config does not explicitly enable it;
     * toDist==stonking: aborts if config explicitly enables it (the 26.04
       documented workaround state IS the blocker on 26.10).
  2) mysql-server preinst (9.7): blocks <8.4 upgrades, native_password
     accounts, mysql_native_password refs in config (defense in depth; the
     quirk fires first in practice).
  3) mysqld itself: 9.7 refuses to start with mysql_native_password in config
     (option removed 9.0).
- The 26.04 documented workaround `mysql_native_password=ON` is 8.4-language:
  applied on noble (8.0) mysqld refuses to start ("unknown variable") — crash
  loop until 8.4 lands. The quirk gate passes on CONFIG PRESENCE ONLY
  (my_print_defaults), not service state, so the release upgrade still
  completes from the broken state; do not restart mysql on 8.0 after applying.
- Quirk account queries go through /etc/mysql/debian.cnf as root: passworded
  debian-sys-maint on noble (8.0), passwordless auth_socket on 8.4/9.7 — run
  probes as root or the user list silently comes back empty.
- AppArmor usr.sbin.mysqld (shipped all series): only /var/lib/mysql/** and
  the exact default socket names are allowed. A second instance on a custom
  datadir dies with EPERM-as-root on initialize and, after allowing the
  datadir, on the socket lock (urc2.sock.lock mknod). Fix: site rules via
  local/usr.sbin.mysqld (datadir rw/rwk + socket/pid rw). The profile's
  #include <local/usr.sbin.mysqld> is MANDATORY — deleting the local file
  breaks `apparmor_parser -r` ("Could not open local/usr.sbin.mysqld"); ship
  an EMPTY file for stock behavior.
- Denials inside LXD are invisible in-container (as with mariadb): read the
  HOST kernel journal, match namespace="root//lxd-<container>_...".
- DBD::mysql (libdbd-mysql-perl 4.053, links libmysqlclient24) against a COLD
  caching_sha2_password account over remote non-TLS fails: "Authentication
  plugin 'caching_sha2_password' reported error: Authentication requires
  secure connection." Same on 8.4 — pre-existing semantics, not a version
  jump. Warm-cache retry passes; mysql/mysqldump CLI (TLS default) fine.
- mysqldump roundtrip on the SAME server needs --set-gtid-purged=OFF on 9.7
  (GTID_PURGED overlap error otherwise).
- Suite harness: dpkg-query -W 'mysql*' globs print non-installed known names
  with EMPTY version lines — filter with -f '${db:Status-Abbrev} ...' |
  grep '^ii '.
- auth for suite probes: root@localhost is auth_socket on all three series
  when installed noninteractively (empty debconf password); `mysql` as root
  just works.
- Hop mechanics: noble mysql-server is a metapackage → resolute/stonking
  mysql-server is the REAL package (same name) — the rename rides on that
  name continuity + Breaks/Replaces(<<8.4); old *-8.0 binaries removed as
  obsolete, libmysqlclient21→24 soname bump on hop 1 only; NO conffile moves
  for mysql on either hop. All hops landed with zero dpkg recoveries.

Findings (details + repro/fix scripts in the 2026-10-20 workdir
~/pkgs/mysql-9.7/mysql-upgrade-tests/, REPORT.md):
1. resolute->stonking notification gap: 26.10 release notes announce the
   8.4→9.7 update with ZERO mysql_native_password coverage; the removal and
   the fact that the 26.04 workaround config blocks the 26.10 upgrade are
   only covered by the upgrader gate message. Suggested notes entry drafted
   in REPORT.md.
2. Custom-datadir second instance: AppArmor-denied on ALL series (pre-
   existing), local-rule fix verified (repro-1/fix-1 scripts).