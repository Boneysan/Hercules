# Mechanics & Quest Design — Hercules DM System

## What the Engine Already Gives Us

Before designing anything custom, here is what Hercules scripting can do out of the box.
Every mechanic below is built on real script commands found in `doc/script_commands.txt`.

---

## 1. Dialogue & Story Choices

### Basic Dialogue Flow

```c
mes("[Barkeep]");
mes("Strangers don't last long in the Glast Heim sewers.");
next();
mes("^3355FF*He leans in and lowers his voice.*^000000");
next();
mes("[Barkeep]");
mes("You sure you want to go in?");
```

`mes()` — one speech bubble line  
`next()` — player clicks to advance (page break)  
`close()` — ends dialogue  
`^RRGGBB text ^000000` — inline color for narration vs. speech

### Branching Choices

```c
switch (select("I'm ready.", "Tell me more.", "Not today.")) {
    case 1:
        // start quest
        break;
    case 2:
        mes("[Barkeep]");
        mes("They say the sewer boss has a grudge...");
        close();
        break;
    case 3:
        close();
        break;
}
```

`select()` returns 1-based index of what the player clicked.  
Nest `switch/select` for multi-level dialogue trees.

### NPC Ambient Talk (No Click Required)

```c
npctalk("The tavern is quiet tonight...");
npctalk("Watch your backs in there.", "Gruff Guard");
```

`npctalk()` makes text appear as a chat bubble above the NPC head — good for
ambient flavour, DM narration, or encounter commentary without blocking the player.

### Dynamic Narration — Inserting Player / Party Names

```c
.@name$ = strcharinfo(PC_NAME);
.@party$ = getpartyname(getcharid(CHAR_ID_PARTY));
mes("^3355FF" + .@party$ + " — your legend begins here.^000000");
mes("[Oracle]");
mes("And you, " + .@name$ + ", will be the deciding factor.");
```

---

## 2. Quest & State Tracking

### Quest States (Player-Persistent)

```
0 = not started
1 = active / in progress
2 = complete
```

```c
// Start
setquest(10001);

// Check
if (questprogress(10001) == 1) { /* in progress */ }
if (questprogress(10001) == 2) { /* done */ }

// Complete
completequest(10001);

// Advance to next stage (removes old, adds new)
changequest(10001, 10002);

// Kill-count tracking — built in
if (questprogress(10005, HUNTING) == 2) {
    mes("You've slain all the targets.");
    completequest(10005);
}
```

Define quests in `db/re/quest_db.conf`:
```
10001: { Name: "The Tavern Job" }
10002: { Name: "Into the Sewers"  TimeLimit: 0
         Targets: [{ MobId: SEWER_RAT  Count: 10 }] }
```

### Story Flags (Simpler Than Quests)

For DM-driven events that don't need a quest log entry, use character
or account variables directly:

```c
// Set a flag on the character
dm_ch01_met_barkeep = 1;

// Read it anywhere in any script
if (dm_ch01_met_barkeep == 1) { ... }
```

Variable scopes:
| Prefix  | Scope              | Persists after logout? |
|---------|--------------------|------------------------|
| (none)  | Character          | Yes — stored in DB     |
| `@`     | Session            | No                     |
| `#`     | Account            | Yes                    |
| `$`     | Global (all chars) | Yes (RAM, saved)       |
| `.`     | NPC object         | While server runs      |
| `.@`    | Script local       | This execution only    |

Use **character vars** for per-player story flags.  
Use **global `$` vars** for DM world-state ("chapter 2 has started").

---

## 3. Party & Group Mechanics

### Check Party Size

```c
if (!instance_check_party(getcharid(CHAR_ID_PARTY), 2, 1, 6)) {
    mes("You need a party of 2-6 to enter.");
    close();
}
```

### Get All Party Members

```c
.@party_id = getcharid(CHAR_ID_PARTY);
.@count = getpartymember(.@party_id, PT_MEMBER_NAME, .@names$);
for (.@i = 0; .@i < .@count; .@i++) {
    announce("Welcome, " + .@names$[.@i] + "!", bc_map);
}
```

