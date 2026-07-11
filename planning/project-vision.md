# Hercules RO — Project Vision & DM Game Night System

## Concept: Live Dungeon Master in Ragnarok Online

RO already has everything a tabletop session needs:

| RO Feature       | D&D Equivalent       |
|------------------|----------------------|
| Classes          | Character archetypes |
| Party gameplay   | Adventuring party    |
| Dungeons         | Dungeon crawls       |
| Loot progression | Treasure / rewards   |
| Social hub towns | Tavern / town hub    |
| GM control       | Dungeon Master       |

### The Session Loop

1. Players gather in **Prontera tavern**
2. GM appears as a **hidden storyteller NPC**
3. Quest is announced and begins
4. Party enters a **custom dungeon instance**
5. GM **spawns encounters and adapts difficulty live**
6. Story resolves, rewards distributed

This maps almost 1:1 to a multiplayer tabletop session.

---

## Why Hercules / RO Over Alternatives

| Path                     | Relative Effort | Notes                              |
|--------------------------|-----------------|------------------------------------|
| Hercules / Ragnarok      | 1×              | Most infrastructure already exists |
| Godot custom game        | 5–10×           | Flexible but build everything      |
| Ryzom modernization      | 50–100×         | Hardest by far                     |

**Goal:** Fun game night with friends → Hercules is the fastest path.

## Modernization Charter

This project is not limited to reproducing the official Ragnarok client. Large
improvements are explicitly in scope when they make the private, DM-led game
night easier to run or more enjoyable to play: modern controls, richer party
UI, campaign journals, GM guidance, encounter telegraphs, accessibility,
spectator tools, and purpose-built client/server features are all valid work.

The safety boundary is architectural rather than nostalgic:

- Hercules remains authoritative for movement, combat, inventory, quests,
  permissions, and persistence.
- Existing RO packets and scripts are preferred until evidence shows that a
  custom packet/plugin is warranted.
- Client and server changes that form one feature are planned and tested as a
  single cross-project slice.
- Core fallbacks remain available where practical, especially click movement
  alongside WASD and manual DM commands alongside graphical tools.
- Large changes require focused acceptance criteria, validation against the
  live `PACKETVER=20220406` stack, and a rollback/configuration path when the
  behavior is disruptive.
- Campaign state must remain party-safe and recoverable through DM tooling.

The official client is a content/protocol reference, not the product ceiling.

### UI contract for server-backed features

When Hercules exposes a feature to Korangar, the server contract must allow a
good interface rather than forcing chat scraping or ambiguous optimistic state:

- permission and final state remain authoritative on Hercules;
- success and rejection responses are explicit and actionable;
- preview/read operations are distinct from mutations;
- destructive DM/campaign actions expose their consequences before commit;
- party-visible and GM-private data are deliberately separated;
- reconnect/map-change recovery can reconstruct current state;
- high-frequency updates are bounded and do not require UI spam.

Use existing packets and structured script feedback first. Add custom packets
only when a tested UI slice demonstrates that the existing transport cannot
represent the required state safely.

### Visual-improvement contract

Modern Korangar graphics are presentation improvements, not alternate game
rules. Hercules supplies authoritative positions, facing, combat/effect events,
weather/campaign intent, and permissions; the client may interpolate and enrich
their presentation without inventing mechanical outcomes.

- Telegraph geometry must reflect server-owned hazard areas and timing.
- Smoother movement/animation must converge on authoritative coordinates.
- Weather, lighting, camera, and particles cannot conceal required information;
  reduced-effects modes remain mechanically complete.
- Visual scene commands are optional enhancements and must not block official or
  other compatible clients from completing campaign content.
- Server-driven visual state must be inspectable and recoverable after map
  changes, reconnects, instance cleanup, and DnD mode shutdown.

---

## Development Environment

### Target Stack

```
Windows 11 Host
├─ RO client(s)
├─ Sprite / GRF tools (e.g. GRF Editor, NEMO patcher)
└─ WSL Ubuntu 22.04 / 24.04
   ├─ Hercules login-server
   ├─ Hercules char-server
   ├─ Hercules map-server
   └─ MariaDB
```

### Why WSL

- Build and run Hercules in Linux without a VM
- Windows RO client connects to `127.0.0.1` or WSL IP (`hostname -I`)
- Keep repo inside Linux filesystem (`~/src/`), not `/mnt/c` or `/mnt/d`

### Resource Estimate (Windows 11 host)

| Component        | Typical RAM |
|------------------|-------------|
| Hercules servers | 200–800 MB  |
| MariaDB          | 300 MB–2 GB |
| **Total**        | ~1–4 GB     |

Fine for a 64 GB machine. Good for 1–50 concurrent players locally.

---

## Repo & Build Workflow

### Setup

```bash
mkdir -p ~/src
cd ~/src
git clone https://github.com/Boneysan/Hercules.git
cd Hercules

# point to upstream for merges
git remote rename origin upstream
git remote add origin https://github.com/Boneysan/Hercules.git
```

### Dependencies (Ubuntu)

```bash
sudo apt update
sudo apt install -y git make gcc g++ libmysqlclient-dev zlib1g-dev libpcre3-dev
```

### Build

```bash
./configure
make clean
make server
```

### Run

```bash
./login-server &
./char-server &
./map-server &
```

### Branch Strategy

| Branch             | Purpose                              |
|--------------------|--------------------------------------|
| `main`             | Stable, working server               |
| `dm-event-system`  | Live DM tools / GM commands          |
| `custom-quests`    | Campaign scripts, NPC dialogue       |
| `sprite-tests`     | Asset and client experiments         |

---

## Work Areas

```
Hercules/
├─ src/        # C source: new GM/DM Atcommands, event hooks
├─ npc/        # Herc script: quest NPCs, tavern scene, dungeon events
├─ conf/       # GM group permissions, command access levels
├─ db/         # Custom mobs, items, maps for DM encounters
├─ plugins/    # Optional: DM API plugin (WebSocket / REST control panel)
└─ planning/   # Design docs (this folder)
```

---

## Planned Features (DM Tooling)

### Phase 1 — Foundation
- [ ] Server builds and runs cleanly in WSL
- [ ] MariaDB configured, SQL scripts imported
- [ ] Windows RO client connects to local server
- [ ] GM account created and tested

### Phase 2 — DM Core
- [ ] Custom `@dm` Atcommand namespace for live control
- [ ] `@dm spawn <mob> <count>` — spawn encounter on the fly
- [ ] `@dm warp <map> <party>` — move party to dungeon instance
- [ ] `@dm story <message>` — broadcast flavour text as NPC voice
- [ ] `@dm reward <item> <player>` — hand out loot live

### Phase 3 — Game Night Loop
- [ ] Prontera tavern NPC as quest board / lobby
- [ ] Custom dungeon map(s) with layered mob placements
- [ ] GM hidden mode (invisible, invincible, spectator)
- [ ] Session log (who did what, what dropped)

### Phase 4 — Polish (optional)
- [ ] Web-based DM control panel (Node/Python → Hercules plugin API)
- [ ] Discord bot integration for session announcements
- [ ] Persistent campaign state (flags/variables per party)

---

## Notes

- Networking: for LAN game nights, players connect to the WSL IP. For internet play, configure Windows Firewall + router port forwarding for RO ports (login/char/map, typically 6900/6121/5121).
- If the project grows beyond ~50 concurrent players, migrate to a native Ubuntu server or VM.
- Client patching: use NEMO patcher to point the RO client at `127.0.0.1` and disable most modern protections for private server use.
