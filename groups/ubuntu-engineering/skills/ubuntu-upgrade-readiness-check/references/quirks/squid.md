# squid — CLI/config/packaging quirks for upgrade-readiness testing

Findings from the 2026-10-08 assessment (noble 6.14 → resolute 7.2 →
stonking 7.7; squashed together from that run's evidence — extend, don't
fork).

## Packaging layout (decides topology)

- noble: `squid` (GnuTLS) and `squid-openssl` CONFLICT — one flavor per
  machine; both ship the same /etc/squid/{squid.conf,conf.d,
  errorpage.css} and a real /usr/sbin/squid binary.
- resolute+: co-installable. `squid` ships /usr/sbin/squid-gnutls,
  `squid-openssl` ships /usr/sbin/squid-openssl; /usr/sbin/squid is an
  update-alternatives symlink (gnutls prio 50, openssl prio 70 — with both
  installed the RUNNING binary is the openssl one). squid-openssl
  Pre-Depends: squid.
- Binary packages squidclient / squid-cgi / squid-purge exist on noble,
  vanish from resolute onward (upstream removed the tools; Debian 7.1-1
  dropped the packages). The upgrader removes an installed squidclient as
  obsolete.
- The noble→resolute hop upgrades an openssl-flavor machine in ONE
  transaction: remove old squid-openssl → install squid → conffile prompt
  (N = keep local) → alternatives register → unpack new squid-openssl.
  Verified clean; local squid.conf edits survive, ownership moves
  squid-openssl → squid.

## Config gotchas that bite the harness

- Debian's `include /etc/squid/conf.d/*.conf` sits AFTER
  `http_access allow localhost` in the shipped squid.conf — conf.d rules
  CANNOT preempt the localhost allow. Order-sensitive http_access rules
  must be inserted into squid.conf itself (before the first http_access
  line).
- `squid -k parse` exits 1 on FATAL directives — good parse probe — but it
  does NOT validate auth_param helper paths (missing helper binaries fail
  only at runtime).
- security_file_certgen: `-c` requires both `-s` AND `-M`; /var/lib/squid
  may not exist and must be mkdir'd first; ssl_db must be owned by proxy.
- ssl-bump https_port requires `intercept` (or tproxy) on 6.14 AND 7.x
  ("FATAL: ssl-bump on https_port requires tproxy/intercept which is
  missing").
- Transparent interception of the squid HOST's own traffic (iptables nat
  OUTPUT REDIRECT) breaks ALL local HTTPS — do-release-upgrade dies with
  "Failed to connect to https://changelogs.ubuntu.com/meta-release*" and
  the presented cert is the local ssl-bump CA. Scope interception to
  forwarded/LAN traffic, or add/remove the rule around the test. In the
  harness the rule is added and removed by the suite around the ssl-bump
  test only.
- Neither noble nor resolute default squid.conf has an UNcommented
  `http_access allow localnet` — transparent clients from the machine's
  own IP are denied (403) until you allow your local net.

## Test-harness environment quirks

- curl needs `--proxy-anyauth` to retry proxy basic auth after a 407 on
  resolute+ (curl 8.18+); with plain `-u` it gives up after the first
  challenge.
- Transparent-interception tests must force `curl -4`: the LXD containers
  get IPv6 and bypass v4-only iptables rules (false PASS otherwise).
- squid.conf.documented lives at
  /usr/share/doc/squid-common/squid.conf.documented.gz (NOT /etc/squid);
  `zcat` it to read per-directive defaults.
- Squid spawns basic-auth helpers on demand: a suite run immediately after
  `systemctl restart squid` may see the first auth attempt challenged —
  retry logic or a warm-up request makes the auth test stable.

## Version-jump behaviors measured (2026-10-08 run)

- FATAL on 7.x, fine on 6.14: ident/ident_regex ACLs, %ui logformat,
  mcast_miss_* directives. No workaround exists — remove the directives.
- ntlm_smb_lm_auth helper: present on noble, gone in resolute+ (CVE fix);
  config referencing it parses fine and breaks silently at runtime.
- basic_smb_lm_auth: never shipped on noble either (only basic_smb_auth).
- email_err_data default is ALREADY `off` on noble's 6.14 backport — the
  7.2 default change is NOT an upgrade regression for noble users.
- esi_parser and error_directory English still parse on 7.2 and 7.7:
  ESI is build-disabled (since Debian 6.12) and the langpack still ships
  the English→en symlink (watch for a future langpack dropping it).
- The Ubuntu 26.04 release notes' "removed in 7.2" list
  (client_delay_access, ftp_epsv, client/server_persistent_connections)
  is wrong — those still parse on 7.2; the actually-FATAL removals are
  not mentioned in the notes.
- cachemgr replacement workflow (works on all series):
  `curl http://127.0.0.1:3128/squid-internal-mgr/menu`.
- NEWS.Debian.gz in every squid binary package is stale (2021-era
  content) and never surfaces during a release upgrade
  (APT_LISTCHANGES_FRONTEND=none).
