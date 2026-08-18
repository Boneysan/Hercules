# Skill Checks and Encounters

Design notes for the `@check` system (`npc/custom/dm_campaign/shared/dm_checks.txt`)
and the encounter tooling built on top of it. Companion to
[dm-tooling.md](dm-tooling.md) and [dm-handoff.md](dm-handoff.md).

## The principle

**A roll should change server state, not produce a sentence.**

RO is a live world with an aggro system, a status system, and mutable terrain.
If a check result only becomes narration, it is a dice toy with extra steps and
players stop caring within a session. Every mechanic below names the Hercules
primitive that makes the outcome real, and where a mechanic has no primitive it
is marked as such rather than described as if it worked.

Corollary: **only call for a roll when both outcomes are interesting.** The
fastest way to make a check system feel flat is rolling for things that should
simply happen.

## The maths, and why

`d20 + stat/15 + proficiency + assists` against a DC. Full rationale lives in
the header of `dm_checks.txt`; the short version is that the divisor is set by
the ladder the table already assumes — somebody good at a task reads DC 10 as
easy, 15 as medium, 20 as hard, where hard means roughly a coinflip.

| | mod | DC 10 | DC 15 | DC 20 | DC 25 |
|---|---|---|---|---|---|
| Good at it (99 + skill lv5+) | +10 | auto | 80% | 55% | 30% |
| Good, has skill | +8 | 95% | 70% | 45% | 20% |
| Good, untrained | +6 | 85% | 60% | 35% | 10% |
| Secondary stat (60) | +4 | 75% | 50% | 25% | — |
| Dumped (15) | +1 | 60% | 35% | 10% | — |

Adjusting a DC up or down a step is the intended knob. Rewriting the ladder is
not.

## What to roll for, and what it changes

| Situation | Stat | Server-side consequence | Primitive |
|---|---|---|---|
| Endure a hazard pulse | VIT `endure` | Half damage and no status on a pass | `DM_HazardArea` save args — **built** |
| Spot the ambush | DEX `perceive` | Marker revealed; on failure the spawn lands adjacent, not at range | `cloakoffnpc`, `viewpoint`, `areamonster` placement |
| Force a barricade | STR `force` | Blocked cells become walkable | `setcell` |
| Read a sigil | INT `arcana` | A mechanical fact with teeth ("Ifrit is Fire 4") | dialogue + flag |
| Stabilise the dying | INT `medicine` | Downed state reversed instead of a respawn | `OnPCDieEvent` — **not built** |
| Haggle | LUK `haggle` | Reward tier, or a bribe branch | `@dmreward`, flags |
| Jury-rig | DEX `craft` | A one-use key item, or a refine for the fight | `getitem`, `successrefitem` |
| Talk past a guard | any | Writes a `dm_*` flag the finale reads back | `DM_PartySetFlag` |

The approach picks the stat for social checks — threaten is STR, reason INT,
lie DEX, charm LUK, outlast VIT, read the room AGI. RO has no Charisma and none
is invented; making the player say *how* is more interesting than one stat
deciding who is allowed to talk.

## Stealth

The key discovery is that **RO already implements this.** `MD_DETECTOR`
(`0x100`, `src/map/status.h`) is precisely the flag for "this monster can see
through Hiding and Cloaking". So:

- A Thief with real `TF_HIDING` is natively stealthed against non-detector
  mobs. The engine enforces it. No new code.
- Everybody else rolls AGI to approximate what that class does for free.
- The DM composes the scene by stripping mode bits:
  `setunitdata(<gid>, UDT_MODE, <mode> & ~(MD_AGGRESSIVE|MD_DETECTOR))`
  makes a mob oblivious, and restoring the bits *is* the moment it notices.

Outcome bands map cleanly:

| Band | Effect |
|---|---|
| Pass | Unnoticed |
| Success at a cost | One mob regains `MD_AGGRESSIVE` — a problem, not a disaster |
| Fail | Nearby mobs wake and `unittalk` an alarm |

**Failure must never remove the encounter.** The party came for the fight;
denying it is a punishment that reads as lost content. Failure should make the
same fight worse instead — reinforcements behind you, a timer on the gate, or
the boss spawning with more HP because it had time to prepare
(`setunitdata(boss, UDT_MAXHP, ...)`).

Patrols are `unitwalk` on an NPC timer; a `perceive` check reveals the route
with `viewpoint` before the party commits.

## Encounters

Before this work, `@dm spawn <id> [count]` placed one mob type in a 7x7 box and
every real encounter was hardcoded per arc in `dm_beats.txt`. The composer adds
named, reusable encounters with slots (elite / minions / caster), spawned as a
unit and cleaned up together.

Requirements that shaped it:

