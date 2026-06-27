# DM Tooling

The Seal Cascade campaign uses a script-first DM tool layer. These tools live in
`npc/custom/dm_campaign/shared/` and are loaded from `npc/scripts_custom.conf`.
They are intentionally small Hercules scripts so campaign flow can be adjusted
without recompiling the server.

## Loaded Scripts

- `dm_common.txt` - shared permission, party, map, reward-tier, and party-warp helpers.
- `dm_flags.txt` - persistent campaign flag helpers and Arc 1-5 flag shortcuts.
- `dm_rewards.txt` - curated arc/level/tier reward generator and party delivery.
- `dm_storyteller.txt` - map and global narration helpers.
- `dm_session.txt` - encounter cleanup helpers.
- `dm_quests.txt` - party-wide quest set/complete/erase plus party/instance story flag wrappers.
- `dm_instances.txt` - script-driven private dungeon instances (create/attach/init/warp/destroy; no instance_db needed).
- `dm_console.txt` - GM-facing bound commands.

## GM Commands

All commands require GM level 60 or higher.

```text
@dm help
@dm reward [arc] [common|uncommon|rare|boss] [dryrun]
@dmreward [arc] [common|uncommon|rare|boss] [dryrun]
@dm flag <get|set|clear|arc01|cleararc01|arc02|cleararc02|arc03|cleararc03|arc04|cleararc04|arc05|cleararc05> [name] [value]
@dmflag <get|set|clear|arc01|cleararc01|arc02|cleararc02|arc03|cleararc03|arc04|cleararc04|arc05|cleararc05> [name] [value]
@dm quest <start|complete|erase> <quest_id>
@dmquest <start|complete|erase> <quest_id>
@dm beat
@dmbeat
@dm story <message>
@dmstory <message>
@dm globalstory <message>
@dm spawn <mob_id> [count] [name]
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
```

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

`@dmbeat` has matching menus for Arc 1 through Arc 5. Each menu can warp the
current party to the relevant NPC/location, start or complete the arc quests, set
branch flags, announce story text, and write `dm_story_beat`.

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

- Arc 1 has its own early-game loot pools.
- Other arcs fall back to level-band pools.
- Reward tiers are `common`, `uncommon`, `rare`, and `boss`.
- Rewards include both item rolls and zeny.
- Party rewards are delivered to online party members when the GM has a party;
  otherwise the attached GM/test character receives the reward.
- Passing `dryrun` as `1` rolls and reports the reward without giving it.
- `DM_PartyExp(base, job{, party_id{, dryrun}})` grants base/job EXP to every
  online party member (used by the Arc 1 boss-death burst).

Examples:

```text
@dmreward 1 common 1
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

- `@dmflag arc01` / `@dmflag cleararc01`
- `@dmflag arc02` / `@dmflag cleararc02`
- `@dmflag arc03` / `@dmflag cleararc03`
- `@dmflag arc04` / `@dmflag cleararc04`
- `@dmflag arc05` / `@dmflag cleararc05`

Generic `@dmflag set` and `@dmflag clear` are party-scoped through
`DM_InstanceSetFlag` / `DM_InstanceClearFlag`.

## Story And Encounter Tools

Use `@dmstory` or `@dm story` for map-local narration. Use
`@dm globalstory` only for campaign-wide beats.

Use `@dm spawn` for quick live pacing near the GM's current position. More
specific arc encounter staging should live in per-arc scripts once those arcs
exist.

Use `@dmcleanup` to remove monsters spawned with the DM console labels from the
current map.

## Act I Quick Test Path

Use the beat director for a fast smoke test of the whole playable Act I surface:

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
```

For a real playthrough, use the NPC conversations and hunting objectives instead
of jumping straight to completion. The beat director exists so the DM can recover,
branch, or stage a scene quickly during live play.

## Validation

The scripts were checked with:

```bash
bash ./script-checker npc/custom/dm_campaign/shared/dm_common.txt npc/custom/dm_campaign/shared/dm_flags.txt npc/custom/dm_campaign/shared/dm_rewards.txt npc/custom/dm_campaign/shared/dm_storyteller.txt npc/custom/dm_campaign/shared/dm_session.txt npc/custom/dm_campaign/shared/dm_quests.txt npc/custom/dm_campaign/shared/dm_instances.txt npc/custom/dm_campaign/shared/dm_console.txt npc/custom/dm_campaign/act_01/arc_01_prontera.txt npc/custom/dm_campaign/act_01/arc_02_payon.txt npc/custom/dm_campaign/act_01/arc_03_morroc.txt npc/custom/dm_campaign/act_01/arc_04_geffen.txt npc/custom/dm_campaign/act_01/arc_05_alberta_izlude.txt
```

A full `map-server --run-once` startup parse should load every `dm_campaign`
script from `npc/scripts_custom.conf` and all campaign quest IDs from
`db/quest_db.conf`. The default `s1/p1` inter-server credential warning is
expected in the local dev database until those credentials are changed.
