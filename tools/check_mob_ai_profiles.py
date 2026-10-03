#!/usr/bin/env python3
"""Static checks for the monster AI pilot layer.

Exists because on 2026-10-02 `mob_ai_profile_db.conf` was found to have NEVER
loaded (a working-directory-relative path in src/map/mob.c). Every consistency
checker passed, the server booted clean, and "No map-scoped mob AI profiles
configured." sat in two boot logs. A config that no one reads is invisible to
every check that only reads the config. This tool therefore also checks the
BOOT LOG, which is the only evidence the server actually loaded it.

    tools/check_mob_ai_profiles.py                 # static checks only
    tools/check_mob_ai_profiles.py --boot-log LOG  # + require the server's own "Read N" line

Checks (mirroring the bounds enforced in mob_read_ai_profiles):
  * every profile has Map, Monster, Role; Role is a known role
  * role parameters are inside the loader's accepted ranges
  * Monster names an existing mob_db SpriteName; Map is a known map
  * no duplicate (Map, Monster); at most MAX_MOB_AI_PROFILES (64)
  * the pilot skill file's monsters and skills exist
  * mob_pilot_version is declared (stock 0) and set deliberately in the import
"""

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILES = os.path.join(ROOT, 'db', 're', 'mob_ai_profile_db.conf')
PILOT_SKILLS = os.path.join(ROOT, 'db', 're', 'mob_pilot_skill_db.conf')
MOB_DB = [os.path.join(ROOT, 'db', 're', 'mob_db.conf'), os.path.join(ROOT, 'db', 'mob_db2.conf')]
SKILL_DB = os.path.join(ROOT, 'db', 're', 'skill_db.conf')
MAP_INDEX = [os.path.join(ROOT, 'db', 're', 'map_index.txt'), os.path.join(ROOT, 'db', 'map_index.txt')]
BATTLE_STOCK = os.path.join(ROOT, 'conf', 'map', 'battle', 'monster.conf')
BATTLE_IMPORT = os.path.join(ROOT, 'conf', 'import', 'battle.conf')

MAX_PROFILES = 64
# role -> {field: (low, high)}; every listed field is required, as in the loader.
ROLES = {
    'aggressor': {},
    'coward': {'HpThreshold': (1, 99), 'FleeDistance': (1, 10), 'Cooldown': (1000, 60000)},
    'rangedkeeper': {'PreferredRange': (2, 8), 'Cooldown': (500, 10000)},
    'skirmisher': {'HitThreshold': (2, 10), 'StepDistance': (2, 5), 'Cooldown': (1000, 15000)},
}


def read(path):
    with open(path, encoding='utf-8', errors='replace') as handle:
        return handle.read()


def strip_comments(text):
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    return re.sub(r'//[^\n]*', '', text)


def parse_profiles(text):
    entries = []
    for block in re.findall(r'\{([^{}]*)\}', strip_comments(text)):
        fields = {}
        for key, value in re.findall(r'(\w+)\s*:\s*("(?:[^"\\]|\\.)*"|[^\s,]+)', block):
            fields[key] = value.strip('"')
        if fields:
            entries.append(fields)
    return entries


def mob_names():
    names = set()
    for path in MOB_DB:
        if os.path.exists(path):
            names.update(re.findall(r'SpriteName:\s*"(\w+)"', strip_comments(read(path))))
    return names


def skill_names():
    return set(re.findall(r'Name:\s*"(\w+)"', strip_comments(read(SKILL_DB))))


def map_names():
    names = set()
    for path in MAP_INDEX:
        if os.path.exists(path):
            for line in read(path).splitlines():
                token = line.split('//')[0].split()
                if token:
                    names.add(token[0].lower().removesuffix('.gat'))
    return names


