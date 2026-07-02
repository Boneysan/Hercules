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

After setting:
```
@dmbeat
# choose arc and branch
@dm warp <boss map>
# spawn or use script NPC
```

Verify narration, adds, flags (`@dm status`), non-combat paths complete cleanly.

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

Known knob: the initial death still applies the RO EXP penalty before the
intercept; use `@dm exp` to hand it back if it matters.

## Other Quick Tests
- `@dm inspire <name>`, spend on `adv` check.
- `@dm spawn`, `@dm encounter`, `@dm scale hp 50 boss`, `@dm bloodied`.
- Full instance: `@dminstance` for an arc (e.g. Arc 4), complete a quest chain, check warps and hidden NPCs.
- Branch flags persist across logouts for party members.
- @dm novice for fresh chars (gives skills, clears tutorial flags).
- Open client Quest window after journal merge to verify 20001 "Omens at the Fountain" shows full flavor + @dm warp lines.

## Known / Watch For
- Client journal must be the merged .lub for @dm warps and flavor to appear.
- Normal MVPs must not linger when mode on.
- Hazards should not damage non-party or out-of-range.
- Kill credit stays with player even on DM-spawned mobs.

Run `./tools/campaign-preflight.sh` before every test session.

See also: dm-handoff.md for full checklists, campaign_client_assets.md for assets.
