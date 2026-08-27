---
name: 34-tietu-workflow
description: 3:4贴图制作工作流。把文档/大纲/文案一键做成 1080×1440（3:4）贴图套图，用于小红书图文、微信贴图、知识卡等。触发词：3:4贴图、贴图制作、贴图套图、小红书贴图、微信贴图、HTML卡片、知识卡、一键出贴图。先问用户选主题（A深色玻璃/B亮色高级），再自动完成：文案拆分 → HTML → 高清截图 → 配套发布文案 → 5秒/张翻页 MP4（BGM） → 3:4 封面。
license: MIT
---

# 3:4 贴图制作工作流

把文档/大纲一键做成 **3:4 贴图套图**。视觉规范见 `references/design-system.md`。

## 默认尺寸（铁律）

| 比例 | 像素 | 用途 |
|---|---|---|
| **3:4 竖版（默认）** | **1080 × 1440** | 小红书图文、微信贴图、朋友圈知识卡 |

除非用户明确要求其它比例，**一律 3:4**。不要用 16:9 或横版替代。

版式与拆图全自动，**但主题必须先问**。用户发来文档时，写 HTML 之前**必须先确认主题**（见「主题选择」）；用户已明确指定 A/B 的除外。

其余可停下来问用户的情况：

- 完全无法判断内容形态（知识点清单 / 流程步骤 / 痛点方案等）。
- 文档有关键信息缺口（课程名、联系方式、CTA 等水印外必须真实的信息）。

张数按默认规则自定；**配色与视觉由所选主题决定**。做完一句话汇报，不出分镜方案等用户点头（主题除外）。

## 触发场景

用户要求做 **3:4 贴图、贴图套图、小红书图文、微信贴图、知识卡、一键出贴图**——均走本工作流。

**不走本 skill**：公众号正文横版流程图 → `gzh-article-html-cards`（默认 1440×1080）。

## 主题选择（第 0 步，每次必做）

读 `references/theme-index.md`。用户发来文档后，**先问选哪套备用主题**：

> 要做成 **3:4 贴图套图**（1080×1440），请选主题：
> - **A 深色玻璃** — 夜间/科技感（玻璃模糊 + 光晕 + 噪点）
> - **B 亮色高级** — 日间/刊物感（Mesh 渐变 + 渐变边框 + 三层阴影）
>
> 回复 A 或 B；若要两套各做一份，回复「A+B」。

**不必再问**：用户已说「深色」「亮色」「A」「B」「跟 055/056 一样」。

| 选择 | 必读规范 | 金标准样例 |
|---|---|---|
| A | `references/theme-a-dark-glass.md` | `examples/gold-a-ceo-star-dark/` |
| B | `references/theme-b-light-premium.md` | `examples/gold-b-ceo-star-light/` |

文件夹名建议加后缀：`（深色）` / `（浅色）`。

## 防重复登记（第 0.5 步）

读仓库根目录 `examples/_card-registry.yaml`（本机新产出也可写在 `workspace/HTMLcards/_card-registry.yaml`）。

1. `slug` 已有 `status: done` 的套图 → **告知并跳过**，除非用户说「重做 / 换主题再出一套」。
2. 若宿主项目还有 `wechat-workbench/published/_index.md`，批量出卡时对照它，只处理未登记 slug；**独立使用本仓库时跳过这一条**。
3. 交付后更新 registry。

## 总流程

```text
0. 问主题 → A / B（已指定则跳过）
1. 读文档 → 主题、语气、读者
2. 拆贴图 → 分镜表（封面 + 内容 + 结尾），内部决定不等确认
2.5 读反塑料感 → references/anti-plastic-design.md（三张旋钮 + 版式手法 + 禁用项）
3. 写 HTML → design-system.md + 所选主题（3:4 竖版 1080×1440）；套图版式要有节奏变化
3.5 出图前 QA → anti-plastic-design.md 第七节 + **design-system 水印安全区 & 画布防裁切**（见 `.cursor/rules/34-tietu-watermark-safe-zone.mdc` B/C 节；**截图前不可跳过**）
4. 截图 → scripts/render.mjs → 成品图/*.png
5. 配套文案 + 关键词
6. 合成轮播 MP4 → 每张可读 **5 秒** + 交界 **约 1 秒丝滑转场**（每次一种、不重复；8 张仍 ≈ 40 秒）+ 固定 BGM
7. 出 3:4 封面（1080×1440）并拼进成片第 0 帧
```

### 第 4 步：截图命令

```bash
node ".cursor/skills/34-tietu-workflow/scripts/render.mjs" "<贴图文件夹绝对路径>"
```