### Warp Whole Party Into Dungeon

```c
// Warp every party member to instance entry point
.@party_id = getcharid(CHAR_ID_PARTY);
// getpartymember returns the member count; collect BOTH char and account ids
getpartymember(.@party_id, PT_MEMBER_CHARID, .@charids);
.@count = getpartymember(.@party_id, PT_MEMBER_ACCID, .@accids);
for (.@i = 0; .@i < .@count; .@i++) {
    // isloggedin(<account id>{, <char id>}); warpchar("<map>", x, y, <char id>)
    if (isloggedin(.@accids[.@i], .@charids[.@i]))
        warpchar("dm_dungeon01", 50, 50, .@charids[.@i]);
}
```

---

## 4. Dungeon Instances (Private Copies Per Party)

Instances give each party their own copy of a map — essential for DM sessions
so groups don't interfere with each other.

```c
// Party leader clicks the entrance NPC
.@party_id = getcharid(CHAR_ID_PARTY);
.@instance_id = instance_create("DM Dungeon Chapter 1", .@party_id);

if (.@instance_id < 0) {
    // -1 invalid type, -2 invalid party id, -4 already exists, <0 queue error
    mes("Instance failed to create. Try again.");
    close();
}

// Required setup BEFORE entering: attach the source map, then initialize.
// (instance_init copies all NPCs from the source map into the instanced copy.)
instance_attachmap("dm_dungeon01", .@instance_id, true, "dm_dungeon01");
instance_init(.@instance_id);

// Warp the whole party into the instance.
// NOTE: there is no instance_enter() command — use instance_warpall().
.@map$ = instance_mapname("dm_dungeon01", .@instance_id);
instance_warpall(.@map$, 50, 50, .@instance_id);
```

Inside the instance, get the instanced map name for spawning:
```c
.@map$ = instance_mapname("dm_dungeon01", .@instance_id);
monster(.@map$, 120, 80, "Sewer Rat", SEWER_RAT, 5, "NPCNAME::OnRatKilled");
```

Announce to instance only:
```c
instance_announce(.@instance_id,
    "^3355FF[DM] The sewer boss has been awakened...^000000", bc_all);
```

---

## 5. Live DM — Spawning Encounters On the Fly

### The Core DM Command Pattern

The DM (GM account) uses custom `@` Atcommands or triggers hidden NPCs.
The most powerful pattern is a **hidden DM console NPC** the GM clicks during play.

```c
// Hidden NPC — only visible to GMs
// prontera,150,150,0  script  DM_Console  HIDDEN_NPC,{
//   (this NPC is invisible; only triggered via donpcevent or @atcommand)

OnDMSpawnWave1:
    .@map$ = instance_mapname("dm_dungeon01");
    areamonster(.@map$, 100, 80, 140, 120, "Cultist", DARK_PRIEST, 4,
        "DM_Console::OnCultistKilled");
    instance_announce(.@party_instance,
        "^CC0000[DM] Shadows gather at the altar...^000000", bc_all);
    end;

OnCultistKilled:
    .@kills++;
    if (.@kills >= 4) {
        instance_announce(.@party_instance,
            "^00CC00[DM] The cultists fall silent.^000000", bc_all);
        callsub(S_SpawnBoss);
    }
    end;

S_SpawnBoss:
    .@map$ = instance_mapname("dm_dungeon01");
    .@boss_gid = monster(.@map$, 120, 100, "The Hollow King", BAPHOMET, 1,
        "DM_Console::OnBossKilled");
    instance_announce(.@party_instance,
        "^FF6600[DM] The ground trembles. Something ancient stirs.^000000", bc_all);
    return;
```

### Dynamic Difficulty — Adapt to Party Size

```c
// getpartymember returns the member count directly — there is no
// getpartymemberinfo() command. Any PT_MEMBER_* type works for counting.
.@count = getpartymember(.@party_id, PT_MEMBER_CHARID, .@charids);
.@mob_count = 2 + (.@count * 2); // scale mobs per player
areamonster(.@map$, 100, 80, 160, 140, "Shadow", DARK_ILLUSION, .@mob_count,
    "DM_Console::OnShadowKilled");
```

