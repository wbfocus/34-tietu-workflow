# 强制视觉规范（提炼自 HTMLcards/写HTML卡片提示词.md）

这些规则不是建议，是硬约束。写每一张卡片的 HTML 之前，逐条核对。

## 0. 反塑料感（写卡前必读）

写 HTML 前读 [anti-plastic-design.md](anti-plastic-design.md)；截图前跑该文 **第七节 QA 10 条**。

核心纪律（摘要）：

- **禁用** Inter / Roboto / Arial 作主字体；**禁用**紫/靛大面积渐变。
- 每套贴图 **≥2 张** 用不对称/错位版式；封面与内页版式结构要有变化。
- 全卡 **≤1 张** featured 高亮卡；亮橙锚点 **≤3 处**。
- 风格发飘时，用 `awesome-design-md` 拉 `stripe` / `linear.app` 对照间距与边框（色值仍服从老汪品牌）。

## 1. 纯净截图底层结构（绝不能省）

```html
<style>
  html, body { margin: 0; padding: 0; overflow: hidden; background-color: <与主容器一致的底色>; font-family: 'LXGW WenKai', sans-serif; }
</style>
```

- 最外层 `<div>` 必须写死宽高：`w-[Wpx] h-[Hpx]`，并带 `relative overflow-hidden box-border`。
- 最外层 div **不能**用 `box-shadow` 外阴影或外 `margin`，否则截图会越界/留白。
- `<body>` 的**第一个直接子元素**必须就是这个最外层卡片 div（渲染脚本靠这个规则定位截图节点，不要在 body 和卡片 div 之间插入包裹层）。

## 2. 尺寸

| 场景 | 尺寸 | 用途 |
|---|---|---|
| 3:4 竖版（**默认**） | `1080x1440` | 小红书图文卡、公众号知识卡，没指定时优先用这个 |
| 16:9 横版 | `1920x1080` | PPT / 长图 / 讲解页 |
| 流程图卡 | `1440x1080` | 步骤多、节点多、需要横向蛇形排布时 |
| 公众号头图/banner | 按需（如 `1080x450`） | 头图、引流海报等特殊场景，参照 HTMLcards 已有同类文件 |

## 3. 字体（`<head>` 里全量引入，一个都不能少）

```html
<link href="https://fonts.googleapis.com/css2?family=Ma+Shan+Zheng&family=ZCOOL+XiaoWei&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lxgw-wenkai-webfont@1.1.0/style.css" />
```

```css
.font-title { font-family: 'ZCOOL XiaoWei', serif; }   /* 大标题，显权威 */
.font-accent { font-family: 'Ma Shan Zheng', cursive; } /* 背景大字/数字冲击，显张力 */
.font-body { font-family: 'LXGW WenKai', sans-serif; }  /* 正文，显书卷气 */
.font-sans { font-family: sans-serif; }                 /* 英文标签/页码等零碎小字 */
```

正文默认套 `font-body`。不要出现英文单词（品牌词、页码格式如 `01 / 08`、`Manufacturing Insight / 2026` 这种装饰性英文小字除外）或繁体字。

## 4. 配色（主题 A/B 为准，拒绝塑料感配色）

写卡时以所选主题文件色板为准（老汪天蓝 `#0EA5E9` + 亮橙 `#FF7700`）。**禁止**：

- 紫/靛/网红紫蓝渐变背景（`from-purple` / `via-indigo` 大面积铺底）
- 高饱和原色块堆叠（`bg-blue-500` + `bg-green-500` + `bg-red-500` 三等分）
- 正文用 `text-gray-400/500` 当主色（仅元信息可降 opacity）

延伸方向（仅在主题组件内使用）：

- **深海蓝+极客青**（主题 A）：`#0a0f1a` 底 + cyan/blue 光晕 + 白字。
- **暖白编辑风**（主题 B）：`#faf8f5` 底 + 墨黑正文 + 橙锚点。

## 5. 质感层次（每张卡至少用 2-3 种）

- 背景大光晕：`absolute w-[NNNpx] h-[NNNpx] bg-<色>-600 rounded-full mix-blend-screen filter blur-[150~250px] opacity-20~40`，通常放 1-2 个在角落。
- 毛玻璃卡片：`bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl`。
- 渐变高亮文字（金句/关键词）：`text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400`。
- 背景巨字衬底（可选，营造氛围）：`font-accent text-[NNNpx] opacity-5 absolute`，用一个和主题相关的单字。

