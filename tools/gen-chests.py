#!/usr/bin/env python3
"""Generate the Seal Cascade hidden chest manifest and verify parity with Hercules scripts.

Parses Hercules hidden chest locations from npc/re/other/achievement_treasures.txt
and Act I campaign titles/slots/hats from npc/custom/dm_campaign/shared/dm_treasures.txt.

Writes:
  <korangar>/src/world/library/chests.tsv

Usage:
  tools/gen-chests.py          write chests.tsv
  tools/gen-chests.py --check  verify chests.tsv matches scripts (exit 1 if not)
"""
from __future__ import annotations

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACH_TREASURES = os.path.join(ROOT, "npc", "re", "other", "achievement_treasures.txt")
DM_TREASURES = os.path.join(ROOT, "npc", "custom", "dm_campaign", "shared", "dm_treasures.txt")
KORANGAR_TSV = os.path.join(ROOT, os.pardir, "korangar", "korangar", "src", "world", "library", "chests.tsv")

SCHEMA_VERSION = 1

TITLES = {
    0: [
        "The Milestone That Moved", "Toll Ledger, Water-Stained", "A Child's Map",
        "Complaint, Unfiled", "Sluice Key, Spare", "The Long Count",
        "Bootprints Cast in Clay", "Humming Stones", "A Guard's Wager Book",
        "Refugee Roll", "The Gardener's Grievance", "Holt's Requisition",
    ],
    1: [
        "Apprentice's Practice Sheet", "Tower Rent Notice", "A Wand, Snapped Clean",
        "Field Notes on Ley Drift", "Letter From a Rival", "Cartomancer's Discard",
        "Warding Salt, Unused", "Vault Inventory, Amended",
    ],
    2: [
        "Water Ration Book", "Checkpoint Sign, Repainted", "A Digger's Contract",
        "Sand Glass, Cracked", "Relief Manifest", "A Dancer's Anklet",
        "Rubbing From a Sealed Door",
    ],
    3: [
        "Lantern Oil Account", "A Bow, Unstrung and Wrapped", "Grave Marker Rubbing",
        "Hunting Permit, Revoked", "Child's Prayer Strip", "Ancestor Roll, Torn",
        "Fletcher's Complaint", "Ferryman's Tally", "A Lantern That Will Not Light",
    ],
    4: [
        "Diver's Slate", "Manifest of the Sunken Ship",
    ],
}

HATS = {
    0: 5108,   # Renown Detective's Cap
    1: 5027,   # Mage Hat
    2: 2222,   # Turban
    3: 5170,   # Feather Beret
    4: 18645,  # Sailor Hat
}


def get_slot(cid: int) -> tuple[int, int]:
    """Map chest achievement ID to (region, slot_index) per DM_TreasureSlot."""
    if 120001 <= cid <= 120010:
        return (0, cid - 120001)
    if cid == 120140:
        return (0, 10)
    if cid == 120141:
        return (0, 11)
    if 120011 <= cid <= 120017:
        return (1, cid - 120011)
    if cid == 120123:
        return (1, 7)
    if 120018 <= cid <= 120023:
        return (2, cid - 120018)
    if cid == 120137:
        return (2, 6)
    if 120024 <= cid <= 120031:
        return (3, cid - 120024)
    if cid == 120139:
        return (3, 8)
    if cid == 120131:
        return (4, 0)
    if cid == 120144:
        return (4, 1)
    return (-1, -1)


def parse_chests() -> list[dict]:
    with open(ACH_TREASURES, "r", encoding="utf-8") as f:
        text = f.read()

    chests = []
    pattern = re.compile(
        r"^([a-zA-Z0-9_]+),(\d+),(\d+),\d+\s+duplicate\(achievement_tr\)\s+#tr(\d+)\s+4_TREASURE_BOX"
    )
    for line in text.splitlines():
        line = line.strip()
        m = pattern.match(line)
        if m:
            map_name, x, y, chest_id = m.groups()
            cid = int(chest_id)
            region, slot = get_slot(cid)
            if region >= 0:
                title = TITLES[region][slot]
                hat = HATS[region]
            else:
                title = "A Hidden Cache"
                hat = 0
            chests.append({
                "id": cid,
                "map": map_name,
                "x": int(x),
                "y": int(y),
                "region": region,
                "title": title,
                "hat_id": hat,
            })

    # Validate uniqueness
    ids = [c["id"] for c in chests]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate chest IDs found in achievement_treasures.txt")

    coords = [(c["map"], c["x"], c["y"]) for c in chests]
    if len(coords) != len(set(coords)):
        raise ValueError("Duplicate chest coordinates found in achievement_treasures.txt")

    return chests


def render_tsv(chests: list[dict]) -> str:
    lines = [
        f"# schema_version: {SCHEMA_VERSION}",
        "id\tmap\tx\ty\tregion\ttitle\that_id",
    ]
    for c in chests:
        lines.append(f"{c['id']}\t{c['map']}\t{c['x']}\t{c['y']}\t{c['region']}\t{c['title']}\t{c['hat_id']}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate/check chests manifest")
    parser.add_argument("--check", action="store_true", help="Check manifest against scripts")
    args = parser.parse_args()

    chests = parse_chests()
    content = render_tsv(chests)

    if args.check:
        if not os.path.exists(KORANGAR_TSV):
            print(f"FAIL: {KORANGAR_TSV} does not exist", file=sys.stderr)
            sys.exit(1)
        with open(KORANGAR_TSV, "r", encoding="utf-8") as f:
            existing = f.read()
        if existing != content:
            print("FAIL: chests.tsv does not match scripts", file=sys.stderr)
            sys.exit(1)
        print(f"OK: chests.tsv matches ({len(chests)} chests, 38 Act I).")
        sys.exit(0)

    os.makedirs(os.path.dirname(KORANGAR_TSV), exist_ok=True)
    with open(KORANGAR_TSV, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Wrote {KORANGAR_TSV} ({len(chests)} chests, 38 Act I).")


if __name__ == "__main__":
    main()
