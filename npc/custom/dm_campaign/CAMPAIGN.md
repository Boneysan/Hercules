# Seal Cascade — DM Campaign Reference

19-arc campaign across 4 acts. Runs inside a party instance. The DM operates
via `dm_console.txt` commands (`@dm`, `@dmbeat`, `@dmflag`, etc.).

---

## Quick Reference

| Arc | Title (vault) | Hub / Map | Boss | Quest IDs |
|-----|---------------|-----------|------|-----------|
| 00 | Tavern Downtime | Prontera Tavern (`prt_in 163 22`) | — | — |
| 01 | Omens at the Fountain | Prontera (Wynne / Frightened Mother / Tibbets) | Deviruchi (1109) | 20001–20006 (+ session 20000) |
| 02 | The Sleeping Forest | Payon (Elder Gyeong / Sun-Hwa / Voss) | Moonlight Flower (1150) | 20007–20012 |
| 03 | Sand and Whispers | Morroc (Mira / Assassin / High Priest) | Amon Ra / Osiris | 20013–20018 |
| 04 | City Above the Beast | Geffen (Vella / Elsbeth / Cassell / Doran) | Baphomet | 20019–20024 |
| 05 | Tides and Trade | Alberta / Izlude (Mara / Sea-Cultist Captain / Brode / Wynne) | Tao Gunka | 20025–20030 |
| 06 | The Floating Republic | Yuno / Juperos (Vahl / Gramps / Krenn / Engineer) | Mistress (1059) | 20101–20105 |
| 07 | Iron and Ash | Einbroch | RSX-0806 (1623) | 20111–20115 |
| 08 | The Cursed Kingdom | Glast Heim | Dark Lord (1272) | 20121–20125 |
| 09 | Frozen Faith | Rachel | Gloom Under Night (1768) | 20131–20135 |
| 10 | The Lab Beneath | Lighthalzen | Kiel D-01 (1734) | 20141–20145 |
| 11 | Wrath of Heaven | Hugel | Valkyrie Randgris (1751) | 20151–20155 |
| 12 | Beyond the Horizon | New World | Nidhoggr's Shadow (2022) | 20161–20165 |
| 13 | Island of the Damned | Nameless Island | Beelzebub (1874) | 20171–20175 |
| 14 | The Fire That Ends the World | Veins | Ifrit (1832) | 20181–20185 |
| 15 | The Hero's Tomb | Aldebaran / Thanatos | Memory of Thanatos (1708) | 20191–20195 |
| 16 | The Royal Banquet | Prontera | Bijou / Doppel (1046) | 20201–20204 |
| 17 | The Sage's Legacy | Biolabs (Varmundt) | Amdarais (2476) | 20211–20214 |
| 18 | The Witch of Death | Niflheim | Himmelmez | 20221–20223 |
| 19 | Nightmare of Midgard (Finale) | Morroc Ruins / Ash Vacuum | Surt (via Garm 1252) | 20230–20234 (incl. support + 20231–20233 core) |

**Source of truth for all titles, beats, choices, flags, and quest prose:**  
H:\Docs\Obsidian Notes\Game Design\Ragnarok_Online\Campaign\ (synced portions in planning/obsidian-campaign/ and this header).

See Choice_Tracker.md for finale gates (Mira Lives, Echo Trusts, etc.) and the 6 possible Arc 19 endings (including Refusal).

---

## Act I (Arcs 1–5) — The First Thread

**Flow:** Tavern intro → each arc uses S_StartArc / S_TurnIns pattern with 2
hunting quests + 1 story quest. No MVP bosses; story resolution via villain
dialogue choices.

Arc 4's Baphomet's Seal beat starts the Vault Seal Pressure hazard: three
pulses around `gef_dun02` 214,212 with curse pressure. The Outer Seal Puzzle
(`DM_ResetPuzzleFlag`) also unlocks via `@dmbeat` in Arc 4.

