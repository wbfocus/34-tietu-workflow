# -*- coding: utf-8 -*-
"""Render a single 3:4 HTML cover to 1080x1440 PNG/JPG via Playwright."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def render_cover(html: Path, out_png: Path) -> Path:
    from playwright.sync_api import sync_playwright

    out_png.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1440}, device_scale_factor=1)
        page.goto(html.resolve().as_uri(), wait_until="networkidle")
        page.wait_for_timeout(200)
        page.screenshot(path=str(out_png), clip={"x": 0, "y": 0, "width": 1080, "height": 1440})
        browser.close()
    jpg = out_png.with_suffix(".jpg")
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(out_png), "-q:v", "2", str(jpg)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    print("OK", jpg if jpg.exists() else out_png)
    return out_png


def main() -> int:
    p = argparse.ArgumentParser(description="Render one 1080x1440 HTML cover")
    p.add_argument("--html", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True, help="output .png path")
    args = p.parse_args()
    if not args.html.exists():
        print("missing html", args.html, file=sys.stderr)
        return 1
    render_cover(args.html, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
