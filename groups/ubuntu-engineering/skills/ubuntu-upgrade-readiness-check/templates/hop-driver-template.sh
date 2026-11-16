#!/bin/bash
# TEMPLATE — not runnable as-is: replace all <...> placeholders (container
# name, target codename, hop timeout) with run-specific values first.
#
# Host-side driver for ONE do-release-upgrade hop on ONE container.
#   Usage: hop-driver-template.sh <container> <lts|normal|devel> <target-codename> <per-hop-log-dir>
#     <container>         LXD container name
#     <lts|normal|devel> lts   : the hop's target series is a released LTS
#                                (default Prompt=lts, plain do-release-upgrade)
#                        normal: the hop's target series is a RELEASED interim
#                                series (Prompt=normal, NO -d)
#                        devel : the hop's target series is UNRELEASED
#                                (Prompt=normal + `do-release-upgrade -d`)
#     <target-codename>   VERSION_CODENAME the container must land on
#     <per-hop-log-dir>   DIRECTORY (created if missing) that receives this
#                         hop's dist-upgrade logs — one dir per hop per
#                         container; pulled BEFORE any later hop starts.
#   Exit codes: 0 = landed on target; 2 = timeout; 3 = the upgrader exited
#   without landing (typically a PRE-FLIGHT GATE ABORT: a quirk refused the
#   upgrade before any change). On 3, apply the remediation the gate message
#   prescribes and re-run this driver from the top — the aborted attempt
#   leaves the container untouched.
#
# Run ONE instance per hop. Hops on the SAME container run sequentially
# (never start hop N+1 before hop N exits); independent containers run in
# parallel.
#
# Design constraints (do not weaken when adapting):
#   * the upgrader runs DETACHED inside the container (setsid + nohup), so
#     a supervisor timeout on this host-side script can never kill it
#     mid-dpkg;
#   * this script only POLLS: never restart a container mid-dpkg, never
#     launch a second upgrader against a container that may still be
#     upgrading;
#   * /var/log/dist-upgrade logs are OVERWRITTEN by the next hop — pull
#     them into <per-hop-log-dir> before returning.
set -u
C=${1:?container}; MODE=${2:?lts|devel}; TARGET=${3:?target codename}; LOGDIR=${4:?per-hop log dir}
mkdir -p "$LOGDIR"
say() { echo "[$(date -u +%T)] $*"; }

say "hop start: $C mode=$MODE target=$TARGET"

# (1) in-release update + full-upgrade — the upgrader refuses a stale system
if ! lxc exec "$C" -- bash -ec 'export DEBIAN_FRONTEND=noninteractive; apt-get update -qq; apt-get full-upgrade -y' >"$LOGDIR/pre-update.log" 2>&1; then
  say "UPDATE FAILED ($C) — see $LOGDIR/pre-update.log"; exit 1
fi

# (2) reboot-required -> restart BEFORE upgrading; a hop launched against an
#     un-rebooted system is refused and wastes the run
if lxc exec "$C" -- test -e /var/run/reboot-required; then
  say "reboot-required set -> restarting $C"
  lxc restart "$C"
  sleep 20
fi
# Bounded wait: wait only out "initializing"; tolerate "degraded" (routine
# after a container restart). An unbounded `is-system-running -q` loop
# hangs forever on a degraded system — before the upgrader even starts.
deadline=$(( $(date +%s) + 120 ))
while [ "$(lxc exec "$C" -- systemctl is-system-running 2>/dev/null || echo initializing)" = initializing ]; do
  sleep 5
  [ "$(date +%s)" -gt "$deadline" ] && break
done

# (3) Prompt handling + stale meta-release caches
lxc exec "$C" -- bash -ec 'rm -f /var/lib/update-manager/meta-release*; \
  if [ "$1" = devel ] || [ "$1" = normal ]; then sed -i "s/^Prompt=.*/Prompt=normal/" /etc/update-manager/release-upgrades; fi' _ "$MODE"

