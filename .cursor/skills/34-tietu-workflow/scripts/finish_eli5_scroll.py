# -*- coding: utf-8 -*-
"""One-shot ELI5 long-image harvest + 3:4 pop-in scroll MP4.

Usage:
  py -3 finish_eli5_scroll.py "<套图文件夹>"
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
SKILL = Path(__file__).resolve().parents[1]
ELI5 = SKILL.parent / "34-eli5-scroll"
REF = ELI5 / "references"
sys.path.insert(0, str(SCRIPTS))


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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("job", type=Path)
    args = ap.parse_args()
    job = args.job.resolve()
    if not job.is_dir():
        print(f"不是文件夹: {job}", file=sys.stderr)
        return 1
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
    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
