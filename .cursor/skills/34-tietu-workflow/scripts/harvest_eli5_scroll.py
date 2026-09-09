# -*- coding: utf-8 -*-
"""Python harvest for ELI5 390px long HTML → long PNG + plate + sprites.

Used when Node Playwright is not available. Same outputs as harvest_eli5_scroll.mjs.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CSS_W = 390
FRAME_W = 1080
FRAME_H = 1440
SCALE = FRAME_W / CSS_W
CSS_H = round(FRAME_H / SCALE)

REVEAL_SEL = ",".join(
    [
        "[data-eli5-reveal]",
        "h1",
        "h2",
        ".eli5-head",
        ".card-paper",
        ".card-blush",
        ".card-sage",
        ".card-callout",
        ".card-principle",
        ".tier",
        ".hl-bar",
        ".pill-dark",
        ".hero-orb",
        ".flow > .box",
        ".brick > .item",
        ".story",
        ".credit",
        ".c-foot",
    ]
)


def even(n: float) -> int:
    x = int(round(n))
    return x + 1 if x % 2 else x


def find_html(input_path: Path) -> Path:
    if input_path.is_file():
        return input_path
    htmls = [p for p in input_path.iterdir() if p.suffix.lower() == ".html"]
    if not htmls:
        raise SystemExit(f"未找到 HTML: {input_path}")
    for key in ("长图", "index", "eli5"):
        for p in htmls:
            if key.lower() in p.stem.lower() or key in p.stem:
                return p
    return sorted(htmls, key=lambda p: p.name)[0]


def harvest(job_or_html: Path) -> Path:
    from playwright.sync_api import sync_playwright

    src = job_or_html.resolve()
    html = find_html(src)
    job = src if src.is_dir() else src.parent
    out_dir = job / "成品图"
    harvest_dir = job / "harvest"
    sprite_dir = harvest_dir / "sprites"
    out_dir.mkdir(parents=True, exist_ok=True)
    sprite_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": CSS_W, "height": CSS_H},
            device_scale_factor=SCALE,
            is_mobile=True,
            has_touch=True,
            user_agent=(
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
                "Mobile/15E148 Safari/604.1"
            ),
        )
        page = context.new_page()
        page.goto(html.resolve().as_uri(), wait_until="load", timeout=45000)
        try:
            page.wait_for_load_state("networkidle", timeout=12000)
        except Exception:
            pass
        page.evaluate("async () => { if (document.fonts?.ready) await document.fonts.ready }")
        page.wait_for_timeout(400)

        phone = page.locator("#capture, .phone").first
        if phone.count() == 0:
            raise SystemExit("找不到 #capture / .phone")

        if page.locator("[data-eli5-reveal]").count() == 0:
            page.evaluate(
                """(sel) => {
                  const nodes = [...document.querySelectorAll(sel)];
                  nodes.filter(el => !nodes.some(o => o !== el && o.contains(el)))
                    .forEach(el => el.setAttribute('data-eli5-reveal', ''));
                }""",
                REVEAL_SEL,
            )

        long_path = out_dir / "long.png"
        phone.screenshot(path=str(long_path), animations="disabled")

        metrics = page.evaluate(
            """() => {
              const phoneEl = document.querySelector('#capture, .phone');
              const pr = phoneEl.getBoundingClientRect();
              const nodes = [...document.querySelectorAll('[data-eli5-reveal]')];
              const leaves = nodes.filter(el => !nodes.some(o => o !== el && o.contains(el)));
              leaves.forEach((el, i) => el.setAttribute('data-eli5-idx', String(i)));
              return { cssW: pr.width, cssH: pr.height, count: leaves.length };
            }"""
        )
        boxes = page.evaluate(
            """() => {
              const phoneEl = document.querySelector('#capture, .phone');
              const pr = phoneEl.getBoundingClientRect();
              return [...document.querySelectorAll('[data-eli5-idx]')].map(el => {
                const r = el.getBoundingClientRect();
                return {
                  idx: Number(el.getAttribute('data-eli5-idx')),
                  x: r.left - pr.left, y: r.top - pr.top, w: r.width, h: r.height
                };
              });
            }"""
        )
        page.evaluate(
            """() => {
              document.querySelectorAll('[data-eli5-idx]').forEach(el => {
                el.dataset._prevVis = el.style.visibility;
                el.style.visibility = 'hidden';
              });
            }"""
        )
        plate_path = harvest_dir / "plate.png"
        phone.screenshot(path=str(plate_path), animations="disabled")
        page.evaluate(
            """() => {
              document.querySelectorAll('[data-eli5-idx]').forEach(el => {
                el.style.visibility = el.dataset._prevVis || '';
              });
            }"""
        )

        reveals = []
        for box in boxes:
            loc = page.locator(f"[data-eli5-idx='{box['idx']}']")
            rel = f"sprites/{int(box['idx']):02d}.png"
            loc.screenshot(path=str(harvest_dir / rel), animations="disabled")
            reveals.append(
                {
                    "id": int(box["idx"]),
                    "file": rel,
                    "x": even(box["x"] * SCALE),
                    "y": even(box["y"] * SCALE),
                    "w": even(box["w"] * SCALE),
                    "h": even(box["h"] * SCALE),
                }
            )

        timeline = {
            "html": html.name,
            "css_width": metrics["cssW"],
            "css_height": metrics["cssH"],
            "scale": SCALE,
            "frame_w": FRAME_W,
            "frame_h": FRAME_H,
            "plate": "plate.png",
            "longshot": "../成品图/long.png",
            "reveals": reveals,
        }
        tl_path = harvest_dir / "timeline.json"
        tl_path.write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
        browser.close()

    print(f"long:    {long_path}")
    print(f"plate:   {plate_path}")
    print(f"reveals: {len(reveals)}")
    print(f"timeline:{tl_path}")
    return job


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    args = ap.parse_args()
    if not args.input.exists():
        print(f"路径不存在: {args.input}", file=sys.stderr)
        return 1
    harvest(args.input)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
