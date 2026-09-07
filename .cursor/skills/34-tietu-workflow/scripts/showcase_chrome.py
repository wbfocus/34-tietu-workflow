# -*- coding: utf-8 -*-
"""Top TOC chrome for showcase mode: title + sliding capsule over tab labels."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HEADER_W = 1080
# 3:4 画布顶栏要薄，给卡片留高度（禁止再做成 9:16 顶栏）
HEADER_H = 120
TITLE_Y = 8
NAV_Y = 58
NAV_ROW = 52
PILL_H = 44
TAB_FONT = 22
TITLE_FONT = 34
GAP = 8
PAD_X = 14

FONT_CANDIDATES = [
    Path(r"C:\Windows\Fonts\msyhbd.ttc"),
    Path(r"C:\Windows\Fonts\msyh.ttc"),
    Path("/System/Library/Fonts/STHeiti Medium.ttc"),
    Path("/System/Library/Fonts/Hiragino Sans GB.ttc"),
    Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc"),
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
]


@dataclass
class TabBox:
    x: float
    y: float
    w: float
    h: float
    text: str


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for p in FONT_CANDIDATES:
        if p.is_file():
            try:
                return ImageFont.truetype(str(p), size=size, index=0)
            except OSError:
                continue
    return ImageFont.load_default()


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lower().replace("0x", "").replace("#", "")
    if len(h) == 6:
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return 26, 26, 26


def is_dark(hex_color: str) -> bool:
    r, g, b = hex_to_rgb(hex_color)
    return (r * 299 + g * 587 + b * 114) / 1000 < 148


def parse_tabs_from_wenan(path: Path) -> list[str]:
    if not path.is_file():
        return []
    rows: list[tuple[int, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"第\s*(\d+)\s*张\s*\|\s*([^|]+)", line.strip())
        if not m:
            continue
        label = m.group(2).strip()
        label = re.sub(r"^(封面|内容|结尾)\s*", lambda x: x.group(1), label)
        if "：" in label:
            label = label.split("：", 1)[0].strip()
        if len(label) > 6:
            label = label[:6]
        rows.append((int(m.group(1)), label))
    rows.sort(key=lambda x: x[0])
    return [x[1] for x in rows]


def parse_title_from_wenan(path: Path, fallback: str) -> str:
    if not path.is_file():
        return fallback
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("#"):
            t = s.lstrip("#").strip()
            t = re.sub(r"\s*[·•].*$", "", t)
            t = re.sub(r"\s*3:4.*$", "", t).strip()
            return t or fallback
    return fallback


def default_tabs(n: int) -> list[str]:
    return [f"{i + 1:02d}" for i in range(n)]


def fit_tabs(tabs: list[str], n: int) -> list[str]:
    tabs = [t.strip() or default_tabs(1)[0] for t in tabs]
    if len(tabs) < n:
        tabs = tabs + default_tabs(n)[len(tabs) :]
    return tabs[:n]


def _layout(draw: ImageDraw.ImageDraw, tabs: list[str], font) -> tuple[list[TabBox], float]:
    sizes = []
    for t in tabs:
        bbox = draw.textbbox((0, 0), t, font=font)
        sizes.append((bbox[2] - bbox[0], bbox[3] - bbox[1]))
    widths = [w + PAD_X * 2 for w, _ in sizes]
    total = sum(widths) + GAP * max(0, len(tabs) - 1)
    scale = 1.0
    if total > HEADER_W - 48:
        scale = (HEADER_W - 48) / total
        widths = [w * scale for w in widths]
        total = sum(widths) + GAP * max(0, len(tabs) - 1)
    x = (HEADER_W - total) / 2
    y = NAV_Y + (NAV_ROW - PILL_H) / 2
    boxes: list[TabBox] = []
    for t, w in zip(tabs, widths):
        boxes.append(TabBox(x=x, y=y, w=w, h=PILL_H, text=t))
        x += w + GAP
    return boxes, scale


def render_header(
    title: str,
    tabs: list[str],
    from_idx: int,
    to_idx: int,
    progress: float,
    bg_hex: str,
) -> Image.Image:
    bg = hex_to_rgb(bg_hex)
    dark = is_dark(bg_hex)
    pill_fill = (255, 255, 255) if dark else (28, 28, 32)
    active_fg = (28, 28, 32) if dark else (255, 255, 255)
    muted_fg = (255, 255, 255, 220) if dark else (40, 40, 45, 220)
    title_fg = (255, 255, 255) if dark else (20, 20, 24)

    im = Image.new("RGB", (HEADER_W, HEADER_H), bg)
    draw = ImageDraw.Draw(im, "RGBA")
    title_font = _font(TITLE_FONT if len(title) <= 16 else 28)
    tab_font = _font(TAB_FONT)

    # title
    tb = draw.textbbox((0, 0), title, font=title_font)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    draw.text(((HEADER_W - tw) / 2, TITLE_Y), title, font=title_font, fill=title_fg)

    boxes, _scale = _layout(draw, tabs, tab_font)
    if not boxes:
        return im

    from_idx = max(0, min(from_idx, len(boxes) - 1))
    to_idx = max(0, min(to_idx, len(boxes) - 1))
    p = max(0.0, min(1.0, progress))
    # ease-in-out：空镜中段胶囊还在路上，才有「拉过来」
    if p < 0.5:
        ease = 4 * p * p * p
    else:
        ease = 1.0 - ((-2 * p + 2) ** 3) / 2
    a, b = boxes[from_idx], boxes[to_idx]
    px = a.x + (b.x - a.x) * ease
    pw = a.w + (b.w - a.w) * ease
    py = a.y
    ph = a.h
    draw.rounded_rectangle([px, py, px + pw, py + ph], radius=ph / 2, fill=pill_fill)

    pill_cx = px + pw / 2
    for box in boxes:
        tb = draw.textbbox((0, 0), box.text, font=tab_font)
        tw, th = tb[2] - tb[0], tb[3] - tb[1]
        tx = box.x + (box.w - tw) / 2
        ty = box.y + (box.h - th) / 2 - 2
        tab_cx = box.x + box.w / 2
        covered = abs(pill_cx - tab_cx) <= max(8.0, box.w * 0.42)
        fill = active_fg if covered else muted_fg
        draw.text((tx, ty), box.text, font=tab_font, fill=fill)
    return im.convert("RGB")


def write_hold_headers(
    out_dir: Path,
    title: str,
    tabs: list[str],
    bg_hex: str,
) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for i in range(len(tabs)):
        im = render_header(title, tabs, i, i, 0.0, bg_hex)
        p = out_dir / f"hold_{i:02d}.png"
        im.save(p, "PNG")
        paths.append(p)
    return paths


def write_slide_headers(
    out_dir: Path,
    title: str,
    tabs: list[str],
    from_idx: int,
    n_frames: int,
    bg_hex: str,
) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    to_idx = from_idx + 1
    for f in range(n_frames):
        prog = f / max(n_frames - 1, 1)
        im = render_header(title, tabs, from_idx, to_idx, prog, bg_hex)
        p = out_dir / f"slide_{from_idx:02d}_{f:02d}.png"
        im.save(p, "PNG")
        paths.append(p)
    return paths
