# Seal Cascade — act-by-act designer handoff

**Date:** 2026-09-06  
**Status:** Proposed design; no campaign scripts changed by this handoff.  
**Audience:** quest designer, Hercules implementer, Korangar UI implementer, DM/playtest lead.  
**Scope:** improve the existing four acts and 19 arcs. Preserve the central mystery, cast, locations, and five ending concepts. This is an implementation brief, not replacement dialogue for every NPC.

## Design decision

Keep the story about the cost of maintaining the seals. Change what players do to discover that story. The campaign should move from investigating a local problem, to negotiating institutional power, to assembling an imperfect coalition, to deciding who can sustain the next world.

The existing scripts contain worthwhile choices and callbacks. Too many of the intervening activities use the same three-item collection pattern, and too many consequential actions happen when the player merely selects dialogue. Make the action occur in the world, then let the conversation interpret it.

**Working playtest assumptions:** four friends plus a live DM, mixed familiarity with RO, laptop-readable UI, roughly two-hour sessions. Budget a normal arc for 60–90 minutes with optional material; a substantial arc may span sessions. These are design targets to measure, not estimates of current completion time. Tune combat to the party's actual level, equipment, and composition; the DM character's level is irrelevant.

### Evidence and source precedence

The review used the 19 `npc/custom/dm_campaign/act_*/*.txt` scripts, `db/dm_hunt_db.json`, and the shared quest, narration, check, flag, and beat helpers. The hunt database contains 41 contracts, each with three item types. The external Obsidian story vault referenced in the older implementation plan was not available for this review.

Treat executable scripts as the baseline for this handoff. `CAMPAIGN.md` has stale descriptions: its Act I summary says no MVP encounters, while the scripts contain encounter controllers and boss-related quests. Some reference titles also differ from script/quest names. Reconcile the reference as part of delivery; do not remove functioning content to make it match an old summary.

### Priority and responsibility

| Label | Meaning | Primary owner |
|---|---|---|
| P0 | Fix misleading decisions, contradictory outcomes, or unsafe progression before another long campaign playthrough | Hercules + narrative designer |
| P1 | Build and validate the new core arc activity | Hercules + quest designer |
| P2 | Add richer presentation or optional variations after the core activity works | Korangar + narrative designer |

Each arc below has a script link, exact activity replacement, proposed state, downstream payoff, journal requirement, and acceptance condition. New state names are design identifiers, not claims that those flags exist. Register their inspect/reset behavior and map them deliberately to existing flags; do not write a second competing source of truth.

## Rules for all four acts

1. **Questions gather information. Commitments change the world.** Asking “What is the catch?” must not kill, betray, accept, or complete anything. Offer a separate action menu after questions, with a “We need to discuss this” exit. Repeat visits must not repeat rewards or increment ally counts.
2. **A group decision belongs to the group.** Current `DM_PartyMes` mirrors narration, while one player controls the menu. First delivery: show the proposed consequential action to the party and require explicit DM confirmation after discussion. No timer commits an unanswered choice. Automated voting is a later feature, not a dependency of these rewrites. Personal sacrifice additionally requires the named player's affirmative consent.
3. **A failed attempt changes the situation without removing the only route forward.** Clues remain obtainable. Failure can add an encounter, require a repair, or reduce optional salvage. Give the player the next available action immediately. Do not use repeated rolls until success as the replacement route.
4. **Use existing combat where it helps the scene.** Optional bounties can retain ordinary tradeable drops and party pooling. Main-story access should follow investigation, rescue, negotiation, or encounter completion. Remove obsolete hunt gates from both the NPC and DM beat paths. Keep the iconic stock monster; dial it with the [DM encounter tools](dm-tools-for-encounters.md) (`UDT_DAMAGE_TAKEN_RATE`, ATK/MATK, add count, named `@dmenc` packs, hazards). Do not add a `mob_db2` clone or pick a different sprite because the database level is too high.
5. **Preserve progression when cutting chores.** For each rewritten arc, total the existing mandatory EXP/zeny grants and redistribute that budget over new main objectives. Start with roughly 60% for reaching the resolution and 40% for resolving it, then tune from playtests. Optional content adds a bounded bonus. Peaceful and combat resolutions receive the same base story reward. No player should need optional bounties merely to reach the next arc's level expectations.
6. **Show the consequence twice.** One observable change before leaving the arc, and one later callback that affects an NPC, approach, support action, or ending preparation. A finale speech alone does not satisfy this rule.
7. **A journal entry is a usable instruction.** Every main objective supplies a player-facing title, reason, current action, NPC/location, completion condition, and next step. Include recap text, known consequences, and reward preview where reliable. Separate “You carry” from party quest completion. Current item hand-ins consume the talking character's inventory; do not imply automatic aggregation across party bags.
8. **Recovery is part of the feature.** Existing quest/flag helpers synchronize online members; that alone is not an offline catch-up system. Record a campaign checkpoint and explicit reconciliation policy before claiming reconnect support. DM-only repair must preview changes, never replay grants, and never silently overwrite an unrelated campaign.
9. **Readable action feedback.** Hazards need advance warning and a readable safe area. A text announcement emitted at the damage tick is not sufficient. Pause scene timers during the shared decision pause; a disconnected player must not trigger a default bargain. Background tension should not punish someone reading.
10. **Keep scope buildable.** First versions use existing maps, NPC interactions, server checks, encounter controllers, and DM narration. No new map art, general escort AI, procedural dialogue, or custom cinematic system is required. New placements need actual walkability and warp checks; coordinates in existing scripts are not blanket approval for nearby placements.

## Act I — The First Thread: learn to investigate and cooperate

**Implementation plan:** [act-01-implementation-plan.md](act-01-implementation-plan.md) — build order, quest/flag IDs, shared helpers, EXP split, and merge tests for arcs 1–5.  
**Arc 1 script review:** [arc-01-deep-review.md](arc-01-deep-review.md).

**Player promise:** “The small people we help change what happens under the city.”  
**Act change:** move the mystery ahead of the collection grind. Teach one new interaction per arc. Establish recognizable allies before introducing the broader conspiracy. At least one noncombat contribution should be available to every party composition.

