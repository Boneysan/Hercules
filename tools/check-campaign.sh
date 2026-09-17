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

# Data checks first - they are fast, and they catch the class of defect a
# clean script load cannot see: a contract pointed at a monster that spawns
# nowhere, an item that does not exist, or generated files that have drifted
# from db/dm_hunt_db.json.
echo "Checking hunting-contract data ..."
if ! ./tools/gen-hunts.py --check; then
    echo
    echo "FAIL - hunting contract data is stale or invalid."
    exit 1
fi

echo "Checking hidden-chest manifest parity ..."
if ! ./tools/gen-chests.py --check; then
    echo
    echo "FAIL - hidden chest manifest is stale or invalid."
    exit 1
fi

echo "Checking equipment-eligibility parity ..."
if ! ./tools/gen-equipment-eligibility.py --check; then
    echo
    echo "FAIL - equipment eligibility manifest is stale or invalid."
    exit 1
fi

echo "Checking Act I static rules ..."
if ! python3 ./tools/check-act1.py; then
    echo
    echo "FAIL - Act I static checks."
    exit 1
fi

echo "Checking warp-graph parity ..."
if ! ./tools/gen-warp-graph.py --check; then
    echo
    echo "FAIL - warp graph is stale or invalid."
    exit 1
fi

echo "Checking encumbrance helper parity ..."
if ! ./tools/check-encumbrance-paths.sh; then
	echo
	echo "FAIL - an audited item-delivery path bypasses the shared encumbrance helpers."
	exit 1
fi

echo "Checking recovery path parity ..."
if ! ./tools/check-recovery-paths.sh; then
	echo
	echo "FAIL - sitting/respawn recovery or HUD wiring is incomplete."
	exit 1
fi

echo "Checking durable checkpoint contract ..."
CHECKPOINT_SQL="sql-files/upgrades/2026-09-16--campaign-checkpoint.sql"
CHECKPOINT_SCRIPT="npc/custom/dm_campaign/shared/dm_checkpoint.txt"
CHECKPOINT_EVENTS="npc/custom/dm_campaign/shared/dm_checkpoint_events.txt"
for required in campaign_id schema_version party_id arc_id step carrier_char_id last_actor_char_id; do
	if ! grep -q "\`$required\`" "$CHECKPOINT_SQL"; then
		echo "FAIL - checkpoint SQL is missing $required."
		exit 1
	fi
done
for required_sql in 'CREATE TABLE IF NOT EXISTS' 'PRIMARY KEY (\`campaign_id\`, \`party_id\`)' 'dm_campaign_checkpoint_log' 'dm_campaign_checkpoint_member' 'ENGINE=InnoDB' 'sql_updates' '20260916'; do
	if ! grep -q "$required_sql" "$CHECKPOINT_SQL"; then
		echo "FAIL - checkpoint SQL is missing $required_sql."
		exit 1
	fi
done
for helper in DM_CheckpointCampaign DM_CheckpointRememberParty DM_CheckpointStart DM_CheckpointAdvance DM_CheckpointConsume DM_CheckpointReset DM_CheckpointSyncParty DM_CheckpointPreview DM_CheckpointReconcile DM_CheckpointRecordPartyEvent; do
	if ! grep -q "function[[:space:]]\+script[[:space:]]\+$helper" "$CHECKPOINT_SCRIPT"; then
		echo "FAIL - checkpoint script is missing $helper."
		exit 1
	fi
done
if ! grep -q 'function[[:space:]]\+script[[:space:]]\+DM_CheckpointCampaign' "$CHECKPOINT_SCRIPT" || \
   ! grep -q '`campaign_id`' "$CHECKPOINT_SCRIPT" || \
   ! grep -q 'dm_campaign_checkpoint_log' "$CHECKPOINT_SCRIPT"; then
	echo "FAIL - checkpoint helpers are not namespaced/audited by campaign identity."
	exit 1
fi
if ! grep -q 'DM_CampaignCheckpointEvents' "$CHECKPOINT_EVENTS" || \
   ! grep -q 'dm_campaign/shared/dm_checkpoint_events.txt' npc/scripts_custom.conf; then
	echo "FAIL - checkpoint reconnect/map-load synchronization hook is missing."
	exit 1
fi
if ! grep -q 'DM_CheckpointRecordPartyEvent' "npc/custom/dm_campaign/shared/dm_quests.txt"; then
	echo "FAIL - party flag transitions are not wired to durable checkpoints."
	exit 1
fi
if ! grep -q 'DM_CheckpointConsume' "npc/custom/dm_campaign/shared/dm_quests.txt"; then
	echo "FAIL - item turn-ins are not wired to checkpoint carrier consumption."
	exit 1
