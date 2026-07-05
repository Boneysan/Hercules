# Handoff — Port the Vault Quest Rewrites into the Server (Arcs 10–19)

> **Task:** The Obsidian vault's quest rewrites (finished 2026-07-02, see
> `H:\Docs\Obsidian Notes\Game Design\Ragnarok_Online\Campaign\_Handoff_XP_Quest_Rewrites.md`)
> were never ported into the server. Arcs 8 and 9 are ported and validated.
> Work the checklist below **top to bottom, one arc per sitting**; check items
> off in THIS file as you complete them (with a date), so the doc is the work log.
>
> Mirrored in the session task tracker (one task per checklist section).

## How to use this doc

- Each arc section is a self-contained work unit following **THE RECIPE** (below).
- Check off `- [x]` items as they land; add the date to the arc heading when done.
- After each arc: run the validation block and only then check the arc's final box.
- If you discover a gotcha, append it to **Gotchas** at the bottom — don't lose it.

## Background (audit findings, 2026-07-04)

- Vault = 95 quest designs (19 arcs × 5). Server had 88 campaign quests + tracker
  (20000), but arcs 8–19 still carried **old pre-rewrite designs**. Zero rewritten
  titles appeared in `npc/` or `db/` before this port began.
- Arcs 1–7 were already in sync. Arcs 8–9 ported 2026-07-04 (commit 89006fa91).
- Design sources: vault `Campaign/Act_*/Arc_NN_*/Quests/0[1-5]_*.md`
  (01–03 = `#xp-support` repeatables, 04–05 = story; one of them is the climax).

## Shared infrastructure already fixed (do NOT redo)

