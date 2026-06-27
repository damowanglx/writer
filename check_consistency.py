#!/usr/bin/env python3
"""
一致性校验工具 — Consistency Checker.

自动扫描小说全文章节，检测：
1. 角色出场追踪 — 哪个角色在哪章出现/消失
2. 名称一致性 — 同一角色是否被叫了不同名字
3. 时间线标记 — 提取所有时间引用，检测异常
4. 伏笔台账交叉校验 — 台账中的伏笔是否在章节中有对应
5. 章节结构异常 — 字数异常/章节缺失
6. 关键道具追踪 — 重要物品的流转是否合理
7. 规则关键词 — 世界观规则引用是否前后矛盾

用法:
    python check_consistency.py <小说名> [--checks <检查项>]
    python check_consistency.py 残响审判
    python check_consistency.py 祠堂 --checks chars,timeline
    python check_consistency.py --list-novels

检查项: all | chars | names | timeline | foreshadow | structure | props | rules
"""

import os
import sys
import re
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(r"D:/workspace/writer/恐怖小说专题/小说库")

# ─── helpers ─────────────────────────────────────────────

def find_novel_dir(name: str) -> Path | None:
    for d in BASE_DIR.iterdir():
        if d.is_dir() and name in d.name:
            return d
    return None

def list_novels() -> list[str]:
    if not BASE_DIR.exists():
        return []
    return [d.name for d in BASE_DIR.iterdir() if d.is_dir()]

def read_file(path: Path) -> str:
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def find_all_chapters(novel_dir: Path) -> list[tuple[int, Path, str]]:
    """Find all chapters sorted by number. Returns [(chap_num, path, volume_name), ...]."""
    chapters = []
    for vol_name in ["第一卷", "第二卷", "第三卷", "第四卷", "第五卷"]:
        vol_dir = novel_dir / vol_name
        if vol_dir.exists():
            for f in sorted(vol_dir.glob("第[0-9]*章*.md")):
                m = re.match(r'第0*(\d+)章', f.name)
                if m:
                    chapters.append((int(m.group(1)), f, vol_name))
    chapters.sort()
    return chapters

def extract_chapter_title(filepath: Path) -> str:
    name = filepath.stem
    cleaned = re.sub(r'^第\d{3}章[-_—]?', '', name)
    return cleaned if cleaned else name

# ─── check 1: character appearance tracking ──────────────

def check_character_appearances(novel_dir: Path) -> dict:
    """Track which chapters each character appears in."""
    chapters = find_all_chapters(novel_dir)
    char_dir = novel_dir / "角色设定"

    # Extract character names from role design files
    known_chars = set()
    if char_dir.exists():
        for cf in char_dir.glob("*.md"):
            content = read_file(cf)
            # Format A: **姓名**：XXX or **姓名**: XXX
            names = re.findall(r'\*\*姓名\*\*[：:]\s*([^\n]+)', content)
            known_chars.update(n.strip() for n in names)
            # Format B: table row | **姓名** | XXX |
            names2 = re.findall(r'\|\s*\*\*姓名\*\*\s*\|\s*([^|\n]+)', content)
            known_chars.update(n.strip() for n in names2 if n.strip())
            # Format C: bold name in heading like ## 一、沈父（第五代守祠人）
            names3 = re.findall(r'#{1,4}\s*[一二三四五六七八九十]+[、．.]\s*([^\s（(]{2,4})', content)
            known_chars.update(n.strip() for n in names3 if n.strip())

    # Track appearances
    char_appearances = defaultdict(list)
    for cn, cp, vol in chapters:
        content = read_file(cp)
        for char_name in known_chars:
            if len(char_name) >= 2 and char_name in content:
                char_appearances[char_name].append(cn)

    # Find ghost characters (in role design but never appear)
    ghost_chars = []
    for char_name in known_chars:
        if len(char_name) >= 2 and char_name not in char_appearances:
            ghost_chars.append(char_name)

    # Find characters who disappear (appear in early chapters but not later)
    disappeared = []
    total_chapters = len(chapters)
    for char_name, apps in char_appearances.items():
        if apps and len(apps) >= 3:
            last_app = max(apps)
            if chapters and last_app < chapters[-1][0] - 10:
                disappeared.append((char_name, min(apps), last_app, chapters[-1][0] - last_app))

    return {
        "known_characters": sorted(known_chars),
        "total_chapters": total_chapters,
        "appearances": dict(char_appearances),
        "ghost_characters": ghost_chars,
        "disappeared_characters": disappeared,
    }

