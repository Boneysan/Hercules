# DM Live-Table Tooling Plan

The existing `@dm` layer is deep on **combat, quests, spawns, and pacing**
(`warp/hazard/spawn/beat/mode/quest/exp/reward/instance/roll`, hunt+objective
markers, traps, branching encounters). What it does not yet have is the
**live-table layer** a tabletop DM leans on: improvised NPC voice, stat-driven
skill checks, on-the-fly mood, cutscenes, and session-flow tooling.

This plan adds that layer. Everything below follows the current conventions in
`npc/custom/dm_campaign/shared/`:

- New commands are bound in `DM_Console` (`dm_console.txt`) via `bindatcmd`,
  dispatched from `OnDM` to an `S_*` sub, and also given a direct `@dm<name>`
  alias (`OnName`).
- Every handler starts with `callfunc("DM_RequireDM")` (GM gate) and reports via
  `dispbottom("[DM] …")`.
- Party-wide effects reuse the attach-RID loop pattern from `dm_quests.txt`
  (`DM_PartyApply*`) and `DM_HazardArea`.
- Repeating effects use the `addtimer`/`deltimer` + `On*Tick` pattern from
  `S_Hazard`.
- New shared logic goes in new files registered in `npc/scripts_custom.conf`.

Global session vars already in use: `$dm_mode`, `$dm_active_party`. New vars are
namespaced `$dm_*` (global) or `dm_*` (per-character).

---

## Build status

**Starter live-table pack shipped** (registered in `npc/scripts_custom.conf`):

- `shared/dm_voice.txt` — `@dm say` / `@dmsay` (improv NPC voice via `unittalk`;
  `@<npc>` puppet form via `npctalk`). ✅
- `shared/dm_checks.txt` — `@dm check` / `@dmcheck` (RO-native d20 + stat/10 vs
  DC, party/single, adv/dis, party-facing `mapannounce`). ✅
- `shared/dm_checks.txt` — `@dm inspire` / `@dminspire` (per-character
  Inspiration tokens consumed by advantaged checks). ✅
- `shared/dm_scene.txt` — `@dm scene` / `@dmscene` (weather mapflags +
  `playbgmall` + party-looped `cutin` presets). ✅
- `shared/dm_scene.txt` — `@dm cutscene` / `@dmcutscene` (party movement freeze,
  optional cutin, auto-release, cleanup/mode-off release). ✅

Remaining (not yet built): `@dm scale` + bloodied, downed/death-saves,
`@dm secret`, initiative/spotlight, tavern hub, recap log.

## New files

| File | Purpose |
|------|---------|
| `shared/dm_voice.txt` ✅   | `@dm say` (+ future `@dm emote`, `@dm secret`) — improv presentation |
| `shared/dm_scene.txt` ✅   | `@dm scene`, `@dm cutscene` — ambience + cutscene director |
| `shared/dm_checks.txt` ✅  | `@dm check`, `@dm inspire` (+ future `@dm initiative`) — tabletop mechanics |
| `shared/dm_combat.txt`    | `@dm scale`, bloodied watcher — live difficulty dial |
| `shared/dm_downed.txt`    | downed/death-save mechanic (`OnPCDieEvent` hook) |
| `shared/dm_session_log.txt` | `@dm log`, "Previously on…" recap |
| `act_00/tavern_hub.txt`   | between-arc social hub map + `@dm rest` |

## Client asset manifest (custom files to distribute to players)

`@dm scene` presets reference custom BGM tracks in the client `BGM/` folder
(`.mp3`). Add these files and hand them to players:

| Preset | BGM file | Weather |
|--------|----------|---------|
| dread | `dm_dread.mp3` | fog |
| boss  | `dm_boss.mp3`  | clouds2 |
| calm  | `dm_calm.mp3`  | (none) |
| holy  | `dm_holy.mp3`  | sakura |
| ruin  | `dm_ruin.mp3`  | fog |
| snow  | `dm_snow.mp3`  | snow |
| fest  | `dm_fest.mp3`  | fireworks |

Portraits passed to `@dm scene <preset> <portrait>` / `@dm say … | portrait=` are
`.bmp` files in `data\texture\유저인터페이스\illust` (magenta = transparent).
**Client limitation:** this client (PACKETVER 20190605, pre-20220504) cannot stop
a BGM from script, so `@dm scene clear` clears weather + portrait only — override
music by playing another scene.

`dm_console.txt` gains one `bindatcmd` + one `OnDM` branch + one `S_*` sub per
command. Consider extracting the presentation/mechanics handlers into their own
FAKE_NPC consoles (e.g. `DM_VoiceConsole`) to keep `dm_console.txt` from
ballooning past its current 1327 lines; the dispatch style stays identical.

---

