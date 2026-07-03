# DM Mode — Architecture Review & Improvement Plan

Written 2026-07-02, after the downed/death-saves feature shipped. This is a
senior review of how DM mode is built, whether that approach is right, and a
set of self-contained work packages a junior developer can pick up without
extra context. Read `planning/dm-handoff.md` ("Junior Developer Rules Of
Engagement") before starting any package here.

---

## 1. Architecture map (what exists today)

DM mode is four layers. Know which layer you are editing before you edit it.

```
┌────────────────────────────────────────────────────────────────────┐
│ 4. Client side    merged quest journal .lub, custom BGM/cutins,    │
│                   clientinfo.xml  (tools/campaign_quest_merge.py)  │
├────────────────────────────────────────────────────────────────────┤
│ 3. Campaign content   npc/custom/dm_campaign/act_XX/arc_YY.txt     │
│                   story NPCs gated on DM_PartyActive-style checks; │
│                   per-character story flags; quests 20000-20234    │
├────────────────────────────────────────────────────────────────────┤
│ 2. Shared DM layer    npc/custom/dm_campaign/shared/dm_*.txt       │
│                   one @dm dispatcher (dm_console.txt) + domain     │
│                   files (voice/checks/scene/combat/downed/...)     │
├────────────────────────────────────────────────────────────────────┤
│ 1. C hooks (minimal)  src/map/mob.c  — MVP/BOSS spawn suppression  │
│                   src/map/pc.c  — party EXP rate scaling           │
│                   both read SCRIPT variables via mapreg (see §3)   │
└────────────────────────────────────────────────────────────────────┘
```

Data flow: the DM types `@dm <sub>` → `DM_Console::OnDM` dispatches to a
`DM_*` function in a domain file → that function loops the active party
(attach-RID pattern) and/or pokes globals that layer 1 reads.

## 2. Verdict: is this the right way to build it?

**Yes.** Script-first with two thin C hooks is the correct architecture for
this project's goal (one DM, one party of friends, live improv on top of a
scripted campaign), and it should not be re-platformed. Reasons:

- **Iteration speed is the top requirement.** Campaign logic changes weekly;
  scripts reload without recompiling. Everything that CAN live in script does.
- **C is used only where script cannot reach** — the mob spawn engine and the
  EXP formula. Both hooks are ~40 lines, read script-owned variables, and make
  no policy decisions of their own. That's the right division.
- **The console architecture scales.** One `bindatcmd("dm")` dispatcher with
  per-domain implementation files has stayed clean through ~10 subsystems;
  `dm_console.txt` is 1.4k lines instead of the 4k it would be monolithic.
- **Instances-from-script** (no instance_db) keeps new dungeon setup at zero
  config cost.

Alternatives considered and rejected:

- **Web control panel / plugin API** (project-vision Phase 4): no table pain
  justifies it. The DM already plays at a keyboard in-client. Revisit only if
  a second DM or spectator-DM need appears. **Do not build.**
- **HPM plugin instead of direct src edits:** would keep upstream merges
  clean, but we merge upstream rarely and the diff is 80 lines. Deferred —
  see WP-8. Do it the first time an upstream merge actually conflicts there.
- **Multi-session support** (several parties, several DMs): `$dm_mode` /
  `$dm_active_party` are deliberately singletons. `DM_PartyActive()` exists so
  storage can change later without touching call sites. Leave it.

The real debts are not structural; they are (a) undocumented contracts,
(b) copy-paste growth in two hot spots, and (c) a few consistency gaps.
Those are the work packages below.

## 3. The script↔C contract (critical, previously undocumented)

`src/map/mob.c` and `src/map/pc.c` look up these script variables **by name**
through mapreg:

| Variable | Read by | Effect |
|---|---|---|
| `$dm_mode` | mob.c `mob_dm_mode_should_suppress` | ==1 removes/delays MVP & BOSS-flagged respawns (10s retry loop) |
| `$@dm_exp_party` | pc.c `pc_dm_exp_rate` | party id whose kills get scaled EXP |
| `$@dm_exp_char` | pc.c `pc_dm_exp_rate` | char id fallback target |
| `$@dm_exp_rate` | pc.c `pc_dm_exp_rate` | percent, 100 = normal |

**Rule: never rename these in script.** There is no compile-time check; a
rename silently turns the feature off. Any change must touch both layers and
both must be in the same commit.

Also note the asymmetry: `$dm_mode` is a **permanent** global (survives server
restart — MVPs stay suppressed across reboots mid-campaign, which is intended),
while `$@dm_exp_*` are **server-temp** (EXP scaling silently resets to normal
on restart). See §4 and WP-5.

## 4. State lifetime matrix (critical, previously undocumented)

Four storage classes are in play. Bugs in this codebase are usually someone
assuming the wrong row of this table.

