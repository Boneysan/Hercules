#!/bin/sh
# dev.sh — build/run helper for this fork's Hercules tree.
#
# Exists to kill three traps that have each cost a session:
#   1. `make map` is NOT a target here (only `map_sql`), and it fails with
#      "No rule to make target" — a message containing no "error", so it slips
#      through a grepped build log and you test a stale binary. `build` checks
#      each binary's mtime, not the build log.
#   2. Server stdout used to be appended to one log, so `head`/early `tail`
#      showed stale shutdown errors from previous runs. `start` opens a fresh
#      timestamped log every time.
#   3. `build` used to run `make map_sql` ALONE, because this fork's deltas
#      mostly live in src/map. That silently left login/char/api stale and
#      still printed OK. Found 2026-09-02: the 2026-08-18 security remediations
#      touched src/login, src/char and src/api, and the running servers had
#      never contained them — the binaries predated the fix by eleven minutes
#      and nothing said so. `build` now makes all four and checks all four.
#
# Usage: ./dev.sh { build | start | wait | stop | restart | log }

set -e

cd "$(dirname "$0")"

M_SRV=map-server
# server:source-dir. src/common is checked for all four on top of these.
SERVERS="login-server:login char-server:char map-server:map api-server:api"
LOG_DIR=log
LATEST=$LOG_DIR/server-latest.log
# The map-server prints this only after all maps are loaded — the real
# readiness marker. "loaded 'N' maps" comes earlier and is not sufficient.
READY_MARKER="listening on port '5121'"
WAIT_TIMEOUT=${WAIT_TIMEOUT:-900}

SNAP_FILE=${SNAP_FILE:-log/db-snapshot.sql}
SQL_CONF=conf/global/sql_connection.conf

# Read the DB credentials from Hercules' own config rather than duplicating
# them, so a changed password cannot leave this script silently pointed at a
# database it can no longer reach.
sqlval() {
	sed -n "s/^[[:space:]]*$1:[[:space:]]*\"\(.*\)\".*/\1/p" "$SQL_CONF" | head -1
}

# stat is not portable: BSD/macOS wants -f %m, GNU/WSL wants -c %Y.
mtime() {
	stat -f %m "$1" 2>/dev/null || stat -c %Y "$1" 2>/dev/null || echo 0
}

case $1 in
'build')
	# ALL FOUR, not just the map-server — see trap 3 in the header. `sql` is
	# the target that covers login_sql/char_sql/map_sql/api_sql; the bare
	# per-server names without `_sql` do not exist.
	for pair in $SERVERS; do
		srv=${pair%%:*}
		eval "before_$(echo "$srv" | tr - _)=$(mtime "$srv")"
	done

	make sql || {
		echo "!! make sql FAILED (exit $?)" >&2
		exit 1
	}

	rebuilt=0
	failed=0
	for pair in $SERVERS; do
		srv=${pair%%:*}
		dir=${pair##*:}
		var=$(echo "$srv" | tr - _)
		eval "before=\$before_$var"
		after=$(mtime "$srv")

		# An unchanged mtime is only a problem if a source file that server
		# actually compiles is newer than the binary — otherwise there was
		# genuinely nothing to do, and crying wolf on every no-op build would
		# train us to ignore this check. src/common counts for all four.
		stale=$(find "src/$dir" src/common -name '*.[ch]' -newer "$srv" 2>/dev/null | head -1)

		if [ "$before" = "$after" ] && [ -n "$stale" ]; then
			echo "" >&2
			echo "!! BUILD PRODUCED NOTHING — $srv was not relinked," >&2
			echo "!! yet $stale is newer than it. The binary is STALE." >&2
			echo "!! Do not conclude a source change 'does not work'." >&2
			failed=1
		elif [ "$before" != "$after" ]; then
			echo "OK: $srv relinked"
			rebuilt=$((rebuilt + 1))
		fi
	done

	[ "$failed" -eq 0 ] || exit 1

	if [ "$rebuilt" -eq 0 ]; then
		echo "OK: nothing to rebuild; all four servers are up to date."
	else
		echo "OK: $rebuilt of 4 servers relinked."
	fi
	;;

'start')
	if [ -e ".$M_SRV.pid" ] && kill -0 "$(cat ".$M_SRV.pid")" 2>/dev/null; then
		echo "Already running (pid $(cat ".$M_SRV.pid")). Use restart." >&2
		exit 1
	fi
	# Advisory only — the servers report their own DB failures.
	if command -v nc >/dev/null && ! nc -z 127.0.0.1 3306 2>/dev/null; then
		echo "WARNING: nothing listening on 3306. Start MariaDB first with"
		echo "         brew services run mariadb    # 'run', NEVER 'start'"
	fi
	mkdir -p $LOG_DIR
	log=$LOG_DIR/server-$(date +%Y%m%d-%H%M%S).log
	# athena-start backgrounds the four servers and returns immediately;
	# they inherit this redirect, so the log fills as they boot.
	./athena-start start >"$log" 2>&1
	ln -sf "$(basename "$log")" $LATEST
	echo "Started. Fresh log: $log (also $LATEST)"
	echo "Map loading takes several minutes — run './dev.sh wait'."
	;;

