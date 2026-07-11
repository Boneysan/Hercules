# Seal Cascade Campaign Implementation Plan

Source campaign notes:
`H:\Docs\Obsidian Notes\Game Design\Ragnarok_Online\Campaign`

This file describes the current Hercules implementation plan for the Seal
Cascade campaign. The Obsidian vault remains the source for long-form story
notes; this repo contains the runnable scripts, database entries, server hooks,
and DM tooling needed to play it.

## Campaign Shape

- Campaign: **The Seal Cascade**
- Structure: 4 acts, 19 arcs
- Runtime model: script-first, DM-guided campaign flow
- Gameplay loop: town hub -> guild contracts -> dungeon or field set-piece ->
  DM beat or scripted boss -> reward/state update
- Core throughline: weakening seals, recurring ally/villain flags, scripted
  branch callbacks, finale gates

## Current Implementation

The campaign is implemented under:

```text
npc/custom/dm_campaign/
├── shared/
│   ├── dm_common.txt
│   ├── dm_console.txt
│   ├── dm_flags.txt
│   ├── dm_instances.txt
│   ├── dm_quests.txt
│   ├── dm_rewards.txt
│   ├── dm_session.txt
│   ├── dm_storyteller.txt
│   └── dm_traps.txt
├── act_01/
├── act_02/
├── act_03/
└── act_04/
```

All 19 arc scripts are registered in `npc/scripts_custom.conf`.

Quest IDs are loaded in `db/quest_db.conf`:

- `20001-20030`: Act I, Arcs 1-5
- `20101-20144`: Act II, Arcs 6-10
- `20151-20185`: Act III, Arcs 11-14
- `20191-20233`: Act IV, Arcs 15-19

The campaign reference in `npc/custom/dm_campaign/CAMPAIGN.md` is the best
single-file overview of arc titles, quest IDs, bosses, flags, and cross-arc
dependencies.

## Runtime Systems

### Party-Safe Quest And Flag Flow

Campaign scripts should not call `setquest`, `completequest`, `erasequest`, or
direct story-flag assignments for party-facing progression. Use the shared
wrappers instead:

```text
DM_InstanceQuestStart(<quest_id>)
DM_InstanceQuestComplete(<quest_id>)
DM_InstanceQuestErase(<quest_id>)
DM_InstanceSetFlag("<flag_name>", <value>)
DM_InstanceClearFlag("<flag_name>")
```

These helpers update every online member of the caller's party and safely fall
back to solo behavior when needed.

### DM Console

The in-game DM layer is script-first and exposed through GM level 60 commands:

- `@dm` / shortcut commands for mode, reward, flag, quest, beat, story, spawn,
  hazard, cleanup, warp, recall, and instance control
- `@dmbeat` menus for all 19 arcs
- `@dmflag arc01` through `@dmflag arc19` plus matching clear shortcuts
- `@roll`, `@roll hidden`, `@roll fudge`, and `@roll override`

Use `planning/dm-tooling.md` for command syntax and examples.

### DnD Mode

`@dm mode on` / `@dmmode on` enables `$dm_mode`. While enabled, normal BOSS/MVP
respawns are held, and already-active stock BOSS/MVP mobs are removed on their
next AI tick. This keeps DM-run campaign boss scenes from being disrupted by
normal world spawns.

### Quest Markers

Quest markers are implemented for every arc hub NPC and visible mid-arc
objective NPC/set-piece where the active quest state clearly indicates the next
scene. Hidden controller NPCs are intentionally not marked unless client testing
proves hidden markers are useful.

### Rewards

`dm_rewards.txt` provides curated arc/tier reward pools and per-member zeny.
Rewards use an arc-expected reward level instead of the DM character's level.
`@dmreward <arc> <tier> preview` rolls without awarding, which is the expected
tool for economy review.

### Hazards And Traps

`dm_traps.txt` provides reusable primitives:

```text
DM_HazardArea("<map>", x, y, range, hp_percent_loss, status_type, status_duration{, party_id})
DM_ResetPuzzleFlag("<flag_prefix>", count)
DM_CleanupEncounter("<label>", "<map>")
```

`@dmhazard` provides manual ticking hazards. Scripted encounter hazards exist in
Arc 12, Arc 14, Arc 15, and Arc 19.

### Instances

