# nginx — assessment quirks and gotchas

Sections attributed to the run that found them. Extend this file (ONE file
per package) on each new assessment of nginx; never fork per-topic files.

## 2026-10-21 run (noble→resolute→stonking, ~/nginx-upgrade-tests)

- **"ssl on;" is the startup breaker, http2 stuff only warns.** Upstream
  removed the `ssl` directive in 1.25.1: on resolute/stonking it is
  `[emerg] unknown directive "ssl"` — nginx.service fails to start and the
  whole reverse-proxy deployment goes dark. `http2_push` is merely
  "obsolete, ignored" and `listen ... http2` "deprecated" — both still
  PARSE and serve. Root-cause order for a dead nginx after LTS upgrade:
  grep for `ssl on;` before anything else.
- **`ssl_protocols` alone does NOT re-enable legacy TLS.** On Ubuntu the
  observable TLS1.1 refusal (even with the shipped noble
  `ssl_protocols TLSv1 ...` listing it) comes from libssl cipher
  seclevel filtering, not the protocol list: nginx's default cipher
  set has no SECLEVEL<=0 TLS1.1 suite. To actually serve legacy TLS you
  need BOTH `ssl_protocols TLSv1 TLSv1.1 ...;` AND
  `ssl_ciphers ALL:@SECLEVEL=0;` (verified). The upstream 1.27.3
  "TLSv1/1.1 disabled by default" change is therefore invisible on
  Ubuntu shipped configs — do not report it as a user-facing flip.
- **Malformed-Host behavior flip is client-visible but silent.** 1.29.4
  (stonking hop) rejects requests with a malformed Host header /
  request-line host with 400; resolute serves them (200, default
  server). No server-side directive relaxes it — remediation is at the
  client/edge. Synthetic monitors or health probes with weird Host
  values start failing at the hop with only an access-log 400.
- **Reverse-proxy wire format flips in 1.29.7 (stonking hop).** Default
  `proxy_http_version` 1.0→1.1, upstream keepalive on by default, and
  `Connection` header no longer sent to backends. Backend log/ACLs/WAFs
  keyed on "HTTP/1.0 + Connection: close" observe changed traffic; pin
  with `proxy_http_version 1.0; proxy_set_header Connection close;`
  (verified restoring noble-era bytes).
- **nginx-extras arch flip (real binary → metapackage) upgrades in
  place.** resolute's nginx-extras is arch:amd64 real binary; stonking's
  is arch:all metapackage. Same-name any→all upgrade through
  do-release-upgrade lands cleanly (verified); no removals, no
  obsolete-package noise, service survives.
- **Ubuntu delta is branding only** (`--build=Ubuntu`,
  `server_tokens build`): survives hops, `nginx -v` shows
  "(Ubuntu)". The `nginx` Breaks/Replaces fields are old-version cleanup,
  not upgrade obstacles.
- **Harness notes:** backend fixtures that assert on proxied wire bytes
  must run their own HTTP server on a dedicated port — reusing the
  suite's 8080/8081 collides with the standing fixture conf and nginx -t
  fails (duplicate listen), silently skipping your reload. Always
  `systemctl reload nginx && sleep 1` before probing a config change —
  reload returns before workers drain, and an immediate probe can hit
  the old worker and report the old behavior.
- **Ubuntu release-notes coverage gap confirmed:** 26.04
  summary-for-lts-users has zero nginx mentions; 26.10 zero so far;
  26.04 changes-since-previous-interim only a cosmetic "1.28.2 bugfix"
  line. None of the behavior changes above are documented, no upgrader
  quirk exists for nginx, and nginx-common's NEWS is still 2017-era.