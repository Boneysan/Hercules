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
| F2 | Per-character story flags drift when a player misses a session; NPC branches then differ depending on who clicks | high | WP-2 + WP-3 |
| F3 | `dm_flags.txt` is 387 lines of copy-paste; every new arc adds two hand-maintained functions; flag lists exist only inside code | med | WP-2 |
| F4 | Attach-RID party loop is duplicated ~15× across 8 files; a fix to iteration logic (e.g. isloggedin edge) must be applied everywhere | med | WP-4 |
| F5 | Docs claimed "GM level 60"; code gates at group level ≥ 1; the actual DM group (id 5) has level 1. Code is right — the stale doc lines (dm-tooling.md, dm-handoff.md, campaign-implementation-plan.md) were fixed with this review, but the threshold is still hardcoded in ~25 `bindatcmd` calls + `DM_RequireDM` | med | WP-1 |
| F6 | Downed and cutscene both toggle `PCBLOCK_MOVE`: releasing one releases the other's move lock (e.g. downed wake during a cutscene frees that player early) | low | WP-6 |
| F7 | `@dm status` shows story state but nothing about live-session health (exp rate, downed rule, registry size, hazard, active instance) — after a restart the DM can't see what silently reset | med | WP-5 |
| F8 | `.dm_params$` (NPC-scope) passes args from dispatcher to `callsub` subs; concurrent executions share it. Single-DM tables make this near-zero risk, but it's a trap for future contributors | low | WP-4 (convention), accepted meanwhile |
| F9 | Kill callbacks and timers reference FAKE_NPC names as strings (`"DM_Console::OnDMKilled"`, `"DM_DownedConsole::OnDeathSaveTick"`). Renaming an NPC breaks them silently | low | convention: grep before renaming any `DM_*Console` NPC; no code change |
| F10 | Quest-ID lists are duplicated (Session Board array, `S_Status`, `DM_EraseAllCampaignQuests`, quest_db, journal lua, hunt markers). Accepted: client tooling owns its copy; server copies are stable. Mitigate with an "adding an arc" checklist | low | WP-7 |
| F11 | No in-game session/audit log. Note: `bindatcmd(..., 1)` already logs every `@dm*` use to the SQL atcommand log if `conf` logging is on — that covers audit. Table-facing recap remains a roadmap feature | low | roadmap (`dm_session_log.txt`) |

---

## 6. Work packages

Each package is standalone, sized S/M, and ends with the standard validation:

```bash
bash ./script-checker $(find npc/custom/dm_campaign -name '*.txt' | sort)
./map-server --run-once
```

Do them roughly in order; WP-2 must precede WP-3.

### WP-1: Single source of truth for the DM permission gate (S)

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
   the registry via `getd("getvariableofnpc(.arc" + ... )` — follow the
   existing `getvariableofnpc` usage pattern; script-check early, this is the
   fiddly part.
3. Reimplement `DM_ClearArcXXFlags` as one generic `DM_ClearArcFlags(arc)`
   loop; keep the 19 old function names as one-line wrappers so arc files and
   `@dm flag cleararcXX` keep working.
4. Reimplement `DM_PrintArcXXFlags` the same way: generic loop printing
   `name=value`, 4 per line. Exact old formatting does not need preserving.
5. `DM_ClearAllArcFlags` becomes a 1..19 loop.

Acceptance: `@dm flag arc03` prints every arc-3 flag; `@dm flag cleararc03`
zeroes them all (verify one manually with `@dm flag get dm_arc03_started`);
file shrinks substantially; adding a future arc means adding one `setarray`.

### WP-3: `@dm flag sync` — fix branch drift for absent players (M)

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

Goal: the quest-ID duplication (F10) is safe because a checklist enumerates
every copy that must be updated together.

Files: `npc/custom/dm_campaign/CAMPAIGN.md` (new section).

List (verify each against the repo while writing — this is from review):
`db/quest_db.conf`; `act_XX/arc_YY.txt`; flag registry (WP-2) + wrappers;
quest arrays in `arc_01_prontera.txt` Session Board and `S_Status`;
`DM_EraseAllCampaignQuests` ranges; `dm_hunt_markers.txt`; `dm_beats.txt` menu;
`dm_symptoms.txt`; journal lua via `tools/campaign_quest_merge.py`; reward
pools in `dm_rewards.txt`; `@dm levels` table in `S_Levels`.

Acceptance: a junior can add a hypothetical Arc 20 touching only listed spots.

### WP-8 (deferred): move C hooks into an HPM plugin (M–L)

Only when an upstream merge first conflicts in `mob.c`/`pc.c`. Recreate
`mob_dm_mode_should_suppress` + spawn-delay as pre-hooks on `mob->spawn` /
`mob->ai_sub_hard` / `mob->ai_sub_lazy`, and the EXP scaling as a hook on the
EXP-award path, inside `src/plugins/dm_mode.c` (see `src/plugins/sample.c`).
Contract in §3 stays identical. Until then: when merging upstream, re-verify
the four variable reads still compile and fire.

---

## 7. What NOT to do (so it doesn't get "improved" by accident)

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
