# -*- coding: utf-8 -*-
"""Prepend a 3:4 cover image as the first frames of a short video.

scale/pad 1080×1440, fps=30, concat cover + main.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "covers-3x4" / "style-catalog.json"
DEFAULT_HOLD = 0.034  # 1 frame @ 30fps（A 区锁定：成片第一帧仅 1 帧）
W, H = 1080, 1440


def ffmpeg_bin() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        raise SystemExit("未找到 ffmpeg。请安装并加入 PATH，或 pip install imageio-ffmpeg")


def load_catalog() -> dict:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def pick_style(seed: str | None = None) -> dict:
    cat = load_catalog()
    pool = cat["pool"]
    rng = random.Random(seed)
    return rng.choice(pool)


def ffprobe_has_audio(path: Path) -> bool:
    ff = ffmpeg_bin()
    proc = subprocess.run(
        [ff, "-hide_banner", "-i", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    blob = (proc.stderr or "") + (proc.stdout or "")
    return bool(re.search(r"Audio:\s", blob))


def prepend_cover(
    cover: Path,
    video: Path,
    out: Path,
    hold: float = DEFAULT_HOLD,
    width: int = W,
    height: int = H,
    pad_color: str = "0x000000",
) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    has_a = ffprobe_has_audio(video)
    pad = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color={pad_color},setsar=1,fps=30,format=yuv420p"
    )
    ff = ffmpeg_bin()
    if has_a:
        fc = (
            f"[0:v]{pad},trim=duration={hold},setpts=PTS-STARTPTS[v0];"
            f"[1:v]{pad},setpts=PTS-STARTPTS[v1];"
            f"[v0][v1]concat=n=2:v=1:a=0[vout];"
            f"aevalsrc=0:d={hold}:channel_layout=stereo:sample_rate=48000[a0];"
            f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo[a1];"
            f"[a0][a1]concat=n=2:v=0:a=1[aout]"
        )
        cmd = [
            ff, "-y",
            "-loop", "1", "-t", str(hold), "-i", str(cover),
            "-i", str(video),
            "-filter_complex", fc,
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            str(out),
        ]
    else:
        fc = (
            f"[0:v]{pad},trim=duration={hold},setpts=PTS-STARTPTS[v0];"
            f"[1:v]{pad},setpts=PTS-STARTPTS[v1];"
            f"[v0][v1]concat=n=2:v=1:a=0[vout]"
        )
        cmd = [
            ff, "-y",
            "-loop", "1", "-t", str(hold), "-i", str(cover),
            "-i", str(video),
            "-filter_complex", fc,
            "-map", "[vout]",
            "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
            "-an",
            "-movflags", "+faststart",
            str(out),
        ]
    print("RUN", " ".join(cmd[:8]), "...")
    subprocess.check_call(cmd)


def main() -> int:
    p = argparse.ArgumentParser(description="Prepend 3:4 cover as first frame(s)")
    p.add_argument("--cover", type=Path, help="1080x1440 cover image")
    p.add_argument("--video", type=Path, help="input mp4")
    p.add_argument("--out", type=Path, help="output mp4 with cover first")
    p.add_argument("--hold", type=float, default=DEFAULT_HOLD, help="cover hold seconds")
    p.add_argument("--pick-style", action="store_true")
    p.add_argument("--seed", default=None)
    args = p.parse_args()

    if args.pick_style:
        style = pick_style(args.seed)
        print(json.dumps(style, ensure_ascii=False, indent=2))
        return 0

    if not args.cover or not args.video or not args.out:
        p.error("--cover --video --out required unless --pick-style")
    if not args.cover.exists():
        print("missing cover", args.cover, file=sys.stderr)
        return 1
    if not args.video.exists():
        print("missing video", args.video, file=sys.stderr)
        return 1
    prepend_cover(args.cover, args.video, args.out, hold=args.hold)
    print("OK", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
