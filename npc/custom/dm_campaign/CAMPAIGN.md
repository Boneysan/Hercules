# Seal Cascade — DM Campaign Reference

19-arc campaign across 4 acts. Runs inside a party instance. The DM operates
via `dm_console.txt` commands (`@dm`, `@dmbeat`, `@dmflag`, etc.).

---

## Quick Reference

| Arc | Title | Hub NPC / Map | Boss | Quest IDs |
|-----|-------|---------------|------|-----------|
| 01 | The Broken Gate | Prontera | — | 20001–20004 |
| 02 | River of Ash | Payon | — | 20007–20012 |
| 03 | The Scar | Morroc | — | 20013–20018 |
| 04 | The Warden's Brand | Geffen | — | 20019–20024 |
| 05 | The Leviathan Compact | Alberta / Izlude | — | 20025–20030 |
| 06 | The Council's Edge | Yuno | Mistress (1059) | 20101–20104 |
| 07 | Iron Congregation | Einbroch | RSX-0806 (1623) | 20111–20115 |
| 08 | Cathedral of Chains | Glast Heim | Dark Lord (1272) | 20121–20124 |
| 09 | The Sealed Oracle | Rachel | Gloom Under Night (1768) | 20131–20134 |
| 10 | The Living Key | Lighthalzen | Kiel D-01 (1734) | 20141–20144 |
| 11 | Veil of the Valkyrie | Hugel | Randgris (1751) | 20151–20155 |
| 12 | The New World Rift | New World | Naght Sieger (1956) | 20161–20165 |
| 13 | The Nameless Pact | Nameless Island | Beelzebub (1874) | 20171–20175 |
| 14 | The Magma Seal | Veins | Ifrit (1832) | 20181–20185 |
| 15 | The Method's Price | Aldebaran | Thanatos (1708) | 20191–20194 |
| 16 | The Prontera Banquet | Prontera | Doppelganger/Bijou (1046) | 20201–20204 |
| 17 | The Sage's Legacy | Biolabs | Amdarais (2476) | 20211–20214 |
| 18 | The Witch of Death | Niflheim | — (Himmelmez dialogue) | 20221–20223 |
| 19 | Nightmare of Midgard | Morroc Ruins | Garm/Surt (1252) | 20231–20233 |

---

## Act I (Arcs 1–5) — The First Thread

**Flow:** Tavern intro → each arc uses S_StartArc / S_TurnIns pattern with 2
hunting contracts + 1 story quest. No MVP bosses; story resolution via villain
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

### Arc 11 — Zealot Bjorn (Hugel)
- Hunting (turn-in): 20153 (Talon of Griffon x8, Cyfar x3, Maneater Root x7); 20154 (Dragon Scale x7, Dragon Canine x5, Dragon Skin x5)
- Villain: Bjorn — subdued / persuaded / **joined**
- Boss: Randgris at `abyss_03`
- Flags: `dm_arc11_bjorn_subdued`, `dm_arc11_bjorn_joined`
- Bjorn_joined reduces Randgris court adds; Bjorn_subdued spawns the full court.

### Arc 12 — Captain Vance (New World)
- Hunting (turn-in): 20163 (Mystic Horn x10, Solid Shell x4, Sharp Leaf x6); 20164 (Shining Scale x7, Stiff Horn x6, Brown Root x4)
- Villain: Vance — exposed / **helped**
- Boss: Naght Sieger (1956) at `spl_fild01`
- Flags: `dm_arc12_vance_exposed`, `dm_arc12_vance_helped`
- Naght Sieger starts the Rift Anchor pressure hazard: four pulses around
  `spl_fild01` 150,150. Helping Vance lowers pulse damage from 7% to 4%.
- Vance_helped → callback in Arc 15 (Lysandra)