**Key flags set:**
- `dm_arc04_cassell_unmasked` — Cassell's true role revealed (callbacks in Arcs 8, 19)
- `dm_arc04_seal_reinforced` — Baphomet seal reinforced (callback in Arc 8)
- `dm_arc01_sigil_ring_obtained` — Sigil Ring item acquired (affects Arc 8 flavor)

---

## Act II (Arcs 6–10) — The Cascade Widens

**Flow:** Each arc escalates the cascade's reach across Midgard's industrial
and political zones.

**Key flags set:**
- `dm_arc06_krenn_bribed` — Yuno Council Krenn bribed (callback in Arc 16)
- `dm_arc07_kessler_confronted` — RSX-0806 exposed (callback in Arc 17)
- `dm_arc09_karsh_deal` — Oracle Karsh made a deal
- `dm_arc10_echo_freed` — Lighthalzen prototype Echo freed (callbacks in Arcs 17, 18)

Arc 7's RSX-0806 beat starts the Reactivation Bay smoke-pressure hazard: three
pulses around `ein_dun02` 150,150 with blind pressure. Supporting the strike
lowers pulse damage from 5% to 3%.

Arc 10's Kiel D-01 beat starts the Kiel Core Pressure hazard: three pulses
around `lhz_dun04` 150,150 with confusion pressure.

---

## Act III (Arcs 11–14) — The Living Seals

**Flow:** Each arc introduces a mortal "co-seal" character with a 3-choice
villain confrontation, then an MVP boss spawned via DM console.

### Arc 11 — Wrath of Heaven (Hugel)
- Hunting: Hugel Airship Muster (20153), Dragon Scale Turn-In (20154), Temple Edge Vigil (20155)
- Story: Sigrun's last word (20152) — Voice clue or comfort branch
- Gate: Bjorn — talked down / forced / exploited
- Boss: Randgris at `abyss_03`
- Flags: `dm_arc11_sigrun_voice`, `dm_arc11_sigrun_comforted`, `dm_arc11_bjorn_joined`
- Bjorn_joined or Sigrun comfort softens court adds; forced/exploited routes increase pressure.

### Arc 12 — Beyond the Horizon (New World)
- Hunting: Manuk Supply Line (20163), Cornus Mercy Run (20164), Dicastes Border Papers (20165)
- Story: First Contact Done Wrong (20162) — truth / peace / order
- Gate: Vance — exposed / turned / occupation
- Boss: Nidhoggr's Shadow (2022) at `spl_fild01`
- Flags: `dm_arc12_first_contact_truth`, `dm_arc12_first_contact_peace`, `dm_arc12_vance_helped`, `dm_new_world_alliance`
- Nidhoggr's Shadow starts the Rift Anchor pressure hazard: four pulses around
  `spl_fild01` 150,150. Vance_helped or New World alliance lowers pulse damage from 7% to 4%; occupation raises it to 9%.
- Vance_helped → callback in Arc 15 (Lysandra)

### Arc 13 — Island of the Damned (Nameless Island)
- Hunting: Abbey Bell Rotation (20173), Drowned Coin Tithe (20174), Lasagna Root Wardens (20175)
- Story: A Name You Knew (20172) — reckon / refuse the familiar dead
- Gate: Broker Carrion — killed / minutes bought
- Boss: Beelzebub (1874) at `abbey03`
- Flags: `dm_arc13_known_dead_reckoned`, `dm_arc13_known_dead_refused`, `dm_arc13_carrion_killed`, `dm_arc13_carrion_bribed`, `dm_arc13_dead_freed`, `dm_arc13_dead_burned`
- Abbey Bell Rotation uses Banshee (1867), Zombie Slaughter (1864), and Ragged Zombie (1865). Drowned Coin Tithe uses Zombie Slaughter and Ragged Zombie in abbey02. Lasagna Root Wardens uses verified Bifrost root-route stand-ins until Lasagna natural spawns exist.
- Carrion changes Beelzebub's support wave instead of skipping the fight: killing him adds harsher necromancer discipline; buying the minutes weakens the council's formation.

