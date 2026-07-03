# MVP Party Balance Checker

Purpose: compare each campaign boss against the party's story position and give the DM a practical first-pass scaling plan.

This document is for live table tuning, not hard balance law. Use it before a session to decide whether a scripted MVP should run raw, weakened, or with reduced adds. During play, use `@dm scale`, `@dm encounter`, and `@dm bloodied` from the campaign tooling.

## Sources

- Campaign boss list: `npc/custom/dm_campaign/CAMPAIGN.md`
- Story level bands: `planning/obsidian-campaign/Tabletop_Campaign_Overview.md`
- Monster stats: `db/re/mob_db.conf` and `db/pre-re/mob_db.conf`
- Runtime tools: `npc/custom/dm_campaign/shared/dm_combat.txt`

When the Obsidian overview and current RO implementation disagree, the "Implemented boss" column follows the RO implementation.

## How To Read The Table

- `Party band` is the story band from the campaign overview.
- `RE Lv` is Renewal monster level from `db/re/mob_db.conf`.
- `Gap` is `RE Lv - party band high`. Negative means the boss level is below the top of the story band.
- `Risk` is a practical DM estimate. Boss level alone is not enough; HP, attack, adds, and mechanics matter more.
- `Starting adjustment` is the recommended opening dial. Change it live if the party is overperforming or collapsing.

## Scaling Rules Of Thumb

Use these as defaults before considering class mix, gear, consumables, and player count.

| Situation | Suggested opening adjustment |
|---|---|
| Boss is below or near band, low add pressure | Run raw or `@dm scale damage 85 boss` |
| Boss is 1-20 levels above band or mechanically swingy | `@dm scale hp 80 boss` and `@dm scale damage 70 boss` |
| Boss is 21-40 levels above band, very high HP, or heavy burst | `@dm scale hp 60 boss` and `@dm scale damage 50 boss`; reduce adds by half |
| Boss is 40+ levels above band or has wipe mechanics | Script a weakened set-piece, or use `@dm scale hp 40 boss` and `@dm scale damage 35 boss`; avoid full adds |
| Party is under 4 players | Reduce add count first, then damage |
| Party has no resurrection/support | Reduce damage and status pressure before reducing HP |
| Party has high sustain but low damage | Reduce HP, leave damage closer to normal |

Useful commands:

```txt
@dm encounter boss last
@dm scale hp 70 boss
@dm scale damage 60 boss
@dm bloodied on boss
```

## Campaign Boss Balance Table

| Arc | Story arc | Party band | Implemented boss | Mob ID | RE Lv | RE HP | RE ATK | Gap | Risk | Starting adjustment |
|---:|---|---:|---|---:|---:|---:|---|---:|---|---|
| 1 | Omens at the Fountain | 1-25 | Deviruchi | 1109 | 93 | 8,912 | 477/182 | +68 | High for level, but HP is small. The danger is early-party burst, not endurance. | Use a weakened story spawn or `hp 45`, `damage 25`; keep adds minimal. |
| 2 | The Sleeping Forest | 12-55 | Moonlight Flower | 1150 | 79 | 324,000 | 2232/1251 | +24 | High. HP and attack are far above normal low-mid party play. | `hp 55`, `damage 40`; reward conduit/ancestor choices by cutting adds. |
| 3 | Sand and Whispers | 20-70 | Osiris into Amon Ra | 1038 / 1511 | 68 / 69 | 1,175,840 / 1,009,000 | 1980/1503, 2090/2052 | -1 | Medium-high because it is a two-phase fight with large HP, even though level fits. | `hp 55` both phases, `damage 60`; if party is small, make Osiris a short prelude. |
| 4 | The City Above the Beast | 30-80 | Baphomet plus Doppelganger | 1039 / 1046 | 81 / 77 | 668,000 / 380,000 | 3150/1984, 2103/1176 | +1 | High due to two MVP bodies and adds, not level gap. | `hp 65`, `damage 60`; if Elsbeth/Doran outcomes help, reduce Doppel or add count. |
| 5 | Tides and Trade | 33-80 | Tao Gunka | 1583 | 110 | 1,252,000 | 3757/1260 | +30 | High. Renewal Tao is much later than the story band. | `hp 55`, `damage 45`; make Sea-Cultist/hold choices reduce pressure. |
| 6 | The Floating Republic | 68-115 | Mistress | 1059 | 78 | 378,000 | 985/1967 | -37 | Low-medium. Level is below band, but MVP behavior can still punish unprepared parties. | Run raw or `damage 85`; use adds/hazards for drama instead of boss scaling. |
| 7 | Iron and Ash | 80-120 | RSX-0806 | 1623 | 100 | 1,001,000 | 3010/976 | -20 | Medium. Fits the band, but HP is substantial. | Run raw for geared party; otherwise `hp 80`, `damage 80`. Strike support should reduce smoke/add pressure. |
| 8 | The Cursed Kingdom | 75-120 | Dark Lord | 1272 | 96 | 1,190,900 | 3935/2585 | -24 | Medium-high. Fits band but Dark Lord can overwhelm with undead court pressure. | `damage 75`; if Manfred spared, reduce adds. If killed, keep full court but consider `hp 85`. |
| 9 | Frozen Faith | 80-145 | Gloom Under Night | 1768 | 139 | 3,005,000 | 6592/2785 | -6 | High. In-band, but HP and attack are steep. | `hp 75`, `damage 65`; Karsh exposed can reduce ice/add pressure. |
| 10 | The Lab Beneath | 120-165 | Kiel D-01 | 1734 | 125 | 2,502,000 | 4112/3580 | -40 | Medium-high. Below top band but high HP and lab pressure. | `hp 80`, `damage 70`; freeing Echo should weaken or delay pressure pulses. |
| 11 | The Wrath of Heaven | 110-155 | Valkyrie Randgris | 1751 | 141 | 3,205,000 | 7343/4412 | -14 | Very high. In-band but punishing attack and court adds. | `hp 70`, `damage 55`; if Bjorn joins, reduce court adds heavily. |
| 12 | Beyond the Horizon | 105-145 | Naght Sieger | 1956 | 99 | 5,000,000 | 7020/3200 | -46 | Medium-high because HP is huge, despite low level. Overview names Nidhoggr's Shadow, but implementation spawns Naght Sieger. | `hp 60`, `damage 70`; Vance helped should improve telegraphs or reduce anchor pulses. |
| 13 | Island of the Damned | 120-165 | Beelzebub | 1874 | 147 | 4,805,000 | 6666/4444 | -18 | Very high. In-band but high endurance and demon pressure. | `hp 65`, `damage 60`; Carrion deal can skip or severely weaken the fight. |
| 14 | The Fire That Ends the World | 130-175 | Ifrit | 1832 | 146 | 6,935,000 | 8063/3389 | -29 | Very high. In-band, but Ifrit's HP and burst are major. | `hp 55`, `damage 50`; Hesma exposed should reduce heat pressure and civilian complication. |
| 15 | The Hero's Tomb | 175-195 | Memory of Thanatos | 1708 | 99 | 1,445,660 | 4956/1671 | -96 | Medium. Level is low for the band, but the encounter is narratively heavy. | Run raw; add mechanics should carry difficulty. If party is tired, `damage 85`. |
| 16 | The Royal Banquet | 180-205 | Bijou using Doppelganger ID | 1046 | 77 | 380,000 | 2103/1176 | -128 | Low as a raw mob. Needs scripted pressure to feel like an Act IV boss. | Run raw only with prison hazards/adds. Consider `hp 200`, `damage 120` if the party is geared. |
| 17 | The Sage's Legacy | 190-215 | Amdarais | 2476 | 150 | 4,290,000 | 5290/3900 | -65 | Medium-high. Below band, but high HP and meaningful damage. Overview names Beta/Silva Papilia; implementation uses Amdarais. | `hp 80`, `damage 75`; Administrator negotiated can improve data/telegraphs. |
| 18 | The Witch of Death | 210-235 | Himmelmez narrative boss | N/A | N/A | N/A | N/A | N/A | Story decision more than normal MVP. Balance depends on chosen implementation. | If using a proxy MVP, start around `hp 70`, `damage 60`; bargain can bypass or transform fight. |
| 19 | Nightmare of Midgard | 230-250+ | Surt using Garm ID | 1252 | 98 | 1,275,500 | 2421/1733 | -152 | Raw Garm is far too weak for finale. Finale difficulty must come from mechanics, phases, and adds. | Use custom phases or heavy upscale: `hp 300+`, `damage 175+`, plus scripted finale pressure. |

## Side Bosses And Optional Pressure

These bosses are mentioned in the design overview or used as supporting beats. They should not be dropped raw into an under-leveled party without checking the table logic above.

| Boss | Mob ID | RE Lv | RE HP | Notes |
|---|---:|---:|---:|---|
| Osiris | 1038 | 68 | 1,175,840 | Arc 3 phase-one boss before Amon Ra. Keep short if party is below 60. |
| Doppelganger | 1046 | 77 | 380,000 | Arc 4 support boss and Arc 16 proxy body. Dangerous early, weak late. |
| Garm | 1252 | 98 | 1,275,500 | Arc 19 proxy body for Surt. Must be upscaled or phased. |
| Nidhoggr's Shadow | 2022 | 117 | 3,452,000 | Overview Arc 12 boss, not current implementation. Good alternate if Naght feels wrong. |
| Amdarais | 2476 | 150 | 4,290,000 | Current Arc 17 implementation. Suitable as a late-campaign body. |

## Implementation Notes

1. Act I bosses are intentionally story set pieces. Do not trust raw MVP stats for arcs 1-5.
2. Act II and Act III bosses mostly fit their story bands by level, but HP and attack still need live tuning.
3. Act IV has the largest implementation mismatch: some finale-stage bosses use lower-level proxy mobs and need mechanics or scaling to feel correct.
4. `@dm scale` only affects tracked monsters. After spawning a boss, use `@dm encounter boss last` if the boss pointer is not already set.
5. Add reduction is usually cleaner than over-reducing boss HP. A boss can feel dramatic at lower damage if the room is not flooded with adds.
6. For a party of 3 or fewer, start by cutting adds by 50-75 percent and reducing boss damage. For a party of 5 or more, keep adds and scale HP instead.

## Recommended Follow-Up Work

1. Add a generated version of this table so it can refresh from `CAMPAIGN.md` and `mob_db.conf`.
2. Add explicit boss IDs to `CAMPAIGN.md` for arcs 3, 4, 5, 18, and the support bosses.
3. Consider custom proxy mobs for Arc 16 Bijou, Arc 18 Himmelmez, and Arc 19 Surt instead of reusing lower-level stock bodies.
4. Add per-arc "weakened by choice" notes directly to boss spawn scripts where the story already supports it.
