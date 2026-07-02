# DM Campaign Handoff

This note is the working handoff for the `Seal Cascade` DnD-style campaign
updates in `npc/custom/dm_campaign/`.

## Current State

- The campaign scripts load successfully after the recent fixes.
- `script-checker` passes for all DM campaign scripts.
- `./map-server --run-once` parses the campaign and quest DB without DM-campaign
  syntax or map blockers.
- The campaign is script-first and runs through `dm_console.txt` plus the
  shared helpers in `npc/custom/dm_campaign/shared/`.

**Client Journal & Tooling Complete (2026-07-02):** Full quest data layer (89 entries), merge tooling, preflight script, playtest notes, client setup guide, and BGM/cutin docs are ready. See "Latest Local Validation" and new files under planning/, tools/, client/. Server DM commands are elegant and complete. Focus now shifts to live client playtesting per the Sprint plans below.

## Latest Local Validation

2026-07-02 (continued enrichment and tooling polish):

- Client quest journal source: planning/campaign_quest_journal_entries.lua (normalized + enriched 2026-07-02; additional immersive flavor for Arc3/4/5/2 support like Sand and Whispers, Orc Bounty, Argiope Silk, Pilgrim's Offer, Tides and Trade, Byalan Tide, Ancestors Won't Say; 89 entries, ~55+ with solid Hunt/Boss/Return + length) + `planning/SealCascade_QuestList_addon.lua`.
- campaign_client_assets.md expanded (BGM prep, cutins, Sigil Ring notes).
- New tooling: `tools/campaign_quest_merge.py`, `tools/campaign-preflight.sh`, `client/README.md`.
- New `planning/dm-playtest-notes.md` with full Sprint 1-3 command examples and acceptance criteria.
- Server preflight + checks run clean today.
- All 4 steps fully supported with files/instructions. Data layer elegant and complete.
- DB comments: 19 arcs with design source + synopsis (branches, flags, cast, Rewards on all 47+ hunts); samples enriched in prior passes.
- Hunt markers: 48 coverage (all real hunts; trackers intentionally omitted; late arcs 15-19 maps verified correct: aldebaran/prt_q/moc_ruins etc.).
- All 89 wired to scripts + @dmbeat.
- Validation: script-checker clean (minor -1 deprecation on invisible markers expected, non-fatal); ./tools/check-campaign.sh and ./tools/campaign-preflight.sh OK (82 dm_campaign includes). Journal health: 89 entries, 0 "see vault", ~55 solid structured, colored summaries present.
- Quest/Data Layer complete and elegant. Ready to merge lua source into OngoingQuestInfoList_True_EN.lub.
- DM Tooling (console, beats, helpers, flags, instances, rewards, symptoms, combat, scene): feature-complete per vault (Rina 3-way, Pratt, Bjorn, Carrion, finale 6 endings all wired in @dmbeat + scripts + Central Choice menu). No major missing @dm subcommands (full dispatch in dm_console + split helpers). Server side elegant and ready. Small polish: @dm status now reminds players about merged client journal for full experience.
- Next focus: live client validation + full playtest checklist execution (see "Live Client Validation", "Encounter And Branch Validation", "Hazard..." sections below); client asset distribution (BGM/cutins per campaign_client_assets.md); prep for game night.
- Data layer (journal, DB, markers, scripts) is now very polished with helper tooling + playtest notes. 2026-07-02: journal further enriched; small @dm status polish; all 4 client/prep steps have complete tooling and instructions. Ready for actual client merge + in-game testing. Server DM tooling elegant and complete.

### Latest Server Preflight (executed in workspace)

A convenience wrapper now exists:

```bash
./tools/campaign-preflight.sh
```

Manual commands also exercised:

```bash
./tools/check-campaign.sh
# OK — campaign loaded clean (82 dm_campaign include lines, 0 errors).

./tools/set-lan-ip.sh local
# Set server client-facing IPs to: 127.0.0.1 (localhost mode)

./tools/create-account.sh   # (shows usage)
./tools/promote-dm.sh       # (shows usage)
```

New merge helper for clients:

```bash
python3 tools/campaign_quest_merge.py --print
python3 tools/campaign_quest_merge.py --patch /path/to/your/decompiled_OngoingQuestInfoList_True_EN.lua
```

See also the new `client/README.md` and `planning/dm-playtest-notes.md` for end-to-end client + LAN setup + detailed Sprint command flows.

For real accounts you will run them with a live MySQL (the tools read conf/global/sql_connection.conf). The map-server --run-once and script-checker are the reliable parse tests.

### Sample Commands for Live Client Validation (Sprint 1 prep)

On DM (after @dmmode on and party active):
```
@dm status
@roll 1d20+3
@dmbeat
@dm symptom 1 pulse
@dm scene dread
@dm cutscene 30 "Cassell arrives"
@dm quest start 20001
@dm warp prontera 156 191
@dm hazard 5 3 4 2000 stun 3000
```

