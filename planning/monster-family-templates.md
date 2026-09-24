# Monster family behavior templates

This is the review contract for family-scoped monster behavior in `db/re/mob_skill_db.conf`. It deliberately describes existing data rather than changing global combat records. Map-specific movement roles belong in `db/re/mob_ai_profile_db.conf`; do not move those roles into the globally applied family skill table.

## Orc family: relentless undead and ranged archer

| Template | Members | Shared behavior | Distinction |
|---|---|---|---|
| Relentless undead Orc | `ORC_ZOMBIE`, `ORC_SKELETON` | Both retain the Angry and Berserk `NPC_CRITICALSLASH` and `NPC_UNDEADATTACK` triggers; Berserk `NPC_POISON` is also shared. Skill states, levels, rates, cast times, delays, cancelability, target/condition, values, and emotes must remain aligned for each shared skill-state pair. | Orc Zombie is the slow, durable pressure body; Orc Skeleton has its separate map-scoped three-hit Skirmisher pilot on `orcsdun01`. |
| Ranged Orc | `ORC_ARCHER` | Keep its ranged `AC_DOUBLE` / `AC_SHOWER` skill kit and existing trigger data. | The `orcsdun02` RangedKeeper and local hazard avoidance are opt-in map+monster profiles, never global mob modes. |

The consistency checker verifies the shared undead Orc entries against the source database. It does not approve changing rates or skills: balance changes still need the S6 solo/party observation gate. Add a member to a shared template only after confirming its role, existing spawn maps, and behavior in `mob_db.conf`, `mob_skill_db.conf`, and spawn scripts.

## Change and acceptance rules

- Keep shared trigger thresholds, skill levels, target, cancelability, and emotes consistent within a template unless a reviewed exception is recorded here.
- A family template is not a map pilot. Do not apply a map-specific Aggressor, Coward, Skirmisher, RangedKeeper, or hazard policy through global mob data.
- Preserve stock data outside this friends-server fork's explicitly reviewed family members.
- Run `python3 tools/check_mob_skill_families.py` after editing these entries and `make -C src/map` after source/config changes. Then perform the solo and mixed-party observations in [the AI pilot spec](../korangar/docs/specs/monster-ai-pilot.md) before advancing to the Glast Heim profiles.
