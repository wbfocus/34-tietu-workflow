# 主题 B：亮色高级（Light Premium）

> 金标准样例：`examples/gold-b-ceo-star-light/`（8 张完整套图）

## 风格定位

暖白底 + Mesh 渐变顶区 + 渐变描边白卡 + 三层阴影 + 橙色 featured 光晕。适合日间信息流、公众号知识卡合集。

## 字体（铁律：楷体正文 + 宋体标题，三套共用）

全文纪律见 [type-shared.md](type-shared.md)。主题 B 重点词：`.mark` `#FF7700`，`.mark-sage` `#0284C7`。

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lxgw-wenkai-webfont@1.1.0/style.css"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/noto-serif-sc@5.2.5/chinese-simplified-700.css"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/noto-serif-sc@5.2.5/chinese-simplified-900.css"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/harmonyos-sans-webfont-splitted@1.2.1/dist/HarmonyOS_Sans_SC/Bold/Bold.css"/>
<link rel="stylesheet" href="theme-b.css"/>
```

新套图把 `references/theme-b.css` **复制到该文件夹**（链接不要带 `?v=`）。

```css
.ui-title{font-family:'Noto Serif SC','Source Han Serif SC',serif;font-weight:900}
.wenkai{font-family:'LXGW WenKai','霞鹜文楷',serif}
.ui-bold{font-family:'HarmonyOS_Sans_SC_Bold','HarmonyOS Sans SC',sans-serif;font-weight:700}
.mark{color:#FF7700}
.mark-sage{color:#0284C7}
```

| 层级 | 类名 | 字号 |
|---|---|---|
| 封面主标题 | `.ui-title` | 80px |
| 封面核心数字 | `.ui-bold` + `.num-glow` | 150px |
| 内页标题 | `.ui-title` | 52–56px |
| 卡片标题 | `.ui-title` | 30–32px |
| 正文/金句/副标 | `.wenkai` | 26–30px（最低 24px） |
| 标签/页码 | `.ui-bold` | 26–28px |

- 正文用 `#1C1917` 墨黑，**禁止** `text-gray-400/500` 细灰正文。
- **禁止**用 HarmonyOS 当大标题；正文不要整段 Bold。
- 每段正文 **1–3 个**重点词 `.mark` / `.mark-sage`，不要整句染色。
- 页眉中文必须是读者能看懂的栏目名，**禁止**「封面钩子」「分镜」「CTA」等内部词。
- 序号用渐变方块（蓝底或橙底），不用细线框。

## 版式（三套共用，本主题只换外壳）

全文见 [layout-shared.md](layout-shared.md)。页眉方标 + 英文小标 + 巨号水印 + `.c-foot` + 六种骨架，**禁止**再写「蓝徽章页眉 + Mesh 顶区 300px + 等宽三列」。

`.terra` = `#FF7700`，`.sage` = `#0284C7`，`.ochre` = `#0EA5E9`。`.card-paper` 在本主题里就是渐变描边白卡，不要再用旧的 `.card-premium` 当主卡片。

## 配色

| 角色 | 值 |
|---|---|
| 画布底色 | `#faf8f5` |
| 卡片底 | `#fff` |
| 结构色 | `#0EA5E9` / `#0284C7` |
| 锚点色 | `#FF7700`（每卡 ≤3 处） |
| 正文墨 | `#1C1917` |
| 徽章底 | `#E0F2FE` + `border #BAE6FD` |

新套图把 `references/theme-b.css` **复制到该文件夹**（链接不要带 `?v=`）。

## Mesh（只做氛围，禁止 300px 顶区）

封面/结尾在内容**底下**铺全卡 `.mesh` + `.noise`，不要再切一块 `h-[300px]` 顶区（那会把页眉 DNA 挤成旧模板）。内页不要 Mesh。

```html
<div class="absolute inset-0 mesh pointer-events-none z-0"></div>
<div class="absolute inset-0 noise pointer-events-none z-[1]"></div>
```

## 饱满度

`.board` / `.board-cover` 均为 **1310px** + `space-between`。**禁止 `flex-1`**。正文墨 `#1C1917`。

## 水印

```html
<div class="absolute bottom-6 left-0 w-full text-center text-[#1C1917]/40 text-[20px] ui-bold tracking-widest whitespace-nowrap z-50 pointer-events-none">@小微之家会计服务 &nbsp;|&nbsp; @老汪洞察 &nbsp;|&nbsp; @汪斌带你开公司</div>
```

外层：`w-[1080px] h-[1440px] bg-[#faf8f5] … pt-9 pb-20 px-10`。`.c-foot` 在 board 内、水印之上。

## 反塑料感（主题 B 追加）

- 骨架服从 layout-shared；禁止退回蓝徽章 + Mesh 顶区。
- 锚点橙 **≤3 处/卡**；禁止细灰正文。
- 对照 [anti-plastic-design.md](anti-plastic-design.md)；必要时 `awesome-design-md` → `stripe` / `notion`。

## 写卡前动作

1. 读 [type-shared.md](type-shared.md) + [layout-shared.md](layout-shared.md) + [anti-plastic-design.md](anti-plastic-design.md)  
2. 打开 `examples/gold-b-ceo-star-light/` 同序号页面对照骨架  
3. 复制 `references/theme-b.css` 到套图目录