### A1-01 — Prontera: follow the water

**Source:** [arc_01_prontera.txt](../../npc/custom/dm_campaign/act_01/arc_01_prontera.txt) — Wynne, Tibbets, the frightened mother, Holt; quests 20001–20006. **Priority: P1, first playable slice.**

- **Keep:** Wynne's dry voice, the missing child, Tibbets's practical knowledge, the Listening Chamber, and the Sigil Ring discovery.
- **Replace:** the requirement to finish both Cellar Vermin and Rockers and Rumors before quest 20005. Keep 20003 as an optional bounty; make 20002 an optional route-cleaning contract. Never require either for the main scene.
- **Build:** Wynne sends the party to the mother and sluice. Inspect a painted gate, question a soup-line witness, then trace the vibration to the lower chamber. Two clues locate the chamber; Tibbets supplies the route if the party misses one. His friendship supplies an easier drain method, not the only way in.
- **Playable payoff:** operate a drain interaction before confronting Holt. The drained approach removes one reinforcement wave. Helping the child causes one named refugee to guide people away from the chamber; reporting the camp brings additional hostile recruits, visibly identified before combat.
- **State:** new `dm_arc01_clue_mask` and `dm_arc01_chamber_drained`; reuse the existing refugee, Tibbets, Holt, and ring flags. A failed mechanism check starts a short repair/defense action; it does not permanently lock the drain.
- **Journal:** “Follow the humming water — ask Tibbets about the painted sluice gates.” Update to the chamber location after sufficient clues.
- **Accept:** new players reach their first investigative decision within ten minutes; the story can be completed with zero bounty turn-ins; both drain methods work; exactly one ring/story grant occurs even on a repeated interaction.

### A1-02 — Payon: restore a name

**Source:** [arc_02_payon.txt](../../npc/custom/dm_campaign/act_01/arc_02_payon.txt) — Sun-Hwa, Voss, lanterns and the grove. **Priority: P1.**

- **Keep:** the ancestor, the lantern imagery, Voss's harvest, and the restore/burn decision.
- **Replace:** mandatory Mushroom Ring Patrol with inspecting three disturbed grave markers. Replace Bone Tag Turn-In's main-story role with matching one recovered name to a family memorial; retain its old collection contract as optional if useful for leveling.
- **Build:** learn the ancestor's name from a memorial, a family witness, or Sun-Hwa's assisted rite. Any two sources establish the rite; an unsuccessful check reveals the clue but causes a spirit-defense encounter. Then players deactivate the grove's conduits through visible interactions before choosing the resolution.
- **Choice:** restoring the grove preserves a place the families can revisit; burning it stops the immediate harvest but destroys that memorial site. If Sun-Hwa must carry a mark, explain the known permanent cost before agreement. “Teach us” is not consent to harm her.
- **State/payoff:** new `dm_arc02_memorial_known`; reuse ancestor-helped, conduit, grove, and mark flags. Show a family reunion or the burned memorial now; use that person's account in Act IV instead of only Loki's summary.
- **Journal:** identify which memorial or witness is still needed; state the ritual cost once learned.
- **Accept:** both resolutions advance; missed clues have alternatives; asking about the rite changes no sacrifice flags; returning after the scene shows the chosen grove state.

### A1-03 — Morroc: choose a route for relief

**Source:** [arc_03_morroc.txt](../../npc/custom/dm_campaign/act_01/arc_03_morroc.txt) — Rashid, Sabra, Osiris's Court and Amon Ra's Lid. **Priority: P1.**

- **Keep:** relief work concealing a dig, Rashid's route knowledge, and the choice about disturbing the dead.
- **Replace:** the three mandatory hunts with one route survey and a relief decision. Caravan Water Debt becomes optional resupply; Ant Hell Survey becomes a route interaction objective; Sphinx Night Watch becomes optional salvage/ward research.
- **Build:** inspect two well/route sites and the excavation manifest. Choose the shorter exposed route or longer sheltered route for relief delivery. Use two discrete checkpoint encounters with NPC arrival after each clear, not continuous escort AI.
- **Choice:** preserve the relief mission while stopping the dig, or expose the whole operation and establish an alternate water point. Give exposure a practical relief follow-up so it is not automatically “truth causes refugees to suffer.” Failure damages optional cargo; people remain recoverable through a follow-up scene.
- **State/payoff:** new `dm_arc03_relief_route` and `dm_arc03_relief_secured`; reconcile Sabra/refugee flags. Arc 5 uses actual relief outcomes, not merely whether the party accused Sabra.
- **Journal:** show delivery checkpoints and whether civilians still need help; keep tomb salvage visibly optional.
- **Accept:** both political choices can protect civilians through different work; no failed navigation roll blocks the tomb; Arc 5 reads the resulting relief state correctly.

### A1-04 — Geffen: operate the seal

**Source:** [arc_04_geffen.txt](../../npc/custom/dm_campaign/act_01/arc_04_geffen.txt) — Elsbeth, Doran, three glyphs, Cassell. **Priority: P1.**

- **Keep:** the city drawing power from the seal, Doran's proof, the three existing glyph NPCs, and the catechism temptation.
- **Replace:** three mandatory hunts with diagnosing three glyphs. Apprentices provide one diagram; Doran or investigation supplies the second; the final relationship is observable from glyph responses. Keep the hunts as optional material/gear preparation.
- **Build:** each glyph reports its effect before activation. Players test and set a stable configuration, then defend it against the existing encounter. Wrong configurations create a short, signaled pressure pulse and reset only the current attempt. Supply a DM hint ladder: observable symptom → relevant glyph → explicit solution.
- **Choice/payoff:** reinforce the seal and divert the city's supply, or preserve the overflow at higher maintenance risk. Use changed lamp NPC effects and apprentice dialogue as the first implementation of “Geffen dims”; a lighting overhaul is unnecessary. Elsbeth can explain either outcome.
- **State:** reuse puzzle flags and mutually exclusive seal/overflow flags; new `dm_arc04_configuration_committed` guards repeat rewards. Catechism acceptance remains separately explicit.
- **Journal:** show the learned glyph relationships and the committed configuration, not an undisclosed puzzle solution.
- **Accept:** a party without a mage can solve or receive assistance; failure is recoverable; the hub visibly acknowledges both outcomes; a reset stops every pulse timer.

