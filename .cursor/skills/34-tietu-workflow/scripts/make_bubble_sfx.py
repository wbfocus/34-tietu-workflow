# -*- coding: utf-8 -*-
"""Synthesize a soft bubble-pop wav (under BGM; not a sharp click)."""
from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "assets" / "sfx" / "bubble-pop.wav"


def write_bubble(path: Path | None = None, seconds: float = 0.18) -> Path:
    """Soft plop: lower pitch, gentle attack, almost no high click."""
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
            # soft attack then slow decay (not a needle click)
            attack = min(1.0, t / 0.012)
            env = attack * math.exp(-t * 14.0) * max(0.0, 1.0 - t / seconds)
            freq = 520.0 * math.exp(-t * 5.5) + 160.0
            sig = math.sin(2 * math.pi * freq * t)
            # tiny shimmer, heavily damped
            shimmer = math.sin(2 * math.pi * 1100.0 * t) * math.exp(-t * 40.0) * 0.06
            v = (sig * 0.72 + shimmer) * env * 0.38
            v = max(-1.0, min(1.0, v))
            frames += struct.pack("<h", int(v * 32767))
        w.writeframes(bytes(frames))
    return out


if __name__ == "__main__":
    p = write_bubble()
    print(p)
