# Traps & Puzzles in Hercules/RO — Implementation Cookbook

Written 2026-07-02. Companion to `dm-architecture-review.md` WP-11 (`@dm trap`)
and WP-12 (puzzle templates): those packages build the *reusable DM tools*;
this guide is the engine cookbook for building them and for bespoke arc
set-pieces. Every primitive here was verified against this build's
`doc/script_commands.txt` and stock scripts in `npc/`.

The one-line summary: **RO has native walk-on triggers, step-off triggers,
interruptible cast bars, per-tile walkability, and enable/disable on every
NPC. That is a complete trap-and-puzzle engine. You never need the client.**

---

## 1. Design rules (read before building anything)

1. **Telegraph, then punish.** D&D traps are fair because they can be
   noticed. Every trap needs at least one perceivable clue before it fires:
   a `specialeffect` shimmer, a `mapannounce` whisper ("the flagstones here
   are unusually clean..."), or the DM narrating via `@dm say`. A trap with
   no tell is a gotcha, not a game.
2. **Consequence beats damage.** The best trap outcomes change the situation:
   an alarm that spawns a patrol in 30 seconds, a pit that separates the
   party, a curse that matters in the boss room. Raw HP loss is the least
   interesting knob (and `percentheal` can't kill anyway — see §3).
3. **Script the mechanism, DM narrates the fiction.** Scripts roll dice,
   deal damage, toggle doors. Descriptions come from the DM live (`@dm say`,
   `@dm story`). Do not bake paragraphs of flavor into mechanism NPCs.
4. **Always leave a DM bypass.** Every trap/puzzle must be skippable and
   resettable from the console: a flag the DM can set (`@dm flag set` /
   future `@dm decide`), plus a reset entry (`DM_ResetPuzzleFlag`,
   `@dm cleanup`). Players *will* solve things sideways; reward it with
   `@dm exp challenge` (WP-12) instead of forcing the scripted path.
5. **Party-gate everything.** Every trigger body starts with
   `if (!callfunc("DM_PartyActive")) end;` so outsiders never spring
   campaign content. Same rule as the arc NPCs.

## 2. The engine toolbox

| Primitive | What it gives you | Gotcha |
|---|---|---|
| `OnTouch:` + trigger area (`SPRITE,<tx>,<ty>` in the NPC header) | Walk-on trigger; the toucher's RID is attached, so checks/damage hit the right player with zero attachrid work | Area is a rectangle ±tx/±ty around the NPC tile. `disablenpc` removes the touch area (= disarmed) |
| `OnUnTouch:` | Fires when the player steps OFF the area | The real pressure-plate primitive: "door open only while held down" |
| `OnTouch_:` | Like OnTouch but one player at a time | Use for airlock-style single-file triggers |
| `enablenpc` / `disablenpc` | Arm/disarm anything, show/hide props | This is the master switch for trap state |
| `HIDDEN_WARP_NPC` sprite + trigger area | Invisible touch tile (stock pattern: Juperos `LeverWarp#ufe`) | Invisible = untelegraphed; see rule 1 |
| `CLEAR_NPC` sprite | Near-invisible but *clickable* object ("It's a lever...") | Stock pattern for suspicious devices (Juperos levers) |
| `HIDDEN_NPC` sprite | Hidden clickable (WoE castle levers) | Players must know to search the spot — pair with a perception check |
| Any prop sprite (`4_BOARD3`, statues, ...) | Visible interactable | Repo already proves `4_BOARD3` on this client |
| `specialeffect(EF_*)` / `soundeffectall("<file>.wav", ...)` | Telegraphs and payoffs (Juperos: `EF_BIG_PORTAL` + warp sound on lever pull) | Effect constants in `db/constants.conf` (`EF_FIREPILLAR`, `EF_VENOMDUST`, `EF_SPRINGTRAP`...) — eyeball in client before shipping |
| `showscript("text"{, GID})` | Floating text over an NPC/unit — glowing runes, countdown numbers | |
| `progressbar("0xRRGGBB", <sec>)` | Cast bar on the attached player; **aborts if they move** | The disarm/ritual minigame primitive. Run the skill check AFTER the bar completes |
| `input(.@answer$)` / `select(...)` | Password and riddle answers | `input` = free text (exact-match passwords); `select` = one right option among decoys |
| `setcell("<map>", x1,y1,x2,y2, cell_walkable, 0/1)` | Open/close floor and doors physically | Map-wide state — always restore on reset. Inside an instance the map copy has its own name, so it's naturally per-party |
| `areawarp("<map>", x1,y1,x2,y2, "<dest>", x, y)` | Pit traps, teleporter tiles, "the floor gives way" | |
| `getareausers("<map>", x1,y1,x2,y2)` | How many players stand in a zone | Cooperative plates, "whole party on the platform" gates |
| `viewpoint(1, x, y, <id>, <color>)` | Minimap X-marks | Treasure hunts, "the tremor came from there" |
| `countitem` / `delitem` / `makeitem` / `getitem` | Key items, offerings, physical clues dropped on the ground | Campaign key items should be etc-tier customs or existing quest items |
| `initnpctimer` + `OnTimerNNNN:` | Rearm delays, timed windows, alarm countdowns (per NPC) | One timer per NPC; `stopnpctimer` when done |
| `addtimer(ms, "NPC::OnLabel")` | Per-player timers | Already used by hazards/downed; label runs with that player attached |
| `sc_start(SC_*, ms, val)` | Trap statuses: poison, blind, curse, stun... | `S_HazardStatus` in `dm_console.txt` already maps names→constants; reuse it |
| `percentheal(-N, 0)` | Trap damage that **cannot kill** (floor at 1 HP unless −100) | The safe default. Lethal danger = statuses + spawned mobs + `@dm downrule on`, not raw script damage |
| `DM_HazardArea(...)` | Party-only AoE damage/status around a point | The blast component for area traps |
| `DM_Check` / `@dm check` math (`d20 + stat/10 vs DC`) | Saving throws and skill checks | WP-11 extracts `DM_RollCheck` so scripts can roll without announcing |
| `DM_TriggerEvent("<npc>", "<label>")` | Fires an event on the party's *instanced* copy of an NPC | **Always use this (or `instance_npcname`) for cross-NPC events inside instances** — bare `donpcevent` hits the original map's copy |

Stock scripts worth reading before writing your first one:
`npc/quests/quests_juperos.txt` (lever → timed hidden warp, item-slot
checkpoint devices, `$@...InUse` concurrency locks), `npc/woe-fe/prtg_cas01.txt`
(HIDDEN_NPC levers), any `npc/re/instances/*.txt` with `OnTouch:`
(BuwayaCave, HazyForest — instance-safe touch triggers), and this repo's own
`act_01/arc_04_geffen.txt` (the three-lever vault, lines ~490+).

## 3. Trap archetypes

All sketches assume the repo conventions: tabs, `DM_PartyActive` gate,
`strnpcinfo(NPC_MAP)` instead of hardcoded map names (instance safety).
`<map>` in headers is the *source* map — instances copy the NPC automatically.

### 3a. Pressure plate / tripwire (the bread-and-butter trap)

Walk-on trigger, AGI save, damage + status on fail. The toucher is already
attached, so this is short:

```
prt_sewb4,120,140,0	script	Plate#a01t1	HIDDEN_WARP_NPC,1,1,{
	end;
OnTouch:
	if (!callfunc("DM_PartyActive")) end;
	specialeffect(EF_SPRINGTRAP);
	// AGI save DC 13 — announces to the map like any table roll.
	// (After WP-11: .@pass = callfunc("DM_RollCheck", bAgi, 13, "");)
	callfunc("DM_Check", strcharinfo(PC_NAME), "agi", 13);
	// Until DM_RollCheck exists, apply flat consequences; with it, branch:
	percentheal(-25, 0);
	sc_start(SC_POISON, 8000, 1);
	disablenpc(strnpcinfo(NPC_NAME_UNIQUE));   // one-shot
	end;
}
```

Rearming variant: replace `disablenpc` with `initnpctimer` +
`OnTimer10000: enablenpc(strnpcinfo(NPC_NAME_UNIQUE)); stopnpctimer; end;`
(dodge-timing corridors want this).

DM control: `@dm say` narrates the click; a scripted reveal label
(`OnReveal: specialeffect(...); end;`) lets the DM show it after a
perception check via `@dm` → `DM_TriggerEvent("Plate#a01t1", "OnReveal")`.

### 3b. Pit trap (movement, not damage)

```
OnTouch:
	if (!callfunc("DM_PartyActive")) end;
	specialeffect(EF_HITLINE);
	mapannounce(strnpcinfo(NPC_MAP), "[DM] The floor gives way beneath " + strcharinfo(PC_NAME) + "!", bc_map, 0xFF6666);
	warp(strnpcinfo(NPC_MAP), <lower_x>, <lower_y>);   // same map, lower ledge
	end;
```

Separating one player from the party is a *strong* consequence — give the
pit a climb-out route (walkable path or a rope NPC with a STR check) and
warn the DM in the file header that a downed-rule fight while split is spicy.
`areawarp` does the same for a whole zone ("the bridge collapses").

### 3c. Ambush trap (trigger → encounter)

```
OnTouch:
	if (!callfunc("DM_PartyActive")) end;
	disablenpc(strnpcinfo(NPC_NAME_UNIQUE));
	mapannounce(strnpcinfo(NPC_MAP), "[DM] Sarcophagi lids grind open!", bc_map, 0xFF6666);
	areamonster(strnpcinfo(NPC_MAP), 115,135, 125,145, "Awakened Guard", 1132, 4, "DM_Console::OnDMKilled");
	end;
```

Spawning with the `DM_Console::OnDMKilled` label keeps the mobs inside the
existing cleanup net (`@dm cleanup` kills them). For boss-adds use the arc's
own kill labels like `arc_08` does.

### 3d. Alarm trap (consequences later — the most D&D trap of all)

No damage. Announce something subtle, start an npc timer, and make the
*future* worse:

```
OnTouch:
	if (!callfunc("DM_PartyActive")) end;
	soundeffectall("bell.wav", PLAY_SOUND_ONCE);   // any client wav
	mapannounce(strnpcinfo(NPC_MAP), "[DM] Somewhere above, a bell begins to toll.", bc_map, 0xFFAA33);
	initnpctimer;
	end;
OnTimer30000:
	stopnpctimer;
	areamonster(strnpcinfo(NPC_MAP), ...);   // the patrol arrives
	end;
```

The 30-second gap is playable time: the party can flee, hide (DM ruling +
AGI check), or prepare. Set a flag (`DM_PartySetFlag("dm_arcXX_alarm", 1)`)
so a later NPC/boss reacts to it — that's the "trap outcome enters the story"
loop the campaign is built on.

### 3e. Cursed chest / mimic (clickable bait)

`CLEAR_NPC` sprite (players see a shimmer and can click). On click: offer the
choice, roll the check, pay out or punish. Reuse the loot system —
`getitem(callfunc("DM_RollRewardItem", <arc>, BaseLevel, <tier>), 1)` — so
trap loot matches campaign loot. Mimic variant: `disablenpc` self +
`monster(...)` on the same tile.

### 3f. Dodge corridor (timed area pulses)

An FAKE_NPC with `initnpctimer` looping `OnTimer2000/4000/...` labels that
alternate a telegraph (`specialeffect` at fixed spots) and a pulse
(`DM_HazardArea(strnpcinfo(NPC_MAP), x, y, 2, 20, SC_STUN, 1500, $dm_active_party)`).
Players learn the rhythm and walk it. Start/stop via `OnStart:`/`OnStop:`
labels so the DM (or a lever) controls it: this is exactly the
`dm_symptoms.txt` pulse pattern pointed at fixed coordinates.

## 4. Puzzle archetypes

### 4a. Lever sequence (exists — extract, don't reinvent)

`act_01/arc_04_geffen.txt` ~line 490 is the reference: three levers, each
sets `dm_arc04_puzzle_N` only if all lower steps are set, else resets all
via `DM_ResetPuzzleFlag`; a gate NPC opens when all three are set. WP-12
turns this into `DM_PuzzleStep(prefix$, step, total, wrong_event$)`. The
`wrong_event$` hook is where wrong guesses get teeth: point it at an alarm
(3d) or a pulse (3f).

### 4b. Riddle keeper / password door

```
	if (!callfunc("DM_PartyActive")) end;
	mes("[Stone Warden]");
	mes("\"Answer, or turn back.\"");
	next();
	input(.@answer$);
	if (strtolower(callfunc("DM_Trim", .@answer$)) == "hlin") {   // taught by Deacon Holt, Arc 1
		callfunc("DM_InstanceSetFlag", "dm_arcXX_warden_passed", 1);
		callfunc("DM_TriggerEvent", "WardenDoor#aXX", "OnOpen");
		close();
	}
	// wrong answer: count attempts on a party flag, consequence at 3
```

Two forms: `input()` for exact passwords **the players learned in play**
(binding-words, names from handouts — this rewards note-taking, very D&D),
`select()` with decoys for riddles where typing exactness would be unfair.
Rule: the answer must exist somewhere in the campaign (an NPC line, a
Discord handout, an item description) — never only in the DM's head.

### 4c. Offering / key-item lock

`countitem`/`delitem` gate: "place three Ancient Seals in the bowl."
Scatter the items via `makeitem` (physical ground drops players must spot),
mob drops, or NPC rewards. The Juperos checkpoint devices
(`#hole#2-1`, quests_juperos.txt ~line 3025) are the stock reference —
including the `$@...InUse` lock so two players can't feed the same slot
simultaneously (use an instance/party flag instead of `$@` inside instances).

### 4d. Cooperative pressure plates (needs 2+ players — party content!)

Two plates, both must be held at once. This is the archetype that makes a
*party* feel like a party, and `OnUnTouch` makes it native:

```
gl_church,150,100,0	script	PlateA#coop	HIDDEN_WARP_NPC,0,0,{
	end;
OnTouch:
	if (!callfunc("DM_PartyActive")) end;
	set getvariableofnpc(.held, strnpcinfo(NPC_NAME_UNIQUE)), 1;
	specialeffect(EF_GLASSWALL);
	callfunc("DM_CoopPlateCheck");
	end;
OnUnTouch:
	set getvariableofnpc(.held, strnpcinfo(NPC_NAME_UNIQUE)), 0;
	callfunc("DM_CoopPlateCheck");   // door closes again
	end;
}
```

`DM_CoopPlateCheck` reads both plates' `.held` vars and opens/closes the
door (`setcell` or an enabled warp) accordingly. Instance note: NPC `.vars`
are shared between the original and instanced copies — inside instances use
per-party flags (`DM_InstanceSetFlag`) or `getareausers` on the instanced
map's plate coordinates instead:
`getareausers(strnpcinfo(NPC_MAP), 149,99, 151,101) > 0` is the stateless,
instance-safe version and usually the better choice.

### 4e. Ritual / defuse channel (progressbar)

The kneeling-at-the-altar, cutting-the-red-wire moment:

```
	mes("Steady your hands...");
	close2();
	progressbar("0x00FF00", 5);     // aborts if the player moves!
	// only reached if they held still 5s
	callfunc("DM_Check", strcharinfo(PC_NAME), "dex", 12);
	// branch on result once DM_RollCheck (WP-11) lands
	end;
```

Stack danger on top: the dodge corridor (3f) keeps pulsing while someone
channels — one player defuses while the others hold the line. That is a
set-piece encounter built from two reusable parts.

### 4f. Sequence-under-time (braziers, bells, glyphs)

N clickable props + one controller FAKE_NPC: first click starts
`initnpctimer`; all N must be clicked in the right order before
`OnTimer20000` resets the flags (`DM_ResetPuzzleFlag`) and fires the
consequence. `showscript` a countdown on the controller
(`showscript("The embers dim...")` at 10s) so pressure is visible. Wrong
order = instant reset + consequence event. This is 4a + a timer — build it
as a WP-12 template variant, not a new system.

## 5. Instance safety checklist (every trap/puzzle NPC)

- [ ] Map references use `strnpcinfo(NPC_MAP)`, never a hardcoded name —
      the instanced copy must act on the instanced map.
- [ ] Cross-NPC events go through `DM_TriggerEvent` / `instance_npcname`.
- [ ] State lives in per-character party flags (`DM_InstanceSetFlag`) or is
      stateless (`getareausers`) — not in `$@` globals or NPC `.vars` if the
      content can run instanced (they are shared with the original map).
- [ ] `setcell` changes are restored by the puzzle's reset path (instance
      maps reset on destroy, but the source-map copy of the NPC must not
      leave the *source map* modified — gate `setcell` behind
      `DM_PartyActive` too).
- [ ] Spawns use a kill label that cleanup knows (`DM_Console::OnDMKilled`
      or the arc's own labels).
- [ ] `@dm cleanup` + the puzzle's own reset restore everything: flags,
      cells, disabled/enabled NPC states, npc timers (`stopnpctimer`).

## 6. Playtest checklist (per trap/puzzle)

Walk-in from every direction (trigger rectangles have corners); trigger with
2 players in the area at once; step-off behavior (`OnUnTouch` plates);
disconnect mid-`progressbar` and mid-puzzle; wrong-answer/wrong-order paths
including the consequence event; the DM bypass (`@dm flag set` the solved
flag — the gate must honor it); reset → solve again; and the whole flow once
inside an instance (`@dm instance start <map>`), which is where map-name and
cross-NPC-event bugs appear.

## 7. How this ties back to the work packages

- **WP-11** (`@dm trap`) is archetype 3a as a *DM-placed, registry-backed*
  version — no NPC file needed at the table. Scripted plates (this guide)
  are for prepped arc content; `@dm trap` is for improv.
- **WP-12** templates are archetypes 4a/4b (+4f as a variant). Arc 4 is the
  retrofit target and reference.
- `@dm exp challenge` (WP-12) is the payout for **any** of these — and for
  the sideways solutions players find that skip the mechanism entirely.
- Everything here composes with the live-table layer: `@dm scene dread` +
  a dodge corridor + a defuse channel + `@dm downrule on` is a finished
  set-piece with zero new systems.
