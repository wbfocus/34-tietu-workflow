# ELI5 长图 · 对齐 3:4 贴图的卡片纪律

源：`34-tietu-workflow` 昨天优化过的 A/B/C 主题。  
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
| 整页同一骨架 | 比喻卡 / 竖向流程 / 坑修 / 积木 / 原则框，至少 3 种 |
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

- 页头整块 `.eli5-head`
- 每张 `.card-paper` / `.card-blush` / `.card-sage` / `.card-principle`
- 流程里每个 `.box`
- 积木每个 `.item`
- 落款 `.credit`、`.c-foot`

不要把整个 `.content` 打成一个 reveal，否则视频里只会弹一次。  
`.wm` / `.atm` / `.mesh` / `.noise` 不要打标。

## 5. 内容骨架（默认）

1. 比喻开场（生活类比）
2. 竖向流程（怎么转起来）
3. 坑 → 修
4. 积木清单
5. 原则框收口

## 6. QA

- [ ] 390px 单列，无双栏裁切
- [ ] 标题宋、正文楷；无紫靛塑料风
- [ ] ≥3 种区块；原则框 ≤1
- [ ] 弹出块 ≥6 且不是整页一块
- [ ] 水印可见不抢读；落款完整
