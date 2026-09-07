# -*- coding: utf-8 -*-
"""3:4 卡片 → 橱窗砸入 MP4（独立于 cards_to_mp4 丝滑轮播）。

舞台锁定 1080×1440（3:4），与贴图/封面同画布。禁止 9:16。
顶部薄目录胶囊 + 下方完整 3:4 卡：静持 5 秒可读 → 淡出（轻一声拉开）→ 空镜静音（胶囊滑到下一张）→ 拖影砸入（重一声）。
静持和空镜禁止出声。音效锁在对应视频段上，禁止用 adelay 往静持里甩。

Usage:
  py -3 cards_to_showcase.py "<成品图文件夹>" --title "大标题" --tabs "封面|口径|铁律"
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

from cards_to_mp4 import DEFAULT_WHOOSH, collect_pngs
from showcase_chrome import (
    HEADER_H,
    default_tabs,
    fit_tabs,
    parse_tabs_from_wenan,
    parse_title_from_wenan,
    write_hold_headers,
    write_slide_headers,
)

STAGE_W, STAGE_H, FPS = 1080, 1440, 30
HEADER_GAP = 8
_avail_h = (STAGE_H - HEADER_H - HEADER_GAP) // 4 * 4
CARD_H = _avail_h
CARD_W = CARD_H * 3 // 4
CARD_X = (STAGE_W - CARD_W) // 2
DEFAULT_HOLD = 5.0
DEFAULT_FADE = 0.35
DEFAULT_EMPTY = 0.50
DEFAULT_SMASH = 0.25
DEFAULT_END_PAD = 0.40
SFX_DIR = Path(__file__).resolve().parents[1] / "assets" / "sfx"
DEFAULT_SLIDE_SFX = SFX_DIR / "sample-slide.wav"
DEFAULT_SMASH_SFX = SFX_DIR / "sample-smash.wav"
# Mixkit whoosh-page.wav 前 0.5s 几乎无声，当样例切片不存在时从这里截
WHOOSH_BODY_START = 0.52
PILL_WHOOSH_VOL = 1.00
SMASH_WHOOSH_VOL = 1.05
# 拉开声只叠在淡出（卡片还在走），空镜/静持必须静音。长度不得超过淡出。
PILL_WHOOSH_LEN = 0.16
# 砸入声必须落在砸入段内，禁止拖进下一张静持。
SMASH_WHOOSH_LEN = 0.22
BGM_VOL = 0.08
BGM_FADE_IN = 0.3
BGM_FADE_OUT = 1.2
FALLBACK_BG = "0x1a1a1a"

CARD_VF = (
    f"scale={CARD_W}:{CARD_H}:force_original_aspect_ratio=decrease,"
    f"pad={CARD_W}:{CARD_H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FPS}"
)


def _ff(*args: str) -> None:
    subprocess.check_call(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args]
    )


def sample_bg_hex(image: Path) -> str:
    try:
        raw = subprocess.check_output(
            [
                "ffmpeg",
                "-v",
                "error",
                "-i",
                str(image),
                "-vf",
                f"scale={CARD_W}:{CARD_H}:force_original_aspect_ratio=decrease,"
                f"pad={CARD_W}:{CARD_H}:(ow-iw)/2:(oh-ih)/2,crop=2:2:16:16",
                "-frames:v",
                "1",
                "-f",
                "rawvideo",
                "-pix_fmt",
                "rgb24",
                "pipe:1",
            ]
        )
        if len(raw) >= 3:
            return f"0x{raw[0]:02x}{raw[1]:02x}{raw[2]:02x}"
    except subprocess.CalledProcessError:
        pass
    return FALLBACK_BG


def _x264(dst: Path) -> list[str]:
    return [
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "17",
        "-pix_fmt",
        "yuv420p",
        "-r",
        str(FPS),
        "-an",
        str(dst),
    ]


def _card_y() -> int:
    return HEADER_H + HEADER_GAP


def _stage(bg: str, seconds: float) -> list[str]:
    return [
        "-f",
        "lavfi",
        "-i",
        f"color=c={bg}:s={STAGE_W}x{STAGE_H}:d={seconds:.3f}:r={FPS}",
    ]


def encode_hold(card: Path, header: Path, seconds: float, bg: str, dst: Path) -> None:
    cy = _card_y()
    fc = (
        f"[1:v]{CARD_VF},format=yuv420p[c];"
        f"[2:v]fps={FPS},format=yuv420p[h];"
        f"[0:v]setsar=1,fps={FPS}[bg];"
        f"[bg][c]overlay={CARD_X}:{cy}[s];"
        "[s][h]overlay=0:0,format=yuv420p"
    )
    _ff(
        *_stage(bg, seconds),
        "-loop",
        "1",
        "-t",
        f"{seconds:.3f}",
        "-i",
        str(card),
        "-loop",
        "1",
        "-t",
        f"{seconds:.3f}",
        "-i",
        str(header),
        "-filter_complex",
        fc,
        *_x264(dst),
    )


def encode_fade(
    card: Path, header: Path | None, seconds: float, bg: str, dst: Path
) -> None:
    cy = _card_y()
    fade_card = (
        f"[1:v]{CARD_VF},fade=t=out:st=0:d={seconds:.3f}:color={bg},format=yuv420p[c];"
        f"[0:v]setsar=1,fps={FPS}[bg];"
        f"[bg][c]overlay={CARD_X}:{cy}"
    )
    inputs = [
        *_stage(bg, seconds),
        "-loop",
        "1",
        "-t",
        f"{seconds:.3f}",
        "-i",
        str(card),
    ]
    if header is not None:
        fc = fade_card + "[s];[2:v]fps={FPS},format=yuv420p[h];[s][h]overlay=0:0,format=yuv420p".replace(
            "{FPS}", str(FPS)
        )
        inputs.extend(["-loop", "1", "-t", f"{seconds:.3f}", "-i", str(header)])
    else:
        fc = fade_card + ",format=yuv420p"
    _ff(*inputs, "-filter_complex", fc, *_x264(dst))


def encode_empty(slide_pattern: Path, seconds: float, bg: str, dst: Path) -> None:
    fc = (
        f"[0:v]setsar=1,fps={FPS}[bg];"
        f"[1:v]fps={FPS},format=yuv420p[h];"
        "[bg][h]overlay=0:0,format=yuv420p"
    )
    _ff(
        *_stage(bg, seconds),
        "-framerate",
        str(FPS),
        "-start_number",
        "0",
        "-i",
        str(slide_pattern),
        "-filter_complex",
        fc,
        "-t",
        f"{seconds:.3f}",
        *_x264(dst),
    )


def encode_smash(
    card: Path, header: Path | None, seconds: float, bg: str, dst: Path
) -> None:
    cy = _card_y()
    blur_d = max(0.08, seconds * 0.80)
    pad = seconds + 0.08
    slide = (
        f"[1:v]{CARD_VF},split[sh][bl];"
        f"[bl]dblur=angle=0:radius=32,format=rgba,"
        f"fade=t=out:st=0:d={blur_d:.3f}:alpha=1[bf];"
        "[sh]format=rgba[sf];"
        "[sf][bf]overlay=format=auto[card];"
        f"[0:v]setsar=1,fps={FPS}[bg];"
        f"[bg][card]overlay=x='-w+({CARD_X}+w)*(1-pow(1-min(1\\,t/{seconds:.3f}),3))'"
        f":y={cy}:shortest=1"
    )
    inputs = [
        *_stage(bg, pad),
        "-loop",
        "1",
        "-t",
        f"{pad:.3f}",
        "-i",
        str(card),
    ]
    if header is not None:
        fc = slide + "[s];[2:v]fps={FPS},format=rgba[h];[s][h]overlay=0:0,format=yuv420p".replace(
            "{FPS}", str(FPS)
        )
        inputs.extend(["-loop", "1", "-t", f"{pad:.3f}", "-i", str(header)])
    else:
        fc = slide + ",format=yuv420p"
    _ff(
        *inputs,
        "-filter_complex",
        fc,
        "-t",
        f"{seconds:.3f}",
        *_x264(dst),
    )


def encode_hold_fullbleed(image: Path, seconds: float, dst: Path) -> None:
    vf = (
        f"scale={STAGE_W}:{STAGE_H}:force_original_aspect_ratio=decrease,"
        f"pad={STAGE_W}:{STAGE_H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FPS},format=yuv420p"
    )
    _ff("-loop", "1", "-t", f"{seconds:.3f}", "-i", str(image), "-vf", vf, *_x264(dst))


def transition_times(
    n: int, hold: float, fade: float, empty: float, smash: float
) -> tuple[list[float], list[float]]:
    pill: list[float] = []
    smash_at: list[float] = []
    if n < 2:
        return pill, smash_at
    t = 0.0
    for _ in range(n - 1):
        t += hold + fade
        pill.append(t)
        t += empty
        smash_at.append(t)
        t += smash
    return pill, smash_at


def total_duration(
    n: int, hold: float, fade: float, empty: float, smash: float, end_pad: float
) -> float:
    if n <= 0:
        return 0.0
    if n == 1:
        return hold + end_pad
    return n * hold + (n - 1) * (fade + empty + smash) + end_pad


def snap_time(seconds: float, fps: int = FPS) -> float:
    return max(1, int(round(seconds * fps))) / float(fps)


def _wav_dur(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        rate = wav.getframerate() or 1
        return wav.getnframes() / float(rate)


def _wav_set_nframes(path: Path, nframes: int, sr: int = 48000, ch: int = 2) -> None:
    with wave.open(str(path), "rb") as src:
        sw = src.getsampwidth()
        data = src.readframes(src.getnframes())
    frame_bytes = sw * ch
    want = nframes * frame_bytes
    if len(data) < want:
        data += b"\x00" * (want - len(data))
    else:
        data = data[:want]
    with wave.open(str(path), "wb") as dst:
        dst.setnchannels(ch)
        dst.setsampwidth(sw)
        dst.setframerate(sr)
        dst.writeframes(data)
    with wave.open(str(path), "rb") as wav:
        rate = wav.getframerate() or 1
        return wav.getnframes() / float(rate)


def _probe_dur(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return float(out.strip())


def encode_silence_wav(dst: Path, seconds: float) -> None:
    _ff(
        "-f",
        "lavfi",
        "-i",
        "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-t",
        f"{seconds:.4f}",
        "-c:a",
        "pcm_s16le",
        str(dst),
    )


def encode_hit_wav(
    src: Path,
    dst: Path,
    seconds: float,
    *,
    start: float,
    hit_len: float,
    vol: float,
) -> None:
    hit_len = min(hit_len, max(0.06, seconds - 0.02), max(0.06, _wav_dur(src) - start - 0.005))
    fade_st = max(0.0, hit_len - 0.04)
    _ff(
        "-i",
        str(src),
        "-af",
        (
            f"atrim={start:.3f}:{start + hit_len:.3f},asetpts=PTS-STARTPTS,"
            f"volume={vol},afade=t=out:st={fade_st:.3f}:d=0.04,"
            f"aformat=sample_fmts=s16:sample_rates=48000:channel_layouts=stereo,"
            f"apad=whole_dur={seconds:.4f},atrim=0:{seconds:.4f}"
        ),
        "-t",
        f"{seconds:.4f}",
        "-c:a",
        "pcm_s16le",
        str(dst),
    )


def _concat_wavs(parts: list[Path], dst: Path) -> None:
    lst = dst.with_suffix(".txt")
    lst.write_text(
        "\n".join(f"file '{p.as_posix()}'" for p in parts) + "\n",
        encoding="utf-8",
    )
    _ff("-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(dst))


def mux_video_audio(
    video: Path,
    sfx_wav: Path | None,
    out: Path,
    dur: float,
    bgm: Path | None,
) -> None:
    cmd: list[str] = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(video),
    ]
    n = 1
    sfx_idx = None
    if sfx_wav is not None:
        sfx_idx = n
        n += 1
        cmd.extend(["-i", str(sfx_wav)])
    bgm_idx = None
    if bgm and Path(bgm).is_file():
        bgm_idx = n
        n += 1
        cmd.extend(["-stream_loop", "-1", "-i", str(bgm)])

    if sfx_idx is None and bgm_idx is None:
        print("WARN showcase has no SFX to mux; writing silent video", flush=True)
        _ff("-i", str(video), "-c:v", "copy", "-an", "-movflags", "+faststart", str(out))
        return

    parts: list[str] = []
    mix: list[str] = []
    fade_out_st = max(0.0, dur - BGM_FADE_OUT)
    if sfx_idx is not None:
        parts.append(
            f"[{sfx_idx}:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[sfx]"
        )
        mix.append("[sfx]")
    if bgm_idx is not None:
        parts.append(
            f"[{bgm_idx}:a]volume={BGM_VOL},atrim=0:{dur:.3f},asetpts=PTS-STARTPTS,"
            f"afade=t=in:st=0:d={BGM_FADE_IN},afade=t=out:st={fade_out_st:.3f}:d={BGM_FADE_OUT},"
            f"aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[bgm]"
        )
        mix.append("[bgm]")
    if len(mix) == 1:
        parts.append(f"{mix[0]}alimiter=limit=0.95[aout]")
    else:
        parts.append(
            "".join(mix)
            + f"amix=inputs={len(mix)}:duration=first:dropout_transition=0:normalize=0[amix];"
            "[amix]alimiter=limit=0.95[aout]"
        )
    cmd.extend(
        [
            "-filter_complex",
            ";".join(parts),
            "-map",
            "0:v",
            "-map",
            "[aout]",
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
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-t",
            f"{dur:.3f}",
            "-movflags",
            "+faststart",
            str(out),
        ]
    )
    print(f"RUN showcase audio  segs+lock bgm={bgm_idx is not None} → {out}", flush=True)
    subprocess.check_call(cmd)


def cards_to_showcase(
    images: list[Path],
    out: Path,
    hold: float = DEFAULT_HOLD,
    fade: float = DEFAULT_FADE,
    empty: float = DEFAULT_EMPTY,
    smash: float = DEFAULT_SMASH,
    end_pad: float = DEFAULT_END_PAD,
    bg: str | None = None,
    whoosh: Path | None = DEFAULT_WHOOSH,
    slide_sfx: Path | None = DEFAULT_SLIDE_SFX,
    smash_sfx: Path | None = DEFAULT_SMASH_SFX,
    bgm: Path | None = None,
    title: str = "",
    tabs: list[str] | None = None,
    toc: bool = True,
) -> Path:
    if not images:
        raise SystemExit("no png images")
    n = len(images)
    hold = snap_time(hold)
    fade = snap_time(fade)
    empty = snap_time(empty)
    smash = snap_time(smash)
    end_pad = snap_time(end_pad)
    bg_hex = (bg or sample_bg_hex(images[0])).lower()
    if not bg_hex.startswith("0x"):
        bg_hex = "0x" + bg_hex
    out.parent.mkdir(parents=True, exist_ok=True)
    dur = total_duration(n, hold, fade, empty, smash, end_pad)
    tab_names = fit_tabs(tabs or default_tabs(n), n)
    head = title.strip() or "知识卡"

    empty_frames = max(2, int(round(empty * FPS)))
    use_sfx = whoosh is not None
    slide_path = slide_sfx if slide_sfx and Path(slide_sfx).is_file() else None
    smash_path = smash_sfx if smash_sfx and Path(smash_sfx).is_file() else None
    fallback = whoosh if whoosh and Path(whoosh).is_file() else None
    if not slide_path:
        slide_path = fallback
    if not smash_path:
        smash_path = fallback
    slide_start = WHOOSH_BODY_START if slide_path == fallback else 0.0
    smash_start = WHOOSH_BODY_START if smash_path == fallback else 0.0

    def _seg_audio(kind: str, video: Path, wav: Path) -> None:
        d = _probe_dur(video)
        if (
            not use_sfx
            or kind in ("hold", "empty")
            or (kind == "fade" and not slide_path)
            or (kind == "smash" and not smash_path)
        ):
            encode_silence_wav(wav, d)
        elif kind == "fade":
            encode_hit_wav(
                slide_path,
                wav,
                d,
                start=slide_start,
                hit_len=min(PILL_WHOOSH_LEN, fade),
                vol=PILL_WHOOSH_VOL,
            )
        else:
            encode_hit_wav(
                smash_path,
                wav,
                d,
                start=smash_start,
                hit_len=min(SMASH_WHOOSH_LEN, smash),
                vol=SMASH_WHOOSH_VOL,
            )
        _wav_set_nframes(wav, int(round(d * 48000)))

    with tempfile.TemporaryDirectory(prefix="34showcase_") as td:
        tmp = Path(td)
        chrome = tmp / "chrome"
        holds = write_hold_headers(chrome, head, tab_names, bg_hex) if toc else []
        segs: list[Path] = []
        audios: list[Path] = []
        k = 0
        for i, img in enumerate(images):
            hold_t = hold + (end_pad if i == n - 1 else 0.0)
            p = tmp / f"{k:03d}_hold.mp4"
            if toc:
                encode_hold(img, holds[i], hold_t, bg_hex, p)
            else:
                encode_hold_fullbleed(img, hold_t, p)
            segs.append(p)
            aw = tmp / f"{k:03d}_hold.wav"
            _seg_audio("hold", p, aw)
            audios.append(aw)
            k += 1
            if i == n - 1:
                break
            p = tmp / f"{k:03d}_fade.mp4"
            encode_fade(img, holds[i] if toc else None, fade, bg_hex, p)
            segs.append(p)
            aw = tmp / f"{k:03d}_fade.wav"
            _seg_audio("fade", p, aw)
            audios.append(aw)
            k += 1
            p = tmp / f"{k:03d}_empty.mp4"
            if toc:
                write_slide_headers(
                    chrome, head, tab_names, i, empty_frames, bg_hex
                )
                pattern = chrome / f"slide_{i:02d}_%02d.png"
                encode_empty(pattern, empty, bg_hex, p)
            else:
                _ff(
                    *_stage(bg_hex, empty),
                    "-vf",
                    "setsar=1,format=yuv420p",
                    *_x264(p),
                )
            segs.append(p)
            aw = tmp / f"{k:03d}_empty.wav"
            _seg_audio("empty", p, aw)
            audios.append(aw)
            k += 1
            p = tmp / f"{k:03d}_smash.mp4"
            encode_smash(
                images[i + 1],
                holds[i + 1] if toc else None,
                smash,
                bg_hex,
                p,
            )
            segs.append(p)
            aw = tmp / f"{k:03d}_smash.wav"
            _seg_audio("smash", p, aw)
            audios.append(aw)
            k += 1

        lst = tmp / "concat.txt"
        lst.write_text(
            "\n".join(f"file '{seg.as_posix()}'" for seg in segs) + "\n",
            encoding="utf-8",
        )
        silent = tmp / "picture.mp4"
        _ff(
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(lst),
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
            "-an",
            str(silent),
        )
        sfx_wav = tmp / "sfx.wav"
        _concat_wavs(audios, sfx_wav)
        print("RUN showcase mux A/V lock", flush=True)
        mux_video_audio(silent, sfx_wav if use_sfx else None, out, _probe_dur(silent), bgm)

        from qa_tietu import qa_showcase_audio

        qa_errs = qa_showcase_audio(out, n, hold, fade, empty, smash, end_pad)
        if qa_errs:
            raise SystemExit("showcase SFX QA FAIL:\n" + "\n".join(f" - {e}" for e in qa_errs))
        print("QA showcase audio OK (hold/empty silent)", flush=True)

    print(
        f"OK showcase  n={n} toc={toc} hold={hold}s empty={empty}s smash={smash}s "
        f"bg={bg_hex} dur={dur:.2f}s tabs={'|'.join(tab_names)} → {out}",
        flush=True,
    )
    return out


def _resolve_tabs_title(folder: Path, n: int, tabs_arg: str, title_arg: str) -> tuple[str, list[str]]:
    card_dir = folder.parent if folder.name == "成品图" else folder
    wenan = card_dir / "文案.txt"
    title = title_arg.strip()
    if not title:
        title = parse_title_from_wenan(wenan, card_dir.name.split("、", 1)[-1])
    if tabs_arg.strip():
        tabs = [x.strip() for x in tabs_arg.split("|") if x.strip()]
    else:
        tabs = parse_tabs_from_wenan(wenan)
    return title, fit_tabs(tabs or default_tabs(n), n)


def main() -> int:
    p = argparse.ArgumentParser(
        description="3:4 cards → 3:4 showcase MP4 (TOC capsule + empty + smash)"
    )
    p.add_argument("images_dir", type=Path, help="成品图 folder")
    p.add_argument("--out", type=Path, help="default 成品视频/showcase.mp4")
    p.add_argument("--hold", type=float, default=DEFAULT_HOLD)
    p.add_argument("--fade", type=float, default=DEFAULT_FADE)
    p.add_argument("--empty", type=float, default=DEFAULT_EMPTY)
    p.add_argument("--smash", type=float, default=DEFAULT_SMASH)
    p.add_argument("--end-pad", type=float, default=DEFAULT_END_PAD)
    p.add_argument("--bg", default="", help="0xRRGGBB; default sample first card")
    p.add_argument("--title", default="", help="top title")
    p.add_argument("--tabs", default="", help="目录胶囊，用 | 分隔，默认读 文案.txt")
    p.add_argument("--no-toc", action="store_true", help="不要顶部目录（仍走空镜砸入）")
    p.add_argument("--whoosh", type=Path, default=DEFAULT_WHOOSH)
    p.add_argument("--bgm", type=Path, default=None)
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
    title, tabs = _resolve_tabs_title(folder, len(pngs), args.tabs, args.title)
    out = args.out or (folder.parent / "成品视频" / "showcase.mp4")
    try:
        cards_to_showcase(
            pngs,
            out,
            hold=args.hold,
            fade=args.fade,
            empty=args.empty,
            smash=args.smash,
            end_pad=args.end_pad,
            bg=args.bg or None,
            whoosh=None if args.no_sfx else args.whoosh,
            bgm=args.bgm,
            title=title,
            tabs=tabs,
            toc=not args.no_toc,
        )
    except ModuleNotFoundError as e:
        if "PIL" in str(e) or "pillow" in str(e).lower():
            print("橱窗模式需要 Pillow：pip install pillow", file=sys.stderr)
            return 1
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
