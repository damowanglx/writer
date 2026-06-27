# writer — 小说创作工作区

> 中文长篇小说创作项目。两条产品线：校园甜宠文（完本） + 恐怖小说（多本并行）。

---

## 项目结构

```
writer/
├── CLAUDE.md                          ← 你在这里
├── readme.md                          ← 项目初始需求
├── skills-lock.json                   ← Skill锁定版本
├── fix_commas.py                      ← 批量修复标点
├── fix_emdash.py                      ← 批量修复破折号
├── fix_quality.py                     ← 批量质量检查
├── pack_context.py                    ← 写作上下文自动打包
├── init_novel.py                      ← 新书一键初始化
├── check_consistency.py               ← 一致性自动校验
│
├── 小说/                              ← 校园甜宠文正文（10卷63章 完本）
│   ├── 第一卷 ~ 第十卷/
│   └── 每卷5-8章，第XXX章-标题.md
│
├── 校园甜宠文/                        ← 甜宠文辅助工具
│   └── fix_endings.py
│
├── 恐怖小说专题/                      ← 恐怖小说创作工具箱 + 小说库
│   ├── README.md                      ← 工具链总览
│   ├── 创作规范与流程.md               ← 完整创作流水线（必读）
│   ├── 监工/SKILL.md                  ← horror-supervisor
│   ├── 角色塑造/                      ← 4个角色Skill
│   │   ├── 主角/SKILL.md              → horror-protagonist
│   │   ├── 反派/SKILL.md              → horror-antagonist
│   │   ├── 配角与队友/SKILL.md         → horror-supporting-characters
│   │   └── 怪物与恐怖实体/SKILL.md     → horror-monster-entity
│   ├── 查重与审查/SKILL.md            → horror-plagiarism-check
│   ├── 去AI味与人味增强/SKILL.md      → horror-humanizer
│   ├── 伏笔管理/SKILL.md              → horror-foreshadowing
│   ├── 章节状态追踪/SKILL.md           → horror-chapter-state
│   ├── 上下文打包/SKILL.md              → horror-context-packer
│   ├── 新书模板/SKILL.md                → init-novel
│   ├── 一致性校验/SKILL.md              → horror-consistency-checker
│   └── 小说库/                        ← 多本恐怖小说
│       ├── 收容失控/                    (完本参考)
│       ├── 凶宅测量员/
│       ├── 祠堂/
│       ├── 残响审判/
│       └── 体表标记/
│
├── .claude/                           ← 项目级Claude配置
│   ├── settings.json                  ← 权限配置
│   ├── settings.local.json            ← 本地权限 + Stop Hook
│   └── skills/                        ← 项目级Skill缓存
│
└── .agents/skills/                    ← Agent Skill定义
```

---

## 两条产品线

### 1. 校园甜宠文（已完本）

- **目标读者**：18-22岁女生
- **规模**：100万字，10卷
- **角色风格**：小白化
- **正文位置**：`小说/第一卷/` ~ `小说/第十卷/`
- **大纲位置**：`小说大纲-校园甜宠文.md`
- **状态**：63章已写完，完本

### 2. 恐怖小说（多本并行创作中）

- **目标读者**：成年人，番茄小说平台
- **风格**：无限流、悬疑解谜、规则怪谈
- **规模**：每本约50万字，5卷
- **创作方式**：多Agent并行写作（1 Agent = 1卷）
- **当前在写**：凶宅测量员、祠堂、残响审判

---

## 恐怖小说创作流水线

完整流程见 `恐怖小说专题/创作规范与流程.md`。核心阶段：

```
📋 立项 → 🎭 准备 → ✍️ 写作 → 🏁 完本
```

### 启动新书的正确顺序

1. **python init_novel.py <书名>** — 一键生成标准目录骨架
2. **/horror-supervisor** — 启动监工，由监工统筹全流程
3. 市场调研 → 书名确定 → 查重
4. 大纲生成（5卷 + 爆点分布 + 伏笔表）
5. 角色设计：主角 → 反派 → 配角 → 怪物
6. 查重确认（书名+金手指+核心概念）
7. 写作规范定稿
8. 5个Agent并行启动（一人一卷）
9. 监工定时巡查（每2小时）
10. 卷后审核（horror-plagiarism-check + horror-humanizer + horror-consistency-checker + horror-chapter-state 卷级交接）
11. 完本终审