### Arc 14 — The Fire That Ends the World (Veins)
- Hunting: Veins Evacuation Ledger (20183), Bifrost Ash Scouting (20184), Magmaring Firebreak (20185)
- Story: The Deep Shift (20182) — expose Hesma / take the seal for silence
- Boss: Ifrit (1832) at `thor_v03`
- Flags: `dm_arc14_hesma_exposed`, `dm_arc14_hesma_bribed`, `dm_arc14_evacuated`, `dm_arc14_miners_lost`, `dm_arc14_cinder_taken`
- Ifrit starts the Magma Cathedral heat pulse hazard: five pulses around
  `thor_v03` 150,150. Exposing Hesma lowers pulse damage from 9% to 6%; ledger families, safe ash routes, and a full firebreak can each reduce it further.
- Arc 14 complete sets `dm_act03_complete` and beat 1499

---

## Act IV (Arcs 15–19) — The Seal's Edge

### Arc 15 — The Hero's Tomb (Aldebaran)
- Hub: Keeper Lysandra (`aldebaran,100,100`)
- Hunting: What the Tower Remembers (20192), Aldebaran Last Letters (20193), Clock Tower Daily Wounds (20194), Fragment Relief Rotation (20195)
- Villain: Scholar Pratt (`aldebaran,110,100`) — exposed / delayed / **challenged**
  - challenged reveals Thanatos is still living inside the seal
- Boss: Thanatos (1708) at `thana_boss`
- HIDDEN_NPC: `Memory of Thanatos#dm` at `thana_boss,150,150`
- Flags: `dm_arc15_pratt_exposed`, `dm_arc15_pratt_challenged`, `dm_arc15_memory_readiness`, `dm_arc15_mirror_shard_strength`
- Pratt_exposed/challenged alter the Thanatos echo adds. Pratt_challenged also
  callbacks in Arcs 18 (Familiar Dead) and 19 (Loki).
- Thanatos starts the tower resonance hazard: four pulses around `thana_boss`
  150,150. Pratt_challenged lowers pulse damage to 4%; Pratt_exposed lowers it
  to 6%; the unresolved default is 8%. Memory readiness and Mirror-Shard strength
  can reduce the pulse further.

### Arc 16 — The Prontera Banquet (Prontera)
- Hub: Kronecker G Heine (`prontera,150,150`)
- Hunting: Disguise (1506 × 20 / 20202), Bloody Murderer (1507 × 20 / 20203)
- Villain: Matron Rina (`prt_q,100,100`) — exposed / rolled / **defected**
  - defected: Bijou is Maret, trying to introduce cascade errors from inside
- Boss: Doppelganger (1046) as Bijou at `prt_q,150,150`
- HIDDEN_NPC: `Prison Vault#dm` at `prt_q,150,150`
- Flags: `dm_arc16_rina_exposed`, `dm_arc16_rina_rolled`,
  `dm_arc16_rina_defected`, `dm_arc16_bijou_killed`, `dm_arc16_maret_freed`
- Rina_defected resolves Bijou as Maret freed instead of a simple kill, and
  callbacks in Arc 18 (Familiar Dead / Maret lore).

### Arc 17 — The Sage's Legacy (Biolabs)
- Hub: Doctor Mira Tressa (`ba_in01,100,100`)
- Hunting: Aliza (1737 × 20 / 20212), Celia (2223 × 15 / 20213)
- Villain: The Administrator (`ba_in01,110,100`) — purged / negotiated / **running**
  - running: sends cascade analysis updates; creates Arc 19 callback
- Boss: Amdarais (2476) at `ba_pw03` (Biosphere Core)
- HIDDEN_NPC: `Biosphere Core#dm` at `ba_pw03,150,150`
- Flags: `dm_arc17_admin_purged`, `dm_arc17_admin_negotiated`,
  `dm_arc17_admin_running`, `dm_arc17_beta_killed`
- Admin_running → callback in Arc 19 (Loki cites 847% cascade deviation)

### Arc 18 — The Witch of Death (Niflheim)
- Hub: The Familiar Dead (`niflheim,100,100`)
- Hunting: Dullahan (1504 × 15 / 20222), Gibbet (1503 × 15 / 20223)
- Villain: Himmelmez (`nif_in,150,150`) — **killed** / **bargained**
  - bargained: Himmelmez holds the dead while party faces finale
  - Himmelmez gates: both hunts must be complete before she will speak