# (4) launch the release upgrade DETACHED inside the container
DFLAG=""; [ "$MODE" = devel ] && DFLAG="-d"
lxc exec "$C" -- bash -ec "setsid nohup env DEBIAN_FRONTEND=noninteractive \
  do-release-upgrade -f DistUpgradeViewNonInteractive $DFLAG \
  </dev/null >/root/hop-driver.log 2>&1 & echo started"
say "do-release-upgrade launched in $C"

# (5) poll until the container reports the target series AND the in-container
#     upgrader has exited:
#     * match the real process name — after download the in-container upgrader
#       runs as /tmp/ubuntu-release-upgrader-*/<series> --frontend=..., so a
#       pgrep pattern for "do-release-upgrade" alone goes stale mid-upgrade;
#     * count with `pgrep -f <pattern> | wc -l`, NEVER
#       `pgrep -cf <pattern> || echo 0` — pgrep exits 1 on no match, the
#       fallback echoes a second, non-numeric line into the count, and the
#       completion test never succeeds (the loop then spins to its deadline
#       on a container that already landed);
#     * re-check after a short delay so a mid-dpkg transient state cannot
#       read as completion.
upgrader_running() {
  [ "$(lxc exec "$C" -- pgrep -f 'ubuntu-release-upgrader|do-release-upgrade' 2>/dev/null | wc -l)" -gt 0 ]
}
deadline=$(( $(date +%s) + <hop-timeout-seconds, e.g. 3600> ))
while :; do
  sleep 30
  OS=$(lxc exec "$C" -- sh -c '. /etc/os-release; echo $VERSION_CODENAME' 2>/dev/null || echo "?")
  say "$C: os=$OS upgrader=$(lxc exec "$C" -- pgrep -f 'ubuntu-release-upgrader|do-release-upgrade' 2>/dev/null | wc -l)"
  if [ "$OS" = "$TARGET" ] && ! upgrader_running; then
    sleep 20
    upgrader_running || break            # landed
  fi
  # upgrader exited WITHOUT landing = pre-flight gate abort (re-check after a
  # delay so a mid-dpkg transient cannot misread): pull logs, exit 3 — never
  # spin to the deadline on an abort that took 3 minutes.
  if [ "$OS" != "$TARGET" ] && ! upgrader_running; then
    sleep 20
    if ! upgrader_running; then
      lxc exec "$C" -- cat /var/log/dist-upgrade/main.log >"$LOGDIR/hop-main.log" 2>/dev/null || true
      say "GATE ABORT: $C still on $OS, upgrader exited — see $LOGDIR/hop-main.log for the refusal message"
      exit 3
    fi
  fi
  if [ "$(date +%s)" -gt "$deadline" ]; then
    say "TIMEOUT waiting for $C -> $TARGET (upgrader still alive INSIDE the container: inspect there; never kill it host-side)"
    exit 2
  fi
done
say "$C landed on $TARGET"

# (6) pull this hop's logs BEFORE any later hop starts (they are overwritten
#     in place by the next do-release-upgrade)
lxc exec "$C" -- cat /var/log/dist-upgrade/main.log     >"$LOGDIR/hop-main.log"     2>/dev/null || true
lxc exec "$C" -- cat /var/log/dist-upgrade/apt-term.log >"$LOGDIR/hop-apt-term.log" 2>/dev/null || true

# (7) post-landing: there are usually NEW pending updates — repeat the
#     update + restart loop before the next hop
lxc exec "$C" -- bash -ec 'export DEBIAN_FRONTEND=noninteractive; apt-get update -qq; apt-get full-upgrade -y' >"$LOGDIR/post-update.log" 2>&1 || true
if lxc exec "$C" -- test -e /var/run/reboot-required; then lxc restart "$C"; sleep 20; fi

# (8) classify the hop against the skill's step-4 criterion: an ABORT that
#     recovered via the upgrader's built-in dpkg fallback still counts as a
#     COMPLETED hop — the landing is valid and the abort is usually the
#     headline finding of the assessment; record it, do NOT re-run the hop.
if grep -q "A recovery will run now" "$LOGDIR/hop-main.log" 2>/dev/null; then
  say "NOTE: hop $C -> $TARGET completed via dpkg recovery — record the abort as a finding"
fi
say "HOP-DONE $C $TARGET"