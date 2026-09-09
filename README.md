# 3:4 贴图工作流（34-tietu-workflow）

把文档 / 大纲做成 **1080×1440（3:4）** 知识卡套图，并合成带轻 chill 背景乐、丝滑翻页的竖版 MP4。

换电脑或分享给别人：克隆本仓库 → 用 Cursor 打开仓库根目录 → 跑一次安装脚本 → 即可按 skill 出卡。

## 换机后 3 步启用

1. 安装 [Node.js 20+](https://nodejs.org/)、[Python 3](https://www.python.org/)、[ffmpeg](https://ffmpeg.org/)（需在 PATH 里能跑 `node`、`py -3` 或 `python`、`ffmpeg`）。
2. 用 Cursor 打开本仓库根目录（不要只打开子文件夹）。
3. 在仓库根目录执行：

```powershell
# Windows
.\bootstrap.ps1
```

```bash
# macOS / Linux
chmod +x bootstrap.sh && ./bootstrap.sh
```

脚本会：在 skill 的 `scripts/` 里 `npm install`、安装 Playwright Chromium 到本仓库 `.playwright-browsers/`（不写进 git）。

首次截图需要能访问 Tailwind CDN 与 jsDelivr 字体（HarmonyOS Bold、霞鹜文楷）。

## 给 Cursor Agent

打开本仓库后，Agent 会读到：

- Skill：`.cursor/skills/34-tietu-workflow/SKILL.md`
- 规则：`.cursor/rules/34-tietu-workflow.mdc`、`34-tietu-watermark-safe-zone.mdc`

对 Agent 说「做一套 3:4 贴图」即可。主题必须先问 A 深色玻璃 / B 亮色高级。

新套图默认写到 `workspace/HTMLcards/`（该目录不提交）。

## 仓库里有什么

| 路径 | 作用 |
|---|---|
| `.cursor/skills/34-tietu-workflow/` | 完整 skill：规范、截图脚本、封面模板、BGM/音效 |
| `.cursor/rules/` | 主题必问、水印与防裁切铁律 |
| `examples/gold-a-ceo-star-dark/` | 主题 A 金标准 HTML（原 055） |
| `examples/gold-b-ceo-star-light/` | 主题 B 金标准 HTML（原 056） |
| `examples/sample-gm-variance-dark/` | 成型样例：毛利率差异拆解 HTML + 封面 + 成片 MP4 |
| `.cursor/skills/34-eli5-scroll/` | ELI5 长图上滑：390px HTML + 三套主题 + 弹出成片 |
| `examples/eli5-scroll-sample-c/` | ELI5 上滑样例（奶油主题） |
| `examples/_card-registry.yaml` | 防重复登记 |
| `workspace/HTMLcards/` | 你的新产出（gitignore） |

未打包进 git 的（体积或版权）：Playwright 浏览器、`node_modules`、@3x 成品 PNG、第三方频道专用 BGM。样例 HTML 可随时用 `render.mjs` 重新出图。

## 常用命令（仓库根目录）

```powershell
# 把某套 HTML 渲成 3:4 PNG（输出到该文件夹/成品图）
node .cursor/skills/34-tietu-workflow/scripts/render.mjs ".\examples\gold-a-ceo-star-dark"

# 合成轮播 MP4 + 3:4 封面
py -3 .cursor/skills/34-tietu-workflow/scripts/finish_cards_media.py ".\workspace\HTMLcards\你的套图文件夹" --title "第一行|第二行" --sub "副标" --pill "经营分析小卡片" --style 4
```

默认 BGM：Mixkit《Serene View》。翻页 whoosh 已压低。转场每次一种、各约 1 秒。

另有独立 **橱窗砸入** 成片（顶部目录胶囊 + 空镜 + 拖影砸入），不覆盖默认轮播：

```powershell
py -3 .cursor/skills/34-tietu-workflow/scripts/finish_cards_showcase.py ".\workspace\HTMLcards\你的套图文件夹" --title "大标题"
```

产出 `成品视频/showcase.mp4`（**1080×1440 · 3:4**，不是 9:16）。

另有独立 **ELI5 长图上滑**（大图少字长卷，不是多页贴图）：选 A/B/C 主题 → 390px HTML → 高清长图 PNG → 3:4 从下往上滑，卡片依次弹出 + 气泡音（**无 BGM、无口播字幕**）。

```powershell
py -3 .cursor/skills/34-tietu-workflow/scripts/finish_eli5_scroll.py ".\examples\eli5-scroll-sample-c"
```

产出 `成品图/long.png`、`封面/cover-3x4.png`（与贴图同一套 covers-3x4）、`成品视频/<文件夹>（上滑）.mp4` 与 `（上滑带封面）.mp4`。规范见 `.cursor/skills/34-eli5-scroll/SKILL.md`。

## 推到你的 GitHub

```powershell
cd "D:\Program Files\Cursor\34-tietu-workflow"
git remote add origin https://github.com/<你的用户名>/<仓库名>.git
git push -u origin main
```

另一台电脑：`git clone` 后用 Cursor 打开该文件夹，再跑 `bootstrap.ps1` / `bootstrap.sh`。

## 许可

- 工作流代码与规范：MIT（见 `LICENSE`）
- 金标准 / 样例文案：随仓库用于学习与对照出图
- BGM / 音效：Mixkit License（见 `.cursor/skills/34-tietu-workflow/assets/audio/CREDITS.txt`）