## 6. 版式布局

- 3:4 卡片：`flex flex-col`，页眉（左侧标签 + 右侧 `NN / NN` 页码）→ 标题区 → 内容区（`grid` 网格或卡片堆叠）→ 底部水印。
- 16:9 卡片：`grid grid-cols-12` 或左右两栏分栏。
- 流程图卡：蛇形排布——第一排 `flex justify-between`（1→4 从左到右），中间一段竖直连接线，第二排 `flex-row-reverse`（5→8 从右到左），每个节点是编号圆角卡（`glass-box`），节点间用一条横线+旋转 45° 的边框箭头连接。

**反塑料感版式**（每套至少用 3 种，详见 anti-plastic-design.md 第四节）：

- 封面：标题左对齐 + 右侧/右下大数字；可加 mono 英文副标。
- 内页：左边框叙事条、提醒条 `w-[94%] ml-auto` 错位、编号渐变方块（非等宽三列模板）。
- **禁止** 8 张全是「标题 + 3 列等宽 grid + 底栏」同一骨架。

## 7. 内容重构手法（禁止平铺直叙）

- 痛点 → 红黑榜：❌ 反例 / ✅ 正例 对照卡。
- 步骤/流程 → 带编号的圆角卡片（左上角悬浮编号圆圈 `01 02 03...`）。
- 金句/结论 → 渐变高亮文字，单独成行。
- 数据/指标 → 小卡片网格，每格：指标名 + 公式/口径 + 标准值 + 一句风险提示。

## 8. 页眉/页脚元素（几乎每张都要有）

- 左上角标签徽章：圆角胶囊，如 `# 内部实战内参` / `老汪出品 · 必是精品` / `实战派财税频道`。
- 右上角页码：`NN / NN` 格式（`font-sans font-black tracking-widest text-slate-500`）。
- 标题命名习惯（仅用于 `<title>` 标签，不影响截图）：`P{N}：{类型}-{要点}`，如 `P1：封面-业财融合`。

## 9. 专属防盗水印（每张卡片最底层必须有，z-50，不可删改文案）

```html
<div class="absolute bottom-6 left-0 w-full text-center text-slate-500/40 text-[22px] font-black tracking-widest whitespace-nowrap z-50 pointer-events-none select-none uppercase font-sans">@小微之家会计服务 &nbsp;&nbsp;|&nbsp;&nbsp; @老汪洞察 &nbsp;&nbsp;|&nbsp;&nbsp; @汪斌带你开公司</div>
```

- 深色背景：`text-slate-500/40` 左右；浅色背景可用 `text-slate-400/40` 保持隐约可见。
- 必须单行、`whitespace-nowrap`、`pointer-events-none select-none`，绝不能被选中/换行/被其它元素遮挡。
- 位置默认底部居中；名片类/横版 banner 可改左对齐或右对齐，但文案内容不变。

### 水印安全区（铁律，防底边溢出）

- 最外层卡片容器必须预留底部安全区：`pb-16`～`pb-20`（约 64–80px），**`pb-20` 写在最外层 `w-[1080px] h-[1440px]` div 上**，不要只写在内层子区块。
- **禁止**在内层内容区用 `flex-1` 撑满后再堆多块卡片——总高度超过 `1440px` 会被 `overflow-hidden` 裁切，表现为底部金句/提醒框被切掉。
- 内容偏多时：**先收紧** mesh 高度、标题区、`gap`、卡片 `p-*`、合并底栏（金句 + 自检写进同一张 featured），**不要**再加独立 CTA 条往下挤。
- **默认不要**把正文块、提醒框、CTA 放到水印行高度内；内容与水印之间至少留一截空白。
- 只有内容极多、不得不挤时，才允许最后一块内容贴近安全区上沿——仍禁止与水印文字重叠或被 `overflow:hidden` 裁切。
- 写卡后自检：底部最后一块内容完整可见，水印整行可读、不被遮挡。

## 10. Tailwind 引入方式

```html
<script src="https://cdn.tailwindcss.com"></script>
```

放在 `<head>` 里，配合内联 `<style>` 补充自定义类（字体映射、`glass-box` 之类的复合样式），不要额外引入其它 CSS 框架。

## 11. 代码注释

在每张卡的关键区块（背景光晕、页眉、标题、内容区、水印）前加一行简短中文注释，方便用户后续手动改字号/间距/颜色时能一眼定位，注释只写"这是什么区块"，不要写废话。