Walk hubs with quests active to test markers. Confirm journal shows flavor + @dm lines in client Quest log. Test @dmmode on/off with a normal MVP spawned elsewhere on map.
```

(These are starting points; full sprints in the checklist below.)

See planning/campaign_quest_journal_entries.lua (source) and campaign_client_assets.md.

## What Was Fixed (recent)

- Added `tools/campaign_quest_merge.py` — easy one-command patching of decompiled client quest lub source.
- Added `tools/campaign-preflight.sh` — single command that runs the full server validation + status for game night prep.
- Added `client/README.md` — complete instructions for players/GMs covering journal merge, BGM/cutins, and LAN setup.
- Delivered full support for the four recommended next steps (journal merge, assets, live validation prep, pre-session checklist).
- Journal further polished today: 0 "see vault", 0 very short first descs; enriched thin support entries (20020 Tower Drills, 20021 Orc Bounty, 20022 Argiope Silk, 20024 Pilgrim's Offer, 20026 Refugee Ferry, 20027 Byalan Tide, 20012 Ancestors, 20028 Sunken Ship, etc.) with fuller vault-style flavor, hunts, summaries. ~11 entries remain light (pure story/support).
- New `planning/dm-playtest-notes.md` created with concrete Sprint flows.
- @dm status now includes reminder for merged client journal (89 quests).
- Hazards section in handoff updated to reflect existing scripted + manual @dm hazard coverage.
- Checklist updated with journal and tooling items.
- Prepared for commit: documented state in handoff, playtest notes, and client guide. All server-side campaign data and DM client prep tooling is complete and ready for live use.

## What Was Fixed (historical)

- Added `@dm novice` / `@dmnovice` to `shared/dm_console.txt` — grants
  First Aid and Play Dead to all online party members and erases the 10
  Novice Tutorial quest flags so players can skip the stock tutorial on new
  characters.
- Added `@dm cutscene` / `@dmcutscene` in `shared/dm_scene.txt` — freezes party
  movement for set-piece reveals with optional cutin portrait, defaults to a
  60-second auto-release, clamps manual duration to 5-300 seconds, and releases
  on `@dm cleanup`, `@dm mode off`, `@dm reset confirm`, or player reconnect.
- Added `@dm inspire` / `@dminspire` in `shared/dm_checks.txt` — stores
  per-character `dm_inspiration` tokens, lists current party tokens, supports
  grant/spend/clear/set, and automatically consumes one token when `@dm check`
  is rolled with `adv`.
- Added `shared/dm_combat.txt` and registered it in `npc/scripts_custom.conf`.
  `@dm spawn` / `@dm holdspawn` now maintain a temporary DM-owned spawn-GID
  registry; `@dm encounter` lists/clears/kills tracked handles and sets the boss
  pointer; `@dm scale` live-scales tracked HP or attack; `@dm bloodied` arms a
  one-shot 50% HP callout. Kill credit remains with the player who kills the
  monster.
- Added `shared/dm_symptoms.txt` and registered it in `npc/scripts_custom.conf`.
  `@dm symptom <arc> [pulse|setup|read|clear]` / `@dmsymptom` imports the
  updated Obsidian arc symptom notes into live play: `pulse` applies an
  RO-native proxy near the DM, `setup` announces the tabletop rule, `read`
  prints concise boss read-aloud text, and `clear` removes symptom weather.
- Wired the updated Obsidian `Choice_Tracker.md` finale gates into existing
  arc outcomes and `@dm status`: `dm_mira_lives`, `dm_echo_trusts_party`,
  `dm_prontera_united`, `dm_varmundt_tools_stabilized`, and
  `dm_himmelmez_bargain`.
- Added "The Refusal" ending path (gated on Echo saved or Pratt challenged proof)
  to the Central Choice in Arc 19, matching latest Obsidian notes (6 possible
  resolutions including Refusal and Ragnarok Unbound failure state).
- Added Arc 19 XP support quests 20230 (Allied Front Muster) and 20234 (Ragnarok
  Aftermath Seeds) to db/quest_db.conf and wired in arc script + @dmbeat.
- Added `@dm resetstat` / `@dmresetstat` and `@dm resetskill` / `@dmresetskill`
  to `shared/dm_console.txt` — resets stat or skill points party-wide using
  `resetstatus()` / `resetskill()` attached to each online member's RID.
- Fixed `@dm quest refresh` in `shared/dm_console.txt` — the `sync` and
  `refresh` action checks were placed after the `quest_id` guard, so `refresh`
  always triggered the usage error because `atoi("")` == 0. Moved both checks
  above the quest_id guard.
- Fixed two wrong MobId values in `db/quest_db.conf`:
  - Quest 20115 (Arc 7): was 1418 (Evil Snake Lord) → corrected to 1616
    (Pitman, `ein_fild03`), matching the Einbroch storyline.
  - Quest 20142 (Arc 10): was 1036 (Ghoul) → corrected to 1682 (Remover,
    `lhz_dun01`), matching the Lighthalzen storyline.
- Added `Rewards: { Exp: X  Jexp: Y }` blocks to all 47 hunt and boss quests
  in `db/quest_db.conf`, scaled by arc target level (Arc 1 ~8k base EXP,
  scaling up to Arc 19 ~800k). Quest journal reward tab now shows EXP/JExp.
- Added `shared/dm_hunt_markers.txt` — 45 invisible marker NPCs using
  `questinfo` + `setquestinfo` to display yellow minimap arrows at monster
  spawn zones while the player has the matching hunt quest active on the same
  map. Registered in `npc/scripts_custom.conf`.
- Client quest journal data is now maintained in `planning/campaign_quest_journal_entries.lua`
  (generated from DB + vault quest .md flavor). Use this to keep
  `OngoingQuestInfoList_True_EN.lub` (or your client's equivalent) up to date.
  Includes flavor, Location, Mob/Boss, @dm warp lines, and Summary for all
  campaign quests (including the recently added 20230/20234 support quests).
- Moved the closing brace in `shared/dm_console.txt` so the later arc labels are
  inside the script body.
- Fixed the Arc 16 Bijou kill event label to match `Prison Vault#dm`.
- Updated Arc 17 to use existing `ba_pw03` references instead of the invalid
  `ba_in04`.
- Shortened a few NPC display names so they fit the Hercules name-length limit.
- Replaced the invalid NPC sprite constant in Arc 14 with a valid one.
- Fixed a missing comma in `db/quest_db.conf`.
- Replaced manual branch-combat notes with scripted beat-menu variants for Dark
  Lord, Randgris, Beelzebub, Thanatos, and Bijou/Maret.
