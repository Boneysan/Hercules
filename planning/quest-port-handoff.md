# Handoff — Port the Vault Quest Rewrites into the Server (Arcs 10–19)

> **Task:** The Obsidian vault's quest rewrites (finished 2026-07-02, see
> `H:\Docs\Obsidian Notes\Game Design\Ragnarok_Online\Campaign\_Handoff_XP_Quest_Rewrites.md`)
> were never ported into the server. Arcs 8 and 9 are now ported and validated.
> Continue the port for Arcs 10–19 using the recipe below, then run the final
> validation + client-journal pass.

## Background (audit findings, 2026-07-04)

- Vault = 95 quest designs (19 arcs × 5). Server had 88 campaign quests + tracker
  (20000), but arcs 8–19 still carried **old pre-rewrite designs** — 0/5 to 4/5 of the
  final vault quests per arc. Zero of the rewritten titles appeared anywhere in
  `npc/` or `db/` before this port began.
- Arcs 1–7 were already in sync (the earlier "sync Arc 4/5/6 dialogue" commits).
- Design sources live in the vault:
  `Campaign/Act_*/Arc_NN_*/Quests/0[1-5]_*.md` (5 per arc; 01–03 are `#xp-support`
  repeatables, 04–05 are story quests — one of which is the arc climax).

## State of the port

| Arc | Status |
|---|---|
| 8 — Glast Heim | ✅ **DONE** (use as the reference port) |
| 9 — Rachel | ✅ **DONE** (second reference; has a new-NPC example, Osric) |
| 10 — Lighthalzen | ❌ todo |
| 11–14 | ❌ todo (each has a FREE ID at the x2 slot: 20152, 20162, 20172, 20182) |
| 15–18 | ❌ todo (partial: only add missing quests / replace stragglers — see below) |
| 19 | ⚠️ only a registry quirk (see below) |
| Final validation + client journal | ❌ todo |

All Arc 8+9 files pass `bash ./script-checker` (exit 0) and quest_db braces balance.

## Shared infrastructure already fixed (do NOT redo)

- `DM_QuestRegistry` converted from `function script` → real invisible NPC
  (`dm_quests.txt`) so `getvariableofnpc()` works and OnInit populates arrays.
- `dm_console.txt`'s two hardcoded campaign-quest-ID lists replaced with
  **registry iteration** (`DM_ArcQuestCount`/`DM_ArcQuestId`, arcs 1–19 + 20000).
  → New arcs' IDs are picked up automatically; also fixed the old lists omitting
  20230/20234.
- Latent data bugs fixed in passing: old 20122 hunted MobId 1164 (**Requiem**,
  mislabeled "Raydric"); old 20132 hunted 1778 (Gazeti, labeled "Ice Titan").
  **Lesson: verify every MobId against `db/re/mob_db.conf` — old comments lie.**

## ID-mapping convention (follow Arc 6/7/8/9)

Registry entry order per arc = `[climax/tracker, other story quest, 01, 02, 03]`:

- **First ID = arc tracker** (`DM_ArcTrackerId` returns registry entry [0]).
  It must be the quest started at arc start and completed at the MVP death
  set-piece. Map it to whichever vault quest is `Type: main (arc climax)` —
  usually 05, but **Arc 9's climax was 04** — read the docs, don't assume.
- Second ID = the other story quest (the side/trial quest).
- Remaining IDs = xp-support 01, 02, 03 (hunt quests with Targets in quest_db).
- Arcs 8–10 gain a 5th quest at x5 (20125, 20135, 20145). Arcs 11–14 reuse the
  **skipped x2 slot** (20152, 20162, 20172, 20182) for their 5th quest.

## THE RECIPE — files to touch per arc (9 stops)

Use `arc_08_glast_heim.txt` / `arc_09_rachel.txt` ports as exemplars throughout.

1. **Read the vault docs**: all 5 `Quests/*.md` + the arc hub + `NPCs/*.md`.
2. **`db/quest_db.conf`** — rewrite the arc's block: names, Targets (verified
   MobIds!), keep the existing Exp/Jexp reward scale of the old entries; update
   the `//=` header comment above the block.
3. **`npc/custom/dm_campaign/shared/dm_quests.txt`** — the arc's
   `setarray .arcNN_id[]` / `.arcNN_nm$[]` (order per the convention above).
4. **`npc/custom/dm_campaign/shared/dm_flags.txt`** — add new story flags to the
   arc's array (branch outcomes: trust/aid/curse/smashed etc.).
