#!/usr/bin/env python3
"""Map every setquest in Hercules NPC scripts to the NPC that issues it.

Writes korangar/.../quest_locations.tsv so the journal can show where to go
for any quest that appears in the log, not only Seal Cascade hunts.

Campaign locations from gen-hunts.py overlay this file in the client.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NPC_ROOT = os.path.join(ROOT, 'npc')
OUT = os.path.join(ROOT, os.pardir, 'korangar', 'korangar', 'src', 'world',
                   'library', 'quest_locations.tsv')

NPC_HEADER = re.compile(
    r'^([a-zA-Z0-9_]+),(\d+),(\d+),-?\d+\t+script\t+([^\t#]+)'
)
SETQUEST = re.compile(
    r'\b(?:setquest|completequest)\s*\(?\s*(\d+)\s*\)?'
    r'|\bsetquestinfo\s+QINFO_QUEST,\s*(\d+)'
)


def load_names():
    path = os.path.join(os.path.dirname(OUT), 'quest_names.tsv')
    names = {}
    if os.path.exists(path):
        for line in open(path, encoding='utf-8', errors='replace'):
            if not line[:1].isdigit():
                continue
            qid, name = line.split('\t', 1)
            names[int(qid)] = name.strip()
    return names


def load_quest_mobs():
    """quest id -> first target mob id from quest_db.conf."""
    path = os.path.join(ROOT, 'db', 'quest_db.conf')
    text = open(path, encoding='utf-8', errors='replace').read()
    quests = {}
    current = None
    for line in text.splitlines():
        m = re.search(r'\bId:\s*(\d+)', line)
        if m and 'Quest ID' not in line:
            current = int(m.group(1))
            continue
        m = re.search(r'\bMobId:\s*(\d+)', line)
        if m and current is not None:
            quests.setdefault(current, int(m.group(1)))
    return quests


def load_spawns():
    spawns = {}
    base = os.path.join(ROOT, 'npc', 're', 'mobs')
    if not os.path.isdir(base):
        return spawns
    for dirpath, _dirs, files in os.walk(base):
        for fname in files:
            if not fname.endswith('.txt'):
                continue
            for line in open(os.path.join(dirpath, fname), encoding='utf-8', errors='replace'):
                line = line.strip()
                if not line or line.startswith('//'):
                    continue
                parts = line.split('\t')
                if len(parts) < 4 or parts[1].strip() not in ('monster', 'boss_monster'):
                    continue
                m = re.match(r'\s*(\d+)\s*,', parts[3])
                if m:
                    spawns.setdefault(int(m.group(1)), [])
                    mmap = parts[0].split(',')[0].strip()
                    if mmap not in spawns[int(m.group(1))]:
                        spawns[int(m.group(1))].append(mmap)
    return spawns


def name_prefix(name):
    for sep in (' - ', ' — ', ':'):
        if sep in name:
            return name.split(sep, 1)[0].strip()
    return name.strip()


def fill_gaps(found, names, quest_mobs, spawns):
    """Inherit giver NPC along a named chain; add hunt maps from kill targets."""
    by_prefix = {}
    for qid, name in names.items():
        by_prefix.setdefault(name_prefix(name), []).append(qid)
    for _prefix, ids in by_prefix.items():
        ids.sort()
        donor = None
        for qid in ids:
            if qid in found:
                donor = found[qid]
                break
        if donor is None:
            continue
        for qid in ids:
            found.setdefault(qid, donor)

    extra_zone = {}
    for qid, mob in quest_mobs.items():
        maps = spawns.get(mob) or []
        if maps:
            extra_zone[qid] = maps[0]
    return extra_zone


def scan():
    found = {}  # id -> (npc, map, x, y, source)
    for dirpath, _dirs, files in os.walk(NPC_ROOT):
        for fname in files:
            if not fname.endswith('.txt'):
                continue
            path = os.path.join(dirpath, fname)
            rel = os.path.relpath(path, ROOT)
            try:
                text = open(path, encoding='utf-8', errors='replace').read()
            except OSError:
                continue
            current = None
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.startswith('//'):
                    continue
                header = NPC_HEADER.match(line)
                if header:
                    name = header.group(4).strip()
                    if name.upper() in ('HIDDEN_NPC', 'FAKE_NPC', '-'):
                        continue
                    current = (name, header.group(1), int(header.group(2)), int(header.group(3)), rel)
                    continue
                for m in SETQUEST.finditer(line):
                    qid = int(m.group(1) or m.group(2))
                    if qid <= 0 or current is None:
                        continue
                    # First script hit wins (usually the quest giver).
                    found.setdefault(qid, current)
    return found


def render(found, zones):
    rows = [
        '# GENERATED by Hercules/tools/export_quest_locations.py from npc scripts.',
        '# quest_id\tnpc\tmap\tx\ty\thunt_zone\tsource',
    ]
    for qid in sorted(set(found) | set(zones)):
        npc, mmap, x, y, src = found.get(qid, ('', '', 0, 0, 'quest_db'))
        npc = npc.replace('\t', ' ')
        zone = zones.get(qid, '')
        rows.append('%d\t%s\t%s\t%d\t%d\t%s\t%s' % (qid, npc, mmap, x, y, zone, src))
    return '\n'.join(rows) + '\n'


def main():
    found = scan()
    names = load_names()
    zones = fill_gaps(found, names, load_quest_mobs(), load_spawns())
    text = render(found, zones)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write(text)
    named_hit = sum(1 for qid in names if qid in found or qid in zones)
    print('wrote %d location rows (%d of %d named quests) to %s' % (
        len(found) + sum(1 for q in zones if q not in found),
        named_hit, len(names), os.path.relpath(OUT, ROOT)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
