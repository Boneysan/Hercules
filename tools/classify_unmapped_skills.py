#!/usr/bin/env python3
"""Classify unmapped BF_WEAPON skills by prefix family"""

import re
from collections import defaultdict

# Read skill_db.conf to get all BF_WEAPON skills with their IDs
with open('db/re/skill_db.conf', 'r') as f:
    content = f.read()

# Parse skill entries - each entry starts with "skill_db: (" and contains Id:, Name:, AttackType:
# We need to match only actual skill blocks that start with "Id: <integer>"
# Use a more specific pattern that requires the block to start with an integer ID
skill_pattern = r'\{[^}]*\bId:\s*(\d+)[^}]*\bName:\s*"([^"]+)".*?\bAttackType:\s*"([^"]+)'
matches = re.findall(skill_pattern, content, re.DOTALL)

weapon_skills_by_id = {}
for sid_str, name, atype in matches:
    if atype == 'Weapon':
        weapon_skills_by_id[int(sid_str)] = name

print(f'Total BF_WEAPON skills in skill_db.conf: {len(weapon_skills_by_id)}')

# Read battle.c and extract all case labels from the BF_WEAPON switch
with open('src/map/battle.c', 'r') as f:
    battle = f.read()

bf_weapon_start = battle.find('case BF_WEAPON:')
bf_weapon_end = battle.find('case BF_BOW:', bf_weapon_start)
bf_weapon_section = battle[bf_weapon_start:bf_weapon_end]

# Extract skill names from case labels (e.g., "SM_BASH", "MS_MAGNUM")
case_pattern = r'case\s+([A-Z0-9_]+):'
all_cases = re.findall(case_pattern, bf_weapon_section)

print(f'Total case labels in BF_WEAPON section: {len(all_cases)}')

# Filter to skill-like identifiers - these prefixes are used by actual skills
valid_prefixes = ['SM_', 'MS_', 'AL_', 'PR_', 'KR_', 'BS_', 'HT_', 'FT_', 'AC_', 'MA_',
                  'KN_', 'ML_', 'MER_', 'TF_', 'AS_', 'MC_', 'NV_', 'RG_', 'SO_',
                  'LG_', 'PG_', 'NJ_', 'SU_', 'WS_', 'WC_', 'SG_', 'WA_', 'DP_',
                  'ST_', 'RF_', 'RE_', 'SC_', 'AB_', 'PA_', 'MI_', 'IM_', 'IN_',
                  'LO_', 'SA_', 'CW_', 'MD_', 'GD_', 'CH_', 'AM_', 'MO_', 'DL_',
                  'BM_', 'CN_', 'EX_', 'WE_', 'ZC_', 'MC2', 'AM2', 'HT2',
                  'LK_', 'GN_', 'RA_', 'RK_', 'EL_', 'NC_', 'CR_', 'GC_', 'SJ_',
                  'KO_', 'TF_', 'HT_', 'CH_', 'ASC_', 'SN_', 'SG_', 'SC_',
                  'SA_', 'BA_', 'DC_', 'PR_', 'HW_', 'CG_', 'ALL_', 'WL_', 'OB_', 'HLIF_', 'HLM_']

skill_cases = set()
for case in all_cases:
    if any(case.startswith(p) for p in valid_prefixes):
        skill_cases.add(case)

print(f'Case labels filtered to skill prefixes: {len(skill_cases)}')

# Build name->id map from skill_db
name_to_id = {}
for sid, name in weapon_skills_by_id.items():
    name_to_id[name] = sid

mapped_ids = set()
unmapped_by_case = []

for case_name in skill_cases:
    if case_name in name_to_id:
        mapped_ids.add(name_to_id[case_name])
    else:
        # Try without underscores comparison
        plain_name = case_name.replace('_', '')
        found = False
        for sid, name in weapon_skills_by_id.items():
            if name.replace('_', '') == plain_name:
                mapped_ids.add(sid)
                found = True
                break
        if not found:
            unmapped_by_case.append(case_name)

print(f'Skills with explicit handlers (mapped): {len(mapped_ids)}')
print(f'Skill case labels without matching entry: {len(unmapped_by_case)}')

# The unmapped skills are those in weapon_skills_by_id but not in mapped_ids
unmapped_skills = [(sid, name) for sid, name in weapon_skills_by_id.items() if sid not in mapped_ids]
print(f'Unmapped BF_WEAPON skills (by ID): {len(unmapped_skills)}')

# Group by prefix
prefix_groups = defaultdict(list)
for sid, name in unmapped_skills:
    # Extract prefix from skill name
    parts = name.split('_')
    if len(parts) >= 2:
        prefix = parts[0] + '_'
    else:
        prefix = name + '_'
    prefix_groups[prefix].append((sid, name))

print(f'\nUnmapped skills grouped by prefix:')
for prefix in sorted(prefix_groups.keys(), key=lambda x: -len(prefix_groups[x])):
    skills = prefix_groups[prefix]
    print(f'\n{prefix}: {len(skills)} skills')
    for sid, name in skills[:10]:
        print(f'  {sid}: {name}')
    if len(skills) > 10:
        print(f'  ... and {len(skills) - 10} more')

# Summary
print('\n\n=== SUMMARY ===')
print(f'Total BF_WEAPON skills: {len(weapon_skills_by_id)}')
print(f'Mapped with explicit handlers: {len(mapped_ids)}')
print(f'Unmapped (use weapon_unknown): {len(unmapped_skills)}')
print(f'Skill case labels in switch: {len(skill_cases)}')