- Flags: `dm_arc18_himmelmez_killed`, `dm_arc18_himmelmez_bargained`
- Himmelmez_killed starts the Himmelmez Pressure hazard: three pulses around
  `nif_in` 150,150 with curse pressure.
- Himmelmez_bargained → major callback in Arc 19 (unlocks "Queen's Bargain" ending)
- **Design note — no scripted boss fight (intentional).** Unlike every other
  boss arc, Arc 18 has no "Beat: Spawn Himmelmez" and no `OnHimmelmezDead`
  handler, because **there is no Himmelmez mob in the 2019-era `mob_db.conf`**
  (mob 1929 is Baphomet, not Himmelmez). Rather than reskin a stand-in as was
  done for Bijou and Surt, the Witch of Death is run as a **narrative
  kill-or-bargain choice**: the DM resolves it with the "Himmelmez Killed" or
  "Himmelmez Bargained" beat (each grants quest credit + EXP), and the
  Himmelmez Pressure hazard supplies the mechanical tension. If a fightable
  Himmelmez is ever wanted, mirror Arc 6: pick a stand-in mob, add a
  "Beat: Spawn Himmelmez" in `dm_beats.txt`, and an `OnHimmelmezDead` handler
  in `arc_18_niflheim.txt`.

### Arc 19 — Nightmare of Midgard (Morroc Ruins)
- Hub: Loki The Voice (`moc_ruins,150,150`) — no traditional villain
- Hunting: Khalitzburg (1132 × 15 / 20232)
  - Auto-completes when party returns to Loki after hunt done (S_Progress)
- Revelation: Loki explains cascade = Thanatos's seal in harmonic decay
- Boss: Garm (1252) as Surt at `moc_fild22,150,150`
- HIDDEN_NPC: `The Ash Vacuum Rift#dm` at `moc_fild22,150,150`
- Surt starts the Ash Vacuum Rift hazard: four pulses around `moc_fild22`
  150,150. Himmelmez_bargained lowers pulse damage from 8% to 5% and removes
  the curse rider.
- Final NPC: The Central Choice (`moc_fild22,155,150`) — gated on `dm_arc19_surt_defeated`
- Six endings (each sets a `dm_finale_*` flag):
  1. `dm_finale_shared_seal` — distributed resonance network
  2. `dm_finale_reforged_seal` — Varmundt's inverse-frequency machine
  3. `dm_finale_queens_bargain` — Himmelmez holds from Niflheim's side
  4. `dm_finale_thanatos_road` — one person chooses the seal knowingly
  5. `dm_finale_refusal` — no new martyr; the seal's demand is denied outright
  6. `dm_finale_ragnarok_unbound` — seal not rebuilt; what's beneath rises
- Beat 1999 + `dm_campaign_complete` + global announce on completion

---

## Puzzles and Challenges

Puzzles and riddles are supported via `DM_PuzzleStep` and `DM_PuzzleRiddle` (see `dm_puzzles.txt` for full API and NPC templates).
- **Sequential Puzzles**: Use `DM_PuzzleStep` for levers or glyphs that must be clicked in order. A wrong step automatically resets the sequence and fires an optional failure event.
- **Riddles & Passwords**: Use `DM_PuzzleRiddle` to track attempts at a password or `select()` menu. It handles locking the puzzle after max attempts and triggering a consequence (e.g. a hazard or add spawn).

To reward non-combat solutions, use the **challenge EXP preset**:
- `@dm exp challenge <minor|standard|major> [arc]`
- It scales the reward to the target level of the current arc.
- `minor` grants ~25% of a mob-grind bar, `standard` ~50%, and `major` ~100%.

---

## Session Start Checklist

1. Form a party with all players.
2. Run `@dm mode on` — this enables DnD mode AND locks campaign NPCs to your party.
   - Only players in your party can interact with campaign NPCs.
   - Players outside the party see the NPC sprites but get silence if they click.