| State | Vars | Lifetime | After server restart | After owner relogs |
|---|---|---|---|---|
| Session on/off, active party | `$dm_mode`, `$dm_active_party`, `$dm_inst_<pid>` | permanent global | **survives** | survives |
| EXP scaling, downed rule | `$@dm_exp_*`, `$@dm_downed_rule` | server-temp global | reset (off) | survives |
| Encounter registry, hazard, bloodied watcher | `@dm_enc_*`, `@dm_hazard_*`, `@dm_bloodied_*` (on the DM char) | char-temp | lost | **lost** |
| Player campaign state | `dm_arc*` flags, `dm_inspiration` (per character) | permanent char | survives | survives |
| Player live state | `@dm_downed`, `@dm_down_*`, `dm_cutscene_blocked` | char-temp | lost (pin self-clears) | lost (pin self-clears) |

Deliberate consequences (do not "fix" these):

- A DM relog drops the encounter registry — mobs stay alive but `@dm scale` /
  `@dm bloodied` lose their handles. Recovery: `@dm cleanup` and respawn.
- Downed/cutscene pins self-clear on relog. That is the disconnect safety net.
- Story flags live **per character**, written to online members only. This is
  a real drift risk — WP-3 addresses it.

## 5. Findings

Ranked by (risk to a live game night) × (cost to fix). F# = finding, WP# =
work package that fixes it.

| # | Finding | Risk | Fix |
|---|---|---|---|
| F1 | Script↔C variable-name contract undocumented (was §3 — now documented; keep it current) | high | done / WP-5 |
| F2 | Per-character story flags drift when a player misses a session; NPC branches then differ depending on who clicks | high | WP-2 + WP-3 (shipped server-side; live smoke test pending) |
| F3 | `dm_flags.txt` was copy-paste heavy; every new arc added two hand-maintained functions; flag lists existed only inside code | med | WP-2 (shipped server-side; live smoke test pending) |
| F4 | Attach-RID party loop is duplicated ~15× across 8 files; a fix to iteration logic (e.g. isloggedin edge) must be applied everywhere | med | WP-4 |
| F5 | Docs claimed "GM level 60"; code gates at group level >= 1; the actual DM group (id 5) has level 1. The default threshold now lives in `DM_Config.gm_level`; `bindatcmd(..., 1, 99, 1)` remains the engine floor. | med | WP-1 (shipped server-side) |
| F6 | Downed and cutscene both toggle `PCBLOCK_MOVE`: releasing one used to release the other's move lock (e.g. downed wake during a cutscene frees that player early) | low | WP-6 (shipped server-side; live movement test pending) |
| F7 | `@dm status` showed story state but nothing about live-session health (exp rate, downed rule, registry size, hazard, active instance) — after a restart the DM could not see what silently reset | med | WP-5 (shipped server-side; live smoke test pending) |
| F8 | `.dm_params$` (NPC-scope) passes args from dispatcher to `callsub` subs; concurrent executions share it. Single-DM tables make this near-zero risk, but it's a trap for future contributors | low | WP-4 (convention), accepted meanwhile |
| F9 | Kill callbacks and timers reference FAKE_NPC names as strings (`"DM_Console::OnDMKilled"`, `"DM_DownedConsole::OnDeathSaveTick"`). Renaming an NPC breaks them silently | low | convention: grep before renaming any `DM_*Console` NPC; no code change |
| F10 | Quest-ID lists are duplicated (Session Board array, `S_Status`, `DM_EraseAllCampaignQuests`, quest_db, journal lua, hunt markers). Accepted: client tooling owns its copy; server copies are stable. Mitigated with an "adding an arc" checklist. | low | WP-7 (complete) |
| F11 | No in-game session/audit log. Note: `bindatcmd(..., 1)` already logs every `@dm*` use to the SQL atcommand log if `conf` logging is on — that covers audit. Table-facing recap remains a roadmap feature | low | roadmap (`dm_session_log.txt`) |
| F12 | The DM-facing quest surface is numeric-only: `@dm quest start 20121` with no in-game id→name lookup or per-arc listing; the DM plays with CAMPAIGN.md alt-tabbed. (Players are fine — journal, questinfo, hunt markers.) | med | WP-9 |
| F13 | No improv-friendly way to record a story outcome. `@dmbeat` handles branch exclusivity correctly but buries decisions in nested menus among warps/spawns; raw `@dm flag set` knows nothing about exclusivity, so the DM can produce contradictory state (`manfred_spared=1` AND `manfred_killed=1` — downstream gates then pick one silently) | **high** | WP-10 |
| F14 | Flag write asymmetry: `@dm flag set` and `@dm reset` are party-wide, but `@dm flag cleararcXX` clears **the DM's character only** (its message admits it). Easy to leave the party on a branch the DM thinks was cleared | med | WP-10 step 5 |
| F15 | No latent trap / detect / disarm loop (hazards fire instantly at the DM's feet); puzzles are bespoke per arc (Arc 4's lever sequence is a good pattern but unextracted); no challenge-XP preset for non-combat solutions | med | WP-11, WP-12 |
| F16 | **No database backups.** All campaign state — story flags, quests, inspiration, characters, `$dm_*` globals — lives in MariaDB, and nothing dumps it. One bad `@dm reset confirm` or a wrong-source `@dm flag sync` (WP-3) loses the playthrough | **high** | WP-13 (shipped with this review) |

---

## 6. Work packages

