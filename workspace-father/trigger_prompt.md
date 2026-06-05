# trigger_prompt.md — 已注册功能的触发词表

> Father 维护。用户发消息时，先扫描本表判断是否命中已注册功能。
> 
> 匹配原则：
> - 包含表中任一触发语 → 调用对应功能
> - 模糊匹配即可，不要求精确格式（比如"扔个瓶子"也命中 /扔瓶子）
> - 命中表中触发语时直接 spawn Son，传 {function, action, params} 指令
> - 表中无匹配 → Father 自行回复或转 Son 做非文本处理
> 
> **不再绕 Spirit。** 功能定义已迁移到 Son 的工作区，日常使用 Father → Son 直达。

---

## 已注册触发词

| 触发词 | 对应功能 | 处理路径 | Son 指令 |
|--------|---------|---------|----------|
| `/菜单` | 查看所有已注册功能 | Father → Spirit(bot_function_explain.md) | — |
| `/删除` | 删除指定功能 | Father → Spirit → 清理全部相关文件 | — |
| `/注册` | 注册新功能 | Father → Spirit → 创建 xxx_function.md → Father → Son(同步功能定义) | — |
| `/扔瓶子` `扔瓶子` `扔个瓶子` `丢瓶子` | 漂流瓶-扔 | → Son | `{function:floatbottle, action:throw, params:{content}}` |
| `/捞瓶子` `捞瓶子` `捞个瓶子` `捡瓶子` | 漂流瓶-捞 | → Son | `{function:floatbottle, action:pickup}` |
| `/看瓶子` `看瓶子` `瓶海` `有哪些瓶子` | 漂流瓶-查看 | → Son | `{function:floatbottle, action:list}` |
| `/回复瓶子` `回复瓶子` | 漂流瓶-回复 | → Son | `{function:floatbottle, action:reply, params:{id, content}}` |
| `/递话` `递话` `给*带个话` `给*带句话` `帮我给*说` | 递话 | → Father | — |
