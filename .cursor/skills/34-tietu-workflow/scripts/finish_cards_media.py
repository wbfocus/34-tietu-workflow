# -*- coding: utf-8 -*-
"""Post-card media: 5s/image MP4 carousel + 3:4 HTML cover + prepend first frame.

Usage:
  py -3 finish_cards_media.py "<贴图文件夹>" ^
    --title "毛利率掉了|别只会说成本升了" --sub "从结果拆到价格、成本与结构" --pill "经营分析小卡片"
"""
from __future__ import annotations

import argparse
import html as html_lib
import json
import random
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COVERS = ROOT / "covers-3x4"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(COVERS))

from cards_to_mp4 import DEFAULT_BGM, DEFAULT_WHOOSH, cards_to_mp4, collect_pngs  # noqa: E402
from prepend_cover_frame import prepend_cover  # noqa: E402

CATALOG = json.loads((COVERS / "style-catalog.json").read_text(encoding="utf-8"))
BRAND_DEFAULT = "汪斌带你开公司"


def title_class(lines: list[str]) -> str:
    n = max((len(s) for s in lines), default=0)
    if n >= 6:
        return "chars6"
    if n >= 5:
        return "chars5"
    return ""


def split_title(raw: str) -> list[str]:
    raw = raw.replace("<br>", "|").replace("<br/>", "|").replace("\n", "|")
    lines = [x.strip() for x in raw.split("|") if x.strip()]
    if len(lines) > 2:
        raise SystemExit("封面大标题最多两行")
    return lines or [raw]


def playwright_env() -> dict:
    import os

    env = os.environ.copy()
    scripts_dir = ROOT / "scripts"
    if ROOT.parent.name == "skills" and ROOT.parents[1].name == ".cursor":
        repo_root = ROOT.parents[2]
    else:
        repo_root = ROOT
    portable_browsers = repo_root / ".playwright-browsers"
    legacy_browsers = Path(r"D:\devtools\tools\playwright-browsers")
    if "PLAYWRIGHT_BROWSERS_PATH" not in env:
        if portable_browsers.is_dir():
            env["PLAYWRIGHT_BROWSERS_PATH"] = str(portable_browsers)
        elif legacy_browsers.is_dir():
            env["PLAYWRIGHT_BROWSERS_PATH"] = str(legacy_browsers)
    env["NODE_PATH"] = str(scripts_dir / "node_modules")
    return env


def render_cover_file(html_path: Path, cover_png: Path) -> None:
    import os
    import shutil

    cover_png.parent.mkdir(parents=True, exist_ok=True)
    env = playwright_env()
    node = shutil.which("node")
    node_script = ROOT / "scripts" / "render_cover.mjs"
    if node and node_script.is_file():
        subprocess.check_call(
            [node, str(node_script), str(html_path), str(cover_png)],
            cwd=str(ROOT / "scripts"),
            env=env,
        )
        return
    if env.get("PLAYWRIGHT_BROWSERS_PATH"):
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = env["PLAYWRIGHT_BROWSERS_PATH"]
    elif "PLAYWRIGHT_BROWSERS_PATH" in os.environ and not Path(os.environ["PLAYWRIGHT_BROWSERS_PATH"]).is_dir():
        del os.environ["PLAYWRIGHT_BROWSERS_PATH"]
    sys.path.insert(0, str(COVERS))
    from render_cover import render_cover as render_cover_py  # noqa: E402

    render_cover_py(html_path, cover_png)


def make_official_cover(
    card_dir: Path,
    title: str,
    sub: str,
    pill: str,
    brand: str = BRAND_DEFAULT,
    style_id: str = "4",
) -> Path:
    """Write covers-3x4 HTML and screenshot to 封面/cover-3x4.png."""
    work = COVERS / "_work"
    work.mkdir(exist_ok=True)
    html_path = work / "cover.html"
    html_path.write_text(
        fill_cover_html(style_id, pill, title, sub, brand),
        encoding="utf-8",
    )
    cover_dir = card_dir / "封面"
    cover_png = cover_dir / "cover-3x4.png"
    render_cover_file(html_path, cover_png)
    (cover_dir / "cover.html").write_text(html_path.read_text(encoding="utf-8"), encoding="utf-8")
    return cover_png