Each package is standalone, sized S/M, and ends with the standard validation:

```bash
bash ./script-checker $(find npc/custom/dm_campaign -name '*.txt' | sort)
./map-server --run-once
```

Do them roughly in order; WP-2 must precede WP-3, and WP-9 through WP-12 are
motivated by the play-content review in §7 (read that section before starting
them). If picking by table impact instead: WP-10 (decisions), then WP-3
(flag sync), then WP-5 (session health), then WP-11 (traps).

### WP-1: Single source of truth for the DM permission gate (S)

Status 2026-07-02: shipped server-side. `DM_Config.gm_level` is now the
default permission gate for `DM_IsDM` / `DM_RequireDM`, while `bindatcmd(...,
1, 99, 1)` remains the engine floor. Preflight passed.

Goal: one constant decides who is a DM; docs match reality.

Files: `shared/dm_common.txt`, `shared/dm_console.txt`.

Steps:
1. In `dm_common.txt`, add a FAKE_NPC `DM_Config` with
   `OnInit: .gm_level = 1;` and a comment explaining group 5 ("Dungeon
   Master", level 1, set by `tools/promote-dm.sh`) is the intended audience.
2. Change `DM_IsDM` to default to
   `getvariableofnpc(.gm_level, "DM_Config")` instead of literal `1`.
3. Leave the `bindatcmd(..., 1, 99, 1)` group-level args as literal 1 — they
   are a floor, `DM_RequireDM` is the real gate; add one comment in
   `dm_console.txt` OnInit saying exactly that.
   (The stale "GM level 60" doc lines were already fixed with this review.)

Acceptance: changing `.gm_level` in one place changes the gate for every
command; a group-0 account gets the refusal message on every `@dm*` command.

### WP-2: Flag registry — turn dm_flags.txt into data (M)

Status 2026-07-02: shipped server-side. `DM_FlagRegistry` now owns 178 story
flag names, `DM_ArcFlagCount` / `DM_ArcFlagName` expose them for WP-3, and
clear/print/reset/party-clear paths all loop the same registry. Preflight
passed; still smoke-test `@dm flag arc03` and `@dm flag cleararc03` in-client.

Goal: each arc's flag list exists exactly once, as an array, usable by
clear/print/sync/status.

Files: `shared/dm_flags.txt` (rewrite), no callers change signatures.

Steps:
1. Add FAKE_NPC `DM_FlagRegistry` with `OnInit` doing, per arc:
   `setarray .arc01$[0], "dm_arc01_started", "dm_arc01_tibbets_befriended", ...;`
   Copy names verbatim from the existing `DM_ClearArcXXFlags` bodies —
   they are the authoritative list. Cross-arc gates (`dm_mira_lives`,
   `dm_echo_trusts_party`, `dm_act01_complete`, ...) stay in the arc that
   currently clears them.
2. Add `DM_ArcFlagCount(arc)` and `DM_ArcFlagName(arc, i)` helpers that read
   the registry. The shipped version flattens the per-arc arrays into
   `.flag_names$`, `.arc_start`, and `.arc_count` during `OnInit`, then reads
   them via `getelementofarray(getvariableofnpc(...))`.
3. Reimplement `DM_ClearArcXXFlags` as one generic `DM_ClearArcFlags(arc)`
   loop; keep the 19 old function names as one-line wrappers so arc files and
   `@dm flag cleararcXX` keep working.
4. Reimplement `DM_PrintArcXXFlags` the same way: generic loop printing
   `name=value`, 4 per line. Exact old formatting does not need preserving.
5. `DM_ClearAllArcFlags` becomes a 1..19 loop.

Acceptance: `@dm flag arc03` prints every arc-3 flag; `@dm flag cleararc03`
zeroes them all party-wide (verify one manually with
`@dm flag get dm_arc03_started`); adding a future arc means adding one per-arc
`setarray` and one registration call.

### WP-3: `@dm flag sync` — fix branch drift for absent players (M)

Status 2026-07-02: shipped server-side. `@dm flag sync <player>` snapshots all
registered story flags from an online member of the DM's current party and
writes them to the other online party members. Preflight passed; still
smoke-test with one returning player in-client.

Goal: after a session where a party member was offline, one command copies the
canonical story state onto them. Depends on WP-2.

Files: `shared/dm_flags.txt`, `shared/dm_console.txt` (dispatcher + help),
`planning/dm-playtest-notes.md`.

Steps:
1. Add `DM_FlagSyncFrom(source_char_name$)`: read every registry flag from the
   source player (attach, `getd`, detach — build a temporary `.@` value list
   per arc), then loop the other online party members and `setd` each flag to
   the source's value. Reuse the attach-RID pattern from `DM_PartyApplyFlag`
   (or `DM_PartyForEach` if WP-4 landed first).
2. Dispatcher: `@dm flag sync <player>` → source is `<player>`;
   `@dm flag sync` with no arg → source is the DM's current attach target
   error — require the name explicitly, ambiguity here corrupts state.
3. Report per-member counts: "synced 214 flags from Alice to 2 member(s)".
4. Add to help text and to the playtest notes (test: set a flag with one
   member logged out, log them in, sync, verify with `@dm flag get`).

Acceptance: a player who missed a session gets identical branch behavior from
story NPCs after one `@dm flag sync <present-player>`.

### WP-4: `DM_PartyForEach` shared iterator (M, incremental)

Goal: one implementation of "run X attached to each online party member".

Files: `shared/dm_common.txt` (new function), then migrate call sites
opportunistically.

Steps:
1. Implement in `dm_common.txt`:
   ```
   // DM_PartyForEach("<FuncName>", party_id, arg2, arg3, ...)
   // Calls callfunc("<FuncName>", arg2, arg3, ...) attached to each online
   // member; restores the caller's attachment; returns members reached.
   ```
   `callfunc` accepts a dynamic name string, so per-member logic lives in a
   small named `function script`. Preserve the exact skip rules used today:
   `isloggedin(accid, charid)` then `attachrid(accid)`.
2. Migrate ONE existing caller as the proof: `DM_ScenePortrait` (smallest,
   lowest risk — its body becomes a 3-line function + one ForEach call).
3. Migrate others only when a package already touches their file (do not do a
   big-bang rewrite; each migration must be playtested per the checklist).
4. Convention note for the file header: new party-wide features must use
   `DM_PartyForEach`; new `@dm` subcommands must be `callfunc`-style domain
   functions taking explicit args (not `.dm_params$` callsubs — F8).

Acceptance: `@dm scene <preset> <portrait>` still shows the cutin to every
online member and to the solo-DM case; grep shows `dm_scene.txt` no longer
contains its own getpartymember loop for portraits.

### WP-5: Session health in `@dm status` + lifetime doc (S)

Status 2026-07-02: shipped server-side. `@dm status` now starts with a
`[Session]` block for mode, active party, instance, downed rule/counts, EXP
scope, encounter registry, hazard ticks, and bloodied watcher state. The
operator lifetime matrix is copied into `CAMPAIGN.md`. Preflight passed; live
smoke-test during an encounter is still pending.

Goal: the DM can see at a glance what live state exists and what a restart
reset. Protects real game nights (F1, F7).

Files: `shared/dm_console.txt` (`S_Status`), `npc/custom/dm_campaign/CAMPAIGN.md`.

Steps:
1. Prepend to `S_Status` output a "[Session]" block:
   mode + active party (exists), downed rule (`$@dm_downed_rule`), exp rate
   (`$@dm_exp_rate` + scope), encounter registry count (`@dm_enc_count` after
   a `DM_EncounterPrune`), hazard ticks remaining (`@dm_hazard_ticks`),
   bloodied watcher gid, live instance id (`$dm_inst_<party>`).
2. If `$dm_mode` is on but `$@dm_exp_rate` is 100 and the registry is empty,
   print a hint: "(restart or DM relog since session start? exp rate and
   registries reset — see CAMPAIGN.md lifetimes)".
