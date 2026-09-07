# Act I implementation plan

**Date:** 2026-09-06  
**Status:** Ready to implement. No campaign scripts changed by this plan.  
**Companions:**
- [Act-by-act designer handoff](seal-cascade-act-redesign.md) — story/activity briefs for all 19 arcs
- [Arc 1 deep review](arc-01-deep-review.md) — confirmed script defects for Prontera
- [DM tools for story and encounters](dm-tools-for-encounters.md) — existing composer, damage-taken knob, checks, hazards; dial stock sprites instead of forking mob_db
- [Current implementation](../campaign-implementation-plan.md) — what is running today

This is the missing Act I delivery document. The redesign says what players should do. The deep review says what is broken in Arc 1. This file says **what to build, in what order, against which IDs**, so Arc 1 can be the reference slice for the rest of the campaign.

## What is already decided

Keep the Seal Cascade story, cast, maps, and five ending concepts. Change the **activities**: investigate, operate, rescue, and negotiate in the world; let dialogue interpret what already happened. Do not add new map art, escort AI, voting, or a cinematic system.

**Playtest target:** four regular players plus a live DM, mixed RO familiarity, laptop UI, ~60–90 minutes per normal arc. Tune combat to the party's real level and gear. The DM character's level is irrelevant.

**Act I player promise:** “The small people we help change what happens under the city.”  
Teach one new interaction per arc. At least one noncombat contribution exists for every party composition. Optional hunts never gate the story scene.

## Current Act I vs intended

| Arc | Today | Intended |
|---|---|---|
| 1 Prontera | Both hunts mandatory; child “rescued” by talking twice; drain/key promised but not implemented; stock lv93 Deviruchi; 20001 never completes | Investigate clues → optional drain/binding → chamber scene; hunts optional; dedicated encounter; complete 20001+20005 |
| 2 Payon | Both hunts gate the grove; lanterns and graves resolve in the same conversation; 20007 never completes | Inspect memorials, match a name, operate conduits, then restore or burn |
| 3 Morroc | Three hunts gate Osiris/Amon; Sabra choice is a dialogue menu; 20013 never completes | Survey a relief route, deliver through checkpoints, then tomb |
| 4 Geffen | Three hunts gate the vault; glyphs exist but are an unexplained sequence and still sit behind hunts; 20019 does complete | Diagnose three glyphs, commit a configuration, defend it |
| 5 Alberta | Ferry/diver “rescues” are menus after hunt turn-ins; 20025 does complete | Two ferry departures and two diver sites; hunts optional |

Shared defects that repeat in every Act I set-piece (Holt, Voss, Osiris/Amon, Baphomet, Tao):

- Death events use the **source NPC name**, so an instanced copy can credit the public map.
- `'boss_up` is checked on entry and set after several `next()` pages.
- `@dm cleanup` only kills `DM_Console::OnDM*` labels. Act I bosses are not on those labels.
- Ownership is read from the **current** DM session at death, not from spawn.

## Locked decisions

1. **Executable scripts win** over `CAMPAIGN.md`. Update the reference as part of delivery; do not delete working content to match stale titles (“Broken Gate”, “no MVP”).
2. **Preserve quest IDs** when the promise is the same. Do not silently turn a completed hunt ID into unfinished required content.
3. **Assign 20006** to the child/soup-line discovery. It is currently reserved and unused.
4. **Canonical story state is flags + quests.** The Sigil Ring item is a per-character token reconciled from `dm_arc01_sigil_ring_obtained`.
5. **Commit fate at resolution**, not during the conversation that starts the fight.
6. **Questions do not mutate.** Every consequential `select` has a “We need to discuss this” / “Later” exit.
7. **Peaceful and combat resolutions pay the same base story EXP.** Optional bounties are extra.
8. **Coordinates in this plan are candidates.** Walkability and warp checks are mandatory before merge. Do not treat Holt `prt_sewb4,103,100` as a safe staging cell just because it is in bounds.
9. **Group voting is out of scope.** First delivery: party-visible proposal, discuss-exit, exclusive scene claim, DM repair. Explicit DM-confirm UI is SC-02 and can follow Arc 1.
10. **Encounter tools are the difficulty layer.** Stock sprites plus `UDT_DAMAGE_TAKEN_RATE`, ATK/MATK, add count, `@dmenc`, and hazards. See [dm-tools-for-encounters.md](dm-tools-for-encounters.md). A new mob id is last resort.

## Delivery order

Do not start Arc 2 until Arc 1’s lifecycle tests pass. Shared helpers land first so later arcs do not copy Holt’s bugs.

