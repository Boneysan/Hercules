# Seal Cascade — deep-dive review, 2026-10-02

**Status:** Findings, then the work done from them. Slices 1–6 are in the working tree (uncommitted); see the "Done" sections.
**Builds on:** [act redesign handoff](seal-cascade-act-redesign.md) (2026-09-06), the 2026-08-18 editorial review, and [Act I implementation plan](act-01-implementation-plan.md). It does not repeat them; it measures the scripts as they stand today and says what is still open.

## Method and limits

- Counted, per arc, with a throwaway script over `npc/custom/dm_campaign/act_*/arc_*.txt` (comment lines stripped): `DM_HuntCollect` gates, `DM_AssertWalk` (a world action the party performs), `DM_EncMonster`/`DM_EncStart` (encounters), `DM_HazardArea`, `DM_SceneClaim`, `select(` menus, and flags set.
- A flag counts as **consumed** only if some script other than the registries `shared/dm_flags.txt` and `shared/dm_quests.txt` mentions it outside a set/clear call. Those two files list every flag for inspect/reset, so they say nothing about the story.
- I read **Arc 6 in full**, the finale's ending code, and the handoff. I did **not** read Arcs 7–18 line by line, so claims about their prose are inferred from the measurements, not from reading them. Quest journal text in `quest_db.conf` was not reviewed.
- The flag counts are not comparable with the 2026-08-18 review (177 set / 108 read); that used a different method.

## What the numbers say

| Arcs | World actions | Encounters | Scene claims | Select menus | Flags set |
|---|---|---|---|---|---|
| 1–5 (Act I) | 7–11 each | 3–11 each | 2–5 each | 12–19 each | 17–37 each |
| 6–19 (Acts II–IV) | **0** | **0** | **0** | 2–5 each | 4–9 each |

1. **The redesign shipped for Act I only.** `CAMPAIGN.md` and the scripts agree: Arcs 1–5 are investigate / operate / rescue / talk. Arcs 6–19 are still the old shape, one NPC hub, 2–3 collection errands, a three-way menu per turn-in, then the boss. The "Quest started" text in Arc 6 lists three collection errands (harpy feathers, Juperos parts, sand samples) before anything story-relevant happens.
2. **Acts II–IV are about 300 lines per arc against about 700 for Act I.** That is not a quality judgement on the writing; it is where the interactivity and branching went.
3. **Quest data is consistent.** All 86 campaign quests (20001–20233) are in `quest_db.conf`; none is unreferenced; every objective monster exists in `mob_db.conf`. The two "undefined" ids my sweep flagged (20000, 20500) are zeny/exp amounts, not quests.
4. **Fifteen real decisions go nowhere.** Of the 59 flags set in Arcs 6–19, 29 have no consumer. 14 are `_started` markers, which is fine. The other 15 are choices or outcomes no later arc, beat, or ending reads:
   `arc06_mistress_killed`, `arc07_strike_broken`, `arc10_reise_confronted`, `arc12_naght_killed`, `arc12_vance_exposed`, `arc14_ifrit_killed`, `arc15_pratt_delayed`, `arc15_thanatos_killed`, `arc16_bijou_killed`, `arc16_maret_freed`, `arc16_rina_exposed`, `arc17_admin_negotiated`, `arc17_admin_purged`, `arc18_himmelmez_killed`, `arc19_surt_defeated`.
   The boss-kill ones are partly by design (terminal). The ones that matter are the choices: `vance_exposed`, `rina_exposed`, `admin_negotiated` / `admin_purged`, `strike_broken`, `pratt_delayed`, `maret_freed`, `reise_confronted`.
5. **The ending ignores what the party did.** `arc_19_finale.txt` offers five endings through one menu. All five are always available, and each only sets one flag and plays a paragraph. 35 references to earlier arcs' flags appear in the file, but none changes which endings exist or what the epilogue says. The thesis (who pays, and did they consent) is stated in the speeches and then not tested by the mechanic.
6. **"Thanatos's Road" has no mechanism for who volunteers.** It says one person becomes the lock. Nothing in the scripts picks, asks, or records which player, and (per the 2026-08-18 review) the Sigil Ring that could have built toward it disappears after Act II.

