#!/usr/bin/env python3
"""Static Act I checks. No map-server required.

Catches the class of defect a clean script load will not see: hunt AND-gates
on story, Complete-Arc beats that skip DM_Arc0NComplete, ally_turnout bumps
from Act I menus, Holt fate written before the death label.
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
ACT = ROOT / "npc/custom/dm_campaign/act_01"
SHARED = ROOT / "npc/custom/dm_campaign/shared"
BEATS = SHARED / "dm_beats.txt"
fails: list[str] = []


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def strip_comments(text: str) -> str:
    return re.sub(r"//.*?$", "", text, flags=re.M)


def check_no_ally_turnout() -> None:
    for path in ACT.glob("*.txt"):
        if "dm_arc19_ally_turnout" in read(path):
            fails.append(f"{path.name}: Act I must not touch dm_arc19_ally_turnout")


def check_hunt_and_gates() -> None:
    gates = [
        (r"questprogress\(20002\)\s*==\s*2.{0,80}questprogress\(20003\)\s*==\s*2", "arc1 20002&&20003"),
        (r"questprogress\(20008\)\s*==\s*2.{0,80}questprogress\(20009\)\s*==\s*2", "arc2 20008&&20009"),
        (r"questprogress\(20014\)\s*==\s*2.{0,80}questprogress\(20015\)\s*==\s*2", "arc3 20014&&20015"),
        (r"questprogress\(20020\)\s*==\s*2.{0,80}questprogress\(20021\)\s*==\s*2", "arc4 20020&&20021"),
        (r"questprogress\(20027\)\s*==\s*2.{0,80}questprogress\(20028\)\s*==\s*2", "arc5 20027&&20028"),
    ]
    for path in ACT.glob("*.txt"):
        body = strip_comments(read(path))
        for pat, label in gates:
            if re.search(pat, body, re.S):
                fails.append(f"{path.name}: hunt AND-gate still present ({label})")


def check_complete_helpers() -> None:
    beats = read(BEATS)
    for arc, helper in (
        ("DM_BeatArc01", "DM_Arc01Complete"),
        ("DM_BeatArc02", "DM_Arc02Complete"),
        ("DM_BeatArc03", "DM_Arc03Complete"),
        ("DM_BeatArc04", "DM_Arc04Complete"),
        ("DM_BeatArc05", "DM_Arc05Complete"),
    ):
        m = re.search(rf"function\s+script\s+{arc}\s*\{{(.*?)\nfunction\s+script", beats, re.S)
        if not m:
            fails.append(f"beats: could not find {arc}")
            continue
        body = m.group(1)
        if helper not in body:
            fails.append(f"beats: {arc} does not call {helper}")
        # Start beats must not auto-start every hunt as a bundle with the tracker.
        if arc == "DM_BeatArc01" and re.search(
            r"DM_InstanceQuestStart\",\s*20001\).{0,200}DM_InstanceQuestStart\",\s*20002",
            body,
            re.S,
        ):
            fails.append("beats: Arc 1 start still auto-starts hunts with 20001")


def check_holt_fate_on_death() -> None:
    text = read(ACT / "arc_01_prontera.txt")
    pre, _, post = text.partition("OnDeviruchiDead:")
    if "dm_arc01_holt_killed" in pre or "dm_arc01_holt_spared" in pre:
        fails.append("arc_01: Holt spared/killed is written before OnDeviruchiDead")
    if "dm_arc01_holt_killed" not in post:
        fails.append("arc_01: Holt killed is not written in OnDeviruchiDead")


def check_world_npcs() -> None:
    required = [
        (ACT / "arc_01_prontera.txt", ("Mira#dm", "Painted Sluice#dm", "Tide-Wheel#dm", "Binding Stone#dm")),
        (ACT / "arc_02_payon.txt", ("West Memorial#dm", "Grove Conduit A#dm", "Shrine Lantern W#dm")),
        (ACT / "arc_03_morroc.txt", ("North Relief Well#dm", "Relief Checkpoint B#dm")),
        (ACT / "arc_04_geffen.txt", ("East Seal Glyph#dm", "Geffen Street Lamp#dm")),
        (ACT / "arc_05_alberta_izlude.txt", ("Saltmother Plank#dm", "West Diver Line#dm", "Harbor Survivor#dm")),
    ]
    for path, names in required:
        text = read(path)
        for name in names:
            if name not in text:
                fails.append(f"{path.name}: missing world NPC {name}")


def check_session_loaded() -> None:
    conf = read(ROOT / "npc/scripts_custom.conf")
    if "dm_session.txt" not in conf:
        fails.append("scripts_custom.conf does not load dm_session.txt")


def check_no_sessionparty_fallback() -> None:
    for path in ACT.glob("*.txt"):
        if "DM_SessionParty" in read(path):
            fails.append(f"{path.name}: still falls back to DM_SessionParty on death")


def main() -> int:
    check_no_ally_turnout()
    check_hunt_and_gates()
    check_complete_helpers()
    check_holt_fate_on_death()
    check_world_npcs()
    check_session_loaded()
    check_no_sessionparty_fallback()
    if fails:
        print("FAIL — Act I static checks:")
        for line in fails:
            print("  -", line)
        return 1
    print("OK — Act I static checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
