# dovecot — upgrade-assessment quirks (one file per package)

Findings from the 2026-10-19 assessment (noble->resolute->stonking,
workdir ~/pkgs/dovecot/dovecot-upgrade-tests/, REPORT.md). Extend this
file on the next assessment; do not fork new files per topic.

## 2026-10-19 run (stonking readiness)

* The 2.3->2.4 config break ABORTS do-release-upgrade, not just dovecot:
  dpkg keeps every locally-modified conffile in 2.3 syntax, the
  dovecot-core postinst restart fails ("The first setting must be
  dovecot_config_version"), dpkg errors, and the upgrader falls into its
  "Could not install the upgrades ... recovery will run now
  (dpkg --configure -a)" path. Hops that start from 2.4-syntax config are
  clean — verify the config language BEFORE blaming the upgrader.
* No compat mode exists in 2.4: `dovecot_config_version = 2.3` is
  refused ("Currently supported versions are: 2.4.0 2.4.1 2.4.2"), and
  mail_location is absent from the 2.4 settings registry entirely
  (renamed family: mail_driver/mail_path/mail_home/mail_inbox_path).
* Migration trap: `mail_location = maildir:~/Maildir` ->
  `mail_path = ~/Maildir` is WRONG; mail_driver defaults to mbox
  (Debian/Ubuntu 10-mail.conf), silently orphaning existing ~/Maildir
  data (INBOX moves to /var/mail/%{user}). Must set
  `mail_driver = maildir` too. (doveadm-sync(1) documents the canonical
  pair: mail_driver = maildir + mail_path = ~/Maildir.)
* 90-plugin.conf is obsolete in 2.4 (plugin {} section removed): the
  postinst auto-removes it only when UNMODIFIED ("Removing unmodified
  obsolete configuration file" in apt-term.log); locally-modified ones
  stay and break the parser. Migrate sieve settings into 90-sieve.conf as
  `sieve_script personal { driver = file; path = ~/sieve;
  active_path = ~/.dovecot.sieve }`.
* auth-passwdfile.conf.ext: 2.3 syntax is anonymous `passdb { driver =
  passwd-file; args = ... }`; 2.4 requires named sections with
  driver-scoped settings (`passdb passwd-file { passwd_file_path = ...
  }`, `auth_username_format = %{user}`) — `args` inside a named section
  is "Unknown setting".
* protocol blocks: `mail_plugins = sieve` -> `mail_plugins { sieve = yes }`
  (list setting became a boolean block).
* Weak password schemes (PLAIN-MD5 and friends) refused by default in
  all 2.4 series INCLUDING fresh installs (not an upgrade regression —
  use the fresh-install control container to classify): error text
  names the knob `auth_allow_weak_schemes=yes`; proper fix is
  `doveadm pw -s SSHA512` re-hash.
* MANAGESIEVE protocol quirks (helpers.py probes):
  - 2.4 no longer advertises/offers the legacy LOGIN command at all
    ("Error in MANAGESIEVE command received by server"); use
    `AUTHENTICATE "PLAIN" {len+}\r\n<base64(\0user\0pass)>`.
  - greeting is MULTILINE (IMPLEMENTATION/SIEVE/NOTIFY/SASL/STARTTLS/
    VERSION capability lines then `OK "Dovecot ready."`) — read until
    the OK line, don't assume a single line.
  - literal syntax is `{n+}` CRLF n-octets CRLF — a missing closing brace
    ({115+ CRLF) is accepted as a broken command and the server then
    interprets each script line as a MANAGESIEVE command (very
    confusing in logs).
  - sieve `mailbox` extension provides a TEST, not a command: there is no
    `mailbox :create "x";` command — use `fileinto :create "x";`.
* ucfq -w on a REMOVED conffile prints the path with empty fields —
  empty output means already-removed, not untracked.
* Release notes: 26.04 summary-for-lts-users has a Dovecot section
  pointing at the upstream 2.3->2.4 doc; 26.10 notes' dovecot section
  has no upgrade guidance (none needed, 2.4.2->2.4.4 is
  config-compatible). No DistUpgradeQuirks hook in either series; only
  dovecot-core carries NEWS(.Debian).gz, and the upgrader sets
  APT_LISTCHANGES_FRONTEND=none so NEWS never surfaces mid-upgrade.