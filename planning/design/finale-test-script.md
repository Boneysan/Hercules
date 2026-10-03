# Finale test script (Arc 19) — DM runbook

**Status:** written 2026-10-02 against the rebuilt finale. **Not yet run.** The expected texts below come from reading the scripts, not from a session, so the first real run may find wording differences. A wrong *behavior* is the finding; a wrong *quoted sentence* is just a typo in this file.

**What it covers:** the ending-eligibility matrix from the handoff — each route ready; each prerequisite absent; Queen pact with the killed flag also present; two conversations committing different endings; a missing volunteer; a repeated commit; resume after Surt but before the choice.

**You need:** two characters in one party. One is the DM (GM level 1 or higher), one is a player. A second player is only needed for tests 7 and 8; the DM character can stand in for the player in the others. All commands below are typed in chat.

---

## 0. Before any session (no client needed)

From `Hercules/`:

```sh
./map-server --run-once 2>&1 | tr '\r' '\n' | grep -E '\[Error\]|DM walk'   # expect no output
rg -n 'select\([^\n]*"[^"]*:[^"]*"' npc/custom/dm_campaign                   # expect no output
```

Then start the servers (`./dev.sh restart && ./dev.sh wait`) and log both characters in.

## 1. Session setup

1. Form a party with the player as a member and the DM in it.
2. `@dmmode on` — expect `DnD mode enabled`. (It refuses without a party.)
3. `@dmpreset list` — expect the list of presets. If it says unknown command, the preset script did not load; stop.
4. `@dmpreset finale-reset`, then `@dmmode off` and `@dmmode on` again to clear the party's once-only grants. Do this between tests.

**Where things are:** Loki `moc_ruins 150,150`, the preparation board `moc_ruins 154,150`, the support console `moc_fild22 172,142`, the Central Choice `moc_fild22 175,140`. Warp with `@warp moc_ruins 152 150` etc.

**Reading state:** `@dmflag get <flag>` prints one flag. The ones that matter: `dm_arc19_prepared_mask`, `dm_arc19_groups_agreed`, `dm_arc19_volunteer_kind`, `dm_arc19_final_choice`, `dm_campaign_complete`, and the five `dm_finale_*`.

---

## 2. Test A — the bare world

`@dmpreset finale-bare`, warp to the board, talk to **Final Preparations**, choose *Show readiness for all five*.

Expected, one line per ending:

| Ending | Expected |
|---|---|
| Shared Seal | Needs preparation: two groups must explicitly agree … (0 so far) |
| Reforged Seal | Needs preparation: the design is not exported; the prototype is not verified; no maintenance team has agreed |
| Queen's Bargain | Needs preparation: no pact has been agreed (return to Niflheim) |
| Thanatos's Road | Needs preparation: the cost has not been disclosed … no informed volunteer has consented |
| Ragnarok Unbound | Needs preparation: the party must accept release … |

Then prepare **Ragnarok Unbound** (the only one reachable at once): choose it, confirm.
**Pass:** `@dmflag get dm_arc19_prepared_mask` = 16, and Unbound now shows `Ready.` while the other four are unchanged.

## 3. Test B — the generous world, each route made ready

`@dmpreset finale-all`. On the board, show readiness. **Nothing should say Ready yet** (preparation is explicit; the preset only sets history). Expected: Shared needs two groups asked; Reforged, Queen, Road and Unbound each say `Needs preparation` with only the *prepare* step missing.

Prepare each in turn and watch the mask:

