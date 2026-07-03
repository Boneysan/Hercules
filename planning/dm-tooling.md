# DM Tooling

The Seal Cascade campaign uses a script-first DM tool layer. These tools live in
`npc/custom/dm_campaign/shared/` and are loaded from `npc/scripts_custom.conf`.
They are intentionally small Hercules scripts so campaign flow can be adjusted
without recompiling the server.

## Loaded Scripts

- `dm_common.txt` - shared permission, party, map, reward-tier, party-warp helpers, and `DM_PartyActive()` gate (single source of truth for session visibility).
- `dm_flags.txt` - persistent campaign flag helpers and Arc 1-19 flag shortcuts.
- `dm_rewards.txt` - curated arc/level/tier reward generator and party delivery.
- `dm_storyteller.txt` - map and global narration helpers.
- `dm_session.txt` - encounter cleanup helpers.
- `dm_quests.txt` - party-wide quest set/complete/erase plus party/instance story flag wrappers.
- `dm_instances.txt` - script-driven private dungeon instances (create/attach/init/warp/destroy; no instance_db needed).
- `dm_console.txt` - GM-facing bound commands.
- `dm_voice.txt` - improvised attributed dialogue and NPC puppet voice helpers.
- `dm_checks.txt` - d20 stat checks and saving throws for live table play.
- `dm_scene.txt` - weather/BGM/portrait scenes and cutscene movement locks.
- `dm_combat.txt` - spawn-GID registry, live HP/damage scaling, and bloodied callouts.
- `dm_traps.txt` - reusable hazard, puzzle reset, encounter cleanup, and @dm trap (latent save traps; MVP surface + stub wired, core watcher in progress per guide).
- `dm_symptoms.txt` - Obsidian-sourced per-arc symptom pulses and boss
  read-aloud helpers.
- `dm_onboarding.txt` - novice-start campaign guide NPCs that can warp new players
  from the starting boat/island/Izlude arrival path to the Prontera Session Board.
- `dm_hunt_markers.txt` - 45 invisible marker NPCs placed at monster spawn zones
  for every hunt quest across Arcs 1–19. Show yellow minimap arrows while the
  player has the matching hunt quest active and is on the same map.

## GM Commands

All commands require the Dungeon Master group (id 5, group level 1+; assigned
by `tools/promote-dm.sh`). The gate is `DM_RequireDM` in `dm_common.txt`.

```text
@dm help
@dm mode <on|off>
@dmmode <on|off>
@dm reward [arc] [common|uncommon|rare|boss] [preview|dryrun|1]
@dmreward [arc] [common|uncommon|rare|boss] [preview|dryrun|1]
@dm flag <get|set|clear|sync> [name] [value]
@dm flag <arc01..arc19|cleararc01..cleararc19>
@dmflag <get|set|clear|sync> [name] [value]
@dmflag <arc01..arc19|cleararc01..cleararc19>
@dm quest <start|complete|erase> <quest_id>
@dmquest <start|complete|erase> <quest_id>
@dm beat
@dmbeat
@dm story <message>
@dmstory <message>
@dm globalstory <message>
@dm spawn <mob_id> [count] [name]
@dm holdspawn <mob_id> [count] [name]
@dm release [all|last]
@dm holdclear
@dm encounter [status|clear|kill|boss <last|gid>]
@dmencounter [status|clear|kill|boss <last|gid>]
@dm scale <hp|damage> <percent> [all|boss|last|gid]
@dmscale <hp|damage> <percent> [all|boss|last|gid]
@dm bloodied <on|off|status> [boss|last|gid]
@dmbloodied <on|off|status> [boss|last|gid]
@dm hazard [range] [damage_pct] [ticks] [interval_ms] [status] [status_ms]
@dm hazard clear
@dmhazard [range] [damage_pct] [ticks] [interval_ms] [status] [status_ms]
@dmhazard clear
@dm symptom <arc> [pulse|setup|read|clear]
@dmsymptom <arc> [pulse|setup|read|clear]
@dm exprate <percent|off|status>
@dmexprate <percent|off|status>
@dm levels
@dmlevels
@dm cleanup
@dmcleanup
@dm warp <map> [x] [y]
@dmwarp <map> [x] [y]
@dm recall
@dmrecall
@dm instance start <source_map> [x] [y] [label]
@dm instance end
@dminstance start <source_map> [x] [y] [label]
@dminstance end
@dm novice
@dmnovice
@dm resetstat
@dmresetstat
@dm resetskill
@dmresetskill
@roll [hidden] <NdX[+/-mod]>
@roll fudge <total> [note]
@roll override <total> [note]
@dm say <speaker> | <text>
@dm say @<npcname> <text>
@dmsay <speaker> | <text>
@dm secret <player> <text>
@dmsecret <player> <text>
@dm check <player|party> <str|agi|vit|int|dex|luk> <DC> [adv|dis]
@dmcheck <player|party> <stat> <DC> [adv|dis]
@dm inspire <player> [+n|spend|clear|set n]
@dm inspire party
@dminspire <player> [+n|spend|clear|set n]
@dm scene <clear|dread|boss|calm|holy|ruin|snow|fest> [portrait]
@dm scene weather <fog|snow|sakura|leaves|clouds|clouds2|fireworks|none> [portrait]
@dmscene <preset|weather ...> [portrait]
@dm cutscene <on|off> [portrait] [seconds]
@dmcutscene <on|off> [portrait] [seconds]
```

