# DM Mode / `@dm` Troubleshooting (Breadcrumbs)

Live-fixed 2026-07-11 on the Seal Cascade + Korangar stack
(`PACKETVER=20220406`, account group Admin 99, char `test`).

Use this when `@dm mode on` “does nothing”, reports **Mode is currently OFF**,
or never shows `[DM] …` feedback after a rebuild or script rewrite.

---

## Expected happy path

1. Log in as a GM/DM account (group with `getgmlevel() >= 1`; Admin is 99).
2. Optionally form a party first (mode stores `$dm_active_party`).
3. Either:
   - type **`@dm mode on`** in chat (no space after `@`), or
   - open **GM / DM Commands** (`Ctrl+O` in Korangar) → **DM mode ON**.
4. Chat should show roughly:
   - `→ @dm mode on` (client local echo for `@…` sends)
   - `[DM] DnD mode enabled. MVP spawns will be suppressed.`
   - `[DM] Campaign NPCs are active for party <id>.`
5. Prontera mapannounce (if anyone is on Prontera): campaign session begun.

Verify state anytime:

```text
@dm mode
@dm status
```

Reload scripts after editing NPC files (no full rebuild needed):

```text
@reloadscript
```

---

## Symptom A — “Mode is currently OFF” after clicking ON or typing `@dm mode on`

### What it means

`S_Mode` ran, but **the `on` argument was empty**. The script fell through to
the status/usage branch in `dm_console.txt` (`S_Mode`).

### Root cause (server script)

Hercules **`.@` variables are scope-local**.

| Step | What happens |
|------|----------------|
| `bindatcmd` fires `OnDM` / `OnMode` | Sets `.@atcmd_parameters$[]` and `.@atcmd_numparameters` in **that** scope |
| `callsub(S_Mode, …)` | Starts a **new** `.@` scope |
| Inside `S_Mode` | `.@atcmd_parameters$` is empty → `.@action$` ≠ `"on"` / `"off"` |

Same bug hits every `S_*` label that used to read `.@atcmd_parameters$` after
`callsub` (reward, flag, warp, exp, hazard, instance, spawn, reset, …).

### Fix (already applied in tree)

File: `npc/custom/dm_campaign/shared/dm_console.txt`

1. **Before** any `callsub` that needs args, bridge into character temps
   (visible across `callsub`):

```text
deletearray @dm_atcmd_p$[0], 128;
copyarray @dm_atcmd_p$[0], .@atcmd_parameters$[0], .@atcmd_numparameters;
@dm_atcmd_n = .@atcmd_numparameters;
```

2. Inside all `S_*` helpers, read **`@dm_atcmd_p$` / `@dm_atcmd_n`**, not
   `.@atcmd_parameters$`.

3. Keep using `.@atcmd_*` only in the **On\*** event body (same scope as
   `bindatcmd`).

Do **not** put the bridge itself behind `callsub` — that would wipe `.@` again.
Inline the three lines (or `goto` a label in the same scope).

### Quick re-break check after a rewrite

If someone “simplifies” the console back to:

```text
callsub(S_Mode, 1);
// S_Mode: .@action$ = .@atcmd_parameters$[getarg(0)];
```

…this symptom returns immediately. Re-apply the bridge pattern.

### Alternate valid patterns

- Pass strings via `getarg` only: `callsub(S_Mode, .@atcmd_parameters$[1]);`
- Or use `goto S_Mode` with `.@offset` set (same scope; use `end` not `return`).

---

## Symptom B — Command works on server but **no** `[DM]` text in client chat

### What it means

`dispbottom` / `clif_disp_onlyself` ran (map log may show
`clif_disp_message: Truncated message…` for very long help lines), but the
client dropped the packet.

### Root cause (Korangar)

Hercules sends self-only / guild-style display on **`0x017F`**
(`clif_disp_message` / `clif_disp_onlyself`). That is **not** `0x008E`
(`ServerMessagePacket`).

Length table already knew `0x017F` was variable-length (`-1`), so the stream
stayed aligned, but with **no handler** the message was discarded.

### Fix (already applied in tree)

