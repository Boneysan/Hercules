#!/usr/bin/env python3
"""
campaign_quest_merge.py

Helper to merge the Seal Cascade campaign quest journal entries
into a decompiled OngoingQuestInfoList_True_EN.lua (or similar).

Usage examples:

  # Just print the addon blocks (for manual copy-paste)
  python3 tools/campaign_quest_merge.py --print

  # Patch a decompiled .lua file in place (creates .bak)
  python3 tools/campaign_quest_merge.py --patch /path/to/decompiled_OngoingQuestInfoList_True_EN.lua

  # Output a ready standalone addon file
  python3 tools/campaign_quest_merge.py --output /tmp/campaign_quests_only.lua

The script prefers planning/SealCascade_QuestList_addon.lua if present,
otherwise falls back to planning/campaign_quest_journal_entries.lua .

After patching, recompile the .lua to .lub using your usual RO lub tools
and distribute to the client.
"""

import argparse
import os
import re
import shutil
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
ADDON_PATH = os.path.join(REPO_ROOT, "planning", "SealCascade_QuestList_addon.lua")
SOURCE_PATH = os.path.join(REPO_ROOT, "planning", "campaign_quest_journal_entries.lua")

CAMPAIGN_ID_START = 20000
CAMPAIGN_ID_END = 20234

def find_questlist_blocks(text):
    """Extract all QuestList[ID] = { ... } blocks."""
    # Match blocks starting with QuestList[NNNN] = {
    pattern = re.compile(
        r'(QuestList\s*\[\s*(\d+)\s*\]\s*=\s*\{.*?\n\s*\})',
        re.DOTALL
    )
    blocks = {}
    for m in pattern.finditer(text):
        qid = int(m.group(2))
        blocks[qid] = m.group(1).rstrip() + "\n"
    return blocks

def load_campaign_blocks():
    """Load the campaign quest blocks from the best available source."""
    for path in (ADDON_PATH, SOURCE_PATH):
        if os.path.exists(path):
            with open(path, encoding="utf-8", errors="replace") as f:
                text = f.read()
            all_blocks = find_questlist_blocks(text)
            campaign = {k: v for k, v in all_blocks.items() if CAMPAIGN_ID_START <= k <= CAMPAIGN_ID_END}
            if campaign:
                print(f"[info] Loaded {len(campaign)} campaign entries from {os.path.relpath(path, REPO_ROOT)}")
                return campaign
    print("[error] Could not find campaign quest blocks in planning/ files.")
    sys.exit(1)

def print_blocks(blocks):
    print("QuestList = QuestList or {}")
    print()
    for qid in sorted(blocks.keys()):
        print(blocks[qid])

def patch_file(target_path, blocks, backup=True):
    if not os.path.exists(target_path):
        print(f"[error] Target file not found: {target_path}")
        sys.exit(1)

    with open(target_path, encoding="utf-8", errors="replace") as f:
        original = f.read()

    # Find existing QuestList table or the or {} declaration
    questlist_decl = re.search(r'QuestList\s*=\s*QuestList\s+or\s*\{\}', original)
    if not questlist_decl:
        # Try to find any QuestList assignment
        questlist_decl = re.search(r'QuestList\s*=\s*\{', original)

    if not questlist_decl:
        print("[warn] Could not find 'QuestList = QuestList or {}' or similar in target.")
        print("       Appending the campaign blocks at the end instead.")
        new_content = original.rstrip() + "\n\n-- === Seal Cascade Campaign Quests (auto-merged) ===\n"
        new_content += "QuestList = QuestList or {}\n\n"
        for qid in sorted(blocks):
            new_content += blocks[qid] + "\n"
    else:
        # Remove any existing campaign-range entries first (to allow clean overwrite)
        cleaned = re.sub(
            rf'QuestList\s*\[\s*({CAMPAIGN_ID_START}|{CAMPAIGN_ID_END}|20[0-2]\d{{2}})\s*\]\s*=\s*\{{\s*.*?\n\s*\}}\s*\n?',
            '',
            original,
            flags=re.DOTALL
        )

        # Insert after the first "QuestList = QuestList or {}" (or the first QuestList = { )
        insert_pos = questlist_decl.end()
        insertion = "\n\n-- === BEGIN Seal Cascade Campaign (20000-20234) ===\n"
        for qid in sorted(blocks.keys()):
            insertion += blocks[qid] + "\n"
        insertion += "-- === END Seal Cascade Campaign ===\n\n"

        new_content = cleaned[:insert_pos] + insertion + cleaned[insert_pos:]

    if backup:
        bak = target_path + ".bak"
        shutil.copy2(target_path, bak)
        print(f"[info] Backup created: {bak}")

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"[success] Patched {len(blocks)} campaign quest entries into {target_path}")
    print("          Remember:")
    print("          - Use latin-1 encoding + CRLF line endings for the .lua before recompiling to .lub")
    print("          - Test in client Quest window (look for @dm warp lines and flavor)")
    print("          - Distribute the .lub (or GRF) to all players.")

def main():
    parser = argparse.ArgumentParser(description="Merge Seal Cascade campaign quests into client quest list lua.")
    parser.add_argument("--print", action="store_true", help="Print the campaign QuestList blocks to stdout")
    parser.add_argument("--patch", metavar="FILE", help="Patch the given decompiled .lua file in place")
    parser.add_argument("--output", metavar="FILE", help="Write only the campaign blocks to a new file")
    args = parser.parse_args()

    blocks = load_campaign_blocks()

    if args.print:
        print_blocks(blocks)
    elif args.patch:
        patch_file(args.patch, blocks)
    elif args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("-- Seal Cascade Campaign QuestList addon (generated)\n")
            f.write("QuestList = QuestList or {}\n\n")
            for qid in sorted(blocks):
                f.write(blocks[qid] + "\n")
        print(f"[success] Wrote {len(blocks)} entries to {args.output}")
    else:
        parser.print_help()
        print("\nQuick start:")
        print("  python3 tools/campaign_quest_merge.py --print")
        print("  python3 tools/campaign_quest_merge.py --patch /path/to/decompiled_questlist.lua")

if __name__ == "__main__":
    main()