### 多Agent并行写作要点

- 每个Agent启动前必须给：完整大纲 + 统一写作规范 + 所有角色设定卡 + 本卷状态承接 + 卷尾目标钩子
- Agent会写不完50章——预留2-3轮续写，监工巡查保障
- 章节命名：`第XXX章-标题.md`（三位零填充，如 `第001章`）

---

## 常用Skill

### 恐怖小说专用

| Skill | 用途 |
|-------|------|
| `horror-supervisor` | 创作总监制，全流程调度 |
| `horror-protagonist` | 主角/幸存者/调查者塑造 |
| `horror-antagonist` | 人性反派/对抗力量塑造 |
| `horror-supporting-characters` | 配角/队友塑造 |
| `horror-monster-entity` | 怪物/鬼魂/超自然实体设计 |
| `horror-plagiarism-check` | 书名/概念/情节查重 |
| `horror-humanizer` | 恐怖小说去AI味+人味增强 |
| `horror-foreshadowing` | 伏笔全生命周期管理：埋设→推进→回收 |
| `horror-chapter-state` | 章节状态追踪（真相系统）：总账+快照+情绪债务 |
| `horror-context-packer` | 写作上下文打包：自动组装写作Agent所需全部上下文 |
| `init-novel` | 新书初始化：从模板一键生成标准目录骨架 |
| `horror-consistency-checker` | 一致性自动校验：角色/时间线/结构/道具/规则7项检测 |

### 通用Skill

| Skill | 用途 |
|-------|------|
| `humanizer-zh` | 通用中文去AI写作痕迹 |
| `novel-writer` | 甜宠/番茄小说风格写作 |

---

## 文本处理工具

```bash
python fix_commas.py      # 批量修复逗号
python fix_emdash.py      # 批量修复破折号
python fix_quality.py     # 批量质量检查
python pack_context.py    # 写作上下文打包（用法: python pack_context.py 小说名 章节号）
python init_novel.py      # 新书初始化（用法: python init_novel.py 书名）
python check_consistency.py # 一致性校验（用法: python check_consistency.py 小说名）
```

---

## 子Agent日志

子Agent转录不存项目目录，存在用户目录：

```
~/.claude/projects/d--workspace-writer/<session-id>/subagents/
  ├── agent-<hash>.jsonl      ← 完整对话转录
  └── agent-<hash>.meta.json  ← 元数据（agent类型、时间等）
```

当前已有 4 个 session 共 175 个子Agent日志。查日志时去这里找，别在项目目录里找。

---

## 会话知识沉淀（CRITICAL — 每次会话启动必读）

### 机制

Stop Hook 在会话结束时自动写入两个标记文件：

| 文件 | 内容 |
|------|------|
| `.claude/last-session.txt` | 上次会话结束时间 |
| `.claude/last-session-transcript.txt` | 上次会话的 JSONL 转录路径 |

### 启动时必做

**每次新会话启动时**，执行以下检查流程：

1. 检查 `.claude/last-session.txt` 是否存在
2. 对照 `.claude/last-session-processed.txt`（上次已处理的时间戳）
3. 如果有未处理的会话：
   - 读取 `.claude/last-session-transcript.txt` 获取转录路径
   - 快速扫描转录，提取以下内容：
     - **新发现的技巧/工作流**（之前不知道的写法、工具用法）
     - **踩坑教训**（什么方式不行、为什么、正确替代方案）
     - **项目变更**（新增文件/目录/配置的含义）
     - **约定变更**（命名规范、流程调整、角色设定变动）
   - 追加到本文件末尾的「会话沉淀」区域
   - 更新 `.claude/last-session-processed.txt`

### 沉淀格式

```markdown
### YYYY-MM-DD — 会话摘要

- **技巧**: xxx
- **教训**: xxx
- **变更**: xxx
```

---

## 项目级配置要点

- **权限**：`settings.local.json` 管理项目级 Bash/Read/Skill 权限
- **额外目录**：已授权访问 `d:\workspace\writer` 及其子目录、`\tmp`
- **Skill 缓存**：`.claude/skills/` 和 `.agents/skills/` 存放项目级 Skill 定义