5. **`npc/custom/dm_campaign/act_0X/arc_NN_*.txt`** — the main rewrite:
   - Quest-giver starts tracker + three xp quests; per-quest turn-ins with the
     vault's Noble/Pragmatic/Suspicious-dark branches setting flags;
     all-three-done → start the story/trial quest; then climax gate.
   - Keep `DM_PartyExp`/`DM_GivePartyZeny` reward scale from the old file.
   - Update the OnInit `setquestinfo` blocks to the new IDs.
   - The MVP set-piece completes the tracker; add flag-aware announce lines.
   - New scene NPCs are fine (see Osric in arc_09, Martyrs' Tombs in arc_08).
6. **`shared/dm_decisions.txt`** — if the arc's DM_Decide rows completed an
   old quest ID that no longer exists as "the decision quest", switch the
   action/quest fields to `"", ""` (flags only) and fix the log strings.
   (Done for arc08.manfred, arc09.karsh; check arc10.echo → completes 20144.)
7. **`shared/dm_beats.txt`** — `DM_BeatArcNN`: fix quest starts (tracker + the
   three xp IDs; story quest gets its own "Beat: start" case), warp targets for
   new NPCs, and flag-aware MVP spawn variants if the vault design calls for it.
8. **`shared/dm_hunt_markers.txt`** — one marker per hunt quest: correct map +
   `setquestinfo QINFO_QUEST, <id>, 1`. Maps come from the vault docs' XP-role
   lines (verify map names exist).
9. **Docs** — `npc/custom/dm_campaign/CAMPAIGN.md` and `planning/dm-tooling.md`
   arc tables: ID range now spans 5 quests (e.g. `20141–20145`).

**Validate after each arc:**
```bash
bash ./script-checker npc/custom/dm_campaign/act_0X/arc_NN_*.txt \
  npc/custom/dm_campaign/shared/{dm_quests,dm_decisions,dm_beats,dm_hunt_markers,dm_flags,dm_console}.txt
# plus a brace-balance / ID-list check on the arc's quest_db block
```

## Per-arc worklist

### Arc 10 — Lighthalzen (`act_02/arc_10_lighthalzen.txt`, IDs 20141–20145)
Old: Heroes They Made / Lab Infiltration / Lower Level Sweep / Echo's Protocol.
New mapping: 20141 **The Factory of Heroes** (climax, Kiel D-01),
20142 **The One Who Said No** (Echo story — arc10.echo decision in dm_decisions
currently completes 20144 → re-point or flags-only), 20143 **Slum Sample Run**,
20144 **Scaraba Chitin Order**, 20145 **Clone Name Registry**.
Note: existing flags dm_wynne_* / dm_arc10_echo_freed / dm_echo_trusts_party are
referenced by later arcs — keep them working.

### Arcs 11–14 (all in `act_03/`; 5th quest goes in the x2 slot)
- **11 Hugel** (20151–55, +20152): climax = When Heaven Turns (20151, keep).
  New: Hugel Airship Muster / Dragon Scale Turn-In / Temple Edge Vigil;
  story = The Dying Valkyrie's Word (replaces Gryphon Vigil/Dragon Pack
  Dispersal/Zealot's Testimony).
- **12 New World** (20161–65, +20162): climax = The Wound With a Keeper (20161,
  keep). New: Manuk Supply Line / Cornus Mercy Run / Dicastes Border Papers;
  story = First Contact Done Wrong.
- **13 Nameless Island** (20171–75, +20172): climax = The Council of the
  Drowned (20171, keep). New: Abbey Bell Rotation / Drowned Coin Tithe /
  Lasagna Root Wardens; story = A Name You Knew.
- **14 Veins/Thor** (20181–85, +20182): climax = The Herald in the Magma
  (20181, keep). New: Veins Evacuation Ledger / Bifrost Ash Scouting /
  Magmaring Firebreak; story = The Deep Shift.

### Arcs 15–18 (gaps only — most quests already match)
- **15** (20191–94 + new 20195): replace 20194 "The Method's Price" → the vault
  quests **Clock Tower Daily Wounds** + **Fragment Relief Rotation** (two in,
  one out — renumber within the block).
- **16** (20201–04 + new 20205): add **Invaded Prontera Relief**.
- **17** (20211–14 + new 20215): add **Corridor of Phantom Map**; server
  "Sages Legacy" ≈ vault "Sage's Legacy Dailies" (rename).
- **18** (20221–23 + 20230…): add **Illusion Grief Rotation** and **Opera House
  Encore** (free IDs 20224/20225).

### Arc 19 — registry quirk only
20230 "Allied Front Muster" sits in the **arc18** registry array; the vault
places it in Arc 19. Move it to `.arc19_id[]`/`.arc19_nm$[]` (and re-check any
`DM_ArcQuestCount(18/19)` consumers).

## Final pass (after all arcs)

1. `bash ./script-checker` over every touched file → exit 0.
2. Full boot-parse: start MariaDB, run all three servers, grep `log/run-map.out`
   for `quest_db` errors and NPC parse errors.
3. **Client quest journal**: regenerate `planning/campaign_quest_journal_entries.lua`
   entries for every changed/added ID (names + `@dm warp` lines), then re-merge
   into the client's `OngoingQuestInfoList_True_EN.lub` per `client/README.md` §1
   (`tools/campaign_quest_merge.py`).
4. Update `planning/dm-playtest-notes.md` if it references old quest IDs
   (it mentions 20124's old behavior).
5. In-game smoke test per arc: `@dmbeat` → Start Arc → hunt marker shows on map
   → turn-in → story quest → climax completes tracker.

## Unrelated open item (from the same session)

`npc/scripts.conf` now loads the **Eden Group** files (beginner quests), but
`npc/re/quests/eden/eden_iro.txt` has 4 `duplicate()` NPCs whose originals live
in files that aren't loaded (`npc/re/merchants/hd_refiner.txt`,
`npc/merchants/cashheadgear_dye.txt`, and a gympass/refiner pair —
Suhnbi#cash, MightyHammer, Ripped Cabus#GymPass, Alora). Either load those
source files in scripts.conf, or comment those 4 duplicate blocks out of
eden_iro.txt. Everything else in the Eden set passes script-check.