### A1-05 — Alberta/Izlude: the manifest is a rescue plan

**Source:** [arc_05_alberta_izlude.txt](../../npc/custom/dm_campaign/act_01/arc_05_alberta_izlude.txt) — Mara, Brode, Exempt Hold, Deep Trench Wake. **Priority: P1.**

- **Keep:** ferry priorities, the breathing “ballast” reveal, Brode's records, and the relics feeding the deep encounter.
- **Replace:** Byalan's compulsory collection with rescuing two diver groups at fixed interaction sites. Replace the manifest collection gate with recovering a damaged ledger and questioning its clerk. Ordinary sea hunting remains optional.
- **Build:** two ferry departures, resolved as explicit scene steps. The first prioritizes people, supplies, or an escorted informant; the second salvages what remains at a known cost. Do not implement an invisible real-time starvation clock. Open the hold quietly with evidence/tools or loudly with an additional defense encounter.
- **Choice/payoff:** neutralize relic crates through interactions before the deep fight, or keep them for leverage and face stronger pressure. Mara's network supplies a later transport/support benefit. Refugee survival follows rescue actions and the Arc 3 relief result, not one old dialogue bit alone.
- **State:** new `dm_arc05_departures_used` and `dm_arc05_diver_groups_saved`; reuse hold, ferry, relic, and alliance outcomes with exactly-once guards.
- **Journal:** list the next departure's passengers/cargo and explicitly explain what waiting changes.
- **Accept:** quiet/loud entry and every first departure have playable follow-ups; disconnects do not consume departures; rescued NPCs are present at the harbor afterward.

**Act I exit:** party can name two allies, explain that the seals are connected, and identify one visible consequence of its own action. The DM can resume from the last completed scene without repeating hunts or grants.

## Act II — The Cascade Widens: evidence, institutions, and personhood

**Player promise:** “Understanding who benefits lets us change how we solve the crisis.”  
**Act change:** replace repeated interrogate-a-villain menus with evidence players acquire and use. Give each institution a different problem. Reward resolving the situation rather than simply endorsing the sympathetic NPC.

### A2-06 — Yuno: build a case that survives suppression

**Source:** [arc_06_yuno.txt](../../npc/custom/dm_campaign/act_02/arc_06_yuno.txt) — Vahl, Krenn, Juperos Vault. **Priority: P1.**

- **Replace:** compulsory collection stages with calibrating two observation sites and retrieving one Juperos recorder. Keep Harpy/parts hunts as optional equipment support.
- **Build:** investigate three evidence sources: migration readings, a signed suppression order, and the recorder. Any two support a council hearing; the third improves witness protection. Bad calibration still retrieves useful but incomplete readings and adds a corroboration task.
- **Decision:** publish with Vahl named, publish anonymously with reduced immediate credibility, or negotiate protected disclosure. Buying silence is a separate, explicitly labeled fourth commitment if retained. Display who is exposed before commitment.
- **State/payoff:** new `dm_arc06_evidence_mask` and `dm_arc06_disclosure_mode`; keep Krenn/Vahl flags only as derived compatibility outcomes. Arc 16 changes which witness can appear and which political introduction is available.
- **Journal:** an evidence list showing source and reliability; do not label a hypothesis as proven.
- **Accept:** all questions about payment/disclosure are inert; each route reaches the vault resolution; missing one source does not stop the campaign; the later witness matches disclosure choices.

### A2-07 — Einbroch: keep the foundry alive

**Source:** [arc_07_einbroch.txt](../../npc/custom/dm_campaign/act_02/arc_07_einbroch.txt) — Greta, Kessler, RSX. **Priority: P0 consistency, then P1 activity.**

- **Fix first:** Mine Dust Medicine's pelts dialogue contradicts its powder/crystal requirements. Generate any retained collection instructions from the hunt table.
- **Replace:** two mandatory hunts with a medical-station repair and a shutdown-code recovery. Keep scrap collection as optional preparation.
- **Build:** complete two of three preparations: repair the medical station, secure the workers' exit, recover Kessler's reactivation order. Each earns a different benefit: one recovery station, fewer threatened civilians, or a machine-control opportunity. Allow the third for a bonus without requiring it.
- **Decision:** support the strike, negotiate a monitored shutdown, or enforce the company's reopening. Spell out labor and security consequences. Do not let separate conversations leave both strike-supported and strike-broken outcomes active.
- **Encounter:** RSX has a signaled approach/pressure phase and an interactable emergency stop unlocked by the recovered code. Failure at the code task offers a manual valve defense route.
- **State/payoff:** new `dm_arc07_preparation_mask` and `dm_arc07_labor_resolution`; derive existing flags. Workers or company engineers later offer different maintenance support in Act IV.
- **Journal:** show two preparations required, the benefit of each available task, and the agreed labor resolution. Once RSX starts, identify the emergency stop or manual valve route the party has unlocked.
- **Accept:** the medical task's requested materials match consumed items; all three resolutions grant equal base story EXP; support benefits are visible during RSX, not just in a later speech.

### A2-08 — Glast Heim: reconstruct the last watch

**Source:** [arc_08_glast_heim.txt](../../npc/custom/dm_campaign/act_02/arc_08_glast_heim.txt) — Aldric, Manfred, abbey. **Priority: P1.**