| Slice | Tickets | Gate |
|---|---|---|
| 0 | A1-S0 scene claim, instance callbacks, encounter record, cleanup without victory, canonical arc-complete | Two-client source/instance lifecycle on a throwaway or Arc 1 prototype |
| 1 | A1-S1 hunt ungate + encounter level contract + truthful mercy | Fresh regular-player party reaches Holt without Vocal dolls or GM items |
| 2 | A1-01 Prontera interactions (child, clues, drain, binding, debrief) | Instructions match world actions; optional content never forces Holt dead |
| 3 | A1-S2 ring repair, EXP split, DM beat parity, Session Board | Replay/reconnect/assisted snapshots converge |
| 4 | A1-02 Payon | Same lifecycle helpers; memorials/conduits exist |
| 5 | A1-03 Morroc | Relief route exists; Arc 5 can read `relief_secured` |
| 6 | A1-04 Geffen | Glyph diagnosis is the main path; hunts optional |
| 7 | A1-05 Alberta | Ferry/diver sites exist; `dm_act01_complete` set once |
| 8 | Docs + `CAMPAIGN.md` + journal copy | Reference matches scripts |

P0 items from later acts (Carrion / ending guards) stay on the campaign-wide list. They are not required to playtest Act I.

---

## Slice 0 — shared helpers

New code belongs in `npc/custom/dm_campaign/shared/`. Arc scripts call these; they do not reimplement them.

### A1-S0a — Scene claim

**Why:** Mother and Holt both check progress, then pause through several `next()`/`select()` pages, then commit. Two party members can both be inside the unresolved branch.

**API (names may be adjusted, behavior may not):**

| Function | Behavior |
|---|---|
| `DM_SceneClaim("<scene>")` | First caller owns the scene for their party. Returns 1. Second caller returns 0 and is told who is speaking. |
| `DM_SceneJoin("<scene>")` | Observer path: hear `DM_PartyMes`, no second menu, no second grant. |
| `DM_SceneOwnerParty("<scene>")` | Party id recorded at claim. |
| `DM_SceneRelease("<scene>")` | Clear claim. Safe if already clear. |
| `DM_SceneBusy("<scene>")` | True while claimed. If owner is offline longer than a documented timeout (suggest 60s), treat as abandoned and allow reclaim. **Never** leave a permanent busy flag. |

Store party id, owner char id, and claim tick. Re-validate at the **commit** line, not only at entry.

**Scenes to register in Arc 1:** `arc01_wynne_start`, `arc01_rescue`, `arc01_holt_approach`, `arc01_drain`. Later arcs add their own keys to the same helper.

**Accept:** two clients at each pause, both commit orders, owner disconnect mid-dialogue. One outcome, one payment, recoverable Holt.

### A1-S0b — Instance-local encounter callbacks

**Why:** `monster ..., "Deacon Holt#dm::OnDeviruchiDead"` is looked up by exact NPC name. Instance copies are `dup_<iid>_<npcid>`. The source NPC can receive the death event.

**Pattern already in tree:** `DM_TriggerEvent` resolves `instance_npcname`. Spawn events should use the **current** NPC unique name:

```text
.@self$ = strnpcinfo(NPC_NAME);
monster .@map$, x, y, "Name", MOB, 1, .@self$ + "::OnBossDead";
```

Store that label on the encounter record so cleanup uses the same string.

**Accept:** kill on the public map, then on a copied map. Inspect which NPC clears `'boss_up`, which map’s adds vanish, which party is paid. An expired copy cannot complete a newer encounter.

### A1-S0c — Encounter record and cleanup

Record at spawn: scene key, party id, map, generation/counter, boss label, add label, `'boss_up` NPC.

| Function | Behavior |
|---|---|
| `DM_EncStart("<scene>", party)` | Increment generation, store owner/map/labels. |
| `DM_EncOnDeath("<scene>")` | Return 1 only if caller matches recorded party **and** generation. Do not call `DM_SessionParty()` as the owner source. |
| `DM_EncCleanup("<scene>")` | `killmonster` stored labels, clear `'boss_up`, release scene. **No** quest complete, **no** EXP. |

Wire `@dm cleanup` / `DM_CleanupMap` to also sweep registered campaign encounter labels for the current map, or call `DM_EncCleanup` for the active scene. `@dm mode off` must document: grants clear, encounters clean, no silent victory.

Distinct DM operations (preview each):

1. Pause session  
2. Reset current encounter (cleanup, no rewards)  
3. Repair quest/flag state  
4. Grant missing eligible rewards  
5. Reset campaign (explicit scope)

**Accept:** reset during dialogue, combat, and after a wipe, on source and instance. No leftover mobs, false victory, duplicate reward, or stuck Holt.

### A1-S0d — Canonical arc complete

One function per arc, used by the death path **and** the DM beat.

`DM_Arc01Complete()` must:

- Complete **20005 and 20001** (idempotent)
- Set beat 199
- Set `dm_arc01_sigil_ring_obtained` if the scene granted the ring
- Not auto-complete unresolved 20004/20006
- Not pay EXP/zeny (callers pass through `DM_ClaimGrant` separately)

DM beat “Complete Arc 1” calls this, then optionally a **previewed** reward repair. It must stop an active encounter via `DM_EncCleanup`.

Same pattern later: `DM_Arc02Complete` completes 20012 **and 20007**, and so on.

---

