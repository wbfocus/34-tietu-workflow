# -*- coding: utf-8 -*-
"""Cover style + BGM rotation history.

Keeps recent picks so consecutive jobs don't stick to one cover style or one song.
History travels with the skill pack (assets/media-rotation.json).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "assets" / "media-rotation.json"
COVER_AVOID = 2
BGM_AVOID = 1
COVER_KEEP = 6
BGM_KEEP = 4


def _load() -> dict:
    if not HISTORY.is_file():
        return {"cover_recent": [], "bgm_recent": []}
    try:
        data = json.loads(HISTORY.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"cover_recent": [], "bgm_recent": []}
    if not isinstance(data, dict):
        return {"cover_recent": [], "bgm_recent": []}
    data.setdefault("cover_recent", [])
    data.setdefault("bgm_recent", [])
    return data


def _save(data: dict) -> None:
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recent_covers(n: int = COVER_AVOID) -> list[str]:
    return list(_load().get("cover_recent") or [])[:n]


def recent_bgms(n: int = BGM_AVOID) -> list[str]:
    return list(_load().get("bgm_recent") or [])[:n]


def remember_cover(style_id: str) -> None:
    data = _load()
    rec = [style_id] + [x for x in data.get("cover_recent") or [] if x != style_id]
    data["cover_recent"] = rec[:COVER_KEEP]
    _save(data)


def remember_bgm(name: str) -> None:
    data = _load()
    rec = [name] + [x for x in data.get("bgm_recent") or [] if x != name]
    data["bgm_recent"] = rec[:BGM_KEEP]
    _save(data)


def filter_ids(candidates: list[str], avoid: list[str]) -> list[str]:
    """Drop avoided ids if enough remain; otherwise keep full list."""
    if not candidates:
        return candidates
    kept = [x for x in candidates if x not in avoid]
    return kept if kept else list(candidates)