- **Replace:** Outer Garrison and Fallen Choir main-story gates with three memory sites: a watch post, a chapel record, and an evacuation marker. One optional bounty can remain for the approach.
- **Build:** recover fragments in any order. After two, the party can distinguish the evacuation order from the fatal command; the third identifies who altered it. Each site is a brief interaction plus a different small encounter, not three inventories of bones.
- **Decision:** release the watch from its oath or rebind it for one last defense with terms they understand. Manfred explains the cost; challenging his beliefs must not silently select “kill Manfred.”
- **Payoff:** released spirits clear an approach; a consenting watch helps during the abbey encounter. Existing Geffen reinforcement evidence adds context or a ward benefit but is never required to understand this arc.
- **State:** new `dm_arc08_memory_mask` and `dm_arc08_watch_resolution`; reconcile Manfred's mutually exclusive outcomes.
- **Journal:** discovered memories in chronological order, plus a concise inference the player can review before choosing.
- **Accept:** every discovery order works; two clues suffice; both outcomes have comparable encounter value; no conversation opinion alone starts a lethal resolution.

### A2-09 — Rachel: protect a witness while revealing the truth

**Source:** [arc_09_rachel.txt](../../npc/custom/dm_campaign/act_02/arc_09_rachel.txt) — Naima, Karsh, Ice Bleed Site. **Priority: P1.**

- **Replace:** two mandatory turn-ins with extracting an ice-core record and securing Naima's testimony. Keep samples as optional scientific collaboration with Vahl.
- **Build:** choose a public briefing with guard protection or a discreet witness transfer through two fixed checkpoints. This is a pressure scene about testimony, distinct from Yuno's evidence assembly. Failed concealment starts a defense encounter, not witness death by a single roll.
- **Decision:** immediate disclosure or a supervised evacuation followed by disclosure. State what can be lost in the delay. Keeping the secret permanently is a separate choice with a clearly recorded accountability cost.
- **Encounter/payoff:** evacuation authorization clears a safe approach to Gloom; public support opens a recovery point. A later message from Naima confirms what happened to her and the archive.
- **State:** new `dm_arc09_witness_secured` and `dm_arc09_disclosure_schedule`; derive exposed/deal flags so exposition and secrecy cannot both be final outcomes.
- **Journal:** next witness location, whether the archive is secured, and the promised publication condition.
- **Accept:** the party can protect Naima on either principal route; delayed disclosure resolves on an explicit scene event; changing maps or talking again does not restart the transfer.

### A2-10 — Lighthalzen: let Echo participate in the rescue

**Source:** [arc_10_lighthalzen.txt](../../npc/custom/dm_campaign/act_02/arc_10_lighthalzen.txt) — Reuter, Reise, Echo, Kiel Core. **Priority: P1.**

- **Replace:** the main-story material gates with disabling a patrol terminal, locating the research record, and opening Echo's containment control. Exploration actions grant the route; optional lab salvage remains separate.
- **Build:** Echo communicates before release and chooses between an assisted remote exit and a physical transfer. The party supports that stated preference. Never set `echo_freed` merely because somebody asks to let Echo reason with Reise.
- **Decision:** preserve testimony while containing the lab, or destroy the dangerous work after securing an independent copy of Echo's identity. Avoid an unannounced “save evidence means sacrifice Echo” trap.
- **Encounter:** during Kiel pressure, players activate two labeled emergency controls in either order. Escort is discrete scene transfer, not new pathfinding. A failed console check unlocks manual isolation with an extra defense phase.
- **State/payoff:** new `dm_arc10_containment_opened`, `dm_arc10_echo_exit`, and `dm_arc10_evidence_secured`; set existing `echo_freed` only after the exit resolves. Echo returns as an adviser in Arc 17.
- **Journal:** “Open Echo's containment” becomes “Secure the exit,” then a recorded outcome in Echo's own words.
- **Accept:** agreeing to help does not count as rescue; either exit can succeed; wipes preserve completed controls and restore only the unresolved encounter; Echo's later appearance matches the exit state.

**Act II exit:** party can distinguish evidence from accusation, identify an institution changed by its intervention, and describe Echo as a person with a preference rather than an item awarded by a dialogue choice.

## Act III — The Living Seals: assemble a coalition under pressure

**Player promise:** “Our allies change how these crises can be resolved.”  
**Act change:** stop making every arc two hunts, a three-answer villain menu, and an MVP. Use four distinct activities: a contested trial, cooperative stabilization, a treaty, and evacuation. Bosses remain useful where they express the crisis; combat is not the only proof of success.

### A3-11 — Hugel: earn cooperation through a trial

**Source:** [arc_11_hugel.txt](../../npc/custom/dm_campaign/act_03/arc_11_hugel.txt) — Eadric, Bjorn, Valkyrie Hall at `abyss_03`. **Priority: P1.**

- **Replace:** mandatory Gryphon/Dragon collection with two ward trials at fixed sites: protect an exposed keeper and interpret a damaged signal. Keep one hunt as optional support for the journey.
- **Build:** Bjorn witnesses the trial and argues his interpretation between stages. The party can show the signal's malfunction, accept his criticism of the city while contesting his remedy, or challenge his authority through the ward trial. Information questions do not automatically subdue him.
- **Choice/payoff:** recruit Bjorn as an accountable ally or proceed independently after disarming his obstruction. Joining requires an explicit agreement about protecting civilians. In the Randgris encounter, he disrupts one reinforcement wave; without him the party can operate the same ward itself during a longer interaction.
- **State:** new `dm_arc11_trial_mask`; use one final Bjorn outcome, then derive joined/subdued flags. Existing adds variation becomes an observable support action, not an invisible difficulty reduction.
- **Journal:** the two trial tasks, what they demonstrate, and the available ward interaction.
- **Accept:** independent play remains viable without a particular class; recruitment is earned through a scene; either outcome can clear the hall; players can identify what Bjorn changed.

### A3-12 — New World: stabilize together

**Source:** [arc_12_new_world.txt](../../npc/custom/dm_campaign/act_03/arc_12_new_world.txt) — Aelith, Vance, Rift Anchor. **Priority: P1.**

