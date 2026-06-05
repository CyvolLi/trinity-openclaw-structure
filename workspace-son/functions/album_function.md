# album_function.md — 相册笔记功能定义

## 1. 功能描述
接收用户发送的图片并附上注释文字，解析注释后一起存入个人相册库，支持按注释内容搜索和按标签浏览。

## 1a. 模型配置
| 动作 (action) | 模型 | 理由 |
|---------------|------|------|
| save | `dashscope/qwen3-vl-flash` | 需视觉模型分析图片内容 |
| list | 不指定（Son 默认） | 纯文本 SQL 查询 |
| view | 不指定（Son 默认） | 纯文本 SQL 查询 |
| search | 不指定（Son 默认） | 纯文本 SQL 查询 |
| delete | 不指定（Son 默认） | 纯文本 SQL 查询 |

## 2. 工作文件夹
Son 工作区内路径: `~/.openclaw/workspace-son/album/`

存储结构：
```
album/
├── images/                  # 图片文件存储
│   └── {sender_id}/         # 按用户分目录
│       ├── ALB-YYYYMMDD-NNNN.jpg
│       └── ...
└── album.db                 # SQLite 数据库（含所有记录）
```

数据库表 `photos`：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 唯一标识 ALB-YYYYMMDD-NNNN |
| timestamp | TEXT | ISO 8601 时间戳 |
| sender_id | TEXT | 用户 QQ ID |
| filename | TEXT | images/ 下的文件名 |
| orig_name | TEXT | 原始文件名 |
| size_bytes | INTEGER | 文件大小 |
| annotation | TEXT | 注释正文 |
| analysis | TEXT | 图片分析结果 |
| tags | TEXT | 逗号分隔标签，如 `夕阳,摄影` |
| source | TEXT | 消息来源 |

索引：sender_id + timestamp DESC，按用户和时间快速查询。

## 3. 触发指令

| 指令 | 参数 | 说明 |
|------|------|------|
| `/存照片 [注释文字]` | 图片（上下文附件）+ 可选注释文字 | 存入一张照片，解析注释后存储 |
| `/看相册 [标签名]` | 可选：标签名 | 浏览相册，不带标签则显示全部，带标签则筛选 |
| `/看照片 <序号>` | 序号（必填），如 `1` 代表最新一张 | 按相册列表的序号查看照片，单独发送到聊天中 |
| `/搜照片 <关键词>` | 关键词（必填） | 搜索注释文字中包含关键词的照片 |
| `/删照片 <ID>` | 照片 ID（必填） | 删除指定照片及其记录 |

## 4. 执行接口

### 4.1 存照片 (save)
Son 执行步骤:
1. 从上下文消息中获取图片附件、注释文字和 sender_id
2. 生成唯一 ID：`ALB-YYYYMMDD-NNNN`（按日流水）
3. 解析注释文字：
   - 整段文字作为 `annotation`（注释正文）
   - 放到 `analysis`(AI按要求解析内容)
   - 如果文字中包含 `#标签` 格式的内容，提取为 `tags`（逗号分隔，如 `夕阳,摄影`）
4. 保存图片到 `album/images/{sender_id}/{ID}.{ext}`
5. 如需分析图片内容（如生成 analysis 字段），必须调用 `dashscope/qwen3-vl-flash` 视觉模型分析原图，不得依赖通道附带的 Description 文本
6. 写入 SQLite：`INSERT INTO photos VALUES (...)`
7. 在返回文本末尾追加 `FILE:/root/.openclaw/workspace-son/album/images/{sender_id}/{ID}.{ext}` 行
8. 返回保存结果给 Father（Father 收到后根据 FILE: 行发出 MEDIA 附件）

### 4.2 看相册 (list)
Son 执行步骤:
1. SQL 查询：`SELECT id, annotation, tags, timestamp FROM photos WHERE sender_id='{sender_id}' ORDER BY timestamp DESC LIMIT 20`
2. 如果指定了标签名，加条件 `AND tags LIKE '%{标签名}%'`
3. 按第 6 节格式拼文本返回

### 4.3 搜照片 (search)
Son 执行步骤:
1. SQL 查询：`SELECT id, annotation, tags, timestamp FROM photos WHERE sender_id='{sender_id}' AND (annotation LIKE '%{关键词}%' OR analysis LIKE '%{关键词}%') ORDER BY timestamp DESC LIMIT 20`
2. 按第 6 节格式拼文本返回

