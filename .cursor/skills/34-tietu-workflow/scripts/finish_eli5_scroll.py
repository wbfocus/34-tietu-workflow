# -*- coding: utf-8 -*-
"""One-shot ELI5 long-image harvest + 3:4 pop-in scroll MP4 + official cover.

Usage:
  py -3 finish_eli5_scroll.py "<套图文件夹>"
  py -3 finish_eli5_scroll.py "<套图文件夹>" --title "第一行|第二行" --sub "副标"
  py -3 finish_eli5_scroll.py "<套图文件夹>" --cover-only
"""
from __future__ import annotations

import argparse
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

from finish_cards_media import (  # noqa: E402
    BRAND_DEFAULT,
    CATALOG,
    make_cover_alts,
    make_official_cover,
    pick_cover_style,
)
from prepend_cover_frame import prepend_cover  # noqa: E402

PILL_DEFAULT = "经营分析小卡片"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("+", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=cwd)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


def copy_theme_css(job: Path) -> None:
    """Copy shared long-scroll CSS into the job folder.

    layout-long.css is always overwritten so spacing fixes (e.g. principle
    margin-top) land on re-runs. theme-*-long.css only copies if missing
    (job may carry a local theme tweak).
    """
    layout = "layout-long.css"
    src_layout = REF / layout
    if src_layout.exists():
        shutil.copy2(src_layout, job / layout)
    for name in (
        "theme-a-long.css",
        "theme-b-long.css",
        "theme-c-long.css",
        "theme-d-long.css",
        "theme-e-long.css",
        "theme-f-long.css",
        "theme-g-long.css",
        "theme-h-long.css",
        "theme-i-long.css",
        "theme-j-long.css",
        "theme-k-long.css",
    ):
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


def scroll_mp4_path(job: Path, day: str | None = None) -> Path:
    from delivery_names import MODE_SCROLL, delivery_mp4

    return delivery_mp4(job / "成品视频", MODE_SCROLL, job.name, day=day)


def scroll_cover_mp4_path(job: Path, day: str | None = None) -> Path:
    from delivery_names import MODE_SCROLL, delivery_mp4

    return delivery_mp4(job / "成品视频", MODE_SCROLL, job.name, cover=True, day=day)


def attach_cover(
    job: Path,
    title: str,
    sub: str,
    pill: str,
    brand: str,
    style_id: str,
    day: str | None = None,
) -> Path:
    cover_png = make_official_cover(job, title, sub, pill, brand, style_id)
    make_cover_alts(job, title, sub, pill, brand, primary_style=style_id, count=3)
    video = scroll_mp4_path(job, day=day)
    if not video.is_file():
        raise SystemExit(f"缺少上滑成片: {video}")
    out_with = scroll_cover_mp4_path(job, day=day)
    prepend_cover(cover_png, video, out_with)
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
    ap.add_argument(
        "--style",
        default="",
        help="1 / 1b / 2 / 3 / 4 / 5 / 6 / 7 / 8；空则加权抽签并避开最近用过的（勿每次默认 4）",
    )
    ap.add_argument("--seed", default=None)
    ap.add_argument("--date", default="", help="成片日期 YYYY-MM-DD，默认今天")
    ap.add_argument("--bgm", type=Path, default=None, help="指定 BGM；默认从曲库随机")
    ap.add_argument("--no-bgm", action="store_true", help="不要背景音乐（例外才用）")
    ap.add_argument("--skip-cover", action="store_true")
    ap.add_argument("--cover-only", action="store_true", help="已有上滑 MP4 时只出封面并拼第一帧")
    ap.add_argument(
        "--mix-bgm-only",
        action="store_true",
        help="不重渲画面，只给已有成片叠 BGM（含带封面版）",
    )
    args = ap.parse_args()
    job = args.job.resolve()
    if not job.is_dir():
        print(f"不是文件夹: {job}", file=sys.stderr)
        return 1

    if args.mix_bgm_only:
        from eli5_scroll_video import mix_bgm_onto_mp4, pick_scroll_bgm
        from delivery_names import MODE_SCROLL, delivery_mp4

        bgm_path = pick_scroll_bgm(job, None if args.no_bgm else args.bgm)
        if bgm_path is None:
            print("没有可用 BGM", file=sys.stderr)
            return 1
        video_dir = job / "成品视频"
        # 只改无封面成片，再按现成封面图重拼带封面版（禁止直接 mix 带封面文件，
        # 否则容易留下「时长多 1/30、画面却没有封面」的坏片）
        base_mp4 = delivery_mp4(video_dir, MODE_SCROLL, job.name, cover=False, day=args.date or None)
        if not base_mp4.is_file():
            print(f"缺少成片: {base_mp4}", file=sys.stderr)
            return 1
        mix_bgm_onto_mp4(base_mp4, bgm_path)
        cover_png = job / "封面" / "cover-3x4.png"
        if cover_png.is_file():
            out_with = delivery_mp4(video_dir, MODE_SCROLL, job.name, cover=True, day=args.date or None)
            prepend_cover(cover_png, base_mp4, out_with)
        else:
            print("WARN 无封面/cover-3x4.png，跳过带封面版", file=sys.stderr)
        print("done (bgm only)")
        return 0

    inferred_title, inferred_sub = infer_cover_copy(job)
    title = args.title.strip() or inferred_title
    sub = args.sub.strip() or inferred_sub
    style_id = pick_cover_style(args.style, seed=args.seed, job=job)

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

        compose(job, day=args.date or None, bgm=args.bgm, no_bgm=args.no_bgm)

    if args.skip_cover:
        print("done (no cover)")
        return 0

    print(f"cover title: {title}")
    print(f"cover sub:   {sub}")
    attach_cover(job, title, sub, args.pill, args.brand, style_id, day=args.date or None)
    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
