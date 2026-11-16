# rabbitmq-server — CLI/config/packaging quirks for upgrade-readiness testing

Findings from the 2026-10-16 assessment (noble 3.12.1 → resolute 4.0.5 →
stonking 4.3.2; extend, don't fork).

## Version topology (decides what "the upgrade" even means)

- noble 3.12.1 / resolute 4.0.5 / stonking 4.3.2; questing (25.10) has NO
  rabbitmq-server at all. Erlang 25 → 27 → 29 alongside.
- The noble→resolute hop is gated by DistUpgradeQuirks
  (_test_and_fail_rabbitmq_server_installed_and_not_upgradable): requires
  {stream_filtering, stream_update_config_command, restart_streams,
  stream_sac_coordinator_unblock_group} (+ 3 mqtt flags if any is known)
  enabled. stream_filtering + stream_update_config_command DO NOT EXIST on
  3.12.1 (and the mqtt trio is likewise absent from 3.12.1's registry, so
  has_mqtt stays False) → the gate can never pass on stock noble; the
  official path is the
  ppa:canonical-server/rabbitmq-3.13-noble stepping stone + enable_feature_flag
  all (Server Gazette Issue 12, discourse 77271). Gate aborts are FAST (~25s)
  and leave the system untouched — safe to probe repeatedly.
- The stonking upgrader carries the SAME hook but guards
  `toDist != "resolute"` → it is a NO-OP for resolute→stonking: no gate, no
  notice (main.log mentions rabbitmq only in DEBUG package lists). No 4.x
  stepping-stone PPAs exist. Empirically 4.0.5→4.3.2 (offline, single node)
  boots and preserves state, but silently runs a one-way Mnesia→Khepri
  metadata migration (20 tables) on first 4.3.2 boot, and leaves the
  rabbitmq_4.3.0 feature flag DISABLED (fresh installs have it enabled).

## CLI gotchas that bite the harness

- `rabbitmqctl --formatter json list_feature_flags` has NO stability field
  (name + state only) — you cannot select "stable flags" via the CLI; match
  named flags instead (e.g. the upgrader's gate set).
- AMQP 0-8 probe: 3.x replies to a 0-8 protocol header with a bare
  connection.start frame (method frame at offset 0, no 8-byte header);
  4.x replies `AMQP\x03\x01\x00\x00` then RSTs. A naive "reply startswith
  AMQP" assertion false-PASSes on 4.x (header/RST race) and the correct
  discriminator is "a connection.start (frame type 1) ever arrives".
- `rabbitmqctl set_policy` with ha-mode keys on 4.x fails with
  "Error: Validation failed ... are not recognised policy settings" — but
  PIPING set_policy through `tee` masks the failure exit code (pipeline
  status is tee's). Redirect, don't pipe, when branching on it.
- Policy removal is `rabbitmqctl clear_policy` (there is no delete_policy);
  `rabbitmqctl delete_queue <name>` exists.
- `rabbitmqadmin-ng` (universe, stonking) restores the SAME
  /usr/bin/rabbitmqadmin path — old runbooks keep working after apt install.
- In LXD containers RabbitMQ (Debian package) logs to
  /var/log/rabbitmq/<node>.log, not the journal — `journalctl -u
  rabbitmq-server` shows almost nothing; grep the files.

## State/flag facts measured (2026-10-16 run)

- CMQ ha-mode policy created on 3.12 SURVIVES the 4.0 upgrade as inert
  stored metadata (still listed, still attached to the queue, no boot
  error) — classic queues simply stop mirroring. No error anywhere.
- enable_feature_flag all: enables every stable flag, leaves khepri_db
  disabled on 3.13/4.0; on 4.3 khepri_db is stable and gets enabled — on an
  upgraded node that triggers the Mnesia→Khepri migration at the NEXT boot
  with the "expect decrease in performance" notice.
- Feature-flag one-wayness: after resolute→stonking the node has khepri_db
  enabled but rabbitmq_4.3.0 disabled; a fresh 4.3.2 node has both enabled.
- A fresh 4.0.5 node leaves detailed_queues_endpoint disabled — fresh
  installs are NOT "all stable flags enabled" either; do not assume.
- do-release-upgrade source handling: add-apt-repository on noble writes a
  deb822 .sources with the key INLINE; the upgrader disables it with
  `Enabled: no` — but the gazette's documented cleanup (rm .list + .gpg)
  matches neither the filename nor the key location.

## Suite design notes

- Durable-message preservation test: the suite's basic_get consumes one
  message per run — publish a batch (10) at setup and assert count >= 1 plus
  the marker body; the counter's slow decline is suite consumption, not loss.
- pgrep -f inside `lxc exec -- bash -c '...pgrep -f PATTERN...'` matches its
  own shell command line — check status files instead of process tables.
