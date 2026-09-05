#!/usr/bin/env python3
"""Generate the Seal Cascade hunting layer from db/dm_hunt_db.json.

The master file names, per hunting contract, which monsters drop which
turn-in items and how many the contract asks for. This tool does the
arithmetic and writes the three places that data has to appear:

  1. db/quest_db.conf              - the Drops: blocks the server rolls
  2. npc/custom/dm_campaign/shared/dm_hunts.txt  - the script-side table
  3. <korangar>/src/world/library/campaign_quests.tsv - the client quest log

Rates are DERIVED, never authored. A contract declares a kill budget; each
item's share of that budget plus the monster's own natural drop rate fixes
the quest bonus. Hand-editing a Rate in quest_db.conf will be reverted by
the next run and reported by --check.

Usage:
    tools/gen-hunts.py            write all three artifacts
    tools/gen-hunts.py --check    verify they match the master (exit 1 if not)
    tools/gen-hunts.py --report   print the kill-budget table and exit
"""

import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER = os.path.join(ROOT, 'db', 'dm_hunt_db.json')
QUEST_DB = os.path.join(ROOT, 'db', 'quest_db.conf')
SCRIPT_TABLE = os.path.join(ROOT, 'npc', 'custom', 'dm_campaign', 'shared', 'dm_hunts.txt')
KORANGAR_TSV = os.path.join(ROOT, os.pardir, 'korangar', 'korangar', 'src', 'world',
                            'library', 'campaign_quests.tsv')

# Hercules rolls quest drops out of 10000 (src/map/quest.c:335).
RATE_DENOMINATOR = 10000
# While a contract is open its items turn up this much more often, on top of
# the monster's own drop rate. One flat, explainable bonus: the contract
# speeds the hunt up, it does not replace it. Turn-in counts are derived from
# this and the kill budget, so a common drop is simply asked for in bulk.
CONTRACT_BONUS = 2000
# Never ask for a single item - a turn-in of one reads as a fetch, not a hunt.
MIN_COUNT = 2

BEGIN = '//================= Seal Cascade Campaign (custom) ========================'


def load_mob_db():
    """id -> {name, lv, exp, drops: {aegis: rate}} from the renewal mob db."""
    path = os.path.join(ROOT, 'db', 're', 'mob_db.conf')
    text = open(path, encoding='utf-8', errors='replace').read()
    mobs = {}
    for entry in re.split(r'\n(?=\{)', text):
        m = re.search(r'\bId:\s*(\d+)', entry)
        if not m:
            continue
        drops = {}
        block = re.search(r'\bDrops:\s*\{(.*?)\n\t\}', entry, re.S)
        if block:
            for line in block.group(1).split('\n'):
                d = re.match(r'\s*(\w+):\s*(\d+)', line)
                if d:
                    # A mob may list the same item twice; the rolls are
                    # independent, so the chance of at least one is what counts.
                    prev = drops.get(d.group(1), 0)
                    cur = int(d.group(2))
                    drops[d.group(1)] = RATE_DENOMINATOR - (
                        (RATE_DENOMINATOR - prev) * (RATE_DENOMINATOR - cur)
                        // RATE_DENOMINATOR)
        name = re.search(r'\bName:\s*"([^"]*)"', entry)
        sprite = re.search(r'\bSpriteName:\s*"([^"]*)"', entry)
        exp = re.search(r'\bExp:\s*(\d+)', entry)
        mobs[int(m.group(1))] = {
            'name': name.group(1) if name else '?',
            'sprite': sprite.group(1) if sprite else '',
            'exp': int(exp.group(1)) if exp else 0,
            'drops': drops,
        }
    return mobs


def load_item_db():
    """aegis name -> (id, display name)."""
    items = {}
    for rel in (('db', 're', 'item_db.conf'), ('db', 'item_db2.conf')):
        text = open(os.path.join(ROOT, *rel), encoding='utf-8', errors='replace').read()
        for m in re.finditer(r'\bId:\s*(\d+)\s*\n\s*AegisName:\s*"([^"]*)"\s*\n\s*Name:\s*"([^"]*)"', text):
            items[m.group(2)] = (int(m.group(1)), m.group(3))
    return items


def load_spawns():
    """mob id -> set of maps it spawns on, from the renewal spawn scripts."""
    spawns = {}
    base = os.path.join(ROOT, 'npc', 're', 'mobs')
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
                    spawns.setdefault(int(m.group(1)), set()).add(parts[0].split(',')[0].strip())
    return spawns


def derive(master, mobs, items, spawns):
    """Attach derived rates and expected kills, and collect problems."""
    problems = []
    for quest in master['quests']:
        weights = [p.get('weight', 1.0) for p in quest['items']]
        total_weight = sum(weights)
        for pick, weight in zip(quest['items'], weights):
            share = quest['budget'] * weight / total_weight
            mob = mobs.get(pick['mob'])
            where = 'quest %d "%s" item %s' % (quest['id'], quest['name'], pick['item'])
            if mob is None:
                problems.append('%s: mob %d is not in mob_db' % (where, pick['mob']))
                continue
            if pick['mob'] not in spawns:
                problems.append('%s: mob %d (%s) spawns on no map'
                                % (where, pick['mob'], mob['name']))
            # Hercules names summoned/guardian copies with a G_ sprite prefix.
            # They award no exp, carry no drop table and spawn nowhere, so a
            # contract pointed at one can never be filled by playing. This is
            # what quest 20173 did with 1868 G_BANSHEE instead of 1867 Banshee.
            if mob['sprite'].startswith('G_') and mob['exp'] == 0:
                problems.append('%s: mob %d (%s) is the summon-only %s variant'
                                % (where, pick['mob'], mob['name'], mob['sprite']))
            if pick['item'] not in items:
                problems.append('%s: no such item' % where)
                continue

            natural = mob['drops'].get(pick['item'], 0)
            pick['rate'] = CONTRACT_BONUS
            pick['natural'] = natural
            # Expected items per kill once the contract is open. The natural
            # and quest rolls are independent, so this can exceed 1.
            yield_per_kill = (natural + CONTRACT_BONUS) / float(RATE_DENOMINATOR)
            pick['count'] = max(MIN_COUNT, int(round(share * yield_per_kill)))
            pick['item_id'] = items[pick['item']][0]
            pick['item_name'] = items[pick['item']][1]
            pick['mob_name'] = mob['name']
            pick['kills'] = pick['count'] / yield_per_kill
        quest['kills'] = sum(p.get('kills', 0) for p in quest['items'])

    # Contracts within one arc are handed out together and are open at the same
    # time. Two of them asking for the same item would have countitem() count a
    # single stack toward both, and the first hand-in would take drops the
    # second still needs.
    by_arc = {}
    for quest in master['quests']:
        for pick in quest['items']:
            by_arc.setdefault((quest['arc'], pick['item']), []).append(quest['id'])
    for (arc, item), quest_ids in sorted(by_arc.items()):
        if len(quest_ids) > 1:
            problems.append('arc %d: %s is asked for by %s - contracts in one arc are '
                            'open at the same time and must not share an item'
                            % (arc, item, ' and '.join(str(q) for q in quest_ids)))

    return problems


def render_quest_db_block(master):
    """The campaign region of quest_db.conf, regenerated from the master."""
    by_id = {q['id']: q for q in master['quests']}
    text = open(QUEST_DB, encoding='utf-8').read()
    head, sep, tail = text.partition(BEGIN)
    if not sep:
        raise SystemExit('quest_db.conf: campaign marker not found')

    out = []
    for entry in re.split(r'\n(?=\{)', tail):
        m = re.search(r'Id:\s*(\d+)', entry)
        if not m or int(m.group(1)) not in by_id:
            out.append(entry)
            continue
        quest = by_id[int(m.group(1))]
        # Drop the old Targets:/Drops: body; the master owns it now. Both
        # comment styles this file uses appear in both block shapes, so match
        # the shapes rather than the contents - and stop at the closing paren
        # without eating the newline that separates it from the entry's brace.
        body = re.sub(r'\n\tTargets:\s*\(\n.*?\n\t\)', '', entry, flags=re.S)
        body = re.sub(r'\n\tTargets:\s*\([^\n]*\)', '', body)
        body = re.sub(r'\n\tDrops:\s*\(\n.*?\n\t\)', '', body, flags=re.S)
        body = re.sub(r'\n\tDrops:\s*\([^\n]*\)', '', body)
        lines = ['\tDrops: (']
        for pick in quest['items']:
            lines.append('\t{')
            lines.append('\t\tMobId: %d    /* %s */' % (pick['mob'], pick['mob_name']))
            lines.append('\t\tItemId: %d   /* %s x%d */'
                         % (pick['item_id'], pick['item_name'], pick['count']))
            lines.append('\t\tRate: %d' % pick['rate'])
            lines.append('\t},')
        lines.append('\t)')
        body = body.replace('\n},', '\n' + '\n'.join(lines) + '\n},', 1)
        out.append(body)
    return head + sep + '\n'.join(out)


def render_script_table(master):
    lines = [
        '// Seal Cascade hunting contracts - GENERATED, do not edit.',
        '//',
        '// Written by tools/gen-hunts.py from db/dm_hunt_db.json. Run',
        "// 'tools/gen-hunts.py --check' to confirm this file is current.",
        '//',
        '// DM_HuntSpec fills .@hunt_item[] / .@hunt_need[] for one contract and',
        '// returns how many distinct items it asks for, so the turn-in NPCs and',
        '// the progress lines all read the same numbers.',
        '',
        'function\tscript\tDM_HuntSpec\t{',
        '\t.@quest_id = getarg(0);',
        '',
        '\tsetarray getarg(1), 0;',
        '\tsetarray getarg(2), 0;',
        '',
        '\tswitch (.@quest_id) {',
    ]
    for quest in master['quests']:
        ids = ', '.join(str(p['item_id']) for p in quest['items'])
        need = ', '.join(str(p['count']) for p in quest['items'])
        names = ', '.join('%s x%d' % (p['item_name'], p['count']) for p in quest['items'])
        lines.append('\tcase %d:  // %s - %s' % (quest['id'], quest['name'], names))
        lines.append('\t\tsetarray getarg(1), %s;' % ids)
        lines.append('\t\tsetarray getarg(2), %s;' % need)
        lines.append('\t\treturn %d;' % len(quest['items']))
    lines += [
        '\t}',
        '',
        '\treturn 0;',
        '}',
        '',
        "// The contract's name, for progress displays that have only its id.",
        'function\tscript\tDM_HuntName\t{',
        '\tswitch (getarg(0)) {',
    ]
    for quest in master['quests']:
        lines.append('\tcase %d: return "%s";' % (quest['id'], quest['name']))
    lines += [
        '\t}',
        '',
        '\treturn "";',
        '}',
        '',
    ]
    return '\n'.join(lines)


def render_tsv(master):
    """quest_id \t name \t item_id:count,item_id:count,..."""
    rows = ['# GENERATED by Hercules/tools/gen-hunts.py from db/dm_hunt_db.json.',
            '# quest_id\tname\titem_id:count[,item_id:count...]']
    for quest in master['quests']:
        reqs = ','.join('%d:%d' % (p['item_id'], p['count']) for p in quest['items'])
        rows.append('%d\t%s\t%s' % (quest['id'], quest['name'], reqs))
    return '\n'.join(rows) + '\n'


def report(master):
    print('%-6s %-34s %6s %6s  %s' % ('id', 'contract', 'budget', 'kills', 'items'))
    for quest in master['quests']:
        detail = '; '.join('%s x%d (%.2f/kill, %.0f kills)'
                           % (p['item_name'], p['count'],
                              (p['natural'] + p['rate']) / float(RATE_DENOMINATOR),
                              p['kills'])
                           for p in quest['items'])
        flag = ' ' if abs(quest['kills'] - quest['budget']) <= quest['budget'] * 0.25 else '!'
        print('%-6d %-34s %6d %6.1f%s %s'
              % (quest['id'], quest['name'][:34], quest['budget'], quest['kills'], flag, detail))
    total = sum(q['kills'] for q in master['quests'])
    print('\n%d contracts, %d turn-in items, %.0f expected kills across the campaign'
          % (len(master['quests']),
             sum(len(q['items']) for q in master['quests']), total))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true', help='verify artifacts match the master')
    ap.add_argument('--report', action='store_true', help='print the kill-budget table')
    args = ap.parse_args()

    master = json.load(open(MASTER, encoding='utf-8'))
    problems = derive(master, load_mob_db(), load_item_db(), load_spawns())
    if problems:
        print('FAIL - %d problem(s) in db/dm_hunt_db.json:' % len(problems), file=sys.stderr)
        for p in problems:
            print('  ' + p, file=sys.stderr)
        return 1

    if args.report:
        report(master)
        return 0

    artifacts = [
        (QUEST_DB, render_quest_db_block(master)),
        (SCRIPT_TABLE, render_script_table(master)),
        (KORANGAR_TSV, render_tsv(master)),
    ]

    if args.check:
        stale = []
        for path, want in artifacts:
            if not os.path.exists(path):
                stale.append('%s: missing' % os.path.relpath(path, ROOT))
            elif open(path, encoding='utf-8').read() != want:
                stale.append('%s: out of date' % os.path.relpath(path, ROOT))
        if stale:
            print('FAIL - regenerate with tools/gen-hunts.py:', file=sys.stderr)
            for s in stale:
                print('  ' + s, file=sys.stderr)
            return 1
        print('OK - all three hunt artifacts match db/dm_hunt_db.json.')
        return 0

    for path, want in artifacts:
        if os.path.exists(path) and open(path, encoding='utf-8').read() == want:
            continue
        open(path, 'w', encoding='utf-8').write(want)
        print('wrote %s' % os.path.relpath(path, ROOT))
    return 0


if __name__ == '__main__':
    sys.exit(main())
