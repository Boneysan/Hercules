#!/usr/bin/env python3
"""
verify_boss_levels.py

Cross-checks Seal Cascade campaign boss mob IDs against db/pre-re/mob_db.conf
and db/re/mob_db.conf, and flags arcs where the boss's canonical Renewal level
is wildly out of line with the arc's target player level (S_Levels table in
dm_console.txt). Bosses are hand-listed below (rather than regex-scraped from
CAMPAIGN.md) since several entries don't follow a single "Name (id)" format.

Usage: python3 tools/verify_boss_levels.py
"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Arc -> [(boss name, mob id), ...]. Source: CAMPAIGN.md Quick Reference +
# "Mob IDs Verified" table. Arc 18 (Himmelmez) has no mob_db entry by design.
ARC_BOSSES = {
    1: [("Deviruchi", 1109)],
    2: [("Moonlight Flower", 1150)],
    3: [("Osiris", 1038), ("Amon Ra", 1511)],
    4: [("Baphomet", 1039)],
    5: [("Tao Gunka", 1583)],
    6: [("Mistress", 1059)],
    7: [("RSX-0806", 1623)],
    8: [("Dark Lord", 1272)],
    9: [("Gloom Under Night", 1768)],
    10: [("Kiel D-01", 1734)],
    11: [("Valkyrie Randgris", 1751)],
    12: [("Naght Sieger", 1956)],
    13: [("Beelzebub", 1874)],
    14: [("Ifrit", 1832)],
    15: [("Memory of Thanatos", 1708)],
    16: [("Bijou / Doppelganger", 1046)],
    17: [("Amdarais", 2476)],
    18: [],  # narrative-only, no mob (see CAMPAIGN.md design note)
    19: [("Surt / Garm", 1252)],
}

# Target finish/reward level by arc, from dm_console.txt S_Levels.
ARC_TARGET_LEVEL = {
    1: 18, 2: 28, 3: 38, 4: 48, 5: 58,
    6: 68, 7: 72, 8: 76, 9: 80, 10: 84,
    11: 88, 12: 90, 13: 92, 14: 94, 15: 95,
    16: 96, 17: 97, 18: 98, 19: 99,
}

FLAG_DELTA = 25  # |boss Lv - target Lv| above this gets flagged for @dm scale


def load_mob_levels(path):
    mobs = {}
    current_id = None
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("Id:"):
                try:
                    current_id = int(line.split(":")[1].strip())
                except ValueError:
                    current_id = None
            elif line.startswith("Lv:") and current_id is not None:
                try:
                    mobs[current_id] = int(line.split(":")[1].strip())
                except ValueError:
                    pass
                current_id = None
    return mobs


def main():
    pre_re = load_mob_levels(os.path.join(ROOT, "db/pre-re/mob_db.conf"))
    re_ = load_mob_levels(os.path.join(ROOT, "db/re/mob_db.conf"))

    print(f"{'Arc':>3} {'Boss':<24} {'ID':>5} {'Target Lv':>9} {'PreRE Lv':>8} {'RE Lv':>6}  Flag")
    for arc in sorted(ARC_BOSSES):
        target = ARC_TARGET_LEVEL[arc]
        bosses = ARC_BOSSES[arc]
        if not bosses:
            print(f"{arc:03d} {'(no mob — narrative)':<24} {'':>5} {target:>9} {'':>8} {'':>6}")
            continue
        for name, mob_id in bosses:
            pre_lv = pre_re.get(mob_id)
            re_lv = re_.get(mob_id)
            if re_lv is None:
                flag = "MISSING FROM re/mob_db.conf (won't spawn on this Renewal server!)"
            else:
                delta = re_lv - target
                flag = f"delta {delta:+d}" + (" ⚠" if abs(delta) > FLAG_DELTA else "")
                if pre_lv is None:
                    flag += "  (Renewal-only mob, not in pre-re db — fine, server runs Renewal)"
            print(f"{arc:03d} {name:<24} {mob_id:>5} {target:>9} "
                  f"{pre_lv if pre_lv is not None else '?':>8} "
                  f"{re_lv if re_lv is not None else '?':>6}  {flag}")


if __name__ == "__main__":
    main()
