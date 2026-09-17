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
KORANGAR_LOC = os.path.join(ROOT, os.pardir, 'korangar', 'korangar', 'src', 'world',
                            'library', 'campaign_quest_locations.tsv')
KORANGAR_HUNT_OBJ = os.path.join(ROOT, os.pardir, 'korangar', 'korangar', 'src', 'world',
                                 'library', 'hunt_objectives.tsv')
KORANGAR_HUNT_GUIDE = os.path.join(ROOT, os.pardir, 'korangar', 'korangar', 'src', 'world',
                                 'library', 'hunt_guidance.tsv')
KORANGAR_STORY = os.path.join(ROOT, os.pardir, 'korangar', 'korangar', 'src', 'world',
                              'library', 'hunt_story.tsv')
CAMPAIGN_FLAGS = os.path.join(ROOT, 'npc', 'custom', 'dm_campaign', 'shared', 'dm_flags.txt')

# Town hub who hands out / takes in contracts for each hunt arc.
ARC_HUBS = {
    1: ('Quartermaster Wynne', 'prontera', 156, 191),
    2: ('Sun-Hwa', 'payon', 181, 104),
    3: ('Rashid the Guide', 'morocc', 159, 97),
    4: ('Apprentice Elsbeth', 'geffen', 120, 100),
    5: ('Captain Mara', 'alberta', 184, 150),
    6: ('Doctor Ingrid Vahl', 'yuno', 155, 185),
    7: ('Greta Holm', 'einbroch', 145, 230),
    8: ('Sir Aldric Unfrocked', 'geffen', 120, 120),
    9: ('Acolyte Naima', 'rachel', 120, 120),
    10: ('Doctor Sabine Reuter', 'lighthalzen', 120, 120),
    11: ('Priest Eadric', 'hugel', 100, 100),
    12: ('Envoy Aelith', 'mid_camp', 100, 100),
    13: ('Father Quill', 'nameless_i', 100, 100),
    14: ('Foreman Dunmar', 'veins', 100, 100),
    15: ('Keeper Lysandra', 'aldebaran', 100, 100),
    16: ('Kronecker G Heine', 'prontera', 150, 150),
    17: ('Doctor Mira Tressa', 'ba_in01', 100, 100),
    18: ('The Familiar Dead', 'niflheim', 100, 100),
    19: ('Loki The Voice', 'moc_ruins', 150, 150),
}

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


def scan_story_npcs():
    """quest_id -> (npc, map, x, y) from campaign script headers + setquestinfo."""
    npc_re = re.compile(
        r'^([a-z0-9_]+),(\d+),(\d+),\d+\tscript\t([^#\t]+)#',
        re.M)
    quest_re = re.compile(r'setquestinfo QINFO_QUEST,\s*(\d+)')
    found = {}
    campaign = os.path.join(ROOT, 'npc', 'custom', 'dm_campaign')
    for dirpath, _dirs, files in os.walk(campaign):
        for fname in files:
            if not fname.endswith('.txt'):
                continue
            text = open(os.path.join(dirpath, fname), encoding='utf-8', errors='replace').read()
            current = None
            for line in text.splitlines():
                m = npc_re.match(line)
                if m:
                    current = (m.group(4).strip(), m.group(1), int(m.group(2)), int(m.group(3)))
                    continue
                for qid in quest_re.findall(line):
                    if current and int(qid) not in found:
                        found[int(qid)] = current
    return found


def render_locations(master):
    """quest_id \t kind \t hunt_zone \t npc \t map \t x \t y"""
    hunt_ids = {q['id'] for q in master['quests']}
    story = scan_story_npcs()
    rows = [
        '# GENERATED by Hercules/tools/gen-hunts.py',
        '# quest_id\tkind\thunt_zone\tnpc\tmap\tx\ty',
    ]
    for quest in master['quests']:
        npc, mmap, x, y = ARC_HUBS.get(quest.get('arc', 0), ('Quest giver', '', 0, 0))
        zone = quest.get('zone', '')
        rows.append('%d\thunt\t%s\t%s\t%s\t%d\t%d' % (
            quest['id'], zone, npc, mmap, x, y))
    for qid, (npc, mmap, x, y) in sorted(story.items()):
        if qid in hunt_ids:
            continue
        rows.append('%d\tstory\t\t%s\t%s\t%d\t%d' % (qid, npc, mmap, x, y))
    return '\n'.join(rows) + '\n'