## Slice 1 — Arc 1 combat contract and hunt ungate

### Encounter level — tune the spawned unit, do not fork mob_db

Confirmed mismatch:

| Signal | Value |
|---|---|
| Spawned mob | `DEVIRUCHI` 1109, lv 93, 8,912 HP, ATK 477–182, DEF 72, DEX 119 (`db/re/mob_db.conf`) |
| Reward helper | Arc 1 expected level **18** (`DM_RewardArcLevel`) |
| Encounter table | `sewer_ambush` intended level **30**, also uses 1109 |

Keep spawning **stock 1109**. The campaign already has the primitives to change that one unit after it lands; do not add a `mob_db2` clone and do not globally edit Deviruchi.

**Already in the tree:**

| Tool | What it does today |
|---|---|
| `monster()` / `areamonster()` | Return the GID when amount is 1 (`$@mobid[0]` also set). Documented in `doc/script_commands.txt`. |
| `setunitdata` / `getunitdata` | Per-unit HP, ATK, MATK, DEF, HIT, FLEE, LEVEL, mode, and **`UDT_DAMAGE_TAKEN_RATE`**. Stealth already uses this (`DM_StealthSet`). |
| **`UDT_DAMAGE_TAKEN_RATE`** | The dedicated damage knob. Default 100. MVP green-aura mobs use 10 (they take 10% damage). Values **above 100** make the unit die faster. Applied to both physical (`battle.c`) and skill (`skill.c`) damage **after** the hit is calculated. |
| `DM_MobStat` + `tools/gen-encounter-stats.py` | Real HP / EHP / DPS for encounter mobs. `1109` is already in the table (lv 93, 8912 HP, 336 DPS). |
| `DM_EncBudget` / `DM_EncPartyPower` | Prices an encounter against the live party: time-to-die, level gap, MVP flag. |
| `DM_EncScale` | Scales **minion count** with online party size, not stats. |
| `DM_RewardArcLevel` | Arc 1 → 18, Arc 2 → 28, … Arc 5 → 58. |
| `@dm hazard … [damage_pct]` | Unrelated: percent-HP pulses on a hazard tick, not combat. |

There is **no** `@dm damage` command yet. The engine knob is `setunitdata(<gid>, UDT_DAMAGE_TAKEN_RATE, <n>)`. Wrap that as the first axis of `DM_EncTune` so story spawns and `@dmenc spawn` share it.

**Two different problems, two knobs:**

| Problem | Knob | Arc 1 example |
|---|---|---|
| Party cannot chew the HP / DEF | Raise `UDT_DAMAGE_TAKEN_RATE` (100 → 300–500) | 1109 takes 3–5× player damage; keep the sprite |
| Party gets one-shot (auto-attack **or** Dark Thunder) | Lower `UDT_ATKMIN/MAX` and `UDT_MATKMIN/MAX` | Skills still fire, but they no longer hit like a lv93 |

`DamageTakenRate` does **not** reduce what the monster deals. Mercy/binding can bump the rate further (visible: the conduit is taking real wounds) and/or drop ATK/MATK.

**Wrapper (built in `dm_encounters.txt`):**

```text
DM_EncTune(<gid>, <target_level>{, <percent>})
```

- `<target_level>` is `DM_RewardArcLevel(<arc>)` unless the DM passes a harder preset.
- `<percent>` default 100; mercy / binding pass ~70 (easier), “had time to prepare” pass ~130.
- **First:** set `UDT_DAMAGE_TAKEN_RATE` from `100 * current_level / target_level` (cap reasonably). That is the DM damage knob.
- **Also:** scale ATK/MATK (and HIT/FLEE if they cannot connect). Do not leave DEX 119 on an opening fight.
- Optionally set `UDT_LEVEL` so the nameplate matches.
- Spawn adds **one at a time** so each GID can be tuned (`monster()` only returns a GID when amount is 1).
- Call this from Holt **and** from `DM_EncSpawn`, using the encounter table’s intended level (field 11) when no arc is given.

Then `@dmenc info sewer_ambush` / `DM_EncBudget` is the rehearsal: spawn, tune, read time-to-die against the actual party. `gen-encounter-stats.py --check` still describes the **untuned** database row; the live budget after `DM_EncTune` is what playtest uses.

**Skills stay on the class.** 1109 still has `NPC_DARKTHUNDER`, `NPC_CURSEATTACK`, `NPC_DARKNESSATTACK`, `NPC_ENERGYDRAIN`. The damage-taken knob does not stop those; MATK/ATK scaling is what tames them. First live test must record whether a tuned unit still one-shots. A new `mob_db2` entry is **last resort**, only if both knobs fail.

| Field | Plan |
|---|---|
| Mob id | Keep **1109** so quest 20005 `Targets.MobId` stays valid |
| Sprite / name | Deviruchi; display name can still be “Listening Chamber Conduit” |
| Target profile | Four regular characters around **level 18–25**, mixed jobs, no GM stats |
| Harder preset | Same spawn, `DM_EncTune(gid, 30)` or percent 130 — not a second database id |