3. Before the arc's boss beat, check `planning/mvp-party-balance-checker.md`
   for that arc's `@dm scale` starting point — most raw MVP stat blocks are
   badly out of line with the party's story level band (see Boss Level
   Reference below).
4. Run `@dm mode off` at end of session to reset everything.

`$dm_active_party` stores the active party ID. If you need to check which party
is currently active: `@dm mode` with no argument reports the current state.

### State Lifetimes

`@dm status` shows the live values in this table. After any server restart or
DM relog, check it before resuming play.

| State | Vars | Lifetime | After server restart | After owner relogs |
|---|---|---|---|---|
| Session on/off, active party | `$dm_mode`, `$dm_active_party`, `$dm_inst_<pid>` | permanent global | survives | survives |
| EXP scaling, downed rule | `$@dm_exp_*`, `$@dm_downed_rule` | server-temp global | reset | survives |
| Encounter registry, hazard, bloodied watcher, traps | `@dm_enc_*`, `@dm_hazard_*`, `@dm_bloodied_*`, `@dm_trap_*` | DM char-temp | lost | lost |
| Player campaign state | `dm_arc*` flags, `dm_inspiration` | permanent char | survives | survives |
| Player live state | `@dm_downed`, `@dm_down_*`, `dm_cutscene_blocked` | char-temp | lost | lost |

---

## How Encounters Work

Boss fights are **DM-driven**, not auto-triggered by player progress. There are
two spawn patterns plus a manual fallback:

**Act I (arcs 1–5) — in-world spawns.** The climactic MVP is spawned by the
story NPC itself once players reach the set-piece through dialogue (e.g., Deacon
Holt drops the Deviruchi in the Listening Chamber). Adds **scale down with the
party's mercy/ally choices** (helping the refugees and befriending Tibbets each
remove adds), and the boss's `On<Boss>Dead` handler grants party-wide quest
credit + EXP automatically. These spawn map-relative so they also work inside a
private DM instance.

**Acts II–IV (arcs 6–17, 19) — Beat Director spawns.** The DM drops the MVP from
the `@dmbeat` menu via **"Beat: Spawn `<Boss>`"** (defined in
`shared/dm_beats.txt`). That `monster` call is wired to the arc's
`On<Boss>Dead` handler in the arc file, so killing it auto-grants the quest
tracker, EXP, and the closing story announcement — same as Act I, just spawned
on the DM's cue instead of by player dialogue.

**Manual completion fallback.** Every boss arc also has a
**"Beat: `<Boss>` slain (Arc Complete)"** option that grants the identical
rewards directly. Use it if the kill event ever fails to fire — boss despawned,
party wiped but you want to advance, or you narrated the fight instead of
running it.

**Stand-in mobs.** Some canonical villains have no mob in the 2019-era
`mob_db.conf`. Where an actual fight is wanted, a stand-in is used (see the Mob
IDs table below): **Doppelganger (1046)** for Bijou, **Garm (1252)** for Surt.
Arc 18 (Himmelmez) is the deliberate exception — see its arc note above.

**Rewards.** Boss-kill EXP is automatic (handler-granted). Loot / level rewards
are *not* auto-issued by arcs — the DM grants them via `@dmreward`
(`DM_RewardArcLevel`).

---

## DM Console Beat Handler Reference

Access via `@dm` in-game (DM account only).

| Beat Option | What it does |
|-------------|--------------|
| Beat: Start Arc N | Sets started flag, starts all arc quest IDs |
| Beat: [Villain] [Choice] | Completes story quest, sets villain flag |
| Warp: [NPC Name] | Teleports DM to that NPC's map coordinates |
| Beat: Spawn [Boss] | Spawns MVP with kill event; dispbottom hint to DM |
| Beat: [Boss] slain (Arc Complete) | Completes arc tracker quest, grants party EXP |

Beat numbers: 1–499 = Act I, 500–999 = Act II, 1000–1499 = Act III,
1500–1999 = Act IV. Beat 1999 = campaign complete.

