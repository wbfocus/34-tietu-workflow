# Agent 入口

本仓库是 **3:4 贴图工作流** 的完整可携带包。

开始任何出卡任务前，先 Read：

`.cursor/skills/34-tietu-workflow/SKILL.md`

并遵守 `.cursor/rules/34-tietu-workflow.mdc`（主题必问 + 三套共用文字与骨架）、`34-tietu-watermark-safe-zone.mdc`（水印与防裁切）、`plain-speech.mdc`（跟人说话、写标题都用会上能说出口的人话）、`push-with-chats.mdc`（推云端必带本会话聊天备份）。文字见 `references/type-shared.md`，版式见 `references/layout-shared.md`。

金标准：`examples/gold-a-ceo-star-dark/`、`examples/gold-b-ceo-star-light/`、`examples/gold-c-workshop-editorial/`。
成型样例：`examples/sample-gm-variance-dark/`。
新产出：`workspace/HTMLcards/`。

## 出作品模式简称（口语）

| 简称 | 全称 | Skill | 一句话 |
|---|---|---|---|
| **轮播** | 贴图套图 + 5 秒丝滑轮播 | `34-tietu-workflow` | 多页卡 → PNG → 翻页 MP4 + BGM |
| **橱窗** | 橱窗砸入 | `34-tietu-showcase` | 顶部目录胶囊 + 空镜 + 砸入（不覆盖轮播） |
| **上滑** | 长图上滑 | `34-eli5-scroll` | 一张长卷 → 从下往上滑弹出（无 BGM / 无口播） |

说「做一套轮播 / 橱窗 / 上滑」即指上表；主题仍先问 A / B / C。

**上滑默认多样式**：复用贴图六种版式节奏（大圆判断 / 分层 / 网格 / 清单 / 对比 / 收口），一套 ≥5 种；禁止只堆模板四段。见 `34-eli5-scroll/references/card-ui-from-34.md`。

**成品禁词**：上滑作品画面与交付文件名禁止出现 `ELI5`/`eli5`；工作文件夹和成片都用 `上滑_YYYY-MM-DD_标题（深色|浅色|刊物）`。

橱窗砸入成片（顶部目录胶囊，**3:4 · 1080×1440**，不替代默认 5 秒轮播）见 `.cursor/skills/34-tietu-showcase/SKILL.md`。

长图上滑（390px 长卷 → 高清 PNG → 3:4 上滑弹出视频，气泡音、无 BGM / 无口播）见 `.cursor/skills/34-eli5-scroll/SKILL.md`。

出图后必须自检：竖向铺满（底不能空一大块）+ 橱窗音效只在切页（静持/空镜不得乱响）。脚本：`.cursor/skills/34-tietu-workflow/scripts/qa_tietu.py`。

## 成片与文件夹命名

工作文件夹和 MP4 同一套：`模式_YYYY-MM-DD_标题（深色|浅色|刊物）`。  
例：`上滑_2026-09-11_毛利根本不是一回事（深色）.mp4`。带封面加 `（带封面）`。  
禁止 `showcase.mp4` / `长图-…` / 文件名带 `eli5`。脚本：`.cursor/skills/34-tietu-workflow/scripts/delivery_names.py`。

## 推云端必带聊天记录

用户要 `git push` / 推云端时：先把本会话 transcript 拷到 `workspace/chats/`，更新该目录 README，再和代码一起提交推送。  
规则见 `.cursor/rules/push-with-chats.mdc`。换机靠这份备份接话，不要只靠本机 Cursor 历史。
