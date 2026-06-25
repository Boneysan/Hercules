# DM Tooling

The Seal Cascade campaign uses a script-first DM tool layer. These tools live in
`npc/custom/dm_campaign/shared/` and are loaded from `npc/scripts_custom.conf`.
They are intentionally small Hercules scripts so campaign flow can be adjusted
without recompiling the server.

## Loaded Scripts

- `dm_common.txt` - shared permission, party, map, reward-tier, and party-warp helpers.
- `dm_flags.txt` - persistent campaign flag helpers and Arc 1 flag shortcuts.
- `dm_rewards.txt` - curated arc/level/tier reward generator and party delivery.
- `dm_storyteller.txt` - map and global narration helpers.
- `dm_session.txt` - encounter cleanup helpers.
- `dm_quests.txt` - party-wide quest set/complete/erase (credits the whole party, not just the killer).
- `dm_instances.txt` - script-driven private dungeon instances (create/attach/init/warp/destroy; no instance_db needed).
- `dm_console.txt` - GM-facing bound commands.

## GM Commands

All commands require GM level 60 or higher.

```text
@dm help
@dm reward [arc] [common|uncommon|rare|boss] [dryrun]
@dmreward [arc] [common|uncommon|rare|boss] [dryrun]
@dm flag <get|set|clear|arc01|cleararc01> [name] [value]
@dmflag <get|set|clear|arc01|cleararc01> [name] [value]
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
@dmflag cleararc01
```

Arc 1 helper flags currently tracked:

- `dm_arc01_started`
- `dm_arc01_tibbets_befriended`
- `dm_arc01_refugees_helped`
- `dm_arc01_holt_spared`
- `dm_arc01_holt_killed`
- `dm_arc01_sigil_ring_obtained`
- `dm_mira_lives`

## Story And Encounter Tools

Use `@dmstory` or `@dm story` for map-local narration. Use
`@dm globalstory` only for campaign-wide beats.

Use `@dm spawn` for quick live pacing near the GM's current position. More
specific arc encounter staging should live in per-arc scripts once those arcs
exist.

Use `@dmcleanup` to remove monsters spawned with the DM console labels from the
current map.

## Validation

The scripts were checked with:

```bash
bash ./script-checker npc/custom/dm_campaign/shared/dm_common.txt npc/custom/dm_campaign/shared/dm_flags.txt npc/custom/dm_campaign/shared/dm_rewards.txt npc/custom/dm_campaign/shared/dm_storyteller.txt npc/custom/dm_campaign/shared/dm_session.txt npc/custom/dm_campaign/shared/dm_console.txt
```

A short `map-server` startup parse also loaded every `dm_campaign/shared` script
from `npc/scripts_custom.conf`. Running `map-server` alone reports a char-server
connection error, which is expected unless the full server stack is running.
