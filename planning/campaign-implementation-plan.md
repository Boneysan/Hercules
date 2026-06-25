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

## Implementation Status

### Done (committed/working-tree)
- **Shared DM tooling** — `npc/custom/dm_campaign/shared/` (console, flags, rewards,
  storyteller, session, common). `@dm` commands gated to GM level 60.
- **Arc 1 vertical slice** — `npc/custom/dm_campaign/act_01/arc_01_prontera.txt`:
  - Quartermaster Wynne (fountain) — swearing-in with noble/pragmatic/aggressive
    branch (`dm_arc01_hero_type`), contracts 20002/20003, gates main quest 20005.
  - Frightened Mother (south gate) — *The Trembling Ground* (20004); protect-vs-report
    fork sets `dm_arc01_refugees_helped`.
  - Tibbets the Keeper (Culvert) — three doors; kind/proven path sets
    `dm_arc01_tibbets_befriended` (tide-wheel key → fewer adds).
  - Deacon Holt (`prt_sewb4`, the Listening Chamber) — cutscene + Cassell escape +
    Sigil Ring grant; spare/kill fork (mercy only if refugees helped); spawns the
    **Deviruchi** MVP with cult-familiar adds that scale down with mercy/ally choices.
    On boss death: completes 20005, EXP burst, "the seals are weakening" beat.
- **Quest DB** — `db/quest_db.conf` entries 20001-20006 (range 20000-20099 reserved).
- **Sigil Ring** — `db/item_db2.conf` Id 50001 (`Sigil_Ring`, IT_ETC, untradeable token).
- **Dungeon Master group** — `conf/groups.conf` id 5, level 60, inherits Event Manager
  + Law Enforcement (spawn/warp/hide/recall/item/zeny/broadcast), `can_trade` re-enabled.
- **Registration** — `npc/scripts_custom.conf` loads the Arc 1 script.
- **Validation** — `bash ./script-checker <files>` passes (note: the checker needs
  **bash**, not sh — line 49 uses `[[`).

### Remaining manual steps (need a running stack / Windows client)
1. **Start MariaDB** (`sudo service mariadb start`) — map-server connects to the DB
   *before* loading scripts/DBs, so a full boot-parse needs it up. Then run
   `./run-servers.sh` and confirm map-server loads quest_db/item_db2/groups/Arc 1
   with no warnings.
2. **Client itemInfo** — add a Sigil Ring (50001) entry to the client's
   `itemInfo.lub` so it displays in-game (server-side it already works).
3. **GM playthrough** — make a DM-group (or Admin) character, run the loop:
   Wynne → contracts → Tibbets → (`@warp prt_sewb4`) → Holt → Deviruchi → reward.
   Use `@dmflag arc01` to inspect flags and `@dmflag cleararc01` to retest branches.

### Backend helpers added (closing earlier gaps)
- **Party-wide quest credit** - `dm_quests.txt` (`DM_PartyQuestComplete/Set/Erase`);
  `OnDeviruchiDead` now credits the whole online party, not just the killer.
- **Private dungeon instances** - `dm_instances.txt` (`DM_InstanceStart/End`),
  exposed as `@dm instance start <map>/end`. Script-driven; no instance_db needed.
- **Party warp tooling** - `DM_WarpParty` + `@dm warp <map>` / `@dm recall`.
- **Party-wide EXP** - `DM_PartyExp(base, job{, party_id{, dryrun}})` in
  `dm_rewards.txt`; the Arc 1 boss EXP burst now credits the whole party.
- **Themed loot** - `dm_rewards.txt` pools rewritten from legacy numeric IDs to
  readable, server-verified AegisName constants (potions -> ores -> prize boxes).
- Arc 1's Listening Chamber is now map-relative (`strnpcinfo(NPC_MAP)`), so it runs
  standalone on `prt_sewb4` *or* inside a `@dm instance` copy.

### Known slice-level simplifications
- Holt's chamber re-triggers per-character until 20005 is complete; concurrent
  re-trigger is blocked by an NPC `.boss_up` guard (single-party assumption).
- The Trembling Ground "search" is narrated, not combat-tracked (table-style).