3. Copy the §4 lifetime matrix into `CAMPAIGN.md` (it's the operator manual;
   this review doc is not required reading at the table).

Acceptance: `@dm status` run mid-fight shows registry/hazard/downed truthfully;
run after a `map-server` restart it shows the reset state plus the hint.

### WP-6: Downed vs cutscene PCBLOCK interplay (S)

Status 2026-07-02: shipped server-side. Downed release now preserves movement
blocking while `dm_cutscene_blocked` is set, and cutscene release preserves
movement blocking while `@dm_downed` is set. Preflight passed; two-order live
movement test pending.

Goal: releasing one movement lock must not release the other (F6).

Files: `shared/dm_downed.txt`, `shared/dm_scene.txt`.

Steps:
1. In `DM_DownedBlock(0)` (release path): if `dm_cutscene_blocked` is set on
   the player, do NOT clear `PCBLOCK_MOVE` — clear only
   `ATTACK|SKILL|USEITEM|SITSTAND|IMMUNE`.
2. In `DM_CutsceneSelf(0)` (release path): if `@dm_downed` is set, keep
   `PCBLOCK_MOVE` set (the downed pin owns it) and skip the `cutin` clear only
   if the downed portraitless state needs none (it doesn't — clearing cutin is
   fine).
3. Playtest both orders: down someone during a cutscene then release the
   cutscene; start a cutscene with someone downed then revive them.

Acceptance: in both orders, the surviving lock still holds and the final
release (revive + cutscene off, any order) leaves the player fully mobile.

### WP-7: "Adding a new arc" checklist (S, docs only)

Status 2026-07-02: complete. `CAMPAIGN.md` now has a repo-specific checklist
covering arc scripts/includes, quest DB and journal source, server quest-ID
copies, flag and decision registries, beats, hunt markers, symptoms, rewards,
levels, reference tables, client merge, and preflight.

Goal: the quest-ID duplication (F10) is safe because a checklist enumerates
every copy that must be updated together.

Files: `npc/custom/dm_campaign/CAMPAIGN.md` (new section).