'wait')
	[ -e "$LATEST" ] || { echo "No log; run './dev.sh start' first." >&2; exit 1; }
	echo "Waiting up to ${WAIT_TIMEOUT}s for the map-server to be ready..."
	elapsed=0
	while [ "$elapsed" -lt "$WAIT_TIMEOUT" ]; do
		if grep -qF "$READY_MARKER" "$LATEST"; then
			grep -a "loaded '.*' maps" "$LATEST" | tail -1
			echo "READY: map-server listening on 5121 (${elapsed}s)"
			exit 0
		fi
		if [ -e ".$M_SRV.pid" ] && ! kill -0 "$(cat ".$M_SRV.pid")" 2>/dev/null; then
			echo "!! map-server DIED during boot. Tail of $LATEST:" >&2
			tail -20 "$LATEST" >&2
			exit 1
		fi
		sleep 5
		elapsed=$((elapsed + 5))
	done
	echo "!! Timed out after ${WAIT_TIMEOUT}s. Tail of $LATEST:" >&2
	tail -20 "$LATEST" >&2
	exit 1
	;;

'stop')
	./athena-start stop
	echo "Stopped."
	;;

'restart')
	./dev.sh stop || true
	./dev.sh start
	;;

'snapshot')
	# Capture the whole database, not a chosen list of tables. Character state
	# is spread across char/inventory/storage/skill/quest/achievement/party and
	# more, and the failure mode of forgetting one is a restore that looks like
	# it worked.
	mkdir -p "$(dirname $SNAP_FILE)"
	# --single-transaction/--skip-lock-tables: the Hercules DB user has no LOCK
	# TABLES privilege, and without these mysqldump dies with a bare
	# "Access denied ... when using LOCK TABLES".
	# --no-create-info/--skip-add-drop-table: the DB user has no DROP privilege,
	# so a dump containing schema statements cannot be replayed at all —
	# "DROP command denied" on the first table. Data only; the schema is not
	# what a test run damages.
	# Every one of these flags exists because the Hercules DB user lacks a
	# privilege the default dump assumes:
	#   --skip-lock-tables / --single-transaction : no LOCK TABLES
	#   --no-create-info / --skip-add-drop-table  : no DROP
	#   --skip-add-locks                          : LOCK TABLES on replay
	#   --skip-disable-keys                       : no ALTER (DISABLE KEYS)
	# Each was found the hard way: the dump or the replay dies on the first
	# table with a bare "command denied", and a replay that dies *after* the
	# clear step leaves the database empty.
	mysqldump --single-transaction --skip-lock-tables \
		--no-create-info --skip-add-drop-table --complete-insert \
		--skip-add-locks --skip-disable-keys \
		-h"$(sqlval db_hostname)" -u"$(sqlval db_username)" -p"$(sqlval db_password)" \
		"$(sqlval db_database)" > "$SNAP_FILE" || {
		echo "!! mysqldump FAILED (exit $?)" >&2
		exit 1
	}
	# A dump that failed part-way still leaves a plausible-looking file behind,
	# so verify the trailer mysqldump only writes on success.
	if ! tail -5 "$SNAP_FILE" | grep -q "Dump completed"; then
		echo "!! snapshot is incomplete (no 'Dump completed' trailer) — refusing to keep it" >&2
		rm -f "$SNAP_FILE"
		exit 1
	fi
	echo "Snapshot written: $SNAP_FILE ($(wc -l < "$SNAP_FILE") lines)"
	;;

