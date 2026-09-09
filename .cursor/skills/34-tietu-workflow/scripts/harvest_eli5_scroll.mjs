#!/usr/bin/env node
/**
 * Harvest an ELI5 390px long HTML into:
 *   成品图/long.png          full long image (WeChat)
 *   harvest/plate.png        same page with reveal nodes hidden
 *   harvest/sprites/NN.png   each reveal sprite
 *   harvest/timeline.json    boxes in output pixels
 *
 * Usage:
 *   node harvest_eli5_scroll.mjs "<html或文件夹>"
 */
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';

const CSS_W = 390;
const FRAME_W = 1080;
const FRAME_H = 1440;
const SCALE = FRAME_W / CSS_W;
const CSS_H = Math.round(FRAME_H / SCALE); // 520

const REVEAL_SEL = [
  '[data-eli5-reveal]',
  'h1',
  'h2',
  '.eli5-head',
  '.card-paper',
  '.card-blush',
  '.card-sage',
  '.card-callout',
  '.card-principle',
  '.tier',
  '.hl-bar',
  '.pill-dark',
  '.hero-orb',
  '.flow > .box',
  '.brick > .item',
  '.story',
  '.credit',
  '.c-foot',
].join(',');

function repoRoot() {
  return path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../../..');
}

function findHtml(inputPath) {
  const stat = fs.statSync(inputPath);
  if (stat.isFile()) return inputPath;
  const names = fs.readdirSync(inputPath).filter((f) => f.toLowerCase().endsWith('.html'));
  const prefer = names.find((n) => /长图|index|eli5/i.test(n));
  const pick = prefer || names.sort((a, b) => a.localeCompare(b, 'zh-CN'))[0];
  if (!pick) throw new Error(`未找到 HTML: ${inputPath}`);
  return path.join(inputPath, pick);
}

function even(n) {
  const x = Math.round(n);
  return x % 2 ? x + 1 : x;
}

async function main() {
  const inputArg = process.argv[2];
  if (!inputArg) {
    console.error('用法: node harvest_eli5_scroll.mjs <html文件或文件夹>');
    process.exit(1);
  }
  const inputPath = path.resolve(inputArg);
  const htmlFile = findHtml(inputPath);
  const jobDir = fs.statSync(inputPath).isDirectory() ? inputPath : path.dirname(htmlFile);
  const outDir = path.join(jobDir, '成品图');
  const harvestDir = path.join(jobDir, 'harvest');
  const spriteDir = path.join(harvestDir, 'sprites');
  fs.mkdirSync(outDir, { recursive: true });
  fs.mkdirSync(spriteDir, { recursive: true });

  const browsers = path.join(repoRoot(), '.playwright-browsers');
  if (fs.existsSync(browsers)) {
    process.env.PLAYWRIGHT_BROWSERS_PATH = browsers;
  }

  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: CSS_W, height: CSS_H },
    deviceScaleFactor: SCALE,
    isMobile: true,
    hasTouch: true,
    userAgent:
      'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
  });
  const page = await context.newPage();
  await page.goto(pathToFileURL(htmlFile).href, { waitUntil: 'load', timeout: 45000 });
  try {
    await page.waitForLoadState('networkidle', { timeout: 12000 });
  } catch {
    /* fonts CDN */
  }
  await page.evaluate(async () => {
    if (document.fonts?.ready) await document.fonts.ready;
  });
  await page.waitForTimeout(400);

  const phone = page.locator('#capture, .phone').first();
  if (!(await phone.count())) {
    throw new Error('找不到 #capture / .phone');
  }

  const nTagged = await page.locator('[data-eli5-reveal]').count();
  if (nTagged === 0) {
    await page.evaluate((sel) => {
      const nodes = [...document.querySelectorAll(sel)];
      const leaves = nodes.filter((el) => !nodes.some((o) => o !== el && o.contains(el)));
      leaves.forEach((el) => el.setAttribute('data-eli5-reveal', ''));
    }, REVEAL_SEL);
  }

  const longPath = path.join(outDir, 'long.png');
  await phone.screenshot({ path: longPath, animations: 'disabled' });

  const metrics = await page.evaluate(() => {
    const phoneEl = document.querySelector('#capture, .phone');
    const pr = phoneEl.getBoundingClientRect();
    const nodes = [...document.querySelectorAll('[data-eli5-reveal]')].filter(
      (el) => !el.closest('[data-eli5-reveal]') || el.closest('[data-eli5-reveal]') === el
    );
    const uniq = [];
    for (const el of nodes) {
      if (uniq.some((o) => o.contains(el) || el.contains(o))) {
        if (!uniq.some((o) => o.contains(el))) uniq.push(el);
        continue;
      }
      uniq.push(el);
    }
    const leaves = uniq.filter((el) => !uniq.some((o) => o !== el && o.contains(el)));
    leaves.forEach((el, i) => el.setAttribute('data-eli5-idx', String(i)));
    return {
      cssW: pr.width,
      cssH: pr.height,
      count: leaves.length,
    };
  });

  const boxes = await page.evaluate(() => {
    const phoneEl = document.querySelector('#capture, .phone');
    const pr = phoneEl.getBoundingClientRect();
    return [...document.querySelectorAll('[data-eli5-idx]')].map((el) => {
      const r = el.getBoundingClientRect();
      return {
        idx: Number(el.getAttribute('data-eli5-idx')),
        x: r.left - pr.left,
        y: r.top - pr.top,
        w: r.width,
        h: r.height,
      };
    });
  });

  await page.evaluate(() => {
    document.querySelectorAll('[data-eli5-idx]').forEach((el) => {
      el.dataset._prevVis = el.style.visibility;
      el.style.visibility = 'hidden';
    });
  });
  const platePath = path.join(harvestDir, 'plate.png');
  await phone.screenshot({ path: platePath, animations: 'disabled' });
  await page.evaluate(() => {
    document.querySelectorAll('[data-eli5-idx]').forEach((el) => {
      el.style.visibility = el.dataset._prevVis || '';
    });
  });

  const reveals = [];
  for (const box of boxes) {
    const handle = await page.$(`[data-eli5-idx="${box.idx}"]`);
    if (!handle) continue;
    const file = `sprites/${String(box.idx).padStart(2, '0')}.png`;
    const abs = path.join(harvestDir, file);
    await handle.screenshot({ path: abs, animations: 'disabled' });
    reveals.push({
      id: box.idx,
      file,
      x: even(box.x * SCALE),
      y: even(box.y * SCALE),
      w: even(box.w * SCALE),
      h: even(box.h * SCALE),
    });
  }

  const timeline = {
    html: path.basename(htmlFile),
    css_width: metrics.cssW,
    css_height: metrics.cssH,
    scale: SCALE,
    frame_w: FRAME_W,
    frame_h: FRAME_H,
    plate: 'plate.png',
    longshot: path.relative(harvestDir, longPath).replaceAll('\\', '/'),
    reveals,
  };
  const tlPath = path.join(harvestDir, 'timeline.json');
  fs.writeFileSync(tlPath, JSON.stringify(timeline, null, 2), 'utf8');

  console.log(`long:   ${longPath}`);
  console.log(`plate:  ${platePath}`);
  console.log(`reveals:${reveals.length}`);
  console.log(`css:    ${Math.round(metrics.cssW)}×${Math.round(metrics.cssH)} @${SCALE.toFixed(3)}x`);
  console.log(`timeline: ${tlPath}`);

  await browser.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