List (verify each against the repo while writing — this is from review):
`db/quest_db.conf`; `act_XX/arc_YY.txt`; flag registry (WP-2) + wrappers;
quest arrays in `arc_01_prontera.txt` Session Board and `S_Status`;
`DM_EraseAllCampaignQuests` ranges; `dm_hunt_markers.txt`; `dm_beats.txt` menu;
`dm_symptoms.txt`; journal lua via `tools/campaign_quest_merge.py`; reward
pools in `dm_rewards.txt`; `@dm levels` table in `S_Levels`. Once WP-9/WP-10
land, the quest registry and decision registry join this list (and replace
the Session Board / `S_Status` / `EraseAll` entries).

Acceptance: a junior can add a hypothetical Arc 20 touching only listed spots.

### WP-8 (deferred): move C hooks into an HPM plugin (M–L)

Only when an upstream merge first conflicts in `mob.c`/`pc.c`. Recreate
`mob_dm_mode_should_suppress` + spawn-delay as pre-hooks on `mob->spawn` /
`mob->ai_sub_hard` / `mob->ai_sub_lazy`, and the EXP scaling as a hook on the
EXP-award path, inside `src/plugins/dm_mode.c` (see `src/plugins/sample.c`).
Contract in §3 stays identical. Until then: when merging upstream, re-verify
the four variable reads still compile and fire.

### WP-9: Quest registry + `@dm quest list` (M)

Goal: the DM can identify any campaign quest in-game by arc, id, and name,
and the four hardcoded quest-ID lists collapse into one.

Files: new `shared/dm_quest_registry.txt` (or extend `dm_quests.txt`),
`shared/dm_console.txt` (S_Quest, S_Status), `act_01/arc_01_prontera.txt`
(Session Board array), `npc/scripts_custom.conf`.

Steps:
1. Build a `DM_QuestRegistry` FAKE_NPC whose `OnInit` holds, per arc, paired
   arrays: `setarray .arc01_id[0], 20001, 20002, ...;` and
   `setarray .arc01_nm$[0], "Omens at the Fountain (tracker)", "Contract: Cellar Vermin", ...;`
   Source ids and names from the arc file headers and `CAMPAIGN.md`'s table
   (both already list them); the first entry of each arc must be the arc
   tracker quest.
2. Helpers: `DM_ArcQuestCount(arc)`, `DM_ArcQuestId(arc, i)`,
   `DM_ArcQuestName(arc, i)`, `DM_QuestNameById(id)` (linear scan is fine),
   and `DM_ArcTrackerId(arc)`.
3. `@dm quest list <arc>`: per quest print id, name, and party progress as
   `done/inprog/missing` counts (attach-loop `questprogress` per member —
   use `DM_PartyForEach` if WP-4 landed).
4. `@dm quest list` with no arc: resolve the party's current arc (the
   first-in-progress-else-last-complete scan already exists on the Session
   Board — move it into a `DM_CurrentArc()` helper) and list that arc.
5. Echo names in existing feedback lines: "Quest 20121 (The Cursed Kingdom
   tracker) started for 3 member(s)."
6. Replace the hardcoded tracker arrays in the Session Board and `S_Status`,
   and the ranges in `DM_EraseAllCampaignQuests`, with registry reads.

Acceptance: `@dm quest list 8` shows Arc 8's quests with names and per-party
progress; `@dm quest start 20121` echoes the quest name; grep finds no
`setarray .@q[0], 20001,` duplicates left; adding an arc's quests means
editing only the registry.

### WP-10: Decision registry + `@dm decide` (M–L, highest table value)

Goal: after a roleplayed scene, the DM records the outcome in one command;
mutually exclusive branch flags can never contradict. Depends on WP-2's
registry idiom (build them the same way; they can share a file).

Status 2026-07-02: shipped server-side. `shared/dm_decisions.txt` now owns the
decision registry and `@dm decide` / `@dmdecide`; `@dmbeat` branch cases
delegate to it; `@dm flag cleararcXX` is party-wide. Preflight parse/load
passes. Live client playtest still needs the decision-drift test added to
`planning/dm-playtest-notes.md`.

Files: new `shared/dm_decisions.txt`, `shared/dm_console.txt` (dispatcher +
help), `shared/dm_beats.txt` (decision cases delegate), `dm-playtest-notes.md`.

Steps:
1. Registry shape, per decision:
   key (e.g. `arc08.manfred`), prompt ("Manfred's fate"), outcome keys
   (`spared`, `killed`), and per outcome: flags to set, flags to clear,
   optional tracker quest to complete, optional `dm_story_beat` value,
   announce line. Encode as parallel arrays or `|`-delimited strings per
   outcome — pick one, document it in the file header, keep it dumb.
   **Extract the data from the existing `DM_BeatArcXX` cases** — they already
   contain the set/clear/quest/beat/narration for every decision — and
   cross-check coverage against `planning/obsidian-campaign/Choice_Tracker.md`
   (it defines which choices must matter later, including the five campaign
   gates: mira/echo/prontera/varmundt/himmelmez).
2. `DM_Decide(key$, outcome$)`: applies clear-list then set-list via
   `DM_PartySetFlag`/`DM_PartyClearFlag` (party-wide, exclusivity guaranteed
   by data), completes the tracker quest if defined, sets `dm_story_beat`,
   fires the announce via `DM_MapStory`, and dispbottoms a confirmation.
