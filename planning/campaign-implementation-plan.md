# Seal Cascade Campaign Implementation Plan

Source campaign notes:
`H:\Docs\Obsidian Notes\Game Design\Ragnarok_Online\Campaign`

This file translates the campaign overview into concrete Hercules server work.
The campaign itself remains in the Obsidian vault; the repo should contain the
runnable scripts, config, database entries, and tooling needed to play it.

## Campaign Shape

- Campaign: **The Seal Cascade**
- Structure: 4 acts, 19 arcs
- First playable scope: **Act I, Arc 1 - Omens at the Fountain**
- Gameplay loop: town hub -> guild contract -> dungeon descent -> DM-guided set-piece -> reward/state update
- Core throughline: Whisperer cult, weakening seals, recurring ally/villain flags, finale gates

## Repo Work Areas

### NPC Scripts

Create campaign scripts under:

```text
npc/custom/dm_campaign/
```

Recommended first layout:

```text
npc/custom/dm_campaign/
├── shared/
│   ├── dm_common.txt
│   ├── dm_flags.txt
│   └── dm_console.txt
└── act_01/
    ├── arc_01_prontera.txt
    ├── arc_02_payon.txt
    ├── arc_03_morroc.txt
    ├── arc_04_geffen.txt
    └── arc_05_alberta_izlude.txt
```

Register the loaded files in `npc/scripts_custom.conf`.

### Quest Database

Reserve quest IDs for campaign content:

```text
20000-20099  Act I
20100-20199  Act II
20200-20299  Act III
20300-20399  Act IV
20900-20999  shared / repeatable / debug quests
```

Use quest DB entries for visible quest log and hunting objectives. Use character
variables for story branches and campaign flags.

### Story Flags

Use persistent character/account flags for choices that matter later:

```text
dm_arc01_holt_spared
dm_arc01_refugees_helped
dm_arc01_tibbets_befriended
dm_arc01_sigil_ring_obtained
dm_mira_lives
dm_echo_trusts_party
dm_prontera_united
dm_varmundt_tools_stabilized
dm_himmelmez_bargain
```

Use global variables only for world state that should affect everyone.

### DM Controls

Start script-first, then move to C/HPM only if the script layer becomes painful.

Phase 1 DM controls:

- Hidden `DM_Console` NPC with labels for each staged event.
- Existing GM commands for `@monster`, `@hide`, `@item`, `@zeny`, `@recall`, `@broadcast`.
- Dedicated Dungeon Master group in `conf/groups.conf`.

Phase 2 DM controls:

- Custom `@dm` atcommand namespace or HPM map plugin.
- Commands for `spawn`, `story`, `reward`, `warp`, `flag`, and `session`.
- Optional web/Discord control panel only after the in-game loop works.

### Campaign Data

Use stock RO maps and monsters first. Add custom data only where the campaign
needs unique behavior.

Likely custom data:

- Symbolic quest items such as **Sigil Ring**, **Refugees' Key**, and relic fragments.
- Optional custom mobs for cultists, acolytes, and staged bosses.
- Mapflags for campaign instances: `nomemo`, `noreturn`, `nosave`, `noteleport`, `nowarp`.

## First Vertical Slice

Implement **Act I, Arc 1 - Omens at the Fountain**.

Required content:

- Quartermaster Wynne at Prontera fountain as guild handler.
- Tibbets the sluice-keeper as ally.
- Deacon Holt as human villain.
- Brother Cassell as escaping recurring foil.
- Main quest: **The Goat-Headed Sign**.
- Support quests:
  - Contract: Cellar Vermin
  - Field Contract: Rockers and Rumors
  - South Gate Soup Line
  - The Trembling Ground
- Culvert descent using existing maps first.
- Listening Chamber set-piece using an existing culvert/deep sewer map first.
- Deviruchi boss event.
- Branches:
  - Tibbets befriended -> drained chamber / easier approach.
  - Refugees helped -> fewer cult adds.
  - Holt spared -> easier boss and Arc 4 witness.
  - Holt killed -> cleaner payout but witness lost.
- Reward:
  - Sigil Ring.
  - Quest completion.
  - Story flags for later arcs.

## Recommended Build Order

1. Add campaign quest ID entries for Arc 1.
2. Add `npc/custom/dm_campaign/shared/dm_common.txt`.
3. Add Arc 1 NPC script with Wynne, Tibbets, Holt, Cassell, and Deviruchi event labels.
4. Register scripts in `npc/scripts_custom.conf`.
5. Add Dungeon Master group permissions.
6. Test script reload and server boot.
7. Play through Arc 1 with a GM account and one test character.
8. Only then expand Act I arcs 2-5.

## What Not To Code Yet

- Full 19-arc automation.
- Custom maps from scratch.
- Web DM panel.
- Discord bot.
- New C atcommands.
- Complex finale gate logic.

Those are useful later, but the first risk is whether the campaign loop feels good
inside RO. Prove that with Arc 1 before widening the surface area.