`dm_instances.txt` provides script-driven private dungeon instances without
requiring `instance_db` entries. Campaign set-pieces work best inside instances
when scripts use `strnpcinfo(NPC_MAP)` for local spawns and announcements.

## Arc Coverage

| Act | Arcs | Status |
| --- | --- | --- |
| I | 1-5 | Scripted hub NPCs, support quests, branch flags, set-pieces, rewards |
| II | 6-10 | Scripted hub NPCs, hunts, branch beats, MVP encounters |
| III | 11-14 | Scripted co-seal villains, branch variants, MVP encounters, hazards |
| IV | 15-19 | Scripted finale chain, branch callbacks, hazards, finale endings |

Notable branch variants already converted from manual notes into explicit beat
paths:

- Arc 8 Dark Lord adds react to Manfred outcomes.
- Arc 11 Randgris court adds react to Bjorn outcomes.
- Arc 13 supports both Beelzebub combat and Carrion coalition deal/no-fight.
- Arc 15 Thanatos echo adds react to Pratt outcomes.
- Arc 16 resolves Bijou/Maret based on Rina's outcome.
- Arc 17 exposes Administrator purged, negotiated, and running outcomes.

## Deferred Or Optional Work

These are not parse blockers. Treat them as product/experience work:

- Live-client validation of `@dmmode` visual timing and respawn behavior.
- Live-client validation of quest marker usefulness and noise level.
- Optional `viewpoint` navigation cues if markers are insufficient.
- In-client review of `@roll` output readability.
- In-client playtest of branch encounter difficulty and non-combat feedback.
- In-client playtest of hazards during map changes and disconnects.
- Reward economy review across all arcs and tiers.
- Optional lower-stakes hazards or puzzle scripts outside boss arenas.
- Full instance smoke tests across copied maps, hidden controllers, warps, boss
  labels, and cleanup.

The current working backlog for these items lives in
`planning/dm-handoff.md`.

## Cross-Project Client Improvement: WASD Movement

Korangar owns implementation of camera-relative WASD character movement; see
`korangar/docs/FEATURE_ROADMAP.md` and
`korangar/docs/plans/modern-mechanics.md`. Hercules remains authoritative for
walkability and movement validation, so this server project owns the live
compatibility pass.

Planned acceptance work:

- [ ] Verify `Click`, `WASD`, and `Both` modes against `PACKETVER=20220406`.
- [ ] Confirm held keys and diagonals do not trigger movement packet flood or
  anti-cheat behavior.
- [ ] Test walls, narrow corners, rapid reversals, map changes, and latency for
  rubber-banding.
- [ ] Confirm chat/NPC text focus prevents unintended movement.
- [ ] Confirm NPC interaction, item pickup, melee chase, skills, hazards, and
  campaign instances still behave normally.
- [ ] Run a 30-minute mixed click/WASD campaign session with no disconnect or
  path desynchronization.

No Hercules protocol change is expected for the MVP. Any server change must be
justified by live evidence rather than client prediction.

## Cross-Project Aspirational Improvement: Campaign Lighting

Korangar owns rendering and interpolation; Hercules owns permission,
campaign-state integration, and recoverable scene intent. The desired DM flow
is preview -> send/activate -> visible acknowledgement -> restore/cleanup.

Planned server responsibilities:

- [ ] Define a small scene-light vocabulary (baseline, dim, cold, ritual,
  hazard pulse, blackout, boss, victory) rather than exposing raw shader values
  through atcommands.
- [ ] Add private preview/status controls and explicit party-visible activation.
- [ ] Associate optional lighting cues with selected `dm_story_beat` entries
  without making lighting required for quest progression.
- [ ] Ensure cleanup, DnD mode off, instance end, map change, and reconnect can
  restore or reconstruct the correct state.
- [ ] Keep non-Korangar clients playable; lighting cues enhance presentation but
  never carry essential mechanics or hidden-only information.
- [ ] Use structured script feedback first; add a custom packet/plugin only when
  the vertical slice proves chat transport cannot represent state safely.

## Validation

Run script validation after NPC script changes:

```bash
bash ./script-checker $(find npc/custom/dm_campaign -name '*.txt' | sort)
```

Run a full startup parse after script, quest DB, registration, or map-server
behavior changes:

```bash
./map-server --run-once
```

For docs-only changes, no script validation is required.

## Historical Note

This plan originally started as an Act I / Arc 1 prototype proposal. That stage
is complete. Treat the current 19-arc campaign surface as authoritative.
