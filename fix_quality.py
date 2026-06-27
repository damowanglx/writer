#!/usr/bin/env python3
"""Fix comma quality issues from automated —— → ， replacement.

Fixes:
1. Lines ending with "，" that should end with "。" (sentence terminators)
2. Single "—" (U+2014) that should be "——" or removed
3. Dialogue that ends with "," instead of proper punctuation
"""

import os
import re

BASE_DIR = r"D:/workspace/writer/恐怖小说专题/小说库/收容失控"

def fix_trailing_commas(text):
    """Fix lines ending with ， that should end with 。"""
    lines = text.split('\n')
    result = []

    for i, line in enumerate(lines):
        stripped = line.rstrip()

        # Skip empty lines and headers
        if not stripped or stripped.startswith('#'):
            result.append(line)
            continue

        # Check if line ends with "，" or "，"
        if stripped.endswith('，') or stripped.endswith(','):

            # Check if next line continues the thought
            # If next line is empty or a new paragraph, current line should end with 。
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if not next_line or next_line.startswith('"') or next_line.startswith('「'):
                    # Next line is new paragraph or dialogue - end current with 。
                    stripped = stripped[:-1] + '。'
                elif stripped.endswith('，'):
                    # Check if this is in dialogue (inside quotes)
                    # Count quotes to determine
                    pass  # Keep as is for now
                else:
                    pass  # Keep as is
            else:
                # Last line - replace with 。
                stripped = stripped[:-1] + '。'

        result.append(stripped)

    return '\n'.join(result)


def fix_partial_dashes(text):
    """Fix single — that aren't part of ——."""
    # Replace remaining single — with —— (only if they look like dashes, not in other contexts)
    # A single — followed by Chinese text
    text = re.sub(r'(?<![—])—(?![—])(?=[一-鿿])', '——', text)
    text = re.sub(r'(?<=[一-鿿])—(?![—])(?![一-鿿])', '——', text)
    return text


def fix_incomplete_sentences(text):
    """Fix sentences that end with ， where —— was removed.

    Pattern: text ends with ， followed by newline + new sentence
    These should end with 。instead.
    """
    # A line ending with ， where the next line starts with a capital letter or Chinese
    # and is a complete new thought
    lines = text.split('\n')
    result = []

    for i, line in enumerate(lines):
        stripped = line.rstrip()

        if stripped.endswith('，') and not stripped.endswith('——'):
            # Check if this looks like an incomplete sentence
            # (short phrase ending with ，)
            if len(stripped) < 15 and not any(c in stripped for c in '？！；：'):
                # Very short line ending with ， - likely a fragment
                # Check next line
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not next_line.startswith('"') and not next_line.startswith('「'):
                        # Next line continues the thought in a new line
                        # This is likely a line break that should be joined
                        pass  # Leave for now - joining is too aggressive

        result.append(stripped)

    return '\n'.join(result)


def process_file(filepath):
    """Process a single file for quality issues."""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    original = text

    # Fix partial dashes
    text = fix_partial_dashes(text)

    # Fix trailing commas
    text = fix_trailing_commas(text)

    if text != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        return True

    return False


def main():
    vol4_dir = os.path.join(BASE_DIR, "第四卷")
    vol5_dir = os.path.join(BASE_DIR, "第五卷")

    changed = 0
    for vol_dir in [vol4_dir, vol5_dir]:
        for fname in sorted(os.listdir(vol_dir)):
            if fname.endswith('.md') and fname.startswith('第'):
                filepath = os.path.join(vol_dir, fname)
                if process_file(filepath):
                    print(f"Fixed: {fname}")
                    changed += 1

    print(f"\nTotal files fixed: {changed}")


if __name__ == '__main__':
    main()
