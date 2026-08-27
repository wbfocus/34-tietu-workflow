#!/usr/bin/env node
/**
 * Render one 1080×1440 HTML cover with this skill's Playwright Chromium.
 *
 *   node render_cover.mjs <cover.html> <out.png>
 */
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';

async function main() {
  const [htmlArg, outArg] = process.argv.slice(2);
  if (!htmlArg || !outArg) {
    console.error('用法: node render_cover.mjs <cover.html> <out.png>');
    process.exit(1);
  }
  const htmlFile = path.resolve(htmlArg);
  const outPng = path.resolve(outArg);
  if (!fs.existsSync(htmlFile)) {
    console.error('missing html', htmlFile);
    process.exit(1);
  }
  fs.mkdirSync(path.dirname(outPng), { recursive: true });

  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1080, height: 1440 },
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();
  await page.goto(pathToFileURL(htmlFile).toString(), { waitUntil: 'load', timeout: 45000 });
  try {
    await page.waitForLoadState('networkidle', { timeout: 8000 });
  } catch {
    /* ignore */
  }
  await page.waitForTimeout(200);
  await page.screenshot({
    path: outPng,
    clip: { x: 0, y: 0, width: 1080, height: 1440 },
  });
  await context.close();
  await browser.close();

  const jpg = outPng.replace(/\.png$/i, '.jpg');
  spawnSync('ffmpeg', ['-y', '-i', outPng, '-q:v', '2', jpg], { stdio: 'ignore' });
  console.log('OK', fs.existsSync(jpg) ? jpg : outPng);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
