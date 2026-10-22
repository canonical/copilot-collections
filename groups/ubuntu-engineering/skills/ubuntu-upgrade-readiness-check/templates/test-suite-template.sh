#!/bin/bash
# TEMPLATE — not runnable as-is: replace all <...> placeholders (package
# name, test commands, roles) with package-specific values first.
# Generic per-package functional test suite for upgrade-path testing.
# Run as: <pkg>-test.sh [role] <phase-label>
#   - "role" is only needed when the package has multiple deployment roles
#     (e.g. server vs. client); drop the case block entirely otherwise.
# Emits PASS:/FAIL: lines to /root/<pkg>-test-results.txt; the header records
# installed versions of the package under test. Keep tests hermetic: fixed
# credentials/key material created during setup, dedicated env (credential
# caches, temp dirs), each test self-contained. Route every probe's output
# to the suite's own detail channel — a probe that redirects its internals
# to per-probe log files returns an EMPTY FAIL detail and costs a manual
# re-run to see the error.
if [ $# -eq 2 ]; then ROLE=$1; PHASE=$2; else ROLE=default; PHASE=${1:-unlabeled}; fi
PKG=<pkg>                      # package name prefix, e.g. krb5
LOG=/root/${PKG}-test-results.txt
DETAIL=/root/${PKG}-test-detail.log
: > $LOG
# Export the shared vars: tests re-invoke helper functions via `bash -c`,
# which does NOT inherit non-exported shell variables.
export PKG LOG DETAIL

try() {  # try <name> <cmd...>
  local name=$1; shift
  if "$@" > $DETAIL 2>&1; then
    echo "PASS: $name" >> $LOG
  else
    echo "FAIL: $name" >> $LOG
    echo "----- $name detail -----" >> $LOG
    head -20 $DETAIL >> $LOG
    echo "-------------------------" >> $LOG
  fi
}

echo "### phase: $PHASE   role: $ROLE   date: $(date -u +%FT%TZ)" >> $LOG
echo "### packages:" >> $LOG
# Status-Abbrev filter: a bare glob also lists uninstalled known names with
# EMPTY version fields, which garbles the header.
dpkg-query -W -f='${db:Status-Abbrev} ${Package} ${Version}\n' "${PKG}*" 2>/dev/null | grep '^ii ' | sort >> $LOG
echo >> $LOG

# Give every test an isolated environment the package won't share with the
# previous test (credential cache, config override, temp dir):
export <PKG>_STATE_DIR=/tmp/${PKG}-test-state
mkdir -p ${PKG}_STATE_DIR 2>/dev/null

# --- modern/default-config tests ---------------------------------------
# With a single deployment role, put all tests here and delete the case
# statement. With multiple roles, split by role:
case "$ROLE" in
server)
  try "service-active"          systemctl is-active --quiet <service>
  try "connect-basic"           bash -c "<basic client operation against the service>"
  try "auth-default"            bash -c "<default-config auth/query, e.g. password login>"
  try "admin-op"                bash -c "<admin operation via the network protocol>"
  try "state-store-readable"    bash -c "<read the on-disk database/state directly>"
  ;;
client)
  try "connect-remote"          bash -c "<operation against the remote server container>"
  try "auth-remote"             bash -c "<credential-based operation against remote>"
  try "key-based"               bash -c "<unattended/key material based operation>"
  ;;
esac

# --- deliberately-legacy tests (from your delta analysis) ---------------
# One test per deprecated feature the delta list flagged. These are the ones
# expected to flip PASS->FAIL across an upgrade, and they need BOTH a
# workaround variant (explicit config re-enabling the old behavior) and a
# proper-fix variant to run after remediation is demonstrated.
try "legacy-feature-default-config"   bash -c "<operation using legacy feature with stock config>"
try "legacy-feature-explicit-config"  bash -c "<same operation with explicit config override>"

# --- state preservation (run after upgrades) ----------------------------
try "conffile-preserved"        grep -q "<marker only your custom config has>" /etc/<pkg>/<conffile>
try "state-files-present"       test -s /etc/<pkg>/<key-or-state-file>

# Clean up package-specific state the tests created:
# <package-specific cleanup, e.g. destroy credential caches, stop test daemons>

echo "DONE phase=$PHASE" >> $LOG
cat $LOG