### Timed Events — Pressure & Pacing

```c
// Start a countdown when party enters
OnInstanceStart:
    addtimer(300000, strnpcinfo(NPC_NAME_UNIQUE) + "::OnTimeWarning"); // 5 min
    addtimer(600000, strnpcinfo(NPC_NAME_UNIQUE) + "::OnTimeExpire");  // 10 min
    end;

OnTimeWarning:
    instance_announce(.@instance_id,
        "^FFAA00[DM] Only 5 minutes remain before the ritual completes!^000000", bc_all);
    end;

OnTimeExpire:
    // Spawn a consequence — boss empowered, flood room, etc.
    callsub(S_SpawnEmpoweredBoss);
    end;
```

---

## 6. NPC as Storyteller — Hidden DM Presence

### Invisible Narrator NPC

```c
prontera,155,190,0  script  The_Narrator  HIDDEN_NPC,{
    end;

OnNarrate:
    // Triggered by GM via donpcevent
    npctalk(getarg(0), "The Narrator");
    end;
}
```

GM triggers from another NPC or Atcommand:
```c
donpcevent("The_Narrator::OnNarrate");
```

### Moving NPC (Quest Guide / Herald Walking Through Town)

```c
npcspeed(150);
npcwalkto(160, 190);
// ... after player follows ...
npcwalkto(155, 200);
```

### Swap NPC Appearance Live

```c
// Reveal the "old man" as the Demon King
setnpcdisplay("The_Barkeep", "Demon King", BAPHOMET_SMALL, 1);
npctalk("Fools. Did you really think a barkeep would know so much?");
```

---

## 7. Reward Distribution

### Give Loot to Whole Party

```c
// getitem2's optional last arg is an ACCOUNT id (not a char id), so collect
// PT_MEMBER_ACCID. Signature: getitem2(id, amount, identify, refine, attribute,
//                                      card1, card2, card3, card4{, account id})
// Note the FOUR card slots (0,0,0,0) before the account id.
.@count = getpartymember(.@party_id, PT_MEMBER_ACCID, .@accids);
for (.@i = 0; .@i < .@count; .@i++) {
    if (isloggedin(.@accids[.@i])) {
        getitem2(SHADOW_RELIC, 1, 1, 0, 0, 0, 0, 0, 0, .@accids[.@i]); // targeted give
    }
}
announce("The party has claimed the Shadow Relic.", bc_map);
```

### Custom Campaign Items

Define in `db/re/item_db.conf`:
```
Id: 50001
Name: "DM_ShadowKey"
AegisName: "Shadow_Key"
Type: IT_ETC
Weight: 10
Flags: { DropAnnounce: true }
Script: <"
    if (dm_ch02_locked == 0) {
        mes("A heavy iron key. It smells of old stone.");
    }
">
```

---

## 8. Mechanics That Map Well to D&D Concepts

| D&D Mechanic         | Hercules Implementation                                          |
|----------------------|------------------------------------------------------------------|
| Skill check          | `rand(1,20)` compared to threshold; can factor char stats       |
| Perception check     | `getcharid` → look up party scout's `AGI` or custom var         |
| Choice consequences  | Character vars carry forward across sessions/maps               |
| Initiative / turn order | Timer-based wave spawning simulates pacing                   |
| Trap room            | `OnTouch:` label on a coordinate tile area                      |
| Locked door          | `disablenpc()` / `enablenpc()` on a warp NPC                    |
| Secret passage       | Hidden warp, revealed by `enablenpc()` after condition met      |
| NPC ally / escort    | Spawn friendly mob with `unitwalk()` guidance                   |
| Boss phase 2         | `OnBossKilled:` triggers `monster()` with tougher mob           |
| Lore item / scroll   | Item with Script block containing `mes()` dialogue              |
| Death consequence    | `OnPCDieEvent:` — track deaths, trigger DM narration            |
| Rest / safe room     | Map with heal NPC and respawn point between encounters          |

---

## 9. Quest Script Architecture — Recommended Pattern

### File Layout

