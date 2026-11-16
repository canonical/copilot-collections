# strongSwan test-setup gotchas (from the 2026-10 noble->stonking run)

Concrete CLI/config pitfalls hit while building the strongSwan upgrade-path
harness (noble 5.9.13 / resolute 6.0.4 / stonking 6.0.7). All verified live
in LXD containers; save yourself the four debug cycles.

This is strongSwan's single quirks file: EXTEND it on each assessment
(attribute new sections to the run that found them) — do not create
topic-named sibling files.

## strongswan-pki

- `--outform` takes LOWERCASE values on 5.9.13 (`pem`/`der`); `PEM` fails
  with "invalid key output format". Use lowercase everywhere for compat.
- `--not-before`/`--not-after` parse with `--dateform` (default format is
  `%d.%m.%y %T`, not ISO). For `YYYYMMDDHHMMSSZ` pass
  `--dateform "%Y%m%d%H%M%SZ"`.
- `pki --issue --in <key>` defaults to reading a PUBLIC key; a private key
  file needs `--in <file> --type priv`, else "building CRED_PUBLIC_KEY
  failed / parsing public key failed".
- Cloud-image containers see many "plugin 'x': failed to load" lines from
  pki/swanctl listing plugins from OTHER binary packages — harmless noise;
  grep it out of logs.

## swanctl.conf (vici) vs ipsec.conf (stroke)

- The strict-proposal `!` suffix is ipsec.conf/stroke syntax ONLY.
  stroke_config.c strips it; vici passes the string to
  proposal_create_from_string(), which rejects it:
  "invalid value for: proposals, config discarded". Rejected identically on
  5.9.13 and 6.0.x — a config-porting gotcha, not an upgrade regression.
- PSK secrets are SECTIONS in swanctl.conf: `secrets { ike-any {
  secret = "..." } }`. A bare `ike-psk = "..."` key loads nothing and both
  sides fail with "no shared key found" / AUTH_FAILED.
- stroke ipsec.secrets: use `: PSK "secret"` (no ID selectors) for a
  catch-all; `%any : PSK` does NOT match when both peers send specific IDs.
- Installing cert/key files under /etc/swanctl or /etc/ipsec.d after the
  daemon started: `swanctl --load-creds` reloads them on the swanctl side,
  but stroke needs `ipsec rereadsecrets` for secrets and a SERVICE RESTART
  for new CA certs (rereadsecrets/rereadcerts does not pick up new files on
  all versions). Simplest: write config first, then
  `systemctl restart strongswan[-starter]`.
- strongswan-charon Conflicts charon-systemd: a single container cannot host
  both flavors, and the stroke flavor requires strongswan-charon. Plan the
  flavor split as separate containers; a fresh post-26.04 `strongswan`
  install is swanctl-flavored by default.
- swanctl's `--file` option for out-of-tree configs trips its apparmor
  profile (usr.sbin.swanctl) — test configs must live under /etc/swanctl.

## Peer/daemon behavior worth knowing

- Expired pre-trusted CA chains are rejected by chain validation on ALL
  series (responder logs: "issuer certificate invalid ... no trusted RSA
  public key found"); 6.0.7 additionally enforces validity of pre-trusted
  self-signed certs outright (NEWS 6.0.7). There is NO config knob to relax
  certificate validity for pre-trusted certs (source: no such option in
  src/libstrongswan) — the only fix is renewing the CA + re-issuing leaves.
- Default proposals on 6.0.x need no `!` and no libstrongswan-extra-plugins
  for AES/SHA/MODP: openssl (in libstrongswan) + aesni provide them
  (`swanctl --list-algs`).
