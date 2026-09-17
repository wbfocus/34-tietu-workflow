# 对话归档

本目录保存本仓库相关 Cursor 对话记录（从本机 `agent-transcripts` 复制），便于换机对照。

换机交接给 Agent 读：`.cursor/rules/handoff-current.mdc`（alwaysApply）。本目录 jsonl 只作备份，文件名日期是开聊日。

**铁律**：每次 `git push` 推云端前，必须把当前会话备份到这里，并改 `CURRENT.md`，一起提交。见 `.cursor/rules/push-with-chats.mdc`。

| 文件 | 主题 |
|---|---|
| `CURRENT.md` | **换机进度指针**（做到哪、下一期） |
| `2026-09-08-b26fc70b-3比4贴图套图.jsonl` | 3:4 贴图套图工作流 |
| `2026-09-08-b26fc70b-3比4贴图套图-完整.jsonl` | 同上（完整备份） |
| `2026-09-09-ddfdf4e2-eli5长图上滑.jsonl` | 上滑嫁接、A/B 类业财、钉钉编码锁死、换机衔接（持续更新到 2026-09-17） |
| `2026-09-11-3c5e3c4e-环境恢复与上滑出片.jsonl` | 环境恢复与上滑出片 |
| `2026-09-11-3c5e3c4e-subagent.jsonl` | 子代理相关 |
| `2026-09-16-7bae3d21-命名规则与业财扫盲.jsonl` | 成片命名规则、正常人话约束、会上缩写橱窗 |