fi
if ! grep -q '\[DMJ\].*checkpoint' "$CHECKPOINT_SCRIPT" || \
   ! grep -q '\[DMJ\].*flag' "$CHECKPOINT_SCRIPT"; then
	echo "FAIL - checkpoint/flag DMJ transport echoes are missing."
	exit 1
fi
if ! grep -q 'function[[:space:]]\+script[[:space:]]\+DM_DMJObjective' npc/custom/dm_campaign/shared/dm_dmj.txt || \
   ! grep -q 'function[[:space:]]\+script[[:space:]]\+DM_DMJStoryObjective' npc/custom/dm_campaign/shared/dm_dmj.txt || \
   ! grep -q 'function[[:space:]]\+script[[:space:]]\+DM_DMJEncounterObjective' npc/custom/dm_campaign/shared/dm_dmj.txt || \
   ! grep -q 'dm_campaign/shared/dm_dmj.txt' npc/scripts_custom.conf || \
   ! grep -q 'DM_DMJObjective' npc/custom/dm_campaign/act_01/arc_01_prontera.txt || \
   ! grep -q 'DM_DMJStoryObjective' npc/custom/dm_campaign/act_01/arc_01_prontera.txt; then
	echo "FAIL - typed DM objective DMJ producer is missing."
	exit 1
fi
if ! grep -q 'DM_DMJStoryObjective.*20006' npc/custom/dm_campaign/shared/dm_beats.txt; then
	echo "FAIL - Arc 1 beat shortcut is missing its typed objective producer."
	exit 1
fi
if ! grep -q 'DM_DMJStoryObjective.*20001.*"Explore"' npc/custom/dm_campaign/shared/dm_beats.txt || \
   ! grep -q 'DM_DMJStoryObjective.*20005.*"Interact"' npc/custom/dm_campaign/shared/dm_beats.txt; then
	echo "FAIL - Arc 1 Explore/Interact beat shortcuts are missing typed objective producers."
	exit 1
fi
for objective_kind in '"Talk"' '"Explore"' '"Interact"'; do
	if ! grep -q "$objective_kind" npc/custom/dm_campaign/act_01/arc_01_prontera.txt; then
		echo "FAIL - Arc 1 typed objective producer is missing $objective_kind."
		exit 1
	fi
done
for encounter_quest in 20012 20018 20023 20030; do
	if ! grep -q "DM_DMJEncounterObjective.*$encounter_quest" npc/custom/dm_campaign/shared/dm_session.txt; then
		echo "FAIL - encounter quest $encounter_quest is missing a DMJ producer."
		exit 1
	fi
done
if rg -n 'select\([^\n]*:' npc/custom/dm_campaign/shared/dm_beats.txt npc/custom/dm_campaign/act_04/arc_17_varmundt.txt; then
	echo "FAIL - campaign select labels must not contain ':'; Hercules treats it as a choice separator."
	exit 1
fi
if ! grep -q 'function[[:space:]]\+script[[:space:]]\+DM_DMJReconcile' npc/custom/dm_campaign/shared/dm_dmj.txt || \
   ! grep -q 'DM_DMJReconcile' npc/custom/dm_campaign/shared/dm_checkpoint.txt || \
   ! grep -q '\\"t\\":\\"reconcile' npc/custom/dm_campaign/shared/dm_dmj.txt; then
	echo "FAIL - typed reconciliation DMJ producer/wiring is missing."
	exit 1
fi
echo "OK — durable checkpoint SQL/script contract present."

echo "Checking isolated checkpoint migration/restart ..."
if ! ./tools/check-checkpoint-migration.sh; then
	echo "FAIL - isolated checkpoint migration/restart validation failed."
	exit 1
fi

LOG="$(mktemp)"
trap 'rm -f "$LOG"' EXIT

echo "Loading all scripts via map-server --run-once ..."
if command -v timeout >/dev/null 2>&1; then
	timeout 120 ./map-server --run-once 2>&1 | tr '\r' '\n' > "$LOG" || true
elif command -v gtimeout >/dev/null 2>&1; then
	gtimeout 120 ./map-server --run-once 2>&1 | tr '\r' '\n' > "$LOG" || true
else
	./map-server --run-once 2>&1 | tr '\r' '\n' > "$LOG" || true
fi

# Real script/load errors. Exclude known-benign library chatter.
ERRORS=$(grep -iE '\[Error\]' "$LOG" | grep -ivE 'MYSQL_OPT_RECONNECT' || true)

LOADED=$(grep -c 'dm_campaign' "$LOG" || true)

WALK=$(grep -E 'DM walk:' "$LOG" || true)
if [ -n "$ERRORS" ] || [ -n "$WALK" ]; then
    echo
    echo "FAIL — script errors detected:"
    echo "$ERRORS"
    echo "$WALK"
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
