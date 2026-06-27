#!/usr/bin/env python3
"""
新书初始化工具 — Novel Initializer.

从模板一键生成新小说目录骨架，确保每本小说起步结构一致。

用法:
    python init_novel.py <书名> [--template <模板目录>]
    python init_novel.py "我的新小说"
    python init_novel.py 诡镇 --dry-run

生成结构:
    小说库/<书名>/
    ├── 书籍简介.md
    ├── 小说大纲-<书名>.md
    ├── 写作规范.md
    ├── 原创性审查报告.md
    ├── 伏笔台账.md
    ├── 章节状态.md
    ├── 大纲/
    ├── 角色设定/
    ├── 监工日志/
    ├── 第一卷/ ~ 第五卷/
    └── CLAUDE.md (新书专属指令)
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(r"D:/workspace/writer/恐怖小说专题/小说库")
TEMPLATE_DIR = Path(r"D:/workspace/writer/恐怖小说专题/新书模板")


def replace_placeholders(text: str, replacements: dict) -> str:
    """Replace {{PLACEHOLDER}} patterns in template text."""
    for key, value in replacements.items():
        text = text.replace(f"{{{{{key}}}}}", value)
    return text


def init_novel(novel_name: str, dry_run: bool = False) -> Path:
    """Create a new novel directory from template.

    Args:
        novel_name: The name of the novel (used as directory name)
        dry_run: If True, print what would be done without doing it

    Returns:
        Path to the new novel directory
    """
    novel_dir = BASE_DIR / novel_name

    if novel_dir.exists():
        raise FileExistsError(f"小说目录已存在: {novel_dir}\n如需重建，请先删除或重命名现有目录。")

    if not TEMPLATE_DIR.exists():
        raise FileNotFoundError(f"模板目录不存在: {TEMPLATE_DIR}")

    # Prepare replacements — only these placeholders are auto-replaced.
    # Other {{PLACEHOLDER}} patterns in templates (e.g. {{TARGET_PLATFORM}},
    # {{GENRE}}, {{MC_VOICE}}) are manual fill-in guidance — replace them
    # when filling out the template files after initialization.
    today = datetime.now().strftime("%Y-%m-%d")
    replacements = {
        "NOVEL_NAME": novel_name,
        "NOVEL_NAME_SHORT": novel_name,
        "REVIEW_DATE": today,
        "TODAY": today,
    }

    if dry_run:
        print(f"[DRY RUN] 将在 {novel_dir} 创建新小说骨架：")
        print()

    # Walk template directory
    created_dirs = set()
    created_files = []

    for root, dirs, files in os.walk(TEMPLATE_DIR):
        rel_path = Path(root).relative_to(TEMPLATE_DIR)

        # Create corresponding directory in target
        if str(rel_path) != '.':
            target_dir = novel_dir / rel_path
        else:
            target_dir = novel_dir

        if str(target_dir) not in created_dirs:
            if dry_run:
                print(f"  📁 {target_dir.relative_to(BASE_DIR)}/")
            else:
                target_dir.mkdir(parents=True, exist_ok=True)
            created_dirs.add(str(target_dir))

        for fname in files:
            src_file = Path(root) / fname
            target_file = target_dir / fname

            # Handle placeholder filenames
            target_name = fname
            for key, value in replacements.items():
                target_name = target_name.replace(f"{{{{{key}}}}}", value)
            target_file = target_dir / target_name

            if dry_run:
                created_files.append(str(target_file.relative_to(BASE_DIR)))
            else:
                # Read template, replace placeholders, write
                with open(src_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Only replace in .md files (skip .gitkeep etc)
                if fname.endswith('.md'):
                    content = replace_placeholders(content, replacements)

                with open(target_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                created_files.append(str(target_file.relative_to(BASE_DIR)))

    if dry_run:
        for f in created_files:
            print(f"  📄 {f}")
        print()
        print(f"共 {len(created_dirs)} 个目录, {len(created_files)} 个文件")
    else:
        # Create per-novel CLAUDE.md
        # NOTE: This content is hardcoded because it must reflect the current
        # template structure. If the template directory changes, update this block.
        claude_md = novel_dir / "CLAUDE.md"
        claude_content = f"""# 《{novel_name}》— 创作指令

> 新书引导文件。监工和写作Agent启动时先读此文件。

---

## 基本信息

| 项目 | 内容 |
|------|------|
| **书名** | 《{novel_name}》 |
| **创建时间** | {today} |
| **当前阶段** | 📋 立项 — 待市场调研+大纲+角色设计 |

---

## 创作流水线

### 下一步行动

1. **/horror-supervisor** — 启动监工，执行市场调研+方向决策
2. 书名确定 → **horror-plagiarism-check** 查重
3. 大纲生成（五卷 + 爆点分布 + 伏笔系统）
4. 角色设计：**horror-protagonist** → **horror-antagonist** → **horror-supporting-characters** → **horror-monster-entity**
5. 查重确认 → 写作规范定稿
6. 伏笔台账初始化 → 章节状态初始化
7. 写作上下文打包 → 5个Agent并行启动

### 文件清单

| 文件 | 状态 | 说明 |
|------|------|------|
| 书籍简介.md | 📝 待填写 | 封面/详情页文案 |
| 小说大纲-{novel_name}.md | 📝 待生成 | 五卷大纲+爆点+伏笔初稿 |
| 写作规范.md | 📝 待填写 | 本书专属写作规范 |
| 原创性审查报告.md | 📝 待审查 | 书名+概念+金手指查重 |
| 伏笔台账.md | 📋 已初始化 | 写作中持续更新 |
| 章节状态.md | 📋 已初始化 | 每章写后结算 |
| 角色设定/ | 📝 待填充 | 4个角色文件 |
| 监工日志/ | 📝 待产出 | 监工全流程产出 |

---

## 关联资源

- 全局创作规范：`恐怖小说专题/创作规范与流程.md`
- 监工Skill：`horror-supervisor`
- 上下文打包：`python pack_context.py {novel_name} <章节号>`
"""
        with open(claude_md, 'w', encoding='utf-8') as f:
            f.write(claude_content)

        # Print summary
        print(f"✅ 新小说骨架已创建: {novel_dir}")
        print()
        print(f"📁 {len(created_dirs)} 个目录")
        print(f"📄 {len(created_files) + 1} 个文件 (含 CLAUDE.md)")
        print()
        print("## 下一步")
        print(f"1. cd {novel_dir}")
        print(f"2. /horror-supervisor — 启动监工")
        print(f"3. 填写 书籍简介.md + 写作规范.md")
        print(f"4. 生成 小说大纲-{novel_name}.md")
        print(f"5. 依次启动角色塑造Skills")
        print(f"6. python pack_context.py {novel_name} 1 — 打包首章上下文")

    return novel_dir


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="新书初始化工具 — 从模板一键生成新小说目录骨架",
    )
    parser.add_argument("name", nargs="?", help="小说名（将作为目录名）")
    parser.add_argument("--template", help="模板目录路径（默认: 恐怖小说专题/新书模板）")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不实际创建文件")

    args = parser.parse_args()

    if not args.name:
        parser.print_help()
        print("\n示例: python init_novel.py 诡镇")
        print("      python init_novel.py \"我的新小说\" --dry-run")
        return

    # Override template dir if specified
    global TEMPLATE_DIR
    if args.template:
        TEMPLATE_DIR = Path(args.template)

    try:
        init_novel(args.name, dry_run=args.dry_run)
    except FileExistsError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