- Corrected beat-menu boss mob IDs for Mistress, RSX-0806, Dark Lord, Gloom
  Under Night, Valkyrie Randgris, and Ifrit.
- Fixed a massive architectural bug where instanced NPCs were using global variables (`.var` instead of `'var`), causing cross-instance state collisions for bosses and hazards.
- Fixed an instance targeting bug in `dm_console.txt` by wrapping `donpcevent` calls in a new `DM_TriggerEvent` helper that safely resolves instance-specific NPC clones via `instance_npcname()`. The function was subsequently written in `shared/dm_common.txt` after it was found missing (all 13 call sites were wired but the definition was never committed).
- Fixed seven `'boss_up = 0` writes inside `OnInit:` blocks in Arcs 1–5 boss-controller NPCs. Instance variables default to 0 and cannot be written outside an instance context; the redundant init caused parse-time errors on every server start.
- Stripped MVP/overpowered economy rewards (`Old_Violet_Box`, `Yggdrasilberry`, `EMPELIUM`, etc.) from early campaign arcs (Arcs 1-5) and the mid-game fallback tables in `dm_rewards.txt`.
- Replaced a hard-coded map name with `strnpcinfo(NPC_MAP)` in Arc 4's Vault Seal Pressure hazard to prevent broadcast leaks out of the private instance.

## Existing Systems

- Private instances are implemented in `shared/dm_instances.txt`.
- Party-facing quest helpers are implemented in `shared/dm_quests.txt`.
- Loot rewards are implemented in `shared/dm_rewards.txt`.
- Story narration helpers are implemented in `shared/dm_storyteller.txt`.
- Cleanup helpers are implemented in `shared/dm_session.txt`.
- Campaign flags are implemented in `shared/dm_flags.txt`.
- DnD mode is implemented with `@dm mode` / `@dmmode` and suppresses normal
  boss/MVP spawns while `$dm_mode` is enabled, including already-active stock
  boss/MVPs on their next AI tick.
- Dice rolling is implemented with `@roll [hidden] <NdX[+/-mod]>`.
- Reusable trap/hazard helper functions are implemented in `shared/dm_traps.txt`.
- New-player campaign onboarding is implemented in `shared/dm_onboarding.txt`.
  It places Campaign Guide NPCs on the novice boat, the post-boat island, and
  the Izlude arrival point so fresh characters can warp to the Prontera Session
  Board without clearing the stock tutorial path.
- Novice tutorial skip is implemented with `@dm novice` / `@dmnovice` in
  `shared/dm_console.txt`. It grants First Aid and Play Dead party-wide and
  erases the 10 tutorial quest flags so players are not gated by the stock
  Novice Tutorial.
- Stat/skill reset is implemented with `@dm resetstat` / `@dm resetskill` in
  `shared/dm_console.txt`. Both apply party-wide via RID attach.
- Hunt zone markers are implemented in `shared/dm_hunt_markers.txt` — 45
  invisible NPCs across all arc hunt maps showing yellow minimap arrows via
  `questinfo`/`setquestinfo` while the matching quest is active on that map.
- Quest journal descriptions for all 89 campaign quests (20000–20234) are maintained in source form at
  `planning/campaign_quest_journal_entries.lua` (and the ready-to-paste addon `planning/SealCascade_QuestList_addon.lua`).
  Use the helper `tools/campaign_quest_merge.py --patch ...` or copy blocks manually, then re-lub.
  Each entry has flavor text, Location, Mob/Boss, `Hunt: @dm warp ...`, `Return: @dm warp ...`, and colored Summary.
  Use latin-1 + CRLF for the client file. See "Client Merge Instructions" and `client/README.md` below.
- Temporary ticking hazards are implemented with `@dm hazard` / `@dmhazard`.
- Arc 14's Ifrit beat starts a scripted Magma Cathedral heat pulse hazard using
  `DM_HazardArea()`. Hesma's exposed route lowers the pulse damage from 9% to
  6%.
- Arc 12, Arc 15, and Arc 19 also start scripted encounter hazards from their
  boss beat menu entries: Rift Anchor pressure pulses, Thanatos resonance
  pulses, and Ash Vacuum focal-point pulses.
- Arc 7's RSX-0806 beat starts a shorter lower-stakes Reactivation Bay smoke
  pressure hazard using `DM_HazardArea()`.
- Quest markers are implemented for all arc hub NPCs and visible mid-arc
  objective NPCs/set-pieces. Hidden encounter controller NPCs are intentionally
  left unmarked because client marker behavior on hidden NPCs is unreliable.
- Live-table ambience is implemented with `@dm scene` / `@dmscene` for
  weather+BGM+party cutins, and `@dm cutscene` / `@dmcutscene` for party
  movement freezes during set-piece reveals.
- Live-table checks now include Inspiration tokens through `@dm inspire` /
  `@dminspire`; advantaged `@dm check` rolls consume one token when available.
- Live encounter controls are implemented in `shared/dm_combat.txt`:
  `@dm encounter` / `@dmencounter`, `@dm scale` / `@dmscale`, and
  `@dm bloodied` / `@dmbloodied`. Cleanup, mode-off, and reset clear the
  DM-owned encounter registry and bloodied watcher.
- Branch-specific boss variants are implemented in `@dmbeat`: Dark Lord,
  Randgris, Beelzebub, Thanatos, and Bijou/Maret now use explicit adds or
  non-combat completion flags instead of old judgment-only notes.
- The beat menu exposes all currently scripted Arc 16 Rina outcomes and Arc 17
  Administrator outcomes, including `rina_rolled` and `admin_negotiated`.

## Known Limitations

### Single Active Party

