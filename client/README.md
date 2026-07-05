# Seal Cascade - Client Setup Guide

This directory contains notes for preparing the player/DM client for the Seal Cascade campaign on Hercules.

## 1. Quest Journal (Required for @dm warps and campaign text)

The campaign uses custom quest IDs 20000–20234.

**Steps:**
1. Make a full backup of your RO client.
2. Locate `System/OngoingQuestInfoList_True_EN.lub` (or your language equivalent).
3. Decompile the .lub to .lua (common tools: unluac, lub decompilers, or online RO tools).
4. Use the merge helper from the server repo:

   ```bash
   # From the Hercules_RO root
   python3 tools/campaign_quest_merge.py --patch /path/to/decompiled_OngoingQuestInfoList_True_EN.lua
   ```

   Or manually copy blocks from `planning/SealCascade_QuestList_addon.lua`.

5. Recompile the .lua back to .lub.
6. Test: Log in (with DM mode or a character that has the quests) and open the Quest window. You should see entries like "Omens at the Fountain", "The Choice He Never Had", etc., with Location, Hunt, Return lines containing `@dm warp` commands.

The journal entries were written to work with the DM's `@dm` commands for easy navigation.

## 2. BGM and Scene Assets (for @dm scene and @dm cutscene)

See `planning/campaign_client_assets.md` in the repo root.

Required (place in your client):