## Phase 1 — Live improv & mechanics (highest leverage)

### 1. `@dm say` — puppet any NPC's voice
**File:** `dm_voice.txt` · **Effort:** M

The single biggest gap. Lets the DM type dialogue live that appears attributed to
a named speaker, instead of pre-scripting every line in a beat.

```
@dm say <speaker> | <text>          // floating dialogue over the DM, map-wide
@dm say @<npcname> <text>           // make a specific on-map NPC/mob speak
@dmsay ...
```

- Map-wide narration already exists (`DM_MapStory`); `say` differs by
  **attribution to a character voice** and optional portrait.
- Implementation: a persistent invisible `DM_Voice` FAKE_NPC per session map, or
  reuse the DM's own unit. Use `npctalk "<text>", "<speaker>", bc_map` to show the
  line to everyone on the map with the speaker's name. To voice an existing unit,
  resolve its GID (from the `@dm spawn` GID table, see Phase 3) and `unittalk`.
- Optional `| portrait=<img>` suffix chains into `cutin` (Phase 1.3 asset rules).
- Pair with **`@dm emote <target> <id>`** → `emotion <id>` / `unitemote` for
  reaction faces (`e_gasp`, `e_omg`, …).

**Edge cases:** speaker names with spaces (use `|` delimiter); target NPC not on
map; sanitize `^` color-code injection in DM text.

### 2. `@dm check` — skill checks / saving throws vs real stats
**File:** `dm_checks.txt` · **Effort:** M

Turns "make a DEX save" into a real mechanic driven by the player's actual stats,
building on `@roll`.

```
@dm check <player|party> <stat> <DC> [adv|dis]
   stat: str|agi|vit|int|dex|luk  (or: dodge, will, might … mapped aliases)
@dmcheck ...
```

- Roll = `rand(1,20)` + modifier, where modifier = `readparam(bStat)/10`
  (**RO-native — decided**). A stat of 30 = +3, 99 = +9. Bonus stats naturally
  make higher-level heroes better at checks without a separate progression.
- `adv`/`dis` rolls twice, takes high/low. Spends an inspiration token if present
  (Phase 2.1).
- Party form loops online members (attach-RID pattern), rolls each, prints a
  per-member pass/fail table via `dispbottom`, and can auto-apply a consequence
  (e.g. start a hazard on failers) by chaining into `DM_HazardArea`.
- Output is party-facing (`bc_map`) so the table sees the drama; add a `hidden`
  variant that whispers only the DM, mirroring `@roll hidden`.

**Edge cases:** unknown stat alias; DC bounds; nat-1 / nat-20 callouts.

### 3. `@dm scene` — ambience director
**File:** `dm_scene.txt` · **Effort:** M

Bundle weather + BGM + effect + portrait into named presets, one command.

```
@dm scene <preset>        // dread | boss | calm | holy | ruin | clear
@dm scene custom <fog|rain|snow|sakura|leaves|clouds|none> [bgm] [effect]
@dmscene ...
```

- Weather via mapflags: `setmapflag`/`removemapflag` with `mf_fog`, `mf_rain`,
  `mf_snow`, `mf_sakura`, `mf_leaves`, `mf_clouds`, `mf_clouds2`, `mf_fireworks`.
- BGM via `playbgmall "<file>", <map>` (**asset dependency:** the mp3 must exist
  in the client `BGM/` folder; ships-with-client tracks are safe, custom tracks
  need distribution — flag in docs).
- Screen effect / shake via `specialeffectall <id>` on the map.
- Optional portrait via `cutin "<illustration>", <pos>` (**asset dependency:** bmp
  in client illustration folder).
- Presets are a data table (`setarray`) mapping name → weather+bgm+effect so the
  DM never memorizes ids. `@dm scene clear` removes all scene mapflags/portrait.

**Edge cases:** presets must clean up prior scene state; per-map mapflags reset on
`@dm cleanup`; document which BGM/illustration assets are client-side.

### 4. `@dm cutscene` — freeze the party for set pieces
**File:** `dm_scene.txt` · **Effort:** S · **Status:** shipped ✅

```
@dm cutscene on [portrait] [seconds]  // freeze party movement, optional cutin
@dm cutscene off                      // release + clear cutin
@dmcutscene ...
```

- Uses `setpcblock(PCBLOCK_MOVE, true/false)` looped over the online party
  (attach-RID pattern) to freeze movement for reveals/monologues.
- Optional `cutin` portrait is shown to the same party members.
- **Safety:** per-player auto-release defaults to 60s and clamps to 5-300s;
  `@dm cleanup`, `@dm mode off`, `@dm reset confirm`, and reconnect all
  force-release movement and clear the portrait.

---

## Phase 2 — Table-feel mechanics

