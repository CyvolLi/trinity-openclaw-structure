# memo_function.md — 备忘录功能定义

> 本文件由 Spirit 维护，Son 执行时严格参照。

---

## 1. 功能描述

个人备忘录：用户可以记录待办事项，查看所有备忘录，修改已有内容，切换待办/已完成状态，删除不需要的备忘。

---

## 2. 工作文件夹

Son 在其工作区内创建和维护：

```
~/.openclaw/workspace-son/memo/
├── memo.db           # SQLite 数据库（含所有备忘录记录）
```

### 数据库表 memos
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 序号（按用户独立，不同用户从1开始） |
| sender_id | TEXT | 用户 QQ ID |
| content | TEXT | 备忘录内容 |
| created_at | TEXT | ISO 8601 创建时间 |
| updated_at | TEXT | ISO 8601 更新时间 |
| status | TEXT | pending / completed / deleted |
| PK | (sender_id, id) | 复合主键 |

### 索引
- memos(sender_id, id) — 复合主键
- memos(sender_id, status) — 按用户+状态查询

---

## 3. 触发指令

| 指令 | 参数 | 说明 |
|------|------|------|
| `/记备忘录 <内容>` | 必填：备忘录内容 | 记录一条新备忘录 |
| `/看备忘录` | 无 | 查看所有备忘录 |
| `/改备忘录 <id> <新内容>` | 必填：序号+新内容 | 修改指定备忘录的内容 |
| `/修改状态 <id>` | 必填：序号 | 切换待办 ↔ 已完成状态 |
| `/删备忘录 <id>` | 必填：序号 | 删除指定备忘录 |

---

## 4. 执行接口

### 4.1 /记备忘录

Son 执行步骤：
1. 接收 Father 传来的用户输入内容和 sender_id
2. 确定新序号：`SELECT COALESCE(MAX(id), 0) + 1 FROM memos WHERE sender_id='{sender_id}'`
3. 写入 SQLite：`INSERT INTO memos (id, sender_id, content, created_at, updated_at, status) VALUES (?, ?, ?, ?, ?, 'pending')`
4. 返回："已记录备忘录 #<id>"

### 4.2 /看备忘录

Son 执行步骤：
1. SQL：`SELECT id, content, status FROM memos WHERE sender_id='{sender_id}' AND status!='deleted' ORDER BY id`
2. 如无，返回："暂无备忘录"
3. 按模板返回列表

### 4.3 /改备忘录

Son 执行步骤：
1. SQL：`SELECT id FROM memos WHERE id={id} AND sender_id='{sender_id}'`
2. 如无结果，返回"未找到或无权修改"
3. SQL 更新：`UPDATE memos SET content='{新内容}', updated_at='{当前时间}' WHERE id={id} AND sender_id='{sender_id}'`
4. 返回："已修改备忘录 #<id>"

### 4.4 /修改状态

Son 执行步骤：
1. SQL：`SELECT status FROM memos WHERE id={id} AND sender_id='{sender_id}'`
2. 如无结果，返回"未找到"
3. 切换状态：pending <-> completed
4. SQL 更新：`UPDATE memos SET status='{new_status}', updated_at='{当前时间}' WHERE id={id} AND sender_id='{sender_id}'`
5. 返回："备忘录 #<id> 状态已切换"

### 4.5 /删备忘录

Son 执行步骤：
1. SQL：`SELECT id FROM memos WHERE id={id} AND sender_id='{sender_id}'`
2. 如无结果，返回"未找到"
3. SQL 软删除：`UPDATE memos SET status='deleted', updated_at='{当前时间}' WHERE id={id} AND sender_id='{sender_id}'`
4. 返回："已删除备忘录 #<id>"
## 5. 数据库字段说明

### 数据库表 memos 字段
| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| id | INTEGER | yes | 序号（按用户独立，不同用户从1开始） |
| sender_id | TEXT | yes | 用户 QQ ID |
| content | TEXT | yes | 备忘录内容 |
| created_at | TEXT | yes | ISO 8601 创建时间 |
| updated_at | TEXT | yes | ISO 8601 更新时间 |
| status | TEXT | yes | pending / completed / deleted |
| PK | (sender_id, id) | yes | 复合主键 |
# 查看列表（有内容）
```
📋 备忘录列表：

1. [待办] 买菜
2. [已完成] 写作业
```

### 查看列表（空）
```
📋 暂无备忘录
```

### 修改成功
```
✅ 已修改备忘录 #1
```

### 状态切换成功
```
✅ 备忘录 #1 状态已切换为 [已完成]
```

### 删除成功
```
✅ 已删除备忘录 #1
```

### 未找到
```
❌ 未找到备忘录 #<id>
```
