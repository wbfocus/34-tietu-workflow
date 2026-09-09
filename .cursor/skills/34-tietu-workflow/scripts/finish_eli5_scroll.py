# -*- coding: utf-8 -*-
"""One-shot ELI5 long-image harvest + 3:4 pop-in scroll MP4 + official cover.

Usage:
  py -3 finish_eli5_scroll.py "<套图文件夹>"
  py -3 finish_eli5_scroll.py "<套图文件夹>" --title "第一行|第二行" --sub "副标" --style 4
  py -3 finish_eli5_scroll.py "<套图文件夹>" --cover-only
"""
from __future__ import annotations

import argparse
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
SKILL = Path(__file__).resolve().parents[1]
ELI5 = SKILL.parent / "34-eli5-scroll"
REF = ELI5 / "references"
COVERS = SKILL / "covers-3x4"
sys.path.insert(0, str(SCRIPTS))

from finish_cards_media import BRAND_DEFAULT, CATALOG, make_official_cover  # noqa: E402
from prepend_cover_frame import prepend_cover  # noqa: E402

PILL_DEFAULT = "经营分析小卡片"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("+", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=cwd)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


def copy_theme_css(job: Path) -> None:
    for name in ("layout-long.css", "theme-a-long.css", "theme-b-long.css", "theme-c-long.css"):
        src = REF / name
        dst = job / name
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)


def find_html(job: Path) -> Path:
    htmls = [p for p in job.iterdir() if p.suffix.lower() == ".html"]
    if not htmls:
        raise SystemExit(f"文件夹里没有 HTML: {job}")
    for key in ("长图", "index", "eli5"):
        for p in htmls:
            if key in p.stem.lower() or key in p.stem:
                return p
    return sorted(htmls, key=lambda p: p.name)[0]


def _strip_tags(chunk: str) -> str:
    chunk = re.sub(r"<br\s*/?>", "|", chunk, flags=re.I)
    chunk = re.sub(r"<[^>]+>", "", chunk)
    chunk = re.sub(r"&nbsp;", " ", chunk)
    chunk = re.sub(r"\s+", " ", chunk)
    return chunk.strip()


def infer_cover_copy(job: Path) -> tuple[str, str]:
    html = find_html(job)
    text = html.read_text(encoding="utf-8")
    m = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S | re.I)
    raw = _strip_tags(m.group(1) if m else "")
    raw = raw.replace("，", "|").replace("：", "|").replace(":", "|")
    parts = [x.strip() for x in raw.split("|") if x.strip()]
    if not parts:
        name = re.sub(r"[（(].*?[）)]", "", job.name)
        name = re.sub(r"^eli5[-_、]?", "", name, flags=re.I).strip()
        parts = [name or job.name]
    if len(parts) == 1:
        s = parts[0]
        if len(s) > 6:
            mid = min(6, max(3, len(s) // 2))
            title = s[:mid] + "|" + s[mid: mid + 6]
        else:
            title = s
    else:
        title = "|".join(p[:6] for p in parts[:2])
    tm = re.search(r'class="tagline"[^>]*>(.*?)</p>', text, re.S | re.I)
    sub = _strip_tags(tm.group(1) if tm else "")
    sub = sub.replace("|", "")
    if len(sub) > 26:
        sub = sub[:26].rstrip("，,。；; ") + "…"
    if not sub:
        sub = "390px 长图上滑"
    return title, sub


def scroll_mp4_path(job: Path) -> Path:
    return job / "成品视频" / f"{job.name}（上滑）.mp4"


def scroll_cover_mp4_path(job: Path) -> Path:
    return job / "成品视频" / f"{job.name}（上滑带封面）.mp4"


def attach_cover(
    job: Path,
    title: str,
    sub: str,
    pill: str,
    brand: str,
    style_id: str,
) -> Path:
    cover_png = make_official_cover(job, title, sub, pill, brand, style_id)
    video = scroll_mp4_path(job)
    if not video.is_file():
        raise SystemExit(f"缺少上滑成片: {video}")
    out_with = scroll_cover_mp4_path(job)
    hold = float(CATALOG.get("first_frame", {}).get("hold_seconds", 0.034))
    prepend_cover(cover_png, video, out_with, hold=hold)
    fake = job / "成品图" / "cover-3x4.png"
    if fake.is_file():
        fake.unlink()
    print("cover", cover_png)
    print("mp4 ", out_with)
    return out_with


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("job", type=Path)
    ap.add_argument("--title", default="", help="两行用 | 分隔")
    ap.add_argument("--sub", default="")
    ap.add_argument("--pill", default=PILL_DEFAULT)
    ap.add_argument("--brand", default=BRAND_DEFAULT)
    ap.add_argument("--style", default="4", help="1 / 1b / 2 / 3 / 4；默认痛点钩子 4")
    ap.add_argument("--seed", default=None)
    ap.add_argument("--skip-cover", action="store_true")
    ap.add_argument("--cover-only", action="store_true", help="已有上滑 MP4 时只出封面并拼第一帧")
    args = ap.parse_args()
    job = args.job.resolve()
    if not job.is_dir():
        print(f"不是文件夹: {job}", file=sys.stderr)
        return 1

    inferred_title, inferred_sub = infer_cover_copy(job)
    title = args.title.strip() or inferred_title
    sub = args.sub.strip() or inferred_sub
    style_id = args.style.strip()
    if not style_id:
        style_id = random.Random(args.seed).choice([x["id"] for x in CATALOG["pool"]])
        print("picked style", style_id)

    if not args.cover_only:
        copy_theme_css(job)
        html = find_html(job)
        print(f"html: {html}")
        node = shutil.which("node")
        harvest_js = SCRIPTS / "harvest_eli5_scroll.mjs"
        if node and harvest_js.exists():
            run([node, str(harvest_js), str(job)])
        else:
            from harvest_eli5_scroll import harvest as harvest_py

            harvest_py(job)
        from eli5_scroll_video import compose

        compose(job)

    if args.skip_cover:
        print("done (no cover)")
        return 0

    print(f"cover title: {title}")
    print(f"cover sub:   {sub}")
    attach_cover(job, title, sub, args.pill, args.brand, style_id)
    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