### 5. Inspiration / fate tokens
**File:** `dm_checks.txt` · **Effort:** S · **Status:** shipped ✅

Reward roleplay with a spendable token that grants advantage or a reroll.

```
@dm inspire <player> [+n]      // grant; default is +1
@dm inspire <player> spend     // manual burn (or auto via `@dm check … adv`)
@dm inspire <player> clear
@dm inspire <player> set <n>
@dm inspire party              // list current tokens
@dminspire ...
```

- Store on a per-character var `dm_inspiration` (party-safe via attach-RID).
- `@dm check` consumes one for `adv` automatically when available and marks the
  public check line with `Inspiration`.
- Token counts are clamped to 0-9 to keep the mechanic bounded.

### 6. Downed & death saves
**File:** `dm_downed.txt` · **Effort:** M–L

Replace plain resurrect with tabletop stakes.

- Hook `OnPCDieEvent` (fires per player death) to enter a **dying** state instead
  of a normal death: freeze/`sc_start SC_STUN`-style incapacitation + a running
  "death save" (roll each tick; 3 successes = stable, 3 fails = out).
- Allies can stabilize by reaching the downed player (proximity check on a timer)
  — reuses the `DM_HazardArea` area-scan logic inverted (ally-in-range = rescue).
- DM overrides: `@dm revive <player|party>`, `@dm downrule <on|off>` to toggle the
  whole system for a given fight.
- Reuses the Play Dead grant already wired into `@dm novice`.

**Edge cases:** interaction with instance/arc respawn points; PvP maps; make it
opt-in per encounter so trash fights aren't punishing.

### 7. Handouts (lore scrolls / letters) — DROPPED
Cut in favor of sending handouts to players over Discord. If an in-game version
is ever wanted, render via `readbook`/`messagebox` with keyed lore in a
`S_HandoutText` switch.

### 8. Secret notes (DM aside to one player)
**File:** `dm_voice.txt` · **Effort:** S

```
@dm secret <player> <text>
```

- Styled private `dispbottom`/`message` to a single member ("_The DM leans in…_"),
  for passing information the rest of the table shouldn't see.

---

## Phase 3 — Pacing & difficulty

### 9. Live difficulty dial + bloodied callout
**File:** `dm_combat.txt` · **Effort:** M (depends on spawn GID tracking)

```
@dm scale <hp%|dmg%> [target]     // adjust the active/last-spawned encounter live
@dm scale boss <hp%>              // just the tracked boss
```

- Requires a **spawned-mob GID table**. Verify whether `@dm spawn`/`holdspawn`
  already records GIDs; if not, add a `$dm_spawn_gid[]` array on spawn. This table
  is shared infrastructure that also powers `@dm say @unit` (Phase 1.1).
- Adjust via `setunitdata(<gid>, UDT_MAXHP, …)` / `UDT_HP` / `UDT_ATKMIN/ATKMAX`.
- **Bloodied watcher:** a timer polling `getunitdata(<gid>, UDT_HP)` against max;
  on crossing 50% fire a one-shot `npctalk`/`specialeffect` for drama. Auto-stops
  when the GID dies (`OnNPCKillEvent`) or on `@dm cleanup`.

**Edge cases:** GID reuse after death; MVP summon-adds; cap scaling to avoid
one-shots.

### 10. Spotlight / initiative
**File:** `dm_checks.txt` · **Effort:** M

```
@dm initiative           // roll d20+AGI for each party member, print turn order
@dm spotlight <player>   // freeze everyone else briefly for one hero's moment
@dm spotlight off
```

- Initiative reuses `@dm check` roll core, sorts, prints the order to the map.
- Spotlight reuses the `setpcblock` party loop from `@dm cutscene`, excluding the
  named player; same auto-release safety timer.

---

## Phase 4 — Session flow

### 11. Tavern downtime hub
**File:** `act_00/tavern_hub.txt` · **Effort:** M

Matches the stated vision (tavern → dungeon → live GM). A between-arc social map:

- A safe hub (reuse an existing indoor map, or an instance) with `@dm rest`
  (full HP/SP heal + `savepoint`), a vendor NPC, and **rumor NPCs** whose lines
  are driven by campaign flags to seed the next arc.
- `@dm rest` = party-wide `percentheal 100,100` + save + short buff, gated to the
  hub or DM discretion.

### 12. Session recap log
**File:** `dm_session_log.txt` · **Effort:** S–M

```
@dm log <text>          // append a timestamped note to the session log
@dm recap               // print "Previously on…" from logged notes + story flags
```

- Append notes to a global array or a per-session `$dm_log$[]` (bounded ring).
- `@dm recap` composes a summary from `@dm log` entries plus the existing
  `arc01..arc19` flags, giving a session-open "Previously on Seal Cascade…".

