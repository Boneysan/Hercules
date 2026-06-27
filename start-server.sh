#!/bin/bash
# start-server.sh — start or stop the Hercules RO server stack.
#
# Usage:
#   ./start-server.sh          Start all three servers (login, char, map)
#   ./start-server.sh stop     Kill all three servers

cd "$(dirname "$0")"

if [ "$1" = "stop" ]; then
    echo "[stop] Stopping login-server..."
    pkill -f "./login-server" 2>/dev/null && echo "  login-server stopped." || echo "  login-server was not running."
    echo "[stop] Stopping char-server..."
    pkill -f "./char-server"  2>/dev/null && echo "  char-server stopped."  || echo "  char-server was not running."
    echo "[stop] Stopping map-server..."
    pkill -f "./map-server"   2>/dev/null && echo "  map-server stopped."   || echo "  map-server was not running."
    exit 0
fi

# Kill any leftover processes from a previous run.
pkill -f "./login-server" 2>/dev/null
pkill -f "./char-server"  2>/dev/null
pkill -f "./map-server"   2>/dev/null
sleep 1

echo "[start] Starting login-server..."
./login-server > log/run-login.out 2>&1 &
LOGIN_PID=$!
sleep 3

echo "[start] Starting char-server..."
./char-server > log/run-char.out 2>&1 &
CHAR_PID=$!
sleep 3

echo "[start] Starting map-server..."
./map-server > log/run-map.out 2>&1 &
MAP_PID=$!

echo "[start] All servers started."
echo "  login-server PID: $LOGIN_PID  (log: log/run-login.out)"
echo "  char-server  PID: $CHAR_PID   (log: log/run-char.out)"
echo "  map-server   PID: $MAP_PID    (log: log/run-map.out)"
echo ""
echo "Run './start-server.sh stop' to shut everything down."
