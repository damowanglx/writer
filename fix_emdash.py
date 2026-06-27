#!/usr/bin/env python3
"""Fix excessive em-dashes (——) in novel chapters.

Target: 30-50 em-dashes per chapter.
Keep functional ones: dialogue response, trailing off, interruption.
Replace breathing ones: clause separators in narrative.
"""

import os
import re
import sys

BASE_DIR = r"D:/workspace/writer/恐怖小说专题/小说库/收容失控"

# Volume 4 chapters (all need fixing)
VOL4_ALL = sorted(os.listdir(os.path.join(BASE_DIR, "第四卷")))

# Volume 5 chapters: fix those with >50 dashes, except 248-259 (already fixed)
VOL5_ALL = sorted(os.listdir(os.path.join(BASE_DIR, "第五卷")))
# Chapters already fixed <12 dashes: 248-259
VOL5_FIXED = {f"第{i}章" for i in range(248, 260)}

def count_emdash(text):
    return text.count('——')

def fix_chapter(text, target_min=30, target_max=50):
    """Reduce em-dashes to target range while keeping functional ones."""
    original_count = count_emdash(text)
    if original_count <= target_max:
        return text, original_count

    # Strategy: replace narrative "——" with "，"
    # Keep functional ones identified by context

    lines = text.split('\n')
    new_lines = []

    for line in lines:
        # Check if line is purely a chapter title
        if line.startswith('# ') or line.startswith('#第'):
            new_lines.append(line)
            continue

        # Check if line is blank
        if not line.strip():
            new_lines.append(line)
            continue

        # Check if line starts with "——" (dialogue response) - keep these
        line_starts_with_dash = line.startswith('——')

        # For lines starting with "——", we keep the first "——" but may reduce others
        if line_starts_with_dash:
            # Keep the line-starting ——, reduce others on this line
            line = process_line_dashes(line, keep_first=True)
        else:
            line = process_line_dashes(line, keep_first=False)

        new_lines.append(line)

    result = '\n'.join(new_lines)
    new_count = count_emdash(result)

    # If still too many, do a more aggressive pass
    if new_count > target_max:
        result = aggressive_reduce(result, target_max)
        new_count = count_emdash(result)

    return result, new_count


def process_line_dashes(line, keep_first=False):
    """Process a single line: replace breathing dashes with commas.

    Strategy:
    - Find all "——" in the line
    - Keep those that appear to be functional (dialogue related)
    - Replace others with "，"
    """
    if '——' not in line:
        return line

    # Find all —— positions
    parts = line.split('——')

    if len(parts) <= 1:
        return line

    # Check if this looks like dialogue (contains quotes)
    has_quotes = '"' in line or '「' in line or '」' in line or '“' in line or '”' in line

    # Check if this is a dialogue attribution pattern (他说——"xxx")
    dialogue_attr_pattern = False
    for i, part in enumerate(parts):
        if i < len(parts) - 1:
            # Check if after this —— there's a quote
            next_part = parts[i+1]
            if next_part.startswith('"') or next_part.startswith('「') or next_part.startswith('“'):
                dialogue_attr_pattern = True
                break

    # Reconstruct the line, deciding which —— to keep
    result_parts = [parts[0]]
    kept_count = 0

    for i in range(1, len(parts)):
        prev_part = parts[i-1]
        curr_part = parts[i]

        should_keep = False

        # Keep if at line start (first position)
        if keep_first and i == 1:
            should_keep = True

        # Keep if dialogue attribution (—"xxx)
        if i < len(parts):
            if curr_part.startswith('"') or curr_part.startswith('「') or curr_part.startswith('“'):
                should_keep = True

        # Keep if preceded by dialogue trailing off (xxx"——)
        if prev_part.endswith('"') or prev_part.endswith('」') or prev_part.endswith('”'):
            should_keep = True

        # Keep if inside quotes (dialogue pauses)
        # Count unclosed quotes before this position to determine if we're inside dialogue
        text_before = ''.join(parts[:i])
        quote_count = text_before.count('"') + text_before.count('「') + text_before.count('“')
        end_quote_count = text_before.count('"') + text_before.count('」') + text_before.count('”')
        # For 「」, count pairs
        if quote_count > end_quote_count:
            # We're inside dialogue
            should_keep = True

        # Keep if the —— is used for interruption (part ends without clear punctuation)
        if prev_part and prev_part[-1] not in '，。；：？！、,.!?;:':
            # Check if it looks like a word being cut off (short final segment)
            last_word = prev_part.split()[-1] if prev_part.split() else ''
            if len(last_word) <= 3 and last_word:
                # Could be trailing off - keep
                should_keep = True

        if should_keep:
            result_parts.append('——' + curr_part)
            kept_count += 1
        else:
            result_parts.append('，' + curr_part)

    result = ''.join(result_parts)

    # Clean up double commas
    result = result.replace('，，', '，')
    result = result.replace('。。', '。')
    result = result.replace('，。', '。')
    result = result.replace('——，', '——')
    result = result.replace('，——', '——')

    return result


def aggressive_reduce(text, target_max):
    """More aggressive reduction: replace remaining narrative dashes."""
    lines = text.split('\n')
    result_lines = []

    for line in lines:
        if '——' not in line:
            result_lines.append(line)
            continue

        if line.startswith('#'):
            result_lines.append(line)
            continue

        # For lines with quotes, try to keep dashes only inside quotes
        has_quotes = '"' in line or '「' in line or '」' in line

        if has_quotes:
            # Complex: keep dashes inside quotes only
            result_lines.append(keep_dashes_inside_quotes_only(line))
        else:
            # Simple: no quotes, replace all remaining dashes
            line = line.replace('——', '，')
            line = line.replace('，，', '，')
            result_lines.append(line)

    return '\n'.join(result_lines)


def keep_dashes_inside_quotes_only(line):
    """Keep em-dashes only inside quotation marks."""
    result = []
    i = 0
    in_quote = False
    quote_char = None

    while i < len(line):
        c = line[i]

        # Check for quote start
        if not in_quote and (c in '"“「'):
            in_quote = True
            quote_char = c
            result.append(c)
            i += 1
            continue

        # Check for quote end
        if in_quote:
            if (quote_char == '"' and c == '"') or \
               (quote_char == '“' and c == '”') or \
               (quote_char == '「' and c == '」'):
                in_quote = False
                result.append(c)
                i += 1
                continue

        # Handle ——
        if line[i:i+2] == '——':
            if in_quote:
                result.append('——')
            else:
                result.append('，')
            i += 2
            continue

        result.append(c)
        i += 1

    return ''.join(result)


def process_file(filepath, target_min=30, target_max=50):
    """Process a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    original_count = count_emdash(text)

    if original_count <= target_max:
        return False, original_count, original_count

    new_text, new_count = fix_chapter(text, target_min, target_max)

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_text)

    return True, original_count, new_count


def main():
    all_files = []

    # Volume 4 - all chapters
    vol4_dir = os.path.join(BASE_DIR, "第四卷")
    for fname in sorted(os.listdir(vol4_dir)):
        if fname.endswith('.md') and fname.startswith('第'):
            all_files.append(os.path.join(vol4_dir, fname))

    # Volume 5 - skip already fixed chapters (248-259)
    vol5_dir = os.path.join(BASE_DIR, "第五卷")
    for fname in sorted(os.listdir(vol5_dir)):
        if not (fname.endswith('.md') and fname.startswith('第')):
            continue
        # Extract chapter number
        match = re.match(r'第(\d+)章', fname)
        if match:
            chap_num = int(match.group(1))
            if 248 <= chap_num <= 259:
                continue
        all_files.append(os.path.join(vol5_dir, fname))

    total_files = len(all_files)
    changed_files = 0
    total_original = 0
    total_new = 0

    print(f"Processing {total_files} files...")
    print(f"{'File':<50} {'Before':>6} {'After':>6} {'Change':>8}")
    print("-" * 72)

    for filepath in all_files:
        fname = os.path.basename(filepath)
        changed, orig, new = process_file(filepath)
        if changed:
            changed_files += 1
            total_original += orig
            total_new += new
            delta = new - orig
            print(f"{fname:<50} {orig:>6} {new:>6} {delta:>+8}")

    print("-" * 72)
    print(f"Changed: {changed_files}/{total_files} files")
    print(f"Total dashes: {total_original} -> {total_new} (removed {total_original - total_new})")


if __name__ == '__main__':
    main()