```
npc/custom/dm_campaign/
├─ campaign_01_tavern.txt      # Chapter 1: Prontera tavern intro
├─ campaign_02_sewers.txt      # Chapter 2: sewer dungeon
├─ campaign_03_boss.txt        # Chapter 3: boss encounter
├─ dm_console.txt              # Hidden GM control NPC
├─ shared_functions.txt        # callsub targets reused across chapters
└─ campaign_items.txt          # Custom quest item scripts
```

### Single Quest Script Template

```c
// npc/custom/dm_campaign/campaign_01_tavern.txt

// ── Entry NPC ─────────────────────────────────────────────────────────────
prontera,155,190,5  script  Old_Barkeep  4_M_TAVERN01,{
    if (questprogress(DM_CH01_QUEST) == 2) {
        mes("[Barkeep]");
        mes("You already know what you need to know. Safe travels.");
        close();
    }
    if (questprogress(DM_CH01_QUEST) == 1) {
        callsub(S_InProgress);
    }
    callsub(S_Intro);
    end;

S_Intro:
    mes("[Old Barkeep]");
    mes("You look like trouble.");
    next();
    switch (select("Trouble finds me.", "I'm just passing through.", "...")) {
        case 1: callsub(S_Accept); break;
        case 2:
            mes("[Barkeep]");
            mes("They all say that.");
            close();
            break;
        case 3:
            npctalk("Hmph.", "Old_Barkeep");
            close();
            break;
    }
    return;

S_Accept:
    mes("[Barkeep]");
    mes("Good. I have a job.");
    next();
    mes("^3355FF[DM] Quest started: The Tavern Job.^000000");
    setquest(DM_CH01_QUEST);
    dm_ch01_hero_type = 1; // remember player chose assertive path
    close();

S_InProgress:
    mes("[Barkeep]");
    mes("The sewers. You know where they are.");
    close();
}

// ── Quest Complete Trigger ─────────────────────────────────────────────────
-  script  DM_CH01_Watcher  FAKE_NPC,{
    end;

OnPCKillEvent:
    if (questprogress(DM_CH01_QUEST, HUNTING) == 2) {
        donpcevent("Old_Barkeep::OnQuestComplete");
    }
    end;
}

// ── Completion callback on the barkeep ────────────────────────────────────
// (added as extra label in Old_Barkeep block — shown separately for clarity)
// OnQuestComplete:
//     npctalk("Well done. Return to me.", "Old_Barkeep");
//     end;
```

---

## 10. Key Gotchas & Design Notes

**Variable persistence after relog**  
Character vars (no prefix) persist in the database. Use these for story flags.
Session vars (`@`) reset on logout — don't store quest state in them.

**Instance limits**  
One instance per owner (party) of the same template at a time.
Destroy it with `instance_destroy()` when the session ends or the party wipes.

**`select()` max options**  
`select()` supports up to 128 options but the client only displays ~5–8 cleanly.
Keep choices to 3–4 for readability.

**`donpcevent()` targeting**  
To trigger an NPC event from a GM Atcommand or another NPC, use the full
`"NPCName::OnLabel"` format. The NPC must be loaded and not disabled.

**Kill-count quests need `quest_db` entries**  
`questprogress(ID, HUNTING)` only works if the quest has `Targets` defined in
`db/re/quest_db.conf`. Plan quest IDs early — pick a range like 20000–20999
for all DM campaign quests to avoid conflicts with official quests.

**NPC dialogue blocks the client**  
While a player is reading `mes()` dialogue, they cannot move or act.
Use `npctalk()` for ambient narration that doesn't block them.

**Map flags for dungeon feel**  
In `npc/mapflag/` or inline: `nomemo`, `noreturn`, `nosave`, `nowarpto`
prevent escape/save-abusing. Consider `noteleport` for boss rooms.

---

## Next Steps

1. Design the quest ID range and register quests in `quest_db.conf`
2. Build a minimal Chapter 1 tavern script end-to-end
3. Create the DM Console NPC with 3–4 encounter triggers
4. Build one instanced dungeon map (can reuse an existing map at first)
5. Test the full loop: tavern → instance enter → DM spawns wave → reward