- **Replace:** the two collection gates with recovering survey information and stabilizing three anchor points. Naga contact becomes an actual parley or contested passage before the anchor, not a post-hunt claim that the party avoided violence.
- **Build:** activate anchors sequentially; each holds its state so simultaneous switches and split-party latency are unnecessary. Different roles can read a signal, defend an operator, or repair a conduit. All tasks also have a basic assisted interaction for parties missing the relevant skill.
- **Decision:** put Vance's expedition under joint supervision or requisition the survey and remove his authority. Helping must include a concrete commitment to local access and limits on extraction.
- **Encounter/payoff:** successful negotiation places a survey crew at one anchor. Without it, the party repairs that point itself. Completing stabilization creates a vulnerability phase for the existing encounter. Failed timing adds one bounded pulse cycle, never an infinitely escalating hazard.
- **State:** new `dm_arc12_anchor_mask` and `dm_arc12_survey_agreement`; map the latter to existing Vance flags.
- **Journal:** anchors stabilized, next interaction, and the visible pulse interval.
- **Accept:** solo/sequential fallback works; pulses stop on reset; a disconnect preserves completed anchors; bargaining and force both have mechanically complete approaches.

### A3-13 — Nameless Island: negotiate an enforceable treaty

**Source:** [arc_13_nameless_island.txt](../../npc/custom/dm_campaign/act_03/arc_13_nameless_island.txt) — Quill, Carrion, Beelzebub. **Priority: P0 choice repair, then P1.**

- **Fix first:** “What is the catch?” currently sets the killed outcome; asking about the cascade currently sets the deal outcome. Both become repeatable, non-mutating questions followed by explicit Accept / Reject / Discuss actions.
- **Replace:** compulsory Abbey Bell/Sanctum collection with inspecting two ward failures and recovering a treaty witness. Keep salvage optional.
- **Build:** Carrion presents terms the party can investigate: containment boundary, civilian passage, and who monitors breaches. One recovered ward record reveals a loophole; the party can demand a monitoring condition or knowingly accept the risk. Do not build a general negotiation simulator—three authored clauses are enough.
- **Resolution:** accept and supervise one containment demonstration, or reject and enter the existing Beelzebub encounter. Neither path gets an inferior base story reward. Completing the demonstration, not merely saying yes, earns the treaty-complete flag.
- **State/payoff:** new `dm_arc13_treaty_terms` and `dm_arc13_treaty_verified`; reconcile bribed/killed/deal-honored flags. Rename player-facing “bribed” to “treaty agreed” where that is what actually occurred. Later safe passage depends on honoring the agreed boundary.
- **Journal:** exact agreed terms and the next verification task; distinguish proposed from ratified.
- **Accept:** every question leaves progression and inventory unchanged; declining after questions remains possible; only one resolution grant occurs; the treaty route genuinely skips the boss and still resolves the arc.

### A3-14 — Veins: get people out before confronting the heat

**Source:** [arc_14_veins.txt](../../npc/custom/dm_campaign/act_03/arc_14_veins.txt) — Dunmar, Hesma, Magma Cathedral. **Priority: P1.**

- **Replace:** both compulsory collection gates with opening an evacuation route and securing two worker groups. Optional mineral salvage is explicitly unsafe to prioritize until evacuation is complete.
- **Build:** three discrete crisis steps: inspect the route, clear or brace its obstruction, move the groups. Each advance is triggered by completing a task, not by real-world reading time. At each step players see whether the route or equipment will be lost if they choose salvage first.
- **Decision:** force public evacuation authorization or use Hesma's private approach access and document accountability afterward. Both can save workers. Neither a critical failure nor a disconnect kills unseen civilians without a recoverable scene.
- **Encounter/payoff:** workers who reach safety reveal a cooling bypass; activating it creates a predictable safe lane during Ifrit pressure. Other parties can discover and repair the bypass themselves at extra encounter cost.
- **State:** new `dm_arc14_evacuation_stage`, `dm_arc14_groups_saved`, and `dm_arc14_bypass_ready`; retain the existing Hesma outcome as a separate political result.
- **Journal:** worker groups safe, remaining route task, and optional salvage marked as optional.
- **Accept:** threat increases only at documented scene transitions; both access routes work; survivors appear at Dunmar's camp; the safe lane matches the server hazard geometry.

**Act III exit:** the four arcs feel different in play. At least two alliances have delivered observable aid; rejecting an ally remains a supported route. The DM can explain the party's treaty obligations without searching through old chat.

## Act IV — The Seal's Edge: make the past actionable

**Player promise:** “The world we helped shape determines what we can responsibly choose now.”  
**Act change:** retire mandatory collection gates. Each arc prepares one part of the final decision: informed consent, political legitimacy, technical capability, a pact with the dead, and execution. Bring back people; shorten recap lectures. Present facts and consequences without making Loki the final judge of the players' motives.

### A4-15 — Thanatos: experience the cost before choosing it

**Source:** [arc_15_thanatos.txt](../../npc/custom/dm_campaign/act_04/arc_15_thanatos.txt) — Lysandra, Pratt, Memory of Thanatos. **Priority: P1.**

- **Replace:** both hunts with three short memory scenes: the offer, the first failure of the seal, and the maintenance burden centuries later. Use existing NPC/encounter scenes with narration rather than new cinematic assets.
- **Build:** each memory asks the party to perform one bounded task—hold a ward, relieve its operator, recover a missing record. No memory permanently traps a player or demands that one person stand idle for minutes. Let players rotate roles.
- **Decision:** interrupt Pratt's uninformed experiment, delay it pending disclosure, or confront him with the full record and establish a consent procedure. The question about hidden costs must be safe to ask before committing.
- **Payoff:** record what the party knows about the personal-seal option. A surviving witness or Lysandra explains that option in the finale; no one is selected as a sacrifice by completing this arc.
- **State:** new `dm_arc15_memory_mask` and `dm_arc15_cost_disclosed`; derive Pratt outcomes after the resolution. Existing Thanatos encounter becomes the final memory defense, not a substitute for the revelation.
- **Journal:** a short “What the seal costs” record with known facts and unresolved risks.
- **Accept:** the party can restate the personal cost in its own words; every experiment resolution advances; no character loses control or permanent playability as a surprise effect.

### A4-16 — Prontera Banquet: return to people who remember

