# Seal Cascade DM Playtest Notes

This file collects concrete commands, flows, and notes for live client validation and game night prep. Use alongside `dm-handoff.md` and `client/README.md`.

## Prerequisites (run before connecting clients)
```bash
./tools/campaign-preflight.sh
# Then on server machine if LAN:
# ./tools/set-lan-ip.sh lan
```

DM account: use `./tools/create-account.sh` + `./tools/promote-dm.sh`.

Client: merge journal with `python3 tools/campaign_quest_merge.py --patch <your decompiled .lua>`, recompile .lub, copy BGM/cutins, update clientinfo.xml.

## Client Runtime QA Run Order

Use this order when validating the latest dialogue and branch implementation in
the live client.

1. Run `./tools/campaign-preflight.sh` on the server machine.
2. Start the server stack in separate terminals:
   - `./login-server`
   - `./char-server`
   - `./map-server`
3. Log into the RO client as `dmqa` / `dmqa123`, then create or select a GM
   character.
4. Log in a second client as `playerqa` / `playerqa123` when party sync needs to
   be tested.
5. Party the GM and player test characters, then run:
   ```
   @dmmode on
   @dm status
   ```
6. Run `Critical Branch QA` first, especially all six Arc 19 endings.
7. Record pass/fail notes under the relevant checklist item and mirror any
   blockers into `planning/dm-handoff.md`.

Server console note: `@dm` commands are player commands and must be run from an
authenticated in-game character. The `login-server`, `char-server`, and
`map-server` consoles only expose server maintenance commands.

## Sprint 1: Live Mode & Marker Validation (start here)
1. Log DM + 1-2 test chars in a party.
2. `@dmmode on`
3. Spawn or wait for a normal MVP/BOSS on map (e.g. in a non-campaign area).
4. Observe removal timing when mode on.
5. `@dmmode off` and check respawn resume.
6. Walk Prontera fountain area with 20001 active — check marker + journal text + @dm warp lines visible in client Quest UI.
7. Test `@roll 1d20+3`, hidden, fudge.

Sample commands:
```
@dmmode on
@dm status
@roll 1d20
@dm quest start 20001
@dm warp prontera 156 191
@dm symptom 1 pulse
@dm scene dread
@dm hazard 5 4 3 2500 poison 4000
@dm cutscene 20
@dm secret <testchar> You notice the statue's eyes follow you.
```

Confirm:
- Journal shows flavor + "Hunt: @dm warp ..." copy-paste lines.
- Yellow minimap arrows appear for hunts.
- Mode suppresses normal MVPs cleanly.

## Sprint 2: Branch Encounter Validation
Use `@dmbeat` menus to set branches then trigger bosses.

Key examples:
- Arc 8 (Glast Heim): Manfred fate → Dark Lord adds
- Arc 11: Bjorn joined/subdued → Randgris
- Arc 13: Carrion bribed/killed → Beelzebub or coalition
- Arc 15: Pratt outcomes → Thanatos echoes + hazard damage
- Arc 16: Rina exposed/rolled/defected → Bijou/Maret
- Arc 17: Admin choices

Decision registry checks:
```
@dm decide arc08.manfred killed
@dm decide status 8
@dm decide arc08.manfred spared
@dm decide status 8
@dm decide undo arc08.manfred
```

Verify `killed` and `spared` fully flip each other for every online party
member. The decision registry path should not auto-complete a quest; the
in-arc Manfred NPC completes `20122` before applying the same branch state.

Decision-drift test: log one party member out, run
`@dm decide arc08.manfred killed`, log them back in, then run
`@dm flag sync <present-player>` using a player who had the decision. Confirm
the returning member catches the chosen branch and does not keep a
contradictory sibling flag.

After setting:
```
@dmbeat
# choose arc and branch
@dm warp <boss map>
# spawn or use script NPC
```

Verify narration, adds, flags (`@dm status`), non-combat paths complete cleanly.

## Critical Branch QA

These are the highest-risk branches after the dialogue implementation pass. Run
each branch on a live test character because `script-checker` only proves parse
validity.

Before each family:
```
@dmmode on
@dm status
```

### Arc 10: Wynne Rescued / Lost

