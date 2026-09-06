# DM tools for story and encounters

**Date:** 2026-09-06  
**Status:** Inventory of what is already loaded. Use this when writing or rewriting an arc.  
**Operator reference:** [dm-tooling.md](../dm-tooling.md)  
**Checks / composer detail:** [skill-checks-and-encounters.md](../skill-checks-and-encounters.md)

Do not invent a new combat system, a new mob database row, or a new HUD just because the stock monster is the wrong level. The campaign already has a DM layer. Design the **scene**, then pick tools from this list to stage, dial, and recover it.

## Design rule

**Keep the iconic sprite. Dial the unit.**

Holt’s Deviruchi, Voss’s Moonlight Flower, Baphomet, Tao Gunka, Dark Lord, Randgris, Ifrit, Thanatos, Surt — those names and looks are the scene. Their `mob_db` level is not a story requirement. Spawn the stock id, then tune **that GID**.

| What you need | Tool | Built? |
|---|---|---|
| Party cannot chew the HP | `UDT_DAMAGE_TAKEN_RATE` via `DM_EncTune` — 100 is default; **above 100** dies faster | **Yes** |
| Party gets one-shot | `UDT_ATKMIN/MAX`, `UDT_MATKMIN/MAX` (skills use MATK too) | **Yes** (same wrapper) |
| They cannot hit / always miss | `UDT_HIT`, `UDT_FLEE`, `UDT_DEF`, `UDT_MDEF` | **Yes** (same wrapper) |
| Nameplate level | `UDT_LEVEL` | **Yes** |
| Match the people in the room | `DM_EncPartyLevel` (skips GM 60+), `DM_EncTuneTarget` | **Yes** |
| Named pack (elite + minions + caster) | `@dmenc spawn <name> [ambush\|line\|scatter]` (auto-tunes) | Yes |
| Price it against *this* party | `@dmenc info <name>` → `DM_EncBudget` + tune target | Yes |
| Live re-dial | `@dmenc tune [level] [percent]` / `@dm tune` | **Yes** |
| Mercy / drain / extra prep | Same spawn, `percent` 70 or 130 | **Yes** |
| Pressure without a second boss | `@dm hazard` / `DM_HazardArea` percent HP + status, optional save | Yes |
| Notice / sneak | `@dm stealth [dc]` / `@dm wake` | Yes |
| Private copy of the map | `@dm instance start <map>` | Yes |

**Not a combat knob:** `@dm hazard … [damage_pct]` is a ticking **percent-HP pulse** on the party, not a modifier to monster damage.

Wrapper (built): `DM_EncTune(<gid>, <target_level>{, <percent>})`. Story scripts should call `DM_EncMonster(...)` instead of raw `monster()`. `@dmenc spawn` and `@dm spawn` auto-tune. `@dmenc tune [level] [percent]` re-dials every mob on the current map.

## Command surface (loaded)

GM 60+ unless noted. All live in `npc/custom/dm_campaign/shared/dm_console.txt`.

### Session

| Command | Use in a scene |
|---|---|
| `@dm mode on\|off` | Start/stop the campaign session; holds stock BOSS/MVP respawns |
| `@dm status` | See arc/quest/flag snapshot |
| `@dm reset confirm` | Wipe campaign state (destructive) |
| `@dmguide` / `@dmguide <1-19>` | Handbook; Arc 1 has the cue-card slice. Browsing does not mutate |

### Stage the room

| Command | Use in a scene |
|---|---|
| `@dm warp <map> [x] [y]` | Party to the set-piece |
| `@dm recall` | Pull party to the DM |
| `@dm instance start <map> [x] [y]` / `end` | Private copy; scripts must spawn on `strnpcinfo(NPC_MAP)` |
| `@dm story <text>` | Map narration |
| `@dm globalstory <text>` | Campaign-wide line (rare) |
| `@dmbeat` / `@dmbeat <1-19>` | Warp, flags, quests, scripted boss spawn, hazards |

