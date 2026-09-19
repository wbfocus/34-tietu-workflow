---
name: 34-eli5-scroll
description: ELI5 长图上滑出片。把概念做成 390px 手机长图 HTML，导出高清 PNG，再合成 1080×1440（3:4）从下往上滑的视频；卡片对象依次弹出并带气泡音效，默认从曲库轮流叠 BGM（按曲跳前奏）。不配口播字幕。触发词：ELI5、eli5 长图、上滑视频、长图滚动、气泡弹出、大图少字。先问主题 A–K。
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
5. **默认配 BGM**（`assets/audio/` 曲库轮流一首，避开最近用过的；**每首歌前奏秒数不同**，见 `bgm-intro-skip.json`，压在气泡下）；**禁止口播、禁止字幕条。** 例外才 `--no-bgm`；指定曲目用 `--bgm`。历史见 `34-tietu-workflow/assets/media-rotation.json`。

静态 PNG 自己不会逐个动画。出片时用「底板 + 每块精灵图」叠上去，所以 HTML 里的块必须能单独截下来（用 `data-eli5-reveal`）。

## 主题选择（第 0 步，每次必做）

与贴图同一套昨天优化过的 UI：

> 要做成 **长图上滑**（先 390px 长图，再 3:4 上滑视频），请选主题：
> - **A 深色玻璃** — 夜间/科技感
> - **B 亮色高级** — 日间/Mesh 刊物感
> - **C 奶油刊物** — 奶油底 + 陶土橙 + 鼠尾草绿
> - **D 工程蓝图** — 藏蓝网格 + 青线描边（图纸感）
> - **E 墨纸朱印** — 冷灰纸 + 朱砂印（账本感）
> - **F 石板粉笔** — 深绿石板 + 粉笔黄（课堂感）
> - **G 丝网海报** — 朱红靛蓝叠印（海报感）
> - **H 地铁线路** — 导视图彩线站点
> - **I 货柜码头** — 港湾深蓝 + 集装箱橙
> - **J 积木乐园** — 米白底红黄蓝色块
> - **K 便签墙** — 暖橙墙粉青便签

| 选择 | 模板 | CSS | 文件夹后缀 |
|---|---|---|---|
| A | `templates/eli5-long-a.html` | `theme-a-long.css` | `（深色）` |
| B | `templates/eli5-long-b.html` | `theme-b-long.css` | `（浅色）` |
| C | `templates/eli5-long-c.html` | `theme-c-long.css` | `（刊物）` |
| D | `templates/eli5-long-d.html` | `theme-d-long.css` | `（蓝图）` |
| E | `templates/eli5-long-e.html` | `theme-e-long.css` | `（墨纸）` |
| F | `templates/eli5-long-f.html` | `theme-f-long.css` | `（石板）` |
| G | `templates/eli5-long-g.html` | `theme-g-long.css` | `（海报）` |
| H | `templates/eli5-long-h.html` | `theme-h-long.css` | `（地铁）` |
| I | `templates/eli5-long-i.html` | `theme-i-long.css` | `（货柜）` |
| J | `templates/eli5-long-j.html` | `theme-j-long.css` | `（积木）` |
| K | `templates/eli5-long-k.html` | `theme-k-long.css` | `（便签）` |

写之前读 `references/card-ui-from-34.md`。字体/组件类名与贴图共用（`.ui-title` / `.wenkai` / `.card-paper` / 坑修 / 原则框）。  
写文案前必读 `workspace/corrections/订正流水账.md`（用户亲手改过的句子，禁止再犯）。
书页改编：案例与数据**另拟**，禁止照抄原文；适当位置用第一人称老汪观察（见 `plain-speech.mdc`）。

**不必再问**：用户已说 A / B / C / D / E / 深色 / 浅色 / 奶油 / 蓝图 / 墨纸 / 图纸。

## 总流程

```text
0. 问主题 A–I
1. 复制对应模板 + layout-long.css + theme-X-long.css
   → workspace/HTMLcards/上滑_YYYY-MM-DD_短标题（深色|浅色|刊物|蓝图|墨纸|石板|海报|地铁|货柜）/
2. 填 HTML（比喻 → 竖向流程 → 坑修 → 积木 → 原则框）
   每个要弹出的块保留 data-eli5-reveal
3. py -3 finish_eli5_scroll.py "<文件夹>"
   （封面文案可加 --title "第一行|第二行" --sub "副标" --pill "经营分析小卡片"；**不要默认 --style 4**，空则自动换封面并渲备选）
4. 交付：成品图/long.png + 封面/cover-3x4.png + 封面/备选/ + 成品视频/`上滑_…（货柜）.mp4` + 同名`（带封面）`
5. 【必做】根据成片内容写 `配套文案与关键词.md`
   → 短标题备选 5～8 条 + 关键词 3～4 组（写法见 34-tietu-workflow/references/caption-keywords.md）
```

出片后 **不能只交视频**：同目录必须有 `配套文案与关键词.md`，方便发视频号 / 抖音 / 朋友圈时直接选标题和话题。
### 出片命令（仓库根目录）

```powershell
py -3 ".cursor/skills/34-tietu-workflow/scripts/finish_eli5_scroll.py" ".\workspace\HTMLcards\上滑_YYYY-MM-DD_你的标题（刊物）"
```

也可拆开：

