#!/bin/bash
# Launch the three Hercules servers and stay alive holding them.
cd /home/boneysan/GitHub/Hercules_RO

pkill -f "login-server" 2>/dev/null
pkill -f "char-server" 2>/dev/null
pkill -f "map-server" 2>/dev/null
sleep 1

./login-server > log/run-login.out 2>&1 &
LOGIN_PID=$!
sleep 3
./char-server > log/run-char.out 2>&1 &
CHAR_PID=$!
sleep 3
./map-server > log/run-map.out 2>&1 &
MAP_PID=$!

echo "login=$LOGIN_PID char=$CHAR_PID map=$MAP_PID"
# Block so this wrapper keeps the servers as live children.
wait