3. Command surface:
   - `@dm decide` → menu (mes/select, like `@dmbeat`): current arc's
     decisions, decided ones annotated with the chosen outcome.
   - `@dm decide <arc>` → that arc's menu.
   - `@dm decide <key> <outcome>` → direct, no menu (the improv fast path).
   - `@dm decide status [arc]` → ledger: each decision `-> outcome` or
     `PENDING`. This is the in-game version of Choice_Tracker.md.
   - `@dm decide undo <key>` → clears all flags of every outcome of that
     decision (back to PENDING) — for "actually, the table re-litigated it".
4. Rewire the decision cases in `DM_BeatArcXX` to call `DM_Decide(...)` so
   there is one source of truth; beats keep their warp/spawn/start cases.
5. Fix F14 while in here: make `@dm flag cleararcXX` party-wide (route
   through `DM_PartyApplyFlag`), and update its message.
6. Alias `@dmdecide` in the new file's FAKE_NPC, per console architecture.

Acceptance: `@dm decide arc08.manfred killed` (or via menu) sets
killed=1/spared=0 for every online member, completes 20124, announces, and
`@dm decide status 8` shows it; setting the opposite outcome afterward fully
flips the flags; `@dmbeat` Arc 8 decision cases produce identical state to
`@dm decide`; playtest notes gain a decision-drift test (decide with one
member offline, then `@dm flag sync`).

### WP-11: Latent traps with saving throws — `@dm trap` (M)

Goal: the classic trap loop — place, (maybe) detect, (maybe) disarm, spring,
save — with RO-native check math. DM narrates; script rolls.
Read `planning/dm-traps-puzzles-guide.md` first — it's the engine cookbook
(primitives, archetypes, instance-safety rules) this package builds on.

Files: `shared/dm_traps.txt` (extend), `shared/dm_checks.txt` (small
refactor), `shared/dm_console.txt` (dispatcher + help + cleanup),
`shared/dm_session.txt` (cleanup), `dm-playtest-notes.md`.

Steps:
1. Refactor first: extract the roll core of `DM_Check`'s `S_Roll` into
   `DM_RollCheck(stat_const, dc, mode$)` returning pass/fail + the roll (keep
   the announce in the caller). Both `DM_Check` and traps use it — one place
   for the d20 + stat/10 + nat-20/nat-1 rules.
2. Trap store on the DM character (same lifetime class as hazards, §4):
   parallel arrays `@dm_trap_map$/x/y/radius/dc/dmg/status/status_ms/armed`,
   cap ~8.
3. `@dm trap set <radius> <dc> <dmg%> [status] [status_ms]` — places at the
   DM's position (stand where the trap goes, then step away). Reuse
   `S_HazardStatus` for status parsing and the hazard clamps for bounds.
4. Watcher: one repeating `addtimer` on the DM (pattern: `OnHazardTick`),
   every ~1s scanning armed traps vs online party positions (the coordinate
   compare from `DM_HazardArea`). Skip scanning entirely when no traps armed.
5. Spring (member enters radius): for each member inside `radius` — AGI save
   via `DM_RollCheck` vs the trap DC, announced like the death-save lines;
   pass = half `dmg%` and no status, fail = full `dmg%` + status. Disarm the
   trap (one-shot). Damage via `percentheal -(n),0` (cannot kill — note in
   help that a lethal follow-up is a DM choice, not a default; pairs with
   `@dm downrule on`).
6. Management: `@dm trap list` (index, map/coords, dc, armed), `@dm trap
   clear [i|all]`, `@dm trap reveal [i]` (announce "You spot a mechanism..."
   — pair with the perception check the DM already rolled), `@dm trap disarm
   <player> [i]` — DEX check vs DC+2: success removes it; **nat 1 springs it
   centered on the disarmer**.
7. Wire `@dm cleanup` and `@dm mode off` to clear all traps + the watcher
   timer; add the new vars to the §4/CAMPAIGN.md lifetime matrix (DM-char-temp
   row); add `@dmtrap` alias.

Acceptance: place a trap, walk a test char in — save rolls announce, damage
and status differ pass vs fail, trap disarms after firing; reveal + disarm
flow works including the nat-1 backfire; `@dmcleanup` removes all traps;
DM relog drops traps (documented, matches hazard behavior).

### WP-12: Puzzle templates + challenge XP (S–M)

Goal: new puzzles are instantiated, not hand-rolled; non-combat solutions pay
XP consistently with the arc's level targets.
Read `planning/dm-traps-puzzles-guide.md` first — §4 defines the archetypes
these templates implement (4a lever sequence, 4b riddle, 4f timed variant).

Files: new `shared/dm_puzzles.txt`, `shared/dm_console.txt` (S_Exp + help),
`npc/scripts_custom.conf`, `CAMPAIGN.md` (how-to section).

