# apache2 — assessment quirks and gotchas

## 2026-10-20 run: resolute (2.4.66-2ubuntu2.6) -> stonking (2.4.68-1ubuntu4)
- No upgrader quirk hooks: DistUpgradeQuirks.py (applied/ubuntu/stonking)
  has zero apache2 mentions.
- mod_lua survives the lua5.4 -> lua5.5 transition (LP: #2155757): a
  simple `LuaMapHandler` script written against the 5.4-era API runs
  unmodified under lua5.5. Use `LuaMapHandler /lua/ /path/handler.lua`
  with a `handle(r)` function; needs `a2enmod lua`.
- mod_ssl + ab work against libssl4/OpenSSL 4 out of the box; TLSv1.3
  and HTTP/2 (Protocols h2 http/1.1) verified. The snakeoil cert from
  the ssl-cert package is enough for a test TLS vhost.
- Conffile burn point for this jump: mods-available/autoindex.conf gains
  "XHTML" in IndexOptions (Debian 2.4.66-3). do-release-upgrade
  (noninteractive) keeps the user's modified file and leaves the
  upstream version as autoindex.conf.dpkg-dist — the upgraded server
  keeps serving HTML 4.01 listings until the admin merges it. Assert
  on listing presence (grep a marker filename), not on the doctype,
  or the suite flips across series.
- webdav DELETE-of-missing already returned 404 on 2.4.66, so the
  upstream 2.4.68 mod_dav_fs 404 change has no visible delta.
- `apache2ctl list-vhosts` exists only from 2.4.68 packaging on — a
  suite test asserting it fails on the from-series baseline by design.
- SSI probes: an `#if expr` that fails to *parse* (e.g. an unterminated
  regex literal) makes 2.4.66 print the if-branch content after the
  "[an error occurred...]" marker, while 2.4.68 prints nothing — a good
  probe shape for the mod_include change, assert only on non-500.
- WebDAV probe dirs must be chowned to www-data for PUT; DAV On needs
  no DavLockDB for plain PUT/GET/DELETE.
- On event MPM use mod_cgid (not cgi) for ExecCGI probes.
- Default-site access log is /var/log/apache2/access.log; name-based
  non-default vhosts log to other_vhosts_access.log when Ubuntu's
  other-vhosts-access-log conf is enabled — probe the default site if
  grepping access.log.
