---
name: init-novel
description: |
  新书初始化。从标准模板一键生成新小说目录骨架——
  确保每本小说起步结构一致：书籍简介+大纲+写作规范+角色设定+伏笔台账+章节状态+监工日志+五卷目录。
allowed-tools:
  - Read
  - Write
  - Bash
  - Edit
metadata:
  trigger: |
    创建新小说、开新书、初始化小说项目、新建小说、
    启动新书、新小说、开始写新书
  category: 恐怖小说-项目管理
---

# 新书初始化

你是新书引导员。创建一本新恐怖小说时，你负责从模板一键生成完整的目录骨架。

---

## 一、为什么需要模板

之前的问题：
- 祠堂角色设定目录是空的
- 凶宅测量员角色设定只有一个单薄文件
- 每本小说结构不统一

模板解决的就是这个问题——**每本新书从同一个骨架起步**。

---

## 二、生成内容

一键生成以下完整结构：

```
小说库/<书名>/
├── CLAUDE.md              ← 新书专属引导指令
├── 书籍简介.md             ← 封面/详情页文案模板
├── 小说大纲-<书名>.md      ← 五卷大纲模板
├── 写作规范.md             ← 本书专属写作规范模板
├── 原创性审查报告.md        ← 查重报告模板
├── 伏笔台账.md             ← 伏笔台账（预初始化）
├── 章节状态.md             ← 章节状态追踪（预初始化）
├── 大纲/                   ← 卷纲+细纲
├── 角色设定/               ← 4个角色文件（待Skills填充）
├── 监工日志/               ← 监工全流程产出
└── 第一卷/ ~ 第五卷/       ← 五卷章节目录
```

---

## 三、使用方法

### 一键生成

```bash
python init_novel.py <书名>

# 预览模式（不实际创建）
python init_novel.py 诡镇 --dry-run
```

### 生成后流程

```
1. python init_novel.py <书名>           ← 生成骨架
2. /horror-supervisor                    ← 启动监工
3. 市场调研 → 书名确定 → 查重
4. 填写 小说大纲-<书名>.md               ← 五卷大纲
5. 依次调度角色塑造Skills                  ← 主角→反派→配角→怪物
6. 填写 写作规范.md + 书籍简介.md         ← 写作规范定稿
7. horror-plagiarism-check 查重确认      ← 书名+概念+金手指
8. horror-foreshadowing 预填大纲伏笔     ← 伏笔台账初始化
9. horror-chapter-state 初始化状态       ← 章节状态初始化
10. python pack_context.py <书名> 1      ← 打包首章上下文
11. 5个Agent并行启动                     ← 一人一卷
```

---

## 四、与其他Skill的协作

| 步骤 | Skill | 产出 |
|------|-------|------|
| 初始化 | `init-novel` | 完整目录骨架 |
| 立项 | `horror-supervisor` | 市场调研+方向决策 |
| 查重 | `horror-plagiarism-check` | 原创性审查报告 |
| 角色 | `horror-protagonist/antagonist/supporting/monster` | 4个角色文件 |
| 伏笔 | `horror-foreshadowing` | 伏笔台账初始化 |
| 状态 | `horror-chapter-state` | 章节状态初始化 |
| 打包 | `horror-context-packer` | 第一章上下文包 |

---

## 五、输出要求

每次被调用时：
1. **检查模板目录**是否存在
2. **确认书名**（合法的目录名）
3. **执行 init_novel.py**（或手动复制模板）
4. **输出生成清单**（目录数+文件数）
5. **给出下一步行动清单**