**Source:** [arc_16_prontera_banquet.txt](../../npc/custom/dm_campaign/act_04/arc_16_prontera_banquet.txt) — Heine, Rina, Prison Vault. **Priority: P1.**

- **Replace:** both collection gates with a three-station social investigation: a witness interview, a seating/guest record, and a intercepted instruction. Any two identify the infiltration route; the third protects an additional witness.
- **Build:** use three existing-map NPC stations and a small testimony menu. A returning ally from Act I/II appears at one station based on recorded outcomes; a neutral clerk fills the slot if none is available. A failed social check costs discretion and changes the vault approach, not access to the essential clue.
- **Decision:** expose Rina publicly, compel a monitored dismantling of the network, or accept a defection with protection terms. A defection reveals a concrete interaction to free Maret during the vault encounter.
- **Payoff:** freeing Maret requires that interaction to succeed. Do not infer rescue solely from having selected Rina's defection earlier. The rescued person speaks afterward and can appear in Niflheim's later account only in an appropriate form.
- **State:** new `dm_arc16_evidence_mask` and `dm_arc16_release_completed`; maintain mutually exclusive Bijou-killed/Maret-freed results. Krenn's prior story changes testimony, not the existence of a required clue.
- **Journal:** known suspects versus confirmed facts, protected witnesses, and the release task if learned.
- **Accept:** no single clue or ally is mandatory; all three confrontation routes work; actual rescue and lethal resolution cannot both be recorded; the banquet changes based on at least two earlier-act outcomes.

### A4-17 — Varmundt: prove a solution works

**Source:** [arc_17_varmundt.txt](../../npc/custom/dm_campaign/act_04/arc_17_varmundt.txt) — Tressa, Administrator, Biosphere Core. **Priority: P1.**

- **Replace:** both hunts with a controlled test of the counter-frequency system. Recover the design, isolate a test chamber, then run a prototype cycle against three labeled faults.
- **Build:** players repair, defend, and verify readings in sequence. Echo, if rescued, translates one fault and asks how copies of living minds will be treated. Without Echo, a slower manual record supplies the same essential information.
- **Decision:** shut the Administrator down after exporting the design, retain it under agreed limits, or continue a broader partnership. “Shut down” must not silently destroy the only copy of a campaign-critical solution.
- **Payoff:** successful testing earns the machine ending's feasibility record. Workers/engineers from Einbroch can offer maintenance support, but no single old ally is required; a new consenting maintenance team is a fallback preparation task.
- **State:** new `dm_arc17_design_exported`, `dm_arc17_prototype_verified`, and `dm_arc17_maintenance_secured`; keep existing Administrator outcomes mutually exclusive.
- **Journal:** prototype faults remaining, test result, and who will maintain it.
- **Accept:** every Administrator resolution can preserve the design if explicitly chosen; interrupted tests resume without duplicating rewards; the ending is not labeled ready until both prototype and maintenance are resolved.

### A4-18 — Niflheim: hear the dead, then negotiate

**Source:** [arc_18_niflheim.txt](../../npc/custom/dm_campaign/act_04/arc_18_niflheim.txt) — Familiar Dead, Himmelmez. **Priority: P0 commitment clarity, then P1.**

- **Replace:** both mandatory hunts with two short audiences drawn from earlier outcomes. Choose applicable named characters; supply an ordinary lost traveler and a former seal keeper when no named deceased character fits. Do not kill a living ally retroactively to populate a scene.
- **Build:** one audience asks for an acknowledgment or returned memory; the other describes the burden of containment. Their account reports what happened without dictating whether the party was morally correct. Players may answer, apologize, dispute the account, or decline.
- **Decision:** negotiate Himmelmez's pact with explicit obligations, refuse and leave, or deliberately challenge her. Refusal must not be synonymous with killing. Challenging starts a clearly announced DM-resolved confrontation/pressure scene; it is not an instant kill hidden behind “This ends here.” A full new boss asset is outside this slice.
- **Payoff:** an agreed pact identifies the containment boundary and her ongoing cost. Her actual continued availability controls the corresponding ending. Rebalance the currently different kill/bargain story EXP so violence is not the default optimization.
- **State:** new `dm_arc18_resolution` (pact/refused/challenged-resolved) and `dm_arc18_pact_valid`; derive killed/bargained flags only from completed outcomes.
- **Journal:** two short testimony records and the precise pact, if any.
- **Accept:** refusal advances to the finale without a fabricated death; queries never commit; two earlier decisions alter the audiences where applicable; only an intact pact enables its ending.

### A4-19 — Finale: prepare and enact the chosen answer

**Source:** [arc_19_finale.txt](../../npc/custom/dm_campaign/act_04/arc_19_finale.txt) — Loki, Surt, Central Choice. **Priority: P0 ending guards, then P1.**

- **Replace:** Beyond the Veil's compulsory item turn-in with a final preparation board. Make any surviving collection version optional and remove its gate from `S_Progress` and corresponding DM beats.
- **Build:** Loki delivers a short required account: the failing seal, the immediate threat, and the decision ahead. Put the long historical callbacks behind “Review our journey.” Let up to three relevant allies deliver their own optional accounts. The party prepares available solutions before Surt; eligibility is checked again at the final commitment.
- **Encounter:** retain Surt and the rift, but give each prepared solution an authored support action using the shared hazard/interaction framework. A support action can alter one wave, stabilize a ward, or provide one recovery opportunity. It should not require five completely different boss implementations.
- **Decision:** show all five concepts with Ready / Needs preparation / Unavailable explanations. Never claim all five are earned regardless of earlier choices. The party can return to preparation before committing; a final action goes through group discussion and an explicit confirmation.
- **State:** new `dm_arc19_prepared_mask`, a canonical `dm_arc19_final_choice`, and a named volunteer reference where applicable. Derive exactly one existing `dm_finale_*` flag. Revalidate and claim the final transition on the server before granting rewards; two simultaneous NPC conversations cannot choose two endings.
- **Journal:** show each solution's readiness, missing preparation and known cost; record the committed ending and its three outcome cards afterward. Keep unrevealed testimony and DM repair controls out of the player view.
- **Payoff:** after confirmation, play a short implementation scene, then three outcome cards: an affected place, a named person, and the new obligation. Base the cards on actual state, not an unconditional victory announcement. Leave the party at a safe hub with the recap available.
- **Accept:** all readiness cases in the matrix below pass, including unavailable choices; a late disconnect pauses commitment; the final state is exclusive and rewards occur once; players see what their selected answer costs after the last fight.