Until a live four-player test records time-to-defeat, deaths, unavoidable skill hits, and whether support jobs contribute, call it **unvalidated**.

Mercy / binding-word must change a **visible** property: remove one add wave **or** call `DM_EncTune` again at ~70% (announce the conduit starving). Hidden undocumented multipliers are not enough. If the word is not implemented yet, delete the promise from Holt’s line.

Adds stay `FARMILIAR` (lv 24) unless the same helper shows they still out-tier the party; then tune them too. Count:

| Condition | Effect |
|---|---|
| Base | 4 |
| Child rescued quietly / civilians guided away | −2 named refugees leave before combat (announce it) |
| Camp reported / recruits hostile | +1–2 visibly identified hostiles |
| Chamber actually drained | −1 wave |
| Binding word applied | −1 wave **or** skip pressure pulse |
| Floor | 1 |

Tibbets friendship no longer subtracts adds by itself. It only unlocks the easier drain method.

### Hunt ungate

| Quest | Today | After |
|---|---|---|
| 20002 Cellar Vermin | Mandatory with 20003 before 20005 | Optional route-cleaning contract |
| 20003 Rockers and Rumors | Mandatory; Rocker Doll ×3 from **Vocal 1088** (~30 min base spawn on `prt_fild07`) | Optional rare bounty **or** retarget the doll onto common Rockers (1052). Never gate Holt |
| Wynne start | Auto-starts 20001+20002+20003 | Starts 20001 only; offers hunts from a contract menu |

Wynne offers 20005 when `dm_arc01_clue_mask` has two clues **or** Tibbets has shown the route. Closing hunts is flavor/pay, not a key.

Extend `tools/gen-hunts.py --check` later to flag rare-spawn mandatory items. Not a blocker for ungate: just stop using 20003 as a gate.

---

## Slice 2 — Arc 1 playable route

### Cast and maps

| NPC | Map / current cell | Role after rewrite |
|---|---|---|
| Session Board#dm | prontera 155,185 | Show current objective, not only “Arc N of 19” |
| Quartermaster Wynne#dm | prontera 156,191 | Swear-in, optional contracts, 20005 after clues, debrief |
| Frightened Mother#dm | prontera 156,40 | Accept 20004; cannot resolve it here |
| Child / soup-line witness (new) | Prontera south gate, near mother — **walk-check** | 20006 discovery; named child with her own lines |
| Painted sluice (new) | Upper Culvert `prt_sewb1` — **walk-check** | Clue bit; crayon / goat-head paint |
| Tibbets the Keeper#dm | prontera 146,193 | Route if a clue is missed; easier drain, not the only drain |
| Tide-wheel (new) | `prt_sewb4` approach cell, not Holt’s tile — **walk-check** | Drain interaction |
| Binding conduit (new) | `prt_sewb4` staging — **walk-check** | Optional “Hlin” apply before hostility |
| Deacon Holt#dm | prt_sewb4 103,100 | Scene host; staging/ready happens **before** this tile goes hostile |
| Brother Cassell | Voice from Holt scene (keep) | Escapes; ring drop; no fake capture |

Fountain opening: reuse Wynne/board. First useful action is next to the fountain (Tibbets) or a clearly marked south-gate walk. Do not send players hunting an unexplained NPC across the city.

### Player sequence

1. Swear in at Wynne. 20001 starts. Optional hunts offered, not required. Party motive is acknowledged, not stored as the party’s eternal `hero_type` label for 19 arcs (keep the flag for Loki flavor if needed; do not treat it as canon).
2. Observable incident: water/ward hum at the fountain, or a witness pointing at Wynne. Then: mother and/or Tibbets.
3. Find the child at the soup line (20006). Mother keeps saying where to look until discovery is recorded. Drawings in the upper Culvert are a second clue source.
4. Two clues (paint + witness, or one clue + Tibbets) unlock 20005. Journal names the chamber.
5. Staging cell on `prt_sewb4`: inspect conduit, optional drain, optional binding word, ready check, warning, then hostility.
6. Cassell speaks and leaves through the grate. Attempted pursuit can yield a dropped message; no chase subsystem and no fake “we caught him.”
7. Resolve the conduit. Holt’s fate commits **here**. Ring attunes.
8. Return to Wynne. 20001+20005 complete. Payon lead is a real destination: Sun-Hwa at Payon shrine `payon,181,104`.

### Quest IDs

| ID | Name | Role |
|---|---|---|
| 20001 | Omens at the Fountain | Arc tracker. Completes with 20005 |
| 20002 | Contract: Cellar Vermin | Optional hunt |
| 20003 | Field Contract: Rockers and Rumors | Optional bounty (fix or label Vocal) |
| 20004 | The Trembling Ground | Rescue; cannot complete without 20006 (or equivalent discovery flag) |
| 20005 | The Goat-Headed Sign | Chamber resolution. Start after clues, not hunts. Target the campaign mob |
| 20006 | South Gate Soup Line | **Assigned:** find the child / question the witness |