## Live-table tools (dm_voice / dm_checks / dm_scene / dm_combat)

The "live-table" layer supports improvised DM play alongside the scripted
campaign. See `planning/dm-live-table.md` for the full roadmap.

- `@dm say` voices attributed dialogue over the DM (`unittalk`) or puppets a named
  on-map NPC (`npctalk`), so lines can be improvised instead of pre-scripted.
- `@dm secret <player> <text>` sends a styled private message only to one player
  (e.g. "_The DM leans in to you..._") for table secrets the rest should not hear.
- `@dm check` rolls a d20 plus an RO-native `stat/10` modifier against a DC for one
  player or the whole party, announcing pass/fail to the map. Nat-20 always
  succeeds, nat-1 always fails; `adv`/`dis` roll twice. If the target has
  `dm_inspiration`, rolling with `adv` consumes one token automatically.
- `@dm inspire` grants, spends, clears, sets, or lists per-character Inspiration
  tokens. `@dm inspire party` lists current tokens for online party members.
- `@dm scene` sets mood on the DM's map: weather (map-wide mapflags), a custom BGM
  track (`playbgmall`), and an optional party-wide illustration (`cutin`). Preset
  BGM/illustration files are custom client assets — see the asset manifest in
  `planning/dm-live-table.md`. This client cannot stop a BGM from script, so
  `@dm scene clear` clears weather and portrait only.
- `@dm cutscene` freezes party movement with `setpcblock(PCBLOCK_MOVE)`, optionally
  shows a party-wide portrait, and auto-releases after 60 seconds by default.
  `@dm cutscene off`, `@dm cleanup`, `@dm mode off`, `@dm reset confirm`, and
  reconnect all release the movement lock and clear the cutin.
- `@dm spawn` and `@dm holdspawn` register each spawned monster GID on the DM
  character who issued the command. `@dm encounter status` lists live tracked
  GIDs, HP, mob IDs, held status, and the current boss pointer.
- `@dm scale hp 150 boss` adjusts tracked monsters' max/current HP from their
  original spawned baseline while preserving the current HP ratio. `@dm scale
  damage 75 all` scales `UDT_ATKMIN`/`UDT_ATKMAX` from the same baseline.
- `@dm bloodied on boss` arms a one-shot 50% HP watcher for the boss/last/GID
  target. It announces to the DM's current map and clears itself after firing.
- `@dm symptom <arc> pulse` converts the updated Obsidian "MVP Encounter &
  Symptom Mechanics" notes into an RO-native live effect near the DM: checks,
  hazard/status pulses, fog/ash weather, or patrol/spirit spawns depending on
  the arc. `setup` announces the tabletop rule without applying effects, `read`
  prints concise boss read-aloud lines, and `clear` removes symptom weather.
- `@dm trap` (surface + stub) places latent position-watched traps using AGI
  saves via DM_RollCheck; full spring/disarm in progress.