### Encounters

| Command | Use in a scene |
|---|---|
| `@dmenc list` | Named packs + intended level |
| `@dmenc info <name>` | Composition, scaled add count, **time-to-die vs the standing party** |
| `@dmenc spawn <name> [ambush\|line\|scatter]` | Drop the pack at the DM’s feet, auto-tuned; wired to `@dm cleanup` |
| `@dmenc tune [level] [percent]` | Re-dial every mob on this map (default: party level, 100%) |
| `@dm spawn <id> [count] [name]` | One-off mob, auto-tuned, same cleanup label |
| `@dm cleanup` | Kills `DM_Console::OnDMKilled\|OnDMBossKilled\|OnDMCleanup` only — **not** Holt/Voss/Baphomet labels |
| `@dm stealth [dc]` / `@dm wake` | Strip aggro/detector, AGI check, wake some or all |

Named packs today (`DM_EncTable` intended level):

| Name | For ~level | Composition |
|---|---|---|
| `sewer_ambush` | 30 | Deviruchi + Tarou |
| `cult_diggers` | 75 | Ancient Mummy + Zerom |
| `gh_crypt` | 100 | Bloody Knight + Wraith |
| `gh_patrol` | 110 | Khalitzburg + Raydric + Wraith |
| `lab_security` | 115 | Alicel + Aliot + Aliza |
| `abbey_choir` | 125 | Necromancer + Zombie Slaughter + Banshee |
| `thor_wardens` | 130 | Kasa + Magmaring + Imp |
| `valkyrie_court` | 130 | Skeggiold + Skogul |

If the story wants “Deviruchi in the Culvert” at Arc 1 (expected reward level **18**), spawn 1109 (or `sewer_ambush`) and **tune**, do not pick a different monster because 1109 is lv 93.

### Checks (player-facing too)

| Command | Who | Use in a scene |
|---|---|---|
| `@check <tag\|stat> <dc>` | anyone | Own roll |
| `@assist <player> <tag>` | anyone | Help, +2, cap +4 |
| `@dm check <player\|me\|party> <tag> <dc> [dm_flag]` | DM | Call it; optional party flag on success |
| `@dm stakes <success> \| <failure>` | DM | Announce the price first |
| `@roll` / `@roll hidden` / `@roll fudge` | mixed | Dice; Korangar Ctrl+D |

Tags (approach picks the stat — no CHA): `force`/`intimidate`, `stealth`/`reflex`, `endure`/`resist`, `arcana`/`lore`/`medicine`, `perceive`/`traps`/`craft`/`deceive`, `haggle`/`charm`/`omen`, or raw `str`…`luk`. DC 10 easy / 15 medium / 20 hard.

A roll must change server state: flag, add count, hazard save, HP, or which door opens. Narration-only rolls are out.

### Hazards and puzzles

| Tool | Use in a scene |
|---|---|
| `@dm hazard [range] [damage_pct] [ticks] [interval] [status] [status_ms]` | Live pressure at the DM’s feet |
| `@dm hazard clear` | Stop it |
| `DM_HazardArea(...)` | Scripted pulse; optional save tag + DC halves damage and skips status |
| `DM_ResetPuzzleFlag("<prefix>", n)` | Glyph / sequence reset |

Status aliases: poison, freeze, stun, sleep, curse, confusion, blind, none.

Already used: Arc 4 vault, 7 smoke, 10 lab, 12 rift, 14 magma, 15 resonance, 18 curse, 19 ash vacuum. Branch flags already change pulse **percent** (Vance helped 4 vs 7, Hesma exposed 6 vs 9, etc.). That is the pattern for “this choice made the fight easier” — do not also swap the boss id.

### Story state

