#!/usr/bin/env python3
"""Generate a comprehensive inventory of status effects mapped to skills."""

from pathlib import Path
import re
import json
from collections import defaultdict


def parse_sc_config():
    """Parse sc_config.conf into structured entries."""
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
                        m = re.match(r'(\d+)(?:\s*second)?s?', value, re.IGNORECASE)
                        if m:
                            current_entry['duration'] = int(m.group(1))
                    elif key == 'Icon':
                        current_entry['icon'] = value
                    elif key == 'Skill':
                        current_entry['skill'] = value

    return entries


def load_skills():
    """Load skills.json with AttackType information."""
    # The korangar repo is at a sibling path to Hercules
    skills_path = Path('/Volumes/T7/GitHub/Ragnarok_Online/korangar/docs/skills.json')
    content = skills_path.read_text(encoding='utf-8', errors='replace')
    return json.loads(content)


def load_skill_reviews():
    """Load existing skill formula reviews."""
    path = Path('/Volumes/T7/GitHub/Ragnarok_Online/korangar/tools/skill_formula_reviews.json')
    if not path.exists():
        return {"schema_version": 1, "entries": []}
    content = path.read_text(encoding='utf-8', errors='replace')
    return json.loads(content)


def extract_skill_id_from_name(skill_name):
    """Extract the numeric skill ID from a skill name like 'AL_HEAL' or 'SC_AL_HEAL'."""
    if not skill_name:
        return None

    # Remove SC_ prefix if present
    if skill_name.startswith('SC_'):
        skill_name = skill_name[3:]

    # Map status names to skill IDs using the naming convention
    # Most SC_XXX maps directly to skill XXX in skill_db.conf
    return skill_name


def build_skill_id_to_names(skills_data):
    """Build mappings from skill name/id to full skill info."""
    name_to_skills = defaultdict(list)
    id_to_skills = defaultdict(list)

    for skill in skills_data:
        # Map by AegisName
        if 'AegisName' in skill:
            name_to_skills[skill['AegisName']].append(skill)
        # Map by Name (display name)
        if 'Name' in skill:
            name_to_skills[skill['Name']].append(skill)

        # Map by ID
        if 'Id' in skill:
            id_to_skills[int(skill['Id'])].append(skill)

    return name_to_skills, id_to_skills


def build_status_inventory():
    """Build the complete status inventory."""
    entries = parse_sc_config()
    skills_data = load_skills()
    reviews = load_skill_reviews()

    # Build lookup tables
    name_to_skills, id_to_skills = build_skill_id_to_names(skills_data)

    # Count reviewed skills by skill ID
    reviewed_skill_ids = set()
    for review in reviews['entries']:
        reviewed_skill_ids.update(review.get('skill_ids', []))

    # Build status inventory with skill mappings
    status_inventory = {
        'total_statuses': len(entries),
        'with_skill_mapping': 0,
        'without_skill_mapping': 0,
        'by_attack_type': {},
        'by_calcflags_pattern': {},
        'reviewed_formula_status': [],
        'unreviewed_status_by_priority': []
    }

    # Track by attack type
    for skill in skills_data:
        atype = skill.get('AttackType', 'Unknown')
        if atype not in status_inventory['by_attack_type']:
            status_inventory['by_attack_type'][atype] = {
                'statuses_count': 0,
                'status_entries': []
            }

    # Process each status entry
    for entry in entries:
        skill_name = entry.get('skill') or extract_skill_id_from_name(entry['name'])

        if skill_name:
            skill_ids = name_to_skills.get(skill_name, [])
            if not skill_ids and entry['skill']:
                # Try to parse as numeric ID
                try:
                    sid = int(skill_name)
                    skill_ids = id_to_skills.get(sid, [])
                except ValueError:
                    pass

            if skill_ids:
                status_inventory['with_skill_mapping'] += 1

                for skill in skill_ids:
                    atype = skill.get('AttackType', 'Unknown')
                    entry_copy = dict(entry)
                    entry_copy['mapped_skill_ids'] = [skill.get('Id')]
                    entry_copy['attack_type'] = atype
                    entry_copy['reviewed'] = int(skill.get('Id')) in reviewed_skill_ids

                    status_inventory['by_attack_type'][atype]['statuses_count'] += 1
                    status_inventory['by_attack_type'][atype]['status_entries'].append(entry_copy)

                    if entry_copy['reviewed']:
                        status_inventory['reviewed_formula_status'].append({
                            'status': entry['name'],
                            'skill_id': skill.get('Id'),
                            'attack_type': atype,
                            'calcflags': entry['calcflags']
                        })
                    else:
                        status_inventory['unreviewed_status_by_priority'].append(entry_copy)
            else:
                status_inventory['without_skill_mapping'] += 1
        else:
            status_inventory['without_skill_mapping'] += 1

    # Group by CalcFlags pattern for prioritization
    calcflags_patterns = defaultdict(list)
    for entry in entries:
        cf_tuple = tuple(sorted(entry.get('calcflags', [])))
        calcflags_patterns[cf_tuple].append(entry)

    # Convert to serializable format - use string representation as key
    status_inventory['by_calcflags_pattern'] = {
        str(k): len(v) for k, v in sorted(calcflags_patterns.items(), key=lambda x: -len(x[1]))
    }

    # Sort unreviewed by priority: Weapon > Magic > Misc > Unknown
    priority_order = {'Weapon': 0, 'Magic': 1, 'Misc': 2, 'Unknown': 3}
    status_inventory['unreviewed_status_by_priority'].sort(
        key=lambda x: (priority_order.get(x.get('attack_type', 'Unknown'), 4), x['name'])
    )

    return status_inventory


