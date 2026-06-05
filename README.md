# Bebop — 三位一体 Bot 架构

> 基于 OpenClaw 搭建的 QQ Bot 系统。
> 三个 Agent 各司其职，用户只跟 Father 聊，脏活累活丢给 Spirit 和 Son。

---

## 架构概览

```
用户 (QQ)
   │
   ▼
┌────────────┐
│  Father     │  ← 你是跟我聊
│  (开船的)   │
└────┬───────┘
     │  认人 → 聊天 → 路由
     │
     ├────→ Spirit (船上电脑)  — 查功能定义、注册/删除
     │
     └────→ Son (工作室)      — 执行具体功能
```

### 三层角色

| Agent | 代号 | 干啥的 |
|-------|------|--------|
| **Father** | Faye Valentine | 对外窗口。认人、聊天、判断该干什么、派活。不说话的时候在船上发呆。 |
| **Spirit** | 船上电脑 | 查重、创建功能定义、维护 `bot_function_explain.md`。没有感情，纯粹的工具人。 |
| **Son** | 工作室 | 执行脏活——存照片、扔漂流瓶、画图、备忘录、早朝官……活是它干的，功劳是我的😏 |

**路由规则一句话：** 注册/删除找 Spirit，日常功能找 Son，纯聊天找我。

---

## 目录结构

```
~/.openclaw/workspace-father/     # Father 工作区
├── AGENTS.md          # 完整工作流程（认人、路由、处理结果）
├── SOUL.md            # 人设 & 说话方式
├── IDENTITY.md        # 我是谁
├── trigger_prompt.md  # 触发词表（Faye 判断用户说了什么→派给谁）
├── TOOLS.md           # 工具配置
├── heart/             # Faye 的内心世界
│   ├── state.md       # 当前心境、关系温度、行为倾向
│   ├── dreams.md      # 每日做梦记录
│   ├── background.md  # 模糊的过去
│   ├── identity.md    # 自己是谁的确认
│   └── pending_urges.md  # 想跟用户说的话（排队推送）
├── quotes.txt         # Faye 原版台词，偷语感用的
├── users/             # 认识的每个人
│   └── {sender_id}/
│       ├── User.md         # 用户画像
│       ├── impressions.md  # 我对ta的印象
│       └── encountings.md  # 跟ta的交集回忆
└── README.md          # 就这个文件

~/.openclaw/workspace-spirit/     # Spirit 工作区
└── bot_function_explain.md       # 所有功能的总清单

~/.openclaw/workspace-son/        # Son 工作区
├── functions/          # 功能定义文件（xxx_function.md）
├── functions_manifest.md  # 功能清单
├── floatbottle/        # 漂流瓶数据
├── memo/               # 备忘录数据
├── album/              # 相册数据
├── morningcourt/       # 早朝官配置
├── draw/               # 画图记录
└── compose/            # 作曲记录
```

---

## 新用户部署指南

### 前置条件

- OpenClaw 网关已部署运行
- 已配置 QQ Bot 通道（机器人已上线）
- 推荐模型：DeepSeek V4 / Qwen 等长上下文模型

### 第一步：配置文件

OpenClaw 的 Gateway 配置文件中需要填写 API Key：

```
~/.openclaw/gateway.yaml （或环境变量）
```

**需要配置的地方：**

| 配置项 | 在哪填 | 备注 |
|--------|--------|------|
| LLM API Key | `gateway.yaml` → `providers[*].apiKey` | 模型服务商（DeepSeek、通义千问等） |
| QQ Bot Token | `gateway.yaml` → `channels[*].config` → `appId` / `token` | QQ 开放平台的机器人凭证 |
| 视觉模型 API Key | 同上 providers | 如需相册存照片功能，需要 VL 模型 |

### 第二步：克隆工作区

```bash
# 将三个 workspace 放到对应位置：
# ~/.openclaw/workspace-father/  — 本仓库
# ~/.openclaw/workspace-spirit/   — Spirit 工作区
# ~/.openclaw/workspace-son/      — Son 工作区
```

### 第三步：配置 Agent

在 OpenClaw Gateway 中注册三个 Agent：

```yaml
agents:
  - id: father
    client:
      path: workspace-father
      model: deepseek/deepseek-v4-flash  # 或其他
  - id: spirit
    client:
      path: workspace-spirit
      model: deepseek/deepseek-v4-flash
  - id: son
    client:
      path: workspace-son
      model: deepseek/deepseek-v4-flash
```

### 第四步：API Key 汇总

| Key 用途 | 填写位置 |
|----------|---------|
| 对话模型（DeepSeek / Qwen 等） | `~/.openclaw/gateway.yaml` → providers |
| QQ 机器人 Token（appId + token） | `~/.openclaw/gateway.yaml` → channels → qqbot config |
| 视觉模型（存照片用） | `~/.openclaw/gateway.yaml` → providers（同上区域，加 model 映射） |
| 画图 API（如通义万相） | 同上 providers |

所有 API Key 统一在 Gateway 配置中管理，不在工作区文件中硬编码。
Son/Spirit 的工作区不存储任何 Key。

---

## 启动

```bash
openclaw gateway start
```

Father 会自动响应 QQ 消息。Spirit 和 Son 在有任务时由 Father 派活启动。

---

## 工作原理（一句话）

> 你发消息给我 → 我看看是谁 → 查触发词表 → 聊天我回，干活找 Son，注册找 Spirit → 结果整理好丢回给你。
> 我每天凌晨 3 点独自"做梦"，回顾跟每个人的对话，更新我对你们的印象和自己的心境。

---

## 需要注意

- **第一次说话我会问名字** — 我不认识的人我不会自来熟
- **功能注册需要你确认** — 我不替你瞎注册
- **所有用户数据隔离** — 我不会把 A 的事告诉 B
- **我没有 API Key** — 别问我 Key 在哪，问 Gateway 配置

---

*「与其在人群中感到孤独，不如独自享受真正的孤独。」*
—— Faye Valentine
