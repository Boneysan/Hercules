# Monster family behavior templates

This is the review contract for family-scoped monster behavior in `db/re/mob_skill_db.conf`. It deliberately describes existing data rather than changing global combat records. Map-specific movement roles belong in `db/re/mob_ai_profile_db.conf`; do not move those roles into the globally applied family skill table.

## Orc family: relentless undead and ranged archer

| Template | Members | Shared behavior | Distinction |
|---|---|---|---|
| Relentless undead Orc | `ORC_ZOMBIE`, `ORC_SKELETON` | Both retain the Angry and Berserk `NPC_CRITICALSLASH` and `NPC_UNDEADATTACK` triggers; Berserk `NPC_POISON` is also shared. Skill states, levels, rates, cast times, delays, cancelability, target/condition, values, and emotes must remain aligned for each shared skill-state pair. | Orc Zombie is the slow, durable pressure body; Orc Skeleton has its separate map-scoped three-hit Skirmisher pilot on `orcsdun01`. |
| Ranged Orc | `ORC_ARCHER` | Keep its ranged `AC_DOUBLE` / `AC_SHOWER` skill kit and existing trigger data. | The `orcsdun02` RangedKeeper and local hazard avoidance are opt-in map+monster profiles, never global mob modes. |

## Raydric family: Glast Heim chivalry and archer guard

| Template | Members | Shared behavior | Distinction |
|---|---|---|---|
| Glast Heim Chivalry | `RAYDRIC`, `RAYDRIC_ARCHER` | Both share defensive `CR_AUTOGUARD` in `MSS_BERSERK` (Lv 2, Rate 500, Delay 300s, Cancelable) and reactive `CR_AUTOGUARD` in `MSS_RUSH` (`MSC_LONGRANGEATTACKED`, Lv 2, Rate 2000), as well as telegraphed `NPC_DARKNESSATTACK` in `MSS_BERSERK` (Lv 3, Rate 500, CastTime 500ms). | Raydric brings melee pressure (`SM_MAGNUM`, `BS_MAXIMIZE`) and Aggressor role; Raydric Archer uses ranged disruption (`AC_CHARGEARROW`, `AC_DOUBLE`) with RangedKeeper and local hazard avoidance on `gl_knt01` and `gl_prison`. |

The consistency checker `tools/check_mob_skill_families.py` verifies all registered families against `db/re/mob_skill_db.conf`. It also includes `--generate <family>` to export a validated template snippet for onboarding new family members.

## Change and acceptance rules

- Keep shared trigger thresholds, skill levels, target, cancelability, and emotes consistent within a template unless a reviewed exception is recorded here.
- A family template is not a map pilot. Do not apply a map-specific Aggressor, Coward, Skirmisher, RangedKeeper, or hazard policy through global mob data.
- Preserve stock data outside this friends-server fork's explicitly reviewed family members.
- Run `python3 tools/check_mob_skill_families.py` after editing these entries and `make -C src/map` after source/config changes.
- To export a family template for adding new members, run `python3 tools/check_mob_skill_families.py --generate "<family>"`.
