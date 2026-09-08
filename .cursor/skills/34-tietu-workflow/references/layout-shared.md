# 三套主题共用 · 信息图版式

A / B / C **外壳不同**（玻璃 / Mesh / 奶油白卡），**骨架相同**。写任何主题的 HTML 前读本节 + [type-shared.md](type-shared.md)。

色值由各主题 CSS 决定。`.terra` / `.sage` / `.ochre` 是**角色类**，不是陶土色本身：

| 角色类 | 含义 | A 深色玻璃 | B 亮色高级 | C 奶油刊物 |
|---|---|---|---|---|
| `.terra` | 主锚 | `#FF7700` | `#FF7700` | `#D16C4F` |
| `.sage` | 辅色 | `#0EA5E9` | `#0284C7` | `#6F8A6A` |
| `.ochre` | 第三色 | `#38bdf8` | `#0EA5E9` | `#C4A46A` |

## 页眉 DNA（每张必有）

左：`.idx-sq` 圆角方标（白字页码）+ `.c-en` 英文大写小标 + `.c-cn` 人话中文栏目。  
右：`.wm-num` 浅色巨号（与页码相同）。  
奇数页方标 `.terra`，偶数 `.sage`。偶数页 `.c-en` 再加 `.sage`。

```html
<div class="relative">
  <div class="wm-num ui-title">03</div>
  <div class="flex items-center gap-4 relative z-10">
    <div class="idx-sq terra ui-bold">03</div>
    <div>
      <div class="c-en ui-bold">STAR</div>
      <div class="c-cn">星型模型</div>
    </div>
  </div>
</div>
```

页眉中文纪律见 type-shared（禁止「封面钩子」等内部词）。

## 页脚 DNA（`.board` 最后一块）

`.c-foot` 贴在水印上沿：左「小方块 + 老汪洞察 · 信息图」，右「01 / 08 · 短标签」。不要另起独立 CTA 底栏。

```html
<div class="c-foot ui-bold">
  <div><span class="c-foot-sq"></span>老汪洞察 · 信息图</div>
  <div>03 / 08 · 星型</div>
</div>
```

## 语义组件（类名三套共用）

| 类名 | 用途 |
|---|---|
| `.card-paper` | 普通内容卡（A=玻璃，B=渐变描边白卡，C=软阴影白卡） |
| `.card-callout` | 提示条 |
| `.card-blush` | 警示 / 强调底 |
| `.hl-bar` | 辅色条 + 左粗边 |
| `.card-principle` | 虚线原则框（**每卡 ≤1**） |
| `.hero-orb` | 封面大圆数字 + 虚线外环 |
| `.pill-dark` | 炭黑/深色胶囊（判断句 / 结尾转发） |
| `.tier` + `.tier-lab` | 左色块右正文的分层条 |
| `.dot-n` | 圆标序号 |
| `.x-mark` / `.ok-mark` | 坑 → 修 对比 |

## 版式节奏（一套至少换 3 种）

1. **封面**：大圆数字 + 判断条 + 底部标签行  
2. **对比**：左坑右修（`.x-mark` → `.ok-mark`）  
3. **分层**：`.tier` 递进（可 `w-[96%]` / `w-[92%]` 错位）  
4. **2×2 网格**：编号白卡  
5. **清单**：圆标 + 横条白卡  
6. **结尾**：原则框 + 三件错位收口 + `.pill-dark` 转发  

**禁止** 8 张全是「标题 + 等宽三列 + 底栏金句」。

## 外壳只做氛围，不做顶区占位

- A：1–2 个光晕 + 全卡 `.noise`，**不要**再做 200px 顶栏。  
- B：封面/结尾可用全卡 `.mesh` 叠在内容底下；内页不要 Mesh 顶区。  
- C：纯底，无 Mesh、无玻璃、无发光。  

`.board` / `.board-cover` 高度均为 **1310px** + `space-between`。**禁止 `flex-1` 撑高**。

## 写卡顺序

1. [type-shared.md](type-shared.md)  
2. 本节  
3. 当前主题 `theme-a-dark-glass.md` / `theme-b-light-premium.md` / `theme-c-cream-editorial.md`（只解决配色与材质）  
4. 打开对应金标准**同序号**页面对照骨架，再动笔  
