#!/bin/bash
# campaign-preflight.sh
#
# One-command server-side preflight for Seal Cascade DM campaign sessions.
# Run this before every game night (after code changes or on a fresh server).

set -e

cd "$(dirname "$0")/.."

echo "==============================================="
echo " Seal Cascade DM Campaign - Server Preflight"
echo "==============================================="
echo

echo ">>> 0. Campaign database backup"
if ./tools/backup-campaign.sh pre_session; then
    :
else
    echo "  [WARN] Backup failed - is MariaDB running? Do NOT start a session without a backup."
fi
echo

echo ">>> 1. Parse / load validation (all scripts + DB)"
./tools/check-campaign.sh
echo

echo ">>> 2. Script-checker on DM campaign files (if available)"
if command -v ./script-checker >/dev/null 2>&1; then
    bash ./script-checker $(find npc/custom/dm_campaign -name '*.txt' | sort) 2>&1 | tail -5 || true
else
    echo "(script-checker not in PATH or not executable - skipping detailed check)"
fi
echo

echo ">>> 3. LAN / client IP status"
if [ -f conf/char/char-server.conf ]; then
    grep -E 'char_ip|map_ip' conf/char/char-server.conf conf/map/map-server.conf 2>/dev/null | cat || true
else
    echo "No conf files found yet."
fi
echo

echo ">>> 4. DM tooling files present"
for f in \
    npc/custom/dm_campaign/shared/dm_console.txt \
    npc/custom/dm_campaign/shared/dm_beats.txt \
    npc/custom/dm_campaign/shared/dm_symptoms.txt \
    planning/SealCascade_QuestList_addon.lua \
    planning/campaign_quest_journal_entries.lua
do
    if [ -f "$f" ]; then
        echo "  [OK] $f"
    else
        echo "  [MISSING] $f"
    fi
done
echo

echo ">>> 5. Recommended next manual steps (if not already done)"
cat << 'EOM'
  - Create DM + player accounts:
      ./tools/create-account.sh dmuser secretpass M
      ./tools/promote-dm.sh dmuser

  - For LAN play:
      ./tools/set-lan-ip.sh lan

  - On clients: update clientinfo.xml to server LAN IP + install the merged quest lub + BGM/cutins.

  - Full test:
      ./map-server --run-once   (already covered above)
EOM

echo
echo "Preflight finished. Review output above before starting the server."
echo "See planning/dm-handoff.md for the complete pre-session and playtest checklist."
echo "==============================================="
