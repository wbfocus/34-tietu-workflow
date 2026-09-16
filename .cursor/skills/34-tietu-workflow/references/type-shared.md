# 三套主题共用 · 文字铁律

A / B / C **配色与材质不同**，文字纪律相同。版式骨架见 [layout-shared.md](layout-shared.md)。写任何主题的 HTML 前两篇都要读。

## 字体分工

| 角色 | 类名 | 字体 | 用途 |
|---|---|---|---|
| 大标题 / 卡片小标题 | `.ui-title` | **思源宋体 ExtraBold**（Noto Serif SC 900） | 封面主标题、内页 h1、区块名 |
| 正文 / 副标 / 金句 | `.wenkai` | **霞鹜文楷**（[LxgwWenKai](https://github.com/lxgw/LxgwWenKai)） | 解释、列表、原则框 |
| 数字 / 英文小标 / 水印 | `.ui-bold` | HarmonyOS Sans Bold | 页码、方标数字、`01 / 08`、品牌水印 |

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lxgw-wenkai-webfont@1.1.0/style.css"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/noto-serif-sc@5.2.5/chinese-simplified-700.css"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/noto-serif-sc@5.2.5/chinese-simplified-900.css"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/harmonyos-sans-webfont-splitted@1.2.1/dist/HarmonyOS_Sans_SC/Bold/Bold.css"/>
```

```css
.ui-title{font-family:'Noto Serif SC','Source Han Serif SC','Songti SC','SimSun',serif;font-weight:900}
.wenkai{font-family:'LXGW WenKai','霞鹜文楷',serif}
.ui-bold{font-family:'HarmonyOS_Sans_SC_Bold','HarmonyOS Sans SC',sans-serif;font-weight:700}
```

- 标题用宋体压楷体，**不要**再用 HarmonyOS 当大标题。
- 正文不要整段 `.ui-bold`。数字发光仍按各主题（A `.glow-num`、B `.num-glow`），封面最多 1 处。

## 重点词换色

每段正文 **1–3 个**词换色，不要整句染色。

| 主题 | `.mark` | `.mark-sage` |
|---|---|---|
| A 深色玻璃 | `#FF7700` | `#7dd3fc`（青） |
| B 亮色高级 | `#FF7700` | `#0284C7`（天蓝） |
| C 奶油刊物 | `#D16C4F`（陶土） | `#6F8A6A`（鼠尾草） |

C 另有 `.mark-ochre` `#B8873A`，A/B 不要用。

## 页眉禁内部词

页眉中文必须是**读者能看懂的栏目名**（如「车间现场」「痛点场景」「拆四刀」）。

**禁止**写在卡面上：封面钩子、分镜、CTA、SKU、slug、金标准、QA、flex-1、mesh、featured。

## 正常人话（标题与正文）

封面大标题、栏目名、画面句子，用会上能说出口的话。专业词可以解释，不能拿黑话当标题。

**禁止**当标题或当动词：写死、对齐、闭环、沉淀、抓手、颗粒度、底座、赋能；也不要两个字概念名直接上封面（口径、三算、漏斗）。

对照：不写「开会前先写死口径」，写「开会前先说清楚：毛利包不包运费」。已经出过的片子就是这个味：「车间说赚钱，财务却说亏钱？」「货不动，账先退再领」。

英文小标可以有（FIELD / GAP），但必须配人话中文，不要单独写 COVER 当「这是封面」。

## 文件夹和成片文件名

工作文件夹和 MP4 同一套：`模式_YYYY-MM-DD_标题（深色|浅色|刊物）`。带封面成片加 `（带封面）.mp4`。禁止每套都叫 `showcase.mp4` / `carousel.mp4`。见 `scripts/delivery_names.py`。