Story outcome shortcuts live in `@dm decide` / `@dmdecide`: use
`@dm decide <key> <outcome>` for the fast path, `@dm decide [arc]` for menus,
and `@dm decide status [arc]` for the branch ledger. `@dmbeat` branch options
delegate to the same registry.

If a player missed a branch decision, use `@dm flag sync <present-player>` to
copy registered story flags from someone who was present.

---

## Adding A New Arc Checklist

When adding a future arc, update every current copy point in one pass:

1. Add the arc script under `npc/custom/dm_campaign/act_XX/arc_YY_*.txt` and
   include it from `npc/scripts_custom.conf`.
2. Register all new quest IDs in `db/quest_db.conf`.
3. Add player journal text in `planning/campaign_quest_journal_entries.lua`
   and `planning/SealCascade_QuestList_addon.lua`; update
   `tools/campaign_quest_merge.py` ID bounds if the range expands.
4. Update quest ID arrays/ranges in the Session Board
   (`act_01/arc_01_prontera.txt`), `S_Status` (`dm_console.txt`), and
   `DM_EraseAllCampaignQuests` (`dm_quests.txt`).
5. Add story flags to `DM_FlagRegistry` in `dm_flags.txt`; add console
   print/clear wrappers and `S_Flag` cases if the arc number exceeds 19.
6. Add any exclusive story choices to `dm_decisions.txt`, then route matching
   `@dmbeat` branch options through `DM_Decide`.
7. Add the `@dmbeat` menu and beat actions in `dm_beats.txt`.
8. Add hunt minimap markers in `dm_hunt_markers.txt`.
9. Add symptom or pressure events in `dm_symptoms.txt` if the arc has a custom
   pulse/hazard.
10. Add or verify reward scaling in `dm_rewards.txt` and the `@dm levels`
    table in `dm_console.txt`.
11. Update this file's quick-reference table, cross-arc dependency map, and
    mob ID table for new bosses/hunts. Add the boss to `ARC_BOSSES` in
    `tools/verify_boss_levels.py` and re-run it to refresh the Boss Level
    Reference table above.
12. Rebuild/merge the client quest journal with
    `tools/campaign_quest_merge.py`, then run `./tools/campaign-preflight.sh`.

When WP-9's quest registry ships, it should replace the Session Board,
`S_Status`, and `DM_EraseAllCampaignQuests` quest-ID copies above.

---

## Cross-Arc Flag Dependency Map

```
Arc 04: cassell_unmasked → Arc 08 (flavor), Arc 19 (Loki speech)
Arc 04: seal_reinforced  → Arc 08 (flavor)
Arc 06: krenn_bribed     → Arc 16 (Heine intro)
Arc 07: kessler_confronted → Arc 17 (Tressa intro)
Arc 10: echo_freed       → Arc 17 (Tressa), Arc 18 (Familiar Dead)
Arc 11: bjorn_joined     → Arc 11 boss flavor
Arc 12: vance_helped     → Arc 15 (Lysandra intro)
Arc 13: carrion_bribed   → Arc 19 (Loki speech — demon coalition lore)
Arc 15: pratt_challenged → Arc 18 (Familiar Dead — Thanatos-in-seal lore)
                        → Arc 19 (Loki speech)
Arc 16: rina_defected    → Arc 18 (Familiar Dead — Maret/Bijou lore)
Arc 17: admin_running    → Arc 19 (Loki speech — 847% cascade deviation)
Arc 17: beta_killed      → Arc 18 (Familiar Dead — Varmundt lore)
Arc 18: himmelmez_bargained → Arc 19 boss flavor, unlocks queens_bargain ending
```

---

## Mob IDs Verified Against `db/re/mob_db.conf`