Steps:
1. Extract the Arc 4 lever pattern into `DM_PuzzleStep(prefix$, step, total,
   wrong_event$)`: sets `<prefix><step>` if all lower steps are set, else
   resets via `DM_ResetPuzzleFlag` and fires the optional consequence event
   (`donpcevent` — e.g. a spawn or hazard label). Arc files keep tiny NPC
   bodies: the gate NPC checks all flags, each lever calls `DM_PuzzleStep`.
   Retrofit Arc 4 to use it as the reference implementation.
2. Add `DM_PuzzleRiddle(flag$, attempts_flag$, max_attempts, fail_event$)` +
   a documented copy-paste NPC template using `select()` with one correct
   option among decoys (or `input()` for a password — offer both in the
   template comment). Success sets the flag; exhausting attempts fires the
   consequence event. State in instance/party flags like everything else.
3. `@dm exp challenge <minor|standard|major>`: party EXP preset scaled from
   the arc target-level table already shown by `@dm levels` (use
   `DM_CurrentArc()` from WP-9; fallback: DM supplies the arc as an extra
   arg). Suggested scaling: minor/standard/major ≈ 25%/50%/100% of one
   mob-grind "bar" at the arc's target level — tune once at the table.
   Announces "[DM] The party overcomes the challenge." so players see the
   payout without combat.
4. Document both templates + the XP presets in `CAMPAIGN.md` with one worked
   example each.

Acceptance: Arc 4 behaves identically after the retrofit (regression-check
lever order + reset-on-wrong-step + gate); a new 3-step puzzle needs only
flag names and NPC shells; `@dm exp challenge standard` pays sensible EXP at
Arc 1 and at Arc 15 levels without the DM doing math.

### WP-13: Campaign database backups (S) — SHIPPED with this review

`tools/backup-campaign.sh` dumps the whole `ragnarok` DB (gzipped,
timestamped, optional label, keeps the newest 20) into `backups/`
(gitignored), refuses to keep a failed or implausibly small dump, and prints
the restore one-liner. `campaign-preflight.sh` now runs it as step 0, so
every game night starts with a snapshot automatically.

Verified 2026-07-02 with MariaDB up. `./tools/backup-campaign.sh verify`
wrote `backups/ragnarok_20260702_180239_verify.sql.gz` (13K on disk; 16K via
`du -h`). Restoring that dump into `ragnarok_restore_test` matched the live
campaign tables exactly: `char_reg_num_db` 8/8, `quest` 14/14,
`map_reg_num_db` 14/14, and `map_reg_str_db` 26/26. `campaign-preflight.sh`
also wrote a fresh pre-session backup and passed script/load validation.

---

## 7. Play-content subsystems: quests, story decisions, traps & puzzles

Reviewed 2026-07-02 as a follow-up pass. Same verdict shape as §2: the bones
are right, the gaps are UX and extraction, not architecture.

### 7.1 Quest identification

What works — keep and do not rebuild:

- **Player side is solved.** The merged client journal shows flavor text plus
  copy-paste `@dm warp` lines; `questinfo` bubbles mark givers; 45 hunt-marker
  NPCs (`dm_hunt_markers.txt`) put yellow minimap arrows on hunt zones. This
  is better quest UX than most retail content.
- `@dm quest sync/refresh` already handle party drift and client desyncs.

The gap is the **DM side**: quest IDs are bare numbers everywhere (F12).
Quest names exist only in `db/quest_db.conf` (script cannot read names — no
such buildin) and in the client journal. The server scripts need their own
small name registry — same idiom as the WP-2 flag registry. See WP-9.

### 7.2 Story decisions (the roleplay → game-state loop)

There are three recording paths today, and each is individually correct:

1. **In-dialogue player choices** (e.g. Deacon Holt in arc_01): the NPC's
   `select()` sets the chosen flag AND explicitly zeroes the sibling
   (`holt_spared=1, holt_killed=0`). Best immersion; keep as the primary path
   when the scene is scripted.
2. **`@dmbeat` menus**: also disciplined — each decision case clears the
   sibling flag, sets the choice, completes the tracker quest, bumps
   `dm_story_beat`, and narrates via `DM_MapStory`. Right tool for prepped
   beats, but decisions sit inside Act→Arc menus mixed with warps and spawns —
   too slow mid-roleplay.
3. **Raw `@dm flag set`**: party-wide and instant, but the DM must recall the
   exact flag name and manually zero siblings, which nobody does at the table
   (F13).

The missing piece for the intended play style — DM improvises the scene with
`@dm say` / `@dm check`, players roleplay, then the outcome goes into the
game — is a fourth path that is as fast as (3) and as safe as (2). That is
WP-10 (`@dm decide`, backed by a decision registry). The registry data is
**extraction, not invention**: `dm_beats.txt` cases and
`planning/obsidian-campaign/Choice_Tracker.md` already enumerate every
decision, its outcomes, and its flags.

### 7.3 Traps & puzzles

What exists: `@dm hazard` (ticking AoE centered on the DM at cast time),
`DM_HazardArea` (the party-only area-damage helper), arc-scripted hazards via
`dm_symptoms.txt`, one real puzzle implementation (Arc 4's three-lever
sequence, hand-rolled on `dm_arc04_puzzle_1..3` + `DM_ResetPuzzleFlag`), and
`@dm check` as a universal resolution mechanic.

