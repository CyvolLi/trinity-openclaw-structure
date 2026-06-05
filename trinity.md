# Trinity — 三位一体多 Agent 协作系统

> 项目名：Trinity  
> 频道：仅 QQ Bot  
> 设计原则：Father 指挥 → Spirit 查 + 注册 → Son 执行  

---

## 一、概述

Trinity 解决 QQ Bot 的两个核心需求：

1. **长期记忆** — Father 通过 `User.md` 积累用户画像，越用越理解用户
2. **可注册的 Bot 功能** — 用户可随时注册新功能（如漂流瓶、灵感收集本），系统自动建目录、写规则、绑定触发词

三个 Agent 分工协作：

```
用户消息
  │
  ▼
┌─────────────────────────────┐
│  Father                      │
│  工作区: workspace-father/   │
│  ┌─────────────────────────┐ │
│  │ trigger_prompt.md       │ │ ← 扫描：命中已注册功能？
│  │ User.md                 │ │ ← 积累用户画像
│  └─────────────────────────┘ │
└──────┬──────────────┬───────┘
       │              │
   命中功能        未命中
       │              │
       ▼              ▼
┌──────────┐    ┌──────────┐
│  Spirit   │    │  Father  │  非纯文本
│  查是否   │    │  自己回  │  (搜图等)
│  已注册   │    │  复 或   │──→ Son
└────┬─────┘    │  转Son   │
     │          └──────────┘
  ┌──┴──┐
  │     │
 注册过 未注册
  │     │
  ▼     ▼
 Son   Spirit 引导注册
 执行   创建 xxx_function.md
  │     更新 bot_function_explain.md
  │     更新 trigger_prompt.md
  │     交 Father 给用户确认
  ▼
 Father
 转发结果给用户
```

---

## 二、信息流详解

### 2.1 消息入口

```
QQ Bot → openclaw.json bindings → Father (agentId: father)
```

所有 QQ 消息经过 Father 统一入口。

### 2.2 Father 决策树

```
收到用户消息
  │
  ├─ 扫描 trigger_prompt.md（模糊匹配，不死扣格式）
  │    │
  │    ├─ 命中 /注册 → Spirit 注册新功能流程
  │    ├─ 命中 /菜单 → Spirit 返回 bot_function_explain.md
  │    ├─ 命中 /删除 → Spirit 清理流程
  │    ├─ 命中其他触发词 → Spirit 查 xxx_function.md → Son 执行
  │    └─ 无匹配 →
  │         ├─ 纯文本聊天 → Father 直接回复（参考 User.md）
  │         └─ 需要非纯文本处理（搜图/生成/网页）→ 直接交 Son
  │
  └─ 每次注册前必须查 bot_function_explain.md 防重复功能
```

### 2.3 注册新功能流程

```
用户: "/注册-漂流瓶 匿名扔消息和随机捞取"
  │
  ▼
Father → Spirit
  │
  ├─ 检查 bot_function_explain.md 是否有相似功能
  │    ├─ 有 → 返回已有功能名，问用户是否继续
  │    └─ 无 → 继续
  │
  ├─ Spirit 创建 draft:
  │    ├─ 在 bot_function_explain.md 添加条目（标记 ⏳ 待确认）
  │    └─ 创建 xxx_function.md（按 6 段格式规范）
  │
  ├─ Father 展示给用户确认
  │    ├─ 确认 → 标记 ✅ 已注册，更新 trigger_prompt.md
  │    └─ 取消/修改 → Spirit 修改或删除 draft
  │
  └─ Son 创建对应工作文件夹
```

### 2.4 调用已注册功能流程

```
用户: "/扔瓶子 今天天气真好"
  │
  ▼
Father → Spirit → 查 floatbottle_function.md
  │
  ▼
Son: 按执行接口章节操作
  ├─ 生成 BTL-20260528-0001.json
  ├─ 写入 floatbottle/ 目录
  └─ 按返回格式拼回复 → Father → 用户
```

### 2.5 删除功能流程

```
用户: "/删除-漂流瓶"
  │
  ▼
Father → Spirit → 清理:
  ├─ bot_function_explain.md 对应条目
  ├─ xxx_function.md
  ├─ trigger_prompt.md 对应行
  └─ Son 下对应工作文件夹
```

---

## 三、角色定义

### 3.1 Father — 总指挥

| 项目 | 内容 |
|------|------|
| **Agent ID** | `father` |
| **Workspace** | `~/.openclaw/workspace-father/` |
| **职责** | 消息入口、决策路由、用户画像积累、回复中转 |

**工作区文件：**

| 文件 | 作用 | 状态 |
|------|------|:--:|
| `AGENTS.md` | 行为规则（待填充） | ⬜ |
| `SOUL.md` | 人格语气（待填充） | ⬜ |
| `IDENTITY.md` | Father, 总指挥 | ✅ |
| `User.md` | 用户画像，长期记忆，越用越精准 | ✅ |
| `trigger_prompt.md` | 已注册功能的触发词表，模糊匹配 | ✅ |

**关键行为：**
- 只有用户**明确说"注册"**才走注册流程（避免误触发）
- "知道用户意思"，不要求精确格式（/扔瓶子 = 扔瓶子 = 扔个瓶子）
- 非纯文本任务（搜图、生成图片、网页抓取）直接交 Son
- 每次注册前查 `bot_function_explain.md` 防重复

### 3.2 Spirit — 智慧 / 知识库

| 项目 | 内容 |
|------|------|
| **Agent ID** | `spirit` |
| **Workspace** | `~/.openclaw/workspace-spirit/` |
| **职责** | 功能注册、功能查询、功能删除、格式规范定义 |

**工作区文件：**

| 文件 | 作用 | 状态 |
|------|------|:--:|
| `AGENTS.md` | 行为规则（待填充） | ⬜ |
| `SOUL.md` | 人格语气（待填充） | ⬜ |
| `IDENTITY.md` | Spirit, 智慧知识源 | ✅ |
| `bot_function_explain.md` | 已注册功能清单 + 系统指令 | ✅ |
| `{name}_function.md` | 每个功能的完整定义（填 6 段） | ✅ 漂流瓶已完成 |

**`bot_function_explain.md` 格式：**

```markdown
## 系统指令
| 指令 | 说明 |
| /菜单 | 返回本文件 |
| /删除-xxx | 清理全部相关文件 |
| /注册-xxx "解释" | 注册新功能 |

## 已注册功能
### 1. 功能名
- 触发指令: ...
- 功能说明: ...
- 存储文件: xxx_function.md
- 状态: ✅ 已注册
```

**`xxx_function.md` 格式规范（六段模板）：**

| # | 章节 | 内容 |
|---|------|------|
| 1 | **功能描述** | 一句话说清功能 |
| 2 | **工作文件夹** | Son 下的存储路径 |
| 3 | **触发指令** | 命令表格（指令/参数/说明） |
| 4 | **执行接口** | Son 每一步的具体操作 |
| 5 | **记录格式** | JSON 结构和字段定义 |
| 6 | **返回格式** | Son→Father→用户 的回复模板 |

### 3.3 Son — 执行者

| 项目 | 内容 |
|------|------|
| **Agent ID** | `son` |
| **Workspace** | `~/.openclaw/workspace-son/` |
| **职责** | 接收指令、执行操作、返回结果 |

**工作区结构：**

```
workspace-son/
├── AGENTS.md               ← 行为规则（待填充）
├── SOUL.md                 ← 人格语气（待填充）
├── IDENTITY.md             ← Son, 执行者 ✅
├── TOOLS.md                ← 工具配置（待填充）
└── {功能名}/                ← 每个注册功能的数据目录
    ├── {record}.json
    └── ...
```

**当前功能目录：**

| 目录 | 对应功能 | 状态 |
|------|---------|:--:|
| `floatbottle/` | 漂流瓶 | ✅ 已初始化 |

**关键行为：**
- 严格按 `xxx_function.md` 中的执行接口操作
- 所有结果按返回格式拼好交给 Father
- 不直接和用户对话

---

## 四、跨 Agent 通信

```
Father 与 Spirit:
  Father ──spawn(spirit)──→ [任务描述 + 用户输入]
  Spirit ──返回结果──────→ Father

Father 与 Son:
  Father ──spawn(son)────→ [执行指令 + xxx_function.md 路径]
  Son ──返回结果─────────→ Father
```

Father 通过 `sessions_spawn` 工具派发子任务给 Spirit 和 Son。

---

## 五、文件总览

```
~/.openclaw/
│
├── openclaw.json                    ← 注册 father/son/spirit + QQ Bot 绑定
├── trinity.md                       ← 本文件（系统架构文档）
│
├── workspace-father/                ← Father 工作区
│   ├── AGENTS.md
│   ├── SOUL.md
│   ├── IDENTITY.md
│   ├── User.md                      ← 用户画像（长期记忆）
│   └── trigger_prompt.md            ← 触发词 → 功能映射
│
├── workspace-spirit/                ← Spirit 工作区
│   ├── AGENTS.md
│   ├── SOUL.md
│   ├── IDENTITY.md
│   ├── bot_function_explain.md      ← 功能清单 + 系统指令
│   └── floatbottle_function.md     ← 漂流瓶功能定义
│
└── workspace-son/                   ← Son 工作区
    ├── AGENTS.md
    ├── SOUL.md
    ├── IDENTITY.md
    └── floatbottle/                 ← 漂流瓶数据
```

---

## 六、扩展新功能步骤

```
用户说: "/注册-灵感收集 随手记下灵感和想法"

→ Spirit:
  1. 查 bot_function_explain.md 无相似 → 继续
  2. 复制 floatbottle_function.md → inspiration_function.md
  3. 填 6 段：描述/文件夹/触发词/执行/格式/返回
  4. 在 bot_function_explain.md 添加条目

→ Father:
  5. 展示 draft 给用户确认

→ 确认后:
  6. Spirit: 标记 ✅ 已注册
  7. Father: 更新 trigger_prompt.md 添加触发词
  8. Son: 创建 inspiration/ 目录

→ 用户即可用 /灵感 /记灵感 等触发词调用
```

---

## 七、设计原则

1. **Father 单一入口** — 所有消息经 Father，保证用户画像连续性
2. **Spirit 知识中枢** — 所有功能定义集中管理，避免分散
3. **Son 纯执行** — 不思考、不决策，只按规则做事
4. **注册需确认** — 新功能必须经用户确认，防止误注册
5. **防重复** — 注册前查 `bot_function_explain.md`，相似功能提示用户
6. **模糊匹配** — 触发词不死扣格式，理解用户意图即可