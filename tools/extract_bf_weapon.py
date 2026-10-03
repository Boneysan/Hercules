#!/usr/bin/env python3
"""Extract all skill IDs with BF_WEAPON attack type from Hercules skill_db.conf"""

import re

with open('db/re/skill_db.conf', 'r') as f:
    content = f.read()

# Find all skill entries
skill_pattern = r'\{\s*Id:\s*(\d+)\s+Name:\s*"([^"]+)".*?AttackType:\s*"([^"]+)'
matches = re.findall(skill_pattern, content, re.DOTALL)

weapon_skills = [(sid, name) for sid, name, atype in matches if atype == 'Weapon']
print(f'Found {len(weapon_skills)} BF_WEAPON skills')

# Check if any are missing from the switch
with open('src/map/battle.c', 'r') as f:
    battle = f.read()

# Extract all skill names mentioned in BF_WEAPON cases - match case patterns like "case SM_BASH:"
switch_pattern = r'case\s+([A-Z0-9_]+):'
bf_weapon_cases = re.findall(switch_pattern, battle)
print(f'\nAll skill cases found in battle.c: {len(bf_weapon_cases)}')
print(', '.join(sorted(set(bf_weapon_cases))[:50]))

# Count unique skills handled
unique_skills_in_switch = set()
for case in bf_weapon_cases:
    # Skip non-skill keywords that might match
    if not case.startswith(('SM_', 'MS_', 'AL_', 'PR_', 'KR_', 'BS_', 'HT_', 'FT_', 'AC_', 'MA_',
                             'KN_', 'ML_', 'MER_', 'TF_', 'AS_', 'MC_', 'NV_', 'RG_', 'SO_',
                             'LG_', 'PG_', 'NJ_', 'SU_', 'WS_', 'WC_', 'SG_', 'WA_', 'DP_')):
        continue
    unique_skills_in_switch.add(case)

print(f'\nUnique skill identifiers in BF_WEAPON switch: {len(unique_skills_in_switch)}')
print(', '.join(sorted(unique_skills_in_switch)[:60]))

# Find unmapped skills by ID - the skill names from skill_db might differ from case labels
mapped_ids = set()
for sid, name in weapon_skills:
    # Convert name to expected case label format (SM_BASH style)
    prefix = name.split('_')[0] if '_' in name else ''
    # Check if this skill's name or a variation appears in the cases
    if any(case == name for case in bf_weapon_cases):
        mapped_ids.add(sid)
    elif any(case.startswith(prefix + '_') and name.replace('_', '') == case.replace('_', '')
             for case in bf_weapon_cases):
        mapped_ids.add(sid)

# Build a more comprehensive mapping by checking prefixes and patterns
print(f'\nSkills found via direct match: {len(mapped_ids)}')

# Better approach: extract all skill IDs mentioned in the BF_WEAPON section
bf_weapon_section = battle[battle.find('case BF_WEAPON:'):battle.find('case BF_BOW:', battle.find('case BF_WEAPON:'))]
skill_id_pattern = r'Id:\s*(\d+)'
section_skill_ids = re.findall(skill_id_pattern, bf_weapon_section)
print(f'\nSkill IDs found in BF_WEAPON section of battle.c: {len(set(section_skill_ids))}')

# Cross-reference by building a name->id map from skill_db
name_to_id = {name: sid for sid, name in weapon_skills}

# Now check which skills from the switch are mapped
switch_skills_mapped = set()
for case in bf_weapon_cases:
    # Skip non-skill keywords
    if not any(case.startswith(p) for p in ['SM_', 'MS_', 'AL_', 'PR_', 'KR_', 'BS_', 'HT_',
                                             'FT_', 'AC_', 'MA_', 'KN_', 'ML_', 'MER_',
                                             'TF_', 'AS_', 'MC_', 'NV_', 'RG_', 'SO_',
                                             'LG_', 'PG_', 'NJ_', 'SU_', 'WS_', 'WC_', 'SG_',
                                             'WA_', 'DP_', 'ST_', 'RF_', 'RE_', 'SC_', 'AB_',
                                             'PA_', 'MI_', 'IM_', 'IN_', 'LO_', 'SA_', 'CW_',
                                             'MD_', 'GD_', 'CH_', 'AM_', 'MO_', 'DL_', 'NV_']):
        continue
    if case in name_to_id:
        switch_skills_mapped.add((case, name_to_id[case]))

print(f'\nMapped skills (by name match): {len(switch_skills_mapped)}')

# Report unmapped skills
unmapped = [(sid, name) for sid, name in weapon_skills
            if not any(case == name or case.replace('_', '') == name.replace('_', '')
                      for case in bf_weapon_cases)]
print(f'\nUnmapped BF_WEAPON skills: {len(unmapped)}')
if len(unmapped) <= 50:
    for sid, name in unmapped:
        print(f'{sid}: {name}')
else:
    for sid, name in unmapped[:30]:
        print(f'{sid}: {name}')
    print(f'... and {len(unmapped) - 30} more')
