# -*- coding: utf-8 -*-
"""工作文件夹和成品 MP4 同一套名字：模式_日期_标题（主题）

例：上滑_2026-09-11_毛利根本不是一回事（深色）
    上滑_2026-09-11_毛利根本不是一回事（深色）.mp4
    上滑_2026-09-11_毛利根本不是一回事（深色）（带封面）.mp4
    橱窗_2026-09-08_经营分析落不到车间（刊物）
    轮播_2026-09-08_经营分析落不到车间（刊物）.mp4
"""
from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path

MODE_SCROLL = "上滑"
MODE_CAROUSEL = "轮播"
MODE_SHOWCASE = "橱窗"
MODES = (MODE_SCROLL, MODE_CAROUSEL, MODE_SHOWCASE)

_DELIVERY = re.compile(
    r"^(?P<mode>上滑|轮播|橱窗)_(?P<day>\d{4}-\d{2}-\d{2})_(?P<rest>.+)$"
)
_THEME_TAIL = re.compile(r"（([^）]+)）\s*$")
_NUM_PREFIX = re.compile(r"^\d+[、.．]\s*")
_LONG_PREFIX = re.compile(r"^(长图[-_]|eli5[-_]?)", re.I)


def parse_day(raw: str | date | None = None) -> date:
    if raw is None or raw == "":
        return date.today()
    if isinstance(raw, date):
        return raw
    return datetime.strptime(str(raw).strip(), "%Y-%m-%d").date()


def split_delivery_name(folder_name: str) -> tuple[str | None, str | None, str]:
    """已是新规则时拆出 (模式, 日期, 其余)；否则 (None, None, 原名)。"""
    name = (folder_name or "").strip()
    m = _DELIVERY.match(name)
    if m:
        return m.group("mode"), m.group("day"), m.group("rest")
    return None, None, name


def parse_job_label(folder_name: str) -> tuple[str, str]:
    """文件夹名 → (标题, 主题括号)。"""
    _mode, _day, name = split_delivery_name(folder_name)
    theme = ""
    m = _THEME_TAIL.search(name)
    if m:
        theme = f"（{m.group(1)}）"
        name = name[: m.start()].rstrip()
    name = _LONG_PREFIX.sub("", name)
    name = _NUM_PREFIX.sub("", name)
    title = name.strip() or (folder_name or "").strip() or "未命名"
    return title, theme


def resolve_day(explicit: str | date | None, folder_name: str = "") -> date:
    if explicit not in (None, ""):
        return parse_day(explicit)
    _mode, day, _rest = split_delivery_name(folder_name)
    if day:
        return parse_day(day)
    return date.today()


def delivery_stem(
    mode: str,
    folder_name: str,
    day: str | date | None = None,
) -> str:
    title, theme = parse_job_label(folder_name)
    when = resolve_day(day, folder_name)
    return f"{mode}_{when.isoformat()}_{title}{theme}"


def delivery_folder(
    mode: str,
    folder_name: str,
    day: str | date | None = None,
) -> str:
    """工作文件夹名，与成片主文件名（不含 .mp4 / 带封面）相同。"""
    return delivery_stem(mode, folder_name, day)


def delivery_mp4(
    video_dir: Path,
    mode: str,
    folder_name: str,
    *,
    cover: bool = False,
    day: str | date | None = None,
) -> Path:
    stem = delivery_stem(mode, folder_name, day)
    name = f"{stem}（带封面）.mp4" if cover else f"{stem}.mp4"
    return Path(video_dir) / name