### 4.4 看照片 (view)
参数说明：用户输入的是序号，如 `1` 代表该用户相册中最新的那张，`2` 代表第二新的。

Son 执行步骤:
1. SQL 查询：`SELECT id, annotation, tags, filename, timestamp FROM photos WHERE sender_id='{sender_id}' ORDER BY timestamp DESC`
2. 取第 N 条：`LIMIT 1 OFFSET {N-1}`
3. 如结果为空（序号超出范围），返回错误"相册只有 N 张照片，没有第 X 张"
4. 在返回文本末尾追加 `FILE:/root/.openclaw/workspace-son/album/images/{sender_id}/{filename}` 行

Father 收到后根据 FILE: 行发出 MEDIA 附件。

### 4.5 删照片 (delete)
Son 执行步骤:
1. SQL 查询：`SELECT filename FROM photos WHERE id='{ID}' AND sender_id='{sender_id}'`
2. 如无结果，返回错误"未找到该照片记录"
3. 删除 `album/images/{sender_id}/{filename}` 文件
4. SQL 删除：`DELETE FROM photos WHERE id='{ID}' AND sender_id='{sender_id}'`
5. 返回删除成功

## 5. 数据库字段说明

### 文件命名
图片文件：`ALB-YYYYMMDD-NNNN.{ext}`（ext 保持原扩展名，如 jpg/png/gif/webp）

图片按 sender_id 分目录存储：`album/images/{sender_id}/ALB-YYYYMMDD-NNNN.{ext}`

### 数据库表 photos 字段
| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| id | TEXT PK | ✅ | 唯一标识 ALB-YYYYMMDD-NNNN |
| timestamp | TEXT | ✅ | ISO 8601 存入时间 |
| sender_id | TEXT | ✅ | 用户 QQ ID，按用户隔离数据 |
| filename | TEXT | ✅ | album/images/ 下的文件名 |
| orig_name | TEXT | ✅ | 用户上传时原始文件名 |
| size_bytes | INTEGER | ✅ | 图片文件大小（字节） |
| annotation | TEXT | ✅ | 注释正文，无则空字符串 |
| analysis | TEXT | ❌ | AI 解析内容 |
| tags | TEXT | ❌ | 逗号分隔标签，如 `夕阳,摄影` |
| source | TEXT | ✅ | 消息来源，固定 "qqbot" |

### ID 生成
格式：`ALB-YYYYMMDD-NNNN`
- 查询当日最大序号：`SELECT id FROM photos WHERE id LIKE 'ALB-{YYYYMMDD}-%' ORDER BY id DESC LIMIT 1`
- 取后缀 +1，4 位补零

## 6. Son 返回格式规范

### 存照片成功
```
📸 已存 1 张照片！
━━━━━━━━━━━━━━━━━
ID: ALB-20260528-0001
注释: "今天拍的夕阳，特别美"
标签: #夕阳 #摄影
━━━━━━━━━━━━━━━━━
查看全部: /看相册
```

Son 不再直接发出 MEDIA 指令。在文本末尾追加 `FILE:<绝对路径>` 行，Father 收到后自动解析并发出 MEDIA 附件。

### 存照片失败（无图片）
```
⚠️ 请先发送图片再使用 /存照片
例如：先发一张照片，然后回复 /存照片 今天天气真好
```

### 看相册
```
📖 相册 (共 N 张)

1. ALB-20260528-0001 | 今天拍的夕阳，特别美
   #夕阳 #摄影 | 2026-05-28 15:10\n

2. ALB-20260527-0003 | 午饭吃的咖喱饭
   #美食 | 2026-05-27 12:30\n

---

查看详情: /搜照片 <关键词>
标签浏览: /看相册 #标签
查看图片: /看照片 <ID>
```

### 看相册（空）
```
📖 相册为空
试试 /存照片 来存入第一张照片吧！
```

### 搜照片结果
```
🔍 搜索"夕阳"结果 (共 2 张)

1. ALB-20260528-0001 | ...拍了**夕阳**...
   #夕阳 #摄影 | 2026-05-28 15:10

2. ALB-20260526-0002 | **夕阳**下的海边散步
   #海边 #心情 | 2026-05-26 18:20
```

### 搜照片无结果
```
🔍 未找到包含"xxx"的照片
试试其他关键词 /搜照片 <关键词>
```

### 删照片成功
```
🗑️ 已删除照片 ALB-20260528-0001
```

### 删照片失败（不存在）
```
⚠️ 未找到照片 ALB-xxxx，请核对 ID
可用 /看相册 查看全部照片
```
