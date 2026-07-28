#!/bin/sh
# dev.sh — build/run helper for this fork's Hercules tree.
#
# Exists to kill two traps that have each cost a session:
#   1. `make map` is NOT a target here (only `map_sql`), and it fails with
#      "No rule to make target" — a message containing no "error", so it slips
#      through a grepped build log and you test a stale binary. `build` checks
#      the binary's mtime, not the build log.
#   2. Server stdout used to be appended to one log, so `head`/early `tail`
#      showed stale shutdown errors from previous runs. `start` opens a fresh
#      timestamped log every time.
#
# Usage: ./dev.sh { build | start | wait | stop | restart | log }

set -e

cd "$(dirname "$0")"

M_SRV=map-server
LOG_DIR=log
LATEST=$LOG_DIR/server-latest.log
# The map-server prints this only after all maps are loaded — the real
# readiness marker. "loaded 'N' maps" comes earlier and is not sufficient.
READY_MARKER="listening on port '5121'"
WAIT_TIMEOUT=${WAIT_TIMEOUT:-900}

# stat is not portable: BSD/macOS wants -f %m, GNU/WSL wants -c %Y.
mtime() {
	stat -f %m "$1" 2>/dev/null || stat -c %Y "$1" 2>/dev/null || echo 0
}

case $1 in
'build')
	before=$(mtime $M_SRV)
	# `map_sql`, never `map` — see the header.
	make map_sql || {
		echo "!! make map_sql FAILED (exit $?)" >&2
		exit 1
	}
	after=$(mtime $M_SRV)
	# An unchanged mtime is only a problem if a source file is newer than the
	# binary — otherwise there was genuinely nothing to do, and crying wolf
	# every no-op build would train us to ignore this check.
	stale=$(find src -name '*.[ch]' -newer $M_SRV 2>/dev/null | head -1)
	if [ "$before" = "$after" ] && [ -n "$stale" ]; then
		echo "" >&2
		echo "!! BUILD PRODUCED NOTHING — $M_SRV was not relinked," >&2
		echo "!! yet $stale is newer than it. The binary is STALE." >&2
		echo "!! Do not conclude a source change 'does not work'." >&2
		exit 1
	fi
	if [ "$before" = "$after" ]; then
		echo "OK: nothing to rebuild; $M_SRV is up to date."
	else
		echo "OK: $M_SRV relinked -> $(ls -la $M_SRV)"
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

'log')
	[ -e "$LATEST" ] || { echo "No log yet." >&2; exit 1; }
	tail -${2:-40} "$LATEST"
	;;

*)
	echo "Usage: ./dev.sh { build | start | wait | stop | restart | log [n] }"
	echo ""
	echo "  build    make map_sql, then FAIL LOUDLY if map-server was not relinked"
	echo "  start    fresh timestamped log (never appended), returns immediately"
	echo "  wait     block until the map-server is actually ready"
	echo "  log [n]  tail the current run's log (default 40 lines)"
	;;
esac
