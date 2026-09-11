# 3:4 贴图截图脚本（render.mjs）

## 一次性环境安装

在**仓库根目录**跑 `bootstrap.ps1` / `bootstrap.sh`，或在本目录：

```bash
# 浏览器装到本仓库（勿默认写 C:）
# Windows:  $env:PLAYWRIGHT_BROWSERS_PATH = "<仓库根>\.playwright-browsers"
npm install
npx playwright install chromium
```

## 用法

```bash
# 仓库根目录
node .cursor/skills/34-tietu-workflow/scripts/render.mjs ".\examples\gold-a-ceo-star-dark"
node .cursor/skills/34-tietu-workflow/scripts/render.mjs ".\workspace\HTMLcards\你的套图"
```

输出到该文件夹下的 `成品图/`，默认 DPR 3.0（3240×4320）。

## 橱窗砸入 MP4（独立，不改默认轮播）

```bash
py -3 finish_cards_showcase.py "<贴图文件夹>" --title "大标题"
# 产出 成品视频/showcase.mp4（1080×1440 · 3:4 · 每张静持 5 秒）
# 内置自检：PNG 竖向铺满 + 静持/空镜不得有音效
```

出片自检也可手跑：

```bash
py -3 qa_tietu.py pngs "<贴图文件夹>/成品图"
py -3 qa_tietu.py showcase "<贴图文件夹>/成品视频/showcase.mp4" --n 8 --hold 5
```

## ELI5 长图上滑 MP4（独立，无 BGM）

```bash
py -3 finish_eli5_scroll.py "<长图文件夹>" --title "第一行|第二行" --sub "副标"
# 产出 成品图/long.png
#      封面/cover-3x4.png（covers-3x4 官方 DNA，不是长图裁切）
#      成品视频/<文件夹>（上滑）.mp4
#      成品视频/<文件夹>（上滑带封面）.mp4
# 1080×1440 · 对象依次弹出 + 气泡音；封面只占成片第 0 帧
```

规范：`.cursor/skills/34-eli5-scroll/SKILL.md`

## 原理

1. Playwright 无头 Chromium，按贴图写死的宽高加载 HTML。
2. 等 `load` + `networkidle` + `document.fonts.ready`。
3. 截 `<body>` 第一个直接子元素（1080×1440 最外层 div）。
