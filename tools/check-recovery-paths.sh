#!/usr/bin/env bash
# Static contract for QW-072 server/client recovery HUD wiring.

set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
client_repo="${KORANGAR_DIR:-$repo/../korangar}"

require() {
    local pattern="$1" file="$2" message="$3"
    if ! rg -q "$pattern" "$file"; then
        echo "FAIL - $message"
        exit 1
    fi
}

require 'status_apply_sitting_recovery' "$repo/src/map/combat_state.h" 'sitting recovery helper is missing.'
require 'status_apply_respawn_fill' "$repo/src/map/combat_state.h" 'respawn recovery helper is missing.'
require 'campaign_respawn_percent' "$repo/src/map/battle.c" 'respawn percentage is not configurable.'
require 'campaign_respawn_fill_ms' "$repo/src/map/battle.c" 'respawn fill duration is not configurable.'
require 'status_apply_sitting_recovery' "$repo/src/map/status.c" 'sitting recovery is not used by the natural-heal path.'
require 'status_apply_respawn_fill' "$repo/src/map/status.c" 'respawn recovery is not used by the natural-heal path.'
require 'status_recovery_ui_state' "$repo/src/map/status.c" 'recovery UI state is not derived server-side.'
require 'recovery_state' "$repo/src/map/clif.c" 'recovery state is not sent by the map server.'
require 'ZC_RECOVERY_STATE' "$repo/src/common/packets_len.h" 'recovery packet contract is missing.'

if [ ! -d "$client_repo/.git" ]; then
    echo "FAIL - Korangar checkout not found; set KORANGAR_DIR."
    exit 2
fi
require 'RecoveryState' "$client_repo/korangar-networking/src/event.rs" 'client recovery event is missing.'
require 'NetworkEvent::RecoveryState' "$client_repo/korangar-networking/src/packet_versions/version_20220406.rs" 'client packet handler is missing.'
require 'NetworkEvent::RecoveryState' "$client_repo/korangar/src/lib.rs" 'client state handler is missing.'
require 'recovery_status' "$client_repo/korangar/src/interface/windows/hud.rs" 'recovery status is not visible in the HUD.'

echo "OK - sitting/respawn recovery and recovery HUD paths are wired."
