#!/usr/bin/env node
/**
 * 批量把 HTML 卡片渲染成高清 PNG，等效于手动
 * Chrome DevTools -> 设备模拟器(DPR 3.0) -> Elements 面板 -> Capture node screenshot。
 *
 * 用法：
 *   node render.mjs <html文件或文件夹路径> [输出文件夹] [--dpr=3]
 *
 * 规则：
 *   - 输入是文件夹：渲染其中所有 *.html（按文件名里的数字排序），输出到 <文件夹>/成品图
 *   - 输入是单个 .html 文件：只渲染这一个，输出到同目录 /成品图
 *   - 截图对象固定为 <body> 的第一个直接子元素（就是卡片规范里那个写死宽高的最外层 div）
 */

import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

function parseArgs(argv) {
  const positional = [];
  let dpr = 3;
  for (const arg of argv) {
    if (arg.startsWith('--dpr=')) {
      dpr = parseFloat(arg.split('=')[1]);
    } else {
      positional.push(arg);
    }
  }
  return { positional, dpr };
}

function collectHtmlFiles(inputPath) {
  const stat = fs.statSync(inputPath);
  if (stat.isFile()) {
    return { baseDir: path.dirname(inputPath), files: [inputPath] };
  }
  const files = fs
    .readdirSync(inputPath)
    .filter((f) => f.toLowerCase().endsWith('.html'))
    .sort((a, b) => {
      const na = parseInt((a.match(/\d+/) || ['0'])[0], 10);
      const nb = parseInt((b.match(/\d+/) || ['0'])[0], 10);
      if (na !== nb) return na - nb;
      return a.localeCompare(b, 'zh-CN');
    })
    .map((f) => path.join(inputPath, f));
  return { baseDir: inputPath, files };
}

async function renderOne(browser, htmlFile, outputDir, dpr) {
  const context = await browser.newContext({
    deviceScaleFactor: dpr,
    viewport: { width: 2200, height: 2200 },
  });
  const page = await context.newPage();
  const fileUrl = pathToFileURL(path.resolve(htmlFile)).toString();

  try {
    await page.goto(fileUrl, { waitUntil: 'load', timeout: 45000 });
  } catch (err) {
    console.warn(`  [警告] 页面加载超时，仍尝试截图: ${htmlFile} (${err.message})`);
  }

  try {
    await page.waitForLoadState('networkidle', { timeout: 8000 });
  } catch {
    // 外部字体/图片没有彻底闲置也无妨，继续走
  }

  try {
    await page.evaluate(async () => {
      if (document.fonts && document.fonts.ready) {
        await document.fonts.ready;
      }
    });
  } catch {
    // 忽略字体 API 不可用的情况
  }

  await page.waitForTimeout(300);

  const handle = await page.evaluateHandle(() => document.body.firstElementChild || document.body);
  const el = handle.asElement();

  if (!el) {
    console.warn(`  [跳过] 找不到可截图的节点: ${htmlFile}`);
    await context.close();
    return false;
  }

  const box = await el.boundingBox();
  if (!box || box.width < 10 || box.height < 10) {
    console.warn(`  [跳过] 节点尺寸异常 (${box ? `${box.width}x${box.height}` : 'null'}): ${htmlFile}`);
    await context.close();
    return false;
  }

  const name = path.basename(htmlFile, path.extname(htmlFile));
  const outPath = path.join(outputDir, `${name}.png`);
  await el.screenshot({ path: outPath });

  console.log(
    `  ✔ ${path.basename(htmlFile)} -> ${outPath}  (${Math.round(box.width)}x${Math.round(box.height)} CSS px @${dpr}x DPR)`
  );

  await context.close();
  return true;
}

async function main() {
  const { positional, dpr } = parseArgs(process.argv.slice(2));
  const [inputArg, outputArg] = positional;

  if (!inputArg) {
    console.error('用法: node render.mjs <html文件或文件夹路径> [输出文件夹] [--dpr=3]');
    process.exit(1);
  }

  const inputPath = path.resolve(inputArg);
  if (!fs.existsSync(inputPath)) {
    console.error(`路径不存在: ${inputPath}`);
    process.exit(1);
  }

  const { baseDir, files } = collectHtmlFiles(inputPath);
  if (files.length === 0) {
    console.error(`未找到任何 .html 文件: ${inputPath}`);
    process.exit(1);
  }

  const outputDir = outputArg ? path.resolve(outputArg) : path.join(baseDir, '成品图');
  fs.mkdirSync(outputDir, { recursive: true });

  console.log(`共 ${files.length} 个 HTML 文件，DPR=${dpr}，输出目录: ${outputDir}\n`);

  const browser = await chromium.launch();
  let ok = 0;
  for (const file of files) {
    const success = await renderOne(browser, file, outputDir, dpr);
    if (success) ok += 1;
  }
  await browser.close();

  console.log(`\n完成: ${ok}/${files.length} 张成功。输出目录: ${outputDir}`);
  if (ok < files.length) {
    process.exitCode = 1;
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