- **BGM/** folder:
  - dm_dread.mp3, dm_boss.mp3, dm_calm.mp3, dm_holy.mp3, dm_ruin.mp3, dm_snow.mp3, dm_fest.mp3
  - (You can start with renamed copies of existing RO bgm and rename as needed for testing.)

- **data/texture/유저인터페이스/illust/** (or equivalent):
  - Custom cutin portraits (.bmp with magenta transparency) referenced by the DM in scenes.

Without these, scene commands will still change weather/effects but BGM and portraits will be missing or silent.

## 3. LAN / Multi-PC Setup (friends connecting to your host)

> ⚠️ **Read this whole section before touching anything.** The obvious step —
> editing `data/clientinfo.xml` — does **NOT** work with this client. See the GRF
> gotcha below. It is the single biggest time-sink in getting a friend connected.

### 3.1 Server config (host machine)

The client is handed three server addresses in sequence: **login** (from the
client's clientinfo) → **char** (`char_ip`) → **map** (`map_ip`). Two of the IPs are
"advertised to clients" and one set is "server-to-server". Set them like this:

| File | Field | Value | Meaning |
|------|-------|-------|---------|
| `conf/char/char-server.conf` | `char_ip`  | **LAN IP** (e.g. `192.168.20.60`) | advertised to clients |
| `conf/map/map-server.conf`   | `map_ip`   | **LAN IP** | advertised to clients |
| `conf/char/char-server.conf` | `login_ip` | **`127.0.0.1`** | char→login, same box |
| `conf/map/map-server.conf`   | `char_ip`  | **`127.0.0.1`** | map→char, same box |

Keep the inter-server pair on `127.0.0.1` — all three servers share the WSL box, so
there is no reason to bounce those out to the LAN. `tools/set-lan-ip.sh lan [IP]`
sets `char_ip`/`map_ip` for you (but see 3.3 — its clientinfo edit is not enough).

### 3.2 WSL2 port forwarding (host machine)

Under WSL2's default NAT networking, WSL has its own internal IP (`172.31.x.x`) that
**changes on every restart** and that friends cannot reach. The Windows host must
forward its LAN IP into WSL. Run **`setup-wsl-portforward.ps1`** (in an Administrator
PowerShell) — it auto-detects the current WSL IP and adds `netsh portproxy` rules +
a firewall rule for all three ports. **Re-run it after any WSL restart.**

Cleaner permanent alternative (Windows 11 22H2+): add to `%UserProfile%\.wslconfig`
```ini
[wsl2]
networkingMode=mirrored
```
then `wsl --shutdown`. With mirrored mode you skip portproxy entirely.

Ports to open / forward: **login 6900, char 6121, map 5121** (TCP). If the host runs
a third-party firewall (e.g. **Bitdefender**), open the ports **there too** — its
rules are separate from Windows Firewall.

### 3.3 ⚠️ The GRF clientinfo gotcha (the important part)

**This client reads `data\clientinfo.xml` from INSIDE the GRF archives, not from the
loose `data/clientinfo.xml` file.** (The "Read Data Folder First" client patch is not
applied, so GRFs win.) Editing the loose file changes nothing.

Worse, GRF precedence follows **`DATA.INI` order, and the LOWER index wins**, and more
than one GRF can carry its own embedded clientinfo. In this client:

```
1=renewal2021.grf   <- has an embedded data\clientinfo.xml — THIS one wins
2=resources2021.grf
3=data.grf          <- also has one (loses to #1)
4=rdata.grf
```

If any winning GRF still says `127.0.0.1`, a **remote** player's client dials
`127.0.0.1` = *their own PC*, and shows **"failed to connect to server"** — even
though ping/`Test-NetConnection` to the host succeeds and the firewall is off (those
test the network; the game exe is quietly dialing the wrong address). The host itself
works regardless, because on the host `127.0.0.1` reaches its own WSL server — which
is why this bug looks like "works for me, not for them."

**Fix it with the repo tool** (patches the address *inside* every GRF that has an
embedded clientinfo, in place, with a verified reversible backup):

```bash
# inspect what each GRF currently advertises
python3 tools/patch-grf-clientinfo.py --show

# set the address in ALL embedded clientinfos (and the loose file, for good measure)
python3 tools/patch-grf-clientinfo.py 192.168.20.60

# back to single-PC play
python3 tools/patch-grf-clientinfo.py 127.0.0.1
```

Then **fully relaunch** the client (GRFs load only at startup). To onboard a friend
you can hand them just the patched **`renewal2021.grf`** (~7 MB, the winning GRF) to
drop into their client, or the whole client folder / zip.

### 3.4 Diagnosing "friend can't connect"

- **`netstat -ano | findstr 6900`** on the *friend's* PC while it's connecting shows
  the real Foreign Address — if it's `127.0.0.1`, it's the GRF gotcha (3.3), not the
  network.
- On the host, watch `log/run-login.out` for `Request for connection of <user>`. Note
  the portproxy NATs every client to the WSL gateway (`172.31.208.1`), so the source
  IP can't tell host from friend — use the **account name** instead. Check
  `SELECT userid,lastlogin,last_ip,logincount FROM login;` — a friend's account with
  `logincount 0` never reached the server.
- Login flow is 3 hops (login→char→map). `char_ip`/`map_ip` come from the *server*
  config; only the **login** address comes from the client's (GRF) clientinfo.

To reset everything to single-PC play: `tools/set-lan-ip.sh local` **and**
`python3 tools/patch-grf-clientinfo.py 127.0.0.1`.

## 4. Other Client Recommendations

- Make sure your client supports the quest IDs (most modern kRO / iRO clients do; 20000+ range is safe).
- Use a client with good support for questinfo markers (yellow arrows on minimap for hunts).
- For full experience, the GM/DM account should be promoted to group 5 (see `tools/promote-dm.sh` on server).
- Test `@roll`, `@dm status`, `@dm warp`, and `@dmbeat` after connecting.

## 5. Cash Shop (DM rewards)

The DM can grant Cash Shop currency to the whole party with `@dm points <amount>` (Kafra Points, spent first) or `@dm points <amount> cash` (Cash Points, used only as backup when Kafra Points run short).

**Important client quirk:** the in-game Cash Shop window has a "Use Free Points" box that does **not** auto-fill. You must click into it and manually type the item's price (or however much of your Kafra Points balance you want to spend) before clicking Buy — otherwise it sends 0 and you'll get a "You do not have enough Kafra Credit Points" error even with plenty of points. Cash Points cover whatever the Free Points box doesn't.

## 6. Quick Test After Merge

1. Connect with a test character in a party.
2. Have the DM run:
   ```
   @dmmode on
   @dm quest start 20001
   @dm warp prontera 156 191
   ```
3. Open Quest window (Alt+U or equivalent) — you should see "Omens at the Fountain" with nice flavor and warp instructions.

## Troubleshooting

- Quests not appearing? Wrong .lub used, or not recompiled, or wrong language file (try _True_EN or your locale).
- No @dm commands? You must be in the active DM party + group level high enough.
- Warps not working? Make sure you are in the correct DM session and the maps exist on the server.
- Cash Shop says you don't have enough Kafra Credit Points? Type the price into the "Use Free Points" box first — see section 5.

See `planning/dm-handoff.md` and `planning/dm-tooling.md` in the server repo for full command reference.