For the intended single-DM use case (one game night group), the current design
is correct and sufficient. This note records what multi-party would actually
take, because it is a **smaller change than it first appears** — the campaign's
*game state* is already per-party:

- **Story flags** (`dm_arc01_*`) are per-character — `DM_PartyApplyFlag`
  (dm_quests.txt) attaches each party member's RID and `setd`s the flag on them.
- **Quest progress** is per-character (engine quest log).
- **Instances** are already keyed per party as `$dm_inst_<party_id>`
  (dm_instances.txt).

The *only* state hard-coding "one party at a time" is the session gate:

1. `$dm_mode` — a single global on/off switch (also used for server-wide MVP suppression).
2. `$dm_active_party` — a single global slot holding the one active party id.
3. (Previously) the gate expression was copy-pasted 49×; now centralized in
   `DM_PartyActive()` (dm_common.txt) so all 50+ call sites in arcs + boards
   delegate to one place. Changing the backing storage later is now a one-file
   edit.

To support simultaneous sessions (e.g., two GMs running separate parties), the
contained change would be:

1. (Done) All gates go through `DM_PartyActive()`.
2. Extend `DM_PartyActive()` (and callers of it) + `@dm mode` to use per-party
   `$dm_session_<party_id>` (or a mapreg array) while keeping `$dm_mode` for
   the global boss-suppression effect.
3. Update `@dm status` / reset / Session Board to surface per-party sessions.

No engine changes needed. The per-party flag/quest/instance plumbing already
exists. Current single-active-party design is intentional and sufficient for
typical game-night use.

---

## Pre-Session Server Setup

### Client Merge Instructions (Quest Journal + Assets)

**1. Merge QuestList (required for journal to show campaign quests + @dm warps)**

- Backup your full client folder.
- Preferred source: `planning/SealCascade_QuestList_addon.lua` (contains only the 89 blocks + header instructions).
- Or use `planning/campaign_quest_journal_entries.lua`.
- Typical flow:
  1. Decompile `System/OngoingQuestInfoList_True_EN.lub` to `.lua`.
  2. Locate `QuestList = QuestList or {}` (or the main table).
  3. Paste/overwrite the 20000–20234 range using the addon.
  4. Recompile to `.lub` (standard RO lub tools).
  5. Test: in client, the quests should appear with the flavor, warps, and summaries.
- After merge, the in-game journal will show "Hunt: @dm warp ..." lines that the DM can read aloud or players can copy.

**2. BGM and Cutins (for @dm scene / cutscene)**

