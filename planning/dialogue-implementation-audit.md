# Dialogue Implementation Audit

Scope: compare the synced Obsidian campaign materials in `planning/obsidian-campaign/` against the current RO implementation in `npc/custom/dm_campaign/`.

Important limitation: this audit can only verify against the synced Obsidian subset in this repo. The full vault path named in script headers, `H:\Docs\Obsidian Notes\Game Design\Ragnarok_Online\Campaign\`, is not available inside this workspace. A strict line-by-line audit against the complete vault is still pending unless those files are synced into the repo.

## Status Legend

| Status | Meaning |
|---|---|
| Implemented | Core dialogue/choice is present in live NPC scripts. |
| Adapted | The beat exists, but text was condensed, rewritten, or moved to another NPC/readable. |
| Partial | Some required surface exists, but a recurring appearance, branch, or payoff is missing. |
| Missing | No clear in-game surface found. |
| Runtime Test | Script exists, but should be walked in-game to confirm map, quest, marker, and branch behavior. |

## High-Level Result

The campaign has live dialogue coverage for all 19 arcs, plus tavern downtime. The implementation is not a verbatim copy of the available Obsidian text; it is an adapted RO implementation with quest-giver NPCs, branch choices, set-piece NPCs, and readable handouts.

The main remaining risk is not "no dialogue exists." The risk is that some recurring-cast source expectations still need runtime confirmation, especially Wynne's new capture branch and whether the current Voice foreshadowing is strong enough before Loki.

## Current Handoff Status

Implemented after the audit:

1. Added `Mira Ashkey#dm01` and `Mira Ashkey#dm05` so Mira is now present in Arcs 1, 3, 5, 16, and 19.
2. Added `Echo#dm10` so Echo's first physical appearance is playable in Arc 10.
3. Tightened Arc 16 `dm_prontera_united`: exposed and rolled outcomes preserve unity; defected clears the unity flag.
4. Added `arc19.finale` Refusal handling to `DM_Decide` and routed the central finale choice through the decision registry.
5. Added Wynne's optional Act II capture/loss branch through `Wynne's Field Kit#dm10`.
6. `script-checker` validation now runs clean for the DM campaign scripts; the wrapper suppresses the environment-only `socket_getips` line while preserving exit status and all other output.

## Synced Handouts

| Source | Expected location | In-game implementation | Status | Notes |
|---|---|---|---|---|
| `01_Cassells_Welcome_Letter.md` | Arc 4, after Cassell escapes Geffen Dungeon | `Silver Dagger Letter#dm` in `act_01/arc_04_geffen.txt` | Adapted | The readable preserves the point of the letter but is condensed from the source handout. |
| `02_Rekenber_Internal_Memo.md` | Arc 10, blood-stained Lighthalzen terminal | `Bloody Terminal#dm` in `act_02/arc_10_lighthalzen.txt` | Adapted | The Echo/Rekenber memo exists as a readable; source redaction/letterhead presentation is adapted to RO dialogue windows. |
| `03_Page_From_Thanatos_Diary.md` | Arc 15, after Memory of Thanatos | `Thanatos Diary#dm` in `act_04/arc_15_thanatos.txt` | Adapted | The central Thanatos lesson is present. Wording is compressed for in-game reading. |

## Recurring Cast