### Arc 13 — Broker Carrion (Nameless Island)
- Hunting (turn-in): 20173 (Old White Cloth x6, Skull x8, Monster's Feed x8); 20174 (Clattering Skull x9, Skel-Bone x6, Torn Magic Book x3)
- Villain: Carrion — killed / **bribed**
- Boss: Beelzebub (1874) at `abbey03`
- Flags: `dm_arc13_carrion_killed`, `dm_arc13_carrion_bribed`
- Carrion_killed spawns full coalition adds. Carrion_bribed can complete the arc
  without spawning Beelzebub and sets `dm_arc13_coalition_deal_honored`.

### Arc 14 — Prelate Hesma (Veins)
- Hunting (turn-in): 20183 (Burning Heart x9, Burning Hair x4, Live Coal x4); 20184 (Sticky Poison x9, Maneater Blossom x4, Jubilee x3)
- Villain: Hesma — exposed / **bribed**
- Boss: Ifrit (1832) at `thor_v03`
- Flags: `dm_arc14_hesma_exposed`, `dm_arc14_hesma_bribed`
- Ifrit starts the Magma Cathedral heat pulse hazard: five pulses around
  `thor_v03` 150,150. Exposing Hesma lowers pulse damage from 9% to 6%.
- Arc 14 complete sets `dm_act03_complete` and beat 1499

---

## Act IV (Arcs 15–19) — The Seal's Edge

### Arc 15 — The Method's Price (Aldebaran)
- Hub: Keeper Lysandra (`aldebaran,100,100`)
- Hunting (turn-in): 20192 (Worn Out Page x8, Topaz x2, Pearl x2); 20193 (Ruby x3, Garnet x3, Red Feather x2)
- Villain: Scholar Pratt (`aldebaran,110,100`) — exposed / delayed / **challenged**
  - challenged reveals Thanatos is still living inside the seal
- Boss: Thanatos (1708) at `thana_boss`
- HIDDEN_NPC: `Memory of Thanatos#dm` at `thana_boss,150,150`
- Flags: `dm_arc15_pratt_exposed`, `dm_arc15_pratt_challenged`
- Pratt_exposed/challenged alter the Thanatos echo adds. Pratt_challenged also
  callbacks in Arcs 18 (Familiar Dead) and 19 (Loki).
- Thanatos starts the tower resonance hazard: four pulses around `thana_boss`
  150,150. Pratt_challenged lowers pulse damage to 4%; Pratt_exposed lowers it
  to 6%; the unresolved default is 8%.

### Arc 16 — The Prontera Banquet (Prontera)
- Hub: Kronecker G Heine (`prontera,150,150`)
- Hunting (turn-in): 20202 (Worn-out Prison Uniform x10, Manacles x5, Cyfar x5); 20203 (Bear's Footskin x13, Garlet x4, Clover x10)
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
- Hunting (turn-in): 20212 (Brigan x7, Solid Iron Piece x4, Smoke Powder x3); 20213 (Handcuffs x5, Research Chart x5, Blood Thirst x2)
- Villain: The Administrator (`ba_in01,110,100`) — purged / negotiated / **running**
  - running: sends cascade analysis updates; creates Arc 19 callback
- Boss: Amdarais (2476) at `ba_pw03` (Biosphere Core)
- HIDDEN_NPC: `Biosphere Core#dm` at `ba_pw03,150,150`
- Flags: `dm_arc17_admin_purged`, `dm_arc17_admin_negotiated`,
  `dm_arc17_admin_running`, `dm_arc17_beta_killed`
- Admin_running → callback in Arc 19 (Loki cites 847% cascade deviation)

### Arc 18 — The Witch of Death (Niflheim)
- Hub: The Familiar Dead (`niflheim,100,100`)
- Hunting (turn-in): 20222 (Armor Piece of Dullahan x9, Ectoplasm x5, Bat Cage x5); 20223 (Decomposed Rope x10, Spool x5, Red Muffler x4)
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
- Hunting (turn-in): 20232 (Rotten Bandage x10, Scale Shell x6, Grit x6)
  - Auto-completes when party returns to Loki after hunt done (S_Progress)
- Revelation: Loki explains cascade = Thanatos's seal in harmonic decay
- Boss: Garm (1252) as Surt at `moc_fild22,170,140`
- HIDDEN_NPC: `The Ash Vacuum Rift#dm` at `moc_fild22,170,140`
- Surt starts the Ash Vacuum Rift hazard: four pulses around `moc_fild22`
  170,140. Himmelmez_bargained lowers pulse damage from 8% to 5% and removes
  the curse rider.
- Final NPC: The Central Choice (`moc_fild22,175,140`) — gated on `dm_arc19_surt_defeated`
- Five endings (each sets a `dm_finale_*` flag):
  1. `dm_finale_shared_seal` — distributed resonance network
  2. `dm_finale_reforged_seal` — Varmundt's inverse-frequency machine
  3. `dm_finale_queens_bargain` — Himmelmez holds from Niflheim's side
  4. `dm_finale_thanatos_road` — one person chooses the seal knowingly
  5. `dm_finale_ragnarok_unbound` — seal not rebuilt; what's beneath rises
- Beat 1999 + `dm_campaign_complete` + global announce on completion

---

## Session Start Checklist

1. Form a party with all players.
2. Run `@dm mode on` — this enables DnD mode AND locks campaign NPCs to your party.
   - Only players in your party can interact with campaign NPCs.
   - Players outside the party see the NPC sprites but get silence if they click.
   - Korangar: **GM / DM Commands** (`Ctrl+O`) → **DM mode ON** sends the same command.
   - Expect chat: `→ @dm mode on` then `[DM] DnD mode enabled…` (not “Mode is currently OFF”).
3. Run `@dm mode off` at end of session to reset everything.

`$dm_active_party` stores the active party ID. If you need to check which party
is currently active: `@dm mode` with no argument reports the current state.

**If mode/help feedback breaks after a rebuild or script edit**, use the breadcrumb
runbook: [planning/dm-mode-troubleshooting.md](../../../planning/dm-mode-troubleshooting.md)
(server `callsub` + `.@` scope; client packet `0x017F` for `dispbottom`).

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
| Naght Sieger | 1956 | NAGHT_SIEGER (not 1957 ENTWEIHEN) |
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
| Gryphon | 1259 | Arc 11 hunt — `hu_fild02` |
| Ferus | 1714 | Arc 11 hunt — `abyss_01`–`abyss_03` |
| Banshee | 1867 | Arc 13 hunt — `abbey01`. **NOT 1868**, which is `G_BANSHEE`: no spawns, no drops, no exp |
| Zombie Slaughter | 1864 | Arc 13 hunt — `abbey01`/`abbey02` |
| Salamander | 1831 | Arc 14 hunt — `thor_v01`–`thor_v03` (NOT 1832 IFRIT) |
| Magmaring / Muscipular / Drosera | 1836 / 1780 / 1781 | Arc 14 hunt — `ve_fild03`/`07` (replaced 1366 Lava Golem, which lives in `mag_dun01`) |
| Harpy | 1376 | Arc 6 hunt — `yuno_fild02`–`yuno_fild07` |
| Metaling | 1613 | Arc 7 hunt — `ein_fild06`–`ein_fild09` |
| Raydric | 1163 | Arc 8 hunt — `gl_cas02`, `gl_knt01`/`02` |
| Wraith | 1192 | Arc 8 hunt — `gl_church`, `gl_chyard` |
| Whikebain / Kavac / Removal | 1653 / 1656 / 1682 | Arc 10 hunt — `lhz_dun01`/`02` (replaced 1035 Hunter Fly, which spawns nowhere near Lighthalzen) |
| Aliot | 1736 | Arc 10 hunt — `kh_dun01`/`02` |

**Off-by-one sweep (2026-08-18).** Eleven campaign hunting quests in
`db/quest_db.conf` carried a mob id exactly one higher than the mob their own
comment/quest name named (e.g. 20183 "Volcanic Salamander Hunt" targeted 1832
IFRIT, an MVP, instead of 1831 SALAMANDER — which made Arc 14 uncompletable,
since `arc_14_veins.txt:148` gates the Hesma confrontation on both hunts).
All eleven are corrected and every arc-script header now agrees with
`quest_db.conf`. When adding a hunt, verify the id against `mob_db.conf` by
name, not by neighbouring id.

**Hunting contracts are item turn-ins (2026-08-25).** All 41 non-boss hunts now
ask for drops rather than kills. The six single-boss quests (20005, 20012,
20017, 20018, 20023, 20030) keep their `Targets:` — killing a named boss is a
story beat, not a counter.

- **Master data:** `db/dm_hunt_db.json`. Nothing else is authoritative.
- **Generator:** `tools/gen-hunts.py` writes the `Drops:` blocks in
  `quest_db.conf`, the `dm_hunts.txt` script table, and korangar's
  `campaign_quests.tsv`. Rates and turn-in counts are **derived** from each
  contract's kill budget and the monster's own drop rate — do not hand-edit
  them. `tools/gen-hunts.py --check` fails on drift and runs first inside
  `tools/check-campaign.sh`.
- **Scripts:** arcs call `DM_HuntReady` / `DM_HuntCollect` / `DM_HuntStanding`
  / `DM_HuntBrief` (in `dm_quests.txt`). No arc reads `questprogress(id,
  HUNTING)` any more.
- **Party behaviour:** quest drops roll for every party member in range
  (`src/map/mob.c:3046`) and land straight in that member's inventory, so a
  party pools its drops and one member hands them in. Credit and payment stay
  party-wide.
- **Client:** korangar now has a quest log (Ctrl+Q, or the menu) showing each
  contract's items and how many the player is carrying. Before this the three
  quest packets were registered and discarded.

**Fixed on the way (2026-08-25).**

- **20173 "Abbey Bell Silencing" hunted a monster that does not exist in the
  world.** It targeted 1868, which is `G_BANSHEE` — the summoned variant: no
  spawns, no drops, `Exp: 0`. The real Banshee is 1867. The 08-18 off-by-one
  sweep missed it because `mob_db.conf` names *both* ids "Banshee", so a
  name-based check passed. `gen-hunts.py` now checks spawns and the `G_`
  sprite prefix instead of the name.
- **Ten hunts pointed at mobs from another region entirely**, so the drops
  could not match the fiction: 20105 and 20113 (Rachel mobs in Yuno/Einbroch
  arcs), 20115 (Kunlun), 20142 (Geffen — the caveat recorded on 08-18),
  20184 (Magma Dungeon), 20192/20193 (Niflheim mobs in Thanatos Tower),
  20202/20203 (Niflheim mobs in the Prontera arc), 20232 (Glast Heim mobs in
  the Morroc ruins). Each is retargeted to its arc's own maps, with the reason
  recorded in the `retarget` field of `db/dm_hunt_db.json`. Arc 15 gained the
  most: Thanatos Tower's own Deathword/Observation/Shelter drop the memory
  pages and jewels its story is about.
- **20105 "Norgroad Heat Index" is now wired into Arc 6.** It was defined and
  reset but started by no script. Vahl asks for three datasets rather than two
  and gates on all three.