### Ending eligibility and fallback matrix — proposed rules

These are design decisions for implementation, replacing the current unconditional menu. “Available” means the approach can be prepared; “Ready” means it is safe to commit now.

| Ending | Ready only when | Preparation/fallback | Cost presented before commitment |
|---|---|---|---|
| Shared Seal | Two distinct groups have explicitly agreed to share maintenance; the distribution rite is prepared | Invite recorded allies. If fewer than two are available, recruit a new consenting civic group through a short preparation scene; never turn an old numerical ally tally into automatic consent | Recurring coordination and maintenance; participating groups share the burden voluntarily |
| Reforged Seal | Design exported, prototype verified, maintenance team secured | Recover a preserved research copy and complete an abbreviated test if the Administrator was shut down; recruit engineers if old allies decline | Power, repair, and public responsibility for keeping the machine running |
| Queen's Bargain | Himmelmez remains available and `pact_valid` is true | A prior refusal permits returning to negotiate if she is still available. Her death makes this route unavailable; do not resurrect her through a menu | The agreed obligations to the dead and her continued burden; do not describe an untested arrangement as guaranteed permanent |
| Thanatos's Road | Cost disclosed and a named, informed volunteer has explicitly consented | An authored willing NPC may volunteer after disclosure. A player volunteer is optional and requires that player's consent; never delete, disable, or retire their character automatically | What carrying the seal entails; distinguish epilogue sacrifice from changes to playable-character access |
| Ragnarok Unbound | Party explicitly accepts release and completes the emergency evacuation/containment preparation | Always has a reachable preparation route; no specific ally, technical result, or sacrifice is required | Uncertain consequences and immediate danger; no promise that the released power will be friendly |

**Minimum automated matrix:** each route ready; each individual prerequisite absent; Queen pact with killed flag also present; two conversations committing different endings; missing/disconnected player volunteer; repeated commit; resume after Surt but before choice. Contradictory legacy state must produce a DM repair explanation, not a guessed resolution.

**Act IV exit:** the players can say why their ending was available, name its cost, and identify two earlier decisions that mattered. They have played at least one preparation action for that ending rather than selecting an unexplained final button.

## Implementation handoff

### Shared work packages

| Ticket | Priority | Deliverable | Dependencies / owner |
|---|---|---|---|
| SC-00 Decision integrity | P0 | Audit all `select` branches; separate questions from mutation; enforce exclusive outcomes; fix Carrion and ending prerequisite guards first | Narrative + Hercules; no new client protocol required for initial explicit action menus |
| SC-01 Quest truth | P0 | Reconcile NPC prose with generated item requirements, names, reference docs and actual completion conditions; verify location instructions | Narrative + Hercules; `db/dm_hunt_db.json` remains source for retained hunts |
| SC-02 Group commitment | P1 | Party-visible proposal, discussion pause, explicit DM commit/cancel, exactly-once decision record; personal-consent check | Hercules shared helpers + DM interface; retain command-based fallback |
| SC-03 Scene checkpoint/recovery | P1 | Inspectable scene stage, durable campaign identity, checkpoint save, explicit rejoin/repair, grant ledger, timer cleanup | Hercules; do not mistake per-online-character variables for a full session ledger |
| SC-04 Journal objectives | P1 | Titles, objective descriptions, named destinations, progress, recap, proposed/committed consequences; completed-history data contract | Korangar + Hercules; use existing packets where adequate; separately specify any missing transport |
| SC-05 Reusable interaction scenes | P1 | Inspectable objects, bounded progress steps, signaled defense/pressure, sequential controls, optional check + assisted fallback | Hercules; reuse existing maps and hazards, verify cells; client cues must reflect server state |
| SC-06 Arc 1 reference delivery | P1 | Playable A1-01 including optional hunt migration, state/reward guards and journal entry | SC-00/01 plus minimum SC-02–05; validate before duplicating across arcs. Concrete tickets: [act-01-implementation-plan.md](act-01-implementation-plan.md) |
| SC-07 Remaining arc deliveries | P1 | Implement each brief as one reviewed vertical slice with its explicit acceptance checks | After SC-06 acceptance; share helpers rather than copying controllers |
| SC-08 Presentation pass | P2 | Ambient consequence cues, testimony/epilogue cards, optional illustrated recap and richer objective HUD | After underlying state is reliable; no invented progress or leaked DM notes |

**Suggested order:** SC-00 and SC-01 → minimum shared support → Arc 1 → Arc 2 → complete Act I → Act II → Act III → Act IV. Apply the P0 fixes in Arcs 13/18/19 early even though their redesigns come later. Do not wait for a new HUD or custom art to playtest the Arc 1 interaction loop.

### State and save rules

- Adopt one durable campaign identity distinct from a temporary instance ID or the current party roster. Record decisions/checkpoints against it and explicitly reconcile participating characters. The storage schema is an engineering deliverable in SC-03, not implied by existing `DM_Instance*` names.
- A scene uses a small explicit sequence such as `not_started → investigating → prepared → resolving → complete`, with a separate branch outcome. Do not represent an in-progress promise as a finished rescue.
- Each new variable needs a declared meaning, value range, writer, readers, reset behavior, and downstream callback. Prefer an enum-like single result over incompatible booleans. Derived legacy flags must be written together from that result.
- Add inspect/repair entries to the relevant DM helpers and handbook. Use the existing quest/flag wrappers for synchronized online updates; add durable reconciliation through the shared checkpoint mechanism rather than writing arbitrary character variables in each NPC.
- Use the existing `DM_ClaimGrant` pattern or a compatible centralized grant ledger for scene rewards and ally recruitment. A revisit, reconnect, or duplicate boss callback must not grant twice.
- Rejoining members inherit the committed story state through an explicit reconciliation operation. Do not award all missed optional loot automatically. Define story participation and reward eligibility separately and show the DM the proposed repair.
- Preserve already completed legacy arcs. Retained accepted bounties remain completable as optional content. When importing a mid-arc save, map completed hunts to preparation credit only where justified; never remove earned items or replay already paid story rewards. Record which legacy grants were consumed before paying new milestones.
- Run migration as a previewable operation, with a recorded pre-migration checkpoint. Conflicting old flags require a DM choice of the canonical outcome; no silent “first flag wins.” A load into the new version must never reset the entire campaign.

