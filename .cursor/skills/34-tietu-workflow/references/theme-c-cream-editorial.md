# 主题 C：奶油刊物（Cream Editorial）

> 金标准样例：`examples/gold-c-workshop-editorial/`（8 张完整套图）  
> 定位：**可选第三主题**。用户指定「C / 奶油 / 刊物 / 信息图 / 陶土」时使用；未指定时仍先问 A/B/C。

## 风格定位

暖奶油底 + 陶土橙锚点 + 鼠尾草绿辅色 + 圆角方标页码 + 右上角浅色巨号水印 + 白卡软阴影 + 虚线原则框。对标知识向信息图（非 Mesh、非玻璃）。适合日间刷、教程拆解、清单/对比/分层。

## 字体（铁律：楷体正文 + 宋体标题，三套共用）

全文纪律见 [type-shared.md](type-shared.md)。主题 C 重点词：`.mark` `#D16C4F`，`.mark-sage` `#6F8A6A`，另有 `.mark-ochre` `#B8873A`。

正文主体用 **霞鹜文楷**（[LxgwWenKai](https://github.com/lxgw/LxgwWenKai)）。大标题用 **思源宋体 ExtraBold**（Noto Serif SC 900）压住楷体，刊物感比系统黑体强。数字方标 / 英文小标 / 水印仍用 HarmonyOS Bold。

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lxgw-wenkai-webfont@1.1.0/style.css"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/noto-serif-sc@5.2.5/chinese-simplified-700.css"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/noto-serif-sc@5.2.5/chinese-simplified-900.css"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/harmonyos-sans-webfont-splitted@1.2.1/dist/HarmonyOS_Sans_SC/Bold/Bold.css"/>
<link rel="stylesheet" href="theme-c.css"/>
```

每套图把 `references/theme-c.css` **复制到该文件夹**（链接不要带 `?v=`）。

```css
.ui-title{font-family:'Noto Serif SC','Source Han Serif SC',serif;font-weight:900}
.wenkai{font-family:'LXGW WenKai','霞鹜文楷',serif}
.ui-bold{font-family:'HarmonyOS_Sans_SC_Bold','HarmonyOS Sans SC',sans-serif;font-weight:700}
.mark{color:#D16C4F}          /* 正文重点词 · 陶土 */
.mark-sage{color:#6F8A6A}     /* 正文重点词 · 鼠尾草 */
```

| 层级 | 类名 | 字号 |
|---|---|---|
| 封面/内页大标题 | `.ui-title` | 50–56px |
| 卡片小标题 | `.ui-title` | 28–32px |
| 封面核心数字（圆标内） | `.ui-title` 或 `.ui-bold` | 88–110px |
| 正文/金句/副标 | `.wenkai` | 26–30px（最低 24px） |
| 英文小标 / 页码 / 水印 | `.ui-bold` | 18–22px |

- 正文墨 `#2A2724`，**禁止** `text-gray-400/500` 细灰正文。
- 元信息可用 `#6B6560` / `#9A938C`。
- 每段正文 **1–3 个**重点词用 `.mark` / `.mark-sage` 换色，不要整句染色。
- 页眉中文必须是读者能看懂的栏目名（如「车间现场」「两张皮」），**禁止**「封面钩子」「分镜」「CTA」等内部词。

## 配色（本主题覆盖 A/B 的天蓝+亮橙）

| 角色 | 值 |
|---|---|
| 画布底 | `#FDF8F2` |
| 卡片底 | `#FFFFFF` |
| 主锚点（陶土） | `#D16C4F` |
| 辅色（鼠尾草） | `#6F8A6A` |
| 第三色（赭石） | `#C4A46A` |
| 炭黑条 | `#2E2E2E` |
| 提示底 / 原则底 | `#F5EAD4` |
| 警示底 | `#FCE6E0` |
| 修法底 | `#E8F0E4` |
| 正文墨 | `#2A2724` |

陶土橙 **每卡 ≤3 处大色块**（方标 + 1 个圆/边 + 原则框「原则」二字即可）。不要再叠品牌 `#FF7700` / `#0EA5E9`，以免两套色打架。水印文案仍用品牌三账号。

## 版式（三套共用）

页眉 / 页脚 / 六种骨架 / 语义组件见 [layout-shared.md](layout-shared.md)。本主题只提供奶油材质与陶土/鼠尾草/赭石色值。

**禁止** Mesh 顶区、玻璃模糊、渐变描边、数字发光（那是 A/B 的外壳）。

## 核心组件（色值）

`.card-paper` 白卡软阴影；`.card-callout` 米黄；`.card-blush` 浅陶土；`.hl-bar` 鼠尾草绿条；`.card-principle` 虚线原则框；`.hero-orb` 陶土大圆；`.pill-dark` 炭黑胶囊。

## 饱满度规则

- 内页/封面均用 `.board`（高 1310px + `space-between`）。本主题无 mesh，**不要**再套一层 200px 顶区。
- **禁止 `flex-1` 撑高**。内容少：加大标题/卡片 `p-*`；内容多：收紧 gap、合并原则框。
- `.card-principle` **每卡 ≤1**。

## 水印 + 底部安全区

```html
<div class="absolute bottom-6 left-0 w-full text-center text-[#2A2724]/35 text-[20px] ui-bold tracking-widest whitespace-nowrap z-50 pointer-events-none">@小微之家会计服务 &nbsp;|&nbsp; @老汪洞察 &nbsp;|&nbsp; @汪斌带你开公司</div>
```

- 外层容器：`w-[1080px] h-[1440px] bg-[#FDF8F2] … pt-9 pb-20 px-10`
- `.c-foot` 在 board 内、水印之上；不要把正文写进水印行。

## 反塑料感（主题 C 追加）

- 不要每张都「方标 + 三列等宽卡」；封面/对比/分层/结尾必须换骨架。
- 白卡阴影保持极淡，禁止 `shadow-lg` 黑投影。
- 背景巨号只放页码，不要再叠第二个大汉字。
- 对照 [anti-plastic-design.md](anti-plastic-design.md)。

## 写卡前动作

1. 读 [anti-plastic-design.md](anti-plastic-design.md) 第二～四节  
2. 打开金标准 `examples/gold-c-workshop-editorial/` 同序号页面对照密度与组件，再动笔  
3. 复制 `references/theme-c.css` 到套图目录  
写卡前还要读 [layout-shared.md](layout-shared.md)。  