| Mob | ID | Notes |
|-----|----|-------|
| Mistress | 1059 | MISTRESS |
| RSX-0806 | 1623 | RSX_0806 |
| Dark Lord | 1272 | DARK_LORD |
| Gloom Under Night | 1768 | GLOOMUNDERNIGHT |
| Randgris | 1751 | VALKYRIE_RANDGRIS |
| Naght Sieger | 1956 | NAGHT_SIEGER (not 1957 ENTWEIHEN); old Arc 12 stand-in |
| Beelzebub | 1874 | BEELZEBUB |
| Ifrit | 1832 | IFRIT |
| Thanatos | 1708 | THANATOS |
| Doppelganger (Bijou) | 1046 | DOPPELGANGER — no BIJOU mob in 2019 db |
| Amdarais (Biosphere) | 2476 | MG_AMDARAIS |
| Garm (Surt) | 1252 | GARM — no SURT mob in 2019 db |
| Hylozoist | 1510 | |
| Lude | 1509 | |
| Disguise | 1506 | |
| Bloody Murderer | 1507 | |
| Aliza | 1737 | |
| Celia | 2223 | |
| Dullahan | 1504 | |
| Gibbet | 1503 | |
| Khalitzburg | 1132 | |
| Cornus | 1992 | (Arc 12, was wrong as 1993 in earlier draft) |
| Naga | 1993 | (Arc 12, was wrong as 1994 in earlier draft) |
| Osiris | 1038 | OSIRIS (Arc 03, dual boss with Amon Ra) |
| Amon Ra | 1511 | AMON_RA (Arc 03, dual boss with Osiris) |
| Baphomet | 1039 | BAPHOMET (Arc 04 — not Baphomet Jr. 1101) |
| Tao Gunka | 1583 | TAO_GUNKA (Arc 05) |
| Nidhoggr's Shadow | 2022 | Arc 12 boss |

---

## Boss Level Reference (Renewal)

Canonical Renewal `Lv` from `db/re/mob_db.conf` vs. each arc's **EXP/reward
target level** (`@dm levels`, ¶ Session Start Checklist — not the same as the
party's story level band, see below). `@dm scale` rescales
HP/ATK/DEF/MDEF/HIT/FLEE as a **percentage of the mob's own spawned base
stats** — it does not touch the `Lv` field or retune it toward the target
level. A large delta is not a bug to "fix" in `mob_db.conf`. Regenerate with
`python3 tools/verify_boss_levels.py`.

For the actual pre-session scaling call — HP/ATK numbers, per-arc `@dm scale`
starting percentages, and add-count guidance against the party's real story
level band — use **`planning/mvp-party-balance-checker.md`**, which is the
source of truth for live tuning. The table below is a quick sanity check
only; its "delta" uses the reward-level target, not the party band, so it
will not exactly match that document's "Gap" column.

| Arc | Boss | Target Lv | Boss Lv (RE) | Delta |
|-----|------|-----------|--------------|-------|
| 01 | Deviruchi | 18 | 93 | +75 |
| 02 | Moonlight Flower | 28 | 79 | +51 |
| 03 | Osiris / Amon Ra | 38 | 68 / 69 | +30 / +31 |
| 04 | Baphomet | 48 | 81 | +33 |
| 05 | Tao Gunka | 58 | 110 | +52 |
| 06 | Mistress | 68 | 78 | +10 |
| 07 | RSX-0806 | 72 | 100 | +28 |
| 08 | Dark Lord | 76 | 96 | +20 |
| 09 | Gloom Under Night | 80 | 139 | +59 |
| 10 | Kiel D-01 | 84 | 125 | +41 |
| 11 | Valkyrie Randgris | 88 | 141 | +53 |
| 12 | Nidhoggr's Shadow | 90 | 117 | +27 |
| 13 | Beelzebub | 92 | 147 | +55 |
| 14 | Ifrit | 94 | 146 | +52 |
| 15 | Memory of Thanatos | 95 | 99 | +4 |
| 16 | Bijou / Doppelganger | 96 | 77 | -19 |
| 17 | Amdarais | 97 | 150 | +53 |
| 19 | Surt / Garm | 99 | 98 | -1 |

Every Act I–III boss (arcs 1–14) runs 20–75 levels hotter than the arc's
reward-target level — these are stock RO MVP/boss stat blocks picked for
lore, not tuned for pacing. Arc 18 (Himmelmez) has no mob and is resolved
narratively — see its arc note above.