# ─── check 2: name consistency ───────────────────────────

def check_name_consistency(novel_dir: Path) -> dict:
    """Check for name variants of the same character."""
    chapters = find_all_chapters(novel_dir)
    char_dir = novel_dir / "角色设定"

    # Build canonical name list from character files
    canonical = {}
    if char_dir.exists():
        for cf in char_dir.glob("*.md"):
            content = read_file(cf)
            # Extract 姓名
            names = re.findall(r'\*\*姓名\*\*[：:]\s*([^\n]+)', content)
            for n in names:
                n = n.strip()
                if n:
                    # Also extract aliases
                    aliases_match = re.search(r'\*\*别名\*\*[：:]\s*([^\n]+)', content)
                    aliases = [a.strip() for a in aliases_match.group(1).split('、')] if aliases_match else []
                    canonical[n] = {"aliases": aliases, "file": cf.name}

    issues = []
    for cn, cp, vol in chapters:
        content = read_file(cp)
        for name, info in canonical.items():
            # Count occurrences of canonical name vs aliases
            main_count = content.count(name)
            alias_counts = {a: content.count(a) for a in info["aliases"] if a}
            # If aliases used more than canonical name, flag
            for alias, count in alias_counts.items():
                if count > main_count and count > 2:
                    issues.append({
                        "chapter": cn,
                        "character": name,
                        "issue": f"别名'{alias}'出现{count}次，正名'{name}'仅出现{main_count}次",
                        "severity": "低",
                    })

    return {"canonical_names": canonical, "name_issues": issues}

# ─── check 3: timeline markers ───────────────────────────

def check_timeline(novel_dir: Path) -> dict:
    """Extract all timeline markers and check for anomalies."""
    chapters = find_all_chapters(novel_dir)

    # Patterns for time references
    time_patterns = [
        (r'(\d{4})年(\d{1,2})月(\d{1,2})日', 'full_date'),
        (r'(\d{1,2})月(\d{1,2})[日号]', 'month_day'),
        (r'(凌晨|早上|上午|中午|下午|傍晚|晚上|午夜|子时|丑时|寅时|卯时|辰时|巳时|午时|未时|申时|酉时|戌时|亥时)', 'time_of_day'),
        (r'(\d{1,2})点(\d{1,2})?分?', 'clock_time'),
        (r'(昨天|今天|明天|前天|后天|三天前|三天后|一周前|一周后|一个月前|一个月后)', 'relative_time'),
        (r'第(\d+)天', 'day_counter'),
    ]

    markers = []
    for cn, cp, vol in chapters:
        content = read_file(cp)
        for pattern, ptype in time_patterns:
            for m in re.finditer(pattern, content):
                markers.append({
                    "chapter": cn,
                    "position": m.start(),
                    "text": m.group(0),
                    "type": ptype,
                })

    # Check for timeline anomalies (simple heuristics)
    anomalies = []
    # If 月/日 values appear that don't make sense (e.g., month > 12)
    for marker in markers:
        if marker["type"] == "month_day":
            parts = re.findall(r'\d+', marker["text"])
            if parts and int(parts[0]) > 12:
                anomalies.append({
                    "chapter": marker["chapter"],
                    "issue": f"月份异常: {marker['text']}",
                    "severity": "中",
                })

    return {
        "total_time_markers": len(markers),
        "markers_by_chapter": {cn: len([m for m in markers if m["chapter"] == cn]) for cn, _, _ in chapters},
        "anomalies": anomalies,
    }