Fast path:
```
@dm decide arc10.wynne rescued
@dm decide status 10
@dm flag get dm_wynne_captured
@dm flag get dm_wynne_rescued
@dm flag get dm_wynne_lost
```

Repeat after undo/reset with:
```
@dm decide arc10.wynne lost
@dm decide status 10
@dm flag get dm_wynne_captured
@dm flag get dm_wynne_rescued
@dm flag get dm_wynne_lost
```

NPC path:
- Start Arc 10 through `Doctor Sabine Reuter#dm`.
- Open `Wynne's Field Kit#dm10` in Lighthalzen.
- Choose both outcomes on separate test runs.
- Visit the tavern and `Wynne's Ledger Copy#dm`.

Pass:
- `rescued` sets `dm_wynne_rescued=1` and clears captured/lost.
- `lost` sets `dm_wynne_lost=1` and clears captured/rescued.
- Tavern and ledger text match the chosen outcome.
- Arc 10 can still continue to Reise and Kiel.

### Arc 10: Echo Freed / Confronted

Fast path:
```
@dm decide arc10.echo freed
@dm decide status 10
@dm flag get dm_arc10_echo_freed
@dm flag get dm_echo_trusts_party
@dm flag get dm_arc10_reise_confronted
```

Repeat with:
```
@dm decide arc10.echo confronted
@dm decide status 10
@dm flag get dm_arc10_echo_freed
@dm flag get dm_echo_trusts_party
@dm flag get dm_arc10_reise_confronted
```

NPC path:
- Resolve `Echo#dm10` and `Director Hallan Reise#dm` on separate runs.
- Later inspect `Echo#dm18` and `Echo#dm19`.

Pass:
- `freed` sets `dm_arc10_echo_freed=1` and `dm_echo_trusts_party=1`.
- `confronted` sets `dm_arc10_reise_confronted=1` and clears Echo trust.
- Quest `20144` completes.
- Arc 18/19 Echo callbacks reflect the branch.

### Arc 16: Rina and Prontera United

Fast path:
```
@dm decide arc16.rina exposed
@dm decide status 16
@dm flag get dm_prontera_united
```

Repeat with:
```
@dm decide arc16.rina rolled
@dm decide status 16
@dm flag get dm_prontera_united
```

Repeat with:
```
@dm decide arc16.rina defected
@dm decide status 16
@dm flag get dm_prontera_united
```

NPC path:
- Resolve `Matron Rina#dm` all three ways on separate runs.
- Check Arc 18/19 callbacks that mention Prontera's condition.

Pass:
- `exposed` and `rolled` set `dm_prontera_united=1`.
- `defected` clears or leaves `dm_prontera_united=0`.
- Only one Rina branch flag remains set after each choice.
- Quest `20204` completes.

### Arc 19: All Six Endings

Unlock Refusal first when testing that path:
```
@dm decide arc10.echo freed
# or:
@dm decide arc15.pratt challenged
```

Test all outcomes:
```
@dm decide arc19.finale shared
@dm decide status 19
@dm decide arc19.finale reforged
@dm decide status 19
@dm decide arc19.finale queen
@dm decide status 19
@dm decide arc19.finale thanatos
@dm decide status 19
@dm decide arc19.finale refusal
@dm decide status 19
@dm decide arc19.finale unbound
@dm decide status 19
```

NPC path:
- Use `The Central Choice#dm` in Arc 19.
- Confirm Refusal appears only when `dm_echo_trusts_party` or
  `dm_arc15_pratt_challenged` is set.
- After each ending, inspect `Loki The Voice#dm`, `Mira Ashkey#dm19`, and
  `Echo#dm19` where applicable.

Pass:
- Exactly one finale flag is set after each choice.
- `dm_campaign_complete=1`.
- Quest `20233` completes.
- EXP reward fires once per test run.
- Refusal gating is correct.
- Post-finale witness dialogue matches the selected ending.

## Sprint 3: Hazards
Test manual + scripted.

Manual:
`@dm hazard 6 5 4 3000 stun 2000`

