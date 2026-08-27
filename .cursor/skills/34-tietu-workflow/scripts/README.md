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

## 原理

1. Playwright 无头 Chromium，按贴图写死的宽高加载 HTML。
2. 等 `load` + `networkidle` + `document.fonts.ready`。
3. 截 `<body>` 第一个直接子元素（1080×1440 最外层 div）。