---

## Shared infrastructure (do first, unblocks the rest)

1. **Spawned-mob GID registry** — needed by `@dm scale`, the bloodied watcher, and
   `@dm say @unit`. Audit `S_Spawn`/`S_HoldSpawn`; add `$dm_spawn_gid[]` if absent.
2. **Party-loop helper for presentation** — a `DM_PartyForEach`-style wrapper (the
   attach-RID loop already exists for quests/flags) generalized so voice/scene/
   check/downed all share one iterator.
3. **Auto-release safety net** — `@dm cleanup` and `@dm mode off` must clear:
   scene mapflags, cutins, `setpcblock` freezes, downed states, and all live
   timers. Centralize in the existing cleanup path.

---

## Suggested sequencing

1. Spawn-GID registry → `@dm scale` + bloodied (#9) — the biggest infra item.
2. Downed/death saves (#6) — most complex; opt-in per fight.
3. Handouts/secret (#7,#8), initiative/spotlight (#10) — quick wins.
4. Tavern hub (#11) + recap log (#12) — session-flow polish.

## Decisions

- **Skill-check math:** RO-native `readparam(bStat)/10` modifier. *(decided)*
- **Scene BGM/portraits:** custom BGM + illustration files will be distributed to
  players, so `@dm scene` / `cutin` can use bespoke assets. Track required files
  in a client-asset manifest so the DM knows what to ship. *(decided)*
- **Console structure:** keep a single unified `@dm` dispatcher in
  `dm_console.txt`, but move each command's implementation into a
  `function script DM_*` in its domain file (`dm_voice.txt`, etc.); the `OnDM`
  branch just calls the function. Bind the `@dm<name>` direct aliases in the
  domain file's own FAKE_NPC. Keeps `dm_console.txt` lean without fragmenting the
  `@dm` command surface. *(decided — see Console architecture below)*

## Open questions

- **Downed rules knobs:** default on/off, save cadence, rescue method, and
  failure consequence — proposed ruleset below, pending confirmation.

## Console architecture

Only one NPC can `bindatcmd("dm", …)`, so the `@dm <sub>` surface must dispatch
from a single place. To avoid a 2500-line `dm_console.txt`:

- `OnDM` stays the one dispatcher; each branch is a thin call, e.g.
  `if (.@sub$ == "say") { callfunc("DM_Say", …); end; }`.
- The real logic lives in `function script DM_Say` inside `dm_voice.txt`.
- The direct alias `@dmsay` is bound by a small FAKE_NPC in `dm_voice.txt`
  (`bindatcmd("dmsay", …::OnSay)`), whose `OnSay` also calls `DM_Say`.

Net: unified command surface, logic grouped by domain, each file stays small.

## Downed & death-save ruleset (proposed)

Adapts D&D 5e death saves to RO. When a hero would die, they instead drop to a
**downed** state and roll to survive; the party can rescue them.

- **Trigger:** intercept `OnPCDieEvent`. Only engages while `$dm_mode` is on and
  the downed system is enabled (default **off per fight**, DM turns it on with
  `@dm downrule on` for set-piece battles — trash fights stay lethal-free/normal).
- **Downed state:** player is pinned (`setpcblock` + Play Dead sprite, reusing the
  `@dm novice` Play Dead grant), HP locked at 1, cannot act. A visible
  `npctalk`/effect marks them as "Dying."
- **Death saves:** every 4s, auto-roll `rand(1,20)`:
  - 10+ = success, <10 = fail (nat-20 = instant self-stabilize at low HP;
    nat-1 = two fails, per 5e).
  - **3 successes → Stable** (unconscious but safe; DM or a heal wakes them).
  - **3 fails → Out** (then normal RO death: respawn/resurrect, or a DM-set
    consequence flag).
- **Rescue:** any online ally standing within N tiles for one tick, OR any heal
  landing on the downed player, stabilizes them immediately (proximity via the
  `DM_HazardArea` area-scan inverted to detect allies).
- **DM overrides:** `@dm revive <player|party>` (instant full rescue),
  `@dm downrule <on|off>`, `@dm down <player>` (manually down someone for drama).
- **Safety:** `@dm cleanup` / `@dm mode off` clears all downed states, timers, and
  `setpcblock` freezes.

Knobs to confirm: default off-per-fight vs. on-in-DM-mode; save interval (4s);
tiles for ally rescue; and whether "Out" is plain RO death or a softer
consequence.

## Testing

Each command needs the same playtest treatment as the current checklist in
`planning/dm-handoff.md`: verify the GM gate, party-wide behavior with 2+ online
members, disconnect/reconnect safety (especially `setpcblock` and downed timers),
and that `@dm cleanup` / `@dm mode off` fully reset live state.
