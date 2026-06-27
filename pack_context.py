#!/usr/bin/env python3
"""
写作上下文打包工具 — Writing Context Packager.

给指定小说的指定章节自动组装写作上下文包。
输出一份结构化 Markdown，可直接喂给写作 Agent。

用法:
    python pack_context.py <小说名> <章节号> [--output <路径>]
    python pack_context.py 残响审判 15
    python pack_context.py 祠堂 8 --output /tmp/context.md
    python pack_context.py --list-novels

设计原则:
    - 只打包"写这一章需要知道的"，不堆砌历史
    - 自动检测可用文件，缺什么标什么
    - 输出一份文件，Agent 一次读完
"""

import os
import sys
import re
import glob as glob_mod
from pathlib import Path
from datetime import datetime

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(r"D:/workspace/writer/恐怖小说专题/小说库")

# ─── helpers ─────────────────────────────────────────────

def find_novel_dir(name: str) -> Path | None:
    """Find novel directory by partial name match."""
    if not BASE_DIR.exists():
        return None
    for d in BASE_DIR.iterdir():
        if d.is_dir() and name in d.name:
            return d
    return None

def list_novels() -> list[str]:
    """List all novel directories."""
    if not BASE_DIR.exists():
        return []
    return [d.name for d in BASE_DIR.iterdir() if d.is_dir()]

def read_file(path: Path) -> str | None:
    """Read file content, return None if not found."""
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def find_files(directory: Path, pattern: str) -> list[Path]:
    """Find files matching pattern in directory."""
    if not directory.exists():
        return []
    return sorted(directory.glob(pattern))

def safe_read(path: Path, max_chars: int = 0) -> str:
    """Read file safely, optionally truncate."""
    content = read_file(path)
    if content is None:
        return "(文件不存在)"
    if max_chars > 0 and len(content) > max_chars:
        content = content[:max_chars] + "\n\n... (已截断，完整文件见原路径)"
    return content

def fmt_chapter(chapter_num: int) -> str:
    """Format chapter number with zero-padding."""
    return f"第{chapter_num:03d}章"

def extract_chapter_title(filepath: Path) -> str:
    """Extract chapter title from filename or first heading."""
    name = filepath.stem  # e.g., "第001章-失踪的侧写师"
    # Remove leading number pattern
    cleaned = re.sub(r'^第\d{3}章[-_—]?', '', name)
    return cleaned if cleaned else name

def find_previous_chapters(novel_dir: Path, chapter_num: int, count: int = 2) -> list[tuple[int, Path]]:
    """Find the N previous chapters before chapter_num. Returns [(chap_num, path), ...]."""
    found = []
    all_chapters = []
    for vol_dir_name in ["第一卷", "第二卷", "第三卷", "第四卷", "第五卷"]:
        vol_dir = novel_dir / vol_dir_name
        if vol_dir.exists():
            for f in vol_dir.glob("第[0-9]*章*.md"):
                # extract chapter number from filename
                m = re.match(r'第(\d+)章', f.name)
                if m:
                    all_chapters.append((int(m.group(1)), f))

    all_chapters.sort()
    # Find chapters less than chapter_num, take last `count`
    prev = [(n, p) for n, p in all_chapters if n < chapter_num]
    return prev[-count:] if len(prev) >= count else prev

def find_outline(novel_dir: Path) -> list[Path]:
    """Find outline files."""
    outlines = []
    # Pattern 1: 小说大纲-*.md in root
    outlines.extend(novel_dir.glob("小说大纲*.md"))
    outlines.extend(novel_dir.glob("大纲*.md"))
    # Pattern 2: 大纲/ directory
    outline_dir = novel_dir / "大纲"
    if outline_dir.exists():
        outlines.extend(outline_dir.glob("*.md"))
    return sorted(outlines)

def find_characters(novel_dir: Path) -> list[Path]:
    """Find character design files."""
    char_dir = novel_dir / "角色设定"
    if char_dir.exists():
        return sorted(char_dir.glob("*.md"))
    return []

def find_supervisor_logs(novel_dir: Path) -> list[Path]:
    """Find supervisor logs."""
    log_dir = novel_dir / "监工日志"
    if log_dir.exists():
        return sorted(log_dir.glob("*.md"))
    return []

def find_writing_spec(novel_dir: Path) -> Path | None:
    """Find writing specification file."""
    spec = novel_dir / "写作规范.md"
    if spec.exists():
        return spec
    return None

# ─── content assemblers ───────────────────────────────────