def readable_area(zone):
    mapping = {
        'prt_sewb1-3': 'Prontera Culverts',
        'prt_fild07': 'Prontera West Field',
        'pay_fild02/06': 'Payon Forest',
        'pay_dun00': 'Payon Caves',
        'moc_fild01/02': 'Sograt Desert',
        'anthell01': 'Ant Hell',
        'in_sphinx1/2': 'Sphinx Dungeon',
        'gef_dun00': 'Geffen Dungeon',
        'gef_fild03/10': 'Orc Village',
        'mjolnir_11': 'Mt. Mjolnir',
        'iz_dun03': 'Byalan Island Dungeon',
        'treasure01/02': 'Sunken Ship',
        'yuno_fild03/04': 'Yuno Field',
        'juperos_01/jupe_core': 'Juperos Ruins',
        'yuno_fild03': 'El Mes Plateau',
        'ein_dun01': 'Einbroch Mine Dungeon',
        'ein_fild06/07': 'Einbroch Field',
        'ein_dun01/02': 'Einbroch Mine Dungeon',
        'gl_knt01/02': 'Glast Heim Knights',
        'gl_chyard/gl_church': 'Glast Heim Abbey',
        'ice_dun02/03': 'Ice Dungeon',
        'ice_dun02': 'Ice Dungeon',
        'lhz_dun01/02': 'Somatology Laboratory',
        'kh_dun01/02': 'Kiel Dungeon',
        'abyss_01/02': 'Abyss Lake',
        'hu_fild05': 'Abyss Lake Entrance',
        'spl_fild02': 'Splendide Field',
        'man_fild01': 'Manuk Field',
        'nameless_n': 'Nameless Island',
        'abbey01/02': 'Cursed Abbey',
        'thor_v01': 'Thor Volcano',
        'thor_v02': 'Thor Volcano',
        'c_tower3/4': 'Clock Tower',
        'alde_dun02/03': 'Clock Tower Basement',
        'prt_maze01/02': 'Labyrinth Forest',
        'prt_prison': 'Underground Prison',
        'sp_cor': 'Special Security Area Cor',
        'ba_2wash': 'Bathory Underground',
        'ba_pw02': 'Power Plant 02',
        'ba_in01': 'Varmundt Biosphere',
    }
    if zone in mapping:
        return mapping[zone]
    return zone.replace('_', ' ').title()


def render_hunt_objectives(master, mobs):
    """quest_id \t name \t type \t sources \t items \t maps \t share \t turn_in \t required \t completion \t dm_trigger"""
    rows = ['# schema=1']
    for quest in master['quests']:
        qid = quest['id']
        name = quest['name']
        obj_type = 'Collect'
        src_parts = []
        item_parts = []
        for pick in quest['items']:
            mob_id = pick['mob']
            mob = mobs.get(mob_id, {})
            mname = pick.get('mob_name') or mob.get('name', 'Monster')
            if mname.lower() == 'vocal' or mob_id == 1088:
                rank = 'vocal'
            elif mob.get('exp', 0) > 10000:
                rank = 'boss'
            else:
                rank = 'normal'
            src_parts.append(f'{mob_id}:{rank}:{mname}')
            item_parts.append(f"{pick['item_id']}:{pick['count']}")
        sources_str = ','.join(src_parts)
        items_str = ','.join(item_parts)
        maps_str = quest.get('zone', '').replace('/', ',')
        party_share = 'inventory'
        npc, _mmap, _x, _y = ARC_HUBS.get(quest.get('arc', 0), ('Quartermaster Wynne', '', 0, 0))
        rows.append(f'{qid}\t{name}\t{obj_type}\t{sources_str}\t{items_str}\t{maps_str}\t{party_share}\t{npc}\trequired\tinventory\t0')
    return '\n'.join(rows) + '\n'


def render_hunt_guidance(master):
    """quest_id \t npc \t area \t steps"""
    rows = ['# schema=1']
    for quest in master['quests']:
        qid = quest['id']
        npc, _mmap, _x, _y = ARC_HUBS.get(quest.get('arc', 0), ('Quartermaster Wynne', '', 0, 0))
        area = readable_area(quest.get('zone', ''))
        item_names = [p['item_name'] for p in quest['items']]
        if len(item_names) == 1:
            item_list_str = item_names[0]
        elif len(item_names) == 2:
            item_list_str = f"{item_names[0]} and {item_names[1]}"
        else:
            item_list_str = ", ".join(item_names[:-1]) + f", and {item_names[-1]}"
        step1 = f"Bring {item_list_str}"
        step2 = f"Turn in to {npc}"
        steps = f"{step1}|{step2}"
        rows.append(f'{qid}\t{npc}\t{area}\t{steps}')
    # Include story guidance fixture
    rows.append('20050\tFountain\tProntera\tSpeak to the fountain keeper')
    return '\n'.join(rows) + '\n'


def load_campaign_flags():
    """Return the canonical campaign flags declared by the server helpers."""
    text = open(CAMPAIGN_FLAGS, encoding='utf-8', errors='replace').read()
    # dm_flags.txt is the reset/diagnostic registry for campaign state. Keeping
    # the generator tied to that registry catches stale client reveal gates
    # without trying to infer state from arbitrary script variable references.
    return set(re.findall(r'DM_ClearFlag",\s*"(dm_[a-z0-9_]+)"', text))


def story_steps():
    """Arc 1 story beats mirrored from act_01/arc_01_prontera.txt."""
    return [
        'wynne_start\tQuartermaster Wynne\tThe fountain hums and the south road is unsafe.\tAsk Tibbets, the mother, or inspect the painted sluice.\ttibbets|mother|sluice\trevealed\tdm_arc01_started',
        'mother\tFrightened Mother\tMira followed the gray bread-man from the south-gate soup line.\tFind Mira before choosing how to rescue her.\tmira\thidden\tdm_arc01_child_found',
        'mira\tMira\tThe bread-man wears a goat ring and the water is a song.\tReturn to her mother; the drawing names the next sign.\tmother\thidden\tdm_arc01_child_found',
        'sluice\tPainted Sluice\tA goat-head and copper-smelling paint lead down into the water.\tFind a second sign from Tibbets or Mira.\ttibbets|mira\thidden\tdm_arc01_clue_mask:1',
        'tibbets\tTibbets the Keeper\tThe gray almsman and Deacon Holt use the lowest chamber.\tObtain the tide-wheel and drain the chamber.\tdrain\thidden\tdm_arc01_clue_mask:4',
        'drain\tTide-Wheel\tThe flooded Listening Chamber can be made dry.\tDrain the chamber, then speak to Hlin at the binding stone if desired.\tbinding|holt\thidden\tdm_arc01_chamber_drained',
        "binding\tBinding Stone\tHolt's chalk names the binding word Hlin.\tApply the word before confronting the conduit.\tholt\thidden\tdm_arc01_binding_applied",
        'holt\tDeacon Holt\tThe Deviruchi is chained to the goat-head conduit.\tResolve the encounter, then return to Wynne.\twynne\thidden\tdm_arc01_holt_approach',
    ]


def validate_story_reveal_conditions(flags):
    """Reject story gates that do not correspond to a server campaign flag."""
    problems = []
    for row in story_steps():
        fields = row.split('\t')
        if len(fields) != 7:
            problems.append('story %s: expected 7 tab-separated fields' % (fields[0],))
            continue
        condition = fields[6]
        if condition == 'always':
            continue
        match = re.fullmatch(r'(dm_[a-z0-9_]+)(?::([1-9][0-9]*))?', condition)
        if not match:
            problems.append('story %s: invalid reveal condition %r' % (fields[0], condition))
            continue
        flag = match.group(1)
        if flag not in flags:
            problems.append('story %s: reveal flag %s is not declared in %s'
                            % (fields[0], flag, os.path.relpath(CAMPAIGN_FLAGS, ROOT)))
    return problems


def validate_story_shape():
    """Keep the generated Arc 1 story graph complete and navigable."""
    rows = story_steps()
    problems = []
    ids = []
    for row in rows:
        fields = row.split('\t')
        if len(fields) != 7:
            continue
        step_id, speaker, clue, action, next_lead, visibility, _condition = fields
        ids.append(step_id)
        if not all((step_id, speaker, clue, action, next_lead)):
            problems.append('story %s: speaker, clue, action, and next lead are required' % (step_id or '<missing>',))
        if visibility not in ('revealed', 'hidden'):
            problems.append('story %s: invalid visibility %r' % (step_id, visibility))
    if len(ids) != len(set(ids)):
        problems.append('story: duplicate step id')
    known = set(ids)
    for row in rows:
        fields = row.split('\t')
        if len(fields) != 7:
            continue
        step_id, _speaker, _clue, _action, next_lead, _visibility, _condition = fields
        for lead in next_lead.split('|'):
            # The final Arc 1 lead returns to Wynne, whose story row is the
            # initial `wynne_start` beat rather than a second step.
            if lead not in known and lead != 'wynne':
                problems.append('story %s: next lead %s is not a story step' % (step_id, lead))
    revealed = [row for row in rows if len(row.split('\t')) == 7 and row.split('\t')[5] == 'revealed']
    if len(revealed) != 1 or revealed[0].split('\t')[0] != 'wynne_start':
        problems.append('story: exactly wynne_start must be initially revealed')
    return problems


def render_story_steps(_master):
    """Arc 1 story beats mirrored from act_01/arc_01_prontera.txt."""
    return '\n'.join([
        '# schema=1',
        '# id\tspeaker\tclue\tremaining action\tnext lead\tvisibility\tauthoritative reveal condition',
    ] + story_steps()) + '\n'


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
    mobs = load_mob_db()
    items = load_item_db()
    spawns = load_spawns()
    problems = derive(master, mobs, items, spawns)
    problems.extend(validate_story_reveal_conditions(load_campaign_flags()))
    problems.extend(validate_story_shape())
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
        (KORANGAR_LOC, render_locations(master)),
        (KORANGAR_HUNT_OBJ, render_hunt_objectives(master, mobs)),
        (KORANGAR_HUNT_GUIDE, render_hunt_guidance(master)),
        (KORANGAR_STORY, render_story_steps(master)),
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
        print('OK - hunt artifacts match db/dm_hunt_db.json.')
        return 0

    for path, want in artifacts:
        if os.path.exists(path) and open(path, encoding='utf-8').read() == want:
            continue
        open(path, 'w', encoding='utf-8').write(want)
        print('wrote %s' % os.path.relpath(path, ROOT))
    return 0


if __name__ == '__main__':
    sys.exit(main())