| Source character | Source expectation | In-game surfaces | Status | Gap / next action |
|---|---|---|---|---|
| Brother Cassell | Recurring gray pilgrim; first seen in Arc 1, unmasked in Arc 4, confirmed through clergy/cult network later. | Arc 1 `Deacon Holt#dm` cutscene references Cassell; Arc 4 `Brother Cassell#dm04`; Arc 4 `Silver Dagger Letter#dm`; later readables imply his network. | Implemented / Adapted | The exact "Meeting Brother Cassell" read-aloud is not verbatim. Consider adding a small Arc 1 refugee-camp readable or witness line to make his early almsman role more visible. |
| Quartermaster Wynne | Guild handler and recurring early ally; possible loss branch if desired. | Arc 1 `Quartermaster Wynne#dm`; Arc 5 `Quartermaster Wynne#dm05`; Arc 10 `Wynne's Field Kit#dm10`; tavern commentary; `Wynne's Ledger Copy#dm`; `Guild Routing Slip#dm05`. | Implemented / Runtime Test | Her recurring handler role exists. The optional Act II capture branch now supports rescued/lost outcomes through `arc10.wynne`. |
| The Voice / Loki | Unseen presence until Act IV; foreshadow once per act. | Arc 19 `Loki The Voice#dm`; scattered "Voice" language in Cassell/Rekenber/cult dialogue; finale choice; Act II/III clues include Rekenber/Echo and Valkyrie signal material. | Implemented / Review | Loki reveal exists and the foreshadowing trail is present. Runtime-read the full campaign flow to decide whether the Voice should be made more explicit. |
| Mira Ashkey | Refugee witness: Arc 1, Arc 3, Arc 5, Arc 16, Arc 19. | Arc 1 `Mira Ashkey#dm01`; Arc 3 `Mira Ashkey#dm`; Arc 5 `Mira Ashkey#dm05`; Arc 16 `Mira Ashkey#dm16`; Arc 19 `Mira Ashkey#dm19`; `dm_mira_lives` set on scarf recovery. | Implemented | Mira now has the expected recurring surface. Runtime-test her stateful callbacks after Arc 3 and Arc 16. |
| Echo | First appears in Arc 10 as a made hero who refuses orders; recurs Arc 18 and Arc 19. | Arc 10 `Echo#dm10`; Arc 10 `Director Hallan Reise#dm` choice can free Echo and set `dm_echo_trusts_party`; Arc 10 `Bloody Terminal#dm`; Arc 18 `Echo#dm18`; Arc 19 `Echo#dm19`. | Implemented | Echo now has a live Arc 10 scene plus later callbacks. Runtime-test freed vs hidden branches through Arc 18/19. |

## Finale Gates

| Gate / flag | Source expectation | Current implementation | Status | Notes |
|---|---|---|---|---|
| Mira Lives | Protect refugees/civilians; Mira reaches finale. | `dm_mira_lives` set in Arc 3 after recovering scarf; checked in Arc 5, 16, and 19. | Implemented / Review | Works mechanically. Arc 1/5 now provide continuity, while Arc 3 remains the decisive survival flag. |
| Echo Trusts the Party | Treat Echo as person, not tool. | Arc 10 `arc10.echo` decision sets `dm_echo_trusts_party` only on the freed outcome. | Implemented | Needs runtime verification through Arc 18/19 Echo callbacks. |
| Prontera United | Preserve legitimacy while exposing court rot. | Arc 16 Rina exposed/rolled outcomes set `dm_prontera_united`; defected clears it. | Implemented | Unity is now limited to outcomes that keep Prontera politically coherent. |
| Varmundt Tools Stabilized | Prioritize safe calibration. | Arc 17 Administrator negotiated outcome sets `dm_varmundt_tools_stabilized`; purged/running do not. | Implemented | Good distinction. |
| Himmelmez Bargain | Bargain with the witch-queen. | Arc 18 bargain outcome sets `dm_himmelmez_bargain`. | Implemented | Good finale gate. |
| The Refusal | Echo trust or Thanatos understanding helps unlock. | Arc 19 allows Refusal if `dm_echo_trusts_party` or `dm_arc15_pratt_challenged`; `DM_Decide("arc19.finale","refusal")` records the ending. | Implemented | This is implemented in live finale UI and decision registry. |
| Six endings | Shared, Reforged, Queen, Thanatos, Refusal, Unbound. | Arc 19 central choice includes all six when Refusal is available; otherwise five visible plus Unbound fallback; all outcomes route through `DM_Decide("arc19.finale", ...)`. | Implemented | Runtime-test all six endings. |

## Arc-By-Arc Audit

