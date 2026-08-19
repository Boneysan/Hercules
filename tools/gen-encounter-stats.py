#!/usr/bin/env python3
"""Generate the encounter stat table from mob_db.conf.

Emits npc/custom/dm_campaign/shared/dm_mobstats.txt, a script lookup of the
combat numbers @dmenc needs to price an encounter. Regenerate after editing
the encounter table or mob_db:

    ./tools/gen-encounter-stats.py            # write
    ./tools/gen-encounter-stats.py --check    # fail if the file is stale

WHY THIS EXISTS RATHER THAN READING korangar/docs/bestiary.json:

That export has a `PhysDPS` field, and it is not DPS. It is (atk1+atk2)/2 --
the mean damage of one hit -- with AttackDelay discarded. Budgeting an
encounter on it ranks monsters by how hard they hit rather than how fast, and
the error is not small:

    Salamander (1831)   exported 1449.5   actual 10353.6/s   (delay  140ms)
    Necromancer (1870)  exported 1182.5   actual   651.2/s   (delay 1816ms)

Those two read as comparable threats in the export. One of them deals sixteen
times the damage of the other. So DPS is computed here from Attack and
AttackDelay directly, against this repo's own mob_db, with no cross-repo
dependency.
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOB_DB = ROOT / "db" / "re" / "mob_db.conf"
ENCOUNTERS = ROOT / "npc" / "custom" / "dm_campaign" / "shared" / "dm_encounters.txt"
OUT = ROOT / "npc" / "custom" / "dm_campaign" / "shared" / "dm_mobstats.txt"

BLOCK = re.compile(r"\n\tId: (\d+)\n(.*?)\n\},\n", re.S)


def field(body, key, default=0):
    m = re.search(r"\n\t%s: (\d+)" % key, body)
    return int(m.group(1)) if m else default


def parse_mob_db():
    text = MOB_DB.read_text(encoding="utf-8", errors="replace")
    mobs = {}
    for blk in BLOCK.finditer(text):
        mob_id, body = int(blk.group(1)), blk.group(2)
        name = re.search(r'\n\tName: "([^"]+)"', body)
        atk = re.search(r"\n\tAttack: \[(\d+), (\d+)\]", body)
        atk1, atk2 = (int(atk.group(1)), int(atk.group(2))) if atk else (0, 0)
        delay = field(body, "AttackDelay", 1000) or 1000
        hp = field(body, "Hp", 1)
        deff = field(body, "Def")

        # Mean hit x attacks per second. This is the number the exported
        # bestiary throws away.
        dps = round((atk1 + atk2) / 2 * 1000.0 / delay)

        # Durability proxy. RO's renewal defence maths is more involved than
        # this; a flat (1 + Def/100) multiplier is deliberately a rough
        # ordering signal, not a damage simulation, and is labelled as such
        # wherever it is shown to a DM.
        ehp = round(hp * (1 + deff / 100.0))

        mobs[mob_id] = {
            "name": name.group(1) if name else "?",
            "lv": field(body, "Lv"),
            "hp": hp,
            "ehp": ehp,
            "dps": dps,
            "def": deff,
            "delay": delay,
            "mvp": 1 if "MvpExp:" in body else 0,
        }
    return mobs


def encounter_mob_ids():
    """Every mob id named in the encounter table."""
    text = ENCOUNTERS.read_text(encoding="utf-8")
    table = text.split("function\tscript\tDM_EncTable\t{")[1].split("\nfunction\t")[0]
    ids = {int(m) for m in re.findall(r'"(\d+)", "', table)}
    ids.discard(0)
    return sorted(ids)


def render(mobs, ids):
    lines = [
        "//===== Seal Cascade Campaign ================================",
        "//= Encounter mob stats — GENERATED, DO NOT EDIT BY HAND",
        "//===== Description: =========================================",
        "//= Regenerate with ./tools/gen-encounter-stats.py after changing",
        "//= the encounter table or mob_db. ./tools/gen-encounter-stats.py",
        "//= --check fails if this file has drifted.",
        "//=",
        "//= DPS is mean hit x attacks per second, computed from Attack and",
        "//= AttackDelay in db/re/mob_db.conf. It is NOT the PhysDPS field",
        "//= in korangar/docs/bestiary.json, which discards AttackDelay and",
        "//= therefore rates a 140ms attacker the same as an 1816ms one.",
        "//=",
        "//= EHP is hp * (1 + Def/100) — a rough durability ordering, not a",
        "//= damage simulation.",
        "//===========================================================",
        "",
        "// DM_MobStat(<mob id>, <field>)",
        "//   0 name  1 level  2 hp  3 ehp  4 dps  5 is_mvp",
        "function\tscript\tDM_MobStat\t{",
        "\t.@id = getarg(0);",
        "\t.@f = getarg(1);",
        "",
    ]
    first = True
    for mob_id in ids:
        m = mobs[mob_id]
        kw = "if" if first else "else if"
        first = False
        lines.append("\t%s (.@id == %d)" % (kw, mob_id))
        lines.append(
            '\t\tsetarray .@s$[0], "%s", "%d", "%d", "%d", "%d", "%d";'
            % (m["name"], m["lv"], m["hp"], m["ehp"], m["dps"], m["mvp"])
        )
    lines += [
        "\telse",
        '\t\treturn "";',
        "",
        "\treturn .@s$[.@f];",
        "}",
        "",
    ]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if the generated file is stale")
    args = ap.parse_args()

    mobs = parse_mob_db()
    ids = encounter_mob_ids()

    missing = [i for i in ids if i not in mobs]
    if missing:
        print("ERROR: encounter table references mobs absent from mob_db: %s" % missing,
              file=sys.stderr)
        return 2

    mvps = [(i, mobs[i]["name"]) for i in ids if mobs[i]["mvp"]]
    if mvps:
        print("WARNING: encounter table uses MVPs: %s" % mvps, file=sys.stderr)
        print("  MVPs belong in @dmbeat boss spawns, not encounter slots.",
              file=sys.stderr)

    text = render(mobs, ids)

    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != text:
            print("STALE: %s does not match mob_db/encounter table." % OUT.name,
                  file=sys.stderr)
            print("  Run ./tools/gen-encounter-stats.py to regenerate.", file=sys.stderr)
            return 1
        print("OK: %s is current (%d mobs)." % (OUT.name, len(ids)))
        return 0

    OUT.write_text(text, encoding="utf-8")
    print("Wrote %s — %d mobs." % (OUT.name, len(ids)))
    for i in ids:
        m = mobs[i]
        print("  %5d %-24s Lv%-4d hp %-8d ehp %-8d dps %-7d%s"
              % (i, m["name"], m["lv"], m["hp"], m["ehp"], m["dps"],
                 "  MVP" if m["mvp"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
