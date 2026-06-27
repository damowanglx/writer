# 恐怖小说专题

> 专业恐怖小说创作工具箱 —— 角色塑造、原创审查、文本优化、进度监制，一站式创作支持。

---

## 📁 项目结构

```
恐怖小说专题/
├── README.md                          ← 你在这里
├── 监工/SKILL.md                      ← 🆕 创作总监制
│                                       → horror-supervisor
├── 角色塑造/                          ← 4个角色塑造Skill
│   ├── 主角/SKILL.md                  → horror-protagonist
│   ├── 反派/SKILL.md                  → horror-antagonist
│   ├── 配角与队友/SKILL.md             → horror-supporting-characters
│   └── 怪物与恐怖实体/SKILL.md         → horror-monster-entity
├── 查重与审查/SKILL.md                ← 原创性审查Skill
│                                       → horror-plagiarism-check
├── 去AI味与人味增强/SKILL.md          ← 恐怖小说文本优化Skill
│                                       → horror-humanizer
├── 伏笔管理/                          ← 🆕 伏笔全生命周期管理
│   ├── SKILL.md                       → horror-foreshadowing
│   └── 伏笔台账模板.md                 ← 新书伏笔台账模板
├── 章节状态追踪/                      ← 🆕 真相系统
│   ├── SKILL.md                       → horror-chapter-state
│   └── 章节状态模板.md                 ← 总账+快照+情绪债务
├── 上下文打包/                        ← 🆕 写作上下文自动打包
│   └── SKILL.md                       → horror-context-packer
├── 新书模板/                          ← 🆕 新书一键初始化
│   ├── SKILL.md                       → init-novel
│   └── (模板文件)                      ← 书籍简介/大纲/写作规范/角色设定/伏笔/章节状态
├── 一致性校验/                        ← 🆕 自动化一致性检查
│   └── SKILL.md                       → horror-consistency-checker
└── 小说库/                            ← 未来的恐怖小说子文件夹
    └── (每本小说单独一个子文件夹)
```

---

## 🎯 工作流程（由监工驱动）

### 新书创作全流程

```
📋 立项阶段（horror-supervisor 主导）
  → **init-novel** 生成目录骨架
  → 市场调研：什么方向最畅销？
  → 书名+概念确定
  → horror-plagiarism-check 查重
  → 立项报告

🎭 准备阶段（horror-supervisor 调度角色Skills）
  → horror-protagonist 设计主角
  → horror-antagonist 设计反派
  → horror-supporting-characters 设计配角
  → horror-monster-entity 设计怪物
  → 人设汇总 + 一致性检查

✍️ 写作阶段（每卷循环）
  → 卷前：确认大纲 + 进度看板更新 + horror-foreshadowing 写前检查 + horror-chapter-state 写前准备
  → 卷中：定期抽检质量 + horror-foreshadowing 写后结算 + horror-chapter-state 写后结算
  → 卷后：horror-plagiarism-check + horror-humanizer + horror-consistency-checker + horror-foreshadowing 卷级汇总 + horror-chapter-state 卷级交接
  → 审核报告 → 通过/修订

🏁 完本阶段
  → 全本终审
  → 完本汇报（向出品人汇报）
  → 发布建议
```

---

## 🛠️ Skills 清单

### 🆕 项目管理（1个）

| Skill | 用途 | 调用方式 |
|-------|------|----------|
| **horror-supervisor** | 创作总监制：进度把控、市场调研、质量关卡、Skill调度、一致性监督、完本汇报 | `Skill("horror-supervisor")` |

### 角色塑造（4个）

| Skill | 用途 | 调用方式 |
|-------|------|----------|
| **horror-protagonist** | 恐怖小说主角/幸存者/调查者塑造 | `Skill("horror-protagonist")` |
| **horror-antagonist** | 人性反派/对抗力量塑造 | `Skill("horror-antagonist")` |
| **horror-supporting-characters** | 配角/队友/牺牲者塑造 | `Skill("horror-supporting-characters")` |
| **horror-monster-entity** | 怪物/鬼魂/超自然实体/诅咒设计 | `Skill("horror-monster-entity")` |

### 审查工具（1个）

| Skill | 用途 | 调用方式 |
|-------|------|----------|
| **horror-plagiarism-check** | 书名/概念/情节/角色全面查重 | `Skill("horror-plagiarism-check")` |

### 文本优化（1个）

| Skill | 用途 | 调用方式 |
|-------|------|----------|
| **horror-humanizer** | 恐怖小说去AI味+人味增强 | `Skill("horror-humanizer")` |

### 质量保障（3个）

| Skill | 用途 | 调用方式 |
|-------|------|----------|
| **horror-foreshadowing** | 伏笔全生命周期管理：埋设即登记、每章对照、推进追踪、回收核验 | `Skill("horror-foreshadowing")` |
| **horror-chapter-state** | 章节状态追踪（真相系统）：总账结算、角色快照、情绪债务追踪 | `Skill("horror-chapter-state")` |
| **horror-consistency-checker** | 一致性自动校验：角色/时间线/结构/道具/规则+伏笔交叉 | `Skill("horror-consistency-checker")` 或 `python check_consistency.py` |

### 写作工具（2个）

| Skill | 用途 | 调用方式 |
|-------|------|----------|
| **horror-context-packer** | 写作上下文自动打包：为任意章节生成Writer Agent所需完整上下文 | `Skill("horror-context-packer")` 或 `python pack_context.py` |
| **init-novel** | 新书初始化：从模板一键生成标准目录骨架 | `Skill("init-novel")` 或 `python init_novel.py <书名>` |

### 已有通用Skills（可配合使用）

| Skill | 用途 |
|-------|------|
| **humanizer-zh** | 通用中文去AI写作痕迹 |
| **novel-writer** | 校园甜宠/番茄小说风格写作与修改 |

---

## 📝 小说库使用规范

每本新恐怖小说请在 `小说库/` 下创建独立子文件夹：

```
小说库/
├── 残响审判/              ← 示例：已完成小说
│   ├── 大纲/
│   ├── 角色设定/
│   ├── 查重报告/
│   ├── 监工日志/
│   ├── 第一卷/
│   ├── 第二卷/
│   └── ...
├── 下一本小说名/
│   └── ...
```

子文件夹命名规范：**使用小说书名作为文件夹名**。

每本小说建议包含以下子目录：
- `大纲/` — 小说大纲、分卷大纲
- `角色设定/` — 所有人设卡
- `查重报告/` — 历次原创性审查报告
- `监工日志/` — 监工出具的进度/质量报告
- `第一卷/` `第二卷/` … — 各卷正文

---

## ⚠️ 重要提醒

- **每本小说先启动监工**（/horror-supervisor），由监工统筹全流程
- 每本小说创作前 **必须先运行查重Skill** 检查书名和核心概念
- 每章完成后建议运行 **去AI味Skill** 进行修订
- 角色塑造建议 **在写正文之前完成**，确保角色行为一致
- 监工是质量防线的最后守门人——它说"不通过"就必须改
