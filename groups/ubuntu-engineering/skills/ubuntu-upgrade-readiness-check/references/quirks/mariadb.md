# mariadb — upgrade-readiness quirks and findings

Accumulated per-package notes from upgrade-readiness assessments. One file
per package; extend, never fork.

## 2026-10-19 assessment (noble->resolute->stonking; stonking = 1:11.8.9+ds-4ubuntu2)

CLI/config pitfalls hit during the run:
- On resolute/stonking, mariadbd writes are AppArmor-confined: isolated
  test instances need a scratch datadir under /var/lib/mysql (allowed by
  the profile) chowned to mysql AND world-writable during the
  mariadb-install-db bootstrap (bootstrap runs as root; resolute's profile
  denies dac_override, so root cannot write into mysql-owned 0700 dirs —
  stonking's profile grants dac_override/dac_read_search, a notable
  profile difference between the two series). /tmp as a scratch datadir
  fails on resolute.
- root@localhost on fresh installs shows plugin=mysql_native_password with
  the literal hash "invalid" — socket-only root; do not test for the string
  "unix_socket" in the plugin column. Test the property instead (root
  connects via socket; a nobody-run client cannot).
- Removed upstream options (innodb_defragment etc.) do NOT abort startup
  on 11.8 — they are silently accepted/ignored; option-parse probing
  (mariadbd --no-defaults --<opt> --datadir=/nonexistent and grepping for
  "unknown variable") is the cheap correct test. mariadb-install-db-based
  second-instance probes are slow and confounded by AppArmor.
- mariadb-print-defaults (Connector/C) and my_print_defaults read the same
  include chain as mariadbd; use them to see which config file a setting
  came from before assuming conffile behavior.
- innodb_purge_batch_size reports 127 on Ubuntu 11.8 builds (not the 300
  the upstream 10.11->11.4 guide mentions as the old default).

Findings (details + repro/fix scripts in the 2026-10-19 workdir
~/pkgs/mariadb/mariadb-upgrade-tests/, REPORT.md):
1. resolute->stonking conffile move preserves pid-file=/run/mysqld/... in
   locally-modified 50-server.cnf -> mariadbd crash-loop after the first
   reboot (works until then thanks to the postinst /run/mariadbd->mysqld
   symlink; nothing recreates /run/mysqld at boot on stonking).
2. mysql* names move to mariadb-{client,server}-compat on stonking; no
   dependency pulls the compat packages in, so they vanish on upgrade.
   mariadb-server-compat ships tmpfiles rule "L /run/mysqld - - - -
   mariadbd" that revives the legacy socket path once installed.
3. /etc/mysql/conf.d customs are neither migrated nor read on stonking
   (only non-dpkg-owned /etc/mysql/mariadb.conf.d files are moved by the
   preinst; dpkg-owned conffiles are renamed with "Preserving user
   changes" via dpkg-maintscript-helper, which is what bites in #1).
4. AppArmor enforce from 1:11.8.6-4 blocks custom datadirs; site rules in
   /etc/apparmor.d/local/mariadbd are the sanctioned fix (package NEWS
   documents this, but NEWS never surfaces during release upgrades).
5. 11.8 clients require TLS; 10.11 servers ship have_ssl=DISABLED ->
   client-hosts-first fleet upgrades lose DB connectivity (--skip-ssl
   works; 11.8 servers have TLS active out of the box, so servers-first
   order is safe in both directions).
6. Upstream RR-isolation change (ERROR 1020) is real on 11.8;
   innodb_snapshot_isolation=OFF restores lenient 10.11 behavior.