def write_summary(inventory):
    """Write a human-readable summary."""
    output_path = Path(__file__).parent / 'status_inventory_summary.md'
    lines = []

    lines.append('# Status Effects Inventory')
    lines.append('')
    lines.append(f'Total status effects: {inventory["total_statuses"]}')
    lines.append(f'Statuses with skill mapping: {inventory["with_skill_mapping"]}')
    lines.append(f'Statuses without skill mapping: {inventory["without_skill_mapping"]}')
    lines.append(f'Reviewed formula statuses: {len(inventory["reviewed_formula_status"])}')
    lines.append(f'Unreviewed status effects: {len(inventory["unreviewed_status_by_priority"])}')
    lines.append('')

    lines.append('## By Attack Type Priority')
    lines.append('')
    priority_order = ['Weapon', 'Magic', 'Misc', 'Unknown']

    for atype in priority_order:
        if atype in inventory['by_attack_type']:
            data = inventory['by_attack_type'][atype]
            reviewed_count = sum(1 for e in data['status_entries'] if e.get('reviewed'))
            lines.append(f'### {atype} ({data["statuses_count"]} statuses)')
            lines.append(f'- **Reviewed:** {reviewed_count}')
            lines.append(f'- **Unreviewed:** {data["statuses_count"] - reviewed_count}')
            lines.append('')

    # Top CalcFlags patterns
    lines.append('## Top CalcFlags Patterns')
    lines.append('')
    for pattern, count in list(inventory['by_calcflags_pattern'].items())[:10]:
        cf_str = ', '.join(pattern) if pattern else '(none)'
        lines.append(f'- **{cf_str}:** {count} statuses')
    lines.append('')

    output_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'Wrote summary to {output_path}')


def write_json_inventory(inventory):
    """Write the full inventory as JSON."""
    output_path = Path('/Volumes/T7/GitHub/Ragnarok_Online/korangar/docs/status_inventory.v1.json')
    output_path.write_text(json.dumps(inventory, indent=2), encoding='utf-8')
    print(f'Wrote inventory to {output_path}')


def main():
    inventory = build_status_inventory()
    write_summary(inventory)
    write_json_inventory(inventory)

    # Print quick summary
    print()
    print('=== Quick Summary ===')
    print(f'Total statuses: {inventory["total_statuses"]}')
    print(f'With skill mapping: {inventory["with_skill_mapping"]}')
    print(f'Reviewed formula statuses: {len(inventory["reviewed_formula_status"])}')
    print(f'Unreviewed (priority order): {len(inventory["unreviewed_status_by_priority"])}')

    # Show unreviewed by attack type
    for atype in ['Weapon', 'Magic', 'Misc', 'Unknown']:
        count = inventory['by_attack_type'].get(atype, {}).get('statuses_count', 0)
        reviewed = sum(1 for e in inventory['by_attack_type'].get(atype, {}).get('status_entries', []) if e.get('reviewed'))
        print(f'  {atype}: {count} total, {reviewed} reviewed')


if __name__ == '__main__':
    main()
