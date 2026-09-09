# -*- coding: utf-8 -*-
"""Compose 3:4 ELI5 scroll video: plate crawls up, sprites pop in, bubble SFX only.

No BGM. No voiceover. No captions.
"""
from __future__ import annotations

import argparse
import json
import struct
import shutil
import subprocess
import sys
from pathlib import Path

from make_bubble_sfx import DEFAULT_OUT as BUBBLE_WAV, write_bubble

W, H, FPS = 1080, 1440, 30
HOLD_START = 0.85
HOLD_END = 1.35
PX_PER_SEC = 78.0
MIN_SECONDS = 18.0
MAX_SECONDS = 90.0
POP_DUR = 0.42
STAGGER = 0.16
POP_PX = 22.0
REVEAL_PAD = 96  # pop after entering from the bottom
BUBBLE_VOL = 0.42


def even(n: int) -> int:
    n = int(round(n))
    return n + 1 if n % 2 else n


def ffmpeg_bin() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        raise SystemExit("未找到 ffmpeg。请安装并加入 PATH，或 pip install imageio-ffmpeg")


def smoothstep_crop(t_name: str, hs: float, he: float, dur: float, travel: int) -> str:
    mov = max(0.001, dur - hs - he)
    u = f"min(1\\,max(0\\,({t_name}-{hs})/{mov}))"
    sm = f"({u})*({u})*(3-2*({u}))"
    raw = f"if(lt({t_name}\\,{hs})\\,0\\,if(gt({t_name}\\,{dur}-{he})\\,{travel}\\,{travel}*{sm}))"
    return f"floor(({raw})/2)*2"


def plan_duration(img_h: int) -> dict[str, float | int]:
    travel = max(0, even(img_h) - H)
    move = travel / PX_PER_SEC if travel else 0.0
    dur = min(MAX_SECONDS, max(MIN_SECONDS, HOLD_START + move + HOLD_END))
    return {"travel": travel, "duration": round(dur, 3), "img_h": even(img_h)}


def scroll_y_at(t: float, travel: int, dur: float) -> float:
    if t <= HOLD_START:
        return 0.0
    if t >= dur - HOLD_END:
        return float(travel)
    u = (t - HOLD_START) / max(0.001, dur - HOLD_START - HOLD_END)
    u = max(0.0, min(1.0, u))
    u = u * u * (3 - 2 * u)
    return travel * u


def invert_scroll(need_y: float, travel: int, dur: float) -> float:
    if need_y <= 0:
        return 0.0
    if need_y >= travel:
        return max(0.0, dur - HOLD_END)
    lo, hi = HOLD_START, dur - HOLD_END
    for _ in range(28):
        mid = (lo + hi) / 2
        if scroll_y_at(mid, travel, dur) < need_y:
            lo = mid
        else:
            hi = mid
    return hi


def assign_pops(reveals: list[dict], travel: int, dur: float) -> list[dict]:
    timed: list[dict] = []
    for r in reveals:
        enter_at = float(r["y"]) - H + REVEAL_PAD
        t0 = invert_scroll(enter_at, travel, dur)
        timed.append({**r, "t": t0})
    timed.sort(key=lambda x: (x["t"], x["y"]))
    last = -1.0
    first_stagger = 0.18
    n_open = 0
    for item in timed:
        if item["t"] <= HOLD_START + 0.05:
            item["t"] = round(0.12 + n_open * first_stagger, 3)
            n_open += 1
        if item["t"] - last < STAGGER:
            item["t"] = round(last + STAGGER, 3)
        last = item["t"]
        if item["t"] > dur - 0.35:
            item["t"] = round(max(0.1, dur - 0.55), 3)
        item["t"] = round(float(item["t"]), 3)
    return timed


def probe_wh(png: Path) -> tuple[int, int]:
    try:
        from PIL import Image

        with Image.open(png) as im:
            return im.size
    except ImportError:
        with png.open("rb") as f:
            sig = f.read(8)
            if sig != b"\x89PNG\r\n\x1a\n":
                raise SystemExit(f"不是 PNG: {png}")
            f.read(8)  # length + IHDR
            w, h = struct.unpack(">II", f.read(8))
            return w, h


def build_filter(timed: list[dict], harvest: Path, plan: dict[str, float | int]) -> str:
    dur = float(plan["duration"])
    travel = int(plan["travel"])
    crop_y = smoothstep_crop("t", HOLD_START, HOLD_END, dur, travel)
    parts = [
        f"[0:v]scale={W}:-2,format=rgba,setsar=1,fps={FPS},"
        f"crop={W}:{H}:0:{crop_y}[base]"
    ]
    last = "base"
    for i, r in enumerate(timed):
        t = float(r["t"])
        x, y = int(r["x"]), int(r["y"])
        w, h = int(r["w"]), int(r["h"])
        src = i + 1
        lab = f"s{i}"
        out = f"v{i}"
        offset = (
            f"{POP_PX}*(1-min(1\\,max(0\\,(t-{t})/{POP_DUR})))"
        )
        y_expr = f"{y}-({crop_y})+({offset})"
        parts.append(
            f"[{src}:v]format=rgba,scale={w}:{h},fade=t=in:st={t}:d={POP_DUR}:alpha=1[{lab}]"
        )
        parts.append(
            f"[{last}][{lab}]overlay=x={x}:y='{y_expr}':enable='gte(t,{t})':format=auto[{out}]"
        )
        last = out
    n = len(timed)
    if n:
        parts.append(f"[{last}]format=yuv420p,setsar=1[vout]")
        splits = "".join(f"[b{j}]" for j in range(n))
        parts.append(f"[bubbles]asplit={n}{splits}")
        mixed = []
        for j, r in enumerate(timed):
            ms = max(0, int(round(float(r["t"]) * 1000)))
            parts.append(f"[b{j}]adelay={ms}|{ms},volume={BUBBLE_VOL}[pop{j}]")
            mixed.append(f"[pop{j}]")
        parts.append(
            f"{''.join(mixed)}amix=inputs={n}:duration=longest:dropout_transition=0:normalize=0,"
            f"apad=whole_dur={dur},alimiter=limit=0.95,aformat=sample_fmts=fltp:channel_layouts=stereo[aout]"
        )
    else:
        parts.append(f"[{last}]format=yuv420p,setsar=1[vout]")
    return ";\n".join(parts)


def run_ffmpeg(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "")[-4000:]
        raise SystemExit(f"ffmpeg failed ({proc.returncode}):\n{err}")


def compose(job_dir: Path, out_mp4: Path | None = None) -> Path:
    harvest = job_dir / "harvest"
    tl_path = harvest / "timeline.json"
    if not tl_path.exists():
        raise SystemExit(f"缺少 {tl_path}，先跑 harvest_eli5_scroll.mjs")
    tl = json.loads(tl_path.read_text(encoding="utf-8"))
    plate = harvest / tl["plate"]
    if not plate.exists():
        raise SystemExit(f"缺少底板 {plate}")
    _w, img_h = probe_wh(plate)
    plan = plan_duration(img_h)
    timed = assign_pops(tl.get("reveals") or [], int(plan["travel"]), float(plan["duration"]))
    dur = float(plan["duration"])

    if not BUBBLE_WAV.exists():
        write_bubble(BUBBLE_WAV)

    video_dir = job_dir / "成品视频"
    video_dir.mkdir(parents=True, exist_ok=True)
    if out_mp4 is None:
        out_mp4 = video_dir / f"{job_dir.name}（上滑）.mp4"

    ff = ffmpeg_bin()
    cmd: list[str] = [ff, "-y", "-loop", "1", "-t", str(dur), "-i", str(plate)]
    for r in timed:
        cmd.extend(["-loop", "1", "-t", str(dur), "-i", str(harvest / r["file"])])
    if timed:
        cmd.extend(["-i", str(BUBBLE_WAV)])

    graph = build_filter(timed, harvest, plan)
    if timed:
        a_idx = 1 + len(timed)
        graph = graph.replace("[bubbles]", f"[{a_idx}:a]")
    script = harvest / "filter.txt"
    script.write_text(graph, encoding="utf-8")

    cmd.extend(
        [
            "-/filter_complex",
            str(script),
            "-map",
            "[vout]",
            "-t",
            str(dur),
            "-r",
            str(FPS),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "20",
            "-movflags",
            "+faststart",
        ]
    )
    if timed:
        cmd.extend(["-map", "[aout]", "-c:a", "aac", "-b:a", "160k"])
    else:
        cmd.extend(["-an"])
    cmd.append(str(out_mp4))
    run_ffmpeg(cmd)

    meta = harvest / "compose.json"
    meta.write_text(
        json.dumps({"output": str(out_mp4), "plan": plan, "pops": [{"id": r["id"], "t": r["t"]} for r in timed]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"mp4: {out_mp4}")
    print(f"duration: {dur}s  travel: {plan['travel']}px  pops: {len(timed)}")
    return out_mp4


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("job", type=Path, help="套图文件夹（内含 harvest/）")
    ap.add_argument("-o", "--output", type=Path)
    args = ap.parse_args()
    job = args.job.resolve()
    if not job.is_dir():
        print(f"不是文件夹: {job}", file=sys.stderr)
        return 1
    compose(job, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