1. **Shared Seal.** Choose it. The board lists up to six groups that have a recorded agreement and *asks you to ask each one* (Einbroch crews, Vance's crew, Hugel, the Naga, Rachel's pilgrims, the Biolab team). Ask two or more, then *Prepare the distribution rite*. **Pass:** mask gains bit 1; `dm_arc19_groups_agreed` has at least two bits set. **Check the negative:** do this once and *skip every group*, then confirm the rite is not offered and Shared stays `Needs preparation (0 so far)`.
2. **Reforged Seal.** Choose it, then *Prepare the counter-frequency*. **Pass:** bit 2.
3. **Queen's Bargain.** Choose it, *Confirm the pact is intact*. **Pass:** bit 4.
4. **Thanatos's Road.** Choose it. Pick *A member of this party volunteers* and answer yes twice as the **player** character. **Pass:** bit 8, `dm_arc19_volunteer_kind` = 1, `dm_finale_road_volunteer` = 1 **on that character only** (check with `@dmflag get` while logged in as the other character: expect 0 or unset on it — the flag is per-character).
5. **Unbound.** Accept, confirm. **Pass:** bit 16.

Mask should now read **31**, and all five show `Ready.`

## 4. Test C — each prerequisite absent

For each row: `@dmpreset finale-all`, apply the one change, open the board's readiness list. The named ending must **not** say Ready after you try to prepare it.

| Change | Command | Ending | Expected |
|---|---|---|---|
| Design not exported | `@dmflag clear dm_arc17_design_exported` | Reforged | board offers *Export the design from the Administrator's archive*; after that, preparable |
| Prototype not verified | `@dmflag clear dm_arc17_prototype_verified` | Reforged | *"The prototype was never verified. That has to be done at the Varmundt Biolabs."* Not preparable from the board |
| No maintenance team | `@dmflag clear dm_arc17_maintenance_secured` | Reforged | board offers *Ask engineers to volunteer*; after that, preparable |
| No pact | `@dmflag clear dm_arc18_pact_valid` | Queen | *"No pact has been agreed… Himmelmez is still available."* Not preparable |
| Cost not disclosed | `@dmpreset finale-no-cost` | Road | *"The cost has not been disclosed."* Not preparable |
| Fewer than two groups | skip all groups (see B.1) | Shared | rite not offered |

## 5. Test D — the Queen, killed

1. `@dmpreset finale-queen-dead`. Board readiness: **Queen's Bargain: Unavailable: Himmelmez fell. This route cannot be restored from a menu.**
2. Choose *Prepare The Queen's Bargain* on the board: *"Himmelmez fell…"* and the mask does not gain bit 4.
3. `@dmpreset finale-contradiction` (pact valid *and* killed). Readiness: **Unavailable: the record is contradictory (a pact marked valid, and Himmelmez killed). The DM needs to repair it.** It must not read Ready under any preparation.

## 6. Test E — Surt, support actions, and the commit

1. `@dmpreset finale-all`, prepare **all five** as in Test B (mask 31).
2. `@dmbeat 19` and choose *Spawn Surt* (option 6). Expected: Surt appears at `moc_fild22 170,140`, four *Surt's Wave* monsters around it, and the rift pulses begin.
3. At **Support Console**, use each prepared answer once. Expected messages:
   - Shared / Road: *"A ward steadies. The pulses will come softer."* — later pulse damage is lower.
   - Reforged / Unbound: *"A reinforcement wave breaks against what you prepared."* — the four adds die.
   - Queen: your HP/SP jump, *"The dead hold the edge of the field for a breath."*
   - Using the same one twice: it is skipped (once per answer per fight).
4. Defeat Surt, or `@dmbeat 19` → *Surt defeated*. Then `@dmflag get dm_arc19_surt_defeated` = 1.

## 7. Test F — commitment

At the **Central Choice** (`moc_fild22 175,140`), with Surt defeated and mask 31:

1. The conversation lists all five with `Ready.` and, after you pick one, prints its **Cost** *before* asking you to confirm. **Pass:** you can read the cost, say *Wait*, and be returned to the list with nothing committed (`dm_arc19_final_choice` still 0).
2. Choose **The Shared Seal**, confirm. Expected sequence: an implementation page, the tailored epilogue (Pratt/Rina/Vance/etc. lines for your world), three cards (`[A place]`, `[A person]`, `[An obligation]`), then *"[DM] The Seal Cascade ends."* and a server announcement.
3. **Pass:** `dm_arc19_final_choice` = 1; **exactly one** of the five `dm_finale_*` is 1; `dm_campaign_complete` = 1; EXP was granted once (check with `@dmstatus` or your exp bar).
4. **Repeated commit:** talk to the Central Choice again. Expected: the "choice was made" line (and, for the Road volunteer, *"You chose this. The seal is you now…"* only on that character). `dm_arc19_final_choice` must not change.

Repeat F.2–F.4 for each of the five endings (reset between runs, section 1 step 4). Check the cards use real state: Shared names *"The New World camp"* in the generous world; Road names the volunteer; Unbound names *"Foreman Dunmar"* when `dm_arc14_evacuation_stage` = 3.

## 8. Test G — two conversations, different endings

Needs **two characters** in the party at the Central Choice with Surt defeated and all five ready.

1. Character A: open the conversation, choose *The Shared Seal*, stop at the **Confirm** prompt.
2. Character B: open the conversation, choose *The Reforged Seal*, stop at **Confirm**.
3. Character A confirms. Expected: the ending plays.
4. Character B confirms. **Expected (the point of the test): *"An answer was given a moment ago, in another conversation. Only one is given."*** B's conversation ends.
5. **Pass:** `dm_arc19_final_choice` = 1 and only `dm_finale_shared_seal` is set. `dm_finale_reforged_seal` must be 0.

## 9. Test H — the volunteer is not there

1. `@dmpreset finale-all`; prepare Road with the **second player** volunteering (yes, yes). Prepare the others if you like.
2. Have the volunteer **log out**. Surt defeated, DM at the Central Choice.
3. Choose **Thanatos's Road**, confirm. **Expected: *"Your volunteer is not here. This choice pauses until they are."*** and the conversation ends.
4. **Pass:** `dm_arc19_final_choice` = 0 and the grant was **not** consumed (log the volunteer back in and the Road must now commit normally).
5. Variant: record *Keeper Lysandra* as the volunteer instead (board option 2). That commits with nobody online; the epilogue names her.

## 10. Test I — resume after Surt, before the choice

1. Surt defeated, nothing committed. Both characters log out and back in.
2. **Pass:** prepared mask, volunteer and groups are unchanged; the Central Choice still works; the board still shows the same readiness.

## 11. Test J — Loki's briefing

1. `@dmpreset finale-reset`, `@dmflag set dm_arc19_started 0`, warp to Loki, talk to him.
2. **Pass:** the **required** account is three short pages (the seal failing; what you found; where the board and Surt are). The long Act I–IV history appears **only** if you choose *Review our journey*. *Hear from our allies* shows at most three accounts, and a bare world shows *"No one has come to speak."*
3. Talk to Loki again after briefing: he points to the board and Surt, and never asks for a hunt turn-in. Quest 20232 (Beyond the Veil) should not appear in the quest log.

---

## What a failure looks like (so you can tell a bug from a typo)

| Symptom | Likely cause |
|---|---|
| `@dmpreset` is an unknown command | `dm_finale_presets.txt` not loaded (check `npc/scripts_custom.conf`) |
| A menu shows one item split in two | a `:` inside a `select` label |
| An ending commits with its prerequisite missing | `DM_Arc19Ready` and the board disagree; read `arc_19_finale.txt` top |
| Two flags set in `dm_finale_*` | the commit latch (`arc19_choice` grant) was bypassed or cleared mid-test |
| EXP granted twice | the once-only grant list was cleared between steps (`@dmmode off`) |
| The Road commits with an offline volunteer | `DM_Arc19VolunteerPresent` read stale ids (`$dm_arc19_vol_aid_<party>`) |

Report what you see against the expected line. Anything that differs in *behavior* is worth a note; anything that differs only in wording can be fixed in the script.
