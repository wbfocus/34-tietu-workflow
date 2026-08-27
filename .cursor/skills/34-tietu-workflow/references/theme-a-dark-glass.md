# 主题 A：深色玻璃（Dark Glass）

> 金标准样例：`examples/gold-a-ceo-star-dark/`（8 张完整套图）

## 风格定位

深色底 + 玻璃拟态卡片 + 青蓝光晕 + SVG 噪点叠加。适合小红书夜间阅读、科技感知识卡。

## 字体（铁律：结构全 Bold，禁止细字）

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lxgw-wenkai-webfont@1.1.0/style.css"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/harmonyos-sans-webfont-splitted@1.2.1/dist/HarmonyOS_Sans_SC/Bold/Bold.css"/>
```

```css
.ui-bold{font-family:'HarmonyOS_Sans_SC_Bold','HarmonyOS Sans SC',sans-serif;font-weight:700}
.wenkai{font-family:'LXGW WenKai','霞鹜文楷',serif}
```

| 层级 | 类名 | 字号 |
|---|---|---|
| 封面主标题 | `.ui-bold` | 80px |
| 封面核心数字 | `.ui-bold` + `.glow-num` | 150px |
| 内页标题 | `.ui-bold` | 52–56px |
| 卡片标题 | `.ui-bold` | 30–32px |
| 正文/金句 | `.wenkai` | 26–30px（最低 24px） |
| 标签/页码/元信息 | `.ui-bold` | 22–28px |

- **禁止** Regular / Medium / `font-normal` 用于标题、标签、数字。
- 序号用**渐变数字方块**，不用细线 emoji 当主视觉（小图标可保留）。

## 配色

| 角色 | 值 |
|---|---|
| 画布底色 | `#0a0f1a` |
| 玻璃卡片底 | `rgba(15,23,42,.62)` |
| 结构色 | `#0EA5E9` / `cyan-200~400` |
| 锚点色 | `#FF7700`（每卡 ≤3 处） |
| 正文 | `text-white` / `text-slate-100~300` |
| 页码 | `text-slate-400` |

## 核心 CSS（每张卡 `<head>` 内联复制）

```css
html,body{margin:0;padding:0;background:#0a0f1a;overflow:hidden}
.glass{
  background:rgba(15,23,42,.62);backdrop-filter:blur(24px);
  border:1px solid rgba(148,163,184,.22);border-top:1px solid rgba(255,255,255,.14);
  box-shadow:0 12px 40px rgba(0,0,0,.4),inset 0 1px 0 rgba(255,255,255,.08);
  position:relative;overflow:hidden
}
.glass-hl{
  background:linear-gradient(135deg,rgba(14,165,233,.22),rgba(30,58,138,.3));
  backdrop-filter:blur(20px);border:1px solid rgba(14,165,233,.4);
  border-top:1px solid rgba(255,255,255,.18);
  box-shadow:0 0 50px rgba(14,165,233,.18),0 16px 48px rgba(0,0,0,.45);
  position:relative;overflow:hidden
}
.glass-warn{background:rgba(255,119,0,.12);backdrop-filter:blur(24px);border:1px solid rgba(255,119,0,.35);...}
.glass-fail{background:rgba(239,68,68,.1);backdrop-filter:blur(24px);border:1px solid rgba(239,68,68,.3);...}
.glow-num{text-shadow:0 0 50px rgba(255,119,0,.6),0 0 100px rgba(255,119,0,.3)}
.noise{opacity:.05;mix-blend-mode:overlay;background-image:url("data:image/svg+xml,...feTurbulence...")}
```

每张 `.glass` / `.glass-hl` 卡片内加 `<div class="absolute inset-0 noise pointer-events-none"></div>`。

## 背景层（每张必有）

```html
<div class="absolute top-[-100px] left-[-60px] w-[680px] h-[680px] bg-cyan-500/28 rounded-full blur-[170px] z-0"></div>
<div class="absolute bottom-[-80px] right-[-40px] w-[580px] h-[580px] bg-blue-600/22 rounded-full blur-[140px] z-0"></div>
<div class="absolute inset-0 noise pointer-events-none z-[1]"></div>
```

## 饱满度规则

- 间距用 `gap-4` / `gap-5`，避免大块 `flex-1` 留白。
- 底部用关系条、口径栏、状态行、金句框填满纵向空间——**总高度将超画布时合并块、收紧 gap，禁止 flex-1 + 独立底栏叠穿**。
- 页眉标签用 `.glass` 胶囊；高亮区块用 `.glass-hl` + 左侧 `border-l-[6px] border-l-[#0EA5E9]`。

## 水印 + 底部安全区

```html
<div class="absolute bottom-6 left-0 w-full text-center text-slate-600 text-[20px] ui-bold tracking-widest whitespace-nowrap z-50 pointer-events-none">@小微之家会计服务 &nbsp;|&nbsp; @老汪洞察 &nbsp;|&nbsp; @汪斌带你开公司</div>
```

- 外层容器用 `pt-9 pb-20`（或等价），**禁止**内容压到水印行。
- 提醒框 / CTA 放在安全区之上；内容多时先收紧间距/字号，不要往下挤穿底边。

## 反塑料感（主题 A 追加）

- 背景光晕 **≤2 个**；全卡只有 **1 张** `.glass-hl`，其余 `.glass`。
- 封面数字可 `glow-num`，内页数字改纯色粗体，不要张张发光。
- 每套 **≥2 张** 用错位：提醒条右缩进、某块 `ml-6`、宽窄不一的卡片堆叠。
- **禁止** 紫/靛渐变底；渐变只用于 `.glass-hl` 青蓝描边区，不铺全屏。
- 对照 [anti-plastic-design.md](anti-plastic-design.md)；必要时 `awesome-design-md` → `linear.app`。

## 写卡前动作

1. 读 [anti-plastic-design.md](anti-plastic-design.md) 第二～四节
2. 打开金标准文件夹中同类型页面（封面→`1.html`，内容→`2~7.html`，结尾→`8.html`）对照结构与密度，再动笔
