# -*- coding: utf-8 -*-
"""橱窗砸入出片入口：成品图 →「套图文件夹名.mp4」（不写轮播成片）。

Usage:
  py -3 finish_cards_showcase.py "<贴图文件夹>" --title "毛利率掉了别只会说成本升了"
  py -3 finish_cards_showcase.py "<贴图文件夹>" --tabs "封面|口径|铁律|方法"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from cards_to_mp4 import DEFAULT_WHOOSH, collect_pngs  # noqa: E402
from cards_to_showcase import (  # noqa: E402
    DEFAULT_EMPTY,
    DEFAULT_FADE,
    DEFAULT_HOLD,
    DEFAULT_SMASH,
    cards_to_showcase,
)
from qa_tietu import qa_png_fill  # noqa: E402
from finish_cards_media import resolve_card_dir, video_paths  # noqa: E402
from prepend_cover_frame import prepend_cover  # noqa: E402
from showcase_chrome import (  # noqa: E402
    default_tabs,
    fit_tabs,
    parse_tabs_from_wenan,
    parse_title_from_wenan,
)


def main() -> int:
    p = argparse.ArgumentParser(description="Cards folder → 3:4 showcase MP4 (TOC + smash)")
    p.add_argument("card_dir", type=Path)
    p.add_argument("--hold", type=float, default=DEFAULT_HOLD)
    p.add_argument("--fade", type=float, default=DEFAULT_FADE)
    p.add_argument("--empty", type=float, default=DEFAULT_EMPTY)
    p.add_argument("--smash", type=float, default=DEFAULT_SMASH)
    p.add_argument("--title", default="")
    p.add_argument("--tabs", default="", help="目录胶囊，| 分隔；默认读 文案.txt 第N张|短标签")
    p.add_argument("--bg", default="")
    p.add_argument("--bgm", type=Path, default=None)
    p.add_argument("--no-sfx", action="store_true")
    p.add_argument("--no-toc", action="store_true")
    args = p.parse_args()

    card_dir = resolve_card_dir(args.card_dir.resolve())
    img_dir = card_dir / "成品图"
    pngs = collect_pngs(img_dir)
    if not pngs:
        print("no png in", img_dir, file=sys.stderr)
        return 1
    fill_errs = qa_png_fill(img_dir)
    if fill_errs:
        print("PNG fill QA FAIL（底部空太大或压水印）:", file=sys.stderr)
        for e in fill_errs:
            print(" -", e, file=sys.stderr)
        return 1
    print("QA png fill OK")

    wenan = card_dir / "文案.txt"
    title = args.title.strip() or parse_title_from_wenan(
        wenan, card_dir.name.split("、", 1)[-1]
    )
    if args.tabs.strip():
        tabs = [x.strip() for x in args.tabs.split("|") if x.strip()]
    else:
        tabs = parse_tabs_from_wenan(wenan)
    tabs = fit_tabs(tabs or default_tabs(len(pngs)), len(pngs))

    paths = video_paths(card_dir)
    video_dir = paths["dir"]
    out = paths["showcase"]
    cards_to_showcase(
        pngs,
        out,
        hold=args.hold,
        fade=args.fade,
        empty=args.empty,
        smash=args.smash,
        bg=args.bg or None,
        whoosh=None if args.no_sfx else DEFAULT_WHOOSH,
        bgm=args.bgm,
        title=title,
        tabs=tabs,
        toc=not args.no_toc,
    )
    print("OK", out)
    cover_png = card_dir / "封面" / "cover-3x4.png"
    if cover_png.is_file():
        out_with = paths["showcase_cover"]
        prepend_cover(cover_png, out, out_with, width=1080, height=1440)
        print("OK", out_with)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