| Piece | Location |
|-------|----------|
| Packet struct | `korangar/ragnarok-packets/src/lib.rs` → `DisplayBottomMessagePacket` `#[header(0x017F)]` |
| Handler | `korangar/korangar-networking/src/packet_versions/version_20220406.rs` → `ChatMessage` / `MessageColor::Server` |
| Local `@` echo | `korangar/korangar/src/lib.rs` → `SendMessage`: push `→ {text}` when text starts with `@` |
| GM panel | `korangar/korangar/src/interface/windows/commands.rs` → sends `@dm mode on` etc. |

Rebuild client after touching those crates:

```bash
cd korangar && cargo build --release -p korangar
# restart the client binary (stale process = old code)
```

### Quick re-break check

If `DisplayBottomMessagePacket` is missing or only registered as
`register_noop` / length-fallback, `@dm*` and most `dispbottom` feedback go
silent again. Confirm with:

```bash
strings target/release/korangar | grep DisplayBottomMessagePacket
```

---

## Symptom C — Nothing at all / wrong command syntax

| Mistake | Result |
|---------|--------|
| `@ dm mode on` (space after `@`) | Not an atcommand |
| `@dmmode` with no `on` | Status only (OFF/ON + usage) |
| Non-DM account | `[DM] You do not have permission…` (`DM_RequireDM`) |
| Scripts not reloaded after edit | Old broken logic still running → `@reloadscript` |
| Stale Korangar process | Old binary without `0x017F` / panel |

Chat wire format (for packet debugging): client sends

```text
<charname> : @dm mode on
```

as `GlobalMessagePacket` **0x00F3** (`send_chat_message`). Server strips the
name and runs `atcommand->exec` on `@dm mode on`.

---

## Server log breadcrumbs

Map log path (this workspace): `Hercules/log/run-map.out` / `Hercules/log/map.log`

| Log line | Meaning |
|----------|---------|
| `'test' logged in. … Group '99'` | Account is Admin; permission OK |
| `clif_disp_message: Truncated message '[DM] @dm flag …'` | `dispbottom` **is** firing (help lines > ~251 chars) |
| No kick on chat | Name prefix `test : ` matches character name |

Long help lines for `@dm flag` can truncate; that is cosmetic, not the mode bug.

---

## Key files (checklist after rebuild / re-merge)

### Hercules (NPC — no C rebuild if only scripts changed)

- [ ] `npc/custom/dm_campaign/shared/dm_console.txt` — bridge + `@dm_atcmd_*` in `S_*`
- [ ] `npc/scripts_custom.conf` still loads `dm_console.txt` (and friends)
- [ ] `conf/groups.conf` — Admin / DM can use bindatcmd level ≥ 1
- [ ] After edit: in-game **`@reloadscript`**

### Korangar (client — must rebuild binary)

- [ ] `ragnarok-packets`: `DisplayBottomMessagePacket` `0x017F`
- [ ] `korangar-networking` `version_20220406.rs`: register → `ChatMessage`
- [ ] `korangar/src/lib.rs`: `@` local echo on `SendMessage`
- [ ] `interface/windows/commands.rs`: GM panel still sends `@dm mode on`
- [ ] Restart **new** `target/release/korangar` process

### Related campaign docs

- [CAMPAIGN.md](../npc/custom/dm_campaign/CAMPAIGN.md) — session start / mode meaning
- [dm-tooling.md](dm-tooling.md) — full command list
- Client packet note: [korangar/docs/dm-atcommand-feedback.md](../../korangar/docs/dm-atcommand-feedback.md)
- Client storage UI: [korangar/docs/storage-window.md](../../korangar/docs/storage-window.md) (unrelated to `@dm`, same bring-up day)

---

## Minimal regression test (2 minutes)

1. `@reloadscript` (if scripts changed) + restart client (if client changed).
2. `@dm mode` → expect OFF or ON status (not silence).
3. `@dm mode on` → expect **DnD mode enabled**, not “currently OFF”.
4. `@dm mode` again → expect ON + party id.
5. `@dm mode off` → expect disabled.
6. Panel button **DM mode ON** → same as step 3.

If step 3 shows “currently OFF” → Symptom A (script scope).  
If step 3 has no `[DM]` lines but map log truncates help → Symptom B (client `0x017F`).