Scripted examples (trigger via beats or NPCs):
- Arc 4 Geffen seal pressure (curse)
- Arc 7 Einbroch smoke (blind)
- Arc 12 New World rift (confusion)
- Arc 14 Thor magma (Ifrit heat, reduced if Hesma exposed)
- Arc 15 Thanatos resonance (Pratt branch affects %)
- Arc 19 Ash Vacuum (Surt, Himmelmez bargain reduces)

Test: move in/out of range, disconnect/reconnect one player, map change.

Clear with `@dm hazard clear` or `@dmcleanup`.

## Sprint 4: Downed / Death Saves (needs 2+ chars in party)
1. `@dmmode on`, party up DM + 1 test char.
2. `@dm downrule on` — map should announce Death's Door is active.
3. Kill the test char (spawn something nasty or `@dm down <name>` for the manual path).
4. Watch: char stays up at ~1% HP, Play Dead sprite, pinned, immune; death saves roll every 4s in map chat.
5. Rescue paths to verify separately:
   - Walk the DM within 3 tiles → "stabilized by an ally" (unconscious, saves stop).
   - Heal the downed char (any heal) → back on their feet immediately.
   - Do nothing → 3 successes = STABLE, or 3 fails = real death (respawn normally).
   - Nat 20 → up with a 10% HP surge.
6. `@dm revive <name>` and `@dm revive party` — full HP/SP; also revives real deaths.
7. `@dm downrule status` — lists downed members with save counts.
8. Safety: with someone downed, run `@dmcleanup` and `@dm mode off` — pin must release both times; relog while downed must also clear the pin.
9. Confirm normal deaths (rule off, or non-party player) are untouched.
10. Cutscene overlap:
   - Start `@dm cutscene on`, down a player, then `@dm cutscene off`; the
     player must stay pinned until `@dm revive`.
   - Down a player, start `@dm cutscene on`, revive them, then
     `@dm cutscene off`; the final release must leave them mobile.

Known knob: the initial death still applies the RO EXP penalty before the
intercept; use `@dm exp` to hand it back if it matters.

## Other Quick Tests
- `@dm inspire <name>`, spend on `adv` check.
- Flag registry smoke: set `dm_arc03_started`, run `@dm flag arc03`, then
  `@dm flag cleararc03`; verify `@dm flag get dm_arc03_started` returns 0.
- `@dm status` mid-fight: confirm `[Session]` shows mode, party, instance,
  EXP scope, downed rule/counts, encounter count, hazard ticks, and bloodied GID.
- `@dm spawn`, `@dm encounter`, `@dm scale hp 50 boss`, `@dm bloodied`.
- Full instance: `@dminstance` for an arc (e.g. Arc 4), complete a quest chain, check warps and hidden NPCs.
- Branch flags persist across logouts for party members.
- @dm novice for fresh chars (gives skills, clears tutorial flags).
- Open client Quest window after journal merge to verify 20001 "Omens at the Fountain" shows full flavor + @dm warp lines.

## If the server dies mid-session (recovery runbook)
1. Restart MariaDB + login/char/map servers; players reconnect.
2. `$dm_mode` and the active party SURVIVE the restart — the session resumes
   where it was. Story flags and quests are safe (SQL).
3. These reset silently and must be re-armed if they were in use:
   - `@dm exprate <pct>` (back to 100)
   - `@dm downrule on` (back to off)
   - encounter registry / bloodied watcher / hazards / cutscene locks (gone —
     respawn boss adds with `@dm spawn`, re-arm `@dm bloodied`)
4. Run `@dm status` to see the current state before resuming play.
5. Worst case (corrupted state): stop servers and restore the latest dump —
   `ls -t backups/` and the restore line printed by `tools/backup-campaign.sh`.
   Preflight takes a snapshot every game night; take a labeled one manually
   before risky operations: `./tools/backup-campaign.sh pre_reset`.

## Known / Watch For
- Client journal must be the merged .lub for @dm warps and flavor to appear.
- Normal MVPs must not linger when mode on.
- Hazards should not damage non-party or out-of-range.
- Kill credit stays with player even on DM-spawned mobs.

Run `./tools/campaign-preflight.sh` before every test session.

See also: dm-handoff.md for full checklists, campaign_client_assets.md for assets.
