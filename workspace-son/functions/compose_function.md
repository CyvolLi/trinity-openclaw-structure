# compose_function.md — 作曲功能定义

## 1. 功能描述
根据用户提供的作曲要求和上下文中的歌词信息，调用 AI 音乐生成能力创作乐曲（含旋律、编曲、风格设定），支持歌词配曲、纯音乐创作、风格参考等。

## 2. 工作文件夹
Son 工作区内路径: `compose/`

## 3. 触发指令

| 指令 | 参数 | 说明 |
|------|------|------|
| `/作曲` | `<描述/关键词>` | 按照描述内容创作新曲。歌词可通过请求附带 |
| `/作曲` | `#auto_lyrics` | 忽略附带歌词，让 AI 完全重新创作歌词 |
| `/作曲` | `#polish` | 对附带的歌词做押韵/节奏润色后再作曲 |
| `/作曲历史` | （无） | 查看最近创作乐曲记录 |
| `/重作曲` | `<描述>` | 基于上次结果，重新生成或修改 |

## 4. 执行接口

### 4.1 作曲

Son 执行步骤:
1. 从 params.lyrics 提取歌词文本（如果有）
2. 从 params.style / params.mood / params.tempo 提取风格/情绪/节奏参数
3. 若用户描述中未提供风格/情绪，则根据歌词内容自动推断
4. 判断是否纯音乐：如果用户未传 lyrics（或歌词为空）且不带 #polish / #auto_lyrics → `is_instrumental: true`（纯音乐）；如果用户传了 lyrics → `is_instrumental: false`（带人声）
5. 检查 prompt 中是否包含控制标签：
   - `#auto_lyrics`：忽略 params.lyrics，清空 lyrics，设 `lyrics_optimizer: true`，让 AI 完全重写歌词
   - `#polish`：将 params.lyrics 发给 LLM 做押韵/节奏润色，润色后的歌词传给 API，`lyrics_optimizer: false`
   - 无标签且 params.lyrics 存在 → 直接用原词，`lyrics_optimizer: false`
   - 无标签且 params.lyrics 为空 → `lyrics_optimizer: true`，AI 自动写词
5. **调用 MiniMax API 生成音乐（禁止使用本地 music21 合成）**：
   - 通过 curl 调用 `POST https://api.minimaxi.com/v1/music_generation`
   - 认证头：`Authorization: Bearer $MINIMAX_API_KEY`（从 `.env` 读取）
   - 请求体参数：
     ```json
     {
       "model": "music-2.6",
       "prompt": "{style描述} + {情绪描述}",
       "lyrics": "{歌词文本（如有）}",
       "lyrics_optimizer": true/false,
       "is_instrumental": true/false,
       "output_format": "url"
     }
     ```
   - 等待返回结果（约 1-3 分钟），从 `data.audio` 获取音频 URL
   - 用 curl 下载音频文件到 `compose/` 目录
6. 生成乐曲唯一 ID（格式: `COMPOSE-YYYYMMDD-NNNN`）
7. 将乐曲记录写入数据库（`compose.db`，表 `compositions`）
8. 准备双文件输出：
   - 将原始 mp3 复制到 `~/.openclaw/media/qqbot/`（用于 Father 后续以 `<qqmedia>` 直接播放）
   - 创建一份 `.mp3.bin` 副本到 `~/.openclaw/media/qqbot/`（用于 Father 后续以 `<qqmedia>` 发送文件供保存转发）
9. 返回结果给 Father，在文本末尾追加两行：
   - `FILE_AUDIO:~/.openclaw/media/qqbot/COMPOSE-YYYYMMDD-NNNN.mp3`
   - `FILE_BIN:~/.openclaw/media/qqbot/COMPOSE-YYYYMMDD-NNNN.mp3.bin`
   Father 收到后根据 FILE_AUDIO 和 FILE_BIN 行自动生成 `<qqmedia>` 标签发出。

### 4.2 查看作曲历史

Son 执行步骤:
1. 查询 `compose.db` 中该用户的最近 N 条记录（默认 5 条）
2. 格式化输出：每条包含标题、风格、情绪、创作日期
3. 若记录为空，返回"你还没有作曲记录，试试 /作曲 来创作你的第一首曲子吧！"

### 4.3 重作曲

Son 执行步骤:
1. 找到该用户上一次的作曲记录
2. 应用用户新的描述参数（风格/情绪/节奏等）
3. 保留同一条歌词（若有）或按新需求调整
4. 重新调用 AI 音乐生成能力
5. 写入新记录，ID 递增
6. 返回结果

## 5. 数据库字段说明

### 表名: `compositions`

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|:--:|------|
| id | TEXT | 是 | 作曲唯一 ID |
| user_id | TEXT | 是 | 群用户 ID（QQ 号或其他标识） |
| group_id | TEXT | 是 | QQ 群号 |
| title | TEXT | 否 | 曲名，可由用户指定或 AI 自动生成 |
| lyrics | TEXT | 否 | 歌词全文（纯文本，换行分隔） |
| style | TEXT | 是 | 曲风（流行/古典/民谣/电子/R&B 等） |
| mood | TEXT | 否 | 情绪标签（欢快/悲伤/激昂/温柔等） |
| tempo | TEXT | 否 | 节奏（快/中/慢） |
| duration_sec | INTEGER | 否 | 生成曲目的时长（秒） |
| prompt_raw | TEXT | 是 | 用户原始描述原文 |
| audio_file | TEXT | 否 | Son 生成/返回的音频文件路径或链接 |
| created_at | TEXT | 是 | 创作时间（ISO 8601 格式） |

### ID 生成规则
`COMPOSE-YYYYMMDD-NNNN`，其中 NNNN 为当日累计序号（从 0001 开始）。

## 6. Son 返回格式规范

### 6.1 作曲成功
```
🎵 新曲创作完成！
────────────────
🎼 曲名：{title}
🎸 风格：{style}
💖 情绪：{mood}
⏱  时长：{duration}
📝 歌词：
{lyrics_preview}
────────────────
FILE_AUDIO:~/.openclaw/media/qqbot/COMPOSE-YYYYMMDD-NNNN.mp3
FILE_BIN:~/.openclaw/media/qqbot/COMPOSE-YYYYMMDD-NNNN.mp3.bin
────────────────
想换风格试试？ /重作曲 我想要摇滚风
```

Son 不再直接嵌入 `<qqmedia>` 标签。末尾追加 `FILE_AUDIO:`（播放用）和 `FILE_BIN:`（保存用）两行，Father 收到后自动生成 `<qqmedia>` 标签。

### 6.2 作曲历史
```
📜 你的作曲历史（最近 {N} 首）：
────────────────
1. 🎵 {title_1} | {style} | {mood} | {date}
2. 🎵 {title_2} | {style} | {mood} | {date}
...
────────────────
回复曲名序号可试听，或 /作曲 创作新曲
```

### 6.3 空记录
```
📭 你还没有作曲记录
试试 /作曲 来创作你的第一首曲子吧！
```

### 6.4 参数缺失
```
⚠️ 请告诉我你想要什么风格的曲子
例如：/作曲 一首古风温柔的曲子
如果上下文有歌词，我会自动帮你配曲 :)
```
