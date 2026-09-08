# 备用主题索引

本 skill 注册三套**备用主题**（老汪品牌专用）。用户发文档做卡片时，**必须先问选哪套**，确认后再写 HTML。

## 主题一览

| ID | 名称 | 风格关键词 | 适用场景 | 规范文件 | 金标准样例 |
|---|---|---|---|---|---|
| **A** | 深色玻璃 | 玻璃模糊、光晕、噪点、科技感 | 夜间刷、信息流抢眼、深色氛围 | `theme-a-dark-glass.md` | `examples/gold-a-ceo-star-dark/` |
| **B** | 亮色高级 | Mesh 渐变、渐变描边、三层阴影、刊物感 | 日间刷、公众号知识卡、打印分享 | `theme-b-light-premium.md` | `examples/gold-b-ceo-star-light/` |
| **C** | 奶油刊物 | 奶油底、陶土橙、鼠尾草绿、圆角方标、巨号水印、虚线原则框 | 教程拆解、清单对比、日间信息图 | `theme-c-cream-editorial.md` | `examples/gold-c-workshop-editorial/` |

## 选主题话术（每次必问）

用户发来文档后，**先问、再动手**，不要默认跳过：

> 要做成 HTML 卡片，请选主题：
> - **A 深色玻璃** — 夜间/科技感，玻璃模糊 + 光晕
> - **B 亮色高级** — 日间/刊物感，Mesh 渐变 + 渐变边框
> - **C 奶油刊物** — 信息图感，陶土橙 + 鼠尾草绿（可选）
>
> 回复 A、B 或 C；若要两套，回复「A+B」。

### 例外（可直接执行、不必再问）

- 用户**已明确指定**主题（如「用深色玻璃」「做 B 亮色那套」「跟 055 一样」「用这套信息图风格 / C」）→ 直接用，不重复问。
- 用户说「两套都要」「A 和 B 各做一套」→ 分别建两个文件夹产出。

## 文件夹命名

选定主题后，在 `workspace/HTMLcards/` 下新建文件夹，标题后可加主题后缀便于区分：

- A：`0XX、选题标题（深色）`
- B：`0XX、选题标题（浅色）`
- C：`0XX、选题标题（刊物）`
- A+B 各一套：两个独立编号文件夹，或用户指定的命名。

## 写 HTML 前必读

0. `references/type-shared.md` — **三套共用文字铁律**（楷体正文 + 宋体标题 + 重点词换色 + 页眉禁内部词 + 成片按文件夹名）
0.5 `references/layout-shared.md` — **三套共用信息图骨架**（方标页眉 + 巨号水印 + `.c-foot` + 六种版式；A/B/C 只换外壳）
1. `references/anti-plastic-design.md` — 反塑料感审美纪律（版式手法、禁用项、出图前 QA）
2. `references/design-system.md` — 通用硬约束（尺寸、水印、截图结构）
3. **当前选定主题的** `theme-a-dark-glass.md` / `theme-b-light-premium.md` / `theme-c-cream-editorial.md` — 配色、组件、饱满度（字体服从 type-shared）

**主题规范优先于** `design-system.md` 中的旧版字体（ZCOOL / Ma Shan Zheng）和旧配色方案。字体一律以 `type-shared.md` 为准。

风格仍发「模板感」时，用 `awesome-design-md` 拉 `stripe`（B/C）或 `linear.app`（A）对照。A/B 色值不偏离天蓝+亮橙；**C 改用陶土+鼠尾草**，不要再叠品牌橙蓝。

## 共用品牌色（A / B 一致；C 见本主题规范）

来自 `wechat-workbench/brand.md`：

| 用途 | 色值 |
|---|---|
| 结构/标签 | 天蓝 `#0EA5E9` / `#0284C7` |
| 锚点/强调（每卡 ≤3 处） | 橙色 `#FF7700` |
| 浅色主题正文墨 | `#1C1917` |
