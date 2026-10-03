#!/usr/bin/env python3
"""Parse sc_config.conf and group status effects by CalcFlags patterns."""

from pathlib import Path
import re
from collections import defaultdict


def parse_sc_config():
    sc_config = Path(__file__).parent / 'sc_config.conf'
    content = sc_config.read_text(encoding='utf-8', errors='replace')

    lines = content.split('\n')
    entries = []
    current_entry = None
    in_flags = False
    in_calcflags = False
    brace_depth = 0

    for line in lines:
        # Remove comments
        if '//' in line:
            line = line.split('//')[0]
        line = line.strip()

        if not line:
            continue

        # Check for SC_XXX: {
        match = re.match(r'^(SC_\w+):\s*\{\s*$', line)
        if match and current_entry is None:
            current_entry = {
                'name': match.group(1),
                'flags': {},
                'calcflags': [],
                'icon': None,
                'skill': None
            }
            brace_depth = 1
            in_flags = False
            in_calcflags = False
            continue

        # Track braces for nested sections
        if '{' in line:
            brace_depth += line.count('{')
        if '}' in line:
            brace_depth -= line.count('}')

        # Check if we've closed the main block
        if brace_depth == 0 and current_entry is not None:
            entries.append(current_entry)
            current_entry = None
            continue

        if current_entry is None:
            continue

        # Parse section headers
        if line.startswith('Flags:'):
            in_flags = True
            in_calcflags = False
            continue
        elif line.startswith('CalcFlags:'):
            in_calcflags = True
            in_flags = False
            continue
        else:
            # Inside Flags or CalcFlags sections, or top-level fields

            if in_flags:
                for flag in ['Buff', 'Debuff', 'NoDeathReset', 'NoSave', 'NoDispelReset', 'Visible']:
                    if f'{flag}: true' in line:
                        current_entry['flags'][flag] = True
            elif in_calcflags:
                for cf in ['Str', 'Agi', 'Vit', 'Int', 'Dex', 'Luk',
                           'AtkPerc', 'DefPerc', 'Maxhp', 'Maxsp',
                           'Speed', 'Aspd', 'Hit', 'Flee',
                           'Batk', 'Watk', 'Matk', 'Def', 'Mdef']:
                    if f'{cf}: true' in line:
                        current_entry['calcflags'].append(cf)
            else:
                # Top-level fields (Icon, Skill, etc.)
                match = re.match(r'(\w+):\s*"([^"]*)"', line)
                if match:
                    key, value = match.groups()
                    if key in ['Icon', 'Skill']:
                        current_entry[key.lower()] = value
                    elif key == 'Duration':
                        # Parse duration: value (optional "second" suffix)
                        m = re.match(r'(\d+)(?:\s*second)?s?', value, re.IGNORECASE)
                        if m:
                            current_entry['duration'] = int(m.group(1))
                    elif key == 'Icon':
                        current_entry['icon'] = value
                    elif key == 'Skill':
                        current_entry['skill'] = value

    return entries


def main():
    entries = parse_sc_config()

    from collections import defaultdict

    by_calcflags = defaultdict(list)
    for entry in entries:
        cf_tuple = tuple(entry.get('calcflags', []))
        by_calcflags[cf_tuple].append(entry)

    print(f'Total status entries: {len(entries)}')
    print()
    print('Top CalcFlags patterns:')
    for pattern, entries_list in sorted(by_calcflags.items(), key=lambda x: -len(x[1])):
        if len(pattern) > 0:
            print(f'  {list(pattern)}: {len(entries_list)} statuses')
            for e in entries_list[:2]:
                skill = e.get('skill') or 'none'
                icon = e.get('icon') or 'none'
                print(f'    - {e["name"]} (Skill: {skill}, Icon: {icon})')
            if len(entries_list) > 2:
                print(f'    ... and {len(entries_list)-2} more')

    print()
    ungrouped = by_calcflags[tuple()]
    if ungrouped:
        print(f'Entries with no CalcFlags ({len(ungrouped)}):')
        for e in ungrouped[:15]:
            skill = e.get('skill') or 'none'
            icon = e.get('icon') or 'none'
            print(f'  - {e["name"]} (Skill: {skill}, Icon: {icon})')


if __name__ == '__main__':
    main()
