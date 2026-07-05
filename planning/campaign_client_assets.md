# Seal Cascade - Client Assets Needed

From dm-live-table.md and vault:

## @dm scene BGM (distribute .mp3 to players in client BGM/ folder)
- dread: dm_dread.mp3 (fog / dread atmosphere)
- boss: dm_boss.mp3 (clouds2 / boss tension)
- calm: dm_calm.mp3 (none / safe hub)
- holy: dm_holy.mp3 (sakura / Rachel temple)
- ruin: dm_ruin.mp3 (fog / Glast/ ruins)
- snow: dm_snow.mp3 (snow / Payon or Niflheim)
- fest: dm_fest.mp3 (fireworks / Prontera events)

**How to prepare:** Start with existing RO BGM files (e.g. 001.mp3 renamed), or source royalty-free / compose custom. Place exactly named in client's BGM dir. @dm scene <preset> will play the matching track for the party.

## Cutin portraits (data\texture\유저인터페이스\illust\*.bmp, magenta transparent)
- Used in @dm scene <preset> <portrait> and @dm cutscene.
- Presets reference custom illustrations (e.g. Rina, Bijou/Maret, Pratt, Voss, Cassell, Loki, etc.).
- Create or extract from vault assets. Use 8-bit bmp with pure magenta (255,0,255) as transparent key. Test with @dm cutscene on 60s or @dm scene.

## Quest Journal
- **Easiest**: Use `planning/SealCascade_QuestList_addon.lua` (minimal, self-documented merge instructions in the header).
- Source of truth: `planning/campaign_quest_journal_entries.lua`.
- Merge process (see also dm-handoff.md "Client quest journal"):
  1. Backup your client's `System/OngoingQuestInfoList_True_EN.lub`.
  2. Decompile .lub → .lua.
  3. Insert/replace the 20000-20234 QuestList entries (append after the existing `QuestList = QuestList or {}` block is usually safe).
  4. Recompile .lua → .lub.
  5. Test that the new quests appear in the client's Quest window for IDs in that range.
- The addon uses ^3355FF color codes and copy-pasteable `@dm warp MAP X Y` lines exactly as expected by the DM tooling.

## Other
- Sigil Ring (item 50001 placeholder + flag dm_arc01_sigil_ring_obtained): acts as compass in later arcs (e.g. Arc 6 Yuno reactions, Arc 8 flavor). Scripts check countitem or flag.
- Handouts (3 in vault/Handouts/): currently Discord preferred per plan; can implement as readable books if desired.
- After lub merge: distribute the patched OngoingQuestInfoList_True_EN.lub (and any GRF) to all players for journal to show campaign text and @dm warps.

Run client with these for full @dm scene / journal experience.

See also vault for any additional custom maps or items.
