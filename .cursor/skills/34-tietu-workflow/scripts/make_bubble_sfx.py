# -*- coding: utf-8 -*-
"""Synthesize a short bubble-pop wav (no BGM, no VO)."""
from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "assets" / "sfx" / "bubble-pop.wav"


def write_bubble(path: Path | None = None, seconds: float = 0.13) -> Path:
    out = path or DEFAULT_OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    sr = 44100
    n = int(sr * seconds)
    with wave.open(str(out), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        frames = bytearray()
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 26.0) * max(0.0, 1.0 - t / seconds)
            freq = 920.0 * math.exp(-t * 8.5) + 210.0
            sig = math.sin(2 * math.pi * freq * t)
            click = math.sin(2 * math.pi * 2650.0 * t) * math.exp(-t * 85.0) * 0.22
            v = (sig * 0.58 + click) * env * 0.62
            v = max(-1.0, min(1.0, v))
            frames += struct.pack("<h", int(v * 32767))
        w.writeframes(bytes(frames))
    return out


if __name__ == "__main__":
    p = write_bubble()
    print(p)
