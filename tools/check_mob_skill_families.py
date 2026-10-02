#!/usr/bin/env python3
"""Check reviewed invariants shared by mob skill family templates and generate templates for new members."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "db/re/mob_skill_db.conf"

FAMILIES = {
    "Orc undead": {
        "members": ("ORC_ZOMBIE", "ORC_SKELETON"),
        "invariant_fields": (
            "SkillLevel",
            "Rate",
            "CastTime",
            "Delay",
            "Cancelable",
            "SkillTarget",
            "CastCondition",
            "ConditionData",
            "val0",
            "val1",
            "val2",
            "val3",
            "val4",
            "Emotion",
            "ChatMsgID",
        ),
        "required_pairs": {
            ("NPC_CRITICALSLASH", "MSS_ANGRY"),
            ("NPC_CRITICALSLASH", "MSS_BERSERK"),
            ("NPC_UNDEADATTACK", "MSS_ANGRY"),
            ("NPC_UNDEADATTACK", "MSS_BERSERK"),
            ("NPC_POISON", "MSS_BERSERK"),
        },
    },
    "Raydric (Glast Heim Chivalry)": {
        "members": ("RAYDRIC", "RAYDRIC_ARCHER"),
        "invariant_fields": (
            "SkillLevel",
            "Rate",
            "CastTime",
            "Delay",
            "Cancelable",
            "SkillTarget",
            "CastCondition",
        ),
        "required_pairs": {
            ("CR_AUTOGUARD", "MSS_BERSERK"),
            ("CR_AUTOGUARD", "MSS_RUSH"),
            ("NPC_DARKNESSATTACK", "MSS_BERSERK"),
        },
    },
}


def matching_brace(text: str, opening: int) -> int:
    depth = 0
    for index in range(opening, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    raise ValueError("unclosed configuration block")


def named_block(text: str, name: str) -> str:
    match = re.search(rf"(?m)^\s*{re.escape(name)}\s*:\s*\{{", text)
    if not match:
        raise ValueError(f"missing {name} block")
    opening = text.index("{", match.start())
    return text[opening + 1 : matching_brace(text, opening)]


def skill_records(mob_block: str) -> dict[tuple[str, str], dict[str, str]]:
    records: dict[tuple[str, str], dict[str, str]] = {}
    # Skill blocks in Hercules libconfig contain scalar fields only.
    for match in re.finditer(r"(?m)^\s*([A-Z0-9_]+)\s*:\s*\{([^{}]*)\}", mob_block):
        skill_name, body = match.groups()
        fields = {
            key: value.strip()
            for key, value in re.findall(r"(?m)^\s*(\w+)\s*:\s*([^\n]+?)\s*$", body)
        }
        state = fields.get("SkillState", '"MSS_ANY"')
        key = (skill_name, state.strip('"'))
        if key in records:
            raise ValueError(f"duplicate skill-state record {key}")
        records[key] = fields
    return records


def generate_template(text: str, family_name: str) -> str:
    fam = FAMILIES.get(family_name)
    if not fam:
        available = ", ".join(repr(k) for k in FAMILIES.keys())
        raise ValueError(f"Unknown family {family_name!r}. Available: {available}")
    donor = fam["members"][0]
    records = skill_records(named_block(text, donor))
    lines = [f"// Template: {family_name} (extracted from donor {donor})"]
    for skill_name, state in sorted(fam["required_pairs"]):
        fields = records[(skill_name, state)]
        lines.append(f"\t\t{skill_name}: {{")
        for k, v in fields.items():
            lines.append(f"\t\t\t{k}: {v}")
        lines.append("\t\t}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("db_path", nargs="?", default=str(DEFAULT_DB), help="Path to mob_skill_db.conf")
    parser.add_argument("--generate", metavar="FAMILY", help="Generate a template snippet for a family")
    parser.add_argument("--list-families", action="store_true", help="List registered family templates")
    args = parser.parse_args()

    if args.list_families:
        print("Registered monster family templates:")
        for name, data in FAMILIES.items():
            print(f"  - {name}: members {', '.join(data['members'])} ({len(data['required_pairs'])} shared skills)")
        return 0

    path = Path(args.db_path)
    text = path.read_text(encoding="utf-8")
    cleaned_text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    cleaned_text = re.sub(r"//[^\n]*", "", cleaned_text)

    if args.generate:
        try:
            snippet = generate_template(cleaned_text, args.generate)
            print(snippet)
            return 0
        except ValueError as error:
            print(f"Template generation failed: {error}", file=sys.stderr)
            return 1

    failures = 0
    print(f"Checking mob skill family consistency in {path}...")
    for family_name, spec in FAMILIES.items():
        members = spec["members"]
        invariant_fields = spec["invariant_fields"]
        required_pairs = spec["required_pairs"]
        try:
            by_member = {name: skill_records(named_block(cleaned_text, name)) for name in members}
            reference = by_member[members[0]]
            for other_name in members[1:]:
                other = by_member[other_name]
                for pair in sorted(required_pairs):
                    if pair not in reference or pair not in other:
                        raise ValueError(f"required shared skill-state {pair} is missing from {members[0]} or {other_name}")
                    for field in invariant_fields:
                        if reference[pair].get(field) != other[pair].get(field):
                            raise ValueError(
                                f"{pair} differs at {field}: "
                                f"{members[0]}={reference[pair].get(field)!r}, "
                                f"{other_name}={other[pair].get(field)!r}"
                            )
            print(f"  [OK] {family_name}: {len(required_pairs)} shared skill-state records verified across {', '.join(members)}.")
        except (OSError, ValueError) as error:
            print(f"  [FAIL] {family_name}: {error}", file=sys.stderr)
            failures += 1

    if failures > 0:
        print(f"Mob skill family check failed: {failures} error(s).", file=sys.stderr)
        return 1

    print(f"All {len(FAMILIES)} mob skill families passed consistency verification.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
