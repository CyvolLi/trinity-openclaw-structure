# users/ — 多用户画像目录

每个 QQ 用户一个独立子目录，目录名 = sender_id（QQ号）。

```
users/
├── _template/           ← 新用户 User.md 模板
│   └── User.md
├── 123456789/
│   └── User.md
└── ...
```

## Father 操作规范

### 收到消息时
```bash
sender_id = 消息中的QQ号
user_dir  = ~/.openclaw/workspace-father/users/{sender_id}/
user_file = {user_dir}/User.md

if 文件存在 → read {user_file}，用上次记录的风格回复
if 不存在    → mkdir -p {user_dir} && cp _template/User.md {user_file}
               → 按新用户引导处理
```

### 对话结束时
```bash
# 覆盖写对应用户的 User.md
write ~/.openclaw/workspace-father/users/{sender_id}/User.md
```
