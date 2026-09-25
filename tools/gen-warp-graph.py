#!/usr/bin/env python3
"""Export literal warp NPC declarations into Korangar's route graph.

Only declarations with a concrete source and destination are exported. Script
warps whose destination is a variable, instance, or runtime expression remain
outside this static graph and are reported in the summary. The generated file
is sorted and checked into the client so route data is reproducible from the
server scripts.
"""

import argparse
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / ".." / "korangar" / "korangar" / "src" / "world" / "library" / "warp_graph.tsv"
SCHEMA = 1

WARP = re.compile(
    r"^\s*(?P<from>[A-Za-z0-9_.-]+),(?P<fx>\d+),(?P<fy>\d+),\d+\s+"
    r"warp\s+\S+\s+(?P<sx>\d+),(?P<sy>\d+),(?P<to>[A-Za-z0-9_.-]+),(?P<tx>\d+),(?P<ty>\d+)\s*;?"
)
NPC = re.compile(r"^\s*(?P<map>[A-Za-z0-9_.-]+),(?P<x>\d+),(?P<y>\d+),\d+\s+(?:script|duplicate)\b.*\{")
SCRIPT_WARP = re.compile(r"\bwarp\s*\(?\s*\"(?P<to>[A-Za-z0-9_.-]+)\"\s*,\s*(?P<tx>\d+)\s*,\s*(?P<ty>\d+)")
DYNAMIC_WARP = re.compile(r"\bwarp\s*(?:\(|\s+\")")


def map_names():
    maps = {}
    for path in (ROOT / "maps" / "re").glob("*.mcache"):
        header = path.read_bytes()[:22]
        if len(header) < 22:
            raise ValueError(f"truncated map cache header: {path}")
        _version, _checksum, width, height = struct.unpack_from("<h16shh", header)
        if width <= 0 or height <= 0:
            raise ValueError(f"invalid map dimensions: {path}")
        maps[path.stem] = (width, height)
    return maps


def export():
    known_maps = map_names()
    rows = []
    dynamic = []
    skipped = 0
    script_roots = (ROOT / "npc" / "re" / "warps", ROOT / "npc" / "custom" / "dm_campaign")
    for path in sorted(path for base in script_roots for path in base.rglob("*.txt")):
        relative = path.relative_to(ROOT).as_posix()
        npc_source = None
        for line_number, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            line = raw.split("//", 1)[0]
            npc = NPC.match(line)
            if npc:
                npc_source = (npc.group("map"), int(npc.group("x")), int(npc.group("y")))
            match = WARP.match(line)
            if not match:
                script_warp = SCRIPT_WARP.search(line)
                if script_warp and npc_source:
                    from_map, from_x, from_y = npc_source
                    to_map = script_warp.group("to")
                    if from_map not in known_maps or to_map not in known_maps:
                        raise ValueError(f"{relative}:{line_number}: unknown map {from_map} -> {to_map}")
                    from_width, from_height = known_maps[from_map]
                    to_width, to_height = known_maps[to_map]
                    tx, ty = int(script_warp.group("tx")), int(script_warp.group("ty"))
                    if not (0 <= from_x < from_width and 0 <= from_y < from_height):
                        raise ValueError(f"{relative}:{line_number}: source coordinate outside {from_map}")
                    if not (0 <= tx < to_width and 0 <= ty < to_height):
                        raise ValueError(f"{relative}:{line_number}: destination coordinate outside {to_map}")
                    rows.append({
                        "from_map": from_map, "from_x": from_x, "from_y": from_y,
                        "to_map": to_map, "to_x": tx, "to_y": ty,
                        "gated": 1, "source": f"{relative}:{line_number}",
                    })
                elif DYNAMIC_WARP.search(line) and not line.strip().startswith("//"):
                    kind = "custom_dm" if "/npc/custom/dm_campaign/" in f"/{relative}" else "dynamic"
                    dynamic.append((f"{relative}:{line_number}", kind, line.strip()))
                    skipped += 1
                continue
            data = match.groupdict()
            if data["from"] not in known_maps or data["to"] not in known_maps:
                raise ValueError(f"{relative}:{line_number}: unknown map {data['from']} -> {data['to']}")
            from_width, from_height = known_maps[data["from"]]
            to_width, to_height = known_maps[data["to"]]
            if not (0 <= int(data["fx"]) < from_width and 0 <= int(data["fy"]) < from_height):
                raise ValueError(f"{relative}:{line_number}: source coordinate outside {data['from']} ({from_width}x{from_height})")
            if not (0 <= int(data["tx"]) < to_width and 0 <= int(data["ty"]) < to_height):
                raise ValueError(f"{relative}:{line_number}: destination coordinate outside {data['to']} ({to_width}x{to_height})")
            rows.append({
                "from_map": data["from"], "from_x": int(data["fx"]), "from_y": int(data["fy"]),
                "to_map": data["to"], "to_x": int(data["tx"]), "to_y": int(data["ty"]),
                "source": f"{relative}:{line_number}",
            })
            if line.rstrip().endswith("}"):
                npc_source = None

    pairs = {(row["from_map"], row["to_map"]) for row in rows}
    for row in rows:
        row["one_way"] = int((row["to_map"], row["from_map"]) not in pairs)
        # Literal warp declarations are not level/quest gated. Runtime and
        # conditional expressions are deliberately not represented as edges.
        row.setdefault("gated", 0)
        row["reserved"] = 0

    rows.sort(key=lambda row: (
        row["from_map"], row["from_x"], row["from_y"], row["to_map"],
        row["to_x"], row["to_y"], row["source"],
    ))
    output = [f"# schema={SCHEMA}", "# from_map\tfrom_x\tfrom_y\tto_map\tto_x\tto_y\tone_way\tgated\treserved\tsource"]
    output.extend(
        "\t".join(str(row[key]) for key in (
            "from_map", "from_x", "from_y", "to_map", "to_x", "to_y",
            "one_way", "gated", "reserved", "source",
        ))
        for row in rows
    )
    output.append("# dynamic")
    output.append("# tag\tsource\tkind\tgated\tavailable\texpression")
    output.extend(f"@dynamic\t{source}\t{kind}\t1\t0\t{expression}" for source, kind, expression in dynamic)
    return "\n".join(output) + "\n", len(rows), skipped


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        generated, count, skipped = export()
    except (OSError, ValueError) as error:
        print(f"gen-warp-graph.py: {error}", file=sys.stderr)
        return 1
    if args.check:
        actual = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if actual != generated:
            print(f"warp graph is stale: regenerate {OUTPUT}", file=sys.stderr)
            return 1
    else:
        OUTPUT.write_text(generated, encoding="utf-8")
    print(f"warp graph: {count} literal edges; {skipped} dynamic/unsupported warp lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
