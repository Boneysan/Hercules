# Seal Cascade - Client Setup Guide

This directory contains notes for preparing the player/DM client for the Seal Cascade campaign on Hercules.

## 1. Quest Journal (Required for @dm warps and campaign text)

The campaign uses custom quest IDs 20000–20234.

**Steps:**
1. Make a full backup of your RO client.
2. Locate `System/OngoingQuestInfoList_True_EN.lub` (or your language equivalent).
3. Decompile the .lub to .lua (common tools: unluac, lub decompilers, or online RO tools).
4. Use the merge helper from the server repo:

   ```bash
   # From the Hercules_RO root
   python3 tools/campaign_quest_merge.py --patch /path/to/decompiled_OngoingQuestInfoList_True_EN.lua
   ```

   Or manually copy blocks from `planning/SealCascade_QuestList_addon.lua`.

5. Recompile the .lua back to .lub.
6. Test: Log in (with DM mode or a character that has the quests) and open the Quest window. You should see entries like "Omens at the Fountain", "The Choice He Never Had", etc., with Location, Hunt, Return lines containing `@dm warp` commands.

The journal entries were written to work with the DM's `@dm` commands for easy navigation.

## 2. BGM and Scene Assets (for @dm scene and @dm cutscene)

See `planning/campaign_client_assets.md` in the repo root.

Required (place in your client):

- **BGM/** folder:
  - dm_dread.mp3, dm_boss.mp3, dm_calm.mp3, dm_holy.mp3, dm_ruin.mp3, dm_snow.mp3, dm_fest.mp3
  - (You can start with renamed copies of existing RO bgm and rename as needed for testing.)

- **data/texture/유저인터페이스/illust/** (or equivalent):
  - Custom cutin portraits (.bmp with magenta transparency) referenced by the DM in scenes.

Without these, scene commands will still change weather/effects but BGM and portraits will be missing or silent.

## 3. LAN / Multi-PC Setup

On the **server** machine:
```bash
cd /path/to/Hercules_RO
./tools/set-lan-ip.sh lan          # or specify IP
```

On **every player machine**:
- Edit `clientinfo.xml` (or `data/clientinfo.xml` / sclientinfo.xml).
- Change `<address>127.0.0.1</address>` (or whatever) to the LAN IP of the server machine.

Restart clients after changes.

To go back to single-PC:
```bash
./tools/set-lan-ip.sh local
```

## 4. Other Client Recommendations

- Make sure your client supports the quest IDs (most modern kRO / iRO clients do; 20000+ range is safe).
- Use a client with good support for questinfo markers (yellow arrows on minimap for hunts).
- For full experience, the GM/DM account should be promoted to group 5 (see `tools/promote-dm.sh` on server).
- Test `@roll`, `@dm status`, `@dm warp`, and `@dmbeat` after connecting.

## 5. Cash Shop (DM rewards)

The DM can grant Cash Shop currency to the whole party with `@dm points <amount>` (Kafra Points, spent first) or `@dm points <amount> cash` (Cash Points, used only as backup when Kafra Points run short).

**Important client quirk:** the in-game Cash Shop window has a "Use Free Points" box that does **not** auto-fill. You must click into it and manually type the item's price (or however much of your Kafra Points balance you want to spend) before clicking Buy — otherwise it sends 0 and you'll get a "You do not have enough Kafra Credit Points" error even with plenty of points. Cash Points cover whatever the Free Points box doesn't.

## 6. Quick Test After Merge

1. Connect with a test character in a party.
2. Have the DM run:
   ```
   @dmmode on
   @dm quest start 20001
   @dm warp prontera 156 191
   ```
3. Open Quest window (Alt+U or equivalent) — you should see "Omens at the Fountain" with nice flavor and warp instructions.

## Troubleshooting

- Quests not appearing? Wrong .lub used, or not recompiled, or wrong language file (try _True_EN or your locale).
- No @dm commands? You must be in the active DM party + group level high enough.
- Warps not working? Make sure you are in the correct DM session and the maps exist on the server.
- Cash Shop says you don't have enough Kafra Credit Points? Type the price into the "Use Free Points" box first — see section 5.

See `planning/dm-handoff.md` and `planning/dm-tooling.md` in the server repo for full command reference.