What's missing for the D&D dungeon-crawl feel (F15):

- **Latent traps.** Nothing waits for the party; every hazard is DM-triggered
  in the moment. The classic loop — party walks in, trap springs, everyone in
  the blast rolls a save — requires the DM to improvise three commands and
  narrate over the seams.
- **Detect/disarm as a loop.** A perception check (`@dm check party int 14`)
  works today, but success changes nothing mechanically — there is no trap
  object to reveal or disarm.
- **Puzzle reuse.** Arc 4's lever pattern is sound (instance flags, reset on
  wrong step, gate NPC checks all flags) but lives only in that file.
- **Non-combat XP.** `@dm exp <base> [job]` exists but makes the DM invent
  numbers; puzzles and talked-out encounters should pay consistently with the
  arc's level targets (`@dm levels` table).

WP-11 and WP-12 close these. Design rule for both: the trap/puzzle layer must
stay **DM-narrated first** — script provides the dice, damage, and state;
the DM provides the description. No auto-generated flavor text.

Full implementation guidance — engine primitives (OnTouch/OnUnTouch trigger
areas, progressbar, setcell, enable/disable, getareausers), six trap and six
puzzle archetypes with sketches, stock-script references (Juperos, WoE
levers), and the instance-safety + playtest checklists — lives in
`planning/dm-traps-puzzles-guide.md`.

## 8. What NOT to do (so it doesn't get "improved" by accident)

- No web panel, REST API, or Discord bot. In-client script tools only.
- No multi-session/multi-DM generalization. `DM_PartyActive()` is the seam if
  it's ever needed; do not pre-build it.
- No conversion of DM improv tools into hard automation. Flexibility that
  looks "unfinished" (e.g. `@dm scale` accepting any percent, hazards without
  bounds-checking every combination) is intentional DM trust — see the Rules
  of Engagement in `dm-handoff.md`.
- Do not rename `$dm_mode`, `$@dm_exp_*`, or any `DM_*Console` FAKE_NPC
  without grepping both `npc/custom/dm_campaign/` and `src/map/`.
- Do not store new live-session state in permanent `$` globals by default:
  pick the row of the §4 matrix that matches the state's intended lifetime,
  and add it to the matrix.

## 9. Consolidated roadmap (the single pick-up list)

Work items currently live in two documents: the WPs above and the remaining
live-table features specced in `planning/dm-live-table.md` (LT items below —
their specs stay in that doc). This table merges both into one ordered list.
Pick from the top unless a dependency says otherwise.

| # | Item | Size | Depends on | Why this position |
|---|---|---|---|---|
| 1 | WP-13 backups — **complete** | S | — | Protects everything below |
| 2 | WP-10 decision registry + `@dm decide` — **shipped; live drift test pending** | M–L | WP-2 idiom (can be built together) | Highest table value; protects story integrity |
| 3 | WP-2 flag registry as data — **shipped server-side; live smoke test pending** | M | — | Unblocks WP-3; removes flag-list duplication |
| 4 | WP-3 `@dm flag sync` — **shipped server-side; live smoke test pending** | M | WP-2 | Fixes absent-player branch drift |
| 5 | WP-5 session health in `@dm status` — **shipped server-side; live smoke test pending** | S | — | Restart/relog visibility at the table |
| 6 | LT: `@dm secret <player> <text>` | S | — | Quick win; spec in dm-live-table.md §8 |
| 7 | WP-1 permission-gate constant — **shipped server-side** | S | — | Trivial; do alongside anything |
| 8 | WP-6 downed/cutscene PCBLOCK interplay — **shipped server-side; live movement test pending** | S | — | Known interaction bug |
| 9 | WP-11 `@dm trap` | M | read the traps/puzzles guide | First big feel upgrade for dungeons |
| 10 | WP-12 puzzle templates + `@dm exp challenge` | S–M | guide §4; `DM_CurrentArc()` from WP-9 (or inline it) | Pays out non-combat play |
| 11 | WP-9 quest registry + `@dm quest list` | M | — | DM quality-of-life; kills ID memorization |
| 12 | WP-4 `DM_PartyForEach` | M | — | Incremental; fold into other packages' files |
| 13 | LT: initiative/spotlight | M | WP-11's `DM_RollCheck` extraction | Spec in dm-live-table.md §10 |
| 14 | LT: recap log (`@dm log` / `@dm recap`) | S–M | — | Spec in dm-live-table.md §12 |
| 15 | LT: tavern downtime hub | M | — | Spec in dm-live-table.md §11; session-flow polish |
| 16 | WP-7 new-arc checklist — **complete** | S | after WP-9/10 land (they change the list) | Docs |
| 17 | WP-8 HPM plugin migration | M–L | first upstream merge conflict | Deferred by design |

Two scheduling notes: items 2–4 all touch flag machinery — one developer
should own that cluster and land it as WP-2 → WP-10 → WP-3 (registry, then
decide, then sync). Items 9–10 plus the guide's archetypes are a natural
second track that doesn't collide with the first.
