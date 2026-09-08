# -*- coding: utf-8 -*-
"""Stitch 3:4 card PNGs into an MP4 carousel.

默认：每张可读 5 秒 + 交界约 1 秒丝滑转场（每次一种，不重复）+ 固定 BGM。
总时长仍是 N×5 秒（转场叠在两张交界，不另占时长）。

转场选型：只用不拧字的柔过渡（fade / smooth* / distance / hblur / radial…），
不用 3D 卷页、硬 wipe、pixelize。
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

W, H, FPS = 1080, 1440, 30
DEFAULT_HOLD = 5.0
DEFAULT_XFADE = 1.0
DEFAULT_TRANSITION = "mix"
BGM_VOL = 0.10  # 钢琴底床，压在画面下，不要抢注意力
WHOOSH_VOL = 0.04  # 点一下即可，不要盖过 BGM
WHOOSH_LEN = 0.45  # 短促点一下，对齐长转场的前半拍
BGM_FADE_IN = 0.4
BGM_FADE_OUT = 1.5

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BGM = ROOT / "assets" / "audio" / "bgm-serene-view.mp3"
DEFAULT_WHOOSH = ROOT / "assets" / "sfx" / "whoosh-page.wav"

# 丝滑池：相邻方向/类型错开。硬 wipe / pixelize / squeeze 不用。
SILKY_POOL = [
    "fade",
    "smoothleft",
    "distance",
    "smoothup",
    "hblur",
    "smoothright",
    "radial",
    "smoothdown",
    "fadegrays",
    "zoomin",
]

XFADES = frozenset(SILKY_POOL) | {"none", "mix", "slideleft", "slideup", "wipeleft"}

VF = (
    f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
    f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FPS},format=yuv420p"
)


def collect_pngs(folder: Path) -> list[Path]:
    files = [p for p in folder.iterdir() if p.suffix.lower() == ".png"]

    def key(p: Path) -> tuple[int, str]:
        m = re.search(r"(\d+)", p.stem)
        return (int(m.group(1)) if m else 10**9, p.name)

    return sorted(files, key=key)


def pick_transitions(n_cuts: int, mode: str) -> list[str]:
    """One unique silky transition per cut; wrap the pool if cuts > pool size."""
    if n_cuts <= 0:
        return []
    if mode == "none":
        return []
    if mode != "mix":
        return [mode] * n_cuts
    out: list[str] = []
    last = None
    i = 0
    while len(out) < n_cuts:
        t = SILKY_POOL[i % len(SILKY_POOL)]
        i += 1
        if t == last:
            continue
        out.append(t)
        last = t
    return out


def _video_chain(n: int, hold: float, td: float, names: list[str]) -> tuple[list[str], str]:
    parts = [f"[{i}:v]{VF},setpts=PTS-STARTPTS[v{i}]" for i in range(n)]
    if n == 1 or not names or td <= 0:
        concat_in = "".join(f"[v{i}]" for i in range(n))
        parts.append(f"{concat_in}concat=n={n}:v=1:a=0[vout]")
        return parts, "[vout]"
    prev = "v0"
    for i in range(1, n):
        out = "vout" if i == n - 1 else f"x{i}"
        offset = hold * i
        name = names[i - 1]
        parts.append(
            f"[{prev}][v{i}]xfade=transition={name}:duration={td}:offset={offset}[{out}]"
        )
        prev = out
    return parts, "[vout]"


def _audio_chain(
    n: int,
    hold: float,
    dur: float,
    bgm_idx: int | None,
    whoosh_idx: int | None,
) -> list[str]:
    parts: list[str] = []
    fade_out_st = max(0.0, dur - BGM_FADE_OUT)
    mix: list[str] = []
    if bgm_idx is not None:
        parts.append(
            f"[{bgm_idx}:a]volume={BGM_VOL},atrim=0:{dur:.3f},asetpts=PTS-STARTPTS,"
            f"afade=t=in:st=0:d={BGM_FADE_IN},afade=t=out:st={fade_out_st:.3f}:d={BGM_FADE_OUT},"
            f"aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[bgm]"
        )
        mix.append("[bgm]")
    if whoosh_idx is not None and n > 1:
        splits = "".join(f"[w{i}]" for i in range(n - 1))
        parts.append(f"[{whoosh_idx}:a]asplit={n - 1}{splits}")
        for i in range(n - 1):
            ms = int(round(hold * (i + 1) * 1000))
            fade_st = max(0.0, WHOOSH_LEN - 0.12)
            parts.append(
                f"[w{i}]volume={WHOOSH_VOL},atrim=0:{WHOOSH_LEN},asetpts=PTS-STARTPTS,"
                f"afade=t=out:st={fade_st:.3f}:d=0.12,adelay={ms}|{ms},"
                f"atrim=0:{dur:.3f},asetpts=PTS-STARTPTS,"
                f"aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[s{i}]"
            )
            mix.append(f"[s{i}]")
    if not mix:
        return parts
    if len(mix) == 1:
        parts.append(f"{mix[0]}volume=1[aout]")
        return parts
    parts.append(
        "".join(mix)
        + f"amix=inputs={len(mix)}:duration=first:dropout_transition=0:normalize=0[aout]"
    )
    return parts


def cards_to_mp4(
    images: list[Path],
    out: Path,
    hold: float = DEFAULT_HOLD,
    transition: str = DEFAULT_TRANSITION,
    xfade: float = DEFAULT_XFADE,
    bgm: Path | None = DEFAULT_BGM,
    whoosh: Path | None = DEFAULT_WHOOSH,
) -> Path:
    if not images:
        raise SystemExit("no png images")
    transition = (transition or "mix").lower()
    if transition not in XFADES:
        raise SystemExit(f"unknown transition {transition}; use mix / none / {sorted(SILKY_POOL)}")
    n = len(images)
    names = pick_transitions(max(0, n - 1), transition)
    use_xfade = n > 1 and bool(names) and xfade > 0
    td = xfade if use_xfade else 0.0
    dur = n * hold
    out.parent.mkdir(parents=True, exist_ok=True)

    cmd: list[str] = ["ffmpeg", "-y"]
    for i, img in enumerate(images):
        t = hold if (i == n - 1 or not use_xfade) else hold + td
        cmd.extend(["-loop", "1", "-t", f"{t:.3f}", "-i", str(img)])

    bgm_idx = None
    if bgm and Path(bgm).is_file():
        bgm_idx = n
        cmd.extend(["-stream_loop", "-1", "-i", str(bgm)])
    elif bgm:
        print("WARN missing BGM", bgm, file=sys.stderr)

    whoosh_idx = None
    if use_xfade and whoosh and Path(whoosh).is_file():
        whoosh_idx = (n + 1) if bgm_idx is not None else n
        cmd.extend(["-i", str(whoosh)])
    elif use_xfade and whoosh:
        print("WARN missing whoosh", whoosh, file=sys.stderr)

    v_parts, vmap = _video_chain(n, hold, td, names if use_xfade else [])
    a_parts = _audio_chain(n, hold, dur, bgm_idx, whoosh_idx)
    fc = ";".join(v_parts + a_parts)

    cmd.extend(["-filter_complex", fc, "-map", vmap])
    has_audio = bool(a_parts)
    if has_audio:
        cmd.extend(["-map", "[aout]", "-c:a", "aac", "-b:a", "192k"])
    else:
        cmd.append("-an")
    cmd.extend(
        [
            "-c:v",
            "libx264",
            "-crf",
            "18",
            "-preset",
            "medium",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(FPS),
            "-t",
            f"{dur:.3f}",
            "-movflags",
            "+faststart",
            str(out),
        ]
    )
    print(
        f"RUN ffmpeg carousel  n={n} hold={hold}s  "
        f"xfade={'+'.join(names) if names else 'none'}/{td}s  bgm={bgm_idx is not None}  → {out}"
    )
    subprocess.check_call(cmd)
    print("OK", out)
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="3:4 cards → MP4 carousel (5s/image + page xfade + BGM)")
    p.add_argument("images_dir", type=Path, help="成品图 folder")
    p.add_argument("--out", type=Path, help="output mp4")
    p.add_argument("--hold", type=float, default=DEFAULT_HOLD, help="readable seconds per image")
    p.add_argument("--xfade", type=float, default=DEFAULT_XFADE, help="page-turn seconds (overlap)")
    p.add_argument(
        "--transition",
        default=DEFAULT_TRANSITION,
        help="mix=每次一种丝滑转场（默认）| fade|smoothleft|… | none",
    )
    p.add_argument("--bgm", type=Path, default=DEFAULT_BGM)
    p.add_argument("--whoosh", type=Path, default=DEFAULT_WHOOSH)
    p.add_argument("--no-bgm", action="store_true")
    p.add_argument("--no-sfx", action="store_true")
    args = p.parse_args()
    folder = args.images_dir
    if folder.is_file():
        folder = folder.parent
    if not folder.exists():
        print("missing", folder, file=sys.stderr)
        return 1
    pngs = collect_pngs(folder)
    if not pngs:
        print("no png in", folder, file=sys.stderr)
        return 1
    out = args.out or (folder.parent / "成品视频" / f"{folder.parent.name}（轮播）.mp4")
    cards_to_mp4(
        pngs,
        out,
        hold=args.hold,
        transition=args.transition,
        xfade=args.xfade,
        bgm=None if args.no_bgm else args.bgm,
        whoosh=None if args.no_sfx else args.whoosh,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