def fill_cover_html(
    style_id: str,
    pill: str,
    title_raw: str,
    sub: str,
    brand: str,
) -> str:
    pool = {x["id"]: x for x in CATALOG["pool"]}
    if style_id not in pool:
        raise SystemExit(f"unknown style {style_id}")
    tpl = (COVERS / pool[style_id]["html"]).read_text(encoding="utf-8")
    lines = split_title(title_raw)
    if style_id == "4":
        if len(lines) == 1:
            title_html = html_lib.escape(lines[0])
        else:
            title_html = html_lib.escape(lines[0]) + "<br><span class=\"bad\">" + html_lib.escape(lines[1]) + "</span>"
        cls = ""
    else:
        title_html = "<br>".join(html_lib.escape(x) for x in lines)
        cls = title_class(lines)
    return (
        tpl.replace("{{PILL}}", html_lib.escape(pill))
        .replace("{{TITLE_HTML}}", title_html)
        .replace("{{TITLE_CLASS}}", cls)
        .replace("{{SUB}}", html_lib.escape(sub))
        .replace("{{BRAND}}", html_lib.escape(brand))
    )


def video_paths(card_dir: Path) -> dict[str, Path]:
    """成品视频按套图文件夹名命名，避免每套都叫 showcase.mp4。"""
    stem = card_dir.name.strip()
    vd = card_dir / "成品视频"
    return {
        "dir": vd,
        "showcase": vd / f"{stem}.mp4",
        "showcase_cover": vd / f"{stem}（带封面）.mp4",
        "carousel": vd / f"{stem}（轮播）.mp4",
        "carousel_cover": vd / f"{stem}（轮播带封面）.mp4",
    }


def resolve_card_dir(path: Path) -> Path:
    if (path / "成品图").is_dir():
        return path
    if path.name == "成品图":
        return path.parent
    return path


def main() -> int:
    p = argparse.ArgumentParser(description="Cards folder → MP4 + 3:4 cover")
    p.add_argument("card_dir", type=Path)
    p.add_argument("--hold", type=float, default=5.0)
    p.add_argument("--xfade", type=float, default=1.0)
    p.add_argument("--transition", default="mix")
    p.add_argument("--no-bgm", action="store_true")
    p.add_argument("--no-sfx", action="store_true")
    p.add_argument("--title", default="", help="两行用 | 分隔")
    p.add_argument("--sub", default="")
    p.add_argument("--pill", default="经营分析小卡片")
    p.add_argument("--brand", default=BRAND_DEFAULT)
    p.add_argument("--style", default="", help="1 / 1b / 2 / 3 / 4；空则随机")
    p.add_argument("--seed", default=None)
    p.add_argument("--skip-cover", action="store_true")
    args = p.parse_args()

    card_dir = resolve_card_dir(args.card_dir.resolve())
    img_dir = card_dir / "成品图"
    pngs = collect_pngs(img_dir)
    if not pngs:
        print("no png in", img_dir, file=sys.stderr)
        return 1

    paths = video_paths(card_dir)
    video_dir = paths["dir"]
    carousel = paths["carousel"]
    cards_to_mp4(
        pngs,
        carousel,
        hold=args.hold,
        transition=args.transition,
        xfade=args.xfade,
        bgm=None if args.no_bgm else DEFAULT_BGM,
        whoosh=None if args.no_sfx else DEFAULT_WHOOSH,
    )

    if args.skip_cover:
        return 0

    style_id = args.style
    if not style_id:
        style_id = random.Random(args.seed).choice([x["id"] for x in CATALOG["pool"]])
        print("picked style", style_id)

    title = args.title
    if not title:
        # fallback: 文案.txt first heading-ish line
        wenan = card_dir / "文案.txt"
        title = card_dir.name.split("、", 1)[-1]
        title = re.sub(r"[（(].*?[）)]", "", title).strip()
        if wenan.exists():
            first = wenan.read_text(encoding="utf-8").splitlines()
            for line in first:
                if "封面" in line and "标题" in line:
                    m = re.search(r"标题[：:]\s*(.+)", line)
                    if m:
                        title = m.group(1).split("|")[0].strip()
                    break
        parts = list(title)
        if len(title) > 8:
            mid = len(title) // 2
            title = title[:mid] + "|" + title[mid:]

    sub = args.sub or "3:4 知识卡轮播"
    cover_png = make_official_cover(
        card_dir, title, sub, args.pill, args.brand, style_id
    )

    out_with = paths["carousel_cover"]
    hold = float(CATALOG.get("first_frame", {}).get("hold_seconds", 0.034))
    prepend_cover(cover_png, carousel, out_with, hold=hold)
    print("OK", out_with)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