| Arc | Source beat from synced overview | In-game dialogue surfaces | Status | Gaps / next action |
|---:|---|---|---|---|
| 00 | Tavern downtime / campaign hub. | `Tavern Keeper`, `Shady Informant`, `Wynne's Ledger Copy#dm`. | Implemented | Runtime-test stateful comments by arc. |
| 01 | Prontera contracts, refugee tremors, goat sigils, Deviruchi/Cassell thread. | `Session Board#dm`, `Quartermaster Wynne#dm`, `Frightened Mother#dm`, `Mira Ashkey#dm01`, `Charity Ledger#dm01`, `Tibbets the Keeper#dm`, `Deacon Holt#dm`. | Implemented | Good coverage. Runtime-test Mira's pre/post quest callbacks. |
| 02 | Payon dead/ancestor rites, Voss and Moonlight Flower. | `Elder Gyeong#dm`, `Sun-Hwa#dm`, `Ancestor Plaque#dm02`, `Scholar Voss#dm`. | Implemented | Good coverage. Runtime-test branch flags for rite path, ancestor help, conduits. |
| 03 | Morroc refugee search, Sabra/Rashid route, Pyramid/Amon Ra foreshadowing Arc 19. | `Mira Ashkey#dm`, `Water Seller Rashid#dm03`, `Mother Sabra#dm03`, `Guild Assassin#dm`, `High Priest#dm`. | Implemented | Good coverage after recent additions. Runtime-test Sabra `DM_Decide` outcomes and later Arc 5 callbacks. |
| 04 | Geffen seal, Elsbeth, Doran, Cassell unmasked, Baphomet. | `Archmage Vella#dm`, `Apprentice Elsbeth#dm`, `Archmagus Doran#dm`, `Baphomet's Seal#dm`, `Brother Cassell#dm04`, seal glyphs, `Silver Dagger Letter#dm`. | Implemented | Handout adapted, not verbatim. Runtime-test `DM_Decide` wiring and catechism ending. |
| 05 | Alberta refugees, Mara, Brode manifests, Tao Gunka/deep current. | `Captain Mara#dm`, `Smuggler-Baron Brode#dm`, `Mira Ashkey#dm05`, `Guild Routing Slip#dm05`, `Exempt Hold#dm`, `Deep Trench Wake#dm`, `Quartermaster Wynne#dm05`. | Implemented | Good coverage. Runtime-test Mira's Arc 3 survival callback. |
| 06 | Yuno/Juperos data suppression, Krenn, Gramps, dimensional measurements. | `Doctor Ingrid Vahl#dm`, `Gramps#dm06`, `Director Aldous Krenn#dm`, `Variance Memo#dm06`, `Cultist Engineer#dm`, `Anchor-Shard#dm`. | Implemented | Good coverage. Runtime-test Krenn bribed/exposed callbacks in later arcs. |
| 07 | Einbroch strike, Rekenber industrial reach, RSX. | `Greta Holm#dm`, `Supervisor Kessler#dm`, `Strike Board#dm07`, `Reactivation Bay#dm`. | Implemented | Good coverage. Runtime-test strike outcome and smoke pressure reduction. |
| 08 | Glast Heim faith/cursed kingdom; Manfred choice. | `Sir Aldric Unfrocked#dm`, `Brother Manfred#dm`, `Vigil Book#dm08`, `Glast Heim Abbey#dm`. | Implemented | Good coverage. Runtime-test Manfred spared/killed effects on adds. |
| 09 | Rachel church cover-up, Karsh, Gloom, dimensional bleed. | `Acolyte Naima#dm`, `High Prelate Karsh#dm`, `Archived Doctrine#dm09`, `Ice Bleed Site#dm`. | Implemented | Good coverage. Cassell clergy confirmation is indirect; add direct Cassell mention if stronger continuity is needed. |
| 10 | Lighthalzen lab, Echo, Reise/Rekenber, false heroes. | `Doctor Sabine Reuter#dm`, `Director Hallan Reise#dm`, `Echo#dm10`, `Wynne's Field Kit#dm10`, `Bloody Terminal#dm`, `Kiel Core#dm`, `Kiel Core Pressure#dm`. | Implemented | Runtime-test Echo freed vs hidden behavior, Wynne rescued/lost branch, and later callbacks. |
| 11 | Hugel/Abyss Lake, Valkyrie judgment, Bjorn. | `Priest Eadric#dm`, `Zealot Bjorn#dm`, `Temple Signal Log#dm`, `Valkyrie Hall#dm`. | Implemented | Good coverage. Runtime-test Bjorn joined/subdued court pressure. |
| 12 | New World rift as escalation, Vance survey ethics. | `Envoy Aelith#dm`, `Captain Vance#dm`, `Anchor Survey Slate#dm`, `Rift Anchor#dm`. | Implemented / Adapted | Overview names Nidhoggr's Shadow; implementation uses Naght Sieger. Dialogue coverage is fine, boss identity differs by implementation. |
| 13 | Nameless Island, Father Quill, Broker Carrion, demon coalition bargain. | `Father Quill#dm`, `The Broker Carrion#dm`, `Broker's Card#dm13`, `Beelzebub Sanctum#dm`. | Implemented | Good coverage. Runtime-test Carrion deal skip/weakening behavior. |
| 14 | Veins/Thor, Hesma cover-up, Ifrit/Surt foreshadowing. | `Foreman Dunmar#dm`, `Prelate Hesma#dm`, `Withheld Notice#dm14`, `Magma Cathedral#dm`. | Implemented | Good coverage. Runtime-test Hesma exposed/bribed heat pressure. |
| 15 | Thanatos moral revelation, living lock cost. | `Keeper Lysandra#dm`, `Scholar Pratt#dm`, `Memory of Thanatos#dm`, `Thanatos Diary#dm`. | Implemented / Adapted | Diary is adapted. Runtime-test `dm_arc15_pratt_challenged` feeding Refusal route. |
| 16 | Prontera court rot, Rina network, Bijou/Maret, evacuation stakes. | `Kronecker G Heine#dm`, `Matron Rina#dm`, `Mira Ashkey#dm16`, `Prison Vault#dm`. | Implemented | Rina exposed/rolled outcomes set `dm_prontera_united`; defected clears it. Runtime-test finale callbacks. |
| 17 | Varmundt legacy, Administrator, tools for finale. | `Doctor Mira Tressa#dm`, `The Administrator#dm`, `Pattern Seven Console#dm`, `Biosphere Core#dm`. | Implemented | Good coverage. Runtime-test Administrator outcome flags. |
| 18 | Niflheim, Himmelmez bargain, Echo mirror. | `The Familiar Dead#dm`, `Echo#dm18`, `Himmelmez#dm`, `Himmelmez Pressure#dm`. | Implemented | Good coverage. Runtime-test bargain vs kill finale effects. |
| 19 | Morroc seal breaks, Loki reveal, Surt, central choice, six endings. | `Loki The Voice#dm`, `Mira Ashkey#dm19`, `Echo#dm19`, `The Ash Vacuum Rift#dm`, `The Central Choice#dm`. | Implemented | Finale outcomes now route through `DM_Decide("arc19.finale", ...)`. Runtime-test all six endings. |

