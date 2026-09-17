# Arc 1 — deep script and design review

**Date:** 2026-09-06  
**Status:** Review complete; consumed by the [Act I implementation plan](act-01-implementation-plan.md). No gameplay scripts changed.  
**Companion:** [Act-by-act designer handoff](seal-cascade-act-redesign.md#act-i--the-first-thread-learn-to-investigate-and-cooperate).

## Assessment

Arc 1 has a good opening cast and a usable mystery, but several promised activities are narration-only, the main tracker does not close, and encounter ownership/recovery need work. Fix those before treating this arc as the reference implementation for the other 18.

This review traces the entire [Arc 1 script](../../npc/custom/dm_campaign/act_01/arc_01_prontera.txt), its [DM beats](../../npc/custom/dm_campaign/shared/dm_beats.txt), handbook, quest/flag/reward/session/instance helpers, hunt generation, renewal monster data, configured field spawns, and the engine's monster-event dispatch. It is not a live multiplayer reproduction or a graphical/map-walkability acceptance pass.

**Evidence labels:** “Confirmed” describes code/data behavior directly visible in the reviewed tree. “Execution risk” describes a reachable interleaving or lifecycle path that still needs a live reproduction. “Design” describes a proposed change, not a defect established by a test.

The retained hunt data passed `python3 tools/gen-hunts.py --check`. That proves the three generated artifacts match the master; it does not establish acceptable time-to-completion or encounter difficulty. No live campaign state was reset or advanced for this review.

## Current player flow

| Step | Current requirement/action | Important detail |
|---|---|---|
| Start | Active DM party; speak to Wynne | Starts 20001, 20002 and 20003; one speaker assigns the party's stated motivation |
| Collection | Finish both 20002 and 20003 | Mandatory before Wynne offers 20005; one character must carry each full turn-in, then online party receives credit/payment |
| Optional mother | Accept 20004, speak to the mother again | Second conversation narrates the entire discovery without requiring travel or another interaction |
| Optional Tibbets | Ask politely, or prove completion of 20002 | Sets friendship; no physical key or drain interaction is implemented here |
| Main scene | Accept 20005, talk to Holt on prt_sewb4 | Multiple dialogue pauses precede encounter lock; ring and Holt outcome are set before fighting |
| Encounter | Spawn ordinary DEVIRUCHI plus 1–4 FARMILIAR | Refugee help removes two adds; Tibbets removes one; mercy announcement does not change boss stats |
| Completion | Deviruchi callback | Completes 20005, grants 60,000 base/25,000 job EXP; leaves 20001 active |
| Next arc | Wynne mentions Payon | No completed Arc 1 anchor for Session Board; next-arc handoff is generic prose |

## Findings and required changes

### AR1-01 — Rescue completes at the quest giver without a rescue

**Confirmed · P1 · Narrative + quest implementation.** In the mother NPC, accepting quest 20004 returns to the player. The next interaction reaches the unconditional in-progress narration: the girl is found at a soup line. There is no visited-location check, drawing interaction, child NPC, or search completion prerequisite on this path. A player following the instruction to search the upper Culvert receives no scripted discovery event from that instruction.

**Reproduction:** start the arc; accept the mother's quest; immediately talk to her again without leaving Prontera. The resolution choice and payment are available.

**Change:** implement one child/soup-line interaction and two observable clue sources. Use quest 20006, currently reserved, only after explicitly assigning its role; otherwise leave it unused. The mother should say where to search until discovery is recorded. The player returns with a real outcome. The child should have a name and a short account in her own voice; she is a person, not only the switch that unlocks mercy.

**Accept:** quest acceptance alone cannot resolve the rescue; going to the stated location produces a discovery; each supported rescue approach reaches a return scene; the journal describes the actual outstanding task.

### AR1-02 — The tide-wheel promise has no matching interaction

**Confirmed · P1 · Quest implementation.** Tibbets repeatedly instructs players to drain the chamber. He sets only `dm_arc01_tibbets_befriended`. The encounter subtracts one add when that flag is true, regardless of any drain operation. The campaign search finds no separate Arc 1 drain interaction/state.

**Change:** separate `key_access` from `chamber_drained`. Provide a visible wheel interaction on a validated approach cell and a manual repair route for parties without Tibbets's help. Apply its benefit only after the drain completes. A flag-backed tool is sufficient; an inventory key item is optional, but the UI must not imply an inventory item was delivered when none exists.

**Accept:** obtaining access alone does not drain the chamber; the player can identify and operate the control; the journal stops instructing them to drain once it is drained; the resulting encounter difference is observable.

### AR1-03 — Mercy advertises a weakened boss but does not weaken it

**Confirmed · P1 · Encounter implementation.** Holt's mercy path gives the binding-word “Hlin” and announces an unfed, weaker Deviruchi. The subsequent `monster` call is identical on both paths. There is no binding-word action or boss-stat change. The add calculation reads refugee help and Tibbets, not `holt_spared`.

**Change:** let a player apply the word to a labeled conduit before the fight or during a safe preparation phase. Prefer one clearly observable mechanical effect, such as removing a particular pressure phase, over a hidden damage modifier. If this action is not built yet, remove the unsupported promise from the dialogue.

**Accept:** mercy provides the opportunity rather than silently completing it; applying the word changes a measurable encounter property; players can still win if they do not apply it.

### AR1-04 — The encounter's level contract is undefined and inconsistent

**Confirmed data mismatch; difficulty requires live testing · P1.** `DEVIRUCHI` resolves to mob 1109 in [renewal mob data](../../db/re/mob_db.conf): level 93, 8,912 HP, substantial attack and defenses. The script spawns that entry directly, without an Arc 1-specific scaling call. The [reward helper](../../npc/custom/dm_campaign/shared/dm_rewards.txt) assigns Arc 1 expected reward level 18. The separate encounter table calls its sewer ambush a level-30 activity. These are three different signals about intended readiness.

The script calls this an MVP in comments, but this Deviruchi entry is not an MVP. Familiar adds are level 24 in the same database. Monster name and HP alone do not establish whether a novice party can reasonably hit, survive, or contribute against the enemy.

**Change:** declare the supported starting/finishing party level and equipment profile before tuning. Keep spawning stock 1109. Tune **that unit** with `DM_EncTune`: first the engine damage knob `UDT_DAMAGE_TAKEN_RATE` (how fast it dies), then ATK/MATK (how hard it hits, including skills). Do not globally weaken all Deviruchis and do not add a `mob_db2` clone unless both knobs still leave it lethal. Use existing `DM_MobStat` / `DM_EncBudget` against the live party. Verify accuracy/evasion, defenses, skills, burst damage, and retreat space as well as HP. Keep a harder preset as a different tune target, not a second mob id.

**Accept:** test the intended four regular-player builds without GM combat stats. Record time-to-defeat, deaths, unavoidable hits and whether low-damage/support builds contribute. Set the normal preset from that evidence. Until then, call it an unvalidated encounter, not a balanced beginner boss.

### AR1-05 — Mandatory Rocker Dolls introduce a rare-spawn bottleneck

**Confirmed data; elapsed impact depends on live rates, pooling and DM intervention · P1.** Quest 20003 requires three Rocker Dolls. Its bonus drop is on Vocal (1088), not the abundant Rockers. The [recommended field](../../npc/re/mobs/fields/prontera.txt) has 150 Rockers and 50 Savage Babes with five-second base respawns, but only one Vocal with a 1,800,000 ms base respawn delay and additional variance. Vocal's natural doll rate is 1,500/10,000; the generated quest bonus is 2,000/10,000.

The generator estimates kills from expected item yield and confirms the species spawns somewhere; it does not budget waiting for a scarce monster on the named map. A clean drift check therefore misses this pacing problem. Do not quote a guaranteed completion time: party quest rolls, inventory pooling, actual server rate configuration and access to other sources affect it.

**Change:** remove 20003 from main progression immediately in the redesign. For an optional contract, use a common enemy's thematic drop or a guaranteed investigation object. If Vocal is retained, label it a rare optional bounty and never make its respawn the clock for reaching Holt.

**Accept:** a fresh party can reach Holt without dolls, stockpiles or GM item grants. Expand data validation to consider recommended-zone spawn density and delay, not only existence anywhere.

### AR1-06 — Arc 1 never completes its anchor quest

**Confirmed · P0 · Progression.** Quest 20001 starts at Wynne and is the Session Board/DM status anchor. Neither `OnDeviruchiDead` nor the DM “Complete Arc 1” beat completes it. Both finish only 20005. The board takes the first in-progress anchor, so an otherwise successful party can continue to be reported as being on Arc 1 after entering later arcs.

**Change:** use one shared completion transition that completes both 20005 and 20001 and updates beat 199. Do not auto-complete an unresolved optional rescue merely to empty the journal. Give that side quest an explicit remaining/resolved/closed policy.

**Accept:** after normal or DM-assisted resolution, the anchor is complete, the main quest no longer looks unfinished, and the board recognizes Arc 2 when it begins. Repeated completion is inert.

### AR1-07 — Multiple conversations can commit the same scene

**Execution risk established by control flow · P0 · Multiplayer.** The mother checks quest progress before several `next()`/`select()` pauses, then commits and pays without rechecking. Two party members can reach the unresolved branch before either completes it; the second can subsequently commit another outcome and payment. Quest completion being idempotent does not make the following EXP/zeny grants idempotent.

Holt checks `'boss_up` only on entry and sets it much later, after several paused dialogue pages, the ring grant and outcome selection. Two admitted conversations can each reach the spawn call. A boss-reward latch can prevent a second payment but does not prevent duplicate monsters or contradictory story flags.

**Change:** claim a party/session scene transaction before shared narration, with an owner and cancellation/rejoin policy. Revalidate at commitment and make completion plus grant claim exclusive. A second participant should observe/join the discussion, not run a second copy. Do not solve this with a permanently stuck busy flag when the speaker disconnects.

**Accept:** stage two players at each pause, commit in both orders, disconnect the owner, and retry. One rescue outcome, one payment, one encounter; a reachable recovery action in every case.

### AR1-08 — Holt can be recorded dead before anyone kills him

**Confirmed · P0 wording/state integrity; P1 design.** If the optional refugee quest was skipped, mercy is unavailable and `holt_killed` is set automatically before combat. The “You'll answer for it” option also sets killed, although accountability can reasonably mean arrest. The only actual enemy spawned as the principal target is the Deviruchi; Holt remains the NPC hosting the scene. Disconnecting after the choice can leave a death outcome without an encounter resolution.

**Change:** distinguish intended approach from completed fate. Offer “Try to persuade him,” “Take him into custody,” and an explicitly lethal action where supported. Refugee help should improve the persuasion route, not be a secret prerequisite for attempting mercy. A harder route can require evidence, the binding-word task, or a nonlethal encounter objective. Commit spared/captured/dead only at its actual resolution.

**Accept:** skipping a side quest does not silently kill an NPC; demanding accountability does not mean execution; failed persuasion has a clear follow-up; aborting the scene records no finished fate.

### AR1-09 — Instanced death callbacks still name the source NPC

**Confirmed source-path mismatch; live instance reproduction required · P0.** The encounter correctly derives its spawn map from `strnpcinfo(NPC_MAP)`, but both death-event strings remain literal `Deacon Holt#dm::...`. [Instance NPC duplication](../../src/map/npc.c) creates unique `dup_<instance>_<npc>` names. The [monster script builtin](../../src/map/script.c) and [mob creation/death path](../../src/map/mob.c) preserve the supplied event string; NPC event dispatch looks it up directly.

Consequently, using a private map does not by itself make the callback instance-local. The named source handler can operate on the source NPC's map/state, including clearing the wrong `'boss_up` and cleaning adds on the wrong map. This contradicts the current documentation's assurance that map-relative spawning alone is enough.

**Change:** derive and store the current instance's unique callback names for both boss and adds; use the same names for cleanup. Tie the handler to an encounter record containing its map, owner and generation. Update the instancing documentation alongside the fix.

**Accept:** fight on the source map, then a copied map. Inspect which NPC state resets, which map's adds disappear and which party receives credit. A callback from an expired copy cannot complete or clean a newer encounter.

### AR1-10 — Encounter ownership is chosen at death, not at spawn

**Execution risk · P0.** `OnDeviruchiDead` asks `DM_SessionParty()` for the current global session party. It does not retain the owner who began the encounter. Changing the active session while an old monster survives can redirect quest credit and EXP. With mode off, the helper falls back to the attached player's party, which also changes the ownership rule.

**Change:** capture campaign/party ownership and encounter generation on creation. On death, validate that record rather than reading the currently active DM session. Session changes should pause or clean old encounters through an explicit lifecycle path.

**Accept:** start for party A, switch active session to B, then resolve or clean A's encounter. B receives no A credit; cleanup grants nothing; an unrelated last hitter does not acquire campaign ownership.

### AR1-11 — Normal cleanup does not reset this encounter

**Confirmed helper coverage gap · P0/P1 recovery.** [DM_CleanupMap](../../npc/custom/dm_campaign/shared/dm_session.txt) kills monsters under three `DM_Console` event labels. Holt's boss/add labels are different, and this helper does not reset his `'boss_up`. `@dm mode off` clears grant latches and session globals without cleaning Holt's monsters. The full campaign reset clears character flags/quests but has no Arc 1 encounter reset transition.

**Change:** implement distinct operations: pause session, reset current encounter without rewards, and reset campaign with explicit scope. Arc 1 reset must remove its boss/adds using the correct instance labels, clear running state, cancel pending scene commitments, and preserve resolved story decisions unless the DM specifically rolls them back. Do not deliver success callbacks as a side effect of cleanup.

**Accept:** reset during dialogue, combat and after a wipe, on source and instance maps. No remaining enemies, false victory, duplicate reward, or permanently busy Holt. Mode-off behavior is documented and matches execution.

### AR1-12 — Ring distribution and repair have inconsistent state

**Confirmed conditional/helper behavior; delivery failures need live tests · P1.** The ring condition claims the party grant before testing whether the speaking character already holds item 50001. If that character already has a ring, the grant latch is consumed but the body—including the story flag update and distribution to other members—is skipped. This matters on replay: the ring is permanent/untradeable and the campaign reset does not remove it.

`DM_GivePartyItem` attempts delivery to online members only and the grant latch is party-wide. A reconnecting member is not automatically repaired. The DM completion beat sets the ring-obtained flag but does not give the item. Later arcs accept either the flag or the item, so physical inventory and story state can disagree without immediately blocking progress.

**Change:** choose a canonical story-discovery state, then reconcile each eligible character's physical token separately. Check capacity and give actionable retry/claim feedback. Never let one member's preexisting token consume everyone else's claim. Decide explicitly whether the story owns one ring with party-wide attunement or each member receives a keepsake; align the “one small ring” scene with inventory behavior.

**Accept:** existing-ring speaker, empty-inventory companion, full inventory, offline/rejoining member and DM repair all converge without duplication or lost entitlement. A new playthrough cannot be broken by keeping the old token.

### AR1-13 — Normal and DM-assisted completion are not equivalent

**Confirmed · P1.** The normal death path completes 20005 and gives EXP, but not the anchor or beat 199. The DM completion beat supplies the story flag and beat but no physical ring or boss reward and does not stop an active encounter. A DM override can intentionally skip combat; the problem is that its resulting state and skipped grants are not made explicit.

**Change:** centralize canonical story completion, with separate choices for “resolve encounter,” “repair quest state” and “grant missing eligible rewards.” Preview what each does. Preserve idempotency across normal resolution followed by repair. The board and journal should depend on canonical completion, not on which UI the DM used.

**Accept:** compare quest/flag/token/grant snapshots after normal victory and documented assisted resolution. Differences must be intentional, visible, and repairable; an old monster cannot pay after the DM already settled its resolution.

## Additional design recommendations

### Give the opening an observable incident

Start with a brief interruption at the fountain: a bucket or nearby ward reacts to the humming water; a witness asks Wynne for help. Reuse existing NPC text/effects. This supplies a reason to care before the guild's exposition. The first useful action should be near the entry point, not a search across the full city for an unexplained NPC.

Keep Wynne's humor, but follow it with one concrete task and a visible route to the mother/Tibbets. Let players establish their own motives; do not turn a single speaker's pay question into an authoritative label for every party member for the next 19 arcs.

### Make the refugee choice more specific than “kindness or a bounty”

The mother currently pays more for reporting the camp, and reporting immediately means an indiscriminate sweep. Give the party evidence about the risk before commitment and allow a targeted report after the girl is safe. Separate rescuing a child from how the party handles a suspected cult operation. Saving her should not implicitly endorse the cult; contacting authorities should not automatically mean consenting to collective punishment.

A concrete three-route scene: escort the child home quietly; arrange a guarded civilian evacuation before reporting Holt; or confront the soup-line organizer with the witness present. These can have different time/encounter costs without requiring an expensive alignment system.

### Do not reward a named action before the action happens

Cassell's escape, the ring discovery, Holt's fate, draining and speaking the binding-word need distinct presentation/state points. A simple sequence is enough:

1. Discover the child/witness and record the route.
2. Reach the chamber staging area and inspect the conduit.
3. Choose optional drain/binding preparations, then ready the party.
4. Hear Cassell's short account; gather information without starting combat.
5. Commit the approach; resolve the encounter and Holt's fate.
6. Recover/attune the ring, return to Wynne, close the main tracker and receive the Payon lead.

If Cassell must escape for later arcs, foreshadow the reachable side-grate and give attempted pursuit a small useful result—a dropped message or identified route. Do not offer a fake capture choice. No new chase subsystem is needed.

### Give the fight a preparation boundary and a retreat route

The current enemy spawns at Holt's position directly after dialogue. Put the active interaction on a safe staging cell, show who is ready, and warn before hostility begins. Retreat should lead to a stable retry state. Shared story text should remain accessible to the party; one player scrolling through pages must not leave everyone else guessing when combat starts.

Map inspection remains outstanding: verify source and instance entry, return warp, staging cell, drain control and room space. Do not assume the existing `103,100` spawn/instance entry is an appropriate safe staging location merely because it is in bounds.

### Rebalance progression around the new route

Current scripted base EXP is 4,000 + 4,500 for mandatory contracts, an optional 3,000 for the mother, and 60,000 for the boss. With the mother included, about 84% of that scripted base EXP arrives at the end, excluding normal monster EXP and other systems. The party may therefore be weakest during its largest encounter, then receive a large jump afterward.

Redistribute existing story budget over discovery, preparation and resolution after deciding the intended starting level. Keep optional bounty rewards separate. Test the transition into Payon as part of Arc 1 acceptance. Do not solve a level-93 encounter mismatch by granting unexplained GM levels immediately before it.

### Make the debrief finish the promise

Wynne should acknowledge the actual child/refugee outcome, Holt's fate, and the recovered clue. Supply “Speak to Sun-Hwa at Payon's shrine” with a player-readable destination and travel guidance. Session Board should show the next task or the completed arc, not always “look for the Quartermaster.” Provide an optional short recap for returning players.

The current headless quest scenarios found in the search exercise generic quest lifecycle/list handling; they do not establish acceptance of this entire NPC route. Add an Arc 1-specific scenario set rather than citing a generic quest pass as coverage.

## Delivery order and review gates

| Order | Work | Gate |
|---|---|---|
| 1 | Canonical anchor completion; exclusive scene commitments; instance callback and encounter-owner fixes; cleanup without victory | Two-client source/instance lifecycle tests pass |
| 2 | Remove mandatory Vocal gate; choose and validate encounter level profile; make mercy claims truthful | Fresh regular-player party can reach and survive the intended encounter without GM compensation |
| 3 | Implement actual child discovery, drain and binding actions; align journal and explicit choices | Instructions correspond to observable interactions; missed optional content never forces a lethal outcome |
| 4 | Per-character ring repair, reward redistribution, DM completion parity and Payon debrief | Replay/reconnect/assisted-run snapshots converge; no double grants |
| 5 | Opening incident, named child/witness, visual consequence and readable group staging | Four-player laptop playtest records comprehension, pacing and participation |

### Minimum test matrix

- Fresh party accepts and resolves Arc 1 through normal NPCs; 20001 and 20005 both complete.
- Accept mother quest and immediately revisit: no discovery or payment until actual search action.
- Two clients resolve the mother simultaneously: one canonical outcome and grant.
- Two clients enter Holt before either leaves dialogue: one encounter, with recovery if the owner disconnects.
- All combinations of refugee outcome, Tibbets access, actual drain action and Holt approach: declared effects match encounter behavior.
- No Vocal kills or carried dolls: redesigned main route remains completable.
- Source-map versus instance-map kill: correct controller, map cleanup and party ownership.
- Change session party during an unresolved encounter: no cross-party completion.
- Reset/cleanup/mode off during dialogue or combat: no false success and no stale busy flag.
- Ring already held by the speaker, not held by another member; full inventory; offline/rejoin; campaign replay: no missing entitlement or duplicate token.
- Normal victory followed by DM completion/repair, and the reverse: rewards once, canonical state consistent.
- Begin Payon after victory: Session Board no longer reports an unfinished Arc 1; next objective is explicit.

**Designer sign-off condition:** players actually find someone, operate something, make an informed consequential choice, and see the result. The arc must then remain coherent when two people click, someone disconnects, or the DM needs to recover the scene.