- **Map-relative.** Spawns resolve off `strcharinfo(3)`, the DM's current map,
  so an encounter works identically inside a private instance. This is the same
  rule the arc beat spawns follow.
- **One event label per encounter** so the existing `@dm cleanup` removes it.
- **Party scaling.** `DM_PartyOnlineCount()` already exists; a three-player
  party should not face a six-player wall.
- **Formations.** Surrounding (ambush), line (blocking a corridor), scattered.
- **An entrance line.** `unittalk` on the elite when it lands. Monsters that
  speak are remembered.

### Difficulty budget — the unused asset

`korangar/docs/bestiary.json` carries `PhysDPS`, `MagicDPS`, HP, and level for
~1759 monsters, exported from this tree's own `mob_db.conf`. It is currently
read only to render the bestiary window. That is enough data to tell a DM
whether an encounter is a fair fight for four level-70s *before* they drop it,
which is the thing DMs most often get wrong live. Treat it as an encounter
balancing corpus, not just display data.

## DM tools that make checks feel weighty

1. **Declare the stakes before the roll.** `@dm stakes` announces what success
   and failure mean, then the check happens. The largest table-feel improvement
   per line of code in this whole document — a check whose price is unknown is
   just a number.
2. **Consequence bank.** Failures increment a debt the DM spends later ("the
   alarm you tripped in Arc 7 is why this door is guarded"). Reuses the flag
   architecture, and the finale readback can consult it.
3. **Inspiration tokens.** A reward currency that is not loot.
4. **Aim checks at what is on screen.** The strongest checks change adds,
   hazard damage, or boss HP — things the party watches change.

## Command surface

| Command | Who | What |
|---|---|---|
| `@check <tag\|stat> <dc>` | anyone | roll your own |
| `@assist <player> <tag>` | anyone | help — DC 10, +2, caps +4 |
| `@dm check <player\|me\|party> <tag> <dc> [flag]` | DM | call a check, optionally write a flag |
| `@dm stakes <success> \| <failure>` | DM | announce the price before rolling |
| `@dmenc list \| info <name> \| spawn <name> [form]` | DM | encounter composer |
| `@dm stealth [dc]` / `@dm wake` | DM | stealth scene |

## Build status

Built, loading clean, **none of it playtested**:

1. **Hazard saves.** `DM_HazardArea` takes an optional save tag and DC as args
   8 and 9. Passing halves the damage and avoids the status entirely. Both are
   optional, so all twenty-odd existing callers in Arcs 4, 7, 10, 12, 14, 15
   and 19 keep their original unconditional behaviour.
2. **`@dm stakes`.** Splits on `|` into success and failure lines, announced
   before the check.
3. **Encounter composer.** `dm_encounters.txt` — eight encounters, three slots
   each, three formations, party scaling from `DM_PartyOnlineCount()`, all
   wired to `DM_Console::OnDMKilled` so the existing `@dm cleanup` sweeps them.
4. **Stealth.** `DM_StealthSet` strips `MD_AGGRESSIVE|MD_DETECTOR` from every
   mob on the map, the party rolls AGI, and the bands decide how much wakes.

Not built: the downed/`OnPCDieEvent` rules, the consequence bank, inspiration
tokens, patrol routes, and the bestiary-driven difficulty budget.

### Two bugs this pass caught, worth not repeating

**MVPs in the elite slot.** The first draft of the encounter table had Baphomet
(1039) as a "Cult Overseer" and Kiel D-01 (1734) as a "Kiel Prototype". Both
are MVPs. A party expecting four minions and a sergeant would have met an MVP
with an MVP's HP and skill list. MVPs belong in `@dmbeat` boss spawns, which
announce themselves and grant arc credit. The same verification pass found 1268
labelled "Wraith Dead" when it is a Bloody Knight, and 1871 with no `mob_db`
entry at all. **Check `MvpExp` before putting a mob in an elite slot.**

**Restoring a mode you never recorded.** The first stealth implementation woke
the room by OR-ing `MD_AGGRESSIVE` onto every mob it could see. That does not
restore the map — it makes naturally passive mobs permanently aggressive, since
nothing recorded which ones had been aggressive to begin with. `DM_StealthSet`
now stores each unit's id and prior mode, and `DM_StealthWake` puts back exactly
what was there. Anything that mutates world state needs to remember the state it
replaced.

## Caveat

None of this has been played. The curve is modelled and the primitives are
verified against `src/map/`, but no party has rolled against a DC in a live
session. First-session numbers to watch: DC 15 against a *secondary* stat sits
at exactly 50%, and if the middle of the party feels like it coin-flips
everything, the cheap adjustment is proficiency `+3/+5` rather than touching the
divisor again.