## Readable / Handout Coverage Added In-Game

| Readable | Arc | Purpose |
|---|---:|---|
| `Wynne's Ledger Copy#dm` | 00 | Tavern continuity and guild record framing. |
| `Charity Ledger#dm01` | 01 | Holt/Cassell refugee outreach paper trail. |
| `Ancestor Plaque#dm02` | 02 | Payon taboo and Voss's scientific violation. |
| `Silver Dagger Letter#dm` | 04 | Cassell handout. |
| `Guild Routing Slip#dm05` | 05 | Wynne/Mara/Brode connective logistics. |
| `Variance Memo#dm06` | 06 | Yuno bureaucratic cover language. |
| `Strike Board#dm07` | 07 | Worker-side institutional voice. |
| `Vigil Book#dm08` | 08 | Manfred faith/cathedral framing. |
| `Archived Doctrine#dm09` | 09 | Rachel doctrine cover-up. |
| `Bloody Terminal#dm` | 10 | Rekenber/Echo handout. |
| `Temple Signal Log#dm` | 11 | Valkyrie signal failure. |
| `Anchor Survey Slate#dm` | 12 | Rift survey stakes. |
| `Broker's Card#dm13` | 13 | Carrion offer language. |
| `Withheld Notice#dm14` | 14 | Hesma delayed evacuation proof. |
| `Thanatos Diary#dm` | 15 | Thanatos handout. |
| `Pattern Seven Console#dm` | 17 | Varmundt/Echo conscience theme. |

## Action Items

1. Done: add `Echo#dm10` in Arc 10 for Echo's first physical scene.
2. Done: add `Mira Ashkey#dm01` and `Mira Ashkey#dm05` for recurring-cast fidelity.
3. Done: implement Wynne's optional Act II capture branch with rescued/lost outcomes.
4. Review in playtest: Voice foreshadowing exists across acts, but the table should decide whether it needs to be more explicit.
5. Done: tighten Arc 16 `dm_prontera_united`; defected no longer grants unity.
6. Done: wire Arc 19's central choice through `DM_Decide("arc19.finale", ...)`.
7. Pending runtime QA: test every branch that now calls `DM_Decide`, especially arcs 3-19 and `arc10.wynne`, because script parsing cannot confirm story-state feel.
8. Pending source sync: sync the full Obsidian campaign vault into `planning/obsidian-campaign/full/` or similar if a true line-by-line dialogue audit is required.
