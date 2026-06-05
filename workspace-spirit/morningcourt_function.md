# morningcourt_function.md — 早朝官功能定义

> 本文件由 Spirit 维护，Son 执行时严格参照。

---

## 1. 功能描述

早朝官：每天早上固定时间自动推送"早朝简报"到用户 QQ，包含备忘录待办提醒、漂流瓶海随机瓶子、根据用户画像生成的迷你童话故事、节气饮食建议、当日摄影建议等。用户也可手动触发 `/早朝` 获取即时简报，或调整播报时间、关闭自动播报。

---

## 2. 工作文件夹

Son 在其工作区内创建和维护：

```
~/.openclaw/workspace-son/morningcourt/
```

配置文件存储：`~/.openclaw/workspace-son/morningcourt/config.json`

---

## 3. 触发指令

| 指令 | 参数 | 说明 |
|------|------|------|
| `/早朝` | 无 | 手动触发一次早朝简报 |
| `/设早朝 HH:MM` | 必填：时间（24小时制） | 设置自动播报时间，如 `/设早朝 08:00` |
| `/关早朝` | 无 | 关闭自动播报 |

---

## 4. 执行接口

### 4.1 早朝简报内容组装（核心逻辑）

Son 执行步骤（需接收 sender_id）：

1. **读备忘录**：读取 ~/.openclaw/workspace-son/memo/ 下所有 JSON，筛选 sender_id 匹配当前用户且 status 为 "pending"（待办）的条目
2. **捞瓶子**：读取 ~/.openclaw/workspace-son/floatbottle/ 下所有 JSON，随机选取 1 个（公有池，不限用户）
3. **生成童话/文学摘选**：每天随机从以下方向选一个——①原创迷你童话（80-120字），或②引用博尔赫斯、王尔德、卡尔维诺、莫言、马尔克斯等作家的经典短篇节选或名句（80-120字），或③古代志怪/寓言故事选段（如聊斋志异、庄子寓言等）。注意每次内容不重复，注明作者和出处。
4. **饮食推荐**：根据当前季节给出饮食推荐，1-2句。每次随机从不同时令食材里选，不要连续两天重复同一道菜/同一种食材，花样多一点，比如今天苦瓜明天冬瓜后天百合之类的。
5. **摄影建议**：根据当前季节/天气给出摄影题材建议，1-2句
6. **组装简报**：按返回格式拼接文本
7. **输出结果**

### 4.2 /早朝

手动触发，执行同上 4.1，直接将简报输出。

### 4.3 /设早朝

修改 `config-{sender_id}.json` 中的 time 字段，直接创建/更新 cron 定时任务（Son 自管，不经过 Father）。

cron 定时任务格式：

```
cron job 名称: morningcourt-{sender_id}
cron 表达式: 根据 config.time 转成 cron format（如 08:00 → 0 8 * * *）
cron 时区: Asia/Shanghai
agentId: son
sessionTarget: isolated
payload 消息格式: [morningcourt] sender_id={sender_id}, trigger briefing generation
payload timeout: 120 秒
delivery 模式: announce
delivery 渠道: qqbot
delivery 目标: qqbot:c2c:{sender_id}
delivery accountId: bot1
```

已有同名 cron 则更新，没有则新建。

### 4.4 /关早朝

将 `config-{sender_id}.json` 中的 enabled 设为 false，删除对应的 cron job。

cron job 名称：`morningcourt-{sender_id}`

---

## 5. 记录格式规范

### config 文件

存储在 morningcourt/ 目录下，按用户独立。文件命名：`config-{sender_id}.json`

```json
{
  "sender_id": "6687D4D2D1F8EDA5231C6809B1A26204",
  "time": "08:00",
  "enabled": true,
  "created_at": "2026-05-28T00:00:00+08:00"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| sender_id | string | 用户 QQ ID，用于按用户隔离配置 |
| time | string | 播报时间，24小时制 HH:MM |
| enabled | bool | 是否启用自动播报 |
| created_at | ISO-8601 | 创建时间 |

---

## 6. Son 返回格式规范

### 手动早朝简报
```
🌅 早朝官报到！

📋 今日待办：
1. [待办] 投递深圳科创学院简历（截止6月20日）

🌊 瓶海一瞥：
🍾 捞到一个瓶子 — "<内容摘要前20字>..."

📖 今日故事：
[故事或文学摘选，80-120字，注明作者和出处]

🥗 今日饮食推荐：
[1-2句时令饮食建议]

📸 今日摄影建议：
[1-2句摄影题材建议]

祝君一日顺利 ☀️
```

### 无待办时
待办部分改为：📋 今日暂无待办，一身轻松！

### 海中无瓶时
瓶海部分改为：🌊 海里还没有瓶子，没人扔也没人捞~

### 设时成功
```
✅ 早朝播报时间已设为 08:00
```

### 关早朝成功
```
✅ 自动播报已关闭，有事喊 /早朝 手动找我
```