- DPR 3.0 → 输出 3240×4320 PNG，适合小红书上传
- 输出目录：`<文件夹>\成品图\`

### 第 6–7 步：轮播 MP4 + 3:4 封面（出卡后必做）

能力已打进本 skill（`covers-3x4/` + `scripts/cards_to_mp4.py` + `scripts/prepend_cover_frame.py`），不依赖外部视频仓库。

封面文案从本套卡提炼：**系列标、最多两行大标题、一句副标**。痛点钩子用 style `4`，否则随机或按主题选 `1`/`2`/`3`。

```bash
py -3 ".cursor/skills/34-tietu-workflow/scripts/finish_cards_media.py" "<贴图文件夹绝对路径>" --title "第一行|第二行" --sub "副标" --pill "系列标" --style 4
```

也可拆开跑：

```bash
py -3 ".cursor/skills/34-tietu-workflow/scripts/cards_to_mp4.py" "<贴图文件夹>/成品图" --hold 5
node ".cursor/skills/34-tietu-workflow/scripts/render_cover.mjs" "<封面>/cover.html" "<封面>/cover-3x4.png"
py -3 ".cursor/skills/34-tietu-workflow/scripts/prepend_cover_frame.py" --cover "<封面>/cover-3x4.png" --video "<成品视频>/carousel.mp4" --out "<成品视频>/carousel_with_cover.mp4"
```

- 轮播：1080×1440 · 30fps · 每张可读 5 秒 · **每次一种丝滑转场（约 1 秒）**（叠在交界，总时长仍是 N×5）· 轻 chill BGM + 轻 whoosh
- 封面：布局 DNA 见 `covers-3x4/README.md`（居中、两边留空、标题最多两行）
- 成片第一帧：封面仅 **1 帧**（约 0.034s），随后进入卡片轮播

转场默认 `mix`：fade → smoothleft → distance → smoothup → hblur → smoothright → radial… 相邻不同。不用 3D 卷页、硬 wipe。`--transition none` 可关动画。

## 产出目录

新套图默认写到仓库根目录 `workspace/HTMLcards/`：

```text
workspace/HTMLcards/0XX、选题标题（深色/浅色）/
  文案.txt
  1.html ~ N.html
  成品图/1.png ~ N.png    ← 3:4 贴图成品（1080×1440 @3x）
  成品视频/carousel.mp4              ← 每张 5 秒 + 翻页动画 + BGM
  成品视频/carousel_with_cover.mp4   ← 封面第一帧 + 轮播
  封面/cover-3x4.png (.jpg)          ← 3:4 封面
  配套文案与关键词.md
```

## 完成后汇报

> 已生成 N 张 **3:4 贴图**（1080×1440），成品在 `workspace/HTMLcards\0XX、…\成品图\`；轮播 MP4 在 `成品视频\`（N×5 秒）；3:4 封面在 `封面\cover-3x4.png`。

## 返修

只改被点名的 `.html`，重跑 `render.mjs` 覆盖对应 PNG，再跑 `finish_cards_media.py` 更新 MP4/封面；主题未变则不重写配套文案。

## 依赖参考

- `examples/_card-registry.yaml` — 产出登记 + 防重复
- `examples/gold-a-ceo-star-dark/` — 主题 A 金标准
- `examples/gold-b-ceo-star-light/` — 主题 B 金标准
- `examples/sample-gm-variance-dark/` — 完整样例（HTML + 封面 + 成片 MP4）
- `references/anti-plastic-design.md` — 反塑料感审美纪律（写卡前 + 出图前 QA）
- `references/theme-index.md` — 主题索引
- `references/theme-a-dark-glass.md` / `theme-b-light-premium.md`
- `references/design-system.md` — 3:4 尺寸、水印、截图结构
- `awesome-design-md` — 可选；风格发飘时对照 stripe / linear.app DESIGN.md（本包不强制附带）
- `references/content-split-rules.md` — 文案拆分
- `references/caption-keywords.md` — 发布文案
- `scripts/render.mjs` — 批量截图
- `scripts/cards_to_mp4.py` — 成品图 → 5 秒/张轮播 MP4（翻页 + BGM）
- `assets/audio/bgm-serene-view.mp3` — 默认 BGM（Mixkit《Serene View》，轻 chill 底床）
- `assets/sfx/whoosh-page.wav` — 翻页音效
- `covers-3x4/` — 3:4 HTML 封面模板 + 截图
- `scripts/prepend_cover_frame.py` — 封面拼成片第一帧
- `scripts/finish_cards_media.py` — 第 6–7 步一键入口
