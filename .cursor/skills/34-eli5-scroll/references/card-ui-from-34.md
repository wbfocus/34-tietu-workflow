# ELI5 长图 · 对齐 3:4 贴图的卡片纪律

源：`34-tietu-workflow` 的 A/B/C 主题 + `layout-shared.md` 版式节奏。  
画布改成 **390px 手机长卷**，不是 1080×1440 多页卡。

写 HTML 前扫一遍；写完跑文末 QA。

## 1. 三套主题（只换外壳）

| ID | 名称 | CSS | 氛围层 |
|---|---|---|---|
| A | 深色玻璃 | `theme-a-long.css` | `.atm` 光晕 + `.noise` |
| B | 亮色高级 | `theme-b-long.css` | `.mesh` + `.noise` |
| C | 奶油刊物 | `theme-c-long.css` | 无 Mesh / 无玻璃 |

共用骨架：`layout-long.css`。类名与贴图相同：`.terra` / `.sage` / `.ochre` 是角色类。

## 2. 反塑料感

| 禁止 | 要做 |
|---|---|
| Inter / Roboto / Arial 主字体 | 标题 `.ui-title` 宋，正文 `.wenkai` 楷 |
| 紫靛大面积渐变 | A 深底玻璃；B 暖 Mesh；C 奶油 `#FDF8F2` |
| 整页同一骨架 / 只有 3–4 段流水账 | 复用贴图六种节奏，一套 ≥5 种组件形态 |
| 处处发光 | 全页 ≤1 个 `.card-principle` |
| 浅灰当正文 | 正文深墨；浅灰只给元信息 |

## 3. 字体

允许 CDN + 系统回退（与贴图 type-shared 相同）。

| 层级 | 字号 | 用途 |
|---|---|---|
| L1 | 26–28px | `h1.ui-title` |
| L2 | 16–17px | `h2` |
| L3 | 15px | `.big` |
| L4 | 13.5–14px | 正文 |
| L5 | 11–12px | 落款 |

每段 1–3 个 `.mark` / `.mark-sage`，禁止整句染色。栏目名用人话，禁止「分镜 / CTA / featured」。

## 4. 弹出块（`data-eli5-reveal`）

每个要「一个个出现」的对象单独打标：

- 页头整块 `.eli5-head`，以及头内的 `.pill-dark` / `.hero-row` / 标签行（可分拆）
- 每张 `.card-paper` / `.card-blush` / `.card-sage` / `.card-callout` / `.card-principle` / `.hl-bar`
- 每个 `.tier`、`.box`、`.list-row`、网格 `.cell`、积木 `.item`
- 落款 `.credit`、`.c-foot`

不要把整个 `.content` 打成一个 reveal，否则视频里只会弹一次。  
`.wm` / `.atm` / `.mesh` / `.noise` 不要打标。

## 5. 内容骨架（默认必做 · 多样式）

**用户说「上滑」即默认本表，不必再提醒「样式丰富一点」。**  
组件与贴图/橱窗共用（`layout-shared.md`），禁止另起一套塑料模板。

一套长卷 **≥5 种** 节奏（推荐全开，内容短可删到 5）：

1. **封面开场** — `.hero-orb` + `.pill-dark` 判断句 + chip 标签行  
2. **比喻** — `.card-paper.story` + `.hl-bar` 或 `.card-callout`  
3. **竖向流程** — `.flow` / `.box`（怎么转起来）  
4. **分层** — `.tier` + `.tier-lab`（可 `w96` / `w92` 错位）  
5. **2×2 网格** — `.grid-2` / `.cell`（场景、类型、样子）  
6. **对比** — `.card-blush` × → `.card-sage` ✓  
7. **清单** — `.list-row` + `.dot-n`  
8. **收口** — `.brick` + `.card-principle`（≤1）+ `.pill-dark` 转发  

本地可加短 `<style>` 补 `.grid-2` / `.list-row` / `.chip-row`（主题色跟 `theme-*-long.css`）。

**禁止**：整页只有「比喻 → 流程 → 坑修 → 积木 → 原则」五段且无大圆/分层/网格/清单任一组合。

## 6. QA

- [ ] 390px 单列，无双栏裁切
- [ ] 标题宋、正文楷；无紫靛塑料风
- [ ] **画面与文件名无 `ELI5`/`eli5`**（页眉英文、页脚、封面、成片名）
- [ ] **≥5 种**版式节奏（见第 5 节）；原则框 ≤1
- [ ] 含贴图组件：大圆/分层/网格/清单至少命中 2 类以上
- [ ] 弹出块 ≥8 且不是整页一块
- [ ] 水印可见不抢读；落款完整