def section_book_position(novel_name: str, chapter_num: int, outline_files: list[Path], novel_dir: Path) -> str:
    """Assemble '本章在全书中的位置' section."""
    chap = fmt_chapter(chapter_num)
    lines = [
        f"## 一、本章在全书中的位置",
        f"",
        f"- **书名**：《{novel_name}》",
        f"- **章节**：{chap}",
        f"- **打包时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
    ]

    # Determine which volume this chapter belongs to
    vol_num = None   # numeric 1-5
    vol_name = None  # string "第一卷"
    for i, vn in enumerate(["第一卷", "第二卷", "第三卷", "第四卷", "第五卷"], 1):
        vol_dir = novel_dir / vn
        if vol_dir.exists():
            for f in vol_dir.glob(f"第{chapter_num:03d}章*.md"):
                vol_num = i
                vol_name = vn
                break
        if vol_name:
            break
    if vol_name is None:
        vol_num = min((chapter_num - 1) // 12 + 1, 5)
        vol_name = f"第{vol_num}卷（推测）"
    lines.append(f"- **所属卷**：{vol_name}")
    lines.append(f"")

    # Read outline and extract relevant volume section
    for outline_file in outline_files:
        content = read_file(outline_file)
        if content:
            lines.append(f"### 大纲参考（来源：{outline_file.name}）")
            lines.append("")
            # Extract a reasonable portion
            if len(content) > 3000 and vol_num:
                # Try to find the relevant volume section by number
                vol_match = re.search(
                    rf'###?\s*第{vol_num}[卷部].*?(?=###?\s*第{vol_num+1}[卷部]|\Z)',
                    content, re.DOTALL
                )
                if vol_match:
                    lines.append(vol_match.group(0)[:2000])
                else:
                    lines.append(content[:1500])
            else:
                lines.append(content)
            lines.append("")
            break

    return "\n".join(lines)

def section_character_state(novel_dir: Path) -> str:
    """Assemble '角色当前状态' section from 章节状态.md or 角色设定 files."""
    lines = ["## 二、角色当前状态", ""]

    # Priority 1: 章节状态.md has current snapshots
    state_file = novel_dir / "章节状态.md"
    state_content = read_file(state_file)

    if state_content:
        # Extract the 角色状态快照 section
        match = re.search(
            r'## 二、角色状态快照.*?(?=## 三、|\Z)',
            state_content, re.DOTALL
        )
        if match:
            lines.append(match.group(0))
            lines.append("")
            return "\n".join(lines)

    # Fallback: Read 角色设定 files
    char_files = find_characters(novel_dir)
    if char_files:
        lines.append("> ⚠️ 无章节状态文件，以下为角色设定（初始状态，非当前状态）")
        lines.append("")
        for cf in char_files:
            content = safe_read(cf)
            if content:
                # Only include key sections, not entire file
                # Extract 基本信息 and 当前状态 if present
                lines.append(f"### {cf.stem}")
                lines.append("")
                if len(content) > 1500:
                    lines.append(content[:1500])
                    lines.append("")
                    lines.append("... (完整人设见原文件)")
                else:
                    lines.append(content)
                lines.append("")
    else:
        lines.append("> ❌ 无角色设定文件")

    return "\n".join(lines)

def section_foreshadowing(novel_dir: Path, chapter_num: int) -> str:
    """Assemble '伏笔提醒' section."""
    lines = ["## 三、伏笔提醒", ""]

    fbd_file = novel_dir / "伏笔台账.md"
    content = read_file(fbd_file)

    if not content:
        lines.append("> ❌ 无伏笔台账文件")
        return "\n".join(lines)

    # Try to find 写前检查 for this chapter
    chap_str = f"第{chapter_num:03d}章"
    chap_alt = f"第{chapter_num}章"

    check_match = re.search(
        rf'\|?\s*{chap_str}.*?\|.*?\|.*?\|',
        content
    )
    if check_match:
        lines.append(f"### {chap_str} 写前检查")
        lines.append("")
        lines.append(check_match.group(0))
        lines.append("")
    else:
        # Extract the 伏笔台账 main table and risk warnings
        lines.append("### 进行中的伏笔")
        lines.append("")

        # Find all entries with 🌿 status
        for line in content.split('\n'):
            if '🌿' in line and line.strip().startswith('| F'):
                lines.append(line)
        lines.append("")

        # Risk warnings: only include if there are actual warnings
        risk_match = re.search(
            r'## 风险预警.*?(?=## |\Z)',
            content, re.DOTALL
        )
        if risk_match:
            risk_text = risk_match.group(0)
            # Empty template has placeholder rows like "| — | — |"
            has_content = bool(re.search(r'\|\s*F\d+\s*\|', risk_text))
            if has_content:
                lines.append("### 超期预警")
                lines.append("")
                lines.append(risk_text)
                lines.append("")

    return "\n".join(lines)

def section_previous_chapters(novel_dir: Path, chapter_num: int) -> str:
    """Assemble '前章承接' section with summaries of previous 2 chapters."""
    lines = ["## 四、前章承接", ""]

    prev = find_previous_chapters(novel_dir, chapter_num, count=2)

    if not prev:
        if chapter_num == 1:
            lines.append("> 这是第一章，无前章承接。")
        else:
            lines.append("> ⚠️ 未找到前章文件")
        return "\n".join(lines)

    for cn, cp in prev:
        title = extract_chapter_title(cp)
        content = read_file(cp)
        if content:
            # Take last ~800 chars as "ending hook" + first ~400 chars as "chapter summary"
            if len(content) > 1500:
                summary = content[:500] + "\n\n... (中略) ...\n\n" + content[-800:]
            else:
                summary = content
            lines.append(f"### 第{cn:03d}章 — {title}")
            lines.append("")
            lines.append(f"```\n{summary}\n```")
            lines.append("")
            lines.append(f"> 完整正文：[{cp.name}]({cp.relative_to(novel_dir.parent.parent)})")
            lines.append("")

    # Remind about the hook to carry forward
    if prev:
        last_cn, last_cp = prev[-1]
        last_content = read_file(last_cp)
        if last_content:
            # Get last ~200 chars
            ending = last_content.strip()[-200:]
            lines.append("### ⚠️ 上章结尾（本章开头的情绪/场景必须承接此状态）")
            lines.append("")
            lines.append(f"> {ending[:200]}")
            lines.append("")

    return "\n".join(lines)

def section_writing_spec(novel_dir: Path) -> str:
    """Assemble '写作规范提醒' section."""
    lines = ["## 五、写作规范提醒", ""]

    # Novel-specific spec
    spec_file = find_writing_spec(novel_dir)
    if spec_file:
        content = safe_read(spec_file, max_chars=3000)
        lines.append(f"### 本书写作规范（{spec_file.name}）")
        lines.append("")
        lines.append(content)
        lines.append("")
    else:
        lines.append("> ⚠️ 本书无独立写作规范文件")
        lines.append("")

    # Global horror writing rules (abbreviated key points)
    process_doc = BASE_DIR.parent / "创作规范与流程.md"
    process_content = read_file(process_doc)
    if process_content:
        lines.append("### 全局提醒（创作规范摘要）")
        lines.append("")
        # Extract key rules
        lines.append("- 单章字数：2100-5000字（目标3000字左右）")
        lines.append("- 每章必须有：核心事件 + 情绪节奏 + 章尾钩子")
        lines.append("- 结尾钩子：必须让读者翻到下一章")
        lines.append("- 禁止：抽象套话、空泛收束、回环对话")
        lines.append("- 动词优先、控制形容词、禁止靠巧合推进")
        lines.append("- 对话每轮必须推进：事实/规矩/代价三选一")
        lines.append("")

    return "\n".join(lines)

def section_chapter_instructions(novel_dir: Path, chapter_num: int) -> str:
    """Assemble '本章写作指令' section."""
    lines = ["## 六、本章写作指令", ""]
    chap = fmt_chapter(chapter_num)

    # Check if there's a 细纲 (detailed outline) for this chapter
    outline_dir = novel_dir / "大纲"
    potential_names = [
        f"细纲_{chap}.md",
        f"章纲_{chap}.md",
        f"第{chapter_num}章.md",
    ]
    found_outline = False
    if outline_dir.exists():
        for name in potential_names:
            f = outline_dir / name
            if f.exists():
                content = safe_read(f)
                lines.append(f"### 本章细纲（来源：{name}）")
                lines.append("")
                lines.append(content)
                lines.append("")
                found_outline = True
                break

    if not found_outline:
        lines.append("> ⚠️ 本章无细纲文件。请根据大纲+前章承接+伏笔提醒自行规划。")
        lines.append("")

    # Always include the writing checklist
    lines.append("### 本章必须包含")
    lines.append("")
    lines.append('- [ ] 核心事件明确（本章的“一件事”是什么）')
    lines.append('- [ ] 情绪节奏设计（哪里压抑、哪里释放）')
    lines.append('- [ ] 至少一处恐怖/悬疑张力节点')
    lines.append('- [ ] 章尾钩子——让读者必须翻到下一章')
    lines.append('- [ ] 对照伏笔台账：本章应推进/回收的伏笔（见上方第三节）')
    lines.append('- [ ] 写后立即执行 horror-chapter-state 写后结算')
    lines.append("")

    return "\n".join(lines)

# ─── main packager ────────────────────────────────────────

def pack_context(novel_name: str, chapter_num: int, output_path: str | None = None) -> str:
    """Assemble the full context package for a given novel + chapter.

    Returns the assembled content as a string.
    If output_path is given, writes to disk.
    """
    novel_dir = find_novel_dir(novel_name)
    if not novel_dir:
        raise FileNotFoundError(f"找不到小说目录: '{novel_name}'\n可用小说: {list_novels()}")

    novel_display_name = novel_dir.name
    chap = fmt_chapter(chapter_num)

    parts = []

    # Section 1: Book position + outline
    outline_files = find_outline(novel_dir)
    parts.append(section_book_position(novel_display_name, chapter_num, outline_files, novel_dir))

    # Section 2: Character state
    parts.append(section_character_state(novel_dir))

    # Section 3: Foreshadowing reminders
    parts.append(section_foreshadowing(novel_dir, chapter_num))

    # Section 4: Previous chapters
    parts.append(section_previous_chapters(novel_dir, chapter_num))

    # Section 5: Writing spec
    parts.append(section_writing_spec(novel_dir))

    # Section 6: Chapter instructions
    parts.append(section_chapter_instructions(novel_dir, chapter_num))

    # Header
    header = f"""# 写作上下文包 — 《{novel_display_name}》{chap}

> 打包时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 用法：将此文件作为写作Agent的上下文输入，一次性提供全部所需信息。
> 写后必做：执行 `horror-chapter-state` 写后结算 + `horror-foreshadowing` 写后结算。

---

"""
    result = header + "\n\n".join(parts)

    # Add footer with file inventory
    result += "\n\n---\n\n"
    result += "## 附：上下文包文件清单\n\n"
    result += "| 类型 | 文件数 | 说明 |\n"
    result += "|------|--------|------|\n"

    outline_names = ', '.join(f.name for f in outline_files) if outline_files else '无'
    result += f"| 大纲 | {len(outline_files)} | {outline_names} |\n"

    char_files = find_characters(novel_dir)
    char_names = ', '.join(f.name for f in char_files) if char_files else '无'
    result += f"| 角色设定 | {len(char_files)} | {char_names} |\n"

    fbd = novel_dir / '伏笔台账.md'
    fbd_status = '伏笔台账.md' if fbd.exists() else '缺失'
    result += f"| 伏笔台账 | {'1' if fbd.exists() else '0'} | {fbd_status} |\n"

    state = novel_dir / '章节状态.md'
    state_status = '章节状态.md' if state.exists() else '缺失'
    result += f"| 章节状态 | {'1' if state.exists() else '0'} | {state_status} |\n"

    spec = find_writing_spec(novel_dir)
    spec_status = '写作规范.md' if spec else '缺失'
    result += f"| 写作规范 | {'1' if spec else '0'} | {spec_status} |\n"

    prev = find_previous_chapters(novel_dir, chapter_num, count=2)
    prev_names = ', '.join(p.name for _, p in prev) if prev else '无'
    result += f"| 前章文件 | {len(prev)} | {prev_names} |\n"

    result += "\n"

    # Write to disk
    if output_path:
        out = Path(output_path)
    else:
        out = novel_dir / f"上下文包-{chap}.md"

    with open(out, 'w', encoding='utf-8') as f:
        f.write(result)

    return result

# ─── CLI ──────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="写作上下文打包工具 — 为指定章节自动组装写作Agent所需的完整上下文",
    )
    parser.add_argument("novel", nargs="?", help="小说名（支持部分匹配，如 '残响审判' 或 '残响'）")
    parser.add_argument("chapter", nargs="?", type=int, help="章节号（如 15）")
    parser.add_argument("--output", "-o", help="输出路径（默认: 小说目录/上下文包-第XXX章.md）")
    parser.add_argument("--list-novels", action="store_true", help="列出所有可用小说")

    args = parser.parse_args()

    if args.list_novels:
        novels = list_novels()
        print("可用小说：")
        for n in novels:
            d = find_novel_dir(n)
            # Count chapters
            chapter_count = 0
            for vol_dir_name in ["第一卷", "第二卷", "第三卷", "第四卷", "第五卷"]:
                vol_dir = d / vol_dir_name if d else None
                if vol_dir and vol_dir.exists():
                    chapter_count += len(list(vol_dir.glob("第[0-9]*章*.md")))
            has_fbd = "✅" if (d / "伏笔台账.md").exists() else "❌"
            has_state = "✅" if (d / "章节状态.md").exists() else "❌"
            has_chars = "✅" if (d / "角色设定").exists() and list((d / "角色设定").glob("*.md")) else "❌"
            print(f"  {n:30s}  {chapter_count:3d}章  伏笔{has_fbd}  状态{has_state}  角色{has_chars}")
        return

    if not args.novel or not args.chapter:
        parser.print_help()
        print("\n示例: python pack_context.py 残响审判 15")
        print("      python pack_context.py 祠堂 8 --output /tmp/ctx.md")
        return

    try:
        content = pack_context(args.novel, args.chapter, args.output)
        out_path = args.output or (
            find_novel_dir(args.novel) / f"上下文包-{fmt_chapter(args.chapter)}.md"
        )
        print(f"✅ 上下文包已生成: {out_path}")
        print(f"   字数: {len(content):,} 字符")
        print(f"   章节: {fmt_chapter(args.chapter)}")
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
