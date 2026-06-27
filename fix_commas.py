#!/usr/bin/env python3
"""Fix comma overload from mechanical —— → ， replacement.

Target: Remove commas that create choppy reading while preserving
necessary punctuation. Focus on patterns like:
- "是，它，自己，向上" → "是它自己向上"
- Commas between short words/phrases that should flow together
"""

import os
import re

BASE_DIR = r"D:/workspace/writer/恐怖小说专题/小说库/收容失控"

def fix_comma_overload(text):
    """Fix excessive commas from mechanical —— → ， replacement."""
    lines = text.split('\n')
    result_lines = []

    for line in lines:
        if not line.strip() or line.startswith('#'):
            result_lines.append(line)
            continue

        # Skip lines that are purely dialogue (inside quotes)
        # Check if this is a pure-dialogue line
        stripped = line.strip()
        if stripped.startswith('"') and stripped.endswith('"'):
            # Pure dialogue - be more careful with commas inside
            # But still fix some comma overload patterns
            line = fix_dialogue_commas(line)
            result_lines.append(line)
            continue

        # Fix narrative text comma overload
        line = fix_narrative_commas(line)
        result_lines.append(line)

    return '\n'.join(result_lines)

def fix_narrative_commas(line):
    """Fix comma overload in narrative text."""
    # Pattern 1: 是，X (single char after comma after 是)
    # e.g., "是，它自己" → "是它自己"
    line = re.sub(r'是，([^，。\n]{1,3})([，。\n])', r'是\1\2', line)
    line = re.sub(r'是，([^，。\n]{1,5})$', r'是\1', line)

    # Pattern 2: Redundant commas between single-character words
    # e.g., "它，自己" → "它自己"
    # Single char + ，+ single char (not at end of clause)
    line = re.sub(r'([^\s，。、：；？！\n])，([^\s，。、：；？！\n]{1,2})([，。、：；？！\n])', r'\1\2\3', line)

    # Pattern 3: Verb + ，+ object (when object is short)
    # e.g., "把地板砖，盖了回去" → "把地板砖盖了回去"
    # But only when the verb and object are closely related
    # This is hard to do reliably, so skip complex cases

    # Pattern 4: Remove comma before 然后/接着/之后 when it creates choppy reading
    # But keep it if it helps readability - often these are fine

    # Pattern 5: Subject-verb comma separation
    # e.g., "她，没有哭" → "她没有哭" (when subject is short)
    line = re.sub(r'([^，。\n]{1,3})，([^，。\n]{1,2}着|了|过|在|没有|不|能|会|要|已经|正在)', r'\1\2', line)

    # Pattern 6: Excessive adjective comma lists that should flow
    # "均匀的，稳定的" → "均匀的稳定的" (keep last comma if followed by 的)
    # Actually these are fine as style choices - leave them

    # Pattern 7: Clean up double commas
    line = line.replace('，，', '，')
    line = line.replace('，。', '。')
    line = line.replace('，，', '，')

    return line


def fix_dialogue_commas(line):
    """Fix comma overload inside dialogue."""
    # Same patterns as narrative but more conservative
    # Only fix the most egregious cases

    # Fix: "我，觉得" → "我觉得" (short subject + verb)
    line = re.sub(r'([我你他她它])，([^，。\n]{1,2})', r'\1\2', line)

    # Fix: "的，时候" → "的时候"
    line = re.sub(r'的，([^，。\n]{1,2})', r'的\1', line)

    # Fix: "在，那" → "在那"
    line = re.sub(r'(在|从|到|向|把|被|让|给)，([^，。\n]{1,2})', r'\1\2', line)

    return line


def count_emdash(text):
    return text.count('——')

def process_file(filepath):
    """Process a single file for comma quality."""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    original_dashes = count_emdash(text)
    original_commas = text.count('，')

    new_text = fix_comma_overload(text)

    new_commas = new_text.count('，')
    new_dashes = count_emdash(new_text)

    # Only write if changes made
    if new_commas != original_commas or new_dashes != original_dashes:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_text)
        return True, original_dashes, new_dashes, original_commas, new_commas

    return False, original_dashes, new_dashes, original_commas, new_commas


def main():
    """Process all files in Vol4 and Vol5."""
    all_files = []

    for vol in ["第四卷", "第五卷"]:
        vol_dir = os.path.join(BASE_DIR, vol)
        for fname in sorted(os.listdir(vol_dir)):
            if fname.endswith('.md') and fname.startswith('第'):
                all_files.append(os.path.join(vol_dir, fname))

    total_changed = 0
    print(f"{'File':<50} {'破折号':>8} {'→':>4} {'':>4} {'逗号':>8} {'→':>4} {'变化':>8}")
    print("=" * 90)

    for filepath in all_files:
        fname = os.path.basename(filepath)
        changed, orig_d, new_d, orig_c, new_c = process_file(filepath)
        if changed:
            total_changed += 1
            delta_c = new_c - orig_c
            print(f"{fname:<50} {orig_d:>4} → {new_d:<4} {orig_c:>6} → {new_c:<6} {delta_c:>+8}")

    print("=" * 90)
    print(f"Total files changed: {total_changed}")


if __name__ == '__main__':
    main()
