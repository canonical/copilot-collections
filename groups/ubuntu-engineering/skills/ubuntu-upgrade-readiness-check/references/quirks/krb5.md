# krb5 gotchas: legacy enctypes vs the library-default delta

From the original krb5 upgrade-path run (noble -> resolute -> stonking,
krb5 1.20.1 -> 1.22.1) that motivated several SKILL.md rules — the
library-default pitfall, control-group logic, detached-supervision
pitfalls, the upgrader gates. The general rules live in SKILL.md; this
file keeps only the krb5-specific facts. Re-read before any krb5
assessment. (That run also verified the openssh/openssh-gssapi split was
auto-handled by the OpenSSHGSSAPISwitch quirk — origin of step 1's
quirks inspection.)

This is krb5's single quirks file: EXTEND it on each assessment (attribute
new sections to the run that found them) — do not create topic-named
sibling files.

## The delta and what it breaks

- The Ubuntu delta patch (LP: #2144909) dropped arcfour-hmac-md5 and
  des3-cbc-sha1 from the LIBRARY default permitted_enctypes list
  (src/lib/krb5/krb/init_ctx.c). A library default hits BOTH roles: after
  upgrade the KDC refuses rc4/des3-only principals with
  `KDC has no support for encryption type`, even when the client sets
  permitted_enctypes explicitly. A client-side PASS proves nothing about
  the KDC — test both roles (origin of that Pitfall).
- Upstream 1.21 release notes: KDC no longer issues RC4/triple-DES
  session keys unless allow_rc4 / allow_des3 is set — but those knobs
  gate session-key selection, a DIFFERENT code path than the client-key
  lookup the delta patch broke. They do NOT work around the delta-patch
  breakage; root-cause from the patched source, not from knob names.
- Verified proper fix: re-key principals to AES via `kadmin cpw`
  (demonstrated restoring stock-default behavior; no krb5.conf override
  restores it).

## Notification assessment specifics

- Release-notes coverage was role-asymmetric: the client-side default
  change was documented, the KDC-side effect and any remediation were
  not. NEWS.Debian.gz shipped only in the server package, so client-only
  hosts saw nothing. Check role coverage per finding, not just whether
  the package is mentioned.
- That run's recommendation: an ubuntu-release-upgrader quirk plus a
  release-notes amendment covering the KDC side and the re-key fix.

## Test-setup facts that caught it

- Topology: one KDC container per upgrade path + current-series control
  KDC + one old-series client container pointed at a KDC.
- Provision per realm: AES, rc4-only, AND des3-only user and service
  principals (plus admin principal, host keytabs, PAM integration,
  remote kadmin, kpasswd). The legacy-only principals are what expose
  the delta-patch breakage.