## Proposed order of work

Ordered by value for the cost; each is one bounded slice.

| # | Slice | Why | Size |
|---|---|---|---|
| 1 | **Finale reads the ledger.** Epilogue text and 1–2 ending-specific consequences chosen from the 15 orphan decisions plus ring/Carrion/Cassell callbacks. No new maps. | Highest payoff per line; makes every earlier choice visible once. | small |
| 2 | **Thanatos's Road gets a volunteer.** The party discusses, the DM confirms who accepts, the character's own flag records it (per-character, S10 pattern), the epilogue names them. | The thesis ending currently has no player in it. | small–medium |
| 3 | **Wire the choice orphans** at the point where each happens (Vance, Rina, Varmundt's admin, Reise) into a later NPC line or support action ("show the consequence twice", handoff rule 6). | Fixes item 4 without new content. | medium |
| 4 | **Rebuild Act II (Arcs 6–10)** to the Act I pattern, using the handoff's A2 briefs, and vary the moral question so the four institutions stop being the same expose-or-be-bought choice. | The weakest act, and the largest block of repeated structure. | large (5 arcs) |
| 5 | **Carry the Sigil Ring** through Acts III–IV and into the Road. | Gives the party a stake. Depends on 2. | medium |
| 6 | **Rebuild Acts III and IV** the same way, after Act II proves the pattern. | Biggest scope; do last. | large (9 arcs) |

Slices 1–3 improve the whole campaign without rebuilding any arc, and only touch `arc_19_finale.txt`, shared flags, and a few NPC lines. I would do them first.

## Done 2026-10-02 (slices 1–3; script loads clean, not played)

| Slice | Change | Files |
|---|---|---|
| 1 | After the chosen ending, `S_Epilogue` reads Acts II–IV decisions (Pratt exposed/delayed, ally turnout, Rina, Vance, Varmundt's Administrator, Einbroch strike, Himmelmez) and prints 1–4 tailored lines, then a closing line. **Fixes a contradiction:** if `dm_arc18_himmelmez_killed`, the Queen's Bargain no longer says "Himmelmez holds the seal"; it says the dead hold it without anyone's consent. | `act_04/arc_19_finale.txt` |
| 2 | Thanatos's Road now needs the *speaking* character to volunteer and confirm twice; declining returns to the five paths. Sets `dm_finale_road_volunteer` on that character only (`DM_SetFlag`: not party-wide, not journaled, not copied on rejoin, not in the enrolment copy list). The epilogue names them; on a return visit only that character sees "the seal is you now". Registered in `DM_ClearArc19Flags`. | `act_04/arc_19_finale.txt`, `shared/dm_flags.txt` |
| 3 | Arc 18 now distinguishes Maret freed alive from Bijou killed (the dead mention her either way). The other apparent orphans turned out to be either consumed in the epilogue (strike, Vance, Pratt, Administrator, Himmelmez) or already read as in-arc gates (`reise_confronted`, `rina_exposed`); boss-kill flags are terminal by design. | `act_04/arc_18_niflheim.txt` |

**Assumptions I made where you had not answered:** endings are tailored, not removed (decision 2); the Road volunteer is a per-character flag plus epilogue naming (decision 3); the Acts II–IV briefs in the handoff stand as direction (decision 4). All new prose is a draft for your edit.

**To preview without playing 19 arcs** (DM console): `@dm reset confirm` is destructive — instead set flags on a test character with `@dmflag set <flag> <value>` (usage line: `@dmflag` with no arguments; the exact argument order was not tested) — e.g. `dm_arc18_himmelmez_killed`, `dm_arc15_pratt_exposed`, `dm_arc19_surt_defeated`, start the session, and talk to *The Central Choice* at `moc_fild22,175,140`. Try each of the five endings, and the Road with a decline, a confirm, and a second character's return visit.

## Done 2026-10-02: Acts II–IV rebuilt (slice 4, 5, 6)

Owner direction: "overhaul it all" (the party is only a few quests into Act I, so none of this had been played). All 14 arcs, 6–19, now follow the Act I pattern: world actions and guarded sites instead of item errands, inert questions, explicit final commitments with a confirm, equal base EXP per route, and a derived-flag layer so later arcs still read the old names. Quest ids are unchanged. The old collection contracts survive as **optional** side work with about a third of their old reward and are locked or offered, never required.

| Arc | New structure | New state (derived compat flags in brackets) |
|---|---|---|
| 6 Yuno | evidence: 2 plateau posts + Krenn's drawer + Juperos recorder; any two open a hearing; disclosure named / anonymous / protected / buried | `evidence_mask`, `posts`, `post_fail`, `krenn_alerted`, `disclosure_mode` (krenn_exposed, krenn_bribed, `krenn_cooperated`) |
| 7 Einbroch | 3 preparations (medical station, workers' exit, Kessler's order), any two; labor decision support / monitored shutdown / enforce; RSX has a cot, an emergency stop or two manual valves | `prep_mask`, `code_failed`, `labor_resolution` (strike_supported / broken / `negotiated`) |
| 8 Glast Heim | 3 memory sites each with a different fight; two reveal the order, three reveal who altered it (Manfred, with Aldric's courier mark); release / rebind / leave; a recovery banner for rebind | `memory_mask`, `watch_resolution`, `manfred_confessed` (manfred_spared / killed) |
| 9 Rachel | extract the ice-core record, protect Naima's testimony by public briefing or two checkpoints, then disclose now / evacuate first / keep secret; a safe approach or a recovery post | `record`, `witness_route`, `witness_secured`, `disclosure_schedule`, `approach_safe`, `secret_kept` (karsh_exposed / deal) |
| 10 Lighthalzen | patrol terminal, research record, containment control; Echo is a character who states a preference and is freed only when her chosen exit resolves; preserve or destroy the work (preconditions stated first); two Kiel emergency controls | `patrol_disabled`, `evidence_secured`, `containment_opened`, `echo_exit`, `lab_resolution` (echo_freed set only on resolution) |
| 11 Hugel | two ward trials with Bjorn arguing between them; he joins only by an explicit civilian-protection pact; a ward in the Hall that breaks a wave | `trial_mask`, `signal_partial`, `bjorn_outcome`, `civilian_pact` (bjorn_joined / subdued) |
| 12 New World | recover the survey, decide Vance's expedition, parley or contest the Naga, three anchors in order, vulnerability window on Naght Sieger | `survey_recovered`, `survey_agreement`, `naga_passage`, `anchor_mask` (vance_helped / exposed) |
| 13 Nameless Island | questions are inert; two ward failures + a treaty witness; three authored clauses; a treaty counts only after a supervised containment demonstration, which resolves the arc without the boss | `ward_mask`, `witness`, `treaty_terms`, `treaty_verified` (carrion_bribed = "treaty agreed", coalition_deal_honored) |
| 14 Veins | evacuation in three discrete steps, Hesma's authorization public or private (with a ledger), a cooling bypass that shrinks Ifrit's hazard from 8 cells to 5 | `evacuation_stage`, `groups_saved`, `bypass_ready`, `authorization`, `accountability_logged` (hesma_exposed / bribed) |
| 15 Thanatos | three memory scenes (hold a ward, relieve the operator, recover the record); confront Pratt only with all three | `memory_mask`, `cost_disclosed`, `pratt_resolution` (pratt_exposed / delayed / challenged) |
| 16 Banquet | three social stations (a returning ally at each when the record says they exist); Rina exposed / monitored / defection with protection terms; Maret freed only by opening her cell, never inferred | `evidence_mask`, `discretion_lost`, `rina_resolution`, `release_known`, `release_completed` (maret_freed / bijou_killed) |
| 17 Varmundt | design archive, isolated chamber, three faults (repair / defend / verify, Echo translates or a slower manual pass), a maintenance team; shutdown never silently destroys the design | `design_recovered`, `chamber_isolated`, `fault_mask`, `prototype_verified`, `maintenance_secured`, `design_exported`, `admin_resolution` |
| 18 Niflheim | two audiences first; Himmelmez: pact / refuse and leave (she lives, the pact stays takeable) / challenge (announced, DM-resolved); equal EXP so violence is not the default | `audience_mask`, `resolution`, `pact_valid` (killed only when the DM resolves a challenge as her fall) |
| 19 Finale | short required account; history and allies' accounts on request; a preparation board; five answers shown Ready / Needs preparation / Unavailable with costs; re-checked at commitment and claimed once per party; support actions in the Surt fight; implementation scene, epilogue, three outcome cards | `briefed`, `groups_agreed`, `prepared_mask`, `volunteer_kind`, `final_choice` (exactly one `dm_finale_*`) |

**Checks that pass** (`./dev.sh` boot, `--run-once`): every script loads with no `[Error]`; every visible NPC is on a walkable tile (14 of 38 Act II–IV NPCs were on unwalkable placeholder tiles before, and Arcs 8–19 had no `DM_AssertWalk` at all); no `select` label contains `:`; every new flag is registered for reset, inspect and rejoin-copy; every new grant key is in the party-grant list. Of 134 flags set in Arcs 6–19, 15 are never read by a script: boss-kill markers, act-complete markers and ending flags (terminal by design), duplicate compat flags, and `dm_story_beat` (the DM's own beat log).

**Bugs found on the way**
- `DM_CheckRoll` returns a band (-1 fumble … 3 critical), so the old `!callfunc("DM_CheckRoll", …)` treated a fumble as a success. Acts II–IV now test `< 2`. One copy remains in Act I (`arc_02_payon.txt`, the memorial check); not touched.
- Arc 14's `Magma Cathedral` set-piece uses `OnMagmaStart`/`OnMagmaStop`; an earlier draft of mine invented different labels. All set-pieces in this pass were copied from the originals, not retyped.
- Hercules treats `:` inside a `select` label as a choice separator.

**Not verified (important)**
- **Nothing here has been played.** Loading clean proves syntax and walkability, not behavior. No headless scenario covers Acts II–IV NPC logic (the single scenario that mentions an Act II quest uses `@dmquest` only).
- Rebuild numbers (EXP splits, check DCs, monster levels, hazard damage, support-action strength) are my first estimates and need a table to tune them. The 60 / 40 split follows the handoff's rule 5 by arithmetic, not by playtest.
- All new prose is a draft for your edit. Several callbacks across arcs (Vahl at the banquet station, Echo at the intercepted instruction, Greta on the Biolab roster) are authored from flags and have never been seen in context.
- The journal text for new objectives lives in the client's quest reference data and has **not** been written; the `[DMJ]` objective events are emitted (nothing in korangar `main` consumes them yet).
- The DM beat shortcuts (`@dmbeat`) were updated for each arc but not exercised.
- `tools/check-campaign.sh` fails at its first gate on a pre-existing mismatch (Hercules `stable` expects four generated korangar TSVs that exist only on the closed playtest branch); I ran its script-load step directly instead.

**Tools added** (`tools/`): `campaign_probe.py map:x:y[:R]` lists clear walkable tiles near a point; `campaign_cellaudit.py <scripts>` reports every NPC position's walkability and suggests the nearest good tiles.

## Decisions I need before starting

1. **Order.** Slices 1–3 first, then Act II, as above — or go straight to rebuilding Act II?
2. **Ending gating.** Should the party's choices *remove* endings (for example, no Queen's Bargain if Himmelmez was killed), or only *change what the epilogue says*? I recommend tailoring, not removing: it is cheaper and nothing becomes unreachable.
3. **Road volunteer.** Is a volunteered character permanently marked on that character (per-character flag, shown in their journal), or only in the epilogue narration?
4. **Handoff briefs.** Treat `seal-cascade-act-redesign.md` Acts II–IV briefs as approved direction, or do you want to revise them?
5. **Playtest evidence.** You have run Act I live. Did Acts II–IV ever get played? Any live notes would outrank my reading of the scripts.

## Not verified

- Anything about how Acts II–IV *play*. The measurements describe structure; I have not run a session.
- Whether the 15 orphan decisions are consumed some other way (for example by the DM reading flags in `@dmflag` during a session). If DMs improvise from them, they are not wasted, but the scripts do not use them.
