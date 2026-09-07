# 主题 B：亮色高级（Light Premium）

> 金标准样例：`examples/gold-b-ceo-star-light/`（8 张完整套图）

## 风格定位

暖白底 + Mesh 渐变顶区 + 渐变描边白卡 + 三层阴影 + 橙色 featured 光晕。适合日间信息流、公众号知识卡合集。

## 字体（铁律：结构全 Bold，禁止细灰细字）

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
| 封面核心数字 | `.ui-bold` + `.num-glow` | 150px |
| 内页标题 | `.ui-bold` | 52–56px |
| 卡片标题 | `.ui-bold` | 30–32px |
| 正文/金句 | `.wenkai` 或 `.ui-bold` | 26–30px（最低 24px） |
| 标签/页码 | `.ui-bold` | 26–28px |

- 正文用 `#1C1917` 墨黑，**禁止** `text-gray-400/500` 细灰正文。
- 序号用渐变方块（蓝底或橙底），不用细线框。

## 配色

| 角色 | 值 |
|---|---|
| 画布底色 | `#faf8f5` |
| 卡片底 | `#fff` |
| 结构色 | `#0EA5E9` / `#0284C7` |
| 锚点色 | `#FF7700`（每卡 ≤3 处） |
| 正文墨 | `#1C1917` |
| 徽章底 | `#E0F2FE` + `border #BAE6FD` |

## 核心 CSS（每张卡 `<head>` 内联复制）

```css
html,body{margin:0;padding:0;background:#faf8f5;overflow:hidden}
.mesh{
  background:
    radial-gradient(ellipse 90% 70% at 10% 0%, rgba(245,233,212,.95) 0%, transparent 50%),
    radial-gradient(ellipse 70% 60% at 50% 5%, rgba(186,230,253,.8) 0%, transparent 45%),
    radial-gradient(ellipse 60% 50% at 85% 10%, rgba(255,119,0,.12) 0%, transparent 50%),
    linear-gradient(180deg,#f0f9ff 0%,#faf8f5 45%,#faf8f5 100%);
}
.card-premium{
  background:#fff;border-radius:16px;position:relative;
  box-shadow:0 1px 2px rgba(13,37,61,.04),0 8px 24px rgba(14,165,233,.1),0 24px 48px rgba(14,165,233,.05);
}
.card-premium::before{
  content:'';position:absolute;inset:0;border-radius:16px;padding:1px;
  background:linear-gradient(135deg,#BAE6FD,#0EA5E9 40%,#FF7700 80%,#BAE6FD);
  -webkit-mask:linear-gradient(#fff 0 0) content-box,linear-gradient(#fff 0 0);
  mask:linear-gradient(#fff 0 0) content-box,linear-gradient(#fff 0 0);
  -webkit-mask-composite:xor;mask-composite:exclude;pointer-events:none;
}
.card-featured{
  background:linear-gradient(135deg,#fff 0%,#FFF4E6 100%);border-radius:16px;
  box-shadow:0 1px 2px rgba(255,119,0,.08),0 8px 32px rgba(255,119,0,.15),0 0 60px rgba(255,119,0,.08);
  border:1px solid rgba(255,119,0,.2);
}
.num-glow{color:#FF7700;text-shadow:0 4px 24px rgba(255,119,0,.35),0 0 60px rgba(255,119,0,.2)}
.badge{background:#E0F2FE;color:#0284C7;border:1px solid #BAE6FD;border-radius:9999px}
.noise{opacity:.03;mix-blend-mode:multiply;background-image:url("data:image/svg+xml,...feTurbulence...")}
.board{display:flex;flex-direction:column;justify-content:space-between;height:1310px}
.board-cover{display:flex;flex-direction:column;justify-content:space-between;height:1140px}
```

## Mesh 顶区（封面 + 结尾卡必有）

封面/结尾用 `.mesh h-[300px]` 顶区 + 内嵌 `.noise`；内页可用纯白顶栏 + `.badge` 标签。

## 饱满度规则

- 间距 `gap-5` / `gap-6`；内容区用 `.board` 竖向铺满（`space-between`），**禁止**全堆上半截、底下空一大块米色。
- **禁止 `flex-1` 撑高**。内容少：拉开块间距或加大字号；内容多：收紧 gap / 合并 featured。
- 重点卡用 `.card-featured`（橙光），普通卡用 `.card-premium`（渐变描边）。
- 底部加关系 pills、自检清单、CTA 框填满空间——**但若总高度将超 1440px，合并进 featured，不要再加独立底栏**。

## 水印 + 底部安全区

```html
<div class="absolute bottom-6 left-0 w-full text-center text-slate-400 text-[20px] ui-bold tracking-widest whitespace-nowrap z-50 pointer-events-none">@小微之家会计服务 &nbsp;|&nbsp; @老汪洞察 &nbsp;|&nbsp; @汪斌带你开公司</div>
```

- 外层容器用 `pt-9 pb-20`（或等价），**禁止**内容压到水印行。
- 提醒框 / CTA 放在安全区之上；内容多时先收紧间距/字号，不要往下挤穿底边。

## 反塑料感（主题 B 追加）

- Mesh 顶区只用于 **封面/结尾**；内页用纯白顶栏 + `.badge`，不要每张都铺渐变顶。
- `.card-featured` **每卡 ≤1 张**；普通内容用 `.card-premium` 渐变描边即可。
- 正文 `#1C1917` 墨黑，**禁止**细灰正文；锚点橙 **≤3 处/卡**。
- 编辑感：左边框金句、关系 pills 底部填满；某张内页用 `w-[92%]` 左对齐错位。
- **禁止** 对称三等分 feature 区 + 居中标题模板套满 8 张。
- 对照 [anti-plastic-design.md](anti-plastic-design.md)；必要时 `awesome-design-md` → `stripe` / `notion`。

## 写卡前动作

1. 读 [anti-plastic-design.md](anti-plastic-design.md) 第二～四节
2. 打开金标准文件夹中同类型页面对照；封面/结尾参考 `1.html`、`8.html` 的 mesh 结构
