#!/usr/bin/env bash
# Validate the QW-054 migration and restart persistence in an isolated MariaDB.
# This never connects to the project's configured ragnarok database.

set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mariadb="$(command -v mariadb || true)"
mariadbd="$(command -v mariadbd || true)"
install_db="$(command -v mariadb-install-db || true)"
admin="$(command -v mariadb-admin || true)"

if [[ -z "$mariadb" || -z "$mariadbd" || -z "$install_db" || -z "$admin" ]]; then
	echo "SKIP - MariaDB client/server tools are unavailable."
	exit 0
fi

tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/qw-checkpoint-db.XXXXXX")"
data_dir="$tmp_dir/data"
socket_path="$tmp_dir/mariadb.sock"
pid_path="$tmp_dir/mariadb.pid"
error_log="$tmp_dir/mariadb.log"

cleanup() {
	"$admin" --no-defaults --socket="$socket_path" -uroot shutdown >/dev/null 2>&1 || true
	rm -rf -- "$tmp_dir"
}
trap cleanup EXIT

mkdir -p "$data_dir"
"$install_db" --no-defaults --auth-root-authentication-method=normal --datadir="$data_dir" >/dev/null

start_db() {
	"$mariadbd" --no-defaults --datadir="$data_dir" --socket="$socket_path" \
		--pid-file="$pid_path" --log-error="$error_log" --skip-networking \
		--user="$(id -un)" >/dev/null 2>&1 &
	for _ in $(seq 1 60); do
		if "$admin" --no-defaults --socket="$socket_path" -uroot ping >/dev/null 2>&1; then
			return 0
		fi
		sleep 0.2
	done
	echo "FAIL - isolated MariaDB did not become ready." >&2
	return 1
}

sql() {
	"$mariadb" --no-defaults --socket="$socket_path" -uroot "$@"
}

start_db
sql -e 'CREATE DATABASE ragnarok; USE ragnarok; CREATE TABLE sql_updates (timestamp INT NOT NULL PRIMARY KEY);'
sql ragnarok < "$repo/sql-files/upgrades/2026-09-16--campaign-checkpoint.sql"
sql ragnarok -e "
INSERT INTO dm_campaign_checkpoint
  (campaign_id, party_id, arc_id, step, carrier_char_id, last_actor_char_id)
  VALUES ('seal_cascade', 42, 1, 3, 9001, 9001);
INSERT INTO dm_campaign_checkpoint_member (campaign_id, char_id, party_id)
  VALUES ('seal_cascade', 7001, 42);
INSERT INTO dm_campaign_checkpoint_log
  (campaign_id, party_id, step, actor_char_id, event)
  VALUES ('seal_cascade', 42, 3, 9001, 'advance');
"
"$admin" --no-defaults --socket="$socket_path" -uroot shutdown
start_db

checkpoint_rows="$(sql -N -B ragnarok -e 'SELECT COUNT(*) FROM dm_campaign_checkpoint;')"
member_rows="$(sql -N -B ragnarok -e 'SELECT COUNT(*) FROM dm_campaign_checkpoint_member;')"
log_rows="$(sql -N -B ragnarok -e 'SELECT COUNT(*) FROM dm_campaign_checkpoint_log;')"
marker_rows="$(sql -N -B ragnarok -e 'SELECT COUNT(*) FROM sql_updates WHERE timestamp = 20260916;')"

if [[ "$checkpoint_rows" != 1 || "$member_rows" != 1 || "$log_rows" != 1 || "$marker_rows" != 1 ]]; then
	echo "FAIL - migration rows did not survive restart (checkpoint=$checkpoint_rows member=$member_rows log=$log_rows marker=$marker_rows)." >&2
	exit 1
fi

echo "OK - isolated checkpoint migration and restart persistence passed."