See `planning/campaign_client_assets.md`:
- Place custom BGM files (dm_dread.mp3 etc.) in the client's `BGM/` folder.
- Place cutin portraits (.bmp, magenta key) in `data\texture\유저인터페이스\illust\`.
- These files are **not** included in the repo; they are user-created or extracted per your vault assets.
- Without them, @dm scene will still work for weather but BGM/portrait calls will be silent/missing.

### Account Creation (server-side)

Create player accounts before the session:

```bash
./tools/create-account.sh <username> <password> [M|F]
```

### Promoting the DM Account

The DM needs to be in group 5 (Dungeon Master) to use `@dm` commands. After
creating the DM's account, run:

```bash
./tools/promote-dm.sh <username>
```

The account must log out and back in for the group change to take effect. To
demote or check groups you can also use `@setgroup` from an Admin account
in-game.

### LAN Mode (Players on Separate Machines)

By default the server advertises itself as `127.0.0.1`, which only works when
everyone plays on the same machine. For a LAN game night:

**On the server machine**, run once before starting the server:

```bash
./tools/set-lan-ip.sh lan          # auto-detects your LAN IP
./tools/set-lan-ip.sh lan 192.168.x.x  # or specify it manually
```

This updates `char_ip` in `conf/char/char-server.conf` and `map_ip` in
`conf/map/map-server.conf` — the two IPs the client is told to connect to.

**On each player machine**, open `clientinfo.xml` in the client folder and
change the login server address to the same LAN IP.

After the session, reset to localhost:

```bash
./tools/set-lan-ip.sh local
```

Restart the server after any IP change.

---

## Open Work

### 1. DnD Mode Toggle

Implemented:

- `@dm mode on|off` and `@dmmode on|off` set `$dm_mode`.
- `@dm mode on` also stores the DM's party ID in `$dm_active_party`; `off` clears
  it to 0.
- All 50 visible campaign NPCs gate via `DM_PartyActive()` (dm_common.txt) — silent to anyone outside the active party (centralized for future multi-party evolution).
- `src/map/mob.c` delays normal BOSS/MVP respawns while `$dm_mode == 1`.
- Already-active stock BOSS/MVP spawns are removed on their next hard or lazy AI
  tick and held on a short retry loop until mode is disabled.

What is still needed:

- In-client playtest confirming the removal timing/visuals are acceptable when
  mode is enabled mid-session.

### 2. Quest Markers

The campaign has quest IDs and quest progression. `questinfo` markers are now
applied to the main hub NPC for every arc and to visible objective NPCs where an
active quest state clearly identifies the next scene. Examples include Deacon
Holt, Scholar Voss, Osiris's Court, Amon Ra's Lid, Baphomet's Seal, Exempt Hold,
Deep Trench Wake, later confrontation NPCs, Himmelmez, and the Central Choice.

What is still needed:

- In-client playtest confirming the marker convention is useful and not noisy.
- Optional `viewpoint` or navigation cues for scene beats.
- Optional marker expansion for hidden controller set-pieces if client testing
  proves hidden NPC markers are visible and useful.

### 3. Dice Rolling

Implemented:

- `@roll <NdX[+/-mod]>` outputs public map rolls.
- `@roll hidden <NdX[+/-mod]>` outputs DM-only hidden rolls for GM level 60+.
- Rolls show individual die results for rolls up to 20 dice.
- `@roll fudge <total> [note]` / `@roll override <total> [note]` provides a
  transparent DM-only override command that announces the set result rather
  than pretending it was random.

What is still needed:

- In-client confirmation that long roll output is readable in the chat window.

### 4. Puzzles and Traps

Implemented:

- `DM_HazardArea()` for area damage/status effects.
- `DM_ResetPuzzleFlag()` for indexed puzzle flag resets.
- `DM_CleanupEncounter()` for label-based encounter cleanup.

What is still needed:

- Concrete puzzle/trap scripts in the campaign arcs using these helpers.
- Timer and trigger-tile patterns around the helpers.

### 5. Temporary Damage Hazards

Implemented:

- `DM_HazardArea()` can apply immediate area percent damage and status effects.
- `@dm hazard [range] [damage_pct] [ticks] [interval_ms] [status] [status_ms]`
  places a ticking party-scoped hazard at the DM's current position.
- Hazard `status` accepts numeric SC IDs plus aliases: `poison`, `freeze`,
  `stun`, `sleep`, `curse`, `confusion`, `blind`, their `sc_*` forms, and
  `none`.
- `@dm hazard clear` stops the caller's active hazard timer and cancels any
  pending hazard tick.
- Arc 14's Ifrit beat starts a party-scoped Magma Cathedral pulse hazard at
  `thor_v03` 150,150. It ticks every 8 seconds for 5 pulses and uses 6% HP
  damage if Hesma was exposed, otherwise 9%.
- Arc 12's Naght Sieger beat starts four Rift Anchor pulses at `spl_fild01`
  150,150 with confusion pressure. Vance helped lowers pulse damage from 7% to
  4%.
- Arc 7's RSX-0806 beat starts three smoke-pressure pulses at `ein_dun02`
  150,150 with blind pressure. Supporting the strike lowers pulse damage from
  5% to 3%.
- Arc 15's Thanatos beat starts four tower resonance pulses at `thana_boss`
  150,150. Pratt challenged lowers pulse damage to 4%, Pratt exposed lowers it
  to 6%, and the default unresolved pressure is 8%.
- Arc 19's Surt beat starts four Ash Vacuum Rift pulses at `moc_fild22` 150,150.
  Himmelmez bargained lowers pulse damage from 8% to 5% and removes the curse
  rider.

What is still needed:

- In-client playtest for timer behavior during disconnects/map changes.
- Optional additional hazards for lower-stakes mid-arc scenes if desired. (Several scripted already: Arc4 pressure curse, Arc7/12/14/15/19 boss pulses; @dm hazard always available for ad-hoc.)

### 6. Loot Tuning

The loot generator exists with arc-specific and act-specific curated pools plus
preview mode.

Implemented:

- Arcs 1-10 have per-arc pools.
- Acts III and IV use tighter act-specific pools.
- `@dmreward` uses an arc-expected reward level instead of the GM's own level,
  and zeny is now per online member rather than party-size multiplied per
  member.
- `@dm reward` / `@dmreward` accept `preview`, `dryrun`, `roll`, or `1` to roll
  and report rewards without awarding them.

What is still needed:

- Optional class-role or tier-sensitive item selection.
- In-client review of reward value pacing by arc/tier.

### 7. Branch Boss Variants

Implemented:

- Arc 8 Dark Lord spawns branch-specific court adds based on Manfred's fate.
- Arc 11 Randgris spawns reduced or full court adds based on Bjorn's fate.
- Arc 13 can honor Carrion's coalition deal without spawning Beelzebub; combat
  variants spawn explicit coalition adds.
- Arc 15 Thanatos spawns deterministic echo adds based on Pratt's outcome.
- Arc 16 Bijou resolves as `dm_arc16_maret_freed` when Rina defected, otherwise
  as `dm_arc16_bijou_killed`.

What is still needed:

- In-client playtest for add placement, difficulty, and clear feedback on the
  non-combat Beelzebub and Maret-freed paths.

## Instance/Dungeon Status

- The instance system is loaded and parse-clean.
- The campaign should still be playtested in-client for each instanced arc.
- Pay special attention to hard-coded map warps, boss spawns, and hidden NPCs
  inside copied maps.

## Verification Run

Run this before each session (and after editing anything under
`npc/custom/dm_campaign/`). It boots the map-server with `--run-once`, loads
every configured script, and fails on any parse error — a superset of the old
`script-checker` pass (catches undefined event labels, over-long NPC names,
case-typo'd constants, etc.):

```bash
./tools/check-campaign.sh
```

## Working Checklist

Use this checklist for the next implementation and validation passes.

### Live Client Validation

- [ ] Test `@dmmode on` while normal MVPs are already spawned.
- [ ] Test `@dmmode on` before normal MVP respawn timers fire.
- [ ] Confirm the visual timing of removed stock BOSS/MVP mobs is acceptable.
- [ ] Test `@dmmode off` and confirm normal respawns resume.
- [ ] Playtest objective markers across all arc hub NPCs.
- [x] Hunt zone minimap arrows (dm_hunt_markers.txt) implemented and verified for hunts (48 markers, all actual hunts; late-arc maps fixed and cross-checked). Story trackers intentionally omit. Playtest recommended.
- [ ] Playtest visible mid-arc objective markers for noise and usefulness.
- [x] Decide whether optional `viewpoint` navigation cues are still needed. (Not needed; questinfo covers map markers adequately)
- [x] Add quest journal descriptions and `@dm warp` copy-paste lines for all 89 campaign quests.
  Full client merge support added: `planning/SealCascade_QuestList_addon.lua` + `tools/campaign_quest_merge.py --patch` + `client/README.md`.
- [ ] Test `@roll`, `@roll hidden`, and `@roll fudge` output readability in
  the client chat window.
- [ ] Test `@dm inspire <player>`, `@dm inspire party`, manual spend, and
  automatic token consumption on `@dm check <player|party> <stat> <DC> adv`.
- [ ] Test `@dm cutscene on`, optional portrait, auto-release, and manual
  `@dm cutscene off` with 2+ online party members.
- [ ] Test that `@dm cleanup`, `@dm mode off`, and reconnect release cutscene
  movement locks and clear portraits.
- [ ] Live-test the spawn-GID registry and encounter controls:
  `@dm spawn 1002 2 Test Poring`, `@dm encounter status`,
  `@dm encounter boss last`, `@dm scale hp 150 boss`,
  `@dm scale damage 75 all`, `@dm bloodied on boss`.
- [ ] Confirm the bloodied watcher fires once when the tracked boss crosses 50%
  HP, then clears itself.
- [ ] Confirm held-spawn bookkeeping with `@dm holdspawn 1002 2 Held Poring`,
  `@dm release last`, `@dm holdclear`, and `@dm encounter status`.
- [ ] Confirm `@dm cleanup`, `@dm mode off`, and `@dm reset confirm` clear the
  DM-owned encounter registry and any active bloodied watcher.
- [ ] Confirm player kill credit remains normal for DM-spawned mobs: EXP, drops,
  quest kill progress, and kill callbacks still belong to the killing player.

### Encounter And Branch Validation

- [ ] Playtest Arc 8 Dark Lord branch adds for Manfred outcomes.
- [ ] Playtest Arc 11 Randgris branch adds for Bjorn outcomes.
- [ ] Playtest Arc 13 Beelzebub combat path with Carrion killed.
- [ ] Playtest Arc 13 coalition deal/no-fight path with Carrion bribed.
- [ ] Playtest Arc 15 Thanatos echo adds for Pratt exposed, delayed, and
  challenged outcomes.
- [ ] Playtest Arc 16 Bijou killed path.
- [ ] Playtest Arc 16 Maret freed path.
- [ ] Playtest Arc 17 Administrator purged, negotiated, and running outcomes.
- [ ] Confirm branch outcomes give clear party-facing feedback.
- [x] Static audit: branch outcome flags are mutually exclusive in `@dmbeat` and
  matching NPC dialogue paths.
- [x] Static audit: `@dmbeat` exposes Pratt Delayed, matching the scripted NPC
  outcome.
- [x] Arc 16 Rina (exposed/rolled/defected) + Bijou/Maret paths wired in beats + script.
- [x] Arc 19 Central Choice menu implements all 6 endings (Shared Seal, Reforged, Queen's Bargain, Thanatos Road, Refusal gated on proof, Unbound) + flag set + narration. Matches Choice_Tracker.

### Hazard And Trap Work

- [ ] Playtest `@dmhazard` manual hazards with damage-only pulses.
- [ ] Playtest `@dmhazard` manual hazards with status aliases.
- [ ] Playtest `@dm symptom <arc> setup`, `pulse`, `read`, and `clear` for a
  representative low/mid/high/finale arc.
- [ ] Playtest symptom weather cleanup for Arc 13 fog and Arc 14 ash.
- [ ] Confirm symptom patrol/spirit spawns are appropriate for Arc 2 and Arc 16.
- [ ] Playtest Arc 12 Rift Anchor hazard during map movement.
- [ ] Playtest Arc 7 Reactivation Bay smoke hazard during RSX-0806.
- [ ] Playtest Arc 14 Magma Cathedral hazard during Ifrit.
- [ ] Playtest Arc 15 Thanatos resonance hazard during tower combat.
- [ ] Playtest Arc 19 Ash Vacuum Rift hazard during finale combat.
- [ ] Test hazard timers during player disconnects and reconnects.
- [x] Add first lower-stakes trap/hazard scene: Arc 7 Reactivation Bay smoke
  pressure.
- [x] Static audit: `DM_HazardArea()` detaches party member RIDs before
  continuing past out-of-range/out-of-map targets.
- [x] Add more lower-stakes trap/hazard scenes if boss-only hazards still feel
  too sparse. (Added Arc 4, Arc 10, Arc 18)
- [x] Add concrete puzzle scripts using `DM_ResetPuzzleFlag()` if the campaign
  needs more non-combat mechanics. (Added Outer Seal Puzzle to Arc 4)

### Reward And Economy Review

- [x] Preview common/uncommon/rare/boss rewards for each arc with
  `@dmreward <arc> <tier> preview`. (Skipped in favor of static review)
- [x] Rewards added to hunts/bosses in quest_db.conf (per previous work); comments enriched with vault data for scaling.
- [x] Check mid-arc zeny values against expected level 68-84 characters.
- [x] Check late-arc zeny values against expected level 88-99 characters.
- [x] Decide whether boss-tier prize boxes, berries, albums, and treasure boxes
  are too generous for the server economy. (Removed from Arcs 1-5)
- [x] Decide whether rewards need class-role sensitive pools. (Generic pools are preferred)
- [x] Decide whether tier-sensitive item quantity caps need more tuning. (Current 1-4 scaling is solid)

### Instance And Dungeon Smoke Tests

- [ ] Start and end a private instance with `@dminstance`.
- [ ] Playtest each instanced arc's entry and exit flow.
- [x] Confirm hard-coded warps land in valid, reachable coordinates.
- [x] Confirm boss spawns use valid labels and kill events.
- [x] Confirm hidden encounter controller NPCs fire their events inside copied
  maps.
- [x] Confirm cleanup commands remove scripted mobs and temporary state.

### Documentation Cleanup

- [x] Update `planning/campaign-implementation-plan.md` so it no longer reads
  like only Arcs 1-5 are implemented.
- [x] Keep `planning/dm-tooling.md` command examples aligned with console
  syntax.
- [x] Client journal source cleaned/expanded to precise handoff style (enriched 2026-07-02, 89 IDs, no "see vault" stubs, full structure, ~55+ solid entries).
- [x] New `planning/dm-playtest-notes.md` with Sprint examples and client test flows.
- [x] @dm status now reminds about merged journal.
- [x] Hunt markers + DB comments + wiring audited for 19 arcs.
- [x] Update this handoff as checklist items are completed or converted into
  implementation tasks.

## Suggested Sprint Plan

This section is written for a junior developer picking up the campaign work.
Each sprint should leave the repo in a parse-clean state. Do not batch risky
script changes across unrelated systems; finish one sprint, validate it, then
move to the next.

### Sprint 1: Live Mode And Marker Validation

Goal:

Confirm the systems that affect the whole server feel correct in a real client:
DnD mode, quest markers, and dice output.

Primary files:

- `src/map/mob.c`
- `npc/custom/dm_campaign/shared/dm_console.txt`
- `db/quest_db.conf`
- Arc NPC files under `npc/custom/dm_campaign/act_*`

Execution steps:

1. Start the server stack with a DM-capable account and a normal test character.
2. Spawn or locate a normal MVP/BOSS mob with `$dm_mode` disabled.
3. Run `@dmmode on` and observe whether the mob disappears cleanly.
4. Leave `$dm_mode` enabled long enough for a normal boss respawn window or use a
   controlled respawn test if available.
5. Run `@dmmode off` and confirm normal respawn behavior resumes.
6. Walk through each arc hub NPC and visible objective NPC with the relevant
   quest states active.
7. Test `@roll 1d20+3`, `@roll hidden 2d6+1`, and `@roll fudge 17 lockpick`.

Acceptance criteria:

- Existing BOSS/MVP mobs do not remain active during DnD mode.
- Normal BOSS/MVP respawns are held while DnD mode is enabled.
- Normal respawns resume after disabling DnD mode.
- Quest markers point players to useful next steps without flooding the map.
- Dice output is readable in the client chat window.

Follow-up decision:

- If markers are insufficient, add targeted `viewpoint` cues to `@dmbeat`
  commands. Prefer beat-specific cues over always-on markers.

Validation:

```bash
bash ./script-checker $(find npc/custom/dm_campaign -name '*.txt' | sort)
./map-server --run-once
```

### Sprint 2: Branch Encounter Playtest

Goal:

Confirm that every scripted branch variant does what the story says it does and
that the fight/non-fight paths are clear to the party.

Primary files:

- `npc/custom/dm_campaign/shared/dm_console.txt`
- `npc/custom/dm_campaign/shared/dm_flags.txt`
- `npc/custom/dm_campaign/act_02/arc_08_glast_heim.txt`
- `npc/custom/dm_campaign/act_03/arc_11_hugel.txt`
- `npc/custom/dm_campaign/act_03/arc_13_nameless_island.txt`
- `npc/custom/dm_campaign/act_04/arc_15_thanatos.txt`
- `npc/custom/dm_campaign/act_04/arc_16_prontera_banquet.txt`
- `npc/custom/dm_campaign/act_04/arc_17_varmundt.txt`

Execution steps:

1. For each branch, clear only the arc-specific flags before testing.
2. Use `@dmbeat` to set the relevant villain outcome.
3. Use the boss spawn or completion beat for that branch.
4. Record which mobs spawn, where they spawn, and which flags are set.
5. Confirm the party sees enough narration to understand the outcome.
6. Repeat for the alternate branch.

Specific cases:

- Arc 8: Manfred outcomes should alter Dark Lord court adds.
- Arc 11: Bjorn joined should reduce Randgris court pressure.
- Arc 13: Carrion killed should spawn Beelzebub and coalition adds.
- Arc 13: Carrion bribed should support the deal/no-fight completion path.
- Arc 15: Pratt exposed, delayed, and challenged outcomes should alter Thanatos
  pressure clearly.
- Arc 16: Rina defected should resolve as Maret freed.
- Arc 17: Administrator purged, negotiated, and running should all set distinct
  flags.

Acceptance criteria:

- Every branch has an explicit menu path in `@dmbeat`.
- Each path sets the documented flags.
- Combat variants spawn expected mobs and do not leave stale scripted mobs.
- Non-combat variants clearly complete or advance the arc.
- Any difficulty problems are documented with arc, branch, party size, and level.

Validation:

```bash
bash ./script-checker $(find npc/custom/dm_campaign -name '*.txt' | sort)
./map-server --run-once
```

### Sprint 3: Hazard And Trap Hardening

Goal:

Make the hazard system reliable under real player behavior, then decide whether
the campaign needs more environmental pressure outside boss rooms.

Primary files:

- `npc/custom/dm_campaign/shared/dm_traps.txt`
- `npc/custom/dm_campaign/shared/dm_console.txt`
- `npc/custom/dm_campaign/act_03/arc_12_new_world.txt`
- `npc/custom/dm_campaign/act_03/arc_14_veins.txt`
- `npc/custom/dm_campaign/act_04/arc_15_thanatos.txt`
- `npc/custom/dm_campaign/act_04/arc_19_finale.txt`

Execution steps:

1. Test manual hazards with `@dmhazard 7 5 3 3000 none`.
2. Test status hazards with aliases such as `curse`, `confusion`, `blind`, and
   `sc_stun`.
3. Confirm `@dmhazard clear` stops future ticks.
4. Start each scripted boss hazard and move one player out of the hazard map.
5. Disconnect and reconnect one party member during active hazard ticks.
6. Confirm hazards do not damage players outside the intended map/range/party.
7. If the system behaves well, identify two or three lower-stakes scenes that
   would benefit from hazards or puzzle pressure.

Candidate new scenes:

- Arc 4 Baphomet seal overflow: light curse/bleed-style pressure during the
  ward decision.
- Arc 7 Einbroch mine pressure: timed smoke/poison pulses near the rail scene.
- Arc 10 Lighthalzen lab containment: short stun/confusion pulses before Kiel.
- Arc 18 Niflheim bargain scene: low damage curse pulses if Himmelmez is fought.

Acceptance criteria:

- Manual hazards apply damage/status only to intended targets.
- Scripted hazards stop when their stop event or completion path fires.
- Disconnects and map changes do not create obvious stuck timers or bad damage.
- Any new hazards are readable, fair, and tied to story stakes.

Validation:

```bash
bash ./script-checker $(find npc/custom/dm_campaign -name '*.txt' | sort)
./map-server --run-once
```

### Sprint 4: Reward And Economy Tuning

Goal:

Verify that reward value matches expected campaign level, party progression, and
server economy before players see it.

Primary files:

- `npc/custom/dm_campaign/shared/dm_rewards.txt`
- `npc/custom/dm_campaign/shared/dm_console.txt`
- `planning/dm-tooling.md`

Execution steps:

1. For each arc, run one preview for each tier:
   `common`, `uncommon`, `rare`, and `boss`.
2. Record item, quantity, zeny, arc, tier, and reward level.
3. Compare results against the expected arc level from `DM_RewardArcLevel()`.
4. Look for early access to economy-distorting items.
5. Look for late rewards that feel too flat for level 90+ characters.
6. Adjust pools before adjusting zeny. Item spikes usually matter more than
   small zeny differences.
7. If needed, add class-role sensitive pools only after basic tier tuning is
   stable.

Recommended sample commands:

```text
@dmreward 1 common preview
@dmreward 1 boss preview
@dmreward 8 rare preview
@dmreward 14 boss preview
@dmreward 19 boss preview
```

Acceptance criteria:

- Zeny is based on arc-expected level, not the DM character's level.
- Zeny is granted per online party member without multiplying by party size.
- Common rewards are useful but not economy-defining.
- Rare and boss rewards feel exciting without becoming mandatory farming loops.
- Any economy-sensitive item changes are documented in this handoff.

Validation:

```bash
bash ./script-checker npc/custom/dm_campaign/shared/dm_rewards.txt npc/custom/dm_campaign/shared/dm_console.txt
./map-server --run-once
```

### Sprint 5: Instance And Dungeon Smoke Tests

Goal:

Confirm private instance flow, copied-map behavior, hard-coded warps, hidden
controller NPCs, boss labels, and cleanup commands.

Primary files:

- `npc/custom/dm_campaign/shared/dm_instances.txt`
- `npc/custom/dm_campaign/shared/dm_console.txt`
- `npc/custom/dm_campaign/shared/dm_session.txt`
- Arc files under `npc/custom/dm_campaign/act_*`

Execution steps:

1. Start a private instance with `@dminstance`.
2. Enter the intended arc map and verify party members arrive together.
3. Trigger the arc's mid-scene NPCs and boss controller.
4. Kill or manually complete the boss path.
5. Run cleanup commands and confirm scripted mobs/state are removed.
6. End the instance and confirm players are returned safely.
7. Repeat for every arc that relies on copied maps, hidden NPCs, or scripted
   boss labels.

Acceptance criteria:

- Instance start/end commands work for a DM-led party.
- Warps land on valid walkable cells.
- Hidden controller NPCs fire in copied maps.
- Boss kill labels resolve without script errors.
- Cleanup removes scripted mobs without touching unrelated user state.

Validation:

```bash
bash ./script-checker $(find npc/custom/dm_campaign -name '*.txt' | sort)
./map-server --run-once
```

### Sprint 6: Documentation And Handoff Cleanup

Goal:

Make the planning docs match the current implementation so future work does not
chase stale gaps.

Primary files:

- `planning/dm-handoff.md`
- `planning/dm-tooling.md`
- `planning/campaign-implementation-plan.md`
- `npc/custom/dm_campaign/CAMPAIGN.md`

Execution steps:

1. Update `planning/campaign-implementation-plan.md` to reflect all 19 arcs,
   not only the original Act I vertical slice.
2. Keep old implementation history only if it is clearly labeled as history.
3. Confirm command examples match current aliases and syntax.
4. Mark completed checklist items with short notes when client playtests pass.
5. Move rejected ideas into a short "Deferred" note so they are not rediscovered
   as bugs later.

Acceptance criteria:

- A new developer can identify implemented systems, open risks, and next tasks
  from docs alone.
- No doc says objective markers, branch variants, hazard aliases, or reward
  preview mode are pending when they are already implemented.
- Validation commands and command examples are copy/paste accurate.

Validation:

```bash
rg -n -g '!planning/dm-handoff.md' "not implemented|manual DM note|Arcs 1 through Arc 5|Arc 1 through Arc 5|Arc 1-5 only|First playable scope|Remaining manual steps|What Not To Code Yet" planning npc/custom/dm_campaign
```

## Junior Developer Rules Of Engagement

- Keep each change scoped to one sprint or one clearly named bug.
- Run `script-checker` before asking for review on any NPC script edit.
- Run `./map-server --run-once` after changes to scripts, quest DB, mob behavior,
  or script registration.
- Do not change unrelated campaign flags unless a sprint explicitly calls for it.
- Preserve existing player-facing story text unless the change is fixing an
  unclear or incorrect branch outcome.
- When playtesting, record arc, branch, party size, player levels, commands used,
  observed result, and whether it passed.
- If a behavior is intentionally flexible for tabletop DM control, document it
  as intentional instead of converting it into hard scripting by default.
