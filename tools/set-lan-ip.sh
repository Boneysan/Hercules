#!/bin/bash
# set-lan-ip.sh — switch server config between localhost and LAN mode.
#
# LAN mode: sets char_ip / map_ip to your machine's LAN IP so players on
# other machines on the same network can connect.
#
# Localhost mode: resets to 127.0.0.1 for single-machine play.
#
# Usage:
#   ./tools/set-lan-ip.sh lan [IP]   — set LAN IP (auto-detected if omitted)
#   ./tools/set-lan-ip.sh local      — reset to 127.0.0.1

set -e

CHAR_CONF="conf/char/char-server.conf"
MAP_CONF="conf/map/map-server.conf"

MODE="$1"
MANUAL_IP="$2"

usage() {
    echo "Usage: $0 lan [ip-address]   — enable LAN mode (auto-detect IP or use given)"
    echo "       $0 local              — reset to localhost (127.0.0.1)"
}

if [ -z "$MODE" ]; then
    usage; exit 1
fi

if [ "$MODE" = "local" ]; then
    TARGET_IP="127.0.0.1"
elif [ "$MODE" = "lan" ]; then
    if [ -n "$MANUAL_IP" ]; then
        TARGET_IP="$MANUAL_IP"
    else
        # Try to auto-detect the primary LAN IP (skip loopback and docker).
        TARGET_IP=$(ip route get 8.8.8.8 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="src") print $(i+1)}' | head -1)
        if [ -z "$TARGET_IP" ]; then
            echo "Could not auto-detect LAN IP. Run: ./tools/set-lan-ip.sh lan <your-ip>"
            exit 1
        fi
    fi
else
    usage; exit 1
fi

# Update char_ip in char-server.conf (client-facing, line ~72).
sed -i "s|char_ip: \"[0-9.]*\"|char_ip: \"$TARGET_IP\"|g" "$CHAR_CONF"

# Update map_ip in map-server.conf (client-facing, line ~76).
sed -i "s|map_ip: \"[0-9.]*\"|map_ip: \"$TARGET_IP\"|g" "$MAP_CONF"

echo "Set client-facing IPs to: $TARGET_IP"
echo "  $CHAR_CONF  → char_ip"
echo "  $MAP_CONF   → map_ip"
echo ""
if [ "$MODE" = "lan" ]; then
    echo "Players should set their clientinfo.xml login server to: $TARGET_IP"
    echo "Restart the server for changes to take effect."
else
    echo "Reverted to localhost. Only connections from this machine will work."
    echo "Restart the server for changes to take effect."
fi