# ─── check 4: foreshadowing cross-reference ──────────────

def check_foreshadow_crossref(novel_dir: Path) -> dict:
    """Cross-reference 伏笔台账 entries against actual chapters."""
    fbd_file = novel_dir / "伏笔台账.md"
    if not fbd_file.exists():
        return {"error": "无伏笔台账文件"}

    fbd_content = read_file(fbd_file)
    chapters = find_all_chapters(novel_dir)

    # Parse foreshadowing entries from ledger
    entries = []
    in_table = False
    for line in fbd_content.split('\n'):
        if line.strip().startswith('| F') and '|' in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 9:
                entries.append({
                    "id": parts[1],
                    "type": parts[2],
                    "content": parts[3],
                    "planted_ch": parts[4],
                    "planned_payoff": parts[5],
                    "actual_payoff": parts[6],
                    "status": parts[7],
                })

    # Check: do planted chapters exist?
    missing_chapters = []
    chapter_nums = {cn for cn, _, _ in chapters}
    for entry in entries:
        planted = entry["planted_ch"]
        m = re.search(r'(\d+)', planted)
        if m:
            ch_num = int(m.group(1))
            if ch_num not in chapter_nums:
                missing_chapters.append({
                    "foreshadow_id": entry["id"],
                    "issue": f"埋设章节不存在: {planted}",
                    "severity": "高",
                })

    # Count statuses
    status_counts = Counter(e["status"] for e in entries)
    uncollected = [e for e in entries if "🌱" in e["status"] or "🌿" in e["status"]]

    return {
        "total_entries": len(entries),
        "status_summary": dict(status_counts),
        "uncollected_count": len(uncollected),
        "uncollected_ids": [e["id"] for e in uncollected],
        "missing_chapter_refs": missing_chapters,
    }

# ─── check 5: chapter structure ───────────────────────────

def check_chapter_structure(novel_dir: Path) -> dict:
    """Check chapter word counts, gaps, and anomalies."""
    chapters = find_all_chapters(novel_dir)

    stats = []
    gaps = []
    prev_num = 0

    for cn, cp, vol in chapters:
        content = read_file(cp)
        char_count = len(content)
        line_count = content.count('\n')
        stats.append({
            "num": cn,
            "title": extract_chapter_title(cp),
            "volume": vol,
            "char_count": char_count,
            "line_count": line_count,
        })

        # Check for gaps
        if prev_num > 0 and cn != prev_num + 1:
            gaps.append({"from": prev_num, "to": cn, "missing": cn - prev_num - 1})
        prev_num = cn

    # Anomalies
    if stats:
        char_counts = [s["char_count"] for s in stats]
        avg = sum(char_counts) / len(char_counts)
        anomalies = []
        for s in stats:
            if s["char_count"] < avg * 0.2:  # Less than 20% of average
                anomalies.append({
                    "chapter": s["num"],
                    "issue": f"字数异常少: {s['char_count']}字 (平均{avg:.0f}字)",
                    "severity": "中",
                })
            if s["char_count"] > avg * 3:  # More than 3x average
                anomalies.append({
                    "chapter": s["num"],
                    "issue": f"字数异常多: {s['char_count']}字 (平均{avg:.0f}字)",
                    "severity": "低",
                })

        return {
            "total_chapters": len(stats),
            "total_chars": sum(char_counts),
            "avg_chars_per_chapter": avg,
            "chapter_gaps": gaps,
            "anomalies": anomalies,
            "per_volume": {
                vol: {
                    "count": len([s for s in stats if s["volume"] == vol]),
                    "total_chars": sum(s["char_count"] for s in stats if s["volume"] == vol),
                }
                for vol in set(s["volume"] for s in stats)
            },
        }

    return {"total_chapters": 0, "error": "未找到章节"}

# ─── check 6: key props tracking ──────────────────────────

def check_props_tracking(novel_dir: Path) -> dict:
    """Track key道具 mentioned in 章节状态 or 伏笔台账."""
    state_file = novel_dir / "章节状态.md"
    fbd_file = novel_dir / "伏笔台账.md"

    # Extract key props from 伏笔台账
    key_props = set()
    fbd_content = read_file(fbd_file)
    # Look for key props in foreshadowing content (2+ char prop names only)
    prop_patterns = re.findall(
        r'[（(]([^）)]*(?:哨子|钥匙|铜铃|卷尺|打火机|红毛线|手表|怀表|小圆镜|发卡|照片|铜牌|竹针|骨铃|银哨|银环|日记本|笔记本)[^）)]*)[）)]',
        fbd_content
    )
    key_props.update(p.strip() for p in prop_patterns if len(p.strip()) >= 2)

    # Also extract from 持有道具 columns in state file
    state_content = read_file(state_file)
    prop_matches = re.findall(r'\|\s*(?:银哨子|铜铃|铜钥匙|卷尺|打火机|红毛线|手表|怀表|小圆镜|发卡|照片|铜牌|竹针|骨铃)[^\|]*\|', state_content)
    for pm in prop_matches:
        key_props.add(pm.strip('| '))

    # Track appearances
    chapters = find_all_chapters(novel_dir)
    prop_tracking = defaultdict(list)
    for cn, cp, vol in chapters:
        content = read_file(cp)
        for prop in key_props:
            if prop and len(prop) >= 2 and prop in content:
                prop_tracking[prop].append(cn)

    # Check for props that disappear
    lost_props = []
    for prop, apps in prop_tracking.items():
        if apps and len(apps) >= 2 and chapters:
            last = max(apps)
            if last < chapters[-1][0] - 5:
                lost_props.append((prop, min(apps), last))

    return {
        "tracked_props": sorted(key_props),
        "appearances": dict(prop_tracking),
        "potentially_lost_props": lost_props,
    }

# ─── check 7: rule keyword consistency ────────────────────

def check_rule_consistency(novel_dir: Path) -> dict:
    """Track worldbuilding rule references for potential contradictions."""
    chapters = find_all_chapters(novel_dir)

    # Common rule-indicating patterns in Chinese horror
    rule_patterns = [
        r'(?:规则|条件|代价|限制)[：:]\s*([^\n]+)',
        r'(?:不能|不可以|禁止|严禁)([^\n，。]+)',
        r'(?:必须|一定要|得)([^\n，。]+)',
    ]

    rules_found = defaultdict(list)
    for cn, cp, vol in chapters:
        content = read_file(cp)
        for pattern in rule_patterns:
            for m in re.finditer(pattern, content):
                rule_text = m.group(0)[:80]
                rules_found[rule_text].append(cn)

    # Rules that appear only once might be forgotten
    single_mention_rules = [
        (rule, chapters_list)
        for rule, chapters_list in rules_found.items()
        if len(chapters_list) == 1 and len(rule) > 10
    ]

    # Rules that have contradictory language (very basic check)
    contradictions = []
    rule_texts = list(rules_found.keys())
    for i, r1 in enumerate(rule_texts):
        for r2 in rule_texts[i+1:]:
            # Simple check: if one rule says "不能X" and another says "必须X" or "可以X"
            neg_match = re.search(r'(?:不能|不可以|禁止|严禁)\s*(.+)', r1)
            pos_match = re.search(r'(?:必须|一定要|可以|能)\s*(.+)', r2)
            if neg_match and pos_match:
                neg_target = neg_match.group(1)[:10]
                pos_target = pos_match.group(1)[:10]
                if neg_target in pos_target or pos_target in neg_target:
                    contradictions.append({
                        "rule_a": r1[:60],
                        "rule_b": r2[:60],
                        "severity": "中",
                    })

    return {
        "total_unique_rules": len(rules_found),
        "single_mention_rules": len(single_mention_rules),
        "potential_contradictions": contradictions[:10],  # limit
    }

# ─── report generator ─────────────────────────────────────

def generate_report(novel_name: str, results: dict) -> str:
    """Generate a formatted consistency report."""
    novel_dir = find_novel_dir(novel_name)
    if not novel_dir:
        return f"❌ 找不到小说: {novel_name}"

    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# 一致性校验报告 — 《{novel_dir.name}》",
        f"",
        f"> 校验时间：{today}",
        f"> 校验工具：check_consistency.py",
        f"",
        "---",
        "",
        "## 总览",
        "",
    ]

    # Summary
    total_issues = 0
    checks_run = []

    for check_name, data in results.items():
        if isinstance(data, dict) and "error" not in data:
            issues_in_check = 0
            if "anomalies" in data:
                issues_in_check += len(data["anomalies"])
            if "ghost_characters" in data:
                issues_in_check += len(data["ghost_characters"])
                issues_in_check += len(data.get("disappeared_characters", []))
            if "name_issues" in data:
                issues_in_check += len(data["name_issues"])
            if "missing_chapter_refs" in data:
                issues_in_check += len(data["missing_chapter_refs"])
            if "chapter_gaps" in data:
                issues_in_check += len(data["chapter_gaps"])
            if "potential_contradictions" in data:
                issues_in_check += len(data["potential_contradictions"])
            if "potentially_lost_props" in data:
                issues_in_check += len(data["potentially_lost_props"])
            total_issues += issues_in_check

            status = "✅" if issues_in_check == 0 else "⚠️"
            checks_run.append(f"| {check_name} | {status} | {issues_in_check} 个问题 |")

    lines.append(f"| 检查项 | 状态 | 结果 |")
    lines.append(f"|--------|------|------|")
    for c in checks_run:
        lines.append(c)
    lines.append(f"| **合计** | — | **{total_issues} 个问题** |")
    lines.append("")

    # Detailed results
    for check_name, data in results.items():
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## {check_name}")
        lines.append(f"")

        if isinstance(data, dict) and "error" in data:
            lines.append(f"> ⚠️ {data['error']}")
            lines.append("")
            continue

        if check_name == "character_appearances":
            lines.append(f"- 已知角色：{len(data.get('known_characters', []))} 个")
            lines.append(f"- 总章节：{data.get('total_chapters', 0)} 章")
            lines.append(f"")

            ghost = data.get("ghost_characters", [])
            if ghost:
                lines.append(f"### 👻 幽灵角色（设定中有但从未出场）")
                for g in ghost:
                    lines.append(f"- {g}")
                lines.append("")

            disappeared = data.get("disappeared_characters", [])
            if disappeared:
                lines.append(f"### 📉 消失角色（出场后超过10章未再出现）")
                lines.append(f"| 角色 | 首次出场 | 最后出场 | 已消失章数 |")
                lines.append(f"|------|----------|----------|------------|")
                for name, first, last, gap in disappeared:
                    lines.append(f"| {name} | 第{first:03d}章 | 第{last:03d}章 | {gap}章 |")
                lines.append("")

            # Top appearances
            apps = data.get("appearances", {})
            if apps:
                lines.append(f"### 出场统计（出场最多的角色 Top 10）")
                lines.append(f"| 角色 | 出场章数 | 章节范围 |")
                lines.append(f"|------|----------|----------|")
                sorted_apps = sorted(apps.items(), key=lambda x: len(x[1]), reverse=True)[:10]
                for name, ch_list in sorted_apps:
                    ch_range = f"第{min(ch_list):03d}-第{max(ch_list):03d}章" if ch_list else "—"
                    lines.append(f"| {name} | {len(ch_list)} | {ch_range} |")
                lines.append("")

        elif check_name == "chapter_structure":
            lines.append(f"- 总章节：{data.get('total_chapters', 0)} 章")
            lines.append(f"- 总字数：{data.get('total_chars', 0):,} 字")
            lines.append(f"- 平均每章：{data.get('avg_chars_per_chapter', 0):.0f} 字")
            lines.append(f"")

            pv = data.get("per_volume", {})
            if pv:
                lines.append(f"### 逐卷统计")
                lines.append(f"| 卷序 | 章数 | 总字数 | 平均字数 |")
                lines.append(f"|------|------|--------|----------|")
                for vol in ["第一卷", "第二卷", "第三卷", "第四卷", "第五卷"]:
                    if vol in pv:
                        v = pv[vol]
                        avg = v["total_chars"] / v["count"] if v["count"] else 0
                        lines.append(f"| {vol} | {v['count']}章 | {v['total_chars']:,}字 | {avg:.0f}字 |")
                lines.append("")

            gaps = data.get("chapter_gaps", [])
            if gaps:
                lines.append(f"### ⚠️ 章节缺失")
                for g in gaps:
                    lines.append(f"- 第{g['from']:03d}章 → 第{g['to']:03d}章：缺失 {g['missing']} 章")
                lines.append("")

            anomalies = data.get("anomalies", [])
            if anomalies:
                lines.append(f"### ⚠️ 字数异常")
                for a in anomalies:
                    lines.append(f"- 第{a['chapter']:03d}章：{a['issue']} [{a['severity']}]")
                lines.append("")

        elif check_name == "foreshadow_crossref":
            lines.append(f"- 台账伏笔总数：{data.get('total_entries', 0)} 条")
            status_summary = data.get("status_summary", {})
            if status_summary:
                lines.append(f"- 状态分布：{status_summary}")
            lines.append(f"- 未回收伏笔：{data.get('uncollected_count', 0)} 条 ({', '.join(data.get('uncollected_ids', []))})")
            lines.append(f"")

            missing = data.get("missing_chapter_refs", [])
            if missing:
                lines.append(f"### ⚠️ 台账引用的章节不存在")
                for m in missing:
                    lines.append(f"- {m['foreshadow_id']}：{m['issue']} [{m['severity']}]")
                lines.append("")

        elif check_name == "timeline":
            lines.append(f"- 时间标记总数：{data.get('total_time_markers', 0)} 处")
            mb = data.get("markers_by_chapter", {})
            if mb:
                avg = sum(mb.values()) / len(mb) if mb else 0
                lines.append(f"- 平均每章时间标记：{avg:.1f} 处")
            lines.append(f"")

            anomalies = data.get("anomalies", [])
            if anomalies:
                lines.append(f"### ⚠️ 时间线异常")
                for a in anomalies:
                    lines.append(f"- 第{a['chapter']:03d}章：{a['issue']} [{a['severity']}]")
                lines.append("")

        elif check_name == "props_tracking":
            tracked = data.get("tracked_props", [])
            lines.append(f"- 追踪道具：{len(tracked)} 个 — {', '.join(tracked) if tracked else '无'}")
            lines.append(f"")

            lost = data.get("potentially_lost_props", [])
            if lost:
                lines.append(f"### ⚠️ 可能丢失的道具（最后出场后超过5章未出现）")
                for prop, first, last in lost:
                    lines.append(f"- {prop}：第{first:03d}章 → 第{last:03d}章后消失")
                lines.append("")

        elif check_name == "rule_consistency":
            lines.append(f"- 唯一规则引用：{data.get('total_unique_rules', 0)} 条")
            lines.append(f"- 仅提及一次的规则：{data.get('single_mention_rules', 0)} 条")
            lines.append(f"")

            contra = data.get("potential_contradictions", [])
            if contra:
                lines.append(f"### ⚠️ 潜在规则矛盾")
                for c in contra:
                    lines.append(f"- 矛盾：`{c['rule_a'][:50]}...` vs `{c['rule_b'][:50]}...` [{c['severity']}]")
                lines.append("")

        elif check_name == "name_consistency":
            issues = data.get("name_issues", [])
            if issues:
                lines.append(f"### ⚠️ 名称使用问题")
                for i in issues:
                    lines.append(f"- 第{i['chapter']:03d}章：{i['issue']} [{i['severity']}]")
                lines.append("")
            else:
                lines.append("✅ 未发现名称使用问题")
                lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append(f"> 校验完成。共检测到 **{total_issues}** 个潜在问题。")
    lines.append(f"> 请逐条审查——此工具仅做模式匹配，可能误报。")
    lines.append("")

    return "\n".join(lines)

# ─── CLI ──────────────────────────────────────────────────

CHECK_MAP = {
    "chars": "check_character_appearances",
    "names": "check_name_consistency",
    "timeline": "check_timeline",
    "foreshadow": "check_foreshadow_crossref",
    "structure": "check_chapter_structure",
    "props": "check_props_tracking",
    "rules": "check_rule_consistency",
}

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="一致性校验工具 — 自动检测小说全文的结构性和模式性矛盾",
    )
    parser.add_argument("novel", nargs="?", help="小说名（支持部分匹配）")
    parser.add_argument("--checks", default="all", help="检查项: all | chars,names,timeline,foreshadow,structure,props,rules")
    parser.add_argument("--list-novels", action="store_true", help="列出所有可用小说")
    parser.add_argument("--output", "-o", help="输出报告路径")

    args = parser.parse_args()

    if args.list_novels:
        novels = list_novels()
        print("可用小说：")
        for n in novels:
            d = find_novel_dir(n)
            chapter_count = 0
            for vol_name in ["第一卷", "第二卷", "第三卷", "第四卷", "第五卷"]:
                vol_dir = d / vol_name if d else None
                if vol_dir and vol_dir.exists():
                    chapter_count += len(list(vol_dir.glob("第[0-9]*章*.md")))
            has_fbd = "✅" if (d / "伏笔台账.md").exists() else "❌"
            has_state = "✅" if (d / "章节状态.md").exists() else "❌"
            print(f"  {n:30s}  {chapter_count:3d}章  台账{has_fbd}  状态{has_state}")
        return

    if not args.novel:
        parser.print_help()
        print("\n示例: python check_consistency.py 残响审判")
        print("      python check_consistency.py 祠堂 --checks chars,timeline")
        return

    novel_dir = find_novel_dir(args.novel)
    if not novel_dir:
        print(f"❌ 找不到小说: '{args.novel}'")
        print(f"可用小说: {list_novels()}")
        return

    # Determine which checks to run
    if args.checks == "all":
        checks_to_run = list(CHECK_MAP.keys())
    else:
        checks_to_run = [c.strip() for c in args.checks.split(",") if c.strip() in CHECK_MAP]

    print(f"🔍 校验中: {novel_dir.name} ({', '.join(checks_to_run)})")
    print()

    results = {}
    for check_name in checks_to_run:
        func_name = CHECK_MAP[check_name]
        func = globals()[func_name]
        print(f"  ⏳ {check_name}...", end=" ")
        try:
            results[check_name] = func(novel_dir)
            print("✅")
        except Exception as e:
            print(f"❌ {e}")
            results[check_name] = {"error": str(e)}

    print()

    # Generate report
    report = generate_report(args.novel, results)

    if args.output:
        out_path = Path(args.output)
    else:
        out_path = novel_dir / f"一致性报告-{datetime.now().strftime('%Y%m%d')}.md"

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ 报告已生成: {out_path}")
    print(f"   字数: {len(report):,} 字符")

    # Quick summary
    total = sum(
        len(data.get("anomalies", [])) +
        len(data.get("ghost_characters", [])) +
        len(data.get("disappeared_characters", [])) +
        len(data.get("name_issues", [])) +
        len(data.get("missing_chapter_refs", [])) +
        len(data.get("chapter_gaps", [])) +
        len(data.get("potential_contradictions", [])) +
        len(data.get("potentially_lost_props", []))
        for data in results.values()
        if isinstance(data, dict) and "error" not in data
    )
    if total == 0:
        print(f"   ✅ 未发现明显问题")
    else:
        print(f"   ⚠️ 发现 {total} 个潜在问题，请查阅报告")


if __name__ == '__main__':
    main()