`@dm mode on` does two things: suppresses normal BOSS/MVP spawns server-wide, and
stores the DM's current party ID in `$dm_active_party`. All 50 visible campaign
NPCs gate on both `$dm_mode` and party membership — they are silent to any player
not in the active party, even while a session is running. `@dm mode off` clears
both `$dm_mode` and `$dm_active_party`, returning all NPCs to silent for everyone.
Already-active stock BOSS/MVP spawns are removed on their next hard or lazy AI
tick and held on a short retry loop until mode is disabled.

`@dm mode on` also starts session marker quest `20000` for the active party. Visible
campaign NPCs use that quest to show yellow quest markers while the session is
active, so players in the party can identify campaign NPCs even when a specific
arc objective marker is not currently pointing at them. `@dm mode off` and
`@dm reset confirm` erase quest `20000`, clearing the session markers.

New characters still start on the stock novice boat (`iz_int`). Campaign Guide
NPCs are placed at `iz_int`, `int_land`, and the Izlude arrival point, including
their duplicate map variants. They are marked for Novices and let campaign
players either warp directly to the Prontera Session Board or open navigation to
it, while leaving the standard training route untouched.

`@roll` is public map output for players and DMs, including individual dice for
rolls up to 20 dice. `@roll hidden` requires the DM group and reports only to
the roller. `@roll fudge` / `@roll override` are transparent DM-only set-result
commands; they announce that the result was set rather than rolled.

## New Player Setup

`@dm novice` / `@dmnovice` grants First Aid (`NV_FIRSTAID`) and Play Dead
(`NV_TRICKDEAD`) to the GM and every online party member, then erases the
10 Novice Tutorial quest flags (7117–7127) so the game no longer gates those
skills behind the tutorial chain. Call this once after creating new characters
so players skip the opening tutorial without losing the two skills.

## Stat and Skill Reset

`@dm resetstat` / `@dmresetstat` resets all distributed stat points for every
online party member, returning them to zero-spent so they can be reallocated.
`@dm resetskill` / `@dmresetskill` does the same for skill points. Both commands
apply party-wide and report how many members were reset. If the GM has no party,
only the GM character is reset.

## Hunt Zone Markers

`dm_hunt_markers.txt` places 45 invisible (sprite -1) NPC markers on the maps
where hunt quest targets spawn. Each marker uses `questinfo QTYPE_QUEST2` +
`setquestinfo QINFO_QUEST` to show a yellow arrow on the minimap **only while
the player has the matching quest active and is standing on the same map as the
marker**. Players will not see the arrow on the world map or from another map —
they need to travel to the field/dungeon first.

The hunt quest journal also has a Navigate button that uses the `MobId` from
`db/quest_db.conf` to route the player to a known spawn map. Use Navigate from
the quest journal to cross maps, then follow the yellow minimap arrow once
inside.

## Quest Journal Descriptions

All 89 campaign quest entries (IDs 20000–20234) are maintained in source form:

- `planning/campaign_quest_journal_entries.lua`
- Ready-to-merge `planning/SealCascade_QuestList_addon.lua`
- Merge helper: `python3 tools/campaign_quest_merge.py --patch ...`

Copy the QuestList blocks into your decompiled `/client/System/OngoingQuestInfoList_True_EN.lub` (or equivalent). Each entry includes:

- 2–3 lines of flavor text.
- `Location: <Map Name> (<map_id>)` — the primary hunt or scene map.
- `Mob: <Name> x<Count> (Lv XX)` for hunt quests, or `Boss: ...` for boss fights.
- `Hunt:   @dm warp <map> x y` — DM copy-paste warp to the monster zone.
- `Return: @dm warp <hub> x y` — DM copy-paste warp back to the quest-turn-in NPC.
- A one-line Summary.

For story (non-hunt) quests the warp block is a single `Warp:` line to the
next scene location. The file uses latin-1 encoding and CRLF line endings;
save it with those settings when editing or the client will reject it.

## Live Questline Flow

The campaign is wired around scripted quest-giver NPCs plus a manual beat
director. A live session can be run in either direction:

- Send the party to the scripted NPC and let dialogue drive the quest state.
- Use `@dmbeat` to pick an arc beat, warp the party, and apply the same quest/flag
  changes from a GM menu.

The important rule for campaign scripts is: **do not call `setquest`,
`completequest`, `erasequest`, or direct story-flag assignment for party-facing
questlines.** Use the party/instance wrappers instead:

