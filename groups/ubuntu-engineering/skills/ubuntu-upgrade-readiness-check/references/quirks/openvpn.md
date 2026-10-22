# openvpn — assessment quirks & gotchas

One file per package, extended on every assessment of openvpn. Attribute
each section to the run that found it.

## 2026-10 upgrade-readiness run (noble→resolute→stonking, 2.6.19→2.7.0→2.7.7)

### Harness / fixture gotchas (verified on containers)

- Static-key (`secret`) configs must pin `cipher` to a **CBC** cipher
  (`AES-256-CBC`): GCM/AEAD ciphers are unsupported in secret mode (no TLS
  packet-id) — openvpn exits `Cipher 'AES-256-GCM' mode not supported`.
  With NO cipher set, 2.7 falls back to the legacy BF-CBC default and exits
  `Cipher BF-CBC not supported` (OpenSSL ≥ 3/4 has no BF-CBC).
- A static-key CLIENT config must NOT use `client` (it implies `tls-client`
  and conflicts with `secret`): `Options error: specify only one of
  --tls-server, --tls-client, or --secret`. Plain `remote`+`ifconfig`+`secret`.
- net30-era server fixtures with manual `ifconfig` + `ifconfig-pool` need an
  explicit server-side `route <pool-net>` — the pool clients are not on the
  server's point-to-point /30, so without it the server replies via the
  DEFAULT route and the reverse data path never returns through the tunnel.
- `--status` file format differs by version: 2.7 writes the "CLIENT
  LIST/ROUTING TABLE/GLOBAL STATS" table (no `OpenVPN STATISTICS` header
  line that 2.6-era format had). Probe with
  `grep -qE "GLOBAL STATS|OpenVPN STATISTICS"`.
- LXD-specific: in an **unprivileged** container, openvpn 2.7 DCO (kernel
  `ovpn` module via generic netlink) fails peer-stats queries with
  `dco_get_peer: netlink reports error (-28): Operation not permitted`,
  producing an endless soft session-restart loop (`SIGUSR1[soft,dco peer
  stats error]`) — tunnels flap every ~11 s. Workaround: `disable-dco` in the
  instance config (2.7) — 2.6 (noble) is unaffected (old ovpn-dco API absent
  → userspace). Do NOT try `security.privileged=true` to work around: the
  openvpn@ systemd units use Protect*/PrivateTmp and die with
  `status=226/NAMESPACE` in privileged LXD containers.
- Cross-container tunnel liveness probes need a settle window (route/ARP
  propagation after instance restart); probe with retries, not a single
  ping.
- Package ships `/usr/lib/tmpfiles.d/openvpn.conf`; `/run/openvpn` is
  recreated at boot — instance units don't need RuntimeDirectory handling.

### Assessment findings (the upgrade story)
- **noble→resolute (2.6.19→2.7.0) breaks legacy configs, zero notification**:
  * `secret` (static-key) instances REFUSE TO START on 2.7.0 ("Options
    error: DEPRECATION: No tls-client or tls-server option in configuration
    detected ... use --allow-deprecated-insecure-static-crypto") — configs
    carried from 2.6 lack the flag; units crash-loop (Restart=on-failure).
  * net30-era servers (manual `ifconfig a b` + `ifconfig-pool`, `topology`
    unset) die programming the tun: `OpenVPN ROUTE: ... failed to
    parse/resolve route`, `net_addr_v4_add: x.x.x.x/-1` → rtnl -22 →
    `Linux can't add IP to interface` → fatal exit. Remediation: explicit
    `topology net30` (upstream's own documented fix).
  * Release notes mention openvpn NOWHERE (26.04 LTS summary, 26.04/26.10
    changes pages — grep 0), upgrader has no quirks hook, and resolute /
    stonking ship no /usr/share/doc/openvpn/NEWS* (only upstream
    Changes.rst.gz). → release-notes gap.
- **resolute→stonking (2.7.0→2.7.7) is clean**: configs written for 2.7
  (flag + explicit topology) need no changes; TLS-mode interop passes in
  both mixed-version staggers. All exposure is concentrated at the
  2.6→2.7 hop.
- 26.10 (stonking) was NOT yet in the normal meta-release channel at
  2026-10-20 — `do-release-upgrade` on resolute says "No new release found"
  until Prompt=normal + `-d`. Expect the driver's gate-abort (exit 3) while
  the series is unreleased; the container is untouched, re-run in devel mode.
- The upgrader itself does nothing openvpn-specific on any hop: no
  removals/demotions/conffile-move lines; local conffile mods
  (/etc/default/openvpn, /etc/openvpn/update-resolv-conf) survive every hop.