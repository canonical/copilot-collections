# bind9 assessment quirks

Findings, gotchas and harness notes from assessments of the bind9 package.
ONE file per package — extend on each assessment; do not fork per-topic files.

## 2026-10 assessment (stonking readiness; containers bind9-{a,e,b,ctl})

- The bind9 package postinst (resolute 1:9.20.18-*, stonking 1:9.20.24-*) runs
  `named-checkconf /etc/bind/named.conf` under `set -e`. Combined with dpkg's
  noninteractive conffile policy (prompts answered "keep current"), a locally
  modified named.conf referencing files or statements removed by the 9.20-era
  packaging/upstream (e.g. the deleted /etc/bind/named.conf.default-zones include)
  makes the POSTINST exit 1 and aborts do-release-upgrade mid-hop; the recovery
  lands the series but leaves bind9 half-configured with named crash-looping.
  LP #2150582 (real user hit, Won't Fix). Remediation: comment the dead include,
  `dpkg --configure bind9`, restart.
- dig's output banner echoes the query args, so `dig ... SOA ... | grep -q SOA`
  false-PASSes on comms errors ("connection refused" still prints the banner).
  Assert on record shape (`grep -qE 'IN[[:space:]]+SOA'`), never on the type token.
- The systemd unit is `named.service`; `systemctl is-active bind9` works via the
  bind9.service alias, but `status bind9` prints named.service.
- rndc works out of the box (Debian patches the default key path to
  /etc/bind/rndc.key); no rndc.conf needed.
- rm_conffile leaves `<file>.dpkg-remove` backups in /etc/bind (db.*, zones.rfc1918,
  named.conf.default-zones) — useful as upgrade forensics; the new package's shipped
  conffiles are staged as `*.dpkg-dist`.
- /etc/bind/bind.keys stopped being shipped in resolute (9.20 packaging) but is NOT
  rm_conffile'd: upgrades from noble keep an ORPHANED file, and bin/named/server.c
  uses it to override the built-in trust anchors if present and populated. In practice
  validation still worked (stale anchor still validates); still worth telling users
  to delete it.
- BIND 9.20's allow-transfer default is deny (#4728) — secondaries of a 9.18-era
  primary with no explicit ACL stop receiving AXFR/IXFR the moment the primary hops.
  The breaking side (primary) logs "zone transfer ... denied"; the broken side
  (secondary) just serves stale data silently — probe transfers explicitly.
- BIND 9.20 removed 9.18-era options fatally (auto-dnssec, coresize, lock-file,
  alt-transfer-source, delegation-only, keep-response-order, DSCP...). On 9.18 those
  same statements only WARN in named-checkconf — so a "valid on from-series" legacy
  config is a clean detection probe: exit 0 on 9.18, exit 1 on 9.20.
- auto-dnssec allow; requires dynamic DNS or inline-signing in the zone to even parse
  (checkconf error on 9.18); use `auto-dnssec off;` for a pure syntax marker.
- Per-container suite parameters via a sourced env file (/etc/bind9-urc.env: zone names,
  peer IP) kept one suite file identical across all containers — the aggregator stays
  happy and N/A rows stay honest (unset parameters -> SKIP -> '-' cell).
- Cloud images resolve via systemd-resolved (stub on 127.0.0.53/54); bind9 forwarders
  should point at the bridge resolver (10.58.79.1) — root-hints recursion from inside
  LXD works too. First cold-cache external query after a restart can transiently
  fail; retry the probe (3x) rather than trusting a single shot.