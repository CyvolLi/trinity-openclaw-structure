# floatbottle_function.md — 漂流瓶功能定义

> 本文件由 Spirit 维护，Son 执行时严格参照。
> 注册新功能时以此文件为格式模板：复制 → 改 `xxx` → 填各章节。

---

## 1. 功能描述

漂流瓶：用户匿名"扔"一条消息到公共瓶海，也能随机"捞"起他人扔的瓶子。捞到后可以查看瓶子内容和历史回复（如有），并决定是否回复。

---

## 2. 工作文件夹

Son 在其工作区内创建和维护：

```
~/.openclaw/workspace-son/floatbottle/
├── floatbottle.db    # SQLite 数据库（含所有瓶子记录）
```

### 数据库表 bottles
| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 唯一标识 BTL-YYYYMMDD-NNNN |
| content | TEXT | 瓶子内容 |
| sender_id | TEXT | 扔瓶者 QQ ID |
| created_at | TEXT | ISO 8601 时间戳 |
| status | TEXT | active / deleted |
| replies | TEXT | JSON 数组字符串 |

### 索引
- bottles(id) — 主键
- bottles(status) — 按状态筛选

---

## 3. 触发指令

| 指令 | 参数 | 说明 |
|------|------|------|
| `/扔瓶子 <内容>` | 必填：瓶中信内容 | 匿名扔一个瓶子到海中 |
| `/捞瓶子` | 无 | 随机捞起一个瓶子 |
| `/看瓶子` | 无 | 查看当前瓶海中所有瓶子的摘要 |
| `/回复瓶子 <ID> <内容>` | 必填：瓶子ID + 回复内容 | 对捞到的瓶子进行回复 |

---

## 4. 执行接口

### 4.1 /扔瓶子

Son 执行步骤：
1. 接收 Father 传来的用户输入内容和 sender_id
2. 生成唯一瓶子 ID（格式：`BTL-YYYYMMDD-XXXX`）
   - SQL: `SELECT id FROM bottles WHERE id LIKE 'BTL-{YYYYMMDD}-%' ORDER BY id DESC LIMIT 1`
   - 取后缀 +1，4 位补零
3. 写入 SQLite: `INSERT INTO bottles (id, content, sender_id, created_at, status, replies) VALUES (?, ?, ?, ?, 'active', '[]')`
4. 返回 Father："瓶子已扔入海中" + 瓶子 ID

### 4.2 /捞瓶子

Son 执行步骤：
1. SQL 查询所有 active 瓶子：`SELECT id, content, replies FROM bottles WHERE status='active'`
2. 随机选取一个（如无则返回"海中还没有瓶子"）
3. 按模板返回

### 4.3 /看瓶子

Son 执行步骤：
1. SQL 统计总数 + 前 5 条：`SELECT id, substr(content,1,30) AS brief, json_array_length(replies) AS reply_cnt FROM bottles WHERE status='active' ORDER BY created_at DESC LIMIT 5`
2. 按模板返回摘要

### 4.4 /回复瓶子

Son 执行步骤：
1. SQL 查找瓶子：`SELECT replies FROM bottles WHERE id='{ID}'`
2. 如无结果，返回"未找到该瓶子"
3. 构造新回复对象，追加到 replies JSON 数组
4. SQL 更新：`UPDATE bottles SET replies='{new_replies_json}' WHERE id='{ID}'`
5. 返回："已回复瓶子 {ID}"
## 5. 数据库字段说明

### 数据库表 bottles 字段
| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| id | TEXT PK | yes | 唯一标识 BTL-YYYYMMDD-NNNN |
| content | TEXT | yes | 瓶子内容 |
| sender_id | TEXT | yes | 扔瓶者的 QQ 用户 ID |
| created_at | TEXT | yes | ISO 8601 扔瓶时间 |
| status | TEXT | yes | active / deleted |
| replies | TEXT | no | JSON 数组字符串 |

### ID 生成
格式：`BTL-YYYYMMDD-NNNN`
- 查询当日最大序号：`SELECT id FROM bottles WHERE id LIKE 'BTL-{YYYYMMDD}-%' ORDER BY id DESC LIMIT 1`
- 取后缀 +1，4 位补零

### replies 结构
```json
[
  {
    "content": "回复内容",
    "sender_id": "6687D4D2D1F8EDA5231C6809B1A26204",
    "timestamp": "2026-05-28T12:30:00+08:00"
  }
]
```
## 6. Son 返回格式规范

Son 完成任务后，按以下模板返回 Father（Father 直接转述给用户）：

### 扔瓶子成功
```
🌊 瓶子已扔入海中！
📮 ID: `BTL-YYYYMMDD-XXXX`
```

### 捞到瓶子
```
🍾 捞到一个瓶子！
📮 ID: <ID>
📝 内容: "<content>"
💬 回复: N 条
```

如有回复则追加：
```
---
🗨️ 回复 1: "<content>"（<timestamp>）
🗨️ 回复 2: "<content>"（<timestamp>）
```

### 捞瓶子失败（空海）
```
🌊 海中还没有瓶子... 你来做第一个扔瓶子的人吧！
```

### 看瓶子
```
🌊 海中目前有 N 个瓶子：

1. `<ID>` | "<content前20字>..." | N 条回复
2. ...
```

### 回复成功
```
✅ 已回复瓶子 `<ID>`
```
