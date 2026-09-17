# -*- coding: utf-8 -*-
"""钉钉/微信能播的成片规格。只贴 High 4.0 标签不够，时间基错了照样拒收。"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

FPS = 30
V_TIMEBASE = "15360"  # 30 * 512；禁止默认 1000k
COVER_HOLD = 1.0 / FPS  # 正好 1 帧。0.034 会变成 30.01 fps
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


def x264_compat(*, crf: str | int = 18, preset: str = "medium") -> list[str]:
    return [
        "-c:v", "libx264",
        "-profile:v", "high",
        "-level", "4.0",
        "-x264-params", "level=4.0",
        "-r", str(FPS),
        "-video_track_timescale", V_TIMEBASE,
        "-pix_fmt", "yuv420p",
        "-crf", str(crf),
        "-preset", preset,
        "-movflags", "+faststart",
    ]


def aac_compat(bitrate: str = "128k") -> list[str]:
    return ["-c:a", "aac", "-b:a", bitrate, "-ar", "48000", "-ac", "2"]


def probe_ffmpeg(path: Path) -> str:
    proc = subprocess.run(
        [ffmpeg_bin(), "-hide_banner", "-i", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return (proc.stderr or "") + (proc.stdout or "")


def qa_mp4_compat(path: Path) -> list[str]:
    """成片不过这条，不准当交付。钉钉看时间基，不看标签。"""
    if not path.is_file():
        return [f"没有文件: {path}"]
    blob = probe_ffmpeg(path)
    errs: list[str] = []
    if "1080x1440" not in blob:
        errs.append("尺寸不是 1080×1440")
    if "h264 (High)" not in blob:
        errs.append("不是 H.264 High")
    if "yuv420p" not in blob:
        errs.append("像素格式不是 yuv420p")
    if re.search(r"30\.0*[1-9]\s*fps", blob) or "30.01 fps" in blob:
        errs.append("帧率是 30.01（钉钉拒收），必须整 30 fps")
    elif not re.search(r"\b30 fps\b", blob):
        errs.append("不是 30 fps")
    if re.search(r"\b1000k tbn\b", blob) or re.search(r"\b1k tbn\b", blob):
        errs.append("时间基是 1000k tbn（钉钉拒收），必须 15360 tbn")
    elif "15360 tbn" not in blob:
        errs.append("时间基不是 15360 tbn")
    if re.search(r"Audio:\s", blob) and "48000 Hz" not in blob:
        errs.append("音频不是 48kHz")
    return errs


def assert_mp4_compat(path: Path) -> None:
    errs = qa_mp4_compat(path)
    if not errs:
        print("MP4 COMPAT OK", path)
        return
    print("MP4 COMPAT FAIL（钉钉/微信会拒收）", file=sys.stderr)
    for e in errs:
        print(" -", e, file=sys.stderr)
    raise SystemExit(1)