```text
DM_InstanceQuestStart(<quest_id>)
DM_InstanceQuestComplete(<quest_id>)
DM_InstanceQuestErase(<quest_id>)
DM_InstanceSetFlag("<flag_name>", <value>)
DM_InstanceClearFlag("<flag_name>")
```

Those wrappers update every online member of the caller's party and safely fall
back to solo behavior when the caller is not in a party. This is what lets a DM
spawn or stage an NPC for one group without advancing unrelated players.

Current scripted arc entry points:

| Arc | Hub NPC | Main set-piece | Quest IDs |
| --- | --- | --- | --- |
| 1 | Quartermaster Wynne, Prontera | Deacon Holt / Deviruchi, `prt_sewb4` | 20001-20006 |
| 2 | Sun-Hwa, Payon | Scholar Voss / Moonlight Flower, `pay_dun04` | 20007-20012 |
| 3 | Rashid, Morroc | Amon Ra's Lid, `moc_pryd06` | 20013-20018 |
| 4 | Apprentice Elsbeth, Geffen | Baphomet's Seal, `gef_dun02` | 20019-20024 |
| 5 | Captain Mara, Alberta | Deep Trench Wake / Tao Gunka, `tur_dun04` | 20025-20030 |
| 6 | Vahl, Yuno | Mistress, `mjolnir_04` | 20101-20105 |
| 7 | Foreman Jori, Einbroch | RSX-0806, `ein_dun02` | 20111-20115 |
| 8 | Sister Margot, Glast Heim | Dark Lord, `gl_chyard` | 20121-20124 |
| 9 | Sister Ilya, Rachel | Gloom Under Night, `ra_san05` | 20131-20134 |
| 10 | Doctor Reuter, Lighthalzen | Kiel D-01, `kh_dun02` | 20141-20144 |
| 11 | Priest Eadric, Hugel | Randgris, `abyss_03` | 20151-20155 |
| 12 | Quartermaster Lian, New World | Naght Sieger, `spl_fild01` | 20161-20165 |
| 13 | Scholar Nadir, Nameless Island | Beelzebub / coalition deal, `abbey03` | 20171-20175 |
| 14 | Foreman Dunmar, Veins | Ifrit / Magma Cathedral, `thor_v03` | 20181-20185 |
| 15 | Keeper Lysandra, Aldebaran | Thanatos Memory, `thana_boss` | 20191-20194 |
| 16 | Kronecker G Heine, Prontera | Prison Vault / Bijou-Maret, `prt_q` | 20201-20204 |
| 17 | Doctor Mira Tressa, Biolabs | Biosphere Core / Amdarais, `ba_pw03` | 20211-20214 |
| 18 | The Familiar Dead, Niflheim | Himmelmez choice, `nif_in` | 20221-20223 |
| 19 | Loki The Voice, Morroc Ruins | Surt / Central Choice, `moc_fild22` | 20231-20233 |

`@dmbeat` has matching menus for Arc 1 through Arc 19. Each menu can warp the
current party to the relevant NPC/location, start or complete arc quests, set
branch flags, announce story text, spawn scripted bosses, start scripted
hazards, and write `dm_story_beat`.

## Party Warp And Instances

`@dm warp` moves the GM's whole online party to a map (random cell if no x/y
given); `@dm recall` pulls the party to the GM's current position. Both fall
back to moving only the GM if they are not in a party.

`@dm instance start <source_map>` gives the party a private copy of that map and
warps them in. One live instance per party is tracked in `$dm_inst_<party_id>`;
`@dm instance end` tears it down. Instances time out after 1h alive / 10m idle.
Because `instance_init` copies the source map's NPCs into the private copy,
campaign set-pieces work inside instances **as long as their scripts spawn and
announce against `strnpcinfo(NPC_MAP)`** rather than a hard-coded map name (the
Arc 1 Listening Chamber does this).

Example - run the Arc 1 climax as a private instance of the deep Culvert:

```text
@dm instance start prt_sewb4 103 100
... party fights Deacon Holt / Deviruchi in their own copy ...
@dm instance end
```

## Reward Generator

`dm_rewards.txt` rolls from curated pools instead of the full item database. This
keeps rewards level-appropriate and campaign-themed.

Current behavior:

- Arcs 1-10 have per-arc pools; Acts III and IV use tighter act-specific pools.
- Unknown arcs still fall back to level-band pools.
- `@dmreward` uses an arc-expected reward level for zeny instead of the GM's
  character level, so low arcs do not overpay when tested by a high-level DM.
- Reward tiers are `common`, `uncommon`, `rare`, and `boss`.
- Rewards include both item rolls and zeny.
- Zeny is awarded per online member. It is not multiplied by party size before
  being handed to every member.
- Party rewards are delivered to online party members when the GM has a party;
  otherwise the attached GM/test character receives the reward.
- Passing `preview`, `dryrun`, `roll`, or `1` rolls and reports the reward
  without giving it.
- `DM_PartyExp(base, job{, party_id{, dryrun}})` grants base/job EXP to every
  online party member (used by the Arc 1 boss-death burst).
- `@dm exprate <percent>` / `@dmexprate <percent>` sets a monster/MVP EXP
  multiplier for the GM's current party. Use `100` for normal, `200` for 2x,
  `500` for 5x. The command is party-scoped, temporary, and reset by
  `@dm exprate off`, `@dm mode off`, or `@dm reset confirm`. It does not
  multiply explicit quest/script rewards such as `@dm exp`.
- Deploying changes to this multiplier requires rebuilding and restarting the
  `map-server` process because the actual EXP hook is in `src/map/pc.c`.
- `@dm levels` / `@dmlevels` prints the arc target finish levels in-game. These
  are reward-scaling targets, not level requirements to start an arc.

Target finish / reward levels:

| Arc | Level | Arc | Level | Arc | Level | Arc | Level |
| --- | ---: | --- | ---: | --- | ---: | --- | ---: |
| 1 | 18 | 6 | 68 | 11 | 88 | 16 | 96 |
| 2 | 28 | 7 | 72 | 12 | 90 | 17 | 97 |
| 3 | 38 | 8 | 76 | 13 | 92 | 18 | 98 |
| 4 | 48 | 9 | 80 | 14 | 94 | 19 | 99 |
| 5 | 58 | 10 | 84 | 15 | 95 |  |  |

Examples:

```text
@dmreward 1 common 1
@dmreward 12 rare preview
@dmreward 1 boss
@dm reward 1 rare
@dm exprate 200
@dm exprate off
```

## Flag Tools

Flags are ordinary persistent Hercules character variables. The helpers make it
fast to inspect and repair campaign state during live testing.

Examples:

```text
@dmflag set dm_arc01_holt_spared 1
@dmflag get dm_arc01_holt_spared
@dmflag arc01
@dmflag arc05
@dmflag cleararc01
@dmflag sync Alice
```

Arc helper shortcuts currently available:

- `@dmflag arc01` through `@dmflag arc19`
- `@dmflag cleararc01` through `@dmflag cleararc19`

Generic `@dmflag set`, `@dmflag clear`, and arc clears are party-scoped through
the online members of the DM's current party. `@dmflag sync <player>` copies
every registered story flag from that online party member to the other online
party members; use it when someone missed a session.

## Story And Encounter Tools

Use `@dmstory` or `@dm story` for map-local narration. Use
`@dm globalstory` only for campaign-wide beats.

Use `@dm spawn` for quick live pacing near the GM's current position. More
specific arc encounter staging should live in per-arc scripts or `@dmbeat`
variants so branch behavior remains repeatable.

Use `@dm encounter status` after `@dm spawn` / `@dm holdspawn` to see the live
spawn-GID registry. `@dm encounter boss last` marks the latest tracked mob as the
boss target for `@dm scale ... boss` and `@dm bloodied on boss`; a numeric GID can
be supplied instead.

Use `@dmcleanup` to remove monsters spawned with the DM console labels from the
current map. Cleanup, `@dm mode off`, and `@dm reset confirm` also clear the
DM-owned encounter registry and any active bloodied watcher.

### Live Encounter Test Script

Run this in a real client with a DM-capable character. Use a harmless low-level
mob first so the HP/damage changes are easy to observe.

```text
@dm spawn 1002 2 Test Poring
@dm encounter status
@dm encounter boss last
@dm scale hp 150 boss
@dm scale damage 75 all
@dm bloodied on boss
```

Fight the marked boss until it crosses 50% HP and confirm the map receives the
one-shot bloodied announcement. Then run:

```text
@dm bloodied status
@dm encounter status
@dm holdspawn 1002 2 Held Poring
@dm encounter status
@dm release last
@dm encounter status
@dm holdclear
@dm encounter status
@dm cleanup
@dm encounter status
```

Expected result: normal and held spawns both show GIDs, released mobs lose their
`held` tag, `holdclear` forgets staged mobs, and cleanup clears the registry and
watcher. Player kill credit should remain normal because the registry is only DM
bookkeeping.

## Trap And Hazard Helpers

Shared helpers in `dm_traps.txt` are script-facing primitives for future
encounters:

```text
DM_HazardArea("<map>", x, y, range, hp_percent_loss, status_type, status_duration{, party_id})
DM_ResetPuzzleFlag("<flag_prefix>", count)
DM_CleanupEncounter("<label>", "<map>")
```

`@dm hazard` places a ticking party-scoped hazard at the DM's current position.
Defaults are range 3, 0% HP damage, 3 ticks, and 3000ms between ticks. Range is
capped at 20, ticks at 60, and interval has a 1000ms floor. `@dm hazard clear`
stops the caller's active hazard timer and cancels any pending hazard tick. The
hazard is pinned to the DM's party when placed, so later party changes do not
retarget it.

The optional `status` argument accepts either a numeric SC ID or one of these
aliases: `poison`, `freeze`, `stun`, `sleep`, `curse`, `confusion`, `blind`,
`none`. The matching `sc_*` forms also work, for example `sc_poison`.

`DM_HazardArea` applies immediate percent HP loss and/or a status effect to the
caller's party members in range, and is used by the ticking command above.
Scripted arc hazards currently use it in Arc 4's Vault Seal Pressure, Arc 7's
Reactivation Bay, Arc 10's Kiel Core Pressure, Arc 12's Rift Anchor, Arc 14's
Magma Cathedral, Arc 15's Thanatos Memory, Arc 18's Himmelmez Pressure, and
Arc 19's Ash Vacuum Rift.

## Campaign Quick Test Path

Use the beat director for a fast smoke test of the campaign surface. The menu is
organized by act, then arc:

```text
@dmbeat
  Act I / Arc 1 - Prontera -> Beat: Wynne starts contracts
  Act I / Arc 1 - Prontera -> Beat: Complete Arc 1
  Act I / Arc 2 - Payon -> Beat: Sun-Hwa starts contracts
  Act I / Arc 2 - Payon -> Beat: Complete Arc 2
  Act I / Arc 3 - Morroc -> Beat: Rashid starts contracts
  Act I / Arc 3 - Morroc -> Beat: Complete Arc 3
  Act I / Arc 4 - Geffen -> Beat: Elsbeth starts contracts
  Act I / Arc 4 - Geffen -> Beat: Complete Arc 4
  Act I / Arc 5 - Alberta -> Beat: Mara starts contracts
  Act I / Arc 5 - Alberta -> Beat: Complete Act I
  Act II / Arc 6 - Yuno -> Beat: Start Arc 6
  Act II / Arc 10 - Lighthalzen -> Beat: Kiel slain (Act II Complete)
  Act III / Arc 12 - New World -> Beat: Spawn Naght Sieger
  Act III / Arc 14 - Veins -> Beat: Ifrit slain (Act III Complete)
  Act IV / Arc 15 - Thanatos -> Beat: Spawn Thanatos
  Act IV / Arc 19 - Finale -> Beat: Campaign Complete
```

For a real playthrough, use the NPC conversations and hunting objectives instead
of jumping straight to completion. The beat director exists so the DM can recover,
branch, or stage a scene quickly during live play.

## Validation

The scripts were checked with:

```bash
bash ./script-checker $(find npc/custom/dm_campaign -name '*.txt' | sort)
git diff --check
./map-server --run-once
```

A full `map-server --run-once` startup parse should load every `dm_campaign`
script from `npc/scripts_custom.conf` and all campaign quest IDs from
`db/quest_db.conf`. The default `s1/p1` inter-server credential warning is
expected in the local dev database until those credentials are changed.

July 1, 2026 local validation: `script-checker` and `git diff --check` passed.
`map-server --run-once` could not complete because local MySQL was not reachable
at `127.0.0.1:3306`; run the Live Encounter Test Script above in a real client
once the server stack is available.
