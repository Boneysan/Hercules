# DM Tooling

The Seal Cascade campaign uses a script-first DM tool layer. These tools live in
`npc/custom/dm_campaign/shared/` and are loaded from `npc/scripts_custom.conf`.
They are intentionally small Hercules scripts so campaign flow can be adjusted
without recompiling the server.

## Loaded Scripts

- `dm_common.txt` - shared permission, party, map, reward-tier, and party-warp helpers.
- `dm_flags.txt` - persistent campaign flag helpers and Arc 1-19 flag shortcuts.
- `dm_rewards.txt` - curated arc/level/tier reward generator and party delivery.
- `dm_storyteller.txt` - map and global narration helpers.
- `dm_session.txt` - encounter cleanup helpers.
- `dm_quests.txt` - party-wide quest set/complete/erase plus party/instance story flag wrappers.
- `dm_instances.txt` - script-driven private dungeon instances (create/attach/init/warp/destroy; no instance_db needed).
- `dm_console.txt` - GM-facing bound commands.
- `dm_traps.txt` - reusable hazard, puzzle reset, and encounter cleanup helpers.
- `dm_beats.txt` - `@dmbeat` director for all 19 arcs.
- `dm_handbook.txt` - `@dmguide` cue cards.
- `dm_hunts.txt` - generated hunt table (do not hand-edit; `tools/gen-hunts.py`).
- `dm_encounters.txt` - named encounter composer, formations, party add-count scaling, budget readout, stealth.
- `dm_mobstats.txt` - generated HP/EHP/DPS lookup (`tools/gen-encounter-stats.py`).
- `dm_checks.txt` - `@check` / `@assist` / `@dm check` skill checks.
- `dm_mapflags.txt` - nowarp/noteleport/nomemo on set-piece maps.

Designer-facing palette (which tool to pick when writing a scene, including the damage-taken knob for high-level sprites):
[design/dm-tools-for-encounters.md](design/dm-tools-for-encounters.md).

## GM Commands

All commands require GM level 60 or higher.

```text
@dm help
@dm mode <on|off>
@dmmode <on|off>
@dm reward [arc] [common|uncommon|rare|boss] [preview|dryrun|1]
@dmreward [arc] [common|uncommon|rare|boss] [preview|dryrun|1]
@dm flag <get|set|clear|arc01..arc19|cleararc01..cleararc19> [name] [value]
@dmflag <get|set|clear|arc01..arc19|cleararc01..cleararc19> [name] [value]
@dm quest <start|complete|erase> <quest_id>
@dmquest <start|complete|erase> <quest_id>
@dm beat
@dmbeat
@dmguide
@dmguide 1
@dm story <message>
@dmstory <message>
@dm globalstory <message>
@dm spawn <mob_id> [count] [name]
@dm hazard [range] [damage_pct] [ticks] [interval_ms] [status] [status_ms]
@dm hazard clear
@dmhazard [range] [damage_pct] [ticks] [interval_ms] [status] [status_ms]
@dmhazard clear
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
@dm exp <base> [job]
@dmexp <base> [job]
@dm status
@dmstatus
@dm reset confirm
@dmreset confirm
@dmenc list | info <name> | spawn <name> [ambush|line|scatter]
@dm stealth [dc]
@dm wake
@dm check <player|me|party> <tag|stat> <dc> [dm_flag]
@dmcheck <player|me|party> <tag|stat> <dc> [dm_flag]
@dm stakes <success> | <failure>
@dmstakes <success> | <failure>
@check <tag|stat> <dc>
@assist <player> <tag>
@roll [hidden] <NdX[+/-mod]>
@roll fudge <total> [note]
@roll override <total> [note]
```

`@check` and `@assist` are player-facing (GM level 0). Everything else in this list is GM 60+ except `@roll` (public; `@roll hidden` / fudge / override are DM-only).

`@dm mode on` does two things: suppresses normal BOSS/MVP spawns server-wide, and
stores the DM's current party ID in `$dm_active_party`. All 49 visible campaign
NPCs gate on both `$dm_mode` and party membership — they are silent to any player
not in the active party, even while a session is running. `@dm mode off` clears
both `$dm_mode` and `$dm_active_party`, returning all NPCs to silent for everyone.
Already-active stock BOSS/MVP spawns are removed on their next hard or lazy AI
tick and held on a short retry loop until mode is disabled.

### Implementation pitfall (`callsub` + `.@atcmd_parameters$`)

`bindatcmd` fills **scope** vars `.@atcmd_parameters$` / `.@atcmd_numparameters`.
**`callsub` / `callfunc` start a new `.@` scope**, so those arrays are empty
inside `S_*` labels unless you bridge them first.

`dm_console.txt` copies into character temps before every param-using `callsub`:

```text
deletearray @dm_atcmd_p$[0], 128;
copyarray @dm_atcmd_p$[0], .@atcmd_parameters$[0], .@atcmd_numparameters;
@dm_atcmd_n = .@atcmd_numparameters;
```

