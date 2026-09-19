# -*- coding: utf-8 -*-
"""Compose 3:4 scroll video: plate crawls up, sprites pop in, bubble SFX + BGM.

Default: light BGM under bubble pops. No voiceover. No captions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import struct
import shutil
import subprocess
import sys
from pathlib import Path

from make_bubble_sfx import DEFAULT_OUT as BUBBLE_WAV, write_bubble
from mp4_compat import assert_mp4_compat

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
BUBBLE_VOL = 0.12  # 轻点一下，别盖过 BGM
SFX_MIN_GAP = 4.0  # 约每 4 秒最多一声；画面照常弹
BGM_VOL = 0.045  # 有声底压低，别盖过气泡
BGM_FADE_IN = 0.5
BGM_FADE_OUT = 1.8
BGM_INTRO_SKIP_DEFAULT = 20.0  # 曲库未登记某首时的兜底
# aloop 保留样本数（约 3 小时 @48kHz），足够整首歌循环
BGM_ALOOP_SIZE = 500_000_000

# 四边循环跑光（吸睛但不抢正文）
RIM_INSET = 4
RIM_SPEED = 150.0  # 沿边框像素/秒（约半分钟一圈，别太赶）
RIM_TRAIL = 900  # 光尾加长
RIM_THICK = 3
RIM_RX = 36  # 四角椭圆水平半径
RIM_RY = 44  # 四角椭圆垂直半径（略拉长更柔）

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "assets" / "audio"
BGM_SERENE = AUDIO / "bgm-serene-view.mp3"
BGM_INTRO_SKIP_FILE = AUDIO / "bgm-intro-skip.json"
# 随机池排除：旧纯音乐底床（仅池空时兜底）
BGM_POOL_EXCLUDE = {"bgm-serene-view.mp3"}


def load_bgm_intro_skips() -> dict[str, float]:
    """每首歌前奏时长不同，读 audio/bgm-intro-skip.json。"""
    if not BGM_INTRO_SKIP_FILE.is_file():
        return {}
    try:
        raw = json.loads(BGM_INTRO_SKIP_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"WARN bad {BGM_INTRO_SKIP_FILE.name}: {e}", file=sys.stderr)
        return {}
    out: dict[str, float] = {}
    for k, v in (raw or {}).items():
        try:
            out[str(k)] = max(0.0, float(v))
        except (TypeError, ValueError):
            continue
    return out


def intro_skip_for(bgm: Path | None) -> float:
    if bgm is None:
        return BGM_INTRO_SKIP_DEFAULT
    table = load_bgm_intro_skips()
    if bgm.name in table:
        return table[bgm.name]
    return BGM_INTRO_SKIP_DEFAULT


def list_scroll_bgm_pool() -> list[Path]:
    """上滑曲库：audio/ 下除兜底曲外的全部 mp3（含《尘缘》与新加的歌）。"""
    if not AUDIO.is_dir():
        return []
    return sorted(
        p
        for p in AUDIO.glob("*.mp3")
        if p.is_file() and p.name not in BGM_POOL_EXCLUDE
    )


def pick_scroll_bgm(
    job_dir: Path | None = None,
    bgm: Path | None = None,
    *,
    seed: str | None = None,
) -> Path | None:
    """显式 --bgm 优先；否则从曲库随机抽一首（避开最近用过的歌，再按文件夹名稳定抽）。"""
    from media_rotation import filter_ids, recent_bgms, remember_bgm

    if bgm is not None:
        p = Path(bgm)
        if not p.is_file():
            return None
        remember_bgm(p.name)
        print(f"BGM pick: {p.name}  (skip intro {intro_skip_for(p):.0f}s)", flush=True)
        return p
    pool = list_scroll_bgm_pool()
    if not pool:
        return BGM_SERENE if BGM_SERENE.is_file() else None
    if len(pool) == 1:
        pick = pool[0]
    else:
        avoid_names = recent_bgms(1)
        candidates = filter_ids([p.name for p in pool], avoid_names)
        by_name = {p.name: p for p in pool}
        narrowed = [by_name[n] for n in candidates if n in by_name] or pool
        key = seed
        if key is None and job_dir is not None:
            key = job_dir.resolve().name
        if key:
            dig = hashlib.md5(key.encode("utf-8")).hexdigest()
            rng = random.Random(int(dig[:8], 16))
        else:
            rng = random.Random()
        pick = rng.choice(narrowed)
    remember_bgm(pick.name)
    print(f"BGM pick: {pick.name}  (skip intro {intro_skip_for(pick):.0f}s)", flush=True)
    return pick


def bgm_af_chain(
    label: str,
    dur: float,
    *,
    vol: float = BGM_VOL,
    out: str = "bgm",
    bgm: Path | None = None,
    skip: float | None = None,
) -> str:
    """跳过该曲前奏 → 循环 → 裁到成片时长 → 音量/淡入淡出。"""
    fade_out_st = max(0.0, dur - BGM_FADE_OUT)
    if skip is None:
        skip = intro_skip_for(bgm)
    skip = max(0.0, float(skip))
    return (
        f"[{label}]atrim=start={skip:.3f},asetpts=PTS-STARTPTS,"
        f"aloop=loop=-1:size={BGM_ALOOP_SIZE},"
        f"atrim=0:{dur:.3f},asetpts=PTS-STARTPTS,"
        f"volume={vol},"
        f"afade=t=in:st=0:d={BGM_FADE_IN},afade=t=out:st={fade_out_st:.3f}:d={BGM_FADE_OUT},"
        f"aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[{out}]"
    )


def build_perimeter(
    w: int = W,
    h: int = H,
    inset: int = RIM_INSET,
    rx: int = RIM_RX,
    ry: int = RIM_RY,
) -> list[tuple[int, int]]:
    """顺时针圆角矩形路径：直边 + 四角椭圆弧。"""
    import math

    x0, y0 = inset, inset
    x1, y1 = w - inset - 1, h - inset - 1
    rx = max(8, min(rx, (x1 - x0) // 3))
    ry = max(8, min(ry, (y1 - y0) // 3))

    def arc(cx: float, cy: float, a0: float, a1: float, steps: int = 28) -> list[tuple[int, int]]:
        out: list[tuple[int, int]] = []
        for i in range(steps + 1):
            a = math.radians(a0 + (a1 - a0) * (i / steps))
            out.append((int(round(cx + rx * math.cos(a))), int(round(cy + ry * math.sin(a)))))
        return out

    pts: list[tuple[int, int]] = []
    for x in range(x0 + rx, x1 - rx + 1):
        pts.append((x, y0))
    pts.extend(arc(x1 - rx, y0 + ry, -90, 0))
    for y in range(y0 + ry + 1, y1 - ry + 1):
        pts.append((x1, y))
    pts.extend(arc(x1 - rx, y1 - ry, 0, 90))
    for x in range(x1 - rx - 1, x0 + rx - 1, -1):
        pts.append((x, y1))
    pts.extend(arc(x0 + rx, y1 - ry, 90, 180))
    for y in range(y1 - ry - 1, y0 + ry - 1, -1):
        pts.append((x0, y))
    pts.extend(arc(x0 + rx, y0 + ry, 180, 270))
    cleaned: list[tuple[int, int]] = []
    for p in pts:
        if not cleaned or cleaned[-1] != p:
            cleaned.append(p)
    return cleaned


_PERI = build_perimeter()


def draw_running_rim(frame_rgba, t: float, *, dark: bool = True):
    """沿四边循环跑光：长光尾、圆角路径；不画硬角圈、不画刺眼光头白点。"""
    from PIL import Image, ImageDraw, ImageFilter

    peri = _PERI
    n = len(peri)
    if n < 8:
        return frame_rgba
    head = int(t * RIM_SPEED) % n
    overlay = Image.new("RGBA", frame_rgba.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    x0, y0 = RIM_INSET, RIM_INSET
    x1, y1 = W - RIM_INSET - 1, H - RIM_INSET - 1
    # 极淡轨道，不画四角椭圆圈
    rim_a = 22 if dark else 16
    rim_col = (255, 140, 60, rim_a) if dark else (56, 189, 248, rim_a)
    draw.line([(x0 + RIM_RX, y0), (x1 - RIM_RX, y0)], fill=rim_col, width=1)
    draw.line([(x1, y0 + RIM_RY), (x1, y1 - RIM_RY)], fill=rim_col, width=1)
    draw.line([(x1 - RIM_RX, y1), (x0 + RIM_RX, y1)], fill=rim_col, width=1)
    draw.line([(x0, y1 - RIM_RY), (x0, y0 + RIM_RY)], fill=rim_col, width=1)

    half = RIM_THICK
    for k in range(0, RIM_TRAIL, 2):
        i = (head - k) % n
        x, y = peri[i]
        u = 1.0 - k / RIM_TRAIL
        a = int(55 + 150 * (u ** 0.75))
        if dark:
            r = int(255 * u + 56 * (1 - u))
            g = int(160 * u + 189 * (1 - u))
            b = int(70 * u + 248 * (1 - u))
        else:
            r = int(255 * u + 2 * (1 - u))
            g = int(150 * u + 132 * (1 - u))
            b = int(80 * u + 199 * (1 - u))
        draw.ellipse([x - half, y - half, x + half, y + half], fill=(r, g, b, a))

    # 光头：大而淡的暖晕，不要聚成一个点
    hx, hy = peri[head]
    for rad, alpha in ((18, 18), (13, 32), (9, 48), (6, 70), (4, 95)):
        col = (255, 190, 130, alpha) if dark else (160, 210, 255, alpha)
        draw.ellipse([hx - rad, hy - rad, hx + rad, hy + rad], fill=col)

    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=2.6))
    return Image.alpha_composite(frame_rgba.convert("RGBA"), overlay)



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
    # 声音抽稀：视觉仍每块弹出，气泡只按最小间隔响
    last_sfx = -999.0
    for item in timed:
        t = float(item["t"])
        if t - last_sfx >= SFX_MIN_GAP:
            item["sfx"] = True
            last_sfx = t
        else:
            item["sfx"] = False
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
    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        raise SystemExit(f"ffmpeg failed ({proc.returncode})")


def bubble_audio_filter(
    timed: list[dict],
    dur: float,
    *,
    has_bgm: bool,
    bgm: Path | None = None,
) -> str:
    """Input 1 = bubble wav; optional input 2 = BGM（整首进滤镜，按曲跳前奏再循环）。"""
    sfx_items = [r for r in timed if r.get("sfx", True)]
    n = len(sfx_items)
    if n == 0:
        if has_bgm:
            return bgm_af_chain("2:a", dur, bgm=bgm, out="aout")
        return (
            f"anullsrc=r=48000:cl=stereo,atrim=0:{dur:.3f},"
            f"aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[aout]"
        )
    splits = "".join(f"[b{j}]" for j in range(n))
    parts = [f"[1:a]asplit={n}{splits}"]
    mixed: list[str] = []
    for j, r in enumerate(sfx_items):
        ms = max(0, int(round(float(r["t"]) * 1000)))
        parts.append(f"[b{j}]adelay={ms}|{ms},volume={BUBBLE_VOL}[pop{j}]")
        mixed.append(f"[pop{j}]")
    sfx_tail = (
        f"{''.join(mixed)}amix=inputs={n}:duration=longest:dropout_transition=0:normalize=0,"
        f"apad=whole_dur={dur},aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[sfx]"
    )
    parts.append(sfx_tail)
    if has_bgm:
        parts.append(bgm_af_chain("2:a", dur, bgm=bgm, out="bgm"))
        parts.append(
            "[bgm][sfx]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
            "alimiter=limit=0.95,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[aout]"
        )
    else:
        parts.append(
            "[sfx]alimiter=limit=0.95,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[aout]"
        )
    return ";\n".join(parts)


def bgm_only_filter(dur: float, *, bgm: Path | None = None) -> str:
    return bgm_af_chain("1:a", dur, bgm=bgm, out="aout")


def probe_duration(mp4: Path) -> float:
    probe = shutil.which("ffprobe")
    if not probe:
        ff = ffmpeg_bin()
        probe = str(Path(ff).with_name(Path(ff).name.replace("ffmpeg", "ffprobe")))
    proc = subprocess.run(
        [
            probe, "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(mp4),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        raise SystemExit(f"无法读取时长: {mp4}\n{proc.stderr}")
    return float(proc.stdout.strip())


def mix_bgm_onto_mp4(
    mp4: Path,
    bgm: Path,
    out: Path | None = None,
    *,
    vol: float = BGM_VOL,
) -> Path:
    """把 BGM 叠进已有上滑成片（保留气泡轨），视频流 copy。"""
    if not mp4.is_file():
        raise SystemExit(f"缺少成片: {mp4}")
    if not bgm.is_file():
        raise SystemExit(f"缺少 BGM: {bgm}")
    out = out or mp4
    dur = probe_duration(mp4)
    tmp = out.with_suffix(".bgm-tmp.mp4")
    af = (
        f"{bgm_af_chain('1:a', dur, vol=vol, bgm=bgm, out='bgm')};"
        f"[0:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[sfx];"
        f"[bgm][sfx]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        f"alimiter=limit=0.95,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[aout]"
    )
    ff = ffmpeg_bin()
    cmd = [
        ff, "-y",
        "-i", str(mp4),
        "-i", str(bgm),
        "-filter_complex", af,
        "-map", "0:v", "-map", "[aout]",
        "-t", f"{dur:.3f}",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart",
        str(tmp),
    ]
    print(
        f"mix BGM {bgm.name} (skip intro {intro_skip_for(bgm):.0f}s) → {out.name}",
        flush=True,
    )
    run_ffmpeg(cmd)
    tmp.replace(out)
    assert_mp4_compat(out)
    return out


def compose(
    job_dir: Path,
    out_mp4: Path | None = None,
    day: str | None = None,
    bgm: Path | None = None,
    *,
    no_bgm: bool = False,
    no_rim: bool = True,
) -> Path:
    """Scroll + pop via PIL frames. FFmpeg 34-overlay graphs stall for hours on this box."""
    from PIL import Image

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
    travel = int(plan["travel"])

    # 每次出片重写软气泡，避免旧版尖点击还在
    write_bubble(BUBBLE_WAV)

    bgm_path = None if no_bgm else pick_scroll_bgm(job_dir, bgm)
    if bgm is not None and bgm_path is None and not no_bgm:
        print(f"WARN missing BGM {bgm}", file=sys.stderr)
    use_rim = not no_rim
    dark_rim = "深色" in job_dir.name

    video_dir = job_dir / "成品视频"
    video_dir.mkdir(parents=True, exist_ok=True)
    if out_mp4 is None:
        from delivery_names import MODE_SCROLL, delivery_mp4

        out_mp4 = delivery_mp4(video_dir, MODE_SCROLL, job_dir.name, day=day)

    plate_im = Image.open(plate).convert("RGBA")
    sprites: list[tuple[Image.Image, dict]] = []
    for r in timed:
        im = Image.open(harvest / r["file"]).convert("RGBA")
        tw, th = int(r["w"]), int(r["h"])
        if im.size != (tw, th):
            im = im.resize((tw, th), Image.Resampling.LANCZOS)
        sprites.append((im, r))

    nframes = int(round(dur * FPS))
    ff = ffmpeg_bin()
    cmd: list[str] = [
        ff, "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "pipe:0",
    ]
    has_audio = bool(timed) or bgm_path is not None
    if timed:
        af = bubble_audio_filter(
            timed, dur, has_bgm=bgm_path is not None, bgm=bgm_path
        )
        (harvest / "filter.txt").write_text(af, encoding="utf-8")
        cmd.extend(["-i", str(BUBBLE_WAV)])
        if bgm_path is not None:
            cmd.extend(["-i", str(bgm_path)])
        cmd.extend(["-filter_complex", af, "-map", "0:v", "-map", "[aout]"])
    elif bgm_path is not None:
        af = bgm_only_filter(dur, bgm=bgm_path)
        (harvest / "filter.txt").write_text(af, encoding="utf-8")
        cmd.extend(
            ["-i", str(bgm_path), "-filter_complex", af, "-map", "0:v", "-map", "[aout]"]
        )
    else:
        cmd.extend(["-an"])
    cmd.extend(
        [
            "-t", str(dur),
            "-c:v", "libx264", "-profile:v", "high", "-level", "4.0",
            "-x264-params", "level=4.0",
            "-r", str(FPS), "-video_track_timescale", "15360",
            "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "20",
            "-movflags", "+faststart",
        ]
    )
    if has_audio:
        cmd.extend(["-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2"])
    cmd.append(str(out_mp4))

    bgm_note = bgm_path.name if bgm_path else "no-bgm"
    n_sfx = sum(1 for r in timed if r.get("sfx", True))
    print(
        f"compose PIL {nframes} frames, {len(timed)} pops / {n_sfx} sfx, "
        f"bgm={bgm_note}, rim={'on' if use_rim else 'off'} -> {out_mp4.name}",
        flush=True,
    )
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        for i in range(nframes):
            t = i / FPS
            y0 = even(int(scroll_y_at(t, travel, dur)))
            y0 = max(0, min(y0, max(0, plate_im.height - H)))
            frame = plate_im.crop((0, y0, W, y0 + H)).copy()
            for im, r in sprites:
                t0 = float(r["t"])
                if t < t0:
                    continue
                fade = min(1.0, (t - t0) / POP_DUR)
                oy = int(r["y"] - y0 + POP_PX * (1.0 - fade))
                ox = int(r["x"])
                layer = im
                if fade < 1.0:
                    layer = im.copy()
                    alpha = layer.getchannel("A").point(lambda p, f=fade: int(p * f))
                    layer.putalpha(alpha)
                frame.paste(layer, (ox, oy), layer)
            if use_rim:
                frame = draw_running_rim(frame, t, dark=dark_rim)
            proc.stdin.write(frame.convert("RGB").tobytes())
            if i % 90 == 0:
                print(f"  frame {i}/{nframes} t={t:.1f}s", flush=True)
        proc.stdin.close()
    except Exception:
        proc.kill()
        raise
    if proc.wait() != 0:
        raise SystemExit(f"ffmpeg failed ({proc.returncode})")

    meta = harvest / "compose.json"
    meta.write_text(
        json.dumps(
            {
                "output": str(out_mp4),
                "plan": plan,
                "engine": "pil",
                "bgm": str(bgm_path) if bgm_path else None,
                "rim": use_rim,
                "pops": [{"id": r["id"], "t": r["t"], "sfx": bool(r.get("sfx", True))} for r in timed],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"mp4: {out_mp4}")
    print(
        f"duration: {dur}s  travel: {plan['travel']}px  pops: {len(timed)}  "
        f"sfx: {n_sfx}  bgm: {bgm_note}  rim: {'on' if use_rim else 'off'}"
    )
    assert_mp4_compat(out_mp4)
    return out_mp4


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("job", type=Path, help="套图文件夹（内含 harvest/）")
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--bgm", type=Path, default=None, help="指定 BGM；默认从曲库随机（同文件夹稳定同曲）")
    ap.add_argument("--no-bgm", action="store_true")
    ap.add_argument("--rim", action="store_true", help="打开边框跑光（默认关）")
    ap.add_argument(
        "--mix-bgm-only",
        action="store_true",
        help="不重渲画面，只把 BGM 叠进已有成品视频（含带封面版）",
    )
    args = ap.parse_args()
    job = args.job.resolve()
    if not job.is_dir():
        print(f"不是文件夹: {job}", file=sys.stderr)
        return 1
    if args.mix_bgm_only:
        from delivery_names import MODE_SCROLL, delivery_mp4
        from prepend_cover_frame import prepend_cover

        bgm_path = pick_scroll_bgm(job, None if args.no_bgm else args.bgm)
        if bgm_path is None:
            print("没有可用 BGM", file=sys.stderr)
            return 1
        video_dir = job / "成品视频"
        base_mp4 = delivery_mp4(video_dir, MODE_SCROLL, job.name, cover=False)
        if not base_mp4.is_file():
            print(f"缺少成片: {base_mp4}", file=sys.stderr)
            return 1
        mix_bgm_onto_mp4(base_mp4, bgm_path)
        cover_png = job / "封面" / "cover-3x4.png"
        if cover_png.is_file():
            out_with = delivery_mp4(video_dir, MODE_SCROLL, job.name, cover=True)
            prepend_cover(cover_png, base_mp4, out_with)
        return 0
    compose(job, args.output, bgm=args.bgm, no_bgm=args.no_bgm, no_rim=not args.rim)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