- `DM_QuestRegistry` is now a real invisible NPC (was `function script` —
  `getvariableofnpc()` can't resolve those and OnInit never ran).
- `dm_console.txt`'s two campaign-quest-ID lists iterate the registry
  (arcs 1–19 + 20000) — new arc IDs are picked up automatically.
- Known data-bug pattern: **old MobId comments lie** (1164=Requiem not Raydric,
  1778=Gazeti not Ice Titan). Verify every MobId against `db/re/mob_db.conf`.

## ID-mapping convention (follow Arc 8/9)

Registry entry order per arc = `[climax/tracker, other story quest, 01, 02, 03]`:

- **First ID = arc tracker** (`DM_ArcTrackerId` = registry entry [0]): started at
  arc start, completed at the MVP-death set-piece. Map to the vault quest typed
  `main (arc climax)` — usually 05, **but Arc 9's climax was 04. Read the docs.**
- Second ID = the other story quest (side/trial).
- Remaining three = xp-support 01–03 (hunt quests with Targets in quest_db).
- 5th-quest ID: arcs 10 → 20145; arcs 11–14 → the skipped x2 slot
  (20152, 20162, 20172, 20182); arcs 15–18 → see their sections.

## THE RECIPE — 9 stops per arc

Exemplars: `act_02/arc_08_glast_heim.txt`, `act_02/arc_09_rachel.txt` (+ their
diffs in commit 89006fa91 show every companion edit).

1. **Vault docs**: read all 5 `Quests/*.md` + arc hub + `NPCs/*.md`.
2. **`db/quest_db.conf`**: rewrite the arc block — names, Targets (verified
   MobIds), keep old Exp/Jexp scale; update the `//=` header comment.
3. **`shared/dm_quests.txt`**: the arc's `setarray .arcNN_id[]` / `.arcNN_nm$[]`.
4. **`shared/dm_flags.txt`**: add new branch-outcome flags to the arc array.
5. **`act_0X/arc_NN_*.txt`**: main rewrite — giver starts tracker + 3 hunts;
   per-quest turn-ins with the vault's Noble/Pragmatic/Dark branches → flags;
   all-3-done → start story quest; climax gate; MVP set-piece completes tracker;
   OnInit `setquestinfo` blocks updated; new scene NPCs welcome (Osric pattern).
6. **`shared/dm_decisions.txt`**: DM_Decide rows that completed a repurposed
   quest ID → `"", ""` (flags only) + fixed log strings.
7. **`shared/dm_beats.txt`**: `DM_BeatArcNN` — quest starts, story-quest beat
   case, warp targets, flag-aware MVP spawn variants where the design calls.
8. **`shared/dm_hunt_markers.txt`**: one marker per hunt quest (map from the
   vault XP-role line; verify map exists).
9. **Docs**: `CAMPAIGN.md` + `planning/dm-tooling.md` arc-table ID ranges.

**Validation block (run after each arc):**
```bash
bash ./script-checker npc/custom/dm_campaign/act_0X/arc_NN_*.txt \
  npc/custom/dm_campaign/shared/{dm_quests,dm_decisions,dm_beats,dm_hunt_markers,dm_flags,dm_console}.txt
# + brace/ID check on the arc's quest_db block (see arc 8/9 python snippet in git log)
```

---

# WORKLIST

## ✅ Arc 8 — Glast Heim (DONE 2026-07-04, commit 89006fa91)
## ✅ Arc 9 — Rachel (DONE 2026-07-04, commit 89006fa91)

## Arc 10 — Lighthalzen (`act_02/arc_10_lighthalzen.txt`, IDs 20141–20145)

Target mapping: 20141 **The Factory of Heroes** (climax, Kiel D-01) ·
20142 **The One Who Said No** (Echo story) · 20143 **Slum Sample Run** ·
20144 **Scaraba Chitin Order** · 20145 **Clone Name Registry** (new ID).

- [ ] 1. Vault docs read (5 quests + hub + NPCs)
- [ ] 2. quest_db block rewritten (verify Scaraba/slum-mob MobIds in mob_db!)
- [ ] 3. dm_quests registry arrays (5 entries)
- [ ] 4. dm_flags additions
- [ ] 5. arc_10_lighthalzen.txt rewrite
      ⚠️ `arc10.echo` decision currently completes 20144 → re-point per new
      mapping (20142) or flags-only. ⚠️ dm_wynne_* / dm_arc10_echo_freed /
      dm_echo_trusts_party are referenced by later arcs — must keep working.
- [ ] 6. dm_decisions updated (arc10.echo, arc10.wynne rows)
- [ ] 7. dm_beats DM_BeatArc10 updated
- [ ] 8. hunt markers (3)
- [ ] 9. CAMPAIGN.md + dm-tooling.md ranges → 20141–20145
- [ ] ✔ Validation block passes → **Arc 10 done** (date: ______)

## Arc 11 — Wrath of Heaven / Hugel (`act_03/`, IDs 20151–20155, +20152 free)

Target: 20151 **When Heaven Turns** (climax, keep) · 20153/54/55 + 20152 remap to
**The Dying Valkyrie's Word** (story) · **Hugel Airship Muster** ·
**Dragon Scale Turn-In** · **Temple Edge Vigil**.
(Replaces: Gryphon Vigil, Dragon Pack Dispersal, The Zealot's Testimony.)

- [ ] 1. Vault docs read
- [ ] 2. quest_db block (uses free 20152; verify Abyss Lake dragon MobIds)
- [ ] 3. dm_quests registry
- [ ] 4. dm_flags additions
- [ ] 5. arc file rewrite
- [ ] 6. dm_decisions rows checked/updated
- [ ] 7. dm_beats updated
- [ ] 8. hunt markers
- [ ] 9. doc tables → 20151–20155
- [ ] ✔ Validation passes → **Arc 11 done** (date: ______)

## Arc 12 — Beyond the Horizon / New World (IDs 20161–20165, +20162 free)

Target: 20161 **The Wound With a Keeper** (climax, keep) · story **First Contact
Done Wrong** · hunts **Manuk Supply Line** / **Cornus Mercy Run** /
**Dicastes Border Papers**.

- [ ] 1. Vault docs read
- [ ] 2. quest_db block (+20162)
- [ ] 3. dm_quests registry
- [ ] 4. dm_flags additions
- [ ] 5. arc file rewrite
- [ ] 6. dm_decisions rows
- [ ] 7. dm_beats
- [ ] 8. hunt markers
- [ ] 9. doc tables
- [ ] ✔ Validation passes → **Arc 12 done** (date: ______)

## Arc 13 — Island of the Damned / Nameless (IDs 20171–20175, +20172 free)

Target: 20171 **The Council of the Drowned** (climax, keep) · story **A Name You
Knew** · hunts **Abbey Bell Rotation** / **Drowned Coin Tithe** /
**Lasagna Root Wardens**.

- [ ] 1. Vault docs read
- [ ] 2. quest_db block (+20172)
- [ ] 3. dm_quests registry
- [ ] 4. dm_flags additions
- [ ] 5. arc file rewrite
- [ ] 6. dm_decisions rows
- [ ] 7. dm_beats
- [ ] 8. hunt markers
- [ ] 9. doc tables
- [ ] ✔ Validation passes → **Arc 13 done** (date: ______)

## Arc 14 — The Fire That Ends the World / Veins (IDs 20181–20185, +20182 free)

Target: 20181 **The Herald in the Magma** (climax, keep) · story **The Deep
Shift** · hunts **Veins Evacuation Ledger** / **Bifrost Ash Scouting** /
**Magmaring Firebreak**.

- [ ] 1. Vault docs read
- [ ] 2. quest_db block (+20182; Magmaring MobId 1836 — verify)
- [ ] 3. dm_quests registry
- [ ] 4. dm_flags additions
- [ ] 5. arc file rewrite
- [ ] 6. dm_decisions rows
- [ ] 7. dm_beats
- [ ] 8. hunt markers
- [ ] 9. doc tables
- [ ] ✔ Validation passes → **Arc 14 done** (date: ______)

## Arc 15 — The Hero's Tomb / Aldebaran (IDs 20191–20195)

Gap-fill: server already matches 3/5. Replace 20194 "The Method's Price";
add **Clock Tower Daily Wounds** + **Fragment Relief Rotation** (two in, one
out — renumber inside the block, tracker 20191 Five Doors stays).

- [ ] Vault docs read (esp. the two new quests)
- [ ] quest_db: 20194 replaced + 20195 added, Targets verified
- [ ] dm_quests registry (5 entries) + dm_flags if needed
- [ ] arc file: turn-ins for the two new hunts wired into the giver
- [ ] dm_beats + hunt markers + doc tables
- [ ] ✔ Validation passes → **Arc 15 done** (date: ______)

## Arc 16 — The Royal Banquet / Prontera (IDs 20201–20205)

Gap-fill: add **Invaded Prontera Relief** (20205).

- [ ] Vault doc read; quest_db entry added (Targets verified)
- [ ] registry + arc file turn-in + beats + marker + doc tables
- [ ] ✔ Validation passes → **Arc 16 done** (date: ______)

## Arc 17 — The Sage's Legacy / Varmundt (IDs 20211–20215)

Gap-fill: add **Corridor of Phantom Map** (20215); rename "Sages Legacy" →
"Sage's Legacy Dailies".

- [ ] Vault doc read; quest_db add + rename
- [ ] registry + arc file turn-in + beats + marker + doc tables
- [ ] ✔ Validation passes → **Arc 17 done** (date: ______)

## Arc 18 — The Witch of Death / Niflheim (IDs 20221–20225 + 20230)

Gap-fill: add **Illusion Grief Rotation** (20224) + **Opera House Encore** (20225).

- [ ] Vault docs read; quest_db entries added
- [ ] registry + arc file turn-ins + beats + markers + doc tables
- [ ] ✔ Validation passes → **Arc 18 done** (date: ______)

## Arc 19 — registry quirk only

- [ ] Move 20230 "Allied Front Muster" from `.arc18_id[]/.arc18_nm$[]` to the
      arc19 arrays in dm_quests.txt (vault places it in Arc 19)
- [ ] Re-check consumers of `DM_ArcQuestCount(18/19)` (console sync loops are
      registry-driven, so this should be automatic — verify once)
- [ ] ✔ Validation passes → **Arc 19 done** (date: ______)

## Eden Group loose end

- [ ] Fix `eden_iro.txt`'s 4 unresolved `duplicate()` NPCs (Suhnbi#cash,
      MightyHammer, Ripped Cabus#GymPass, Alora): either load the source files
      (`npc/re/merchants/hd_refiner.txt`, `npc/merchants/cashheadgear_dye.txt`,
      + the refiner/gympass pair) in scripts.conf, or comment those 4 blocks out
- [ ] `bash ./script-checker` on the whole eden set → exit 0 (date: ______)

## Final pass (after all arcs)

- [ ] script-checker over every touched file → exit 0
- [ ] Full boot-parse: MariaDB up, all 3 servers start, `log/run-map.out` free of
      quest_db + NPC parse errors
- [ ] Regenerate `planning/campaign_quest_journal_entries.lua` for every
      changed/added ID (names + `@dm warp` lines)
- [ ] Re-merge client journal per `client/README.md` §1
      (`tools/campaign_quest_merge.py` → recompile .lub) and hand the new file
      to players
- [ ] Update `planning/dm-playtest-notes.md` stale ID references (mentions old
      20124 behavior)
- [ ] In-game smoke test per ported arc: `@dmbeat` → Start Arc → marker on map →
      turn-in → story quest → climax completes tracker
- [ ] Commit per arc or per session; update this doc's checkboxes in the same
      commit — **the doc is the work log** (date all boxes)

## Gotchas (append as found)

- Old MobId comments lie — verify against mob_db (1164=Requiem, 1778=Gazeti).
- The climax quest isn't always vault file 05 (Arc 9's was 04).
- `DM_ArcTrackerId` = registry entry [0]; get the order wrong and the Session
  Board / `@dm status` arc detection breaks.
- Don't wire extra MVP spawns to the tracker-completing kill event (a Vesper
  add on `OnGloomDead` would complete the arc when the add dies).
- `dm_decisions.txt` quest-action field: `"complete","<id>"` completes that
  quest on DM_Decide — set `"", ""` when the confrontation belongs to the climax.