### Content implementation surface

For each delivered arc, update:

1. Its linked `act_*/arc_*.txt` script: entry gates, actual interactions, action menus, reward guards, recovery labels, return dialogue.
2. `shared/dm_beats.txt`, the flag/quest/session helpers and `dm_handbook.txt`: the same progression rules through NPC and DM paths, with readable inspect and reset operations.
3. `db/quest_db.conf`: preserve existing IDs where the quest still represents the same promise. Reserve and document new IDs before adding materially different side quests. Never silently repurpose a completed ID into unfinished required content.
4. `db/dm_hunt_db.json` and `tools/gen-hunts.py` outputs if a retained contract changes. Do not hand-edit `shared/dm_hunts.txt` or the generated client requirements TSV. Run generation and its drift check.
5. Client quest metadata and objective handling. The September 6 journal refresh adds names/search/collection progress in source; it does not supply this richer narrative state. Do not mark this dependency done because the window opens.
6. `CAMPAIGN.md`, this brief's implementation status, and the focused test record. Keep known legacy behavior separate from intended new behavior.

### Narrative/editorial instructions

- Keep Wynne practical, Sun-Hwa attentive to names and relationships, Vahl specific about evidence, Greta concerned with work and people, and Echo capable of disagreement. Do not give every NPC the same sardonic cadence or abstract vocabulary about systems and maintenance.
- Before a major decision, write three blocks: what the NPC knows, what the party can ask, and what the explicit commitments do. Test the wording independently of the script branch labels.
- Target two short paragraphs before offering an interaction. Longer history belongs behind optional questions or recap entries. These are drafting constraints, not a ban on dramatic scenes that the table chooses to hear.
- Acknowledge the player's stated motive; do not have Loki assert why the party acted when only the action is recorded. NPCs can disagree about consequences without the narrator declaring a single moral score.
- Reuse a few named relationships across acts. New allies should arrive with a role and a desire, not only a proper noun and a lore paragraph.
- Optional contracts should fund a believable local need. Avoid having a title promise rescue, investigation, or diplomacy when the actual objective is collecting unrelated monster drops.

### Example handoff payload — Arc 1 objective

This is an authoring example, not a new wire format. Engineering should adapt it to the approved metadata/state contract.

| Field | Proposed content |
|---|---|
| Player title | Follow the Humming Water |
| Purpose | Find why the city's water vibrates and where the missing girl's trail leads |
| Current objective | Ask Tibbets about the painted sluice gates |
| Location label | Prontera — near the fountain; then the Culvert approach |
| Progress source | Server-owned clue bits; two clues reveal the chamber route |
| Optional preparation | Drain the Listening Chamber; reduces one reinforcement wave |
| Resolution condition | Listening Chamber scene resolved; Holt outcome committed |
| Recovery text | Tibbets can show the route if a clue was missed |
| Completion recap | The sigils led beneath the city. Include the actual child, drain and Holt outcomes |
| Visibility | Party objective/recap public to participants; encounter controls and unrevealed branches DM-only |

### Acceptance and playtest protocol

Automated tests establish state correctness; a real group establishes whether the activity is enjoyable and understandable. Do not substitute one for the other.

**For every arc:** exercise each authored route, one failed check, duplicate interaction, duplicated completion callback, one disconnect/rejoin, and a DM reset during the active hazard. Check exclusive outcomes, exactly-once rewards, journal reconstruction, and a reachable next objective. Test with the intended regular-player group permissions, not only a GM character. Audit every new spawn, interaction approach and warp destination against the loaded maps.

Use `tools/check-campaign.sh` and `tools/gen-hunts.py --check` for existing static coverage. Extend the repository's campaign headless scenarios for new state invariants; do not claim they cover new branches until those assertions exist. Run the relevant client tests and live graphical checks when journal/scene presentation changes.

**Four-player session record:** record party level/equipment, time to first meaningful choice, time spent traveling or repeating kills without a new decision, number of “where now?” interventions, which players took an action, understood consequences, and recovery after one staged interruption. Ask each player to state the next objective before the DM explains it. The DM records whether manual repair was needed and why.

**Initial acceptance targets, to tune after the first session:**

- First meaningful action/choice within ten minutes of starting Arc 1.
- No more than two unexplained “where now?” stalls in a normal arc; any repeated stall becomes a named content/UI defect.
- Every player has an opportunity to investigate, operate, negotiate, defend, or assist; no specific job is mandatory for main progression.
- No compulsory repeated farming as the only means of reaching the next story scene in the redesigned route.
- No player mistakes an information question for a commitment, or collected items for a completed rescue.
- One visible local consequence and one planned later callback per major decision.
- A staged disconnect resumes at the last valid scene without duplicated payment or lost completed objectives.

### Reviewable completion package per arc

Deliver the changed scripts and metadata, a short before/after quest-flow description, a state/branch table, migration notes for an in-progress legacy save, automated results, and a live session record. Include screenshots of objective/decision/recovery states at laptop UI scales 1.0, 1.3 and 1.5 where client changes are involved. List remaining presentation gaps explicitly.

The arc is ready to hand to the regular group when its core routes work, instructions agree with behavior, and players can describe the consequence they just caused. “All files parse” and “the boss can die” are necessary checks, not campaign acceptance.
