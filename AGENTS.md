# Agent 入口

本仓库是 **3:4 贴图工作流** 的完整可携带包。

跨电脑进度写在 `.cursor/rules/handoff-current.mdc`（alwaysApply）。Agent 按那条继续，不要让用户去翻聊天或打开交接文件。

开始任何出卡任务前，Read：

`.cursor/skills/34-tietu-workflow/SKILL.md`

并遵守 `.cursor/rules/34-tietu-workflow.mdc`（主题必问 + 八套共用文字与骨架）、`34-tietu-watermark-safe-zone.mdc`（水印与防裁切）、`34-mp4-dingtalk.mdc`（成片必须钉钉/微信能播）、`plain-speech.mdc`（跟人说话、写标题都用会上能说出口的人话）、`corrections-log.mdc`（用户订正记流水账，出文案前必读）、`push-with-chats.mdc`（推云端必带本会话聊天备份）、`handoff-current.mdc`（跨电脑工作记忆，Agent 自动带上）。文字见 `references/type-shared.md`，版式见 `references/layout-shared.md`。

用户亲手改过的句子记在：`workspace/corrections/订正流水账.md`。写画面文案前必读；用户每更正一次必须追加一条。

金标准：`examples/gold-a-ceo-star-dark/`、`examples/gold-b-ceo-star-light/`、`examples/gold-c-workshop-editorial/`。
成型样例：`examples/sample-gm-variance-dark/`。
新产出：`workspace/HTMLcards/`。

## 出作品模式简称（口语）

| 简称 | 全称 | Skill | 一句话 |
|---|---|---|---|
| **轮播** | 贴图套图 + 5 秒丝滑轮播 | `34-tietu-workflow` | 多页卡 → PNG → 翻页 MP4 + BGM |
| **橱窗** | 橱窗砸入 | `34-tietu-showcase` | 顶部目录胶囊 + 空镜 + 砸入（不覆盖轮播） |
| **上滑** | 长图上滑 | `34-eli5-scroll` | 一张长卷 → 从下往上滑弹出（BGM + 气泡 / 无口播）；出片后写短标题+关键词 |

说「做一套轮播 / 橱窗 / 上滑」即指上表；主题仍先问 A / B / C / D。

**上滑默认多样式**：复用贴图六种版式节奏（大圆判断 / 分层 / 网格 / 清单 / 对比 / 收口），一套 ≥5 种；禁止只堆模板四段。见 `34-eli5-scroll/references/card-ui-from-34.md`。

**成品禁词**：上滑作品画面与交付文件名禁止出现 `ELI5`/`eli5`；工作文件夹和成片都用 `上滑_YYYY-MM-DD_标题（深色|浅色|刊物）`。

橱窗砸入成片（顶部目录胶囊，**3:4 · 1080×1440**，不替代默认 5 秒轮播）见 `.cursor/skills/34-tietu-showcase/SKILL.md`。

长图上滑（390px 长卷 → 高清 PNG → 3:4 上滑弹出视频，气泡音 + 曲库随机 BGM 跳过前奏、无口播）见 `.cursor/skills/34-eli5-scroll/SKILL.md`。

出图后必须自检：竖向铺满（底不能空一大块）+ 橱窗音效只在切页（静持/空镜不得乱响）+ **成片编码**（整 30fps、15360 tbn、High 4.0，钉钉/微信能播）。脚本：`.cursor/skills/34-tietu-workflow/scripts/qa_tietu.py`。

## 成片与文件夹命名

工作文件夹和 MP4 同一套：`模式_YYYY-MM-DD_标题（深色|浅色|刊物|蓝图|墨纸|石板|海报|地铁）`。 
例：`上滑_2026-09-19_如何管好应收账款（墨纸）.mp4`。带封面加 `（带封面）`。 
禁止 `showcase.mp4` / `长图-…` / 文件名带 `eli5`。脚本：`.cursor/skills/34-tietu-workflow/scripts/delivery_names.py`。

## 推云端必带聊天记录

用户要 `git push` / 推云端时：先把本会话 transcript 拷到 `workspace/chats/`，更新 `handoff-current.mdc` 与 `CURRENT.md` 里的「当前状态」，再和代码一起提交推送。  
规则见 `.cursor/rules/push-with-chats.mdc`。
