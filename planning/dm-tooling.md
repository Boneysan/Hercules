# DM Tooling

The Seal Cascade campaign uses a script-first DM tool layer. These tools live in
`npc/custom/dm_campaign/shared/` and are loaded from `npc/scripts_custom.conf`.
They are intentionally small Hercules scripts so campaign flow can be adjusted
without recompiling the server.

## Loaded Scripts

- `dm_common.txt` - shared permission, party, map, and reward-tier helpers.
- `dm_flags.txt` - persistent campaign flag helpers and Arc 1 flag shortcuts.
- `dm_rewards.txt` - curated arc/level/tier reward generator and party delivery.
- `dm_storyteller.txt` - map and global narration helpers.
- `dm_session.txt` - encounter cleanup helpers.
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
