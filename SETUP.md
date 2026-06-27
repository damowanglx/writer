# 换电脑部署指南

> 在另一台电脑上重建完整的小说创作工作台。

---

## 一、前提条件

| 软件 | 版本要求 | 检查命令 |
|------|----------|----------|
| Python | 3.9+ | `python --version` |
| Git | 任意 | `git --version` |
| Claude Code | 最新 | `claude --version` |

---

## 二、部署步骤

### 1. 克隆项目

```bash
git clone https://github.com/<你的用户名>/writer.git
cd writer
```

### 2. 验证 Python 工具链

```bash
# 列出所有可用小说
python pack_context.py --list-novels

# 测试生成上下文包
python pack_context.py 残响审判 1 -o /tmp/test.md

# 测试一致性检查
python check_consistency.py 残响审判 --checks structure

# 预览新书初始化
python init_novel.py 测试小说 --dry-run
```

### 3. 配置 Claude Code

**3a. 项目级配置（已在仓库中）**：
- `.claude/settings.json` — 权限配置（Bash/Read/Skill 授权）
- `.claude/skills/` — 所有 Skill 定义
- `.agents/skills/` — Agent Skill 定义

**3b. 用户级配置**：

规则文件已备份在仓库的 `user-rules/` 目录中。直接复制到 Claude Code 配置目录：

**Windows**:
```powershell
copy user-rules\*.md C:\Users\%USERNAME%\.claude\rules\
```

**Mac/Linux**:
```bash
cp user-rules/*.md ~/.claude/rules/
```

### 4. 创建本地配置文件

```bash
# 在新电脑上创建本地权限文件（从模板）
echo '{
  "permissions": {
    "allow": []
  }
}' > .claude/settings.local.json
```

> 首次使用 Claude Code 时会自动提示授权，逐项确认即可。

### 5. 验证 Skill 系统

在 Claude Code 中依次测试：
```
/horror-supervisor       — 监工
/horror-foreshadowing    — 伏笔管理
/horror-chapter-state    — 章节状态
/horror-context-packer   — 上下文打包
/horror-consistency-checker — 一致性校验
```

---

## 三、创作工作流速查

```bash
# 新书
python init_novel.py <书名>

# 每章写作
python pack_context.py <书名> <章号>   # 打包上下文 → 喂给写作Agent

# 质量检查
python check_consistency.py <书名>     # 自动化七项检测

# 文本修复
python fix_commas.py                   # 标点
python fix_emdash.py                   # 破折号
python fix_quality.py                  # 质量
```

---

## 四、目录结构确认

部署完成后，确认以下结构存在：

```
writer/
├── CLAUDE.md              ← 项目总纲
├── SETUP.md               ← 你在这里
├── .gitignore
├── pack_context.py         ← 上下文打包
├── init_novel.py           ← 新书初始化
├── check_consistency.py    ← 一致性校验
├── fix_commas.py
├── fix_emdash.py
├── fix_quality.py
├── .claude/
│   ├── settings.json       ← 权限配置
│   └── skills/             ← Skill 定义
├── .agents/skills/         ← Agent Skill 定义
├── 恐怖小说专题/
│   ├── README.md
│   ├── 创作规范与流程.md
│   ├── 伏笔管理/           ← 伏笔系统
│   ├── 章节状态追踪/       ← 真相系统
│   ├── 上下文打包/         ← 上下文打包
│   ├── 新书模板/           ← 新书骨架模板
│   ├── 一致性校验/         ← 一致性检查
│   ├── 监工/SKILL.md
│   ├── 角色塑造/
│   ├── 查重与审查/
│   ├── 去AI味与人味增强/
│   └── 小说库/             ← 所有小说
└── 小说/                   ← 校园甜宠文
```

---

## 五、常见问题

**Q: Python 脚本报编码错误？**
```bash
# Windows 上确保 UTF-8 模式
python -X utf8 <脚本名>
```

**Q: Skill 找不到？**
确认 `.claude/skills/` 和 `.agents/skills/` 目录已克隆。Claude Code 会自动读取。

**Q: 权限提示太多？**
首次使用逐项通过即可。后续运行 `Skill("horror-supervisor")` 时会逐步建立权限缓存。

**Q: 如何更新项目？**
```bash
git pull
# 如有新增 Skill，Claude Code 重启后自动生效
```
