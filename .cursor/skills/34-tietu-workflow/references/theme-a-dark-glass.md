# 主题 A：深色玻璃（Dark Glass）

> 金标准样例：`examples/gold-a-ceo-star-dark/`（8 张完整套图）

## 风格定位

深色底 + 玻璃拟态卡片 + 青蓝光晕 + SVG 噪点叠加。适合小红书夜间阅读、科技感知识卡。

## 字体（铁律：楷体正文 + 宋体标题，三套共用）

全文纪律见 [type-shared.md](type-shared.md)。主题 A 重点词：`.mark` `#FF7700`，`.mark-sage` `#7dd3fc`。

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lxgw-wenkai-webfont@1.1.0/style.css"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/noto-serif-sc@5.2.5/chinese-simplified-700.css"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/noto-serif-sc@5.2.5/chinese-simplified-900.css"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/harmonyos-sans-webfont-splitted@1.2.1/dist/HarmonyOS_Sans_SC/Bold/Bold.css"/>
<link rel="stylesheet" href="theme-a.css"/>
```

新套图把 `references/theme-a.css` **复制到该文件夹**（链接不要带 `?v=`）。金标准若内联 `<style>`，必须包含同样的 `.ui-title` / `.wenkai` / `.mark`。

```css
.ui-title{font-family:'Noto Serif SC','Source Han Serif SC',serif;font-weight:900}
.wenkai{font-family:'LXGW WenKai','霞鹜文楷',serif}
.ui-bold{font-family:'HarmonyOS_Sans_SC_Bold','HarmonyOS Sans SC',sans-serif;font-weight:700}
.mark{color:#FF7700}
.mark-sage{color:#7dd3fc}
```

| 层级 | 类名 | 字号 |
|---|---|---|
| 封面主标题 | `.ui-title` | 80px |
| 封面核心数字 | `.ui-bold` + `.glow-num` | 150px |
| 内页标题 | `.ui-title` | 52–56px |
| 卡片标题 | `.ui-title` | 30–32px |
| 正文/金句/副标 | `.wenkai` | 26–30px（最低 24px） |
| 标签/页码/水印 | `.ui-bold` | 22–28px |

- **禁止**用 HarmonyOS 当大标题；正文不要整段 Bold。
- 每段正文 **1–3 个**重点词 `.mark` / `.mark-sage`，不要整句染色。
- 页眉中文必须是读者能看懂的栏目名，**禁止**「封面钩子」「分镜」「CTA」等内部词。
- 序号用**渐变数字方块**，不用细线 emoji 当主视觉（小图标可保留）。

## 版式（三套共用，本主题只换外壳）

全文见 [layout-shared.md](layout-shared.md)。页眉方标 + 英文小标 + 巨号水印 + `.c-foot` + 六种骨架，**禁止**再写「胶囊页眉 + 等宽三列 + 底栏金句」。

`.terra` = `#FF7700`，`.sage` = `#0EA5E9`，`.ochre` = `#38bdf8` / `#0284C7`。`.card-paper` 在本主题里就是玻璃卡，不要再用旧的 `.glass` 当主卡片。

## 配色

| 角色 | 值 |
|---|---|
| 画布底色 | `#0a0f1a` |
| 玻璃卡片底 | `rgba(15,23,42,.62)` |
| 结构色 | `#0EA5E9` / `cyan-200~400` |
| 锚点色 | `#FF7700`（每卡 ≤3 处） |
| 正文 | `text-white` / `text-slate-100~300` |
| 页码 | `text-slate-400` |

新套图把 `references/theme-a.css` **复制到该文件夹**（链接不要带 `?v=`）。不要把整段 CSS 内联进每张 HTML。

## 氛围层（每张必有，不做顶区占位）

光晕 **≤2 个**。叠在 `.board` 底下，内容从页眉一直铺到 `.c-foot`。

```html
<div class="absolute top-[-100px] left-[-60px] w-[680px] h-[680px] bg-cyan-500/28 rounded-full blur-[170px] z-0"></div>
<div class="absolute bottom-[-80px] right-[-40px] w-[580px] h-[580px] bg-blue-600/22 rounded-full blur-[140px] z-0"></div>
<div class="absolute inset-0 noise pointer-events-none z-[1]"></div>
```

封面数字在 `.hero-orb` 内，可加 `.glow-num`；内页数字不要发光。

## 饱满度

`.board` / `.board-cover` 均为 **1310px** + `space-between`。**禁止 `flex-1`**。内容多：收紧 gap、合并原则框；不要加独立底栏。

## 水印

```html
<div class="absolute bottom-6 left-0 w-full text-center text-slate-600 text-[20px] ui-bold tracking-widest whitespace-nowrap z-50 pointer-events-none">@小微之家会计服务 &nbsp;|&nbsp; @老汪洞察 &nbsp;|&nbsp; @汪斌带你开公司</div>
```

外层：`w-[1080px] h-[1440px] bg-[#0a0f1a] … pt-9 pb-20 px-10`。`.c-foot` 在 board 内、水印之上。

## 反塑料感（主题 A 追加）

- 骨架服从 layout-shared，不要退回胶囊页眉。
- 禁止紫/靛大面积渐变；光晕 ≤2。
- 对照 [anti-plastic-design.md](anti-plastic-design.md)；必要时 `awesome-design-md` → `linear.app`。

## 写卡前动作

1. 读 [type-shared.md](type-shared.md) + [layout-shared.md](layout-shared.md) + [anti-plastic-design.md](anti-plastic-design.md)  
2. 打开 `examples/gold-a-ceo-star-dark/` 同序号页面对照骨架  
3. 复制 `references/theme-a.css` 到套图目录