def check_profiles(problems):
    entries = parse_profiles(read(PROFILES))
    mobs = mob_names()
    maps = map_names()
    seen = set()
    valid = 0
    if len(entries) > MAX_PROFILES:
        problems.append('%d profiles exceeds the loader maximum of %d' % (len(entries), MAX_PROFILES))
    for index, entry in enumerate(entries, 1):
        label = 'profile #%d (%s on %s)' % (index, entry.get('Monster', '?'), entry.get('Map', '?'))
        ok = True
        for required in ('Map', 'Monster', 'Role'):
            if required not in entry:
                problems.append('%s: missing %s' % (label, required))
                ok = False
        if not ok:
            continue
        role = entry['Role'].lower()
        if role not in ROLES:
            problems.append('%s: unknown role %r' % (label, entry['Role']))
            continue
        for field, (low, high) in ROLES[role].items():
            if field not in entry:
                problems.append('%s: %s requires %s' % (label, entry['Role'], field))
                ok = False
                continue
            try:
                value = int(entry[field])
            except ValueError:
                problems.append('%s: %s is not an integer' % (label, field))
                ok = False
                continue
            if not low <= value <= high:
                problems.append('%s: %s=%d outside the loader range %d..%d' % (label, field, value, low, high))
                ok = False
        if entry['Monster'] not in mobs:
            problems.append('%s: monster %r is not in mob_db' % (label, entry['Monster']))
            ok = False
        if maps and entry['Map'].lower() not in maps:
            problems.append('%s: map %r is not in map_index' % (label, entry['Map']))
            ok = False
        key = (entry['Map'].lower(), entry['Monster'])
        if key in seen:
            problems.append('%s: duplicate (Map, Monster)' % label)
            ok = False
        seen.add(key)
        if ok:
            valid += 1
    return valid


def check_pilot_skills(problems):
    if not os.path.exists(PILOT_SKILLS):
        problems.append('db/re/mob_pilot_skill_db.conf is missing')
        return
    text = strip_comments(read(PILOT_SKILLS))
    mobs = mob_names()
    skills = skill_names()
    # Monster blocks sit one level inside mob_skill_db: ({ NAME: { SKILL: {...} ... } })
    for mob in re.findall(r'^\t(\w+):\s*\{', text, flags=re.M):
        if mob not in mobs:
            problems.append('pilot skills: monster %s is not in mob_db' % mob)
    for skill in re.findall(r'^\t\t(\w+):\s*\{', text, flags=re.M):
        if skill not in skills:
            problems.append('pilot skills: skill %s is not in skill_db' % skill)


def check_switch(problems):
    stock = read(BATTLE_STOCK) if os.path.exists(BATTLE_STOCK) else ''
    if not re.search(r'^\s*mob_pilot_version\s*:\s*0\b', stock, flags=re.M):
        problems.append('conf/map/battle/monster.conf must declare mob_pilot_version: 0 (stock default)')
    imported = read(BATTLE_IMPORT) if os.path.exists(BATTLE_IMPORT) else ''
    if not re.search(r'^\s*mob_pilot_version\s*:\s*[01]\b', imported, flags=re.M):
        problems.append('conf/import/battle.conf does not set mob_pilot_version deliberately')


def check_boot_log(log_path, expected, problems):
    text = read(log_path).replace('\r', '\n')
    match = re.search(r'Read (\d+) map-scoped mob AI profiles', text)
    if 'No map-scoped mob AI profiles configured' in text:
        problems.append('boot log: the server found NO profile file (the path bug class): %s' % log_path)
    elif not match:
        problems.append('boot log: no "Read N map-scoped mob AI profiles" line in %s' % log_path)
    elif int(match.group(1)) != expected:
        problems.append('boot log: server read %s profiles but the file has %d valid ones' % (match.group(1), expected))
    for line in text.splitlines():
        if 'mob_ai_profile_db:' in line and 'Warning' in line:
            problems.append('boot log: ' + line.strip())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--boot-log', help='a map-server boot log that must show the profiles were actually read')
    args = parser.parse_args()
    problems = []
    valid = check_profiles(problems)
    check_pilot_skills(problems)
    check_switch(problems)
    if args.boot_log:
        check_boot_log(args.boot_log, valid, problems)
    if problems:
        print('FAIL - %d problem(s):' % len(problems), file=sys.stderr)
        for problem in problems:
            print('  ' + problem, file=sys.stderr)
        return 1
    print('OK - %d AI profiles valid%s.' % (valid, '; boot log confirms the server read them' if args.boot_log else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
