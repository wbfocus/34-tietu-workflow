---
name: 34-eli5-scroll
description: ELI5 长图上滑出片。把概念做成 390px 手机长图 HTML，导出高清 PNG，再合成 1080×1440（3:4）从下往上滑的视频；卡片对象依次弹出并带气泡音效。不配 BGM、不配口播字幕。触发词：ELI5、eli5 长图、上滑视频、长图滚动、气泡弹出、大图少字。先问主题 A 深色玻璃 / B 亮色高级 / C 奶油刊物。
license: MIT
---

# ELI5 长图上滑（独立模式）

把复杂概念做成 **一张 390px 手机长卷**，再滚成 **3:4 · 1080×1440** 上滑视频。

**不是**多页 3:4 贴图套图。默认轮播 / 橱窗砸入不要走这里。

## 效果合同

1. 写 ELI5 HTML（390px 单列，大图少字）。
2. Playwright 导出 **高清长图 PNG**（公众号也能用）。
3. FFmpeg 做成 **从下往上滑** 的 3:4 视频：底板在爬，卡片/步骤块 **依次弹出**（淡入 + 上移）。
4. 每个对象出现时放一声 **气泡音效**。
5. **禁止 BGM、禁止口播、禁止字幕条。**

静态 PNG 自己不会逐个动画。出片时用「底板 + 每块精灵图」叠上去，所以 HTML 里的块必须能单独截下来（用 `data-eli5-reveal`）。

## 主题选择（第 0 步，每次必做）

与贴图同一套昨天优化过的 UI：

> 要做成 **ELI5 长图上滑**（先 390px 长图，再 3:4 上滑视频），请选主题：
> - **A 深色玻璃** — 夜间/科技感
> - **B 亮色高级** — 日间/Mesh 刊物感
> - **C 奶油刊物** — 奶油底 + 陶土橙 + 鼠尾草绿

| 选择 | 模板 | CSS | 文件夹后缀 |
|---|---|---|---|
| A | `templates/eli5-long-a.html` | `theme-a-long.css` | `（深色）` |
| B | `templates/eli5-long-b.html` | `theme-b-long.css` | `（浅色）` |
| C | `templates/eli5-long-c.html` | `theme-c-long.css` | `（刊物）` |

写之前读 `references/card-ui-from-34.md`。字体/组件类名与贴图共用（`.ui-title` / `.wenkai` / `.card-paper` / 坑修 / 原则框）。

**不必再问**：用户已说 A / B / C / 深色 / 浅色 / 奶油。

## 总流程

```text
0. 问主题 A / B / C
1. 复制对应模板 + layout-long.css + theme-X-long.css
   → workspace/HTMLcards/eli5-短标题（深色|浅色|刊物）/
2. 填 HTML（比喻 → 竖向流程 → 坑修 → 积木 → 原则框）
   每个要弹出的块保留 data-eli5-reveal
3. py -3 finish_eli5_scroll.py "<文件夹>"
4. 交付：成品图/long.png + cover-3x4.png + 成品视频/<文件夹>（上滑）.mp4
```

### 出片命令（仓库根目录）

```powershell
py -3 ".cursor/skills/34-tietu-workflow/scripts/finish_eli5_scroll.py" ".\workspace\HTMLcards\eli5-你的标题（刊物）"
```

也可拆开：

```powershell
node ".cursor/skills/34-tietu-workflow/scripts/harvest_eli5_scroll.mjs" ".\workspace\HTMLcards\eli5-你的标题（刊物）"
py -3 ".cursor/skills/34-tietu-workflow/scripts/eli5_scroll_video.py" ".\workspace\HTMLcards\eli5-你的标题（刊物）"
```

## HTML 铁律

- `html, body, .phone` 锁死 **390px**；单列；流程竖排。
- 外层必须是 `.phone#capture`。
- 主题 CSS 用相对路径：`layout-long.css` + `theme-a|b|c-long.css`（脚本会缺则拷进文件夹）。
- 要弹出的对象加 `data-eli5-reveal`（整张卡、步骤块、原则框各一块；不要把整页包成一个 reveal）。
- 水印 `.wm`、氛围 `.atm` / `.mesh` / `.noise` **不要**加 reveal。
- 全页至少 3 种区块骨架；原则框全页 ≤1。

## 成片规格

| 项 | 值 |
|---|---|
| 长图 | 宽 1080（390×2.769），高度随内容 |
| 视频 | **1080×1440 · 30fps · 约 18–90 秒** |
| 运动 | 内容上滑（窗口下移） |
| 入画 | 块进入画面后淡入 + 上移约 22px / 0.42s |
| 声音 | 仅 `assets/sfx/bubble-pop.wav`，跟弹出走 |
| 禁止 | BGM、口播、字幕、9:16 |

## 产出目录

```text
workspace/HTMLcards/eli5-短标题（刊物）/
  长图.html
  layout-long.css
  theme-c-long.css
  成品图/long.png
  成品图/cover-3x4.png
  成品视频/<文件夹>（上滑）.mp4
  harvest/plate.png
  harvest/sprites/
  harvest/timeline.json
```

## 完成后汇报

> 已生成 ELI5 长图（1080 宽）和 **3:4 上滑视频**（1080×1440，N 个对象弹出 + 气泡音，无 BGM / 无口播）。成品在 `…/成品图` 与 `…/成品视频`。