```powershell
node ".cursor/skills/34-tietu-workflow/scripts/harvest_eli5_scroll.mjs" ".\workspace\HTMLcards\上滑_YYYY-MM-DD_你的标题（刊物）"
py -3 ".cursor/skills/34-tietu-workflow/scripts/eli5_scroll_video.py" ".\workspace\HTMLcards\上滑_YYYY-MM-DD_你的标题（刊物）"
py -3 ".cursor/skills/34-tietu-workflow/scripts/finish_eli5_scroll.py" ".\workspace\HTMLcards\上滑_YYYY-MM-DD_你的标题（刊物）" --cover-only --title "第一行|第二行" --sub "副标"
```

封面走贴图同一套 `covers-3x4/`（居中大字、最多两行，每行尽量 ≤6 字），写入 `封面/cover-3x4.png`，再拼成片 **第 0 帧仅 1 帧** → `上滑_YYYY-MM-DD_标题（主题）（带封面）.mp4`。不要把长图头顶裁成封面。

## HTML 铁律

- `html, body, .phone` 锁死 **390px**；单列；流程竖排。
- 外层必须是 `.phone#capture`。
- 主题 CSS 用相对路径：`layout-long.css` + `theme-a|b|c-long.css`（脚本会缺则拷进文件夹）。
- 要弹出的对象加 `data-eli5-reveal`（整张卡、步骤块、原则框各一块；不要把整页包成一个 reveal）。
- 水印 `.wm`、氛围 `.atm` / `.mesh` / `.noise` **不要**加 reveal。
- 原则框全页 ≤1；与上方块必须留空（`layout-long.css` 里 `.card-principle { margin-top: 16px }`，主题 CSS 不得清零）。

### 成品禁词（铁律）

**作品画面与交付文件名禁止出现 `ELI5` / `eli5` 字样**（含页眉英文小标、页脚、封面、`<title>`、成片文件名）。  
「ELI5」只作内部 skill / 脚本名；读者侧统一说「上滑 / 长图」。

| 位置 | 禁止 | 改用 |
|---|---|---|
| `.c-en` | `ELI5` | 选题英文词，如 `BOOK` / `COST` / `STOCK` |
| `.c-foot` 右侧 | `ELI5 长卷` | `长图信息` 或短主题名 |
| 文件夹 | `eli5-标题…` / `长图-标题` | `上滑_YYYY-MM-DD_标题（深色\|浅色\|刊物\|蓝图\|墨纸）` |
| 成片名 | 带 `eli5` | `上滑_YYYY-MM-DD_标题（深色\|浅色\|刊物\|蓝图\|墨纸）.mp4` |

### 多样式铁律（默认必做，用户不必再提醒）

上滑长图 **必须** 复用贴图/橱窗同一套版式组件（见 `34-tietu-workflow/references/layout-shared.md` + `references/card-ui-from-34.md`），**禁止**只堆「比喻卡 + 竖流程 + 坑修 + 积木」四段流水账。

一套长卷至少覆盖下面 **≥5 种**（可按内容删减，但不得少于 5）：

| 节奏 | 组件 | 说明 |
|---|---|---|
| 封面开场 | `.hero-orb` + `.pill-dark` + 标签行 | 大圆数字 / 判断句 / chip |
| 比喻 | `.card-paper.story` + `.hl-bar` / `.card-callout` | 生活类比 + 一句定义 |
| 竖向流程 | `.flow` + `.box` | 怎么转起来 |
| 分层 | `.tier` + `.tier-lab`（可错位 `w96`/`w92`） | 递进看穿 |
| 网格 | 2×2 `.grid-2` / `.cell` | 场景或类型 |
| 对比 | `.card-blush`× + `.card-sage`✓ | 坑 → 修 |
| 清单 | `.list-row` + `.dot-n` | 抓法 / 步骤 |
| 收口 | `.brick` + `.card-principle` + `.pill-dark` | 带走 + 原则 + 转发 |

写之前读 `layout-shared.md`「版式节奏」；对照金标准多页卡的组件类名，不要发明另一套 UI。

## 成片规格

| 项 | 值 |
|---|---|
| 长图 | 宽 1080（390×2.769），高度随内容 |
| 视频 | **1080×1440 · 整 30fps · 15360 tbn · H.264 High 4.0 · 约 18–90 秒** |
| 运动 | 内容上滑（窗口下移） |
| 入画 | 块进入画面后淡入 + 上移约 22px / 0.42s |
| 声音 | 气泡 `bubble-pop.wav` + 曲库随机 BGM（跳过前奏，压在气泡下）；AAC 48kHz |
| 禁止 | 口播、字幕、9:16、**30.01fps、1000k tbn、封面停 0.034 秒** |

出片后必须：`py -3 ".cursor/skills/34-tietu-workflow/scripts/qa_tietu.py" mp4 "<带封面.mp4>"`。不过检不准交付。

## 产出目录

```text
workspace/HTMLcards/上滑_YYYY-MM-DD_短标题（墨纸）/
  长图.html
  layout-long.css
  theme-e-long.css          ← A/B/C/D/E 换对应 theme-*-long.css
  成品图/long.png
  封面/cover.html
  封面/cover-3x4.png
  成品视频/上滑_YYYY-MM-DD_短标题（墨纸）.mp4
  成品视频/上滑_YYYY-MM-DD_短标题（墨纸）（带封面）.mp4
  配套文案与关键词.md          ← 短标题备选 + 关键词分组（出片后必写）
  harvest/plate.png
  harvest/sprites/
  harvest/timeline.json
```

## 完成后汇报

> 已生成长图（1080 宽）和 **3:4 上滑视频**（1080×1440，N 个对象弹出 + 气泡音 + 曲库 BGM，无口播）；3:4 封面在 `封面\cover-3x4.png`，成片为 `上滑_YYYY-MM-DD_标题（主题）.mp4`，带封面为同名加 `（带封面）`；配套短标题与关键词在 `配套文案与关键词.md`。