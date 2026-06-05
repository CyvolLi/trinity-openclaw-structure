# functions_manifest.md — Son 功能路由清单

> 每次 spawn 时自动加载。收到 Father 的指令后根据 `function` 字段定位对应功能定义文件。
> 
> 路径规则：`functions/{function}_function.md`

---

## 已注册功能

| Function ID | 功能名 | 定义文件 | 数据目录 |
|-------------|--------|---------|---------|
| floatbottle | 漂流瓶 | `functions/floatbottle_function.md` | `floatbottle/` |
| memo | 备忘录 | `functions/memo_function.md` | `memo/` |
| morningcourt | 早朝官 | `functions/morningcourt_function.md` | `morningcourt/` |
| album | 相册笔记 | `functions/album_function.md` | `album/` |
| draw | 画图 | `functions/draw_function.md` | `draw/` |
| compose | 作曲 | `functions/compose_function.md` | `compose/` |
| stench_number | 恶臭数字 | `functions/stench_number_function.md` | `stench_number/` |

---

## 执行指引

### 来自 Father 的指令

收到 Father 传过来的指令（JSON 格式）后：

1. 读 `functions_manifest.md` 确认 function 已注册
2. 读 `functions/{function}_function.md` 定位对应执行接口
3. 按第 4 节「执行接口」中对应 action 的步骤执行
4. 按第 6 节「返回格式规范」拼接并返回

> 不需要再从 Spirit 工作区读取任何文件。所有定义都在本目录下。

### 来自 cron 定时触发

Son 也可能是孤立 session 中由 cron 直接唤醒的。消息格式为：

```
[morningcourt] sender_id={sender_id}, trigger briefing generation
```

此时直接按 `function=morningcourt, action=manual` 处理，产出的 reply 由 cron 的 announce delivery 推给用户。