Do not invent a new required ID in 20031+ for Arc 1.

### Flags

Keep existing names as **derived compatibility** where later content already reads them. New names are the source of truth.

| Flag | Values | Writer | Readers | Reset |
|---|---|---|---|---|
| `dm_arc01_started` | 0/1 | Wynne / beat | Gates | `DM_ClearArc01Flags` |
| `dm_arc01_hero_type` | 1 help / 2 pay / 3 monsters | Wynne intro | Arc 19 flavor only | **Add to clear helper** (currently omitted) |
| `dm_arc01_clue_mask` | bit0 paint, bit1 witness/child, bit2 Tibbets route | Clue NPCs | Wynne 20005 gate, journal | Clear |
| `dm_arc01_child_found` | 0/1 | 20006 NPC | Mother resolution, journal | Clear |
| `dm_arc01_rescue_route` | 0 none, 1 quiet escort, 2 guarded report after she is safe, 3 confront organizer | Mother **after** discovery | Encounter adds, mother epilogue | Clear |
| `dm_arc01_refugees_helped` | 0/1 derived from route 1 or 3 vs 2 | Same commit | Existing Holt add math until swapped | Clear |
| `dm_arc01_tibbets_befriended` | 0/1 | Tibbets | Easier drain only | Clear |
| `dm_arc01_key_access` | 0/1 | Tibbets or manual repair start | Drain NPC | Clear |
| `dm_arc01_chamber_drained` | 0/1 | Tide-wheel success | Encounter −1 wave; Tibbets journal | Clear |
| `dm_arc01_binding_applied` | 0/1 | Conduit NPC | Encounter | Clear |
| `dm_arc01_holt_approach` | 0 none, 1 persuade, 2 custody, 3 lethal | Holt menu **intent only** | — | Clear on abort |
| `dm_arc01_holt_fate` | 0 none, 1 spared, 2 captured, 3 dead | Encounter resolution only | Debrief, later callbacks | Clear |
| `dm_arc01_holt_spared` / `holt_killed` | derived from fate | Resolution | Existing readers | Clear; never both 1; never set before the fight |
| `dm_arc01_sigil_ring_obtained` | 0/1 | Ring grant | Arcs 2–6, 8 flavor | Clear flags; item repair is separate |
| `dm_mira_lives` | legacy | unused in Arc 1 script | print only | Keep clear |

Failed drain check: short repair/defense, then retry. Never permanently lock the wheel.

Refugee routes (after the child is found, with evidence of risk stated first):

1. Escort her home quietly → civilians guided away from the chamber  
2. Guarded evacuation, then report Holt → not an indiscriminate sweep  
3. Confront the soup-line organizer with the witness present  

Saving the child does not endorse the cult. Reporting does not mean consenting to collective punishment. Skipping 20004 does **not** set Holt killed.

Holt menu (always available, refugee help improves persuasion, does not unlock the concept of mercy):

- Try to persuade him  
- Take him into custody  
- An explicitly lethal action  

“You’ll answer for it” is custody, not execution. Abort records no fate.

### EXP / zeny budget (scripted story only)

Current scripted **base EXP**: 4,000 + 4,500 mandatory hunts, optional 3,000 mother, 60,000 boss. ~84% of the mother-included total lands after the fight.

Keep the **mandatory total near 68,500** base / **28,300** job (today’s 20002+20003+20005). Redistribute:

| Beat | Share | Proposed base / job | Grant key |
|---|---|---|---|
| Clues + 20006 discovery | 30% | 20,500 / 8,500 | `arc01_clues` |
| Drain and/or staging ready (story, even if drain skipped) | 30% | 20,500 / 8,500 | `arc01_prepared` |
| Chamber resolved (any Holt fate) | 40% | 27,500 / 11,300 | `arc01_deviruchi` |
| Optional 20002 | extra | keep 4,000 / 1,500 | hunt collect |
| Optional 20003 | extra | keep 4,500 / 1,800 | hunt collect |
| Optional 20004 rescue | extra | keep 3,000 / 1,200 | `arc01_rescue` |

Zeny: keep mother quiet 1,500 vs report 2,500 only if the routes stay distinct; do not pay more for cruelty as the sole differentiator. Prefer equal story zeny + different encounter/support outcomes.

Add every new grant key to `DM_ClearPartyGrants`.

### Ring

Canonical discovery: `dm_arc01_sigil_ring_obtained`.  
Each eligible online member gets item 50001 independently. One member already holding a ring must **not** consume the party latch.

`DM_GivePartyItem` today grants online members only. Add a claim/repair line: “Wynne can replace a missing ring” / DM repair preview. Campaign reset does not delete the untradeable item; repair must be idempotent (no duplicates).

Decision: **each participating member receives a keepsake**, because later arcs check `countitem(50001) \|\| dm_arc01_sigil_ring_obtained` per character. Align Holt’s “one small ring” prose with that, or attune one ring and flag the party — pick the item-per-member model; it already matches the gate.

### Journal (player-facing)

| Field | Copy |
|---|---|
| Title | Follow the Humming Water |
| Purpose | Find why the city’s water vibrates and where the missing girl’s trail leads |
| First objective | Ask Tibbets about the painted sluice gates, or speak to the mother at the south gate |
| After one clue | Find the second sign: the soup line, the painted gate, or Tibbets |
| After two clues | Descend to the lowest Culvert chamber. Optional: drain the wheel and speak the binding-word |
| Location | Prontera fountain → south gate / Culvert → `prt_sewb4` |
| Complete | Listening Chamber resolved; speak to Wynne; then Sun-Hwa at Payon’s shrine |

Separate “you carry” hunt items from party quest completion. Hand-ins consume the talking character’s inventory.

### DM beats (`DM_BeatArc01`)

| Beat | Must match NPC path |
|---|---|
| Wynne starts | 20001 only; optional hunt start as a separate beat |
| Trembling Ground | Start 20004; do **not** complete it |
| Soup line / child found | Start/complete 20006 discovery |
| Tibbets | Sets friendship/key_access, not `chamber_drained` |
| Drain | Sets drained only |
| Start 20005 | Allowed without 20002/20003 |
| Complete Arc 1 | `DM_Arc01Complete` + encounter cleanup; preview rewards |

---

## Arcs 2–5 — same pattern after Arc 1 ships

Copy Slice 0 helpers. Do not copy Holt’s spawn/grant code. Each arc below lists only what is specific.

### A1-02 Payon — restore a name

**Files:** `act_01/arc_02_payon.txt`, beats `DM_BeatArc02`, quests 20007–20012.

**Confirmed today:** 20008+20009 gate 20012. 20010 lanterns and 20011 graves complete in the same Sun-Hwa conversation (no walk) and are completed **without ever being started**, so they never appear as active journal quests. 20007 never completes. Voss “These were people” sets `voss_killed` before combat. “Teach us the rite” / restore-without-ancestor sets `sunhwa_marked` without a separate consent line. Conduit “sever” is a menu on Voss. `mushroom_choice` and `bone_tags_choice` are written and almost unused (`ancestor_helped` from 20011 is what actually softens the rite). Start-time `rite_path` is later overwritten. Same instance-callback pattern as Holt (`Scholar Voss#dm::OnMoonlightDead`). DM “Complete Arc 2” skips grove/Voss/conduit flags.

| Keep | Replace | Optional |
|---|---|---|
| Sun-Hwa, Voss, lantern imagery, restore/burn | Mandatory 20008 as the memorial gate | Keep 20008/20009 as leveling contracts |
| Grove flags, notebook | 20010/20011 as talk-complete | — |

**Build:** three disturbed grave/memorial interactions (any two name the ancestor: memorial, family witness, Sun-Hwa’s assisted rite). Failed check still reveals the clue and adds a spirit-defense encounter. Visible conduit objects in the grove **before** the restore/burn choice. “Teach us” is not consent to mark Sun-Hwa — require her explicit agreement after the cost is stated.

**State:** new `dm_arc02_memorial_known` (bitmask). Reuse `ancestor_helped`, `conduits_severed`, `grove_restored`/`grove_burned`, `sunhwa_marked`. `DM_Arc02Complete` finishes 20012 **and 20007**.

**EXP (current scripted base):** 7k+9k hunts + 5–12k story menus + **110k** boss. Move hunt XP to optional. Split remaining story ~60/40 across memorials+conduits vs grove resolution.

**Payoff now:** family at the shrine or a burned memorial NPC. Act IV should quote that person, not only Loki.

**Accept:** both grove outcomes advance; missed clues have an alternate; asking about the rite does not set the mark; returning shows the chosen grove; 20007 complete; Session Board can show Arc 3.

### A1-03 Morroc — choose a route for relief

**Files:** `act_01/arc_03_morroc.txt`, quests 20013–20018.

**Confirmed today:** 20014+20015 gate Osiris (20017); **only 20016** gates Amon (20018), so the main close is Sphinx-only even though Rashid starts all three hunts and talks as if they are required. 20013 never completes. Sabra exposed/deal/marked is a three-option menu with **no commit latch until 20018 is done** — re-talk overwrites the political outcome. Arc 5 already branches on `dm_arc03_sabra_deal` vs `sabra_exposed` (safe vs starved flavor). Osiris/Amon use the same encounter bugs as Holt. Osiris NPC is `moc_pryd04,100,92`; the DM beat warps to `91,83`. DM “Complete Arc 3” sets lidstone/shaft only.

| Hunt | After |
|---|---|
| 20014 Caravan Water Debt | Optional resupply |
| 20015 Ant Hell Survey | Replace main-story role with route-site interactions |
| 20016 Sphinx Night Watch | Optional salvage / ward research |

**Build:** inspect two well/route sites + excavation manifest. Choose shorter exposed vs longer sheltered relief route. Two **checkpoint** encounters with NPC arrival after each clear (not escort AI). Failure damages optional cargo; people remain recoverable.

**Choice:** preserve relief while stopping the dig, **or** expose the operation and establish an alternate water point. Exposure must include a practical follow-up so “truth” is not automatically “refugees suffer.”

**State:** new `dm_arc03_relief_route`, `dm_arc03_relief_secured`. Reconcile Sabra flags from that result. `DM_Arc03Complete` finishes 20018 **and 20013**. Arc 5 reads `relief_secured`, not only accusation flags.

**EXP:** 16k+22k+30k hunts + 90k Osiris + **150k** Amon. Hunts optional. Split story across survey/delivery vs tomb resolution; peaceful tomb handling (if any) pays the same base as combat.

**Accept:** both political choices can protect civilians by different work; a failed navigation roll does not block the tomb; Arc 5 flavor matches the relief state; 20013 complete.

### A1-04 Geffen — operate the seal

**Files:** `act_01/arc_04_geffen.txt`, glyphs already at `gef_dun02` 219,212 / 214,217 / 209,212, quests 20019–20024.

**Confirmed today:** 20020+20021+20022 gate 20023. Glyphs are a silent East→North→West sequence; wrong order resets; they do not explain relationships. Puzzle flags `dm_arc04_puzzle_1..3` are **not** in `DM_ClearArc04Flags`. 20019 **does** complete, but only when Cassell finishes 20024 — skipping the catechism leaves the tracker open after Baphomet. Vault Seal Pressure is a **DM-only** beat, not started by the player path. Doran “fought” is a flag with no Doran fight.

This is the closest existing “operate something” pattern. Promote it to the main path and teach it.

| Hunt | After |
|---|---|
| 20020–20022 | Optional material/gear prep |

**Build:** each glyph reports its effect **before** activation. Players test a stable configuration, then defend. Wrong config: short, signaled pressure pulse, reset only the current attempt. DM hint ladder: symptom → relevant glyph → explicit solution. A party without a mage can still solve or receive Elsbeth/Doran assistance. “Channel magic” cannot be the only verb.

**Choice:** reinforce the seal and divert the city’s supply (`seal_reinforced` + `city_dimmed`) vs keep overflow (`overflow_kept`). First “Geffen dims” implementation: lamp NPC lines / Elsbeth epilogue, not a lighting overhaul.

**State:** new `dm_arc04_configuration_committed` for repeat-reward guard. Add puzzle flags to clear/print. Catechism 20024 stays a **separate explicit** accept. `DM_Arc04Complete` already has the right quest pair; keep using it.

**EXP:** 38k+52k+62k hunts + **210k** Baphomet + 80k catechism. Hunts optional. Split diagnosis vs defense; catechism remains optional extra.

**Accept:** non-mage party can finish; failure is recoverable; hub acknowledges both outcomes; reset stops every pulse timer.

### A1-05 Alberta / Izlude — the manifest is a rescue plan

**Files:** `act_01/arc_05_alberta_izlude.txt`, quests 20025–20030.

**Confirmed today:** 20026 ferry completes in the next Mara menu (no departure) and **does not gate** 20029/20030. Mara starts 20029 only after both hunts, but **Brode can start 20029 with no hunt check**. Diver “rescue” is a hunt-turn-in select. Quiet vs loud hold only changes text — both spawn the same crew fight. Completing 20026/diver-help increments `dm_arc19_ally_turnout` immediately (fragile if repeated). 20025 **does** complete on Tao death. Arc 3 Sabra flags already flavor Mara and hold refugees. Mara is `alberta,183,151`; the DM beat warps `184,150`. Brode has no choice latch until 20029 is done.

| Keep | Replace |
|---|---|
| Mara, Brode, breathing ballast, relics → Tao | 20027 as mandatory; 20028 as the only way to open the hold |
| Quiet vs loud hold flags | Menu-only ferry and diver |

**Build:** two ferry **departures** as scene steps (people / supplies / escorted informant on the first; salvage the remainder at a known cost on the second). No invisible starvation clock. Two diver groups at fixed interaction sites. Open the hold quietly with evidence/tools or loudly with an extra defense encounter. Neutralize relic crates by interaction before Tao, or keep them and face stronger pressure.

**State:** new `dm_arc05_departures_used`, `dm_arc05_diver_groups_saved`. Reuse hold/ferry/relic/alliance flags with exactly-once grants. Stop incrementing `dm_arc19_ally_turnout` from raw menus; set a stable ally flag and let Arc 19 count committed allies once.

**Disconnect:** a departure in progress is not consumed. `DM_Arc05Complete` keeps completing 20030+20025 and `dm_act01_complete`.

**EXP:** 45k ferry + 70k+76k hunts + 110k cargo + **280k** Tao. Hunts optional. Split departures/divers vs hold/Tao.

**Accept:** every first-departure choice has a follow-up; quiet and loud entry both work; rescued NPCs are at the harbor afterward; Act I complete once; Session Board can show Arc 6.