'restore')
	# Undo whatever a test run did to the shared character.
	#
	# The headless suite mutates one character and never resets it, so state
	# accumulates across runs. That is not hypothetical: ammunition granted 100
	# rounds at a time built up until the character was too heavy to pick items
	# up, and four unrelated scenarios began failing far from the cause.
	[ -f "$SNAP_FILE" ] || { echo "!! No snapshot at $SNAP_FILE — run './dev.sh snapshot' first" >&2; exit 1; }

	# Never restore from a half-written dump. A truncated file replays as a
	# partial success: some tables restored, some silently left as they were,
	# and the command still reports "Restored".
	if ! tail -5 "$SNAP_FILE" | grep -q "Dump completed"; then
		echo "!! $SNAP_FILE is incomplete (no 'Dump completed' trailer) — refusing to restore" >&2
		exit 1
	fi

	# REFUSE while anyone is logged in. The map-server holds character state in
	# memory and writes it on logout, so restoring under a live session is
	# silently undone the moment that session ends — the worst kind of failure,
	# because the restore reports success.
	online=$(mysql -h"$(sqlval db_hostname)" -u"$(sqlval db_username)" -p"$(sqlval db_password)" \
		-N -B -e "SELECT COUNT(*) FROM \`char\` WHERE online <> 0;" "$(sqlval db_database)" 2>/dev/null)
	if [ "$online" != "0" ]; then
		echo "!! $online character(s) still online — stop the stack first, or the restore will be overwritten on logout" >&2
		exit 1
	fi

	DB=$(sqlval db_database)
	MYSQL="mysql -h$(sqlval db_hostname) -u$(sqlval db_username) -p$(sqlval db_password)"

	# Clear every table before replaying, discovered from the live schema rather
	# than a hand-kept list — a forgotten table is a restore that reports
	# success and leaves state behind, which is the whole bug class this exists
	# to prevent. DELETE, not TRUNCATE: TRUNCATE needs DROP privilege too.
	tables=$($MYSQL -N -B -e "SELECT table_name FROM information_schema.tables WHERE table_schema='$DB';")
	{
		echo "SET FOREIGN_KEY_CHECKS=0;"
		for t in $tables; do echo "DELETE FROM \`$t\`;"; done
		echo "SET FOREIGN_KEY_CHECKS=1;"
	} | $MYSQL "$DB" || {
		echo "!! clearing tables FAILED (exit $?) — database may be empty, restore immediately" >&2
		exit 1
	}

	$MYSQL "$DB" < "$SNAP_FILE" || {
		echo "!! restore FAILED (exit $?) — tables were cleared first, so the database is now INCOMPLETE" >&2
		exit 1
	}
	echo "Restored from $SNAP_FILE"
	;;

'log')
	[ -e "$LATEST" ] || { echo "No log yet." >&2; exit 1; }
	tail -${2:-40} "$LATEST"
	;;

*)
	echo "Usage: ./dev.sh { build | start | wait | stop | restart | snapshot | restore | log [n] }"
	echo ""
	echo "  build    make sql (all four servers), FAIL LOUDLY on any stale binary"
	echo "  start    fresh timestamped log (never appended), returns immediately"
	echo "  wait     block until the map-server is actually ready"
	echo "  snapshot save the whole DB (character state) to log/db-snapshot.sql"
	echo "  restore  put it back — refuses while any character is still online"
	echo "  log [n]  tail the current run's log (default 40 lines)"
	;;
esac
