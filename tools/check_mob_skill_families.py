#!/usr/bin/env python3
"""Check reviewed invariants shared by the Orc undead skill template."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "db/re/mob_skill_db.conf"
MEMBERS = ("ORC_ZOMBIE", "ORC_SKELETON")
INVARIANT_FIELDS = (
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
)
REQUIRED_PAIRS = {
    ("NPC_CRITICALSLASH", "MSS_ANGRY"),
    ("NPC_CRITICALSLASH", "MSS_BERSERK"),
    ("NPC_UNDEADATTACK", "MSS_ANGRY"),
    ("NPC_UNDEADATTACK", "MSS_BERSERK"),
    ("NPC_POISON", "MSS_BERSERK"),
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


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DB
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", "", text)

    try:
        by_member = {name: skill_records(named_block(text, name)) for name in MEMBERS}
        left, right = (by_member[name] for name in MEMBERS)
        for pair in sorted(REQUIRED_PAIRS):
            if pair not in left or pair not in right:
                raise ValueError(f"required shared skill-state {pair} is missing")
            for field in INVARIANT_FIELDS:
                if left[pair].get(field) != right[pair].get(field):
                    raise ValueError(
                        f"{pair} differs at {field}: "
                        f"{MEMBERS[0]}={left[pair].get(field)!r}, "
                        f"{MEMBERS[1]}={right[pair].get(field)!r}"
                    )
    except (OSError, ValueError) as error:
        print(f"mob skill family check failed: {error}", file=sys.stderr)
        return 1

    print(f"Orc undead family check passed: {len(REQUIRED_PAIRS)} shared skill-state records in {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