---

## Act I exit criteria

The party can name two allies, explain that the seals are connected, and point to one visible consequence of its own action. The DM can resume from the last completed scene without repeating hunts or grants.

Suggested ally pairs: Tibbets / child-and-mother, Sun-Hwa, Rashid or protected civilians, Elsbeth, Mara.

---

## Files to touch (Act I)

| File | Why |
|---|---|
| `npc/custom/dm_campaign/shared/dm_session.txt` | Scene claim, encounter record, cleanup |
| `npc/custom/dm_campaign/shared/dm_common.txt` | Grant keys; maybe `DM_EncBind` |
| `npc/custom/dm_campaign/shared/dm_flags.txt` | New flags + `hero_type` + Arc 4 puzzle clear/print |
| `npc/custom/dm_campaign/shared/dm_beats.txt` | Beats match NPC paths; complete trackers |
| `npc/custom/dm_campaign/shared/dm_handbook.txt` | Inspect new state |
| `npc/custom/dm_campaign/shared/dm_console.txt` | Cleanup / repair previews |
| `npc/custom/dm_campaign/shared/dm_rewards.txt` | Item repair; do not retune arc expected levels until the live test |
| `npc/custom/dm_campaign/shared/dm_encounters.txt` | `DM_EncTune` via `setunitdata`; also use it from `DM_EncSpawn` |
| `npc/custom/dm_campaign/act_01/arc_01_prontera.txt` | Reference rewrite |
| `act_01/arc_02_payon.txt` … `arc_05_alberta_izlude.txt` | After Arc 1 acceptance; same tune helper on Voss/Osiris/Amon/Baphomet/Tao |
| `db/quest_db.conf` | Keep 20005 on mob 1109; 20006 remains the soup-line quest (add objectives if the client needs them) |
| `db/mob_db2.conf` | **Do not add a campaign Deviruchi** unless live skill tests prove `setunitdata` cannot make 1109 survivable |
| `db/dm_hunt_db.json` + `tools/gen-hunts.py` | Only if 20003’s doll source changes; never hand-edit `dm_hunts.txt` |
| `npc/custom/dm_campaign/CAMPAIGN.md` | Titles, quest ranges, MVP/set-piece honesty |
| Client quest TSV / journal | After server objectives exist (`korangar` journal refresh is names/progress, not this narrative state) |

`npc/scripts_custom.conf` already loads the five Act I scripts.

## Migration

- Completed legacy Arc 1 (20005 done, 20001 still active): on login or DM repair, complete 20001, set beat 199, do not repay `arc01_deviruchi`.
- In-progress hunts 20002/20003 remain completable as optional.
- `holt_killed` set because 20004 was skipped: DM repair offers fate rewrite; do not silently resurrect or execute.
- Preview migration; conflicting flags require a DM choice. Do not wipe the campaign on load.

## Tests

Static: `tools/check-campaign.sh`, `python3 tools/gen-hunts.py --check`, `script-checker` on touched NPCs.

Headless `korangar-networking` DM scenarios cover generic quest/flag/beat surfaces. They do **not** accept Arc 1. Add campaign-specific assertions when the helpers exist; until then the matrix below is live/two-client.

### Arc 1 matrix (from the deep review, now the merge bar)

- Fresh party, no 20002/20003: reaches and resolves Holt; 20001 and 20005 both complete.
- Accept 20004 and immediately revisit mother: no discovery, no payment.
- Two clients on mother: one outcome, one grant.
- Two clients on Holt: one encounter; owner disconnect recovers.
- All combos of rescue route × drain × binding × Holt approach: announced effects match adds/pressure.
- Source-map vs instance-map kill: correct controller, cleanup, party.
- Switch DM session mid-fight: no cross-party credit.
- Cleanup / mode-off during dialogue or combat: no false success, no stuck busy.
- Ring: speaker already has it; companion empty; full inventory; offline rejoin; replay. No missing token, no duplicate.
- Normal victory then DM complete, and the reverse: pay once.
- Begin Payon: Session Board is not stuck on Arc 1; next objective names Sun-Hwa.

Four-player laptop record (design targets, not current estimates): first meaningful action within ten minutes; each player gets to investigate, operate, or assist; no compulsory Vocal farm.

## Out of scope for this plan

- Implementing Acts II–IV (use the redesign briefs after Act I playtest)
- Automated party voting
- New HUD packets beyond existing quest log fields
- Map art, lighting overhaul, chase/escort AI
- Balancing the campaign Deviruchi from theory — measure it

## Implementation start

First PR: Slice 0 helpers + Arc 1 lifecycle (complete 20001, instance callbacks, scene claim, cleanup) **without** waiting for the child NPC or the new mob. That unblocks every later arc.

Second PR: hunt ungate + `DM_EncTune` on 1109 + truthful mercy math.

Third PR: child, clues, drain, binding, Wynne debrief, journal copy.

Do not duplicate this controller into Payon until PR1’s two-client tests pass.
