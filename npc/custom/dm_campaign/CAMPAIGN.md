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
hunting quests + 1 story quest. No MVP bosses; story resolution via villain
dialogue choices.

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

---

## Act III (Arcs 11–14) — The Living Seals

**Flow:** Each arc introduces a mortal "co-seal" character with a 3-choice
villain confrontation, then an MVP boss spawned via DM console.

### Arc 11 — Zealot Bjorn (Hugel)
- Hunting: Priest Eadric questline (20153 × 15, 20154 × 20)
- Villain: Bjorn — subdued / persuaded / **joined**
- Boss: Randgris at `abyss_03`
- Flags: `dm_arc11_bjorn_subdued`, `dm_arc11_bjorn_joined`
- Bjorn_joined reduces Randgris court adds; Bjorn_subdued spawns the full court.

### Arc 12 — Captain Vance (New World)
- Hunting: Cornus (1992 × 15), Naga (1993 × 15)
- Villain: Vance — exposed / **helped**
- Boss: Naght Sieger (1956) at `spl_fild01`
- Flags: `dm_arc12_vance_exposed`, `dm_arc12_vance_helped`
- Naght Sieger starts the Rift Anchor pressure hazard: four pulses around
  `spl_fild01` 150,150. Helping Vance lowers pulse damage from 7% to 4%.
- Vance_helped → callback in Arc 15 (Lysandra)

### Arc 13 — Broker Carrion (Nameless Island)
- Hunting: Banshee (1868 × 20 / 20173), Zombie Slaughter (1865 × 20 / 20174)
- Villain: Carrion — killed / **bribed**
- Boss: Beelzebub (1874) at `abbey03`
- Flags: `dm_arc13_carrion_killed`, `dm_arc13_carrion_bribed`
- Carrion_killed spawns full coalition adds. Carrion_bribed can complete the arc
  without spawning Beelzebub and sets `dm_arc13_coalition_deal_honored`.

### Arc 14 — Prelate Hesma (Veins)
- Hunting: Salamander (1832 × 20 / 20183), Lava Golem (1367 × 20 / 20184)
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
- Hunting: Hylozoist (1510 × 15 / 20192), Lude (1509 × 15 / 20193)
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
- Himmelmez_bargained → major callback in Arc 19 (unlocks "Queen's Bargain" ending)

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
- Five endings (each sets a `dm_finale_*` flag):
  1. `dm_finale_shared_seal` — distributed resonance network
  2. `dm_finale_reforged_seal` — Varmundt's inverse-frequency machine
  3. `dm_finale_queens_bargain` — Himmelmez holds from Niflheim's side
  4. `dm_finale_thanatos_road` — one person chooses the seal knowingly
  5. `dm_finale_ragnarok_unbound` — seal not rebuilt; what's beneath rises
- Beat 1999 + `dm_campaign_complete` + global announce on completion

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
