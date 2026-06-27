#!/bin/bash
# check-campaign.sh — verify the DM campaign scripts load without errors.
#
# Usage: ./tools/check-campaign.sh
#
# Boots the map-server with --run-once (loads every configured NPC/script,
# then exits) and fails if the loader reported any script errors. This is a
# superset of the old ad-hoc checks: it catches undefined event labels,
# over-long NPC names, case-typo'd constants, and any other parse error.
#
# Run this before each session, or after editing anything under
# npc/custom/dm_campaign/. Requires the map-server binary to be built and the
# database to be reachable (same prerequisites as actually running the server).

set -e

cd "$(dirname "$0")/.."

if [ ! -x ./map-server ]; then
    echo "Error: ./map-server not found or not executable. Build the server first (make)."
    exit 1
fi

LOG="$(mktemp)"
trap 'rm -f "$LOG"' EXIT

echo "Loading all scripts via map-server --run-once ..."
timeout 120 ./map-server --run-once 2>&1 | tr '\r' '\n' > "$LOG" || true

# Real script/load errors. Exclude known-benign library chatter.
ERRORS=$(grep -iE '\[Error\]' "$LOG" | grep -ivE 'MYSQL_OPT_RECONNECT' || true)

LOADED=$(grep -c 'dm_campaign' "$LOG" || true)

if [ -n "$ERRORS" ]; then
    echo
    echo "FAIL — script errors detected:"
    echo "$ERRORS"
    exit 1
fi

if ! grep -q "Successfully loaded" "$LOG"; then
    echo
    echo "FAIL — server did not finish loading (DB unreachable, or crashed early)."
    echo "Last lines:"
    tail -n 15 "$LOG"
    exit 1
fi

echo "OK — campaign loaded clean ($LOADED dm_campaign include lines, 0 errors)."