| Command / helper | Use |
|---|---|
| `@dmflag get\|set\|clear` / `arcNN` / `cleararcNN` | Inspect/repair |
| `@dmquest start\|complete\|erase <id>` | 20001–20233, party-wide |
| `DM_InstanceQuestStart/Complete/Erase` | Scripts — never raw `setquest` for party story |
| `DM_InstanceSetFlag` / `ClearFlag` | Scripts — never raw `set dm_…` for party story |
| `DM_ClaimGrant("<key>")` | Exactly-once EXP/item |
| `@dmreward <arc> <tier> [preview]` | Curated loot at **arc expected level**, not the DM’s level |
| `@dm exp <base> [job]` | Manual EXP |

`DM_RewardArcLevel`: Arc 1=18, 2=28, 3=38, 4=48, 5=58, then 68…99.

## Script helpers to call from an NPC, not only the DM

When the **script** runs the set-piece (Holt, Voss, Baphomet), it should use the same primitives the DM would:

1. `strnpcinfo(NPC_MAP)` for spawn/announce (instance-safe).
2. `strnpcinfo(NPC_NAME)+"::OnBossDead"` for the death event (instance-safe). Do not hard-code `Deacon Holt#dm::…`.
3. GID from `monster(...)` when amount is 1, then `setunitdata` / future `DM_EncTune`.
4. Adds on `DM_Console::OnDMKilled` **or** the same unique NPC label, so `@dm cleanup` or `DM_CleanupEncounter` can take them.
5. `DM_EncScale` for party size.
6. `DM_HazardArea` for pressure; pass a save tag if the party can brace.
7. `DM_ClaimGrant` + `DM_PartyExp` on the real owner party, not `DM_SessionParty()` at death.
8. Branch: add count, hazard percent, `UDT_DAMAGE_TAKEN_RATE`, ATK/MATK — not a second mob class.

## How a high-level story boss should be written

Example — Arc 1 Listening Chamber (stock Deviruchi 1109, reward level 18):

```text
.@self$ = strnpcinfo(NPC_NAME);
.@pct = 100;
if (dm_arc01_holt_spared)
	.@pct = 70;
callfunc("DM_EncMonster", .@map$, x, y, "Deviruchi", DEVIRUCHI,
	.@self$ + "::OnDeviruchiDead", 18, .@pct, 1, 0);
```

`DM_EncTuneTarget(18)` uses the online party’s average level, **excluding GM 60+**, floored near 18 so a brand-new party is not under-tuned and capped so one overlevelled friend does not turn Holt into a mid-game boss. Mercy passes 70.

Live rehearsal: `@dmenc info sewer_ambush` prints the tune target. `@dmenc spawn sewer_ambush` then `@dmenc tune 18 70` to re-dial.

Live rehearsal: `@dmenc info sewer_ambush` with the actual four players standing there. If time-to-die is 3s, raise the rate or drop ATK. If it is 90s, lower the rate. Record the numbers in the arc’s playtest notes.

The same recipe applies to Moonlight (1150), Osiris (1038), Amon Ra (1511), Baphomet (1039), Tao Gunka (1583), and every `@dmbeat` “Spawn \<Boss\>” in Acts II–IV.

## Gaps (do not pretend these exist)

| Missing | Until it exists |
|---|---|
| `@dmcleanup` sweeping leftover story labels on older arcs | Act I set-pieces now use `strnpcinfo(NPC_NAME)`; Acts II–IV beat spawns still use source names |
| `DM_EncTune` on Act II–IV `@dmbeat` spawns | Call `DM_EncMonster` the same way as Act I |
| Scene claim / exclusive dialogue | Still to build (Act I plan Slice 0) |
| Downed / `OnPCDieEvent` | Not built |
| Client DM panel “damage slider” | Use `@dmenc tune`; Korangar has Bestiary + Loot, not a live tuner |

## Loaded shared scripts

`dm_common`, `dm_flags`, `dm_quests`, `dm_rewards`, `dm_storyteller`, `dm_session`, `dm_instances`, `dm_console`, `dm_traps`, `dm_beats`, `dm_handbook`, `dm_hunts`, `dm_encounters`, `dm_mobstats` (generated), `dm_checks`, `dm_mapflags`.
