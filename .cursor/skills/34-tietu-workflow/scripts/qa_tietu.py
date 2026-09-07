# -*- coding: utf-8 -*-
"""出片自检：竖向铺满 + 橱窗音效只能出现在切页。

Usage:
  py -3 qa_tietu.py pngs "<成品图文件夹>"
  py -3 qa_tietu.py showcase "<showcase.mp4>" --n 8 --hold 5 --fade 0.35 --empty 0.50 --smash 0.25
"""
from __future__ import annotations

import argparse
import math
import subprocess
import sys
import tempfile
import wave
from array import array
from pathlib import Path

from cards_to_mp4 import collect_pngs

CSS_H = 1440
WM_TOP = 1360  # 水印安全区上沿（css px）
FILL_MIN = 1240  # 最后一块内容至少到这里，否则底空一大块
HOLD_RMS_MAX = 550  # 静持/空镜允许的编码器底噪
HIT_RMS_MIN = 1800  # 砸入段必须有一下


def _row_energy(im, y: int, bg: tuple[int, int, int]) -> float:
    w, _ = im.size
    px = im.load()
    acc = 0.0
    n = 0
    step = max(1, w // 360)
    for x in range(0, w, step):
        r, g, b = px[x, y][:3]
        acc += abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2])
        n += 1
    return acc / max(1, n)


def png_last_content_css(path: Path) -> float:
    from PIL import Image

    im = Image.open(path).convert("RGB")
    w, h = im.size
    scale = h / CSS_H
    px = im.load()
    # 四角取底色，避开 mesh / 卡片
    samples = [
        px[4, 4][:3],
        px[w - 5, 4][:3],
        px[4, min(h - 5, int(200 * scale))][:3],
        px[w - 5, min(h - 5, int(200 * scale))][:3],
    ]
    bg = tuple(sum(c[i] for c in samples) // 4 for i in range(3))
    cut = int(WM_TOP * scale)
    last = 0
    step = max(1, int(scale))
    for y in range(0, cut, step):
        if _row_energy(im, y, bg) > 22:
            last = y
    return last / scale


def qa_png_fill(folder: Path) -> list[str]:
    errs: list[str] = []
    pngs = collect_pngs(folder)
    if not pngs:
        return [f"no png in {folder}"]
    for p in pngs:
        last = png_last_content_css(p)
        if last < FILL_MIN:
            errs.append(
                f"{p.name}: 底部空太大（最后内容约 y={last:.0f}px，应 ≥{FILL_MIN}，贴在水印上沿）"
            )
        if last > WM_TOP + 8:
            errs.append(f"{p.name}: 内容可能压进水印区（y={last:.0f}px）")
    return errs


def _decode_mono_wav(mp4: Path) -> tuple[int, array]:
    wav_path = Path(tempfile.gettempdir()) / f"qa_{mp4.stem}.wav"
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(mp4),
            "-ac",
            "1",
            "-ar",
            "48000",
            str(wav_path),
        ]
    )
    with wave.open(str(wav_path), "rb") as wav:
        sr = wav.getframerate()
        n = wav.getnframes()
        raw = wav.readframes(n)
    samples = array("h")
    samples.frombytes(raw)
    return sr, samples


def _rms_windows(samples: array, sr: int, hop: float = 0.05) -> list[tuple[float, float]]:
    step = max(1, int(sr * hop))
    out: list[tuple[float, float]] = []
    for i in range(0, len(samples), step):
        chunk = samples[i : i + step]
        if not chunk:
            break
        rms = math.sqrt(sum(int(x) * int(x) for x in chunk) / len(chunk))
        out.append((i / sr, rms))
    return out


def showcase_windows(
    n: int, hold: float, fade: float, empty: float, smash: float, end_pad: float
) -> list[tuple[str, float, float]]:
    """(kind, t0, t1) 时间轴。kind: hold / fade / empty / smash"""
    wins: list[tuple[str, float, float]] = []
    t = 0.0
    for i in range(n):
        ht = hold + (end_pad if i == n - 1 else 0.0)
        wins.append(("hold", t, t + ht))
        t += ht
        if i == n - 1:
            break
        wins.append(("fade", t, t + fade))
        t += fade
        wins.append(("empty", t, t + empty))
        t += empty
        wins.append(("smash", t, t + smash))
        t += smash
    return wins


def qa_showcase_audio(
    mp4: Path,
    n: int,
    hold: float,
    fade: float,
    empty: float,
    smash: float,
    end_pad: float = 0.40,
) -> list[str]:
    if not mp4.is_file():
        return [f"missing {mp4}"]
    sr, samples = _decode_mono_wav(mp4)
    env = _rms_windows(samples, sr)
    wins = showcase_windows(n, hold, fade, empty, smash, end_pad)
    errs: list[str] = []

    def peak_in(t0: float, t1: float) -> float:
        vals = [rms for t, rms in env if t0 - 1e-6 <= t < t1]
        return max(vals) if vals else 0.0

    smash_n = 0
    stray: list[str] = []
    for kind, t0, t1 in wins:
        peak = peak_in(t0, t1)
        if kind in ("hold", "empty"):
            # 帧取整会让理论窗和成片差几十毫秒，头尾各让一点
            check0 = t0 + (0.06 if kind == "hold" else 0.04)
            check1 = t1 - 0.06
            if check1 > check0:
                peak = peak_in(check0, check1)
                if peak > HOLD_RMS_MAX:
                    stray.append(f"{kind} {t0:.2f}-{t1:.2f}s rms={peak:.0f}")
        elif kind == "smash":
            smash_n += 1
            if peak < HIT_RMS_MIN:
                errs.append(f"砸入段 {t0:.2f}-{t1:.2f}s 没有砸入声（peak={peak:.0f}）")
        elif kind == "fade":
            # 允许淡出开头一声拉开；淡出后半必须静
            tail = peak_in(min(t1, t0 + 0.22), t1)
            if tail > HOLD_RMS_MAX * 1.6:
                stray.append(f"fade-tail {t0:.2f}-{t1:.2f}s rms={tail:.0f}")
    if stray:
        errs.append("静持/空镜不该响（乱入）：" + "；".join(stray[:8]))
    expect_smash = max(0, n - 1)
    if smash_n != expect_smash:
        errs.append(f"砸入段数量 {smash_n} ≠ {expect_smash}")
    return errs


def main() -> int:
    p = argparse.ArgumentParser(description="3:4 贴图出片自检")
    sub = p.add_subparsers(dest="cmd", required=True)
    p_png = sub.add_parser("pngs")
    p_png.add_argument("folder", type=Path)
    p_sh = sub.add_parser("showcase")
    p_sh.add_argument("mp4", type=Path)
    p_sh.add_argument("--n", type=int, required=True)
    p_sh.add_argument("--hold", type=float, default=5.0)
    p_sh.add_argument("--fade", type=float, default=0.35)
    p_sh.add_argument("--empty", type=float, default=0.50)
    p_sh.add_argument("--smash", type=float, default=0.25)
    p_sh.add_argument("--end-pad", type=float, default=0.40)
    args = p.parse_args()
    if args.cmd == "pngs":
        errs = qa_png_fill(args.folder)
    else:
        errs = qa_showcase_audio(
            args.mp4,
            args.n,
            args.hold,
            args.fade,
            args.empty,
            args.smash,
            args.end_pad,
        )
    if errs:
        print("QA FAIL", file=sys.stderr)
        for e in errs:
            print(" -", e, file=sys.stderr)
        return 1
    print("QA OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
