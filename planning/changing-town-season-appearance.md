# Changing a Town's Seasonal Appearance (e.g. Christmas Prontera → Normal)

## TL;DR

The seasonal look of a town (Christmas Prontera, Halloween, Sakura/spring, etc.) is
**100% client-side** — it is baked into the client's map files, not controlled by the
server. There is **no server "time of year" / season setting** in Ragnarok that decorates
towns, so changing server time does nothing. To change the look you swap the town's map
files on the client.

The clean, non-destructive way is to drop replacement map files into the client's loose
`data\` folder, which the client reads **before** the GRF archives — so you never have to
edit a GRF.

---

## Why our Prontera is Christmas

Our base client (`04_kRO`) ships a `data.grf` that was packed **Dec 23, 2021** — Christmas
Eve. At that moment kRO's live Prontera was its winter/Christmas version, so the decorated
map (trees, lights, snow) got baked into the GRF. The client simply renders whatever map
files it loads.

---

## How the client picks map files (load order)

Our client is configured so loose files win over archived ones:

- `clientinfo.xml` contains `<readfolder/>` → the client reads the loose `data\` folder.
- The patched exe has "Read Data Folder First" applied.
- `data.ini` lists the GRF priority:
  ```
  [Data]
  1=renewal2021.grf
  2=resources2021.grf
  3=data.grf
  4=rdata.grf
  ```

Effective priority when the client looks for `data\prontera.rsw`:

```
loose  data\  folder   (highest priority — wins)
  └─ renewal2021.grf
       └─ resources2021.grf
            └─ data.grf        ← the Christmas prontera lives here
                 └─ rdata.grf  (lowest)
```

So putting a **normal** `prontera.rsw` in `H:\RO\client\data\` overrides the Christmas one
inside `data.grf` — no GRF editing required.

---

## What files make up a map

A Ragnarok map is three core files (all under the internal `data\` path):

| File           | Controls                                                        |
|----------------|----------------------------------------------------------------|
| `prontera.rsw` | **World / object placement** — which props, trees, lights, NPCs-as-models, water, lighting. *This is the file that removes the Christmas decorations.* |
| `prontera.gnd` | Ground mesh / terrain textures.                                |
| `prontera.gat` | Walkability / collision (which tiles you can stand on).        |

For switching *from* a seasonal version *to* the normal one you usually only need these
three. The models (`.rsm`) and textures the normal `.rsw` references already exist inside
`data.grf`, so they don't need copying.

---

## Step-by-step: revert Prontera to normal

### 1. Get the standard (non-seasonal) Prontera files
You need normal-season `prontera.rsw`, `prontera.gnd`, `prontera.gat`. Sources:

- A **kRO `data.grf` from a non-December date** (extract the three files from it).
- A community **kRO data pack / map collection** (most private-server data repos ship the
  standard maps).
- Extract from any other RO install whose Prontera is the normal version.

Use **GRF Editor** (Windows tool) to open a GRF, search `prontera`, and extract the files.

### 2. Drop them into the loose data folder
Place the files here, preserving the `data\` subfolder:

```
H:\RO\client\data\prontera.rsw
H:\RO\client\data\prontera.gnd
H:\RO\client\data\prontera.gat
```

(Create the `data\` folder if it isn't already there. It is read first, so these win.)

### 3. Remove leftover snow weather (if any)
The falling-snow *weather effect* may be separate from the map. In-game as a GM, run:

```
@clearweather
```

If snow stops, it was a weather effect. If it persists, it's baked into the `.rsw` and the
file swap in step 2 handles it.

### 4. Restart the client
Close and relaunch `2019-06-05fRagexe_patched.exe`. Walk into Prontera — it should now load
the normal version.

---

## Notes & gotchas

- **Non-destructive:** the `data\` folder method never touches `data.grf`, so you can undo by
  simply deleting the three loose files.
- **Internal path must match:** files must sit under `client\data\` (mirroring the GRF's
  internal `data\` path), or the client won't find them.
- **Map name vs. display:** the filename `prontera` is the map's internal ID; the in-game
  display name is unrelated and set elsewhere.
- **Same trick, any town/season:** to *force* a season (e.g. always-Halloween Geffen) you do
  the reverse — drop the seasonal `.rsw` into `data\`.
- **Server stays out of it:** none of this requires touching the Hercules server, DB, or a
  restart. It's purely client files.

---

## Quick reference

| Goal                          | Action                                                        |
|-------------------------------|---------------------------------------------------------------|
| Remove snow weather           | `@clearweather` in-game (GM)                                   |
| Revert one town to normal     | Drop normal `<map>.rsw/.gnd/.gat` into `client\data\`          |
| Force a seasonal look         | Drop seasonal `<map>.rsw` into `client\data\`                  |
| Undo a swap                   | Delete the loose files from `client\data\`                    |
| Browse / extract from a GRF   | GRF Editor (Windows)                                           |