`S_Mode` / `S_Reward` / … read `@dm_atcmd_p$`, not `.@atcmd_parameters$`.

If a rebuild or rewrite drops that bridge, `@dm mode on` reports
**“Mode is currently OFF”** even when the command was sent correctly.

Full symptom matrix (client `0x017F` silence, reload steps, regression test):
**[dm-mode-troubleshooting.md](dm-mode-troubleshooting.md)**.

`@roll` is public map output for players and DMs, including individual dice for
rolls up to 20 dice. `@roll hidden` requires GM level 60+ and reports only to
the roller. `@roll fudge` / `@roll override` are transparent DM-only set-result
commands; they announce that the result was set rather than rolled.

Players can also roll from a GUI: the **Dice Roller** window in Korangar
(**Ctrl+D**, or Menu → Dice Roller) sends these same `@roll` commands — standard
dice, common combos, a custom `NdX+mod` field, and a GM-only Hidden toggle. See
`korangar/docs/dice-roller-window.md`.

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

`@dmbeat` with no argument opens the full Act → Arc → Beat director. `@dmbeat
<1-19>` jumps **straight into that arc's beat submenu** (`OnBeat` parses the
numeric arg and calls `DM_BeatArcNN` directly, skipping the Act/Arc navigation).

`@dmguide` opens the private in-game GM Handbook. `@dmguide <1-19>` jumps to an
arc guide. Arc 1 currently has the complete cue-card vertical slice: scene
purpose, NPC performance notes, suggested play/checks, party-state summary,
prepared read-aloud, and a safe handoff to the authoritative Beat Director.
Browsing never changes state. Only the clearly labelled `SEND read-aloud`
choice broadcasts text to the current map.
The client **Beats tab** (GM/DM panel) uses this: one button per arc, grouped by
act. Invalid/out-of-range arg falls back to the full menu.

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

Examples:

```text
@dmreward 1 common 1
@dmreward 12 rare preview
@dmreward 1 boss
@dm reward 1 rare
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
```

Arc helper shortcuts currently available:

- `@dmflag arc01` through `@dmflag arc19`
- `@dmflag cleararc01` through `@dmflag cleararc19`

Generic `@dmflag set` and `@dmflag clear` are party-scoped through
`DM_InstanceSetFlag` / `DM_InstanceClearFlag`.

## Story And Encounter Tools

Use `@dmstory` or `@dm story` for map-local narration. Use
`@dm globalstory` only for campaign-wide beats.

Use `@dm spawn` for quick live pacing near the GM's current position. More
specific arc encounter staging should live in per-arc scripts or `@dmbeat`
variants so branch behavior remains repeatable.

Use `@dmcleanup` to remove monsters spawned with the DM console labels from the
current map. It does **not** kill story-script labels such as
`Deacon Holt#dm::OnDeviruchiDead`. Those need `DM_CleanupEncounter` or a spawn
wired to `DM_Console::OnDMKilled`.

### Named encounters and live budget

`@dmenc list` / `info` / `spawn` is the composer in `dm_encounters.txt`. Packs
have an elite, minions, and optional caster; minion **count** scales with
`DM_PartyOnlineCount()`. `@dmenc info` prints time-to-die against the party
standing there, using `DM_MobStat` (regenerate with
`./tools/gen-encounter-stats.py`). Formations: `ambush`, `line`, `scatter`.

`@dm stealth [dc]` (default 15) strips `MD_AGGRESSIVE|MD_DETECTOR` on the map,
the party rolls AGI, and the outcome wakes none / one / all. `@dm wake`
restores stored modes.

### Dialing a high-level sprite (damage knob)

`DM_EncTune` / `DM_EncMonster` wrap the engine knobs. `@dmenc spawn` and
`@dm spawn` auto-tune. Re-dial live with:

```text
@dmenc tune              // party average (excluding the DM), 100%
@dmenc tune 18           // force level 18
@dmenc tune 18 70        // mercy / easier
@dm tune 30 130          // same, from @dm
```

`DM_EncPartyLevel` skips GM 60+ so a level-99 DM in the party does not inflate
the target. `DM_EncTuneTarget(<expected>)` then clamps around the scene's
contract (expected−8 … expected+15).

Story set-pieces should call `DM_EncMonster` with the iconic stock id
(Deviruchi 1109, Baphomet, Tao, …) rather than adding a `mob_db2` clone.
Full recipe: [design/dm-tools-for-encounters.md](design/dm-tools-for-encounters.md).

### Checks

`@check <tag|stat> <dc>` and `@assist <player> <tag>` are for players.
`@dm check` calls one on a name, `me`, or `party`, and may set a `dm_*` flag
on success. `@dm stakes` announces success/failure lines first. Maths and tags:
[skill-checks-and-encounters.md](skill-checks-and-encounters.md).

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
./map-server --run-once
```

A full `map-server --run-once` startup parse should load every `dm_campaign`
script from `npc/scripts_custom.conf` and all campaign quest IDs from
`db/quest_db.conf`. The default `s1/p1` inter-server credential warning is
expected in the local dev database until those credentials are changed.
