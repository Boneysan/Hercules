# Campaign NPC Sprite Availability (Korangar client)

Fixed 2026-07-11. Use this when a campaign NPC renders as a **silhouette with an
exclamation point** in Korangar.

## Runbook: fix a newly-reported silhouette NPC

Given just the **NPC name + map** the user saw:

1. **Find the NPC definition + its sprite constant.**
   ```bash
   grep -rn "<NPC name>" Hercules/npc/custom/dm_campaign/
   ```
   The header line is `map,x,y,dir<TAB>script<TAB><name><TAB><SPRITE_CONSTANT>,{`.

2. **Get the numeric sprite ID.**
   ```bash
   grep -niE "^\s*<SPRITE_CONSTANT>:" Hercules/db/constants.conf
   ```

3. **Probe whether that sprite is in the client GRF** (both `.spr` and `.act`).
   Use the Python GRF probe in the "Probe" section below with
   `<sprite_constant_lowercased>.spr` / `.act`.
   - **Present** → the missing-sprite is a *different* problem (e.g. the client's
     `npcidentity.lub` maps the ID to another name). Note it and inspect the
     running client; this offline probe can't see that mapping.
   - **Missing** → continue.

4. **Pick a present, thematically-similar replacement.** List candidates by
   keyword against the GRF npc sprite set (see the search snippet used for
   Sun-Hwa: `4_f_thaishaman` for a shaman, `1_f_orient_0x` for oriental females,
   etc.). Confirm the replacement's `.spr` **and** `.act` are present.

5. **Edit the constant** in the NPC's `.txt`, then validate + reload:
   ```bash
   ./script-checker npc/custom/dm_campaign/.../<file>.txt   # expect EXIT=0
   # in-game:
   @reloadscript
   ```
   No client rebuild is needed — the client loads the new sprite on next sight.

6. **Log the swap** in the "Fix applied" section below and mark it verified once
   the user confirms in-game.

## What that placeholder means

The silhouette+"!" is Korangar's missing-sprite fallback,
`FALLBACK_SPRITE_FILE = "npc\\missing.spr"` (`korangar/src/loaders/mod.rs`). The
NPC's sprite could not be loaded.

## How the client resolves an NPC sprite

1. The server (Hercules) sends the NPC's **view / sprite ID** — a number the
   sprite constant maps to in `db/constants.conf` (e.g. `4_F_SHAMAN` = 720).
2. Korangar maps that `JobId` → a sprite folder name via
   `npcidentity.lub` / `jobidentity.lub`
   (`korangar/src/world/library/job_identity.rs`). Unmapped IDs default to
   `1_f_maria`.
3. It loads `data\sprite\npc\<name>.spr` (+ `.act`) from the GRF
   (`world/entity/mod.rs`: `format!("npc\\{}", JobIdentity)`). Missing file →
   `missing.spr` fallback.

**Key tell:** a *silhouette* (not the `1_f_maria` default woman) means the ID
**is** in `npcidentity.lub` but the `.spr` file is **absent from the GRF**. If
the ID were simply unmapped, you'd see Maria, not a silhouette.

## The GRF data set here

Client data: `korangar/korangar/data.grf` (3.0 GB, 151062 files) + `rdata.grf`.
Full sets, but **not every** sprite ID's file is present. GRF file tables are
zlib-compressed, so plain `grep` on the `.grf` finds nothing — use the probe
below.

## Probe: is a sprite in the GRF?

```python
python3 - <<'PY'
import struct, zlib, os
GRF="/Volumes/T7/GitHub/Ragnarok_Online/korangar/korangar/data.grf"
def names(path):
    with open(path,'rb') as f:
        h=f.read(46); fo=struct.unpack('<I',h[30:34])[0]; sd=struct.unpack('<I',h[34:38])[0]; fc=struct.unpack('<I',h[38:42])[0]
        rc=fc-sd-7; f.seek(fo+46); cl,ul=struct.unpack('<II',f.read(8)); t=zlib.decompress(f.read(cl))
    out=[];pos=0
    for _ in range(rc):
        e=t.index(b'\x00',pos); out.append(t[pos:e].decode('latin-1')); pos=e+1+17
    return out
npc=set(os.path.basename(n).lower() for n in names(GRF) if n.lower().startswith('data\\sprite\\npc\\'))
for probe in ['4_f_shaman.spr','4_f_thaishaman.spr']:
    print(probe, "PRESENT" if probe in npc else "MISSING")
PY
```

A full programmatic audit of **every** `dm_campaign` NPC definition (28 distinct
sprite constants, `script` + `duplicate` lines, all acts/arcs) on 2026-07-11
found **only one** missing file: `4_f_shaman.spr`. Every other constant has both
`.spr` **and** `.act` present in `data.grf` (`4_f_01..05`, `4_m_01..06`,
`4_f_sister`, `4_m_monk`, `4_m_science`, `4_m_orient02`, `4_energy_*`,
`4_m_cru_head`, `4_m_job_wizard`, `4_m_nfdeadman`, `1_m_pastor`, `1_m_siz`,
`4_board3`, `4_treasure_box`, …).

**Proxy caveat.** The audit assumes `npcidentity.lub` maps an ID to a sprite
named after its constant (verified true for `4_F_SHAMAN`→`4_F_SHAMAN`). If a
specific ID instead maps to a *different* name whose file is absent, that NPC
would still be a silhouette and this audit would miss it. `npcidentity.lub` is
compiled Lua bytecode, so that mapping can only be confirmed against the running
client. Definitive check = look at each arc hub NPC in-game after
`@reloadscript`. Report any remaining silhouette by NPC name + map.

## Fix log

Append each sprite swap here (newest first). Mark verified once confirmed in-game.

| Date | NPC (map) | Old constant (id) | New constant (id) | File | Status |
|------|-----------|-------------------|-------------------|------|--------|
| 2026-07-11 | Five Prontera WoE castle flags | `GUILD_FLAG` (722, mapped asset missing) | Client compatibility mapping to `1_flag_eagle` (present) | `korangar/src/world/library/job_identity.rs` | Awaiting live verification |
| 2026-07-11 | Sun-Hwa#dm (Payon) | `4_F_SHAMAN` (720, `.spr` missing) | `4_F_THAISHAMAN` (840, present) | `act_01/arc_02_payon.txt` | ✅ live-verified |

## Rule for new campaign NPCs

Before assigning a sprite constant, probe that its `.spr` exists in `data.grf`.
If missing, pick a present alternative (or the reward would be a silhouette). The
safe, verified-present humanoid sprites are the ones listed above.
