# openldap quirks (upgrade-readiness-check references)

ONE file for the openldap package, extended on each assessment.

## 2026-10 run: noble -> resolute -> stonking assessment

- slapd and any slapd -Tt / slaptest config-check invocation is confined by
  /etc/apparmor.d/usr.sbin.slapd (enforce by default). Test slapd.conf files
  must live under /etc/ldap/** (profile grants kr) — /tmp config files fail
  with a misleading "bad configuration file!" (real cause: AppArmor EACCES,
  visible with -d1).
- back-config (cn=config) does NOT evaluate substring value filters like
  (olcModuleLoad=*syncprov*) — they silently return nothing. To check loaded
  modules: ldapsearch -b cn=config olcModuleLoad (retrieve values, grep).
- Loading an overlay module (e.g. syncprov.so) via olcModuleLoad then adding
  the olcOverlay={0}syncprov child entry in the same breath fails with
  "attribute 'olcOverlay' not allowed" — restart slapd between moduleload
  and overlay entry so the schema is registered. The overlay itself must be
  ldapadd'ed as a child entry (dn: olcOverlay={0}syncprov,olcDatabase={1}mdb,
  cn=config), not added as an olcOverlay attribute on the database entry.
- ldapmodrdn's new-RDN argument needs attribute=value syntax ("uid=foo");
  "uid:foo" is rejected with "Invalid DN syntax (34) / invalid new RDN".
- pw-pbkdf2 ships in slapd-contrib (universe) — universe must be enabled
  before moduleload pw-pbkdf2.so works; missing module gives
  "lt_dlopenext failed: (pw-pbkdf2.so) file not found".
- Preseeding slapd/no_configuration=true on noble leaves slapd unable to
  start at all ("No configuration file was found"); for a syncrepl consumer,
  install normally, empty the DB, then ldapmodify olcSyncrepl onto the
  existing mdb database instead.
- NEWS packaging detail: the binary-specific debian/slapd.NEWS SHADOWS the
  source-level debian/NEWS for the slapd package — slapd's installed
  NEWS.Debian.gz is stale (2.5.5-era) while libldap2's carries the current
  GnuTLS->OpenSSL entry; ldap-utils/libldap-common symlink to libldap2's.

## 2026-10 run: upgrade findings worth re-testing next cycle

- GnuTLS->OpenSSL carry-overs, in breakage order: (1) olcTLSCipherSuite with
  a GnuTLS priority string is FATAL AT STARTUP on the OpenSSL build
  ("no cipher match") — and the release upgrade completes fine with slapd
  dead, so post-hop checks must not assume the service survived; (2) a
  GnuTLS TLS_CIPHER_SUITE line in /etc/ldap/ldap.conf stays valid-looking on
  a noble client but turns fatal only once that host's own libldap is
  OpenSSL-built — test client hosts one hop AFTER their server.
- Live ldapmodify to cn=config VALIDATES olcTLSCipherSuite (refuses bad
  strings); only on-disk slapd.d carry-over from the old release hits the
  startup failure. Repros must edit the LDIF offline, not ldapmodify.
- do-release-upgrade's noninteractive frontend answers conffile prompts with
  "no" (keep local): a locally modified /etc/apparmor.d/usr.sbin.slapd is kept
  without the @{run}/systemd/notify rule -> Type=notify timeout (LP #2119884
  on upgrade paths). Same mechanism preserves local /etc/default/slapd edits.
- debian/slapd.NEWS shadows debian/NEWS for the slapd binary: slapd's
  installed NEWS.Debian.gz misses source-level NEWS entries; check libldap2's
  for the current content.
