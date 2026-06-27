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

## What Was Fixed

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
- Branch-specific boss variants are implemented in `@dmbeat`: Dark Lord,
  Randgris, Beelzebub, Thanatos, and Bijou/Maret now use explicit adds or
  non-combat completion flags instead of old judgment-only notes.
- The beat menu exposes all currently scripted Arc 16 Rina outcomes and Arc 17
  Administrator outcomes, including `rina_rolled` and `admin_negotiated`.

## Open Work

### 1. DnD Mode Toggle

Implemented:

- `@dm mode on|off` and `@dmmode on|off` set `$dm_mode`.
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
- Optional additional hazards for lower-stakes mid-arc scenes if desired.

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

Checked with:

```bash
bash ./script-checker $(find npc/custom/dm_campaign -name '*.txt' | sort)
./map-server --run-once
```

## Working Checklist

Use this checklist for the next implementation and validation passes.

### Live Client Validation

- [ ] Test `@dmmode on` while normal MVPs are already spawned.
- [ ] Test `@dmmode on` before normal MVP respawn timers fire.
- [ ] Confirm the visual timing of removed stock BOSS/MVP mobs is acceptable.
- [ ] Test `@dmmode off` and confirm normal respawns resume.
- [ ] Playtest objective markers across all arc hub NPCs.
- [ ] Playtest visible mid-arc objective markers for noise and usefulness.
- [ ] Decide whether optional `viewpoint` navigation cues are still needed.
- [ ] Test `@roll`, `@roll hidden`, and `@roll fudge` output readability in
  the client chat window.

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

### Hazard And Trap Work

- [ ] Playtest `@dmhazard` manual hazards with damage-only pulses.
- [ ] Playtest `@dmhazard` manual hazards with status aliases.
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
- [ ] Add concrete puzzle scripts using `DM_ResetPuzzleFlag()` if the campaign
  needs more non-combat mechanics.

### Reward And Economy Review

- [ ] Preview common/uncommon/rare/boss rewards for each arc with
  `@dmreward <arc> <tier> preview`.
- [ ] Check early-arc zeny values against expected level 18-58 characters.
- [ ] Check mid-arc zeny values against expected level 68-84 characters.
- [ ] Check late-arc zeny values against expected level 88-99 characters.
- [ ] Decide whether boss-tier prize boxes, berries, albums, and treasure boxes
  are too generous for the server economy.
- [ ] Decide whether rewards need class-role sensitive pools.
- [ ] Decide whether tier-sensitive item quantity caps need more tuning.

### Instance And Dungeon Smoke Tests

- [ ] Start and end a private instance with `@dminstance`.
- [ ] Playtest each instanced arc's entry and exit flow.
- [ ] Confirm hard-coded warps land in valid, reachable coordinates.
- [ ] Confirm boss spawns use valid labels and kill events.
- [ ] Confirm hidden encounter controller NPCs fire their events inside copied
  maps.
- [ ] Confirm cleanup commands remove scripted mobs and temporary state.

### Documentation Cleanup

- [x] Update `planning/campaign-implementation-plan.md` so it no longer reads
  like only Arcs 1-5 are implemented.
- [x] Keep `planning/dm-tooling.md` command examples aligned with console
  syntax.
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
