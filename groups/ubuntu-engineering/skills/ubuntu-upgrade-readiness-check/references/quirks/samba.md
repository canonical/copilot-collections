# samba gotchas: container setup, packaging quirks, upgrade-path findings

Single quirks file for samba (the skill's ONE-file-per-package rule).
Sections attributed to the run that found them. Re-read this file before
any samba assessment; extend it, never fork topic files.

## From the 2026-10-14 run (noble -> resolute -> stonking assessment)

### Test-setup facts (container environment)

- AD DC provisioning in LXD REQUIRES `security.privileged=true` on the
  container: samba-tool provision's sysvol ACL setup (smbd.set_nt_acl via
  ntacls.py) fails with `NT_STATUS_ACCESS_DENIED`
  ("ERROR(runtime): uncaught exception - (3221225506, '{Access Denied}...')")
  in unprivileged containers — sysvol ACLs carry idmap uids (3000000+).
  Setting `security.privileged` on an EXISTING (running) container breaks
  systemd-networkd permanently (`status=243/CREDENTIALS`) and kills the
  DHCP lease — launch fresh privileged containers instead. Combine with
  `security.nesting=true` (matches the package's own autopkgtest setup).
- Hostnames longer than 15 chars break AD DC provisioning/startup via the
  netbios name limit (LP #2160627 — the package's own dep8 test forces a
  short hostname for exactly this reason). samba then dies at startup with
  "Failed to obtain server credentials, perhaps a standalone server?:
  NT_STATUS_CANT_ACCESS_DOMAIN_INFO" — misleading; check netbios name
  length first.
- 4.19/4.23 write /var/lib/samba/private/krb5.conf at provision; 4.24 does
  NOT — generate /etc/krb5.conf yourself on 4.24 (realms section pointing
  at the DC hostname).
- Wiping /var/lib/samba completely (rm -rf /var/lib/samba) deletes the
  package-created dir skeleton and provision then fails with
  "Failed to create directory /var/lib/samba/private"; wipe CONTENTS
  (rm -rf /var/lib/samba/*) or re-create the skeleton.
- A real noble DC install pulls winbind (samba master forks /usr/sbin/
  winbindd as a child); "bare bin:samba" DC setups must still install the
  winbind package or samba-ad-dc terminates with "winbindd child process
  exited" immediately.
- DC containers need smbclient installed explicitly (samba-ad-dc does not
  depend on it).
- MIT krb5 clients reject the enctype alias `rc4-hmac-md5`
  ("kinit: No supported encryption types (config file error?)") — use the
  canonical `arcfour-hmac-md5` spelling, with `allow_weak_crypto = true`.
- Kerberos auth needs the HOSTNAME (SPN cifs/dc.name@REALM), not the IP —
  smbclient -L <ip> --use-kerberos=required fails while -L <hostname> works.
- Kernel cifs mounts (fstab) are NOT viable in containers: the cifs.ko
  keyctl/upcall path returns ENOENT ("mount error(2)") even with keyutils
  and a valid ccache — container artifact; use smbclient for client-path
  coverage.
- smbd never enumerates CUPS queues into printer shares in this container
  environment (no pcap entries at log level 3 despite HAVE_CUPS,
  `printcap name = cups`, `load printers = yes` and a working lpstat
  queue) — identical on noble 4.19 and stonking 4.24, so [printers]/
  printing e2e tests are class-(c) N/A here. Root-caused once; do not
  re-investigate per path.
- Member servers with winbind (`security = ads`) need domain-qualified
  usernames everywhere on modern samba (`EXAMPLE\user`, `user@realm`);
  unqualified `user` stops resolving (nss + smbclient tree connect) unless
  `use default domain = yes` is set. `valid users =` in smb.conf must also
  be qualified.

### Packaging/upgrade findings (verified this run)

- noble bin:samba ships the AD DC binary AND samba-tool; the noble
  samba-ad-dc is an arch:all METAPACKAGE with no files. From resolute on,
  samba-ad-dc is a real arch:any package shipping /usr/sbin/samba etc.,
  and samba no longer depends on/recommends samba-ad-dc. A noble DC
  deployed without the samba-ad-dc metapackage (legal: bin:samba had
  everything) loses its DC at the N->R hop: the resolute samba.postinst
  stops samba-ad-dc.service and purges its systemd state; /usr/sbin/samba
  is gone. Fix: `apt install samba-ad-dc` restores the DC with all state
  intact (verified). Release notes DO document this
  (release-notes/26.04/summary-for-lts-users, "Samba" section).
- 4.24's AES-only `kdc default domain supported enctypes` default does NOT
  break RC4-capable accounts: a 4.24.7 KDC still issues arcfour session
  keys for accounts whose effective supportedEncryptionTypes include
  RC4 (verified on the stonking control DC with a keytab-provisioned
  RC4-only kinit). Not an upgrade regression in this configuration.
- The R->S release upgrade re-enables systemd-resolved (systemd preset on
  the new systemd package), which binds :53 before samba's internal DNS
  task can ("NT_STATUS_ADDRESS_ALREADY_ASSOCIATED" in log.samba;
  samba-ad-dc stays "active" but serves no DNS; kinit fails with "Cannot
  find KDC"). Bites every SAMBA_INTERNAL-dns DC whose admin had
  stopped/disabled resolved (mandatory on both series). Neither samba
  nor the upgrader handles it; release notes silent. Fix: mask
  systemd-resolved + restart samba-ad-dc (verified full restore). For DC
  setups: mask (not just disable) resolved — a plain disable does NOT
  survive a release upgrade.